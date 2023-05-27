import aioschedule
import asyncio
import logging
import nats
import os

from lib.timespec import Timespec
from lib.periodic import Periodic
from lib.airtabledb import AirtableDB

tz_name = os.environ.get("TZ", "UTC")

app_dev_mode = os.environ.get("APP_DEV")

app_name = os.environ.get("APP_NAME", "personal-assistant")

nats_address = os.environ.get("NATS_ADDR", "nats://nats.nats.svc:4222")
nats_prefix = os.environ.get("NATS_PREFIX", "dummy")
nats_kv_bucket = os.environ.get("NATS_KV_BUCKET", "cron")

at_db = os.environ.get("AIRTABLE_DB")
at_tables = os.environ.get("AIRTABLE_TABLES", "foo:ID,bar:ID")
at_tables = {
    table.split(":")[0]: table.split(":")[1] for table in at_tables.split(",")
}  # "foo:ID,bar:ID" -> {foo: ID, bar: ID}
at_token = os.environ.get("AIRTABLE_TOKEN")

nats_subj_out = f"{nats_prefix}.tg.out"


async def main() -> None:
    logging.warning(f"connecting to NATS at: {nats_address}")
    nc = await nats.connect(nats_address)

    js = nc.jetstream()
    kv = await js.create_key_value(bucket=nats_kv_bucket)

    timespec = Timespec(tz_name=tz_name)

    airtable = AirtableDB(db=at_db, tables=at_tables, token=at_token)
    periodic = Periodic(jetstream=js, kv=kv, airtable=airtable, timespec=timespec, nats_subj_prefix=nats_subj_out)

    if app_dev_mode:
        await periodic.do()
        return None

    logging.warning("planning jobs")

    aioschedule.every().minute.do(periodic.do)

    logging.warning("running loop")

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


if __name__ == "__main__":
    logging.critical("starting app")

    asyncio.run(main())
