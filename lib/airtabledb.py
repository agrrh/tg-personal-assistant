from pyairtable import Table
from pyairtable.formulas import match as airtable_match


class AirtableDB:
    def __init__(self, db: str, tables: dict, token: str) -> None:
        self.tables = {t: Table(token, db, tables[t]) for t, _ in tables.items()}

    async def upsert_by_fields(self, table_name: str, data: dict, fields: list) -> None:
        t = self.tables[table_name]

        formula = airtable_match({k: v for k, v in data.items() if k in fields})
        r = t.first(formula=formula)

        if r:
            t.update(r.get("id"), data)
        else:
            t.create(data)
