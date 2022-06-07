from typing import Generator, Iterable

from discord import Embed

from utils.translator import Translator
from services.goolabs import *


def display_no_sentence_exception(language: str) -> str:
    return Translator(language)("NO_SENTENCE_EXCEPTION")


def display_error(language: str) -> str:
    return Translator(language)("ERROR")


def display_times(language: str, result: NormalizedTimes, initial: str) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("CHRONO_EMBED_TITLE"),
        description=tr("CHRONO_EMBED_DESCRIPTION").format(
            doc_time=result.doc_time.isoformat(), initial_text=initial
        ),
    )
    embed.add_field(
        name=tr("CHRONO_EMBED_FIELD"),
        value="\n".join(
            f"{time.text} — {time.time.to_goolabs_format()}"
            for time in result.datetime_list
        )
        or tr("NOTHING"),
    )
    return embed


def display_named_entities(
    language: str, result: ExtractedNamedEntities, initial: str
) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("ENTITIES_EMBED_TITLE"),
        description=tr("ENTITIES_EMBED_DESCRIPTION").format(initial_text=initial),
    )
    entities = {ne_type.value: [] for ne_type in NamedEntityType}
    for entity in result.entities:
        entities[entity.entity_type.value].append(entity.text)
    for ne_type in entities:
        if entities[ne_type]:
            embed.add_field(name=tr(ne_type), value="\n".join(entities[ne_type]))
    return embed


def display_furigana(language: str, result: ConvertedToFurigana, initial: str) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("FURIGANA_EMBED_TITLE"),
        description=tr(
            "HIRAGANA_EMBED_DESCRIPTION"
            if result.kana_type is KanaType.HIRAGANA
            else "KATAKANA_EMBED_DESCRIPTION"
        ),
    )
    embed.add_field(
        name=tr("FURIGANA_EMBED_CONVERTED_SENTENCE"),
        value=result.text or tr("NOTHING"),
        inline=False,
    )
    embed.add_field(
        name=tr("FURIGANA_EMBED_INITIAL_SENTENCE"),
        value=initial or tr("NOTHING"),
        inline=False,
    )
    return embed


def display_keywords(language: str, result: ExtractedKeywords, title: str) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("KEYWORDS_EMBED_TITLE"),
        description=tr("KEYWORDS_EMBED_DESCRIPTION").format(title=title),
    )
    for keyword in result.keywords:
        embed.add_field(name=keyword.text, value=str(keyword.score))
    return embed


def _display_morpheme(tr: Translator, morpheme: AnalyzedMorpheme) -> str:
    if morpheme.read:
        return f"**{morpheme.form}** ({morpheme.read}) — {tr(morpheme.pos.value)}"
    else:
        return f"**{morpheme.form}** — {tr(morpheme.pos.value)}"


def _display_sentence(tr: Translator, sentence: AnalyzedSentence) -> str:
    return "\n".join(_display_morpheme(tr, morpheme) for morpheme in sentence)


def display_morphology(
    language: str, result: AnalyzedMorphology, initial: str
) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("MORPHOLOGY_EMBED_TITLE"),
        description=tr("MORPHOLOGY_EMBED_DESCRIPTION").format(
            sentence_count=len(result.word_list), initial_text=initial
        ),
    )
    for index, sentence in enumerate(result.word_list):
        embed.add_field(
            name=tr("MORPHOLOGY_EMBED_SENTENCE_FIELD").format(
                sentence_number=index + 1
            ),
            value=_display_sentence(tr, sentence) or tr("NOTHING"),
        )
    return embed


def _extract_words(
    sentence: AnalyzedSentence,
    prefixes: Iterable[PartOfSpeechType],
    stem: PartOfSpeechType,
    suffixes: Iterable[PartOfSpeechType],
) -> Generator[tuple[AnalyzedMorpheme, ...], None, None]:
    index = 0
    while index < len(sentence):
        result = []
        if sentence[index].pos in prefixes:
            result = [sentence[index]]
            index += 1
            while index <= len(sentence) and sentence[index].pos in prefixes:
                result.append(sentence[index])
                index += 1
            if index >= len(sentence):
                return
            if not sentence[index].pos is stem:
                result = []
        if sentence[index].pos is stem:
            result.append(sentence[index])
            index += 1
            while index < len(sentence) and sentence[index].pos in suffixes:
                result.append(sentence[index])
                index += 1
        else:
            index += 1
        if result:
            yield tuple(result)


def _display_word(tr: Translator, word_tuple: tuple[AnalyzedMorpheme, ...]) -> str:
    morphemes = "\n".join(_display_morpheme(tr, morpheme) for morpheme in word_tuple)
    if len(word_tuple) > 1:
        form, read = map(
            lambda x: "".join(x),
            zip(*((morpheme.form, morpheme.read) for morpheme in word_tuple)),
        )
        return f"**{form}** ({read}):\n{morphemes}"
    else:
        return morphemes


def _display_words(
    tr: Translator,
    words: Generator[tuple[AnalyzedMorpheme, ...], None, None],
) -> str:
    return "\n\n".join(_display_word(tr, word_tuple) for word_tuple in words)


def display_nouns(language: str, result: AnalyzedMorphology, initial: str) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("NOUNS_EMBED_TITLE"),
        description=tr("NOUNS_EMBED_DESCRIPTION").format(
            sentence_count=len(result.word_list), initial_text=initial
        ),
    )
    for index, sentence in enumerate(result.word_list):
        embed.add_field(
            name=tr("NOUNS_EMBED_SENTENCE_FIELD").format(sentence_number=index + 1),
            value=_display_words(
                tr,
                _extract_words(
                    sentence,
                    prefixes=(PartOfSpeechType.NOUN_PREFIX,),
                    stem=PartOfSpeechType.NOUN,
                    suffixes=(
                        PartOfSpeechType.NOUN_SUFFIX,
                        PartOfSpeechType.ENGLISH_SUFFIX,
                    ),
                ),
            )
            or tr("NOTHING"),
        )
    return embed


