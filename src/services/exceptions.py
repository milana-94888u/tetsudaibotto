class UnexpectedGoolabsAPIResponseError(Exception):
    """Received an unexpected response from the Goolabs API"""

    code = "GOOLABS_API_UNEXPECTED_RESPONSE_ERROR"


class InvalidArgsForGoolabsRequestError(Exception):
    """Attempting to pass invalid arguments for a request to the Goolabs API"""

    code = "INVALID_ARGS_FOR_GOOLABS_REQUEST_ERROR"
