import logging
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from src.core.client import CAMPAIGN_MAPPING_CHANNEL_PREVIEW, Twitch


def _campaign(channel_count: int) -> SimpleNamespace:
    return SimpleNamespace(
        name="Campaign",
        active=True,
        ends_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        allowed_channels=[SimpleNamespace(name=f"ch{i}") for i in range(channel_count)],
    )


def _logged_lines(caplog, campaign) -> list[str]:
    with caplog.at_level(logging.DEBUG, logger="TwitchDrops"):
        Twitch._log_campaign_channels(campaign)
    return [record.getMessage() for record in caplog.records]


def test_directory_campaign_logs_directory(caplog):
    lines = _logged_lines(caplog, _campaign(0))

    assert lines[-1] == "     Channels: directory"


@pytest.mark.parametrize("extra", [0, 1])
def test_channel_list_is_truncated_after_preview_limit(caplog, extra):
    count = CAMPAIGN_MAPPING_CHANNEL_PREVIEW + extra

    lines = _logged_lines(caplog, _campaign(count))

    assert lines[-2] == f"     Channels: {count} channels"
    shown = ", ".join(f"ch{i}" for i in range(CAMPAIGN_MAPPING_CHANNEL_PREVIEW))
    expected = f"     └─ {shown} ... (+{extra} more)" if extra else f"     └─ {shown}"
    assert lines[-1] == expected
