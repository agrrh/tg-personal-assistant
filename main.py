import asyncio
import logging
import nats
import os

from lib.handler import Handler

app_name = os.environ.get("APP_NAME", "personal-assistant")

nats_address = os.environ.get("NATS_ADDR", "nats://nats.nats.svc:4222")
nats_prefix = os.environ.get("NATS_PREFIX", "dummy")

nats_subj_in = f"{nats_prefix}.tg.in"
nats_subj_out = f"{nats_prefix}.tg.out"


async def main() -> None:
    logging.warning(f"connecting to NATS at: {nats_address}")
    nc = await nats.connect(nats_address)

    js = nc.jetstream()

    handler = Handler(jetstream=js, nats_subj_response=nats_subj_out)

    logging.warning(f"getting updates for subject: {nats_subj_in}.>")

    await js.subscribe(f"{nats_subj_in}.>", "worker", cb=handler.echo)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    logging.critical("starting app")

    asyncio.run(main())
