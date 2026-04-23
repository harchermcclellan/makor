from pydantic import BaseModel

class SefariaText(BaseModel):
    ref: str
    he_ref: str | None = None
    text: list | str | None = None
    he: list | str | None = None
    versions: list[dict] = []
    index: int | None=None

    # ... add more as needed

    model_config = {"extra": "allow"}  # don't error on unknown fields

class SefariaTopic(BaseModel):
    primary_title_en: str
    primary_title_he: str
    slug: str | None = None
    titles: list[dict] | None=None
    subclass: str | None=None
    description_en: str | None=None
    description_he: str | None=None
    sources: list[SefariaText] | None=None
    model_config = {"extra": "allow"}  # don't error on unknown fields

