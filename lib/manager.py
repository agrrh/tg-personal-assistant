import json
import logging


class Manager:
    def __init__(self, jetstream: object, nats_subj_prefix: str, handler: object) -> None:
        self.jetstream = jetstream
        self.nats_subj_prefix = nats_subj_prefix

        self.handler = handler

        self.commands = {
            "/health": self.handler.health,
            "/memo": self.handler.memo,
        }

    async def do(self, message: object) -> None:
        logging.warning(f"received a message on: {message.subject}")

        req = json.loads(message.data)
        topic_id = req.get("chat").get("id")

        text = req.get("text")

        if text.startswith("/"):
            try:
                resp = await self.commands[text.split(" ")[0]](req)
            except Exception as e:
                logging.error(f"could not handle request {e}")
        else:
            resp = await self.handler.dunno(req)

        topic = f"{self.nats_subj_prefix}.{topic_id}"

        logging.warning(f"sending response message to bus: {topic}")
        await self.jetstream.publish(topic, resp)
        await message.ack()
