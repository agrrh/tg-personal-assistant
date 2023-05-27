import json
import logging

from lib.handler import Handler


class Manager:
    def __init__(
        self,
        jetstream: object,
        nats_subj_prefix: str,
        airtable: object,
        timespec: object,
    ) -> None:
        self.jetstream = jetstream
        self.nats_subj_prefix = nats_subj_prefix

        self.airtable = airtable
        self.timespec = timespec

        self.handler = Handler(airtable=airtable, timespec=timespec)

        self.commands = {
            "/health": self.handler.health,
            "/memo": self.handler.memo,
            "/remind": self.handler.remind,
            "/start": self.handler.start,
            "/help": self.handler.start,
        }

    async def do(self, message: object) -> None:
        logging.warning(f"received a message on: {message.subject}")

        req = json.loads(message.data)
        topic_id = req.get("chat").get("id")

        text = req.get("text")
        if text.startswith("/"):
            command = text.split(" ")[0]
            try:
                logging.warning(f"{command}: {text}")
                resp = await self.commands[command](req)
            except Exception as e:
                logging.error(f"could not handle request: {e}")
        else:
            resp = await self.handler.dunno(req)

        topic = f"{self.nats_subj_prefix}.{topic_id}"

        logging.warning(f"sending response message to bus: {topic}")
        await self.jetstream.publish(topic, resp)
        await message.ack()
