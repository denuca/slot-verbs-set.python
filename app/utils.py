class StringNormalizer:
    @staticmethod
    def normalize(value: str) -> str:
        return value.strip().casefold()

    @classmethod
    def normalize_list(cls, values: list[str]) -> list[str]:
        return [cls.normalize(v) for v in values]