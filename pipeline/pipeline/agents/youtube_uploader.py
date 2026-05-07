"""Thin wrapper over the YouTube Data API v3 for uploading videos + thumbnails.

OAuth flow:
- First run: launches a browser, user authorizes, refresh token saved to
  pipeline/secrets/youtube_token.json.
- Subsequent runs: refresh token is exchanged silently for a fresh access token.

The Cloud project's OAuth consent screen must include the uploader's Google
account as a test user, otherwise auth completes but the user sees a
"verification required" warning. We surface that case clearly.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from pipeline.schemas import PublishMetadata


SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",  # needed for thumbnails.set
]

DEFAULT_CLIENT_SECRET = (
    Path(__file__).resolve().parent.parent.parent
    / "secrets" / "youtube_client_secret.json"
)
DEFAULT_TOKEN_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "secrets" / "youtube_token.json"
)


class YouTubeUploadError(RuntimeError):
    pass


@dataclass
class UploadResult:
    video_id: str
    watch_url: str
    thumbnail_set: bool


class YouTubeUploader:
    def __init__(
        self,
        client_secret_path: Path = DEFAULT_CLIENT_SECRET,
        token_path: Path = DEFAULT_TOKEN_PATH,
        scopes: Optional[list] = None,
    ) -> None:
        self.client_secret_path = client_secret_path
        self.token_path = token_path
        self.scopes = scopes or SCOPES
        if not self.client_secret_path.exists():
            raise YouTubeUploadError(
                f"OAuth client secret not found at {self.client_secret_path}. "
                f"Place youtube_client_secret.json in pipeline/secrets/."
            )

    # ---------- public API ---------- #

    def upload(
        self,
        *,
        video_path: Path,
        metadata: PublishMetadata,
        thumbnail_path: Optional[Path] = None,
    ) -> UploadResult:
        if not video_path.exists():
            raise YouTubeUploadError(f"Video not found: {video_path}")

        creds = self._authorize()
        youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

        status_block = {
            "privacyStatus": metadata.privacy_status.value,
            "selfDeclaredMadeForKids": metadata.made_for_kids,
        }
        if metadata.publish_at is not None:
            from datetime import timezone as _tz
            # YouTube requires privacy=private when publishAt is set; it flips
            # the video to public at the scheduled time.
            status_block["privacyStatus"] = "private"
            ts = metadata.publish_at
            if ts.tzinfo is None:
                ts = ts.astimezone()  # assume local
            status_block["publishAt"] = (
                ts.astimezone(_tz.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            )

        body = {
            "snippet": {
                "title": metadata.title,
                "description": metadata.description,
                "tags": metadata.tags,
                "categoryId": metadata.category_id.value,
            },
            "status": status_block,
        }
        media = MediaFileUpload(
            str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4"
        )
        try:
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
                notifySubscribers=metadata.notify_subscribers,
            )
            response = self._resumable_upload(request)
        except HttpError as e:
            raise YouTubeUploadError(self._format_http_error(e)) from e

        video_id = response["id"]
        watch_url = f"https://youtu.be/{video_id}"

        thumbnail_set = False
        if thumbnail_path and thumbnail_path.exists():
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/png"),
                ).execute()
                thumbnail_set = True
            except HttpError as e:
                # Custom thumbnails require a verified channel. Surface but
                # don't fail the upload.
                print(f"[publisher] thumbnail upload failed: {self._format_http_error(e)}")

        return UploadResult(
            video_id=video_id,
            watch_url=watch_url,
            thumbnail_set=thumbnail_set,
        )

    # ---------- internals ---------- #

    def _authorize(self) -> Credentials:
        creds: Optional[Credentials] = None
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_info(
                    json.loads(self.token_path.read_text()), self.scopes
                )
            except Exception:
                creds = None

        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self._save_token(creds)
            return creds

        # Need interactive consent.
        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.client_secret_path), self.scopes
        )
        # port=0 picks a random free port; Google accepts any localhost port for
        # desktop OAuth clients.
        creds = flow.run_local_server(port=0, prompt="consent")
        self._save_token(creds)
        return creds

    def _save_token(self, creds: Credentials) -> None:
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_path.write_text(creds.to_json())

    @staticmethod
    def _resumable_upload(request) -> dict:
        response = None
        retries = 0
        while response is None:
            try:
                _status, response = request.next_chunk()
            except HttpError as e:
                if e.resp.status in (500, 502, 503, 504) and retries < 3:
                    retries += 1
                    continue
                raise
        return response

    @staticmethod
    def _format_http_error(e: HttpError) -> str:
        try:
            data = json.loads(e.content.decode())
            err = data.get("error", {})
            return f"HTTP {err.get('code')}: {err.get('message')}"
        except Exception:
            return str(e)
