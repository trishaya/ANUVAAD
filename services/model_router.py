from models.llm_adapter import LLMAdapter
from models.indictrans_adapter import IndicTransAdapter
from services.transliterator import Transliterator
import re
import redis
import json


class ModelRouter:
    def __init__(self):

        # =================================================
        # Initialize Primary Translation Model
        # =================================================

        self.llm = LLMAdapter()

        # =================================================
        # Lazy Loaded IndicTrans
        # =================================================

        self.indic = None

        # =================================================
        # Transliterator
        # =================================================

        self.transliterator = Transliterator()

        # =================================================
        # Simple In-Memory Cache
        # =================================================

        self.redis_client = redis.Redis(
             host="localhost",
             port=6379,
             db=0,
             decode_responses=True
        )

        print("Redis Connected:",
             self.redis_client.ping())

    # =====================================================
    # Lazy Load IndicTrans
    # =====================================================

    def load_indic_model(self):

        """
        Loads IndicTrans only when needed.
        """

        if self.indic is None:

            print("Loading IndicTrans...")

            self.indic = IndicTransAdapter()

    # =====================================================
    # Detect Romanized Indian Language
    # =====================================================

    def is_roman_text(self, text):

        """
        Detects Romanized Indian language.
        """

        if not text:
            return False

        text = text.lower().strip()

        # ================================================
        # Common English Words
        # ================================================

        common_english = {

            "the", "is", "are", "you",
            "hello", "replace", "file",
            "good", "morning", "thank",
            "please", "what", "where",
            "how", "this", "that",
            "project", "report",
            "deadline", "extended",
            "send", "tomorrow",
            "meeting"
        }

        # ================================================
        # Conversational Indian Markers
        # ================================================

        indian_markers = {

            "hai", "hun", "hoon",
            "mera", "tera", "tum",
            "kya", "kyu", "kaise",
            "acha", "accha",
            "kal", "ghar",
            "raha", "rahi",
            "rahe", "milte",
            "baad", "koribo",
            "ache", "jaa",
            "kaha", "kahaan"
        }

        words = text.split()

        # ================================================
        # Count English Matches
        # ================================================

        english_matches = sum(

            1 for word in words
            if word in common_english
        )

        # ================================================
        # Count Indian Markers
        # ================================================

        indian_matches = sum(

            1 for word in words
            if word in indian_markers
        )

        # ================================================
        # Strong Romanized Conversational Signal
        # ================================================

        if indian_matches >= 1:

            return True

        # ================================================
        # Strong English Signal
        # ================================================

        if (

            english_matches >= 2

            and indian_matches == 0

        ):

            return False

        # ================================================
        # Latin Character Ratio
        # ================================================

        latin_chars = sum(

            1 for c in text
            if c.isascii() and c.isalpha()
        )

        total_chars = len(text) or 1

        return (
            latin_chars / total_chars
        ) > 0.6

    # =====================================================
    # Detect Code-Mixed Text
    # =====================================================

    def is_code_mixed(self, text):

        """
        Detects mixed native + Latin script.
        """

        has_latin = bool(
            re.search(r'[A-Za-z]', text)
        )

        has_native = bool(
            re.search(
                r'[\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF]',
                text
            )
        )

        return has_latin and has_native

    # =====================================================
    # Cache Helpers
    # =====================================================

    def get_cache_key(

        self,

        text,

        source_lang,

        target_lang,

        model,

        output_script,

        numerals_format
    ):

        return (

            f"{text.strip()}:"
            f"{source_lang}:"
            f"{target_lang}:"
            f"{model}:"
            f"{output_script}:"
            f"{numerals_format}"
        )

    def save_to_cache(

        self,

        key,

        value
    ):
       print("Saving to redis:", key)
       self.redis_client.setex(key, 3600, json.dumps(value))
       print("Redis save complete")
    # =====================================================
    # Main Translation Router
    # =====================================================

    def translate(

        self,

        text,

        source_lang=None,

        target_lang=None,

        model=None,

        mode="formal",

        output_script=None,

        numerals_format="international"
    ):

        # =================================================
        # Default Languages
        # =================================================

        if not source_lang:

            source_lang = "en"

        target_lang = target_lang or "en"

        # =================================================
        # Romanized Preprocessing
        # =================================================

        if (

            self.is_roman_text(text)

            and source_lang == "hi"

        ):

            print(
                "Romanized text detected → Transliteration"
            )

            text = self.transliterator.to_hindi(
                text
            )

            print(
                "TRANSLITERATED:",
                text
            )

        # =================================================
        # CACHE CHECK
        # =================================================

        cache_key = self.get_cache_key(

            text,

            source_lang,

            target_lang,

            model,

            output_script,

            numerals_format
        )

        cached_value = self.redis_client.get(cache_key)
        print("Cache Lookup:", cache_key)
        if cached_value:

            print("CACHE HIT")

            return json.loads(cached_value)

        # =================================================
        # MANUAL MODEL OVERRIDE
        # =================================================

        if model == "indic":

            try:

                self.load_indic_model()

                translated = self.indic.translate(

                    text,

                    source_lang,

                    target_lang
                )

                result = {

                    "translated_text":
                        translated,

                    "model_used":
                        "IndicTrans"
                }

                self.save_to_cache(
                    cache_key,
                    result
                )

                return result

            except Exception as error:

                print(
                    "IndicTrans Error:",
                    error
                )

        # =================================================
        # PRIMARY TRANSLATION
        # =================================================

        translated = ""

        primary_model = (
            "Sarvam Translation API"
        )

        try:

            translated = self.llm.translate(

                text=text,

                source_lang=source_lang,

                target_lang=target_lang,

                mode=mode,

                output_script=
                    output_script,

                numerals_format=
                    numerals_format
            )

        except Exception as error:

            print(
                "Sarvam failed:",
                error
            )

        # =================================================
        # FALLBACK TO INDICTRANS
        # =================================================

        if not translated:

            print(
                "Fallback → IndicTrans"
            )

            try:

                self.load_indic_model()

                translated = self.indic.translate(

                    text,

                    source_lang,

                    target_lang
                )

                primary_model = (
                    "IndicTrans Fallback"
                )

            except Exception as error:

                print(
                    "IndicTrans failed:",
                    error
                )

                translated = (
                    "Translation failed"
                )

        # =================================================
        # FINAL RESULT
        # =================================================

        result = {

            "translated_text":
                translated,

            "model_used":
                primary_model
        }

        self.save_to_cache(
            cache_key,
            result
        )

        return result