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

    async def upsert_by_fields(self, table_name: str, data: dict, fields: list) -> None:
        t = self.tables[table_name]

        formula = airtable_match({k: v for k, v in data.items() if k in fields})
        r = t.first(formula=formula)

        if r:
            t.update(r.get("id"), data)
        else:
            t.create(data)
