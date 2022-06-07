class NoSentenceException(Exception):
    """No sentence was provided into command that needs it"""

    code = "NO_SENTENCE_EXCEPTION"


class NoCachedMessageException(Exception):
    """Can't retrieve the cached message"""

    code = "NO_CACHED_MESSAGE_EXCEPTION"
