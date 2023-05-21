import logging


class Rating:
    RATING_TABLE = {
        "👍": 3,
        "👎": 1,
    }

    def get_from_text(self, text: str) -> int:
        if not text:
            rating = 2
        elif text in self.RATING_TABLE:
            rating = self.RATING_TABLE[text]
        else:
            try:
                rating = int(text)
            except Exception:
                logging.warning(f"could not convert {text} to rating")

        if rating > 3 or rating < 1:
            raise ValueError

        return rating
