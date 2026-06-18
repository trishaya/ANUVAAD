import re


class LanguageDetector:

    def __init__(self):
        pass

    def detect(self, text):

        text = text.strip()

        # English / Roman
        if all(ord(c) < 128 for c in text):
            return "en"

        #Devanagari (Hindi, Marathi, Nepali, Sanskrit, etc.)
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"

        #Bengali script (Bengali, Assamese, Manipuri)
        if re.search(r'[\u0980-\u09FF]', text):
            if "ৰ" in text or "ৱ" in text:
                return "as"
            return "bn"

        #Tamil
        if re.search(r'[\u0B80-\u0BFF]', text):
            return "ta"

        #Telugu
        if re.search(r'[\u0C00-\u0C7F]', text):
            return "te"

        #Kannada
        if re.search(r'[\u0C80-\u0CFF]', text):
            return "kn"

        #Malayalam
        if re.search(r'[\u0D00-\u0D7F]', text):
            return "ml"

        # Punjabi (Gurmukhi)
        if re.search(r'[\u0A00-\u0A7F]', text):
            return "pa"

        # Gujarati
        if re.search(r'[\u0A80-\u0AFF]', text):
            return "gu"

        # Odia
        if re.search(r'[\u0B00-\u0B7F]', text):
            return "or"

        # Sinhala
        if re.search(r'[\u0D80-\u0DFF]', text):
            return "si"

        # Arabic script (Urdu, Sindhi)
        if re.search(r'[\u0600-\u06FF]', text):
            return "ur"

        # Ol Chiki (Santali)
        if re.search(r'[\u1C50-\u1C7F]', text):
            return "sat"

        # fallback
        return "hi"