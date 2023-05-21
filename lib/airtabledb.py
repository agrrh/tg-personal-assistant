import os

from datetime import datetime
from pytz import timezone

from pyairtable import Table
from pyairtable.formulas import match as airtable_match


class AirtableDB:
    def __init__(self, db: str, tables: dict, token: str) -> None:
        self.tables = {t: Table(token, db, tables[t]) for t, _ in tables.items()}

    async def get_time(self, normalize: bool = True) -> str:
        tz = timezone(os.environ.get("TZ", "UTC"))
        dt = datetime.now(tz)
        if normalize:
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            dt = dt.astimezone(timezone("UTC"))
            dt = dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")

        return dt  # noqa: PIE781

    async def upsert(self, table_name: str, data: dict) -> None:
        t = self.tables[table_name]

        dt = await self.get_time()

        date_part = {
            "date": dt,
        }

        formula = airtable_match(date_part)
        r = t.first(formula=formula)

        data.update(date_part)

        if r:
            t.update(r.get("id"), data)
        else:
            t.create(data)
