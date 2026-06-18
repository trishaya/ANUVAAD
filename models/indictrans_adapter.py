import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor


class IndicTransAdapter:
    """
    Adapter for IndicTrans2 model (Indian-to-Indian translation).

    Responsibilities:
    - Load model and tokenizer
    - Handle language mapping
    - Preprocess and postprocess using IndicProcessor
    - Perform translation with safe fallback handling
    """

    def __init__(self):

        # Select device (GPU if available)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Recommended stable model (balanced size + performance)
        self.model_name = "ai4bharat/indictrans2-indic-indic-dist-320M"

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        # Load model
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            trust_remote_code=True
        ).to(self.device)

        # Set model to evaluation mode
        self.model.eval()

        # Language code mapping (ISO → IndicTrans format)
        self.lang_map = {
            "hi": "hin_Deva",
            "bn": "ben_Beng",
            "as": "asm_Beng",
            "gu": "guj_Gujr",
            "kn": "kan_Knda",
            "ml": "mal_Mlym",
            "mr": "mar_Deva",
            "or": "ory_Orya",
            "pa": "pan_Guru",
            "ta": "tam_Taml",
            "te": "tel_Telu",
            "ur": "urd_Arab",
            "ne": "npi_Deva",
            "sd": "snd_Arab",
            "si": "sin_Sinh",
            "ks": "kas_Arab",
            "mai": "mai_Deva",
            "sa": "san_Deva",
            "mni": "mni_Beng",
            "doi": "doi_Deva",
            "kok": "gom_Deva",
            "brx": "brx_Deva",
            "sat": "sat_Olck",
            "en": "eng_Latn"
        }

        # Indic preprocessing toolkit
        self.processor = IndicProcessor(inference=True)

    def safe_lang(self, lang, default):
        """Ensure language is supported, else fallback."""
        lang = (lang or "").lower()
        return lang if lang in self.lang_map else default

    def translate(self, text, source_lang, target_lang="en"):
        """
        Perform translation using IndicTrans2.

        Args:
            text (str): Input text
            source_lang (str): Source language (ISO code)
            target_lang (str): Target language (ISO code)

        Returns:
            str: Translated output
        """

        if not text or not text.strip():
            return ""

        try:
            # Normalize language codes
            source_lang = self.safe_lang(source_lang, "hi")
            target_lang = self.safe_lang(target_lang, "en")

            src_lang = self.lang_map[source_lang]
            tgt_lang = self.lang_map[target_lang]

            # --- Preprocessing ---
            batch = self.processor.preprocess_batch(
                [text],
                src_lang=src_lang,
                tgt_lang=tgt_lang
            )

            # --- Tokenization ---
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)

            # --- Inference ---
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=60,
                    num_beams=1,
                    do_sample=False
                )

            # --- Decode ---
            decoded = self.tokenizer.batch_decode(
                outputs,
                skip_special_tokens=True
            )

            # --- Postprocess ---
            translations = self.processor.postprocess_batch(
                decoded,
                lang=tgt_lang
            )

            result = translations[0].strip()

            return result if result else ""

        except RuntimeError as e:
            # GPU OOM or runtime failure
            print("IndicTrans Runtime Error:", str(e))
            return ""

        except Exception as e:
            # General failure (never crash system)
            print("IndicTrans Error:", str(e))
            return ""