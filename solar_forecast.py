"""Dummy solar forecast with Gaussian bell curve for Open-Meteo PV Forecast."""

from datetime import datetime, timedelta, timezone, time
from zoneinfo import ZoneInfo
import math


def generate_forecast(config: dict) -> dict[datetime, float]:
    """Return dummy forecast with bell curve for the next 48 hours."""

    # Use the configured timezone or UTC fallback
    tz_str = config.get("timezone", "UTC")
    tz = ZoneInfo(tz_str)

    # Fixed sunrise and sunset times for dummy example (local time)
    sunrise_time = time(6, 0)
    sunset_time = time(20, 0)
    noon_time = time(13, 0)

    now_utc = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    forecast = {}

    # Gaussian bell parameters
    peak_value = 10.0
    sigma_hours = 3.0  # width of the bell curve in hours

    for hour_offset in range(48):
        dt_utc = now_utc + timedelta(hours=hour_offset)
        dt_local = dt_utc.astimezone(tz)
        local_time = dt_local.time()

        # Check if within daylight period
        if sunrise_time <= local_time <= sunset_time:
            # Calculate hours from noon
            delta_hours = (dt_local.hour + dt_local.minute / 60) - noon_time.hour

            # Gaussian formula: peak * exp(-0.5 * (x/sigma)^2)
            value = peak_value * math.exp(-0.5 * (delta_hours / sigma_hours) ** 2)
        else:
            value = 0.0

        forecast[dt_utc] = round(value, 2)

    return forecast
