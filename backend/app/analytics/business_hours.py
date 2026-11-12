from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

NY_TZ = ZoneInfo("America/New_York")
WORK_START = time(9, 0)
WORK_END = time(17, 0)
HOURS_PER_DAY = 8.0


def add_business_hours(start_utc: datetime, business_hours: float) -> datetime:
    """Add business hours (Mon-Fri, 09:00-17:00 America/New_York) to a UTC timestamp."""
    if start_utc.tzinfo is None:
        start_utc = start_utc.replace(tzinfo=timezone.utc)

    local = start_utc.astimezone(NY_TZ)
    remaining = float(business_hours)

    # Advance to next valid business moment if outside hours
    while True:
        if local.weekday() >= 5:
            local = datetime.combine(local.date() + timedelta(days=1), WORK_START, tzinfo=NY_TZ)
            continue
        if local.time() < WORK_START:
            local = datetime.combine(local.date(), WORK_START, tzinfo=NY_TZ)
        elif local.time() >= WORK_END:
            local = datetime.combine(local.date() + timedelta(days=1), WORK_START, tzinfo=NY_TZ)
            continue

        day_end = datetime.combine(local.date(), WORK_END, tzinfo=NY_TZ)
        avail_hours = (day_end - local).total_seconds() / 3600.0
        if remaining <= avail_hours + 1e-9:
            result = local + timedelta(hours=remaining)
            return result.astimezone(timezone.utc)
        remaining -= avail_hours
        local = datetime.combine(local.date() + timedelta(days=1), WORK_START, tzinfo=NY_TZ)


def elapsed_business_hours(start_utc: datetime, end_utc: datetime) -> float:
    """Calculate elapsed business hours (Mon-Fri, 09:00-17:00 America/New_York) between two UTC timestamps."""
    if start_utc.tzinfo is None:
        start_utc = start_utc.replace(tzinfo=timezone.utc)
    if end_utc.tzinfo is None:
        end_utc = end_utc.replace(tzinfo=timezone.utc)
    if end_utc <= start_utc:
        return 0.0

    cur = start_utc.astimezone(NY_TZ)
    end_local = end_utc.astimezone(NY_TZ)
    total_hours = 0.0

    # Fast-forward full weeks if span is large
    days_diff = (end_local.date() - cur.date()).days
    if days_diff > 14:
        full_weeks = (days_diff - 7) // 7
        if full_weeks > 0:
            total_hours += full_weeks * 5 * HOURS_PER_DAY
            cur = cur + timedelta(days=full_weeks * 7)

    while cur < end_local:
        if cur.weekday() >= 5:
            cur = datetime.combine(cur.date() + timedelta(days=1), WORK_START, tzinfo=NY_TZ)
            continue
        day_start = datetime.combine(cur.date(), WORK_START, tzinfo=NY_TZ)
        day_end = datetime.combine(cur.date(), WORK_END, tzinfo=NY_TZ)
        seg_start = max(cur, day_start)
        seg_end = min(end_local, day_end)
        if seg_end > seg_start:
            total_hours += (seg_end - seg_start).total_seconds() / 3600.0
        cur = datetime.combine(cur.date() + timedelta(days=1), WORK_START, tzinfo=NY_TZ)

    return round(total_hours, 2)
