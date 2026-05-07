"""Schema-level tests for publish-side artifacts."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from pipeline.schemas import (
    PrivacyStatus,
    PublishMetadata,
    PublishPackage,
    ThumbnailLayout,
    ThumbnailMood,
    ThumbnailSpec,
    YouTubeCategory,
)


def test_publish_metadata_min_fields() -> None:
    m = PublishMetadata(
        title="THE ROCK Rates Sandwiches | Cracked Cartoons Ep. 1 #shorts",
        description="Picnic horror.\n\n#shorts",
        tags=["cracked cartoons", "the rock has thoughts", "comedy"],
    )
    assert m.privacy_status == PrivacyStatus.private
    assert m.category_id == YouTubeCategory.comedy


def test_publish_metadata_title_length_enforced() -> None:
    with pytest.raises(ValidationError):
        PublishMetadata(title="x" * 101, description="d", tags=[])


def test_thumbnail_spec_color_pattern() -> None:
    with pytest.raises(ValidationError):
        ThumbnailSpec(
            background_color="not-a-hex",
            episode_badge="EP. 1",
            headline="NOBODY ASKED.",
        )


def test_thumbnail_spec_defaults() -> None:
    s = ThumbnailSpec(episode_badge="EP. 1", headline="NOBODY ASKED.")
    assert s.background_color.startswith("#")
    assert s.layout == ThumbnailLayout.rock_left_object_right
    assert s.mood == ThumbnailMood.angry
    assert s.footer == "the rock has thoughts"


def test_publish_package_roundtrips() -> None:
    pkg = PublishPackage(
        metadata=PublishMetadata(title="t", description="d", tags=[]),
        thumbnail=ThumbnailSpec(episode_badge="EP. 1", headline="NOBODY."),
    )
    payload = pkg.model_dump()
    PublishPackage.model_validate(payload)
