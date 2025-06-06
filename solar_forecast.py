"""Solar forecast calculator for Open-Meteo PV Forecast."""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo


def generate_forecast(config: dict[str, Any]) -> dict[datetime, float]:
    """Generate solar forecast for the next 48 hours.

    Uses a Gaussian bell curve to simulate daily solar production.
    """
    tz = ZoneInfo(config.get("timezone", "UTC"))

    # Fixed times for demonstration
    sunrise = time(6, 0)
    sunset = time(20, 0)
    solar_noon = time(13, 0)

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    forecast: dict[datetime, float] = {}
    peak_power = 10.0
    curve_width = 3.0

    for hour in range(48):
        dt_utc = now + timedelta(hours=hour)
        dt_local = dt_utc.astimezone(tz)

        if sunrise <= dt_local.time() <= sunset:
            delta = (dt_local.hour + dt_local.minute / 60) - solar_noon.hour
            value = peak_power * (1 - (delta / curve_width) ** 2)
            value = max(0, value)
        else:
            value = 0.0

        forecast[dt_utc] = round(value, 2)

    return forecast
