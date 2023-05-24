import json
import logging

from lib.rating import Rating
from lib.remind import Remind


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

    async def start(self, req: object) -> None:
        logging.debug(f"request: {req}")

        # ---

        chat_id = req.get("chat").get("id")
        reply_to = req.get("message_id")

        # TODO: Place a gif or video demo!
        text_resp = "\n".join(
            (
                "Hello, my name is Felix! 😼",
                "",
                "I'd be there for you to remember your most important deeds and to track your well-being!",
                "",
                "`/health` tracks your health",
                "",
                "`/memo` makes me memorize what was your best memory for today",
                "- keep memos practical to make an useful review later 📈",
                "- keep those lovely to have some nostalgic fun 😻",
            ),
        )

        resp = {
            "chat": chat_id,
            "reply_to": reply_to,
            "text": text_resp,
        }

        # ---

        resp_msg = json.dumps(resp).encode()
        logging.debug(f"response: {resp_msg}")

        return resp_msg

    async def remind(self, req: object) -> None:
        logging.debug(f"request: {req}")

        # ---

        text = req.get("text")

        text = " ".join(text.split(" ")[1:]).strip()

        chat_id = req.get("chat").get("id")
        reply_to = req.get("message_id")

        text_resp = "Done! 😼"

        if Remind.validate_time(text):
            await self.airtable.upsert_by_fields(
                "users",
                {
                    "tg_id": chat_id,
                    "remind_time": text,
                },
                fields=["tg_id"],
            )
        elif Remind.validate_tz(text):
            await self.airtable.upsert_by_fields(
                "users",
                {
                    "tg_id": chat_id,
                    "remind_tz": text,
                },
                fields=["tg_id"],
            )
        else:
            text_resp = "\n".join(
                (
                    "Invalid remind notation! 🙀",
                    "",
                    "Sample values:",
                    "- Time: `19:00`, `23:59`",
                    "- Timezone: `UTC`, `Europe/Moscow`",
                    "",
                    "Full timezones list:" "https://en.wikipedia.org/wiki/List_of_tz_database_time_zones",
                ),
            )

        resp = {
            "chat": chat_id,
            "reply_to": reply_to,
            "text": text_resp,
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

        date = await self.airtable.get_time()

        data = {
            "date": date,
            "memo": text,
        }

        try:
            await self.airtable.upsert_by_fields("memo", data, ("date",))
            text_resp = "Done! 😼"
        except Exception as e:
            logging.error(f"could not upsert data: {e}")
            text_resp = "Something went wrong! 🙀"

        resp = {
            "chat": chat_id,
            "reply_to": reply_to,
            "text": text_resp,
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

        date = await self.airtable.get_time()

        data = {
            "date": date,
            "rating": rating,
        }

        try:
            await self.airtable.upsert_by_fields("health", data, ("date",))
            text_resp = "Done! 😼"
        except Exception as e:
            logging.error(f"could not upsert data: {e}")
            text_resp = "Something went wrong! 🙀"

        resp = {
            "chat": chat_id,
            "reply_to": reply_to,
            "text": text_resp,
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
        text_resp = "I don't understand 😿"

        resp = {
            "chat": chat_id,
            "reply_to": reply_to,
            "text": text_resp,
        }

        # ---

        resp_msg = json.dumps(resp).encode()
        logging.debug(f"response: {resp_msg}")

        return resp_msg
