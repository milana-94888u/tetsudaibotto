from discord.ext import commands
from multilingual_discord.ext.commands import *
import discord

from services.goolabs import GoolabsService

from utils.html_article_extractor import extract_article

from discord_bot.exceptions import NoSentenceException
from discord_bot.display import goolabs_display

from config import DISCORD_LANGUAGE_ALIASES as DLA


async def _get_sentence_from_context(
    ctx: commands.Context, sentence: str | None = None
) -> str:
    match sentence:
        case str():
            return sentence
        case None:
            match reference := ctx.message.reference:
                case discord.message.MessageReference():
                    match reference.cached_message:
                        case discord.message.Message():
                            message = reference.cached_message
                        case None:
                            message = await ctx.channel.fetch_message(
                                reference.message_id
                            )
                        case _:
                            raise NoSentenceException
                    match content := message.content:
                        case str() if content:
                            return content
    raise NoSentenceException


class GoolabsCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.service = GoolabsService()

    @multilingual_command(language_aliases=DLA["CHRONO"])
    async def chrono(self, ctx: MultilingualContext, *, sentence: str = None) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_times(
                ctx.language, self.service.normalize_times(sentence), sentence
            )
        )

    @multilingual_command(language_aliases=DLA["ENTITIES"])
    async def entities(self, ctx: MultilingualContext, *, sentence: str = None) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_named_entities(
                ctx.language, self.service.extract_named_entities(sentence), sentence
            )
        )

    @multilingual_group(invoke_without_command=True, language_aliases=DLA["FURIGANA"])
    async def furigana(self, ctx: MultilingualContext, *, sentence: str = None) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_furigana(
                ctx.language, self.service.convert_to_furigana(sentence), sentence
            )
        )

    @furigana.command(name="hiragana", language_aliases=DLA["HIRAGANA"])
    async def furigana_hiragana(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        await self.hiragana(ctx=ctx, sentence=sentence)

    @furigana.command(name="katakana", language_aliases=DLA["KATAKANA"])
    async def furigana_katakana(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        await self.katakana(ctx=ctx, sentence=sentence)

    @multilingual_command(language_aliases=DLA["HIRAGANA"])
    async def hiragana(self, ctx: MultilingualContext, *, sentence: str = None) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_furigana(
                ctx.language,
                self.service.convert_to_furigana(sentence, "hiragana"),
                sentence,
            )
        )

    @multilingual_command(language_aliases=DLA["KATAKANA"])
    async def katakana(self, ctx: MultilingualContext, *, sentence: str = None) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_furigana(
                ctx.language,
                self.service.convert_to_furigana(sentence, "katakana"),
                sentence,
            )
        )

    @multilingual_group(invoke_without_command=True, language_aliases=DLA["KEYWORDS"])
    async def keywords(self, ctx: MultilingualContext, url: str) -> None:
        title, body = extract_article(url)
        await ctx.reply(
            embed=goolabs_display.display_keywords(
                ctx.language, self.service.extract_keywords(title, body), title
            )
        )

    @keywords.command(name="org", language_aliases=DLA["ORG"])
    async def keywords_org(self, ctx: MultilingualContext, url: str) -> None:
        title, body = extract_article(url)
        await ctx.reply(
            embed=goolabs_display.display_keywords(
                ctx.language,
                self.service.extract_keywords(title, body, focus="ORG"),
                title,
            )
        )

    @keywords.command(name="psn", language_aliases=DLA["PSN"])
    async def keywords_psn(self, ctx: MultilingualContext, url: str) -> None:
        title, body = extract_article(url)
        await ctx.reply(
            embed=goolabs_display.display_keywords(
                ctx.language,
                self.service.extract_keywords(title, body, focus="PSN"),
                title,
            )
        )

    @keywords.command(name="loc", language_aliases=DLA["LOC"])
    async def keywords_loc(self, ctx: MultilingualContext, url: str) -> None:
        title, body = extract_article(url)
        await ctx.reply(
            embed=goolabs_display.display_keywords(
                ctx.language,
                self.service.extract_keywords(title, body, focus="LOC"),
                title,
            )
        )

    @multilingual_group(invoke_without_command=True, language_aliases=DLA["MORPHOLOGY"])
    async def morphology(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_morphology(
                ctx.language, self.service.analyze_morphology(sentence), sentence
            )
        )

    @morphology.command(name="nouns", language_aliases=DLA["NOUNS"])
    async def morphology_nouns(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_nouns(
                ctx.language,
                self.service.analyze_morphology(
                    sentence, pos_filter="??????|???????????????|?????????|???????????????"
                ),
                sentence,
            )
        )

    @morphology.command(name="verbs", language_aliases=DLA["VERBS"])
    async def morphology_verbs(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_verbs(
                ctx.language,
                self.service.analyze_morphology(
                    sentence, pos_filter="????????????|??????????????????|???????????????|?????????"
                ),
                sentence,
            )
        )

    @morphology.command(name="adjectives", language_aliases=DLA["ADJECTIVES"])
    async def morphology_adjectives(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_adjectives(
                ctx.language,
                self.service.analyze_morphology(
                    sentence, pos_filter="???????????????|??????????????????|????????????"
                ),
                sentence,
            )
        )

    @morphology.command(name="numbers", language_aliases=DLA["NUMBERS"])
    async def morphology_numbers(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_numbers(
                ctx.language,
                self.service.analyze_morphology(
                    sentence, pos_filter="Number|?????????|????????????|?????????"
                ),
                sentence,
            )
        )

    @morphology.command(name="auxiliary", language_aliases=DLA["AUXILIARY"])
    async def morphology_auxiliary(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_morphology(
                ctx.language,
                self.service.analyze_morphology(
                    sentence, pos_filter="????????????|?????????|???????????????|?????????|?????????"
                ),
                sentence,
            )
        )

    @morphology.command(name="adverbs", language_aliases=DLA["ADVERBS"])
    async def morphology_adverbs(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_morphology(
                ctx.language,
                self.service.analyze_morphology(sentence, pos_filter="?????????"),
                sentence,
            )
        )

    @morphology.command(name="interjections", language_aliases=DLA["INTERJECTIONS"])
    async def morphology_interjections(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_morphology(
                ctx.language,
                self.service.analyze_morphology(sentence, pos_filter="?????????|?????????"),
                sentence,
            )
        )

    @morphology.command(name="particles", language_aliases=DLA["PARTICLES"])
    async def morphology_particles(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_morphology(
                ctx.language,
                self.service.analyze_morphology(
                    sentence, pos_filter="?????????|????????????|????????????|?????????"
                ),
                sentence,
            )
        )

    @morphology.command(name="punctuation", language_aliases=DLA["PUNCTUATION"])
    async def morphology_punctuation(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_morphology(
                ctx.language,
                self.service.analyze_morphology(
                    sentence, pos_filter="??????|??????|??????|??????|Symbol"
                ),
                sentence,
            )
        )

    @morphology.command(name="unknown", language_aliases=DLA["UNKNOWN"])
    async def morphology_unknown(
        self, ctx: MultilingualContext, *, sentence: str = None
    ) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_morphology(
                ctx.language,
                self.service.analyze_morphology(
                    sentence, pos_filter="Alphabet|Kana|Katakana|Kanji|Roman|Undef"
                ),
                sentence,
            )
        )

    @multilingual_command(language_aliases=DLA["SLOTS"])
    async def slots(self, ctx: MultilingualContext, *, sentence: str = None) -> None:
        sentence = await _get_sentence_from_context(ctx, sentence)
        await ctx.reply(
            embed=goolabs_display.display_slots(
                ctx.language, self.service.extract_slot_values(sentence), sentence
            )
        )

    @multilingual_command(language_aliases=DLA["SIMILARITY"])
    async def similarity(
        self, ctx: MultilingualContext, text1: str, text2: str
    ) -> None:
        await ctx.reply(
            embed=goolabs_display.display_similarity(
                ctx.language,
                self.service.calculate_similarity(text1, text2),
                text1,
                text2,
            )
        )

    async def cog_command_error(self, ctx: MultilingualContext, error) -> None:
        match error:
            case commands.errors.CommandInvokeError():
                match error.original:
                    case NoSentenceException():
                        return await ctx.reply(
                            goolabs_display.display_no_sentence_exception(ctx.language)
                        )
        await ctx.reply(goolabs_display.display_error(ctx.language))
