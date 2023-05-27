import datetime
import logging
import nats
import json

from aiocache import cached


class Periodic:
    TEXT_RESP = "\n".join(
        (
            "Подведем итоги дня! 😼",
            "",
            "Пришли мне команды по тем направлениям, которые готов выделить:",
            "",
            "`/health` 👍 или 👎",
            "",
            "`/memo` одно событие, которым запомнился день",
        ),
    )

    def __init__(
        self,
        jetstream: object,
        kv: object,
        airtable: object,
        timespec: object,
        nats_subj_prefix: str,
    ) -> None:
        self.jetstream = jetstream
        self.kv = kv
        self.airtable = airtable
        self.timespec = timespec
        self.nats_subj_prefix = nats_subj_prefix

    @cached(ttl=3600)
    async def get_users(self) -> list:
        data = []

        try:
            data = self.airtable.tables["users"].all()
        except Exception as e:
            logging.error(f"could not get users: {e}")

        return data

    async def do(self) -> None:
        users = await self.get_users()

        try:
            last_run_kv = await self.kv.get("last_run")
        except nats.js.errors.NotFoundError:
            last_run_dt = await self.timespec.this_minute()
            last_run_dt -= datetime.timedelta(hours=12)
        else:
            last_run_dt = await self.timespec.from_string(last_run_kv.value.decode())

        logging.warning(f"last run: {last_run_dt}")

        today_dt = await self.timespec.today()

        now_dt = await self.timespec.now()
        logging.warning(f"current time: {now_dt}")

        for u in users:
            tg_id = u.get("fields").get("tg_id")
            remind_time = u.get("fields").get("remind_time") or "22:00"
            remind_tz = u.get("fields").get("remind_tz") or self.timespec.tz_name

            remind_dt = await self.timespec.specific_time(remind_time, tz_name=remind_tz)

            logging.warning(f"{tg_id} wants remind at {remind_dt} ({remind_tz})")

            if remind_dt > today_dt and remind_dt > last_run_dt and remind_dt <= now_dt:
                logging.warning(f"sending remind for {tg_id}")

                message = {
                    "chat": tg_id,
                    # "reply_to": None,
                    "text": self.TEXT_RESP,
                }

                await self.send(tg_id, message)

        now_dt_string = await self.timespec.to_string(now_dt)
        await self.kv.put("last_run", now_dt_string.encode())

    async def send(self, tg_id: int, message: dict) -> None:
        topic = f"{self.nats_subj_prefix}.{tg_id}"

        logging.warning(f"sending message to bus: {topic}")

        message = json.dumps(message).encode()

        await self.jetstream.publish(topic, message)