def display_verbs(language: str, result: AnalyzedMorphology, initial: str) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("VERBS_EMBED_TITLE"),
        description=tr("VERBS_EMBED_DESCRIPTION").format(
            sentence_count=len(result.word_list), initial_text=initial
        ),
    )
    for index, sentence in enumerate(result.word_list):
        embed.add_field(
            name=tr("VERBS_EMBED_SENTENCE_FIELD").format(sentence_number=index + 1),
            value=_display_words(
                tr,
                _extract_words(
                    sentence,
                    prefixes=(PartOfSpeechType.VERB_PREFIX,),
                    stem=PartOfSpeechType.VERB_STEM,
                    suffixes=(
                        PartOfSpeechType.VERB_INFLECTIONAL_ENDING,
                        PartOfSpeechType.VERB_SUFFIX,
                    ),
                ),
            )
            or tr("NOTHING"),
        )
    return embed


def display_adjectives(
    language: str, result: AnalyzedMorphology, initial: str
) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("ADJECTIVES_EMBED_TITLE"),
        description=tr("ADJECTIVES_EMBED_DESCRIPTION").format(
            sentence_count=len(result.word_list), initial_text=initial
        ),
    )
    for index, sentence in enumerate(result.word_list):
        embed.add_field(
            name=tr("ADJECTIVES_EMBED_SENTENCE_FIELD").format(
                sentence_number=index + 1
            ),
            value=_display_words(
                tr,
                _extract_words(
                    sentence,
                    prefixes=(PartOfSpeechType.ADJECTIVE_PREFIX,),
                    stem=PartOfSpeechType.ADJECTIVE_STEM,
                    suffixes=(PartOfSpeechType.ADJECTIVE_SUFFIX,),
                ),
            )
            or tr("NOTHING"),
        )
    return embed


def display_numbers(language: str, result: AnalyzedMorphology, initial: str) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("NUMBERS_EMBED_TITLE"),
        description=tr("NUMBERS_EMBED_DESCRIPTION").format(
            sentence_count=len(result.word_list), initial_text=initial
        ),
    )
    for index, sentence in enumerate(result.word_list):
        embed.add_field(
            name=tr("NUMBERS_EMBED_SENTENCE_FIELD").format(sentence_number=index + 1),
            value=_display_words(
                tr,
                _extract_words(
                    sentence,
                    prefixes=(PartOfSpeechType.ORDINAL_NUMBER_PREFIX,),
                    stem=PartOfSpeechType.NUMBER,
                    suffixes=(
                        PartOfSpeechType.COUNTER_WORD,
                        PartOfSpeechType.ORDINAL_NUMBER_SUFFIX,
                    ),
                ),
            )
            or tr("NOTHING"),
        )
    return embed


def display_slots(language: str, result: ExtractedSlotValues, initial: str) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("SLOTS_EMBED_TITLE"),
        description=tr("SLOTS_EMBED_DESCRIPTION").format(initial_text=initial),
    )
    if result.name:
        embed.add_field(
            name=tr("NAME_SLOT_EMBED_FIELD"),
            value="\n".join(
                f"__{name_slot.surname}__{name_slot.given_name}"
                for name_slot in result.name
            ),
        )
    if result.birthday:
        embed.add_field(
            name=tr("BIRTHDAY_SLOT_EMBED_FIELD"),
            value="\n".join(
                f"{birthday_slot.value if birthday_slot.value else ''}{' — ' if birthday_slot.value and birthday_slot.norm_value else ''}{birthday_slot.norm_value.isoformat() if birthday_slot.norm_value else ''}"
                for birthday_slot in result.birthday
            ),
        )
    if result.sex:
        embed.add_field(
            name=tr("SEX_SLOT_EMBED_FIELD"),
            value="\n".join(
                f"{sex_slot.value} — {sex_slot.norm_value}" for sex_slot in result.sex
            ),
        )
    if result.address:
        embed.add_field(
            name=tr("ADDRESS_SLOT_EMBED_FIELD"),
            value="\n".join(
                f"{address_slot.value} — {address_slot.norm_value} ({address_slot.latitude}, {address_slot.longitude})"
                for address_slot in result.address
            ),
        )
    if result.telephone:
        embed.add_field(
            name=tr("SEX_SLOT_EMBED_FIELD"),
            value="\n".join(
                f"{tel_slot.value} — {tel_slot.norm_value}"
                for tel_slot in result.telephone
            ),
        )
    if result.age:
        embed.add_field(
            name=tr("AGE_SLOT_EMBED_FIELD"),
            value="\n".join(
                f"{age_slot.value if age_slot.value else ''}{' — ' if age_slot.value and age_slot.norm_value else ''}{age_slot.norm_value if age_slot.norm_value else ''}"
                for age_slot in result.age
            ),
        )
    return embed


def display_similarity(
    language: str, result: CalculatedSimilarity, text1: str, text2: str
) -> Embed:
    tr = Translator(language)
    embed = Embed(
        title=tr("SIMILARITY_EMBED_TITLE"),
        description=tr("SIMILARITY_EMBED_DESCRIPTION").format(score=result.score),
    )
    embed.add_field(name=tr("SIMILARITY_EMBED_FIRST_TEST"), value=text1)
    embed.add_field(name=tr("SIMILARITY_EMBED_SECOND_TEST"), value=text2)
    return embed
