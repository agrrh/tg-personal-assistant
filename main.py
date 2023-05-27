import asyncio
import logging
import nats
import os

from lib.timespec import Timespec
from lib.manager import Manager
from lib.airtabledb import AirtableDB

tz_name = os.environ.get("TZ", "UTC")

app_name = os.environ.get("APP_NAME", "personal-assistant")

nats_address = os.environ.get("NATS_ADDR", "nats://nats.nats.svc:4222")
nats_prefix = os.environ.get("NATS_PREFIX", "dummy")

at_db = os.environ.get("AIRTABLE_DB")
at_tables = os.environ.get("AIRTABLE_TABLES", "foo:ID,bar:ID")
at_tables = {
    table.split(":")[0]: table.split(":")[1] for table in at_tables.split(",")
}  # "foo:ID,bar:ID" -> {foo: ID, bar: ID}
at_token = os.environ.get("AIRTABLE_TOKEN")

nats_subj_in = f"{nats_prefix}.tg.in"
nats_subj_out = f"{nats_prefix}.tg.out"


async def main() -> None:
    logging.warning(f"connecting to NATS at: {nats_address}")
    nc = await nats.connect(nats_address)

    js = nc.jetstream()

    timespec = Timespec(tz_name=tz_name)

    airtable = AirtableDB(db=at_db, tables=at_tables, token=at_token)
    manager = Manager(jetstream=js, airtable=airtable, nats_subj_prefix=nats_subj_out, timespec=timespec)

    logging.warning(f"getting updates for subject: {nats_subj_in}.>")

    await js.subscribe(f"{nats_subj_in}.>", "worker", cb=manager.do)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    logging.critical("starting app")

    asyncio.run(main())
