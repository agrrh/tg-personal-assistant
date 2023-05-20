import asyncio
import logging
import nats
import os
import time

from lib.handler import Handler

app_name = os.environ.get("APP_NAME", "personal-assistant")

nats_address = os.environ.get("NATS_ADDR", "nats://nats.nats.svc:4222")
nats_prefix = os.environ.get("NATS_PREFIX")
nats_subj_inbox = os.environ.get("NATS_SUBJ_INBOX", "inbox")
nats_subj_response = os.environ.get("NATS_SUBJ_RESPONSE", "response")

nats_prefix = nats_prefix or app_name
nats_subj_in = f"{nats_prefix}.tg.{nats_subj_inbox}.>"
nats_subj_out = f"{nats_prefix}.tg.{nats_subj_response}"


async def main() -> None:
    logging.warning(f"connecting to NATS at: {nats_address}")
    nc = await nats.connect(nats_address)

    js = nc.jetstream()
    await js.add_stream(name=app_name, subjects=[nats_subj_out, f"{nats_subj_out}.*"])

    handler = Handler(jetstream=js, nats_subj_response=nats_subj_out)

    logging.warning(f"getting updates for subject: {nats_subj_in}")

    await js.subscribe(nats_subj_in, "workers", cb=handler.echo)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    logging.critical("starting app")

    asyncio.run(main())
