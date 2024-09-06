# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: MIT

"""
This module tests the scheming related parts of the GDI userportal plugin (validation.py)
"""

from datetime import datetime

import ckanext.gdi_userportal.validation as validation
import pytest
import pytz


@pytest.fixture
def time_nye():
    return datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.parametrize(
    "time",
    [
        # No timezone defined
        datetime(2020, 1, 1),
        # Time ahead
        pytz.timezone("CET").localize(datetime(2020, 1, 1, 1, 0)),
        # Time behind
        pytz.timezone("America/Chicago").localize(datetime(2019, 12, 31, 18, 0, 0)),
        # Timezone with more than just hours and microseconds
        pytz.timezone("Asia/Kolkata").localize(datetime(2020, 1, 1, 5, 30, 0, 987654)),
    ],
)
def test_utc_enforcer(time, time_nye):
    result = validation.enforce_utc_time(time)
    assert result == time_nye
    assert result.tzinfo == pytz.UTC
