import logging
import pytz

import datetime


class Timespec:
    def __init__(self, tz_name: str = "UTC") -> None:
        self.tz_name = tz_name
        self.tz = pytz.timezone(tz_name)

    async def now(self) -> datetime.datetime:
        return datetime.datetime.now(self.tz).astimezone(self.tz)

    async def today(self) -> datetime.datetime:
        dt = await self.now()
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    async def this_minute(self) -> datetime.datetime:
        return await self.now().replace(second=0, microsecond=0)

    async def specific_time(self, notation: str, tz_name: str) -> datetime.datetime:
        tz = pytz.timezone(tz_name or self.tz_name)

        try:
            h, m = notation.split(":")
        except Exception as e:
            logging.error(f'could not decode time notation "{notation}": {e}')

        dt_now = await self.today()
        dt_now = dt_now.astimezone(tz)

        return dt_now.replace(hour=int(h), minute=int(m))

    async def to_string(self, dt: datetime.datetime, as_utc: bool = False) -> str:
        if as_utc:
            dt = dt.astimezone(pytz.timezone("UTC"))
        return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    async def to_airtable_string(self, dt: datetime.datetime) -> str:
        return await self.to_string(dt, as_utc=True)

    async def from_string(self, s: str) -> datetime.datetime:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))

    async def from_airtable_string(self, s: str) -> datetime.datetime:
        return await self.from_string(s)
