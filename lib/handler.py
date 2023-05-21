import json
import logging

from lib.rating import Rating


class Handler:
    def __init__(self, airtable: object) -> None:
        self.airtable = airtable

    async def echo(self, req: object) -> None:
        logging.debug(f"request: {req}")

        # ---

        chat_id = req.get("chat").get("id")
        reply_to = req.get("message_id")
        text = req.get("text")

        resp = {
            "chat": chat_id,
            "reply_to": reply_to,
            "text": text,
        }

        # ---

        resp_msg = json.dumps(resp).encode()
        logging.debug(f"response: {resp_msg}")

        return resp_msg

    async def memo(self, req: object) -> None:
        logging.debug(f"request: {req}")

        # ---

        chat_id = req.get("chat").get("id")
        reply_to = req.get("message_id")
        text = req.get("text")

        text = " ".join(text.split(" ")[1:]).strip()

        try:
            await self.airtable.upsert("memo", {"memo": text})
            text = "Done! 😼"
        except Exception as e:
            logging.error(f"could not upsert data: {e}")
            text = "Something went wrong! 🙀"

        resp = {
            "chat": chat_id,
            "reply_to": reply_to,
            "text": text,
        }

        # ---

        resp_msg = json.dumps(resp).encode()
        logging.debug(f"response: {resp_msg}")

        return resp_msg

    async def health(self, req: object) -> None:
        logging.debug(f"request: {req}")

        # ---

        chat_id = req.get("chat").get("id")
        reply_to = req.get("message_id")
        text = req.get("text")

        text = " ".join(text.split(" ")[1:]).strip()
        rating = Rating().get_from_text(text)

        try:
            await self.airtable.upsert("health", {"rating": rating})
            text = "Done! 😼"
        except Exception as e:
            logging.error(f"could not upsert data: {e}")
            text = "Something went wrong! 🙀"

        resp = {
            "chat": chat_id,
            "reply_to": reply_to,
            "text": text,
        }

        # ---

        resp_msg = json.dumps(resp).encode()
        logging.debug(f"response: {resp_msg}")

        return resp_msg

    async def dunno(self, req: object) -> None:
        logging.debug(f"request: {req}")

        # ---

        chat_id = req.get("chat").get("id")
        reply_to = req.get("message_id")
        text = "I don't understand 😿"

        resp = {
            "chat": chat_id,
            "reply_to": reply_to,
            "text": text,
        }

        # ---

        resp_msg = json.dumps(resp).encode()
        logging.debug(f"response: {resp_msg}")

        return resp_msg
