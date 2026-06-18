import os
import re
import requests


class Transliterator:

    def __init__(self):

        self.api_key = os.getenv(
            "SARVAM_API_KEY"
        )

        self.url = (
            "https://api.sarvam.ai/transliterate"
        )

    # =========================================
    # Romanized Hindi → Native Hindi
    # =========================================

    def to_hindi(self, text: str):

        try:

            if not text or not text.strip():

                return text

            # =====================================
            # Normalize Input
            # =====================================

            normalized = text.lower().strip()

            replacements = {

                r"\brha\b": "raha",
                r"\brhi\b": "rahi",
                r"\bhu\b": "hoon",
                r"\bhun\b": "hoon",
                r"\bkr\b": "kar",
                r"\bacha\b": "accha",
                r"\bkese\b": "kaise",
                r"\bkyu\b": "kyon",
                r"\bkaha\b": "kahaan",
                r"\bm\b": "main"

            }

            for pattern, replacement in replacements.items():

                normalized = re.sub(
                    pattern,
                    replacement,
                    normalized
                )

            # =====================================
            # Request Payload
            # =====================================

            payload = {

                "input": normalized,

                "source_language_code":
                    "en-IN",

                "target_language_code":
                    "hi-IN"
            }

            headers = {

                "api-subscription-key":
                    self.api_key,

                "Content-Type":
                    "application/json"
            }

            # =====================================
            # API Request
            # =====================================

            response = requests.post(

                self.url,

                json=payload,

                headers=headers,

                timeout=15
            )

            print(
                "TRANSLITERATION STATUS:",
                response.status_code
            )

            # =====================================
            # Handle HTTP Errors
            # =====================================

            if response.status_code != 200:

                print(
                    "TRANSLITERATION FAILED:",
                    response.text
                )

                return text

            # =====================================
            # Parse JSON Safely
            # =====================================

            try:

                data = response.json()

            except Exception:

                print(
                    "INVALID JSON RESPONSE"
                )

                return text

            print(
                "TRANSLITERATION RESPONSE:",
                data
            )

            # =====================================
            # Extract Output
            # =====================================

            transliterated = data.get(
                "transliterated_text"
            )

            if transliterated:

                return transliterated

            # =====================================
            # Fallback
            # =====================================

            return text

        except Exception as error:

            print(
                "Transliteration Error:",
                str(error)
            )

            return text