from enum import Enum


class NamedEntityType(Enum):
    ARTIFACT_NAME = "ART"
    ORGANIZATION_NAME = "ORG"
    PERSON_NAME = "PSN"
    LOCATION_NAME = "LOC"
    DATE_EXPRESSION = "DAT"
    TIME_EXPRESSION = "TIM"
    MONEY_AMOUNT_EXPRESSION = "MNY"
    PERCENTAGE_EXPRESSION = "PCT"


class KanaType(Enum):
    HIRAGANA = "hiragana"
    KATAKANA = "katakana"


class KeywordFocusType(Enum):
    ORGANIZATION_NAME = "ORG"
    PERSON_NAME = "PSN"
    LOCATION_NAME = "LOC"


class MorphemeInfoType(Enum):
    FORM = "form"
    PART_OF_SPEECH = "pos"
    READ = "read"


class PartOfSpeechType(Enum):
    NOUN = "名詞"
    NOUN_SUFFIX = "名詞接尾辞"
    NOUN_PREFIX = "冠名詞"
    ENGLISH_SUFFIX = "英語接尾辞"
    VERB_STEM = "動詞語幹"
    VERB_INFLECTIONAL_ENDING = "動詞活用語尾"
    VERB_SUFFIX = "動詞接尾辞"
    VERB_PREFIX = "冠動詞"
    AUXILIARY_NOUN = "補助名詞"
    ADJECTIVE_STEM = "形容詞語幹"
    ADJECTIVE_SUFFIX = "形容詞接尾辞"
    ADJECTIVE_PREFIX = "冠形容詞"
    ADNOMINAL_ADJECTIVE = "連体詞"
    ADVERB = "連用詞"
    CONJUNCTION = "接続詞"
    INDEPENDENT_WORD = "独立詞"
    CONNECTION_SUFFIX = "接続接尾辞"
    PREDICATE = "判定詞"
    CASE_MARKING_PARTICLE = "格助詞"
    QUOTATION_PARTICLE = "引用助詞"
    ADVERBIAL_PARTICLE = "連用助詞"
    SENTENCE_ENDING_PARTICLE = "終助詞"
    INTERJECTION = "間投詞"
    BRACKETS = "括弧"
    FULL_STOP_PUNCTUATION_MARK = "句点"
    COMMA = "読点"
    BLANK_SPACE = "空白"
    SYMBOL = "Symbol"
    MONTH = "Month"
    DAY = "Day"
    YEAR_MONTH = "YearMonth"
    MONTH_DAY = "MonthDay"
    HOUR = "Hour"
    MINUTE = "Minute"
    SECOND = "Second"
    HOUR_MINUTE = "HourMinute"
    MINUTE_SECOND = "MinuteSecond"
    PRE_HOUR = "PreHour"
    POST_HOUR = "PostHour"
    NUMBER = "Number"
    COUNTER_WORD = "助数詞"
    ORDINAL_NUMBER_SUFFIX = "助助数詞"
    ORDINAL_NUMBER_PREFIX = "冠数詞"
    ALPHABET = "Alphabet"
    HIRAGANA = "Kana"
    KATAKANA = "Katakana"
    KANJI = "Kanji"
    ROMAN = "Roman"
    UNDEFINED = "Undef"


class SlotType(Enum):
    NAME = "name"
    BIRTHDAY = "birthday"
    SEX = "sex"
    ADDRESS = "address"
    TELEPHONE = "tel"
    AGE = "age"
