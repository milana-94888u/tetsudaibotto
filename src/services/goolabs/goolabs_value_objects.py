from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Literal

from .goolabs_value_types import (
    NamedEntityType,
    KanaType,
    KeywordFocusType,
    MorphemeInfoType,
    PartOfSpeechType,
    SlotType,
)


class GoolabsDatetime(datetime):
    def __new__(cls, *args, **kwargs) -> GoolabsDatetime:
        self = datetime.__new__(cls, *args, **kwargs)
        self.is_month_set = True
        self.is_day_set = True
        return self

    @classmethod
    def from_goolabs_format(cls, date_string: str) -> GoolabsDatetime:
        try:
            dt = cls.fromisoformat(date_string)
            dt.is_month_set = True
            dt.is_day_set = True
        except ValueError as ex:
            match date_string.split("-"):
                case [str(year)] if year.isdecimal():
                    dt = cls(int(year), 1, 1)
                    dt.is_month_set = False
                    dt.is_day_set = False
                case [str(year), str(month)] if year.isdecimal() and month.isdecimal():
                    dt = cls(int(year), int(month), 1)
                    dt.is_month_set = True
                    dt.is_day_set = False
                case _:
                    raise ex
        return dt

    def to_goolabs_format(self, *args, **kwargs) -> str:
        if self.is_day_set:
            return super().isoformat(*args, **kwargs)
        if self.is_month_set:
            return f"{self.year}-{self.month}"
        return str(self.year)


@dataclass
class NormalizedTime:
    text: str
    time: GoolabsDatetime


@dataclass
class NamedEntity:
    text: str
    entity_type: NamedEntityType


@dataclass
class Keyword:
    text: str
    score: float


@dataclass
class AnalyzedMorpheme:
    form: str | None
    pos: PartOfSpeechType | None
    read: str | None


AnalyzedSentence = list[AnalyzedMorpheme]


@dataclass
class NameSlot:
    surname: str
    given_name: str


@dataclass
class BirthdaySlot:
    value: str
    norm_value: date | None


@dataclass
class SexSlot:
    value: str
    norm_value: Literal["男性", "女性"]


@dataclass
class AddressSlot:
    value: str
    norm_value: str
    latitude: float
    longitude: float


@dataclass
class TelephoneSlot:
    value: str
    norm_value: str


@dataclass
class AgeSlot:
    value: str | None
    norm_value: int | None


@dataclass
class NormalizedTimes:
    datetime_list: list[NormalizedTime]
    doc_time: GoolabsDatetime


@dataclass
class ExtractedNamedEntities:
    entities: list[NamedEntity]
    class_filter: list[NamedEntityType]


@dataclass
class ConvertedToFurigana:
    text: str
    kana_type: KanaType


@dataclass
class ExtractedKeywords:
    keywords: list[Keyword]
    focus: KeywordFocusType | None


@dataclass
class AnalyzedMorphology:
    word_list: list[AnalyzedSentence]
    info_filter: list[MorphemeInfoType]
    pos_filter: list[PartOfSpeechType]


@dataclass
class ExtractedSlotValues:
    name: list[NameSlot] | None
    birthday: list[BirthdaySlot] | None
    sex: list[SexSlot] | None
    address: list[AddressSlot] | None
    telephone: list[TelephoneSlot] | None
    age: list[AgeSlot] | None
    slot_filter: list[SlotType]


@dataclass
class CalculatedSimilarity:
    score: float
