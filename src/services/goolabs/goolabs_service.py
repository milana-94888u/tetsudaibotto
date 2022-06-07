from datetime import datetime, date
from typing import Iterable, Literal, Type

import config
from goolabs import GoolabsAPI
from services.exceptions import UnexpectedGoolabsAPIResponseError
from .goolabs_value_objects import (
    NamedEntityType,
    KanaType,
    KeywordFocusType,
    MorphemeInfoType,
    PartOfSpeechType,
    SlotType,
    GoolabsDatetime,
    NormalizedTime,
    NamedEntity,
    Keyword,
    AnalyzedMorpheme,
    AnalyzedSentence,
    NameSlot,
    BirthdaySlot,
    SexSlot,
    AddressSlot,
    TelephoneSlot,
    AgeSlot,
    NormalizedTimes,
    ExtractedNamedEntities,
    ConvertedToFurigana,
    ExtractedKeywords,
    AnalyzedMorphology,
    ExtractedSlotValues,
    CalculatedSimilarity,
)
from .utils import (
    response_processing_method,
    goolabs_methods_class,
    convert_the_datetime_value_to_goolabs_format,
    convert_num_value_to_int_in_range,
    check_if_the_value_is_in_type_enum,
    convert_the_type_enum_value_to_string,
    convert_filters_to_goolabs_format,
    get_type_enum_from_response_filter_string,
    get_type_enum_list_from_response_filters_string,
)


def _create_goolabs_datetime(date_string: str) -> GoolabsDatetime:
    try:
        return GoolabsDatetime.from_goolabs_format(date_string)
    except ValueError:
        raise UnexpectedGoolabsAPIResponseError(
            f"{date_string=} has unexpected time format"
        )


def _create_normalized_time(time_entity: list[str, str]) -> NormalizedTime:
    match time_entity:
        case [str(text), str(time)]:
            return NormalizedTime(text, _create_goolabs_datetime(time))
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{time_entity=} has unexpected format"
            )


@response_processing_method([("doc_time", str), ("datetime_list", list)])
def _create_normalized_times_from_response(response: dict) -> NormalizedTimes:
    doc_time = _create_goolabs_datetime(response.get("doc_time"))
    datetime_list = [
        _create_normalized_time(time_entity)
        for time_entity in response.get("datetime_list")
    ]
    return NormalizedTimes(datetime_list, doc_time)


def _create_named_entity(entity: list[str, str]) -> NamedEntity:
    match entity:
        case [str(text), str(entity_type)] if check_if_the_value_is_in_type_enum(
            NamedEntityType, entity_type
        ):
            return NamedEntity(text, NamedEntityType(entity_type))
        case _:
            raise UnexpectedGoolabsAPIResponseError(f"{entity=} has unexpected format")


@response_processing_method([("ne_list", list)])
def _create_extracted_named_entities_from_response(
    response: dict,
) -> ExtractedNamedEntities:
    class_filter = get_type_enum_list_from_response_filters_string(
        NamedEntityType, response.get("class_filter")
    )
    ne_list = [_create_named_entity(entity) for entity in response.get("ne_list")]
    return ExtractedNamedEntities(ne_list, class_filter)


@response_processing_method([("output_type", str), ("converted", str)])
def _create_converted_to_furigana_from_response(response: dict) -> ConvertedToFurigana:
    match response:
        case {
            "output_type": "hiragana" | "katakana" as output_type,
            "converted": str(text),
        }:
            return ConvertedToFurigana(text, KanaType(output_type))
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{response=} has unexpected format"
            )


def _create_keyword(keyword_entity: dict[str, float]) -> Keyword:
    match keyword_entity:
        case {} if len(keyword_entity) == 1:
            match keyword_entity.popitem():
                case (str(text), float(score)):
                    return Keyword(text, score)
                case _:
                    raise UnexpectedGoolabsAPIResponseError(
                        f"{keyword_entity=} has unexpected format"
                    )
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{keyword_entity=} has unexpected format"
            )


@response_processing_method([("keywords", list)])
def _create_extracted_keywords_from_response(response: dict) -> ExtractedKeywords:
    focus = get_type_enum_from_response_filter_string(
        KeywordFocusType, response.get("focus")
    )
    keywords = [
        _create_keyword(keyword_entity) for keyword_entity in response.get("keywords")
    ]
    return ExtractedKeywords(keywords, focus)


def _create_analyzed_morpheme(
    info_filter: list[MorphemeInfoType], morpheme_entity: list[str]
) -> AnalyzedMorpheme:
    match morpheme_entity:
        case [*_] if len(morpheme_entity) == len(info_filter):
            entity_dict = dict(zip(info_filter, morpheme_entity))
            match (
                entity_dict.pop(MorphemeInfoType.FORM, None),
                entity_dict.pop(MorphemeInfoType.PART_OF_SPEECH, None),
                entity_dict.pop(MorphemeInfoType.READ, None),
            ):
                case str() | None as form, str() | None as pos, str() | None as read if entity_dict == {}:
                    return AnalyzedMorpheme(
                        form,
                        get_type_enum_from_response_filter_string(
                            PartOfSpeechType, pos
                        ),
                        read,
                    )
                case _:
                    raise UnexpectedGoolabsAPIResponseError(
                        f"{morpheme_entity=} has unexpected format"
                    )
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{morpheme_entity=} has unexpected format"
            )


def _create_analyzed_sentence(
    info_filter: list[MorphemeInfoType], sentence_entity: list[list]
) -> AnalyzedSentence:
    if not isinstance(sentence_entity, list):
        raise UnexpectedGoolabsAPIResponseError(f"{sentence_entity=} is not a list")

    return [
        _create_analyzed_morpheme(info_filter, morpheme_entity)
        for morpheme_entity in sentence_entity
    ]


@response_processing_method([("word_list", list)])
def _create_analyzed_morphology_from_response(response: dict) -> AnalyzedMorphology:
    info_filter = get_type_enum_list_from_response_filters_string(
        MorphemeInfoType, response.get("info_filter")
    )
    pos_filter = get_type_enum_list_from_response_filters_string(
        PartOfSpeechType, response.get("pos_filter")
    )
    word_list = [
        _create_analyzed_sentence(info_filter, sentence_entity)
        for sentence_entity in response.get("word_list")
    ]
    return AnalyzedMorphology(word_list, info_filter, pos_filter)


def _create_name_slot(name_entity: dict[str, str]) -> NameSlot:
    match name_entity:
        case {
            "surname": str(surname),
            "given_name": str(given_name),
            **rest,
        } if not rest:
            return NameSlot(surname, given_name)
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{name_entity=} has unexpected format"
            )


def _create_date(date_string: str) -> date:
    try:
        return date.fromisoformat(date_string)
    except ValueError:
        raise UnexpectedGoolabsAPIResponseError(
            f"{date_string=} has unexpected time format"
        )


def _create_birthday_slot(birthday_entity: dict[str, str]) -> BirthdaySlot:
    match birthday_entity:
        case {"value": str(value), "norm_value": str(norm_value), **rest} if not rest:
            return BirthdaySlot(value, _create_date(norm_value))
        case {"value": str(value), "norm_value": None, **rest} if not rest:
            return BirthdaySlot(value, None)
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{birthday_entity=} has unexpected format"
            )


def _create_sex_slot(sex_entity: dict[str, str]) -> SexSlot:
    match sex_entity:
        case {
            "value": str(value),
            "norm_value": "男性" | "女性" as norm_value,
            **rest,
        } if not rest:
            return SexSlot(value, norm_value)
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{sex_entity=} has unexpected format"
            )


def _create_address_slot(address_entity: dict[str, str | float]) -> AddressSlot:
    match address_entity:
        case {
            "value": str(value),
            "norm_value": str(norm_value),
            "lat": float(latitude),
            "lon": float(longitude),
            **rest,
        } if not rest:
            return AddressSlot(value, norm_value, latitude, longitude)
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{address_entity=} has unexpected format"
            )


def _create_telephone_slot(telephone_entity: dict[str, str]) -> TelephoneSlot:
    match telephone_entity:
        case {"value": str(value), "norm_value": str(norm_value), **rest} if not rest:
            return TelephoneSlot(value, norm_value)
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{telephone_entity=} has unexpected format"
            )


def _create_age_slot(age_entity: dict[str, str | int]) -> AgeSlot:
    match age_entity:
        case {"value": str(value), "norm_value": int(norm_value), **rest} if not rest:
            return AgeSlot(value, norm_value)
        case {"value": str(value), "norm_value": None, **rest} if not rest:
            return AgeSlot(value, None)
        case {"value": None, "norm_value": int(norm_value), **rest} if not rest:
            return AgeSlot(None, norm_value)
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{age_entity=} has unexpected format"
            )


_SLOT_FUNCTION_DICT = {
    SlotType.NAME: _create_name_slot,
    SlotType.BIRTHDAY: _create_birthday_slot,
    SlotType.SEX: _create_sex_slot,
    SlotType.ADDRESS: _create_address_slot,
    SlotType.TELEPHONE: _create_telephone_slot,
    SlotType.AGE: _create_age_slot,
}


@response_processing_method([("slots", dict)])
def _create_extracted_slot_values_from_response(response: dict) -> ExtractedSlotValues:
    slot_filter = get_type_enum_list_from_response_filters_string(
        SlotType, response.get("slot_filter")
    )
    slots_dict = response.get("slots")

    if set(slots_dict.keys()) != set(item.value for item in slot_filter):
        raise UnexpectedGoolabsAPIResponseError(f"{slots_dict=} has unexpected format")
    if any(not isinstance(slot, list) for slot in slots_dict.values()):
        raise UnexpectedGoolabsAPIResponseError(f"{slots_dict=} has unexpected format")

    slots = (
        [
            _SLOT_FUNCTION_DICT[slot_type](slot_entity)
            for slot_entity in slots_dict.get(slot_type.value)
        ]
        if slot_type in slot_filter
        else None
        for slot_type in _SLOT_FUNCTION_DICT
    )
    return ExtractedSlotValues(*slots, slot_filter)


@response_processing_method([("score", float)])
def _create_calculated_similarity_from_response(response: dict) -> CalculatedSimilarity:
    score = response.get("score")
    return CalculatedSimilarity(score)


