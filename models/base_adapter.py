class BaseModelAdapter:
    def translate(self, text: str, target_lang: str):
        raise NotImplementedError("Subclasses must implement translate()")