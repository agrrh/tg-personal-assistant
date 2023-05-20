import json
import logging


class Handler:
    def __init__(self, jetstream: object, nats_subj_response: str) -> None:
        self.jetstream = jetstream
        self.nats_subj_response = nats_subj_response

    async def echo(self, message: object) -> None:
        logging.warning(f"received a message on: {message.subject}")
        req = json.loads(message.data)

        logging.debug(f"request: {req}")

        chat_id = req.get("chat").get("id")
        nats_subject = f"{self.nats_subj_response}.{chat_id}"

        chat = req.get("chat").get("id")
        reply_to = req.get("message_id")
        text = req.get("text")

        resp = {
            "chat": chat,
            "reply_to": reply_to,
            "text": text,
        }

        resp_msg = json.dumps(resp).encode()
        logging.debug(f"response: {resp_msg}")

        logging.warning(f"sending response message to bus: {nats_subject}")
        await self.jetstream.publish(nats_subject, resp_msg)
        await message.ack()
