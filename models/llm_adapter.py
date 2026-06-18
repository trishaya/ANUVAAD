import os
import requests

from dotenv import load_dotenv


# =========================================================
# Environment Setup
# =========================================================

load_dotenv()


# =========================================================
# Language Code Mapping
# =========================================================

LANGUAGE_CODE_MAP = {

    "en": "en-IN",
    "hi": "hi-IN",
    "bn": "bn-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "mr": "mr-IN",
    "pa": "pa-IN",
    "or": "od-IN",

    "as": "as-IN",
    "brx": "brx-IN",
    "doi": "doi-IN",
    "kok": "kok-IN",
    "ks": "ks-IN",
    "mai": "mai-IN",
    "mni": "mni-IN",
    "ne": "ne-IN",
    "sa": "sa-IN",
    "sat": "sat-IN",
    "sd": "sd-IN",
    "ur": "ur-IN"
}


# =========================================================
# LLM Adapter
# =========================================================

class LLMAdapter:

    def __init__(self):

        self.api_key = os.getenv(
            "SARVAM_API_KEY"
        )

        self.translation_url = (
            "https://api.sarvam.ai/translate"
        )

        if not self.api_key:

            raise ValueError(
                "SARVAM_API_KEY not found"
            )

    # =====================================================
    # Mayura Language Support
    # =====================================================

    def is_mayura_supported(
        self,
        lang_code
    ):

        mayura_languages = {

            "en",
            "hi",
            "bn",
            "gu",
            "kn",
            "ml",
            "mr",
            "or",
            "pa",
            "ta",
            "te"
        }

        return lang_code in mayura_languages

    # =====================================================
    # Intelligent Model Selection
    # =====================================================

    def select_model(
        self,
        source_lang,
        target_lang,
        text
    ):

        """
        Intelligent routing.
        """

        # =================================================
        # Large Text
        # =================================================

        if len(text.split()) > 120:

            print(
                "Large text → sarvam-translate:v1"
            )

            return "sarvam-translate:v1"

        # =================================================
        # Supported Languages
        # =================================================

        if (

            self.is_mayura_supported(
                source_lang
            )

            and

            self.is_mayura_supported(
                target_lang
            )
        ):

            print(
                "Using mayura:v1"
            )

            return "mayura:v1"

        # =================================================
        # Fallback
        # =================================================

        print(
            "Using sarvam-translate:v1"
        )

        return "sarvam-translate:v1"

    # =====================================================
    # Text Chunking
    # =====================================================

    def split_text(
        self,
        text,
        max_len=1500
    ):

        """
        Preserve paragraphs while splitting.
        """

        if len(text) <= max_len:

            return [text]

        paragraphs = text.split("\n")

        chunks = []

        current_chunk = ""

        for para in paragraphs:

            if (

                len(current_chunk)
                + len(para)

                < max_len
            ):

                current_chunk += (
                    para + "\n"
                )

            else:

                chunks.append(
                    current_chunk.strip()
                )

                current_chunk = (
                    para + "\n"
                )

        if current_chunk.strip():

            chunks.append(
                current_chunk.strip()
            )

        return chunks

    # =====================================================
    # Translation API Call
    # =====================================================

    def call_api(
        self,
        text,
        source_lang,
        target_lang,
        mode="formal",
        output_script=None,
        numerals_format="international"
    ):

        """
        Calls Sarvam Translation API.
        """

        model = self.select_model(

            source_lang,
            target_lang,
            text
        )

        # =================================================
        # Unsupported Features
        # =================================================

        if model == "sarvam-translate:v1":

            mode = "formal"

            output_script = None

        # =================================================
        # Language Codes
        # =================================================

        source_code = (
            LANGUAGE_CODE_MAP.get(
                source_lang,
                "en-IN"
            )
        )

        target_code = (
            LANGUAGE_CODE_MAP.get(
                target_lang,
                "en-IN"
            )
        )

        # =================================================
        # Headers
        # =================================================

        headers = {

            "api-subscription-key":
                self.api_key,

            "Content-Type":
                "application/json"
        }

        # =================================================
        # Payload
        # =================================================

        payload = {

            "input": text,

            "source_language_code":
                source_code,

            "target_language_code":
                target_code,

            "mode":
                mode,

            "model":
                model,

            "numerals_format":
                numerals_format
        }

        if output_script:

            payload["output_script"] = (
                output_script
            )

        print(
            "TRANSLATION PAYLOAD:",
            payload
        )

        # =================================================
        # API Call
        # =================================================

        try:

            response = requests.post(

                self.translation_url,

                headers=headers,

                json=payload,

                timeout=8
            )

            print(
                "SARVAM STATUS:",
                response.status_code
            )

            if response.status_code != 200:

                print(
                    "SARVAM ERROR:",
                    response.text
                )

                return ""

            data = response.json()

            translated_text = (
                data.get(
                    "translated_text",
                    ""
                )
            )

            print(
                "TRANSLATED:",
                translated_text
            )

            return translated_text.strip()

        except requests.exceptions.Timeout:

            print(
                "SARVAM TIMEOUT"
            )

            return ""

        except Exception as error:

            print(
                "SARVAM ERROR:",
                str(error)
            )

            return ""

    # =====================================================
    # Main Translation Pipeline
    # =====================================================

    def translate(
        self,
        text,
        target_lang="en",
        source_lang="en",
        mode="formal",
        output_script=None,
        numerals_format="international"
    ):

        """
        Main translation workflow.
        """

        if not text:

            return ""

        try:

            chunks = self.split_text(
                text
            )

            translated_chunks = []

            for chunk in chunks:

                translated = self.call_api(

                    text=chunk,

                    source_lang=source_lang,

                    target_lang=target_lang,

                    mode=mode,

                    output_script=output_script,

                    numerals_format=
                        numerals_format
                )

                if translated:

                    translated_chunks.append(
                        translated
                    )

            final_output = "\n".join(
                translated_chunks
            ).strip()

            return final_output

        except Exception as error:

            print(
                "TRANSLATION ERROR:",
                str(error)
            )

            return "Translation error"