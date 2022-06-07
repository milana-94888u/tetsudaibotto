from datetime import date

from unittest import TestCase
from unittest.mock import MagicMock

from services.exceptions import (
    UnexpectedGoolabsAPIResponseError,
    InvalidArgsForGoolabsRequestError,
)
from services.goolabs import (
    GoolabsService,
    GoolabsDatetime,
    NamedEntityType,
    KanaType,
    KeywordFocusType,
    MorphemeInfoType,
    PartOfSpeechType,
    SlotType,
    NormalizedTime,
    NamedEntity,
    Keyword,
    AnalyzedMorpheme,
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


class TestGoolabsService(TestCase):
    def setUp(self) -> None:
        self.service = GoolabsService(None, MagicMock)

    def test_normalize_times_with_doc_time_passed(self) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["今日", "2016-04-01"], ["10時半", "2016-04-01T10:30"]],
            "doc_time": "2016-04-01T09:00:00",
            "request_id": "labs.goo.ne.jp\t1654044681\t0",
        }

        expected_result = NormalizedTimes(
            datetime_list=[
                NormalizedTime(text="今日", time=GoolabsDatetime(2016, 4, 1, 0, 0)),
                NormalizedTime(text="10時半", time=GoolabsDatetime(2016, 4, 1, 10, 30)),
            ],
            doc_time=GoolabsDatetime(2016, 4, 1, 9, 0),
        )

        self.assertEqual(
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00"),
            expected_result,
        )

    def test_normalize_times_without_doc_time_passed(self) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["昨日", "2022-06-01"], ["9時43分", "2022-06-01T09:43"]],
            "doc_time": "2022-06-02T01:11:30",
            "request_id": "labs.goo.ne.jp\t1654099890\t0",
        }

        expected_result = NormalizedTimes(
            datetime_list=[
                NormalizedTime(text="昨日", time=GoolabsDatetime(2022, 6, 1, 0, 0)),
                NormalizedTime(text="9時43分", time=GoolabsDatetime(2022, 6, 1, 9, 43)),
            ],
            doc_time=GoolabsDatetime(2022, 6, 2, 1, 11, 30),
        )

        self.assertEqual(
            self.service.normalize_times("昨日は9時43分に起床"),
            expected_result,
        )

    def test_normalize_times_processes_date_with_no_day(self) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["六月", "2022-06"]],
            "doc_time": "2022-06-02T01:17:56",
            "request_id": "labs.goo.ne.jp\t1654100276\t0",
        }

        expected_result = NormalizedTimes(
            datetime_list=[
                NormalizedTime(text="六月", time=GoolabsDatetime(2022, 6, 1, 0, 0))
            ],
            doc_time=GoolabsDatetime(2022, 6, 2, 1, 17, 56),
        )

        self.assertEqual(
            self.service.normalize_times("六月"),
            expected_result,
        )

    def test_normalize_times_processes_date_with_no_month(self) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["平成27年", "2015"]],
            "doc_time": "2022-06-02T01:37:13",
            "request_id": "labs.goo.ne.jp\t1654101433\t0",
        }

        expected_result = NormalizedTimes(
            datetime_list=[
                NormalizedTime(text="平成27年", time=GoolabsDatetime(2015, 1, 1, 0, 0))
            ],
            doc_time=GoolabsDatetime(2022, 6, 2, 1, 37, 13),
        )

        self.assertEqual(
            self.service.normalize_times("平成27年"),
            expected_result,
        )

    def test_normalize_times_processes_empty_datetime_list(self) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [],
            "doc_time": "2022-06-02T01:44:28",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        expected_result = NormalizedTimes(
            datetime_list=[],
            doc_time=GoolabsDatetime(2022, 6, 2, 1, 44, 28),
        )

        self.assertEqual(
            self.service.normalize_times("全世界の人々が平和を切望している。"),
            expected_result,
        )

    def test_raises_InvalidArgsForGoolabsRequestError_on_normalize_times_sentence_is_not_a_string_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.normalize_times(0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_normalize_times_empty_sentence_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.normalize_times("")

    def test_raises_InvalidArgsForGoolabsRequestError_on_normalize_times_sentence_is_not_a_string_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.normalize_times(sentence=0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_normalize_times_empty_sentence_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.normalize_times(sentence="")

    def test_raises_InvalidArgsForGoolabsRequestError_on_normalize_times_doc_time_is_not_a_string_or_a_datetime(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.normalize_times("今日の10時半に出かけます。", 0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_normalize_times_incorrect_doc_time_format(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.normalize_times("今日の10時半に出かけます。", "incorrect")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_no_request_id(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["今日", "2016-04-01"], ["10時半", "2016-04-01T10:30"]],
            "doc_time": "2016-04-01T09:00:00",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_no_doc_time(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["今日", "2016-04-01"], ["10時半", "2016-04-01T10:30"]],
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_no_datetime_list(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "doc_time": "2016-04-01T09:00:00",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_datetime_list_is_not_a_list(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": "",
            "doc_time": "2016-04-01T09:00:00",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_doc_time_is_not_a_string(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["今日", "2016-04-01"], ["10時半", "2016-04-01T10:30"]],
            "doc_time": 0,
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_error_response(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "error": "error",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_redundant_key(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["今日", "2016-04-01"], ["10時半", "2016-04-01T10:30"]],
            "doc_time": "2016-04-01T09:00:00",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_not_a_dict(
        self,
    ) -> None:
        self.service.api.chrono.return_value = ""

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_incorrect_doc_time_format(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["今日", "2016-04-01"], ["10時半", "2016-04-01T10:30"]],
            "doc_time": "incorrect",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_incorrect_time_format_in_datetime_list(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["今日", "incorrect"], ["10時半", "2016-04-01T10:30"]],
            "doc_time": "2016-04-01T09:00:00",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_time_entity_text_not_a_string(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [[0, "2016-04-01"], ["10時半", "2016-04-01T10:30"]],
            "doc_time": "2016-04-01T09:00:00",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_time_entity_not_a_list(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": ["incorrect", ["10時半", "2016-04-01T10:30"]],
            "doc_time": "2016-04-01T09:00:00",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_time_entity_has_not_enough_items(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [["今日"], ["10時半", "2016-04-01T10:30"]],
            "doc_time": "2016-04-01T09:00:00",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_normalize_times_time_entity_has_a_redundant_item(
        self,
    ) -> None:
        self.service.api.chrono.return_value = {
            "datetime_list": [
                ["今日", "2016-04-01", "redundant"],
                ["10時半", "2016-04-01T10:30"],
            ],
            "doc_time": "2016-04-01T09:00:00",
            "request_id": "labs.goo.ne.jp\t1654101868\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.normalize_times("今日の10時半に出かけます。", "2016-04-01T09:00:00")

    def test_extract_named_entities_without_class_filter(self) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [["鈴木", "PSN"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        expected_result = ExtractedNamedEntities(
            entities=[
                NamedEntity(text="鈴木", entity_type=NamedEntityType.PERSON_NAME),
                NamedEntity(text="9時30分", entity_type=NamedEntityType.TIME_EXPRESSION),
                NamedEntity(text="横浜", entity_type=NamedEntityType.LOCATION_NAME),
            ],
            class_filter=[
                NamedEntityType.ARTIFACT_NAME,
                NamedEntityType.ORGANIZATION_NAME,
                NamedEntityType.PERSON_NAME,
                NamedEntityType.LOCATION_NAME,
                NamedEntityType.DATE_EXPRESSION,
                NamedEntityType.TIME_EXPRESSION,
                NamedEntityType.MONEY_AMOUNT_EXPRESSION,
                NamedEntityType.PERCENTAGE_EXPRESSION,
            ],
        )

        self.assertEqual(
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。"),
            expected_result,
        )

    def test_extract_named_entities_with_class_filter_as_string(self) -> None:
        self.service.api.entity.return_value = {
            "class_filter": "PSN",
            "ne_list": [["鈴木", "PSN"]],
            "request_id": "labs.goo.ne.jp\t1654114199\t0",
        }

        expected_result = ExtractedNamedEntities(
            entities=[NamedEntity(text="鈴木", entity_type=NamedEntityType.PERSON_NAME)],
            class_filter=[NamedEntityType.PERSON_NAME],
        )

        self.assertEqual(
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。", "PSN"),
            expected_result,
        )

    def test_extract_named_entities_with_class_filter_as_string_list(self) -> None:
        self.service.api.entity.return_value = {
            "class_filter": "LOC|TIM",
            "ne_list": [["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654114459\t0",
        }

        expected_result = ExtractedNamedEntities(
            entities=[
                NamedEntity(text="9時30分", entity_type=NamedEntityType.TIME_EXPRESSION),
                NamedEntity(text="横浜", entity_type=NamedEntityType.LOCATION_NAME),
            ],
            class_filter=[
                NamedEntityType.LOCATION_NAME,
                NamedEntityType.TIME_EXPRESSION,
            ],
        )

        self.assertEqual(
            self.service.extract_named_entities(
                "鈴木さんがきょうの9時30分に横浜に行きます。", ["TIM", "LOC"]
            ),
            expected_result,
        )

    def test_extract_named_entities_processes_empty_ne_list_with_class_filter(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "class_filter": "ORG",
            "ne_list": [],
            "request_id": "labs.goo.ne.jp\t1654114459\t0",
        }

        expected_result = ExtractedNamedEntities(
            entities=[],
            class_filter=[NamedEntityType.ORGANIZATION_NAME],
        )

        self.assertEqual(
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。", ["ORG"]),
            expected_result,
        )

    def test_extract_named_entities_processes_empty_ne_list_without_class_filter(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [],
            "request_id": "labs.goo.ne.jp\t1654115063\t0",
        }

        expected_result = ExtractedNamedEntities(
            entities=[],
            class_filter=[
                NamedEntityType.ARTIFACT_NAME,
                NamedEntityType.ORGANIZATION_NAME,
                NamedEntityType.PERSON_NAME,
                NamedEntityType.LOCATION_NAME,
                NamedEntityType.DATE_EXPRESSION,
                NamedEntityType.TIME_EXPRESSION,
                NamedEntityType.MONEY_AMOUNT_EXPRESSION,
                NamedEntityType.PERCENTAGE_EXPRESSION,
            ],
        )

        self.assertEqual(
            self.service.extract_named_entities("おはよう"),
            expected_result,
        )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_named_entities_sentence_is_not_a_string_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_named_entities(0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_named_entities_empty_sentence_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_named_entities("")

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_named_entities_sentence_is_not_a_string_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_named_entities(sentence=0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_named_entities_empty_sentence_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_named_entities(sentence="")

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_named_entities_class_filter_has_incorrect_type(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。", 0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_named_entities_class_filter_has_incorrect_format(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。", "incorrect")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_no_request_id(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [["鈴木", "PSN"], ["9時30分", "TIM"], ["横浜", "LOC"]],
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_no_ne_list(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_no_class_filter(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [["鈴木", "PSN"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。", "PSN|LOC")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_redundant_class_filter(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "class_filter": "ORG",
            "ne_list": [["鈴木", "PSN"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_ne_list_is_not_a_list(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": "",
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_class_filter_is_not_a_string(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "class_filter": 0,
            "ne_list": [["鈴木", "PSN"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。", "ORG")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_error_response(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "error": "error",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_redundant_key_with_class_filter(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "class_filter": "ORG",
            "ne_list": [["鈴木", "PSN"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。", "ORG")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_redundant_key_without_class_filter(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [["鈴木", "PSN"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_not_a_dict(
        self,
    ) -> None:
        self.service.api.entity.return_value = ""

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_incorrect_format_of_class_filter(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "class_filter": "incorrect",
            "ne_list": [["鈴木", "PSN"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。", "ORG")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_entity_text_is_not_a_string(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [[0, "PSN"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_entity_class_is_not_a_string(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [["鈴木", 0], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_entity_class_incorrect_format(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [["鈴木", "incorrect"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_entity_is_not_a_list(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": ["", ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_entity_has_not_enough_items(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [["鈴木"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_named_entities_entity_has_a_redundant_item(
        self,
    ) -> None:
        self.service.api.entity.return_value = {
            "ne_list": [["鈴木", "PSN", "redundant"], ["9時30分", "TIM"], ["横浜", "LOC"]],
            "request_id": "labs.goo.ne.jp\t1654045886\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_named_entities("鈴木さんがきょうの9時30分に横浜に行きます。")

    def test_convert_to_furigana_hiragana_as_string_implicit(self) -> None:
        self.service.api.hiragana.return_value = {
            "converted": "かんじが まざっている ぶんしょう",
            "output_type": "hiragana",
            "request_id": "labs.goo.ne.jp\t1654046966\t0",
        }

        expected_result = ConvertedToFurigana(
            text="かんじが まざっている ぶんしょう",
            kana_type=KanaType.HIRAGANA,
        )

        self.assertEqual(
            self.service.convert_to_furigana("漢字が混ざっている文章"),
            expected_result,
        )

    def test_convert_to_furigana_hiragana_as_string_explicit(self) -> None:
        self.service.api.hiragana.return_value = {
            "converted": "かんじが まざっている ぶんしょう",
            "output_type": "hiragana",
            "request_id": "labs.goo.ne.jp\t1654046966\t0",
        }

        expected_result = ConvertedToFurigana(
            text="かんじが まざっている ぶんしょう",
            kana_type=KanaType.HIRAGANA,
        )

        self.assertEqual(
            self.service.convert_to_furigana("漢字が混ざっている文章", "hiragana"),
            expected_result,
        )

    def test_convert_to_furigana_hiragana_as_enum(self) -> None:
        self.service.api.hiragana.return_value = {
            "converted": "かんじが まざっている ぶんしょう",
            "output_type": "hiragana",
            "request_id": "labs.goo.ne.jp\t1654046966\t0",
        }

        expected_result = ConvertedToFurigana(
            text="かんじが まざっている ぶんしょう",
            kana_type=KanaType.HIRAGANA,
        )

        self.assertEqual(
            self.service.convert_to_furigana("漢字が混ざっている文章", KanaType.HIRAGANA),
            expected_result,
        )

    def test_convert_to_furigana_katakana_as_string(self) -> None:
        self.service.api.hiragana.return_value = {
            "converted": "カンジガ マザッテイル ブンショウ",
            "output_type": "katakana",
            "request_id": "labs.goo.ne.jp\t1654118930\t0",
        }

        expected_result = ConvertedToFurigana(
            text="カンジガ マザッテイル ブンショウ",
            kana_type=KanaType.KATAKANA,
        )

        self.assertEqual(
            self.service.convert_to_furigana("漢字が混ざっている文章", "katakana"),
            expected_result,
        )

    def test_convert_to_furigana_katakana_as_enum(self) -> None:
        self.service.api.hiragana.return_value = {
            "converted": "カンジガ マザッテイル ブンショウ",
            "output_type": "katakana",
            "request_id": "labs.goo.ne.jp\t1654118930\t0",
        }

        expected_result = ConvertedToFurigana(
            text="カンジガ マザッテイル ブンショウ",
            kana_type=KanaType.KATAKANA,
        )

        self.assertEqual(
            self.service.convert_to_furigana("漢字が混ざっている文章", KanaType.KATAKANA),
            expected_result,
        )

    def test_raises_InvalidArgsForGoolabsRequestError_on_convert_to_furigana_sentence_is_not_a_string_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.convert_to_furigana(0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_convert_to_furigana_empty_sentence_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.convert_to_furigana("")

    def test_raises_InvalidArgsForGoolabsRequestError_on_convert_to_furigana_sentence_is_not_a_string_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.convert_to_furigana(sentence=0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_convert_to_furigana_empty_sentence_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.convert_to_furigana(sentence="")

    def test_raises_InvalidArgsForGoolabsRequestError_on_convert_to_furigana_output_type_has_incorrect_type(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.convert_to_furigana("漢字が混ざっている文章", 0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_convert_to_furigana_output_type_has_incorrect_format(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.convert_to_furigana("漢字が混ざっている文章", "incorrect")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_convert_to_furigana_no_request_id(
        self,
    ):
        self.service.api.hiragana.return_value = {
            "converted": "かんじが まざっている ぶんしょう",
            "output_type": "hiragana",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.convert_to_furigana("漢字が混ざっている文章")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_convert_to_furigana_no_converted(
        self,
    ):
        self.service.api.hiragana.return_value = {
            "output_type": "hiragana",
            "request_id": "labs.goo.ne.jp\t1654046966\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.convert_to_furigana("漢字が混ざっている文章")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_convert_to_furigana_no_output_type(
        self,
    ):
        self.service.api.hiragana.return_value = {
            "converted": "かんじが まざっている ぶんしょう",
            "request_id": "labs.goo.ne.jp\t1654046966\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.convert_to_furigana("漢字が混ざっている文章")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_convert_to_furigana_converted_is_not_a_string(
        self,
    ):
        self.service.api.hiragana.return_value = {
            "converted": 0,
            "output_type": "hiragana",
            "request_id": "labs.goo.ne.jp\t1654046966\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.convert_to_furigana("漢字が混ざっている文章")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_convert_to_furigana_output_type_is_not_a_string(
        self,
    ):
        self.service.api.hiragana.return_value = {
            "converted": "かんじが まざっている ぶんしょう",
            "output_type": 0,
            "request_id": "labs.goo.ne.jp\t1654046966\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.convert_to_furigana("漢字が混ざっている文章")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_convert_to_furigana_output_type_has_incorrect_format(
        self,
    ):
        self.service.api.hiragana.return_value = {
            "converted": "かんじが まざっている ぶんしょう",
            "output_type": "incorrect",
            "request_id": "labs.goo.ne.jp\t1654046966\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.convert_to_furigana("漢字が混ざっている文章")

    def test_extract_keywords_with_focus_as_string(self) -> None:
        self.service.api.keyword.return_value = {
            "focus": "ORG",
            "keywords": [{"gooラボ": 3.75}, {"MURA": 0.7921}, {"匿名性コミュニケーションサービス": 0.75}],
            "request_id": "labs.goo.ne.jp\t1654087471\t0",
        }

        expected_result = ExtractedKeywords(
            keywords=[
                Keyword(text="gooラボ", score=3.75),
                Keyword(text="MURA", score=0.7921),
                Keyword(text="匿名性コミュニケーションサービス", score=0.75),
            ],
            focus=KeywordFocusType.ORGANIZATION_NAME,
        )

        self.assertEqual(
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                3,
                "ORG",
            ),
            expected_result,
        )

    def test_extract_keywords_with_focus_as_enum(self) -> None:
        self.service.api.keyword.return_value = {
            "focus": "ORG",
            "keywords": [{"gooラボ": 3.75}, {"MURA": 0.7921}, {"匿名性コミュニケーションサービス": 0.75}],
            "request_id": "labs.goo.ne.jp\t1654087471\t0",
        }

        expected_result = ExtractedKeywords(
            keywords=[
                Keyword(text="gooラボ", score=3.75),
                Keyword(text="MURA", score=0.7921),
                Keyword(text="匿名性コミュニケーションサービス", score=0.75),
            ],
            focus=KeywordFocusType.ORGANIZATION_NAME,
        )

        self.assertEqual(
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                3,
                KeywordFocusType.ORGANIZATION_NAME,
            ),
            expected_result,
        )

    def test_extract_keywords_without_focus(self) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [
                {"MURA": 0.7921},
                {"gooラボ": 0.75},
                {"匿名性コミュニケーションサービス": 0.75},
                {"ネタ枯れ防止機能": 0.75},
                {"コンセプト": 0.75},
                {"goo": 0.75},
                {"若井 昌宏": 0.0421},
                {"代表取締役社長": 0.0421},
                {"NTTレゾナント": 0.0421},
                {"gooラボ上": 0.0421},
            ],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        expected_result = ExtractedKeywords(
            keywords=[
                Keyword(text="MURA", score=0.7921),
                Keyword(text="gooラボ", score=0.75),
                Keyword(text="匿名性コミュニケーションサービス", score=0.75),
                Keyword(text="ネタ枯れ防止機能", score=0.75),
                Keyword(text="コンセプト", score=0.75),
                Keyword(text="goo", score=0.75),
                Keyword(text="若井 昌宏", score=0.0421),
                Keyword(text="代表取締役社長", score=0.0421),
                Keyword(text="NTTレゾナント", score=0.0421),
                Keyword(text="gooラボ上", score=0.0421),
            ],
            focus=None,
        )

        self.assertEqual(
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            ),
            expected_result,
        )

    def test_extract_keywords_empty_keywords_without_focus(self) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        expected_result = ExtractedKeywords(keywords=[], focus=None)

        self.assertEqual(
            self.service.extract_keywords("title", "body"),
            expected_result,
        )

    def test_extract_keywords_empty_keywords_with_focus(self) -> None:
        self.service.api.keyword.return_value = {
            "focus": "ORG",
            "keywords": [],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        expected_result = ExtractedKeywords(
            keywords=[], focus=KeywordFocusType.ORGANIZATION_NAME
        )

        self.assertEqual(
            self.service.extract_keywords("title", "body", 10, "ORG"),
            expected_result,
        )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_title_is_not_a_string_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                0,
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_empty_title_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_body_is_not_a_string_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_empty_body_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_empty_title_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                title="",
                body="NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_title_is_not_a_string_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                title=0,
                body="NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_body_is_not_a_string_as_kwarg_title_is_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                body=0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_empty_body_as_kwarg_title_is_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                body=0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_body_is_not_a_string_as_kwarg_title_is_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                title="「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                body=0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_empty_body_as_kwarg_title_is_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                title="「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                body=0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_max_num_is_not_an_int_or_a_decimal_string(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                [],
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_max_num_has_incorrect_format(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                "incorrect",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_max_num_out_of_range_string(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                "11",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_max_num_out_of_range_int(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                11,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_focus_has_incorrect_type(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                10,
                0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_keywords_focus_has_incorrect_format(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                10,
                "incorrect",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_no_request_id(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [
                {"MURA": 0.7921},
                {"gooラボ": 0.75},
                {"匿名性コミュニケーションサービス": 0.75},
                {"ネタ枯れ防止機能": 0.75},
                {"コンセプト": 0.75},
                {"goo": 0.75},
                {"若井 昌宏": 0.0421},
                {"代表取締役社長": 0.0421},
                {"NTTレゾナント": 0.0421},
                {"gooラボ上": 0.0421},
            ],
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_no_keywords(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_no_focus(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [{"gooラボ": 3.75}, {"MURA": 0.7921}, {"匿名性コミュニケーションサービス": 0.75}],
            "request_id": "labs.goo.ne.jp\t1654087471\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                3,
                "ORG",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_redundant_focus(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "focus": "ORG",
            "keywords": [
                {"MURA": 0.7921},
                {"gooラボ": 0.75},
                {"匿名性コミュニケーションサービス": 0.75},
                {"ネタ枯れ防止機能": 0.75},
                {"コンセプト": 0.75},
                {"goo": 0.75},
                {"若井 昌宏": 0.0421},
                {"代表取締役社長": 0.0421},
                {"NTTレゾナント": 0.0421},
                {"gooラボ上": 0.0421},
            ],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_redundant_key(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [
                {"MURA": 0.7921},
                {"gooラボ": 0.75},
                {"匿名性コミュニケーションサービス": 0.75},
                {"ネタ枯れ防止機能": 0.75},
                {"コンセプト": 0.75},
                {"goo": 0.75},
                {"若井 昌宏": 0.0421},
                {"代表取締役社長": 0.0421},
                {"NTTレゾナント": 0.0421},
                {"gooラボ上": 0.0421},
            ],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_error_response(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "error": "error",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_not_a_dict(
        self,
    ) -> None:
        self.service.api.keyword.return_value = ""

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_keywords_is_not_a_list(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "keywords": "",
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_focus_is_not_a_string(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "focus": 0,
            "keywords": [{"gooラボ": 3.75}, {"MURA": 0.7921}, {"匿名性コミュニケーションサービス": 0.75}],
            "request_id": "labs.goo.ne.jp\t1654087471\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                3,
                "ORG",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_focus_has_incorrect_format(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "focus": "incorrect",
            "keywords": [{"gooラボ": 3.75}, {"MURA": 0.7921}, {"匿名性コミュニケーションサービス": 0.75}],
            "request_id": "labs.goo.ne.jp\t1654087471\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
                3,
                "ORG",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_keyword_entity_is_not_a_dict(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [
                "",
                {"gooラボ": 0.75},
                {"匿名性コミュニケーションサービス": 0.75},
                {"ネタ枯れ防止機能": 0.75},
                {"コンセプト": 0.75},
                {"goo": 0.75},
                {"若井 昌宏": 0.0421},
                {"代表取締役社長": 0.0421},
                {"NTTレゾナント": 0.0421},
                {"gooラボ上": 0.0421},
            ],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_keyword_entity_text_is_not_a_string(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [
                {0: 0.7921},
                {"gooラボ": 0.75},
                {"匿名性コミュニケーションサービス": 0.75},
                {"ネタ枯れ防止機能": 0.75},
                {"コンセプト": 0.75},
                {"goo": 0.75},
                {"若井 昌宏": 0.0421},
                {"代表取締役社長": 0.0421},
                {"NTTレゾナント": 0.0421},
                {"gooラボ上": 0.0421},
            ],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_keyword_entity_score_is_not_a_float(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [
                {"MURA": ""},
                {"gooラボ": 0.75},
                {"匿名性コミュニケーションサービス": 0.75},
                {"ネタ枯れ防止機能": 0.75},
                {"コンセプト": 0.75},
                {"goo": 0.75},
                {"若井 昌宏": 0.0421},
                {"代表取締役社長": 0.0421},
                {"NTTレゾナント": 0.0421},
                {"gooラボ上": 0.0421},
            ],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_keyword_entity_is_empty(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [
                {},
                {"gooラボ": 0.75},
                {"匿名性コミュニケーションサービス": 0.75},
                {"ネタ枯れ防止機能": 0.75},
                {"コンセプト": 0.75},
                {"goo": 0.75},
                {"若井 昌宏": 0.0421},
                {"代表取締役社長": 0.0421},
                {"NTTレゾナント": 0.0421},
                {"gooラボ上": 0.0421},
            ],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_keywords_keyword_entity_has_a_redundant_item(
        self,
    ) -> None:
        self.service.api.keyword.return_value = {
            "keywords": [
                {"MURA": 0.7921, "key": "value"},
                {"gooラボ": 0.75},
                {"匿名性コミュニケーションサービス": 0.75},
                {"ネタ枯れ防止機能": 0.75},
                {"コンセプト": 0.75},
                {"goo": 0.75},
                {"若井 昌宏": 0.0421},
                {"代表取締役社長": 0.0421},
                {"NTTレゾナント": 0.0421},
                {"gooラボ上": 0.0421},
            ],
            "request_id": "labs.goo.ne.jp\t1654119671\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_keywords(
                "「和」をコンセプトとする 匿名性コミュニケーションサービス「MURA」 gooラボでのβ版のトライアル実施 ～gooの検索技術を使った「ネタ枯れ防止機能」によりコミュニティの話題活性化が可能に～",
                "NTTレゾナント株式会社（本社：東京都港区、代表取締役社長：若井 昌宏、以下、NTTレゾナント）は、同じ興味関心を持つ人と匿名でコミュニティをつくることができるコミュニケーションサービス「MURA」を、2015年8月27日よりgooラボ上でβ版サイトのトライアル提供を開始します。",
            )

    def test_analyze_morphology_without_info_filter_without_pos_filter(self) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["を", "格助詞", "ヲ"],
                    ["分析", "名詞", "ブンセキ"],
                    ["し", "動詞活用語尾", "シ"],
                    ["ます", "動詞接尾辞", "マス"],
                ]
            ],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(
                        form="日本語", pos=PartOfSpeechType.NOUN, read="ニホンゴ"
                    ),
                    AnalyzedMorpheme(
                        form="を", pos=PartOfSpeechType.CASE_MARKING_PARTICLE, read="ヲ"
                    ),
                    AnalyzedMorpheme(form="分析", pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form="し",
                        pos=PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                        read="シ",
                    ),
                    AnalyzedMorpheme(
                        form="ます", pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.FORM,
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.NOUN_SUFFIX,
                PartOfSpeechType.NOUN_PREFIX,
                PartOfSpeechType.ENGLISH_SUFFIX,
                PartOfSpeechType.VERB_STEM,
                PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                PartOfSpeechType.VERB_SUFFIX,
                PartOfSpeechType.VERB_PREFIX,
                PartOfSpeechType.AUXILIARY_NOUN,
                PartOfSpeechType.ADJECTIVE_STEM,
                PartOfSpeechType.ADJECTIVE_SUFFIX,
                PartOfSpeechType.ADJECTIVE_PREFIX,
                PartOfSpeechType.ADNOMINAL_ADJECTIVE,
                PartOfSpeechType.ADVERB,
                PartOfSpeechType.CONJUNCTION,
                PartOfSpeechType.INDEPENDENT_WORD,
                PartOfSpeechType.CONNECTION_SUFFIX,
                PartOfSpeechType.PREDICATE,
                PartOfSpeechType.CASE_MARKING_PARTICLE,
                PartOfSpeechType.QUOTATION_PARTICLE,
                PartOfSpeechType.ADVERBIAL_PARTICLE,
                PartOfSpeechType.SENTENCE_ENDING_PARTICLE,
                PartOfSpeechType.INTERJECTION,
                PartOfSpeechType.BRACKETS,
                PartOfSpeechType.FULL_STOP_PUNCTUATION_MARK,
                PartOfSpeechType.COMMA,
                PartOfSpeechType.BLANK_SPACE,
                PartOfSpeechType.SYMBOL,
                PartOfSpeechType.MONTH,
                PartOfSpeechType.DAY,
                PartOfSpeechType.YEAR_MONTH,
                PartOfSpeechType.MONTH_DAY,
                PartOfSpeechType.HOUR,
                PartOfSpeechType.MINUTE,
                PartOfSpeechType.SECOND,
                PartOfSpeechType.HOUR_MINUTE,
                PartOfSpeechType.MINUTE_SECOND,
                PartOfSpeechType.PRE_HOUR,
                PartOfSpeechType.POST_HOUR,
                PartOfSpeechType.NUMBER,
                PartOfSpeechType.COUNTER_WORD,
                PartOfSpeechType.ORDINAL_NUMBER_SUFFIX,
                PartOfSpeechType.ORDINAL_NUMBER_PREFIX,
                PartOfSpeechType.ALPHABET,
                PartOfSpeechType.HIRAGANA,
                PartOfSpeechType.KATAKANA,
                PartOfSpeechType.KANJI,
                PartOfSpeechType.ROMAN,
                PartOfSpeechType.UNDEFINED,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology("日本語を分析します"),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_without_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "form",
            "request_id": "labs.goo.ne.jp\t1654088209\t0",
            "word_list": [[["日本語"], ["を"], ["分析"], ["し"], ["ます"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form="日本語", pos=None, read=None),
                    AnalyzedMorpheme(form="を", pos=None, read=None),
                    AnalyzedMorpheme(form="分析", pos=None, read=None),
                    AnalyzedMorpheme(form="し", pos=None, read=None),
                    AnalyzedMorpheme(form="ます", pos=None, read=None),
                ]
            ],
            info_filter=[MorphemeInfoType.FORM],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.NOUN_SUFFIX,
                PartOfSpeechType.NOUN_PREFIX,
                PartOfSpeechType.ENGLISH_SUFFIX,
                PartOfSpeechType.VERB_STEM,
                PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                PartOfSpeechType.VERB_SUFFIX,
                PartOfSpeechType.VERB_PREFIX,
                PartOfSpeechType.AUXILIARY_NOUN,
                PartOfSpeechType.ADJECTIVE_STEM,
                PartOfSpeechType.ADJECTIVE_SUFFIX,
                PartOfSpeechType.ADJECTIVE_PREFIX,
                PartOfSpeechType.ADNOMINAL_ADJECTIVE,
                PartOfSpeechType.ADVERB,
                PartOfSpeechType.CONJUNCTION,
                PartOfSpeechType.INDEPENDENT_WORD,
                PartOfSpeechType.CONNECTION_SUFFIX,
                PartOfSpeechType.PREDICATE,
                PartOfSpeechType.CASE_MARKING_PARTICLE,
                PartOfSpeechType.QUOTATION_PARTICLE,
                PartOfSpeechType.ADVERBIAL_PARTICLE,
                PartOfSpeechType.SENTENCE_ENDING_PARTICLE,
                PartOfSpeechType.INTERJECTION,
                PartOfSpeechType.BRACKETS,
                PartOfSpeechType.FULL_STOP_PUNCTUATION_MARK,
                PartOfSpeechType.COMMA,
                PartOfSpeechType.BLANK_SPACE,
                PartOfSpeechType.SYMBOL,
                PartOfSpeechType.MONTH,
                PartOfSpeechType.DAY,
                PartOfSpeechType.YEAR_MONTH,
                PartOfSpeechType.MONTH_DAY,
                PartOfSpeechType.HOUR,
                PartOfSpeechType.MINUTE,
                PartOfSpeechType.SECOND,
                PartOfSpeechType.HOUR_MINUTE,
                PartOfSpeechType.MINUTE_SECOND,
                PartOfSpeechType.PRE_HOUR,
                PartOfSpeechType.POST_HOUR,
                PartOfSpeechType.NUMBER,
                PartOfSpeechType.COUNTER_WORD,
                PartOfSpeechType.ORDINAL_NUMBER_SUFFIX,
                PartOfSpeechType.ORDINAL_NUMBER_PREFIX,
                PartOfSpeechType.ALPHABET,
                PartOfSpeechType.HIRAGANA,
                PartOfSpeechType.KATAKANA,
                PartOfSpeechType.KANJI,
                PartOfSpeechType.ROMAN,
                PartOfSpeechType.UNDEFINED,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology("日本語を分析します", "form"),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_list_without_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|form",
            "request_id": "labs.goo.ne.jp\t1654123625\t0",
            "word_list": [
                [
                    ["日本語", "ニホンゴ"],
                    ["を", "ヲ"],
                    ["分析", "ブンセキ"],
                    ["し", "シ"],
                    ["ます", "マス"],
                ]
            ],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form="日本語", pos=None, read="ニホンゴ"),
                    AnalyzedMorpheme(form="を", pos=None, read="ヲ"),
                    AnalyzedMorpheme(form="分析", pos=None, read="ブンセキ"),
                    AnalyzedMorpheme(form="し", pos=None, read="シ"),
                    AnalyzedMorpheme(form="ます", pos=None, read="マス"),
                ]
            ],
            info_filter=[
                MorphemeInfoType.FORM,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.NOUN_SUFFIX,
                PartOfSpeechType.NOUN_PREFIX,
                PartOfSpeechType.ENGLISH_SUFFIX,
                PartOfSpeechType.VERB_STEM,
                PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                PartOfSpeechType.VERB_SUFFIX,
                PartOfSpeechType.VERB_PREFIX,
                PartOfSpeechType.AUXILIARY_NOUN,
                PartOfSpeechType.ADJECTIVE_STEM,
                PartOfSpeechType.ADJECTIVE_SUFFIX,
                PartOfSpeechType.ADJECTIVE_PREFIX,
                PartOfSpeechType.ADNOMINAL_ADJECTIVE,
                PartOfSpeechType.ADVERB,
                PartOfSpeechType.CONJUNCTION,
                PartOfSpeechType.INDEPENDENT_WORD,
                PartOfSpeechType.CONNECTION_SUFFIX,
                PartOfSpeechType.PREDICATE,
                PartOfSpeechType.CASE_MARKING_PARTICLE,
                PartOfSpeechType.QUOTATION_PARTICLE,
                PartOfSpeechType.ADVERBIAL_PARTICLE,
                PartOfSpeechType.SENTENCE_ENDING_PARTICLE,
                PartOfSpeechType.INTERJECTION,
                PartOfSpeechType.BRACKETS,
                PartOfSpeechType.FULL_STOP_PUNCTUATION_MARK,
                PartOfSpeechType.COMMA,
                PartOfSpeechType.BLANK_SPACE,
                PartOfSpeechType.SYMBOL,
                PartOfSpeechType.MONTH,
                PartOfSpeechType.DAY,
                PartOfSpeechType.YEAR_MONTH,
                PartOfSpeechType.MONTH_DAY,
                PartOfSpeechType.HOUR,
                PartOfSpeechType.MINUTE,
                PartOfSpeechType.SECOND,
                PartOfSpeechType.HOUR_MINUTE,
                PartOfSpeechType.MINUTE_SECOND,
                PartOfSpeechType.PRE_HOUR,
                PartOfSpeechType.POST_HOUR,
                PartOfSpeechType.NUMBER,
                PartOfSpeechType.COUNTER_WORD,
                PartOfSpeechType.ORDINAL_NUMBER_SUFFIX,
                PartOfSpeechType.ORDINAL_NUMBER_PREFIX,
                PartOfSpeechType.ALPHABET,
                PartOfSpeechType.HIRAGANA,
                PartOfSpeechType.KATAKANA,
                PartOfSpeechType.KANJI,
                PartOfSpeechType.ROMAN,
                PartOfSpeechType.UNDEFINED,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology("日本語を分析します", ["read", "form"]),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_enum_list_without_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|form",
            "request_id": "labs.goo.ne.jp\t1654123625\t0",
            "word_list": [
                [
                    ["日本語", "ニホンゴ"],
                    ["を", "ヲ"],
                    ["分析", "ブンセキ"],
                    ["し", "シ"],
                    ["ます", "マス"],
                ]
            ],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form="日本語", pos=None, read="ニホンゴ"),
                    AnalyzedMorpheme(form="を", pos=None, read="ヲ"),
                    AnalyzedMorpheme(form="分析", pos=None, read="ブンセキ"),
                    AnalyzedMorpheme(form="し", pos=None, read="シ"),
                    AnalyzedMorpheme(form="ます", pos=None, read="マス"),
                ]
            ],
            info_filter=[
                MorphemeInfoType.FORM,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.NOUN_SUFFIX,
                PartOfSpeechType.NOUN_PREFIX,
                PartOfSpeechType.ENGLISH_SUFFIX,
                PartOfSpeechType.VERB_STEM,
                PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                PartOfSpeechType.VERB_SUFFIX,
                PartOfSpeechType.VERB_PREFIX,
                PartOfSpeechType.AUXILIARY_NOUN,
                PartOfSpeechType.ADJECTIVE_STEM,
                PartOfSpeechType.ADJECTIVE_SUFFIX,
                PartOfSpeechType.ADJECTIVE_PREFIX,
                PartOfSpeechType.ADNOMINAL_ADJECTIVE,
                PartOfSpeechType.ADVERB,
                PartOfSpeechType.CONJUNCTION,
                PartOfSpeechType.INDEPENDENT_WORD,
                PartOfSpeechType.CONNECTION_SUFFIX,
                PartOfSpeechType.PREDICATE,
                PartOfSpeechType.CASE_MARKING_PARTICLE,
                PartOfSpeechType.QUOTATION_PARTICLE,
                PartOfSpeechType.ADVERBIAL_PARTICLE,
                PartOfSpeechType.SENTENCE_ENDING_PARTICLE,
                PartOfSpeechType.INTERJECTION,
                PartOfSpeechType.BRACKETS,
                PartOfSpeechType.FULL_STOP_PUNCTUATION_MARK,
                PartOfSpeechType.COMMA,
                PartOfSpeechType.BLANK_SPACE,
                PartOfSpeechType.SYMBOL,
                PartOfSpeechType.MONTH,
                PartOfSpeechType.DAY,
                PartOfSpeechType.YEAR_MONTH,
                PartOfSpeechType.MONTH_DAY,
                PartOfSpeechType.HOUR,
                PartOfSpeechType.MINUTE,
                PartOfSpeechType.SECOND,
                PartOfSpeechType.HOUR_MINUTE,
                PartOfSpeechType.MINUTE_SECOND,
                PartOfSpeechType.PRE_HOUR,
                PartOfSpeechType.POST_HOUR,
                PartOfSpeechType.NUMBER,
                PartOfSpeechType.COUNTER_WORD,
                PartOfSpeechType.ORDINAL_NUMBER_SUFFIX,
                PartOfSpeechType.ORDINAL_NUMBER_PREFIX,
                PartOfSpeechType.ALPHABET,
                PartOfSpeechType.HIRAGANA,
                PartOfSpeechType.KATAKANA,
                PartOfSpeechType.KANJI,
                PartOfSpeechType.ROMAN,
                PartOfSpeechType.UNDEFINED,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                [MorphemeInfoType.FORM, MorphemeInfoType.READ],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_mixed_list_without_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|form",
            "request_id": "labs.goo.ne.jp\t1654123625\t0",
            "word_list": [
                [
                    ["日本語", "ニホンゴ"],
                    ["を", "ヲ"],
                    ["分析", "ブンセキ"],
                    ["し", "シ"],
                    ["ます", "マス"],
                ]
            ],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form="日本語", pos=None, read="ニホンゴ"),
                    AnalyzedMorpheme(form="を", pos=None, read="ヲ"),
                    AnalyzedMorpheme(form="分析", pos=None, read="ブンセキ"),
                    AnalyzedMorpheme(form="し", pos=None, read="シ"),
                    AnalyzedMorpheme(form="ます", pos=None, read="マス"),
                ]
            ],
            info_filter=[
                MorphemeInfoType.FORM,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.NOUN_SUFFIX,
                PartOfSpeechType.NOUN_PREFIX,
                PartOfSpeechType.ENGLISH_SUFFIX,
                PartOfSpeechType.VERB_STEM,
                PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                PartOfSpeechType.VERB_SUFFIX,
                PartOfSpeechType.VERB_PREFIX,
                PartOfSpeechType.AUXILIARY_NOUN,
                PartOfSpeechType.ADJECTIVE_STEM,
                PartOfSpeechType.ADJECTIVE_SUFFIX,
                PartOfSpeechType.ADJECTIVE_PREFIX,
                PartOfSpeechType.ADNOMINAL_ADJECTIVE,
                PartOfSpeechType.ADVERB,
                PartOfSpeechType.CONJUNCTION,
                PartOfSpeechType.INDEPENDENT_WORD,
                PartOfSpeechType.CONNECTION_SUFFIX,
                PartOfSpeechType.PREDICATE,
                PartOfSpeechType.CASE_MARKING_PARTICLE,
                PartOfSpeechType.QUOTATION_PARTICLE,
                PartOfSpeechType.ADVERBIAL_PARTICLE,
                PartOfSpeechType.SENTENCE_ENDING_PARTICLE,
                PartOfSpeechType.INTERJECTION,
                PartOfSpeechType.BRACKETS,
                PartOfSpeechType.FULL_STOP_PUNCTUATION_MARK,
                PartOfSpeechType.COMMA,
                PartOfSpeechType.BLANK_SPACE,
                PartOfSpeechType.SYMBOL,
                PartOfSpeechType.MONTH,
                PartOfSpeechType.DAY,
                PartOfSpeechType.YEAR_MONTH,
                PartOfSpeechType.MONTH_DAY,
                PartOfSpeechType.HOUR,
                PartOfSpeechType.MINUTE,
                PartOfSpeechType.SECOND,
                PartOfSpeechType.HOUR_MINUTE,
                PartOfSpeechType.MINUTE_SECOND,
                PartOfSpeechType.PRE_HOUR,
                PartOfSpeechType.POST_HOUR,
                PartOfSpeechType.NUMBER,
                PartOfSpeechType.COUNTER_WORD,
                PartOfSpeechType.ORDINAL_NUMBER_SUFFIX,
                PartOfSpeechType.ORDINAL_NUMBER_PREFIX,
                PartOfSpeechType.ALPHABET,
                PartOfSpeechType.HIRAGANA,
                PartOfSpeechType.KATAKANA,
                PartOfSpeechType.KANJI,
                PartOfSpeechType.ROMAN,
                PartOfSpeechType.UNDEFINED,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                [MorphemeInfoType.FORM, "read"],
            ),
            expected_result,
        )

    def test_analyze_morphology_without_info_filter_with_pos_filter_as_string(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "pos_filter": "名詞",
            "request_id": "labs.goo.ne.jp\t1654124620\t0",
            "word_list": [[["日本語", "名詞", "ニホンゴ"], ["分析", "名詞", "ブンセキ"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(
                        form="日本語", pos=PartOfSpeechType.NOUN, read="ニホンゴ"
                    ),
                    AnalyzedMorpheme(form="分析", pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                ]
            ],
            info_filter=[
                MorphemeInfoType.FORM,
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[PartOfSpeechType.NOUN],
        )

        self.assertEqual(
            self.service.analyze_morphology("日本語を分析します", pos_filter="名詞"),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_with_pos_filter_as_string(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter="read|pos",
                pos_filter="名詞|動詞接尾辞",
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_list_with_pos_filter_as_string(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=["read", "pos"],
                pos_filter="名詞|動詞接尾辞",
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_enum_list_with_pos_filter_as_string(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=[MorphemeInfoType.READ, MorphemeInfoType.PART_OF_SPEECH],
                pos_filter="名詞|動詞接尾辞",
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_mixed_list_with_pos_filter_as_string(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=[MorphemeInfoType.READ, "pos"],
                pos_filter="名詞|動詞接尾辞",
            ),
            expected_result,
        )

    def test_analyze_morphology_without_info_filter_with_pos_filter_as_string_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654124997\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["分析", "名詞", "ブンセキ"],
                    ["ます", "動詞接尾辞", "マス"],
                ]
            ],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(
                        form="日本語", pos=PartOfSpeechType.NOUN, read="ニホンゴ"
                    ),
                    AnalyzedMorpheme(form="分析", pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form="ます", pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.FORM,
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology("日本語を分析します", pos_filter=["名詞", "動詞接尾辞"]),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_with_pos_filter_as_string_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter="read|pos",
                pos_filter=["名詞", "動詞接尾辞"],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_list_with_pos_filter_as_string_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=["read", "pos"],
                pos_filter=["名詞", "動詞接尾辞"],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_enum_list_with_pos_filter_as_string_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=[MorphemeInfoType.READ, MorphemeInfoType.PART_OF_SPEECH],
                pos_filter=["名詞", "動詞接尾辞"],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_mixed_list_with_pos_filter_as_string_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=[MorphemeInfoType.READ, "pos"],
                pos_filter=["名詞", "動詞接尾辞"],
            ),
            expected_result,
        )

    def test_analyze_morphology_without_info_filter_with_pos_filter_as_enum_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654124997\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["分析", "名詞", "ブンセキ"],
                    ["ます", "動詞接尾辞", "マス"],
                ]
            ],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(
                        form="日本語", pos=PartOfSpeechType.NOUN, read="ニホンゴ"
                    ),
                    AnalyzedMorpheme(form="分析", pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form="ます", pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.FORM,
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                pos_filter=[PartOfSpeechType.NOUN, PartOfSpeechType.VERB_SUFFIX],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_with_pos_filter_as_enum_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter="read|pos",
                pos_filter=[PartOfSpeechType.NOUN, PartOfSpeechType.VERB_SUFFIX],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_list_with_pos_filter_as_enum_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=["pos", "read"],
                pos_filter=[PartOfSpeechType.NOUN, PartOfSpeechType.VERB_SUFFIX],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_enum_list_with_pos_filter_as_enum_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=[MorphemeInfoType.PART_OF_SPEECH, MorphemeInfoType.READ],
                pos_filter=[PartOfSpeechType.NOUN, PartOfSpeechType.VERB_SUFFIX],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_mixed_list_with_pos_filter_as_enum_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=["pos", MorphemeInfoType.READ],
                pos_filter=[PartOfSpeechType.NOUN, PartOfSpeechType.VERB_SUFFIX],
            ),
            expected_result,
        )

    def test_analyze_morphology_without_info_filter_with_pos_filter_as_mixed_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654124997\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["分析", "名詞", "ブンセキ"],
                    ["ます", "動詞接尾辞", "マス"],
                ]
            ],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(
                        form="日本語", pos=PartOfSpeechType.NOUN, read="ニホンゴ"
                    ),
                    AnalyzedMorpheme(form="分析", pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form="ます", pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.FORM,
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します", pos_filter=[PartOfSpeechType.NOUN, "動詞接尾辞"]
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_with_pos_filter_as_mixed_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter="read|pos",
                pos_filter=[PartOfSpeechType.NOUN, "動詞接尾辞"],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_string_list_with_pos_filter_as_mixed_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=["pos", "read"],
                pos_filter=[PartOfSpeechType.NOUN, "動詞接尾辞"],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_enum_list_with_pos_filter_as_mixed_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=[MorphemeInfoType.PART_OF_SPEECH, MorphemeInfoType.READ],
                pos_filter=[PartOfSpeechType.NOUN, "動詞接尾辞"],
            ),
            expected_result,
        )

    def test_analyze_morphology_with_info_filter_as_mixed_list_with_pos_filter_as_mixed_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "info_filter": "read|pos",
            "pos_filter": "名詞|動詞接尾辞",
            "request_id": "labs.goo.ne.jp\t1654210962\t0",
            "word_list": [[["名詞", "ニホンゴ"], ["名詞", "ブンセキ"], ["動詞接尾辞", "マス"]]],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ニホンゴ"),
                    AnalyzedMorpheme(form=None, pos=PartOfSpeechType.NOUN, read="ブンセキ"),
                    AnalyzedMorpheme(
                        form=None, pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                ]
            ],
            info_filter=[
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.VERB_SUFFIX,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology(
                "日本語を分析します",
                info_filter=["pos", MorphemeInfoType.READ],
                pos_filter=[PartOfSpeechType.NOUN, "動詞接尾辞"],
            ),
            expected_result,
        )

    def test_analyze_morphology_processes_multiple_sentences(self) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654212441\t0",
            "word_list": [
                [
                    ["私", "名詞", "ワタシ"],
                    ["は", "連用助詞", "ハ"],
                    ["この", "連体詞", "コノ"],
                    ["ボット", "名詞", "ボット"],
                    ["を", "格助詞", "ヲ"],
                    ["作", "動詞語幹", "ツク"],
                    ["り", "動詞活用語尾", "リ"],
                    ["始め", "動詞接尾辞", "ハジメ"],
                    ["ました", "動詞接尾辞", "マシタ"],
                    ["。", "句点", ""],
                ],
                [
                    ["そして", "接続詞", "ソシテ"],
                    ["ボット", "名詞", "ボット"],
                    ["は", "連用助詞", "ハ"],
                    ["働", "動詞語幹", "ハタラ"],
                    ["き", "動詞活用語尾", "キ"],
                    ["始め", "動詞接尾辞", "ハジメ"],
                    ["ます", "動詞接尾辞", "マス"],
                    ["。", "句点", ""],
                ],
            ],
        }

        expected_result = AnalyzedMorphology(
            word_list=[
                [
                    AnalyzedMorpheme(form="私", pos=PartOfSpeechType.NOUN, read="ワタシ"),
                    AnalyzedMorpheme(
                        form="は", pos=PartOfSpeechType.ADVERBIAL_PARTICLE, read="ハ"
                    ),
                    AnalyzedMorpheme(
                        form="この", pos=PartOfSpeechType.ADNOMINAL_ADJECTIVE, read="コノ"
                    ),
                    AnalyzedMorpheme(form="ボット", pos=PartOfSpeechType.NOUN, read="ボット"),
                    AnalyzedMorpheme(
                        form="を", pos=PartOfSpeechType.CASE_MARKING_PARTICLE, read="ヲ"
                    ),
                    AnalyzedMorpheme(
                        form="作", pos=PartOfSpeechType.VERB_STEM, read="ツク"
                    ),
                    AnalyzedMorpheme(
                        form="り",
                        pos=PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                        read="リ",
                    ),
                    AnalyzedMorpheme(
                        form="始め", pos=PartOfSpeechType.VERB_SUFFIX, read="ハジメ"
                    ),
                    AnalyzedMorpheme(
                        form="ました", pos=PartOfSpeechType.VERB_SUFFIX, read="マシタ"
                    ),
                    AnalyzedMorpheme(
                        form="。",
                        pos=PartOfSpeechType.FULL_STOP_PUNCTUATION_MARK,
                        read="",
                    ),
                ],
                [
                    AnalyzedMorpheme(
                        form="そして", pos=PartOfSpeechType.CONJUNCTION, read="ソシテ"
                    ),
                    AnalyzedMorpheme(form="ボット", pos=PartOfSpeechType.NOUN, read="ボット"),
                    AnalyzedMorpheme(
                        form="は", pos=PartOfSpeechType.ADVERBIAL_PARTICLE, read="ハ"
                    ),
                    AnalyzedMorpheme(
                        form="働", pos=PartOfSpeechType.VERB_STEM, read="ハタラ"
                    ),
                    AnalyzedMorpheme(
                        form="き",
                        pos=PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                        read="キ",
                    ),
                    AnalyzedMorpheme(
                        form="始め", pos=PartOfSpeechType.VERB_SUFFIX, read="ハジメ"
                    ),
                    AnalyzedMorpheme(
                        form="ます", pos=PartOfSpeechType.VERB_SUFFIX, read="マス"
                    ),
                    AnalyzedMorpheme(
                        form="。",
                        pos=PartOfSpeechType.FULL_STOP_PUNCTUATION_MARK,
                        read="",
                    ),
                ],
            ],
            info_filter=[
                MorphemeInfoType.FORM,
                MorphemeInfoType.PART_OF_SPEECH,
                MorphemeInfoType.READ,
            ],
            pos_filter=[
                PartOfSpeechType.NOUN,
                PartOfSpeechType.NOUN_SUFFIX,
                PartOfSpeechType.NOUN_PREFIX,
                PartOfSpeechType.ENGLISH_SUFFIX,
                PartOfSpeechType.VERB_STEM,
                PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                PartOfSpeechType.VERB_SUFFIX,
                PartOfSpeechType.VERB_PREFIX,
                PartOfSpeechType.AUXILIARY_NOUN,
                PartOfSpeechType.ADJECTIVE_STEM,
                PartOfSpeechType.ADJECTIVE_SUFFIX,
                PartOfSpeechType.ADJECTIVE_PREFIX,
                PartOfSpeechType.ADNOMINAL_ADJECTIVE,
                PartOfSpeechType.ADVERB,
                PartOfSpeechType.CONJUNCTION,
                PartOfSpeechType.INDEPENDENT_WORD,
                PartOfSpeechType.CONNECTION_SUFFIX,
                PartOfSpeechType.PREDICATE,
                PartOfSpeechType.CASE_MARKING_PARTICLE,
                PartOfSpeechType.QUOTATION_PARTICLE,
                PartOfSpeechType.ADVERBIAL_PARTICLE,
                PartOfSpeechType.SENTENCE_ENDING_PARTICLE,
                PartOfSpeechType.INTERJECTION,
                PartOfSpeechType.BRACKETS,
                PartOfSpeechType.FULL_STOP_PUNCTUATION_MARK,
                PartOfSpeechType.COMMA,
                PartOfSpeechType.BLANK_SPACE,
                PartOfSpeechType.SYMBOL,
                PartOfSpeechType.MONTH,
                PartOfSpeechType.DAY,
                PartOfSpeechType.YEAR_MONTH,
                PartOfSpeechType.MONTH_DAY,
                PartOfSpeechType.HOUR,
                PartOfSpeechType.MINUTE,
                PartOfSpeechType.SECOND,
                PartOfSpeechType.HOUR_MINUTE,
                PartOfSpeechType.MINUTE_SECOND,
                PartOfSpeechType.PRE_HOUR,
                PartOfSpeechType.POST_HOUR,
                PartOfSpeechType.NUMBER,
                PartOfSpeechType.COUNTER_WORD,
                PartOfSpeechType.ORDINAL_NUMBER_SUFFIX,
                PartOfSpeechType.ORDINAL_NUMBER_PREFIX,
                PartOfSpeechType.ALPHABET,
                PartOfSpeechType.HIRAGANA,
                PartOfSpeechType.KATAKANA,
                PartOfSpeechType.KANJI,
                PartOfSpeechType.ROMAN,
                PartOfSpeechType.UNDEFINED,
            ],
        )

        self.assertEqual(
            self.service.analyze_morphology("私はこのボットを作り始めました。 そしてボットは働き始めます。"),
            expected_result,
        )

    def test_raises_InvalidArgsForGoolabsRequestError_on_analyze_morphology_sentence_is_not_a_string_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.analyze_morphology(0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_analyze_morphology_empty_sentence_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.analyze_morphology("")

    def test_raises_InvalidArgsForGoolabsRequestError_on_analyze_morphology_sentence_is_not_a_string_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.analyze_morphology(sentence=0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_analyze_morphology_empty_sentence_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.analyze_morphology(sentence="")

    def test_raises_InvalidArgsForGoolabsRequestError_on_analyze_morphology_info_filter_has_incorrect_type(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.analyze_morphology("日本語を分析します。", info_filter=0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_analyze_morphology_class_filter_has_incorrect_format(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.analyze_morphology("日本語を分析します。", info_filter="incorrect")

    def test_raises_InvalidArgsForGoolabsRequestError_on_analyze_morphology_pos_filter_has_incorrect_type(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.analyze_morphology("日本語を分析します。", pos_filter=0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_analyze_morphology_pos_filter_has_incorrect_format(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.analyze_morphology("日本語を分析します。", pos_filter="incorrect")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_no_request_id(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["を", "格助詞", "ヲ"],
                    ["分析", "名詞", "ブンセキ"],
                    ["し", "動詞活用語尾", "シ"],
                    ["ます", "動詞接尾辞", "マス"],
                ]
            ],
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_no_word_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_no_info_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語"],
                    ["を"],
                    ["分析"],
                    ["し"],
                    ["ます"],
                ]
            ],
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", "form")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_redundant_info_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["を", "格助詞", "ヲ"],
                    ["分析", "名詞", "ブンセキ"],
                    ["し", "動詞活用語尾", "シ"],
                    ["ます", "動詞接尾辞", "マス"],
                ]
            ],
            "info_filter": "form",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_no_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["分析", "名詞", "ブンセキ"],
                ]
            ],
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", pos_filter="名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_redundant_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["を", "格助詞", "ヲ"],
                    ["分析", "名詞", "ブンセキ"],
                    ["し", "動詞活用語尾", "シ"],
                    ["ます", "動詞接尾辞", "マス"],
                ]
            ],
            "pos_filter": "名詞",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_word_list_is_not_a_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": "",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_info_filter_is_not_a_string(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["ニホンゴ"],
                    ["ヲ"],
                    ["ブンセキ"],
                    ["シ"],
                    ["マス"],
                ]
            ],
            "info_filter": 0,
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", "read")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_pos_filter_is_not_a_string(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["分析", "名詞", "ブンセキ"],
                ]
            ],
            "pos_filter": 0,
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", pos_filter="名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_error_response(
        self,
    ) -> None:
        self.service.api.morph.return_value = {"error": "error"}

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_redundant_key_without_info_filter_without_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["を", "格助詞", "ヲ"],
                    ["分析", "名詞", "ブンセキ"],
                    ["し", "動詞活用語尾", "シ"],
                    ["ます", "動詞接尾辞", "マス"],
                ]
            ],
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_redundant_key_with_info_filter_without_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語"],
                    ["を"],
                    ["分析"],
                    ["し"],
                    ["ます"],
                ]
            ],
            "info_filter": "form",
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", info_filter="form")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_redundant_key_without_info_filter_with_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["分析", "名詞", "ブンセキ"],
                ]
            ],
            "pos_filter": "名詞",
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", pos_filter="名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_redundant_key_with_info_filter_with_pos_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語"],
                    ["分析"],
                ]
            ],
            "info_filter": "form",
            "pos_filter": "名詞",
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", "form", "名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_not_a_dict(
        self,
    ) -> None:
        self.service.api.morph.return_value = ""

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_incorrect_info_filter_format(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語"],
                    ["分析"],
                ]
            ],
            "info_filter": "incorrect",
            "pos_filter": "名詞",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", "form", "名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_incorrect_pos_filter_format(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語"],
                    ["分析"],
                ]
            ],
            "info_filter": "form",
            "pos_filter": "incorrect",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", "form", "名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_sentence_entity_is_not_a_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [[["日本語"], ["分析"]], ""],
            "info_filter": "form",
            "pos_filter": "名詞",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", "form", "名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_morpheme_entity_is_not_a_list(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [["日本語", ["分析"]]],
            "info_filter": "form",
            "pos_filter": "名詞",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", "form", "名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_morpheme_entity_has_not_enough_items(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [[[], ["分析"]]],
            "info_filter": "form",
            "pos_filter": "名詞",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", "form", "名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_morpheme_entity_has_a_redundant_item_with_info_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [[["日本語", "redundant"], ["分析"]]],
            "info_filter": "form",
            "pos_filter": "名詞",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", "form", "名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_morpheme_entity_has_a_redundant_item_without_info_filter(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語", "名詞", "ニホンゴ"],
                    ["分析", "名詞", "ブンセキ", "redundant"],
                ]
            ],
            "pos_filter": "名詞",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", pos_filter="名詞")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_analyze_morphology_morpheme_entity_pos_has_incorrect_format(
        self,
    ) -> None:
        self.service.api.morph.return_value = {
            "request_id": "labs.goo.ne.jp\t1654210596\t0",
            "word_list": [
                [
                    ["日本語", "incorrect", "ニホンゴ"],
                    ["分析", "名詞", "ブンセキ"],
                ]
            ],
            "pos_filter": "名詞",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.analyze_morphology("日本語を分析します", pos_filter="名詞")

    def test_extract_slot_values_without_slot_filter(self) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        expected_result = ExtractedSlotValues(
            name=[NameSlot(surname="田中", given_name="太郎")],
            birthday=[BirthdaySlot(value="3-4-1", norm_value=None)],
            sex=[SexSlot(value="男性", norm_value="男性")],
            address=[
                AddressSlot(
                    value="港区芝浦3-4-1",
                    norm_value="東京都港区芝浦三丁目4-1",
                    latitude=35.643462,
                    longitude=139.746042,
                )
            ],
            telephone=[],
            age=[AgeSlot(value="30歳", norm_value=30)],
            slot_filter=[
                SlotType.NAME,
                SlotType.BIRTHDAY,
                SlotType.SEX,
                SlotType.ADDRESS,
                SlotType.TELEPHONE,
                SlotType.AGE,
            ],
        )

        self.assertEqual(
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。"),
            expected_result,
        )

    def test_extract_slot_values_with_slot_filter_as_string(self) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": "age|birthday",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
            },
        }

        expected_result = ExtractedSlotValues(
            name=None,
            birthday=[BirthdaySlot(value="3-4-1", norm_value=None)],
            sex=None,
            address=None,
            telephone=None,
            age=[AgeSlot(value="30歳", norm_value=30)],
            slot_filter=[SlotType.BIRTHDAY, SlotType.AGE],
        )

        self.assertEqual(
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。",
                "age|birthday",
            ),
            expected_result,
        )

    def test_extract_slot_values_with_slot_filter_as_string_list(self) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": "age|birthday",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
            },
        }

        expected_result = ExtractedSlotValues(
            name=None,
            birthday=[BirthdaySlot(value="3-4-1", norm_value=None)],
            sex=None,
            address=None,
            telephone=None,
            age=[AgeSlot(value="30歳", norm_value=30)],
            slot_filter=[SlotType.BIRTHDAY, SlotType.AGE],
        )

        self.assertEqual(
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。",
                ["age", "birthday"],
            ),
            expected_result,
        )

    def test_extract_slot_values_with_slot_filter_as_enum_list(self) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": "age|birthday",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
            },
        }

        expected_result = ExtractedSlotValues(
            name=None,
            birthday=[BirthdaySlot(value="3-4-1", norm_value=None)],
            sex=None,
            address=None,
            telephone=None,
            age=[AgeSlot(value="30歳", norm_value=30)],
            slot_filter=[SlotType.BIRTHDAY, SlotType.AGE],
        )

        self.assertEqual(
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。",
                [SlotType.AGE, SlotType.BIRTHDAY],
            ),
            expected_result,
        )

    def test_extract_slot_values_with_slot_filter_as_mixed_list(self) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": "age|birthday",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
            },
        }

        expected_result = ExtractedSlotValues(
            name=None,
            birthday=[BirthdaySlot(value="3-4-1", norm_value=None)],
            sex=None,
            address=None,
            telephone=None,
            age=[AgeSlot(value="30歳", norm_value=30)],
            slot_filter=[SlotType.BIRTHDAY, SlotType.AGE],
        )

        self.assertEqual(
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。",
                [SlotType.AGE, "birthday"],
            ),
            expected_result,
        )

    def test_extract_slot_values_processes_tel_slot(self) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654248743\t0",
            "slots": {
                "address": [],
                "age": [],
                "birthday": [],
                "name": [],
                "sex": [],
                "tel": [{"norm_value": "0312345678", "value": "(03)1234-5678"}],
            },
        }

        expected_result = ExtractedSlotValues(
            name=[],
            birthday=[],
            sex=[],
            address=[],
            telephone=[TelephoneSlot(value="(03)1234-5678", norm_value="0312345678")],
            age=[],
            slot_filter=[
                SlotType.NAME,
                SlotType.BIRTHDAY,
                SlotType.SEX,
                SlotType.ADDRESS,
                SlotType.TELEPHONE,
                SlotType.AGE,
            ],
        )

        self.assertEqual(
            self.service.extract_slot_values("私の電話番号は(03)1234-5678です"),
            expected_result,
        )

    def test_extract_slot_values_processes_normal_birthday_slot(self) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654249101\t0",
            "slots": {
                "address": [],
                "age": [{"norm_value": 19, "value": None}],
                "birthday": [{"norm_value": "2002-10-12", "value": "2002年10月12日"}],
                "name": [],
                "sex": [],
                "tel": [],
            },
        }

        expected_result = ExtractedSlotValues(
            name=[],
            birthday=[BirthdaySlot(value="2002年10月12日", norm_value=date(2002, 10, 12))],
            sex=[],
            address=[],
            telephone=[],
            age=[AgeSlot(value=None, norm_value=19)],
            slot_filter=[
                SlotType.NAME,
                SlotType.BIRTHDAY,
                SlotType.SEX,
                SlotType.ADDRESS,
                SlotType.TELEPHONE,
                SlotType.AGE,
            ],
        )

        self.assertEqual(
            self.service.extract_slot_values("私は2002年10月12日に生まれました"),
            expected_result,
        )

    def test_extract_slot_values_processes_out_of_age_range_birthday_slot(self) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654249698\t0",
            "slots": {
                "address": [],
                "age": [],
                "birthday": [{"norm_value": None, "value": "明治4年2月6日"}],
                "name": [],
                "sex": [],
                "tel": [],
            },
        }

        expected_result = ExtractedSlotValues(
            name=[],
            birthday=[BirthdaySlot(value="明治4年2月6日", norm_value=None)],
            sex=[],
            address=[],
            telephone=[],
            age=[],
            slot_filter=[
                SlotType.NAME,
                SlotType.BIRTHDAY,
                SlotType.SEX,
                SlotType.ADDRESS,
                SlotType.TELEPHONE,
                SlotType.AGE,
            ],
        )

        self.assertEqual(
            self.service.extract_slot_values("明治4年2月6日に生まれました。"),
            expected_result,
        )

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_slot_values_sentence_is_not_a_string_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_slot_values(0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_slot_values_empty_sentence_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_slot_values("")

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_slot_values_sentence_is_not_a_string_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_slot_values(sentence=0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_slot_values_empty_sentence_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_slot_values(sentence="")

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_slot_values_slot_filter_has_incorrect_type(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。", 0)

    def test_raises_InvalidArgsForGoolabsRequestError_on_extract_slot_values_slot_filter_has_incorrect_format(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。", "incorrect"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_no_request_id(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            }
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_no_slots(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_no_slot_filter(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。", "age|birthday"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_redundant_slot_filter(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slot_filter": "age|birthday",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_error_response(
        self,
    ) -> None:
        self.service.api.slot.return_value = {"error": "error"}

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_slot_filter_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": 0,
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。", "age|birthday"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_slots_is_not_a_dict(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": "",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_slot_filter_has_incorrect_format(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": "incorrect",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。", "age|birthday"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_redundant_key_without_slot_filter(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_redundant_key_with_slot_filter(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": "age|birthday",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
            },
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。", "age|birthday"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_not_a_dict(
        self,
    ) -> None:
        self.service.api.slot.return_value = ""

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_slots_has_not_enough_keys_with_slot_filter(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": "age|birthday",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。", "age|birthday"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_slots_has_not_enough_keys_without_slot_filter(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_slots_has_a_redundant_impossible_key_with_slot_filter(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": "age|birthday",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "key": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。", "age|birthday"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_slots_has_a_redundant_possible_key_with_slot_filter(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654218246\t0",
            "slot_filter": "age|birthday",
            "slots": {
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values(
                "名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。", "age|birthday"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_slots_has_a_redundant_key_without_slot_filter(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
                "key": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_address_slot_is_not_a_list(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": "",
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_age_slot_is_not_a_list(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": "",
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_birthday_slot_is_not_a_list(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": "",
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_name_slot_is_not_a_list(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": "",
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_sex_slot_is_not_a_list(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": "",
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_tel_slot_is_not_a_list(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": "",
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_address_slot_lat_is_not_a_float(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": [],
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_address_slot_lon_is_not_a_float(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": [],
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_address_slot_value_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": 0,
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_address_slot_norm_value_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": 0,
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_address_has_not_enough_keys(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {"lat": 35.643462, "lon": 139.746042, "value": "港区芝浦3-4-1"}
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_address_slot_has_a_redundant_key(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                        "key": "value",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_age_slot_norm_value_is_not_an_int_or_a_nonetype(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": "30", "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_age_slot_value_is_not_a_string_or_a_nonetype(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": 0}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_age_slot_value_and_norm_value_are_none(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": None, "value": None}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_age_slot_has_not_enough_keys(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_age_slot_has_a_redundant_key(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳", "key": "value"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_birthday_slot_norm_value_has_incorrect_format(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654249101\t0",
            "slots": {
                "address": [],
                "age": [{"norm_value": 19, "value": None}],
                "birthday": [{"norm_value": "incorrect", "value": "2002年10月12日"}],
                "name": [],
                "sex": [],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("私は2002年10月12日に生まれました"),

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_birthday_slot_norm_value_is_not_a_string_or_a_nonetype(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": 0, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_birthday_slot_value_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": 0}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_birthday_slot_norm_value_has_not_enough_keys(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654249101\t0",
            "slots": {
                "address": [],
                "age": [{"norm_value": 19, "value": None}],
                "birthday": [{"value": "2002年10月12日"}],
                "name": [],
                "sex": [],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("私は2002年10月12日に生まれました")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_birthday_slot_norm_value_has_a_redundant_key(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654249101\t0",
            "slots": {
                "address": [],
                "age": [{"norm_value": 19, "value": None}],
                "birthday": [
                    {"norm_value": "2002-10-12", "value": "2002年10月12日", "key": "value"}
                ],
                "name": [],
                "sex": [],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("私は2002年10月12日に生まれました")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_name_slot_given_name_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": 0, "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_name_slot_surname_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": 0}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_name_slot_has_not_enough_keys(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_name_slot_has_a_redundant_key(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中", "key": "value"}],
                "sex": [{"norm_value": "男性", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_sex_slot_value_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": 0}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_sex_slot_norm_value_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": 0, "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_sex_slot_norm_value_has_incorrect_format(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "incorrect", "value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_sex_slot_has_not_enough_keys(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"value": "男性"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_sex_slot_has_a_redundant_key(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089313\t0",
            "slots": {
                "address": [
                    {
                        "lat": 35.643462,
                        "lon": 139.746042,
                        "norm_value": "東京都港区芝浦三丁目4-1",
                        "value": "港区芝浦3-4-1",
                    }
                ],
                "age": [{"norm_value": 30, "value": "30歳"}],
                "birthday": [{"norm_value": None, "value": "3-4-1"}],
                "name": [{"given_name": "太郎", "surname": "田中"}],
                "sex": [{"norm_value": "男性", "value": "男性", "key": "value"}],
                "tel": [],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("名前は田中太郎で、男性で、30歳です。港区芝浦3-4-1に住んでいます。")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_tel_slot_value_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654248743\t0",
            "slots": {
                "address": [],
                "age": [],
                "birthday": [],
                "name": [],
                "sex": [],
                "tel": [{"norm_value": "0312345678", "value": 0}],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("私の電話番号は(03)1234-5678です")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_tel_slot_norm_value_is_not_a_string(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654248743\t0",
            "slots": {
                "address": [],
                "age": [],
                "birthday": [],
                "name": [],
                "sex": [],
                "tel": [{"norm_value": 0, "value": "(03)1234-5678"}],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("私の電話番号は(03)1234-5678です")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_tel_slot_value_has_not_enough_keys(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654248743\t0",
            "slots": {
                "address": [],
                "age": [],
                "birthday": [],
                "name": [],
                "sex": [],
                "tel": [{"norm_value": "0312345678"}],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("私の電話番号は(03)1234-5678です")

    def test_raises_GoolabsAPIUnexpectedResponseError_on_extract_slot_values_tel_slot_value_has_a_redundant_key(
        self,
    ) -> None:
        self.service.api.slot.return_value = {
            "request_id": "labs.goo.ne.jp\t1654248743\t0",
            "slots": {
                "address": [],
                "age": [],
                "birthday": [],
                "name": [],
                "sex": [],
                "tel": [
                    {
                        "norm_value": "0312345678",
                        "value": "(03)1234-5678",
                        "key": "value",
                    }
                ],
            },
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.extract_slot_values("私の電話番号は(03)1234-5678です")

    def test_calculate_similarity(self) -> None:
        self.service.api.textpair.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089869\t3289",
            "score": 0.633348,
        }

        expected_result = CalculatedSimilarity(score=0.633348)

        self.assertEqual(
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。", "山田さんはイギリスに留学している。"
            ),
            expected_result,
        )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_text1_is_not_a_string_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                0,
                "山田さんはイギリスに留学している",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_empty_text1_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                "",
                "山田さんはイギリスに留学している",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_text2_is_not_a_string_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。",
                0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_empty_text2_as_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。",
                0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_empty_text1_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                text1="",
                text2="山田さんはイギリスに留学している",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_text1_is_not_a_string_as_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                text1=0,
                text2="山田さんはイギリスに留学している",
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_text2_is_not_a_string_as_kwarg_text1_is_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。",
                text2=0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_empty_text2_as_kwarg_text1_is_arg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。",
                text2=0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_text2_is_not_a_string_as_kwarg_text1_is_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                text1="高橋さんはアメリカに出張に行きました。",
                text2=0,
            )

    def test_raises_InvalidArgsForGoolabsRequestError_on_calculate_similarity_empty_text2_as_kwarg_text1_is_kwarg(
        self,
    ) -> None:
        with self.assertRaises(InvalidArgsForGoolabsRequestError):
            self.service.calculate_similarity(
                text1="高橋さんはアメリカに出張に行きました。",
                text2=0,
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_calculate_similarity_no_request_id(
        self,
    ) -> None:
        self.service.api.textpair.return_value = {"score": 0.633348}

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。", "山田さんはイギリスに留学している。"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_calculate_similarity_no_score(
        self,
    ) -> None:
        self.service.api.textpair.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089869\t3289",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。", "山田さんはイギリスに留学している。"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_calculate_similarity_error_response(
        self,
    ) -> None:
        self.service.api.textpair.return_value = {"error": "error"}

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。", "山田さんはイギリスに留学している。"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_calculate_similarity_not_a_dict(
        self,
    ) -> None:
        self.service.api.textpair.return_value = ""

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。", "山田さんはイギリスに留学している。"
            )

    def test_raises_GoolabsAPIUnexpectedResponseError_on_calculate_similarity_redundant_key(
        self,
    ) -> None:
        self.service.api.textpair.return_value = {
            "request_id": "labs.goo.ne.jp\t1654089869\t3289",
            "score": 0.633348,
            "key": "value",
        }

        with self.assertRaises(UnexpectedGoolabsAPIResponseError):
            self.service.calculate_similarity(
                "高橋さんはアメリカに出張に行きました。", "山田さんはイギリスに留学している。"
            )