@goolabs_methods_class
class GoolabsService:
    """The class used to call Goolabs API methods with args validation
    and process responses casting them into dataclasses implemented in goolabs_value_objects.py

    :param app_id: The ID of registered Goolabs application used to make requests to the Goolabs API,
        defaults to value of GOOLABS_APP_ID variable set in config
    :type app_id: str, optional
    :param api_class: Any class that implements Goolabs API methods called with
        their names and Goolabs request params passed with their names as arg name
        and values with None value should not be passed to request body,
        methods should return a dict of a corresponding method response,
        defaults to GoolabsAPI class
    :type api_class: Type[GoolabsAPI], optional
    """

    def __init__(
        self,
        app_id: str = config.GOOLABS_APP_ID,
        api_class: Type[GoolabsAPI] = GoolabsAPI,
    ) -> None:
        """Constructor method"""
        self.api = api_class(app_id)

    def normalize_times(
        self, sentence: str, doc_time: str | datetime = None
    ) -> NormalizedTimes:
        """The method used to normalize times inside the passed sentence.
        Returns a NormalizedTimes object with data received from the Goolabs API.

        :param sentence: the sentence that will be used for the request,
            should be a non-empty string
        :type sentence: str
        :param doc_time: the reference datetime used for time normalization,
            should be a datetime string in the "%Y-%m-%dT%H:%M:%S" format or a datetime instance,
            if omitted, the current time is used,
            defaults to None
        :type doc_time: str or datetime, optional
        :return: A NormalizedTimes object created from response dict
        :rtype: NormalizedTimes
        :raises InvalidArgsForGoolabsRequestError: if passed params are invalid for a Goolabs API request
        :raises UnexpectedGoolabsAPIResponseError: if received response has unexpected format
        """
        return _create_normalized_times_from_response(
            self.api.chrono(
                sentence=sentence,
                doc_time=convert_the_datetime_value_to_goolabs_format(doc_time),
            )
        )

    def extract_named_entities(
        self,
        sentence: str,
        class_filter: Iterable[
            Literal["ART", "ORG", "PSN", "LOC", "DAT", "TIM"] | NamedEntityType
        ]
        | str = None,
    ) -> ExtractedNamedEntities:
        """The method used to extract named entities from the passed sentence.
        Returns an ExtractedNamedEntities object with data received from the Goolabs API.

        :param sentence: the sentence that will be used for the request,
            should be a non-empty string
        :type sentence: str
        :param class_filter: the filters used for named entity extraction,
            should be a string of possible filters separated with '|'
            or a list of strings of possible filters values or NamedEntityType objects,
            if omitted, all filters will be used,
            defaults to None
        :type class_filter: str or list of str/NamedEntityType, optional
        :return: An ExtractedNamedEntities object created from response dict
        :rtype: ExtractedNamedEntities
        :raises InvalidArgsForGoolabsRequestError: if passed params are invalid for a Goolabs API request
        :raises UnexpectedGoolabsAPIResponseError: if received response has unexpected format
        """
        return _create_extracted_named_entities_from_response(
            self.api.entity(
                sentence=sentence,
                class_filter=convert_filters_to_goolabs_format(
                    NamedEntityType, class_filter
                ),
            ),
            [("class_filter", str) if class_filter is not None else None],
        )

    def convert_to_furigana(
        self,
        sentence: str,
        output_type: Literal["hiragana", "katakana"] | KanaType = "hiragana",
    ) -> ConvertedToFurigana:
        """The method used to convert the passed sentence to furigana.
        Returns a ConvertedToFurigana object with data received from the Goolabs API.

        :param sentence: the sentence that will be used for the request,
            should be a non-empty string
        :type sentence: str
        :param output_type: the output type used for conversion to furigana,
            should be a string of possible output type or a KanaType object,
            defaults to "hiragana"
        :type output_type: str or KanaType, optional
        :return: A ConvertedToFurigana object created from response dict
        :rtype: ConvertedToFurigana
        :raises InvalidArgsForGoolabsRequestError: if passed params are invalid for a Goolabs API request
        :raises UnexpectedGoolabsAPIResponseError: if received response has unexpected format
        """
        return _create_converted_to_furigana_from_response(
            self.api.hiragana(
                sentence=sentence,
                output_type=convert_the_type_enum_value_to_string(
                    KanaType, output_type, True
                ),
            )
        )

    def extract_keywords(
        self,
        title: str,
        body: str,
        max_num: int | str = None,
        focus: Literal["ORG", "PSN", "LOC"] | KeywordFocusType = None,
    ) -> ExtractedKeywords:
        """The method used to extract keywords from the article passed as title and body.
        Returns an ExtractedKeywords object with data received from the Goolabs API.

        :param title: the title that will be used for the request,
            should be a non-empty string
        :type title: str
        :param body: the body that will be used for the request,
            should be a non-empty string
        :type body: str
        :param max_num: the max_num used for the request,
            should be an int or a decimal string with value in range between 1 and 10,
            defaults to None
        :type max_num: int or str, optional
        :param focus: the focus used for keyword extraction,
            should be a string of possible focus or a KeywordFocusType object,
            defaults to None
        :type focus: str or KeywordFocusType, optional
        :return: An ExtractedKeywords object created from response dict
        :rtype: ExtractedKeywords
        :raises InvalidArgsForGoolabsRequestError: if passed params are invalid for a Goolabs API request
        :raises UnexpectedGoolabsAPIResponseError: if received response has unexpected format
        """
        return _create_extracted_keywords_from_response(
            self.api.keyword(
                title=title,
                body=body,
                max_num=convert_num_value_to_int_in_range(max_num),
                focus=convert_the_type_enum_value_to_string(KeywordFocusType, focus),
            ),
            [("focus", str) if focus is not None else None],
        )

    def analyze_morphology(
        self,
        sentence: str,
        info_filter: Iterable[Literal["form", "pos", "read"] | MorphemeInfoType]
        | str = None,
        pos_filter: Iterable[
            Literal[
                "名詞",
                "名詞接尾辞",
                "冠名詞",
                "英語接尾辞",
                "動詞語幹",
                "動詞活用語尾",
                "動詞接尾辞",
                "冠動詞",
                "補助名詞",
                "形容詞語幹",
                "形容詞接尾辞",
                "冠形容詞",
                "連体詞",
                "連用詞",
                "接続詞",
                "独立詞",
                "接続接尾辞",
                "判定詞",
                "格助詞",
                "引用助 詞",
                "連用助詞",
                "終助詞",
                "間投詞",
                "括弧",
                "句点",
                "読点",
                "空白",
                "Symbol",
                "Month",
                "Day",
                "YearMonth",
                "MonthDay",
                "Hour",
                "Minute",
                "Second",
                "HourMinute",
                "MinuteSecond",
                "PreHour",
                "PostHour",
                "Number",
                "助数詞",
                "助助数詞",
                "冠数詞",
                "Alphabet",
                "Kana",
                "Katakana",
                "Kanji",
                "Roman",
                "Undef",
            ]
            | PartOfSpeechType
        ]
        | str = None,
    ) -> AnalyzedMorphology:
        """The method used analyze morphology of the passed sentence.
        Returns an AnalyzedMorphology object with data received from the Goolabs API.

        :param sentence: the sentence that will be used for the request,
            should be a non-empty string
        :type sentence: str
        :param info_filter: the filters used for analyzing morphology,
            should be a string of possible filters separated with '|'
            or a list of strings of possible filters values or MorphemeInfoType objects,
            if omitted, all filters will be used,
            defaults to None
        :type info_filter: str or list of str/MorphemeInfoType, optional
        :param pos_filter: the filters used for analyzing morphology,
            should be a string of possible filters separated with '|'
            or a list of strings of possible filters values or PartOfSpeechType objects,
            if omitted, all filters will be used,
            defaults to None
        :type pos_filter: str or list of str/PartOfSpeechType, optional
        :return: An AnalyzedMorphology object created from response dict
        :rtype: AnalyzedMorphology
        :raises InvalidArgsForGoolabsRequestError: if passed params are invalid for a Goolabs API request
        :raises UnexpectedGoolabsAPIResponseError: if received response has unexpected format
        """
        return _create_analyzed_morphology_from_response(
            self.api.morph(
                sentence=sentence,
                info_filter=convert_filters_to_goolabs_format(
                    MorphemeInfoType, info_filter
                ),
                pos_filter=convert_filters_to_goolabs_format(
                    PartOfSpeechType, pos_filter
                ),
            ),
            [
                ("info_filter", str) if info_filter else None,
                ("pos_filter", str) if pos_filter else None,
            ],
        )

    def extract_slot_values(
        self,
        sentence: str,
        slot_filter: Iterable[
            Literal["name", "birthday", "sex", "address", "tel", "age"] | SlotType
        ]
        | str = None,
    ) -> ExtractedSlotValues:
        """The method used to extract slot values from the passed sentence.
        Returns an ExtractedSlotValues object with data received from the Goolabs API.

        :param sentence: the sentence that will be used for the request,
            should be a non-empty string
        :type sentence: str
        :param slot_filter: the filters used for slot values extraction,
            should be a string of possible filters separated with '|'
            or a list of strings of possible filters values or SlotType objects,
            if omitted, all filters will be used,
            defaults to None
        :type slot_filter: str or list of str/SlotType, optional
        :return: An ExtractedSlotValues object created from response dict
        :rtype: ExtractedSlotValues
        :raises InvalidArgsForGoolabsRequestError: if passed params are invalid for a Goolabs API request
        :raises UnexpectedGoolabsAPIResponseError: if received response has unexpected format
        """
        return _create_extracted_slot_values_from_response(
            self.api.slot(
                sentence=sentence,
                slot_filter=convert_filters_to_goolabs_format(SlotType, slot_filter),
            ),
            [("slot_filter", str) if slot_filter is not None else None],
        )

    def calculate_similarity(self, text1: str, text2: str) -> CalculatedSimilarity:
        """The method used to calculate similarity between 2 passed texts.
        Returns a CalculatedSimilarity object with data received from the Goolabs API.

        :param text1: the first text that will be used for the request,
            should be a non-empty string
        :type text1: str
        :param text2: the second text that will be used for the request,
            should be a non-empty string
        :type text2: str
        :return: A CalculatedSimilarity object created from response dict
        :rtype: CalculatedSimilarity
        :raises InvalidArgsForGoolabsRequestError: if passed params are invalid for a Goolabs API request
        :raises UnexpectedGoolabsAPIResponseError: if received response has unexpected format
        """
        return _create_calculated_similarity_from_response(
            self.api.textpair(text1=text1, text2=text2)
        )
