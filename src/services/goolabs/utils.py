from copy import copy
from datetime import datetime
from enum import Enum
from functools import wraps
import inspect
from typing import Any, Callable, Iterable, Type

from logging import getLogger, Logger

from requests.exceptions import HTTPError

from services.exceptions import (
    UnexpectedGoolabsAPIResponseError,
    InvalidArgsForGoolabsRequestError,
)
from .goolabs_value_objects import GoolabsDatetime


def _match_response_for_error(response: dict) -> None:
    match response:
        case {"error": error}:
            raise UnexpectedGoolabsAPIResponseError(f"Response error, {error=}")
        case {}:
            pass
        case _:
            raise UnexpectedGoolabsAPIResponseError(f"{response=} is not a dict")


def _compare_keys_with_response(
    response: dict, keys: Iterable[tuple[str, type]]
) -> None:
    resp = copy(response)
    for key, key_type in keys:
        if key not in resp:
            raise UnexpectedGoolabsAPIResponseError(
                f"Expected {key=} is not found in {resp=}"
            )
        if not isinstance(value := resp.pop(key), key_type):
            raise UnexpectedGoolabsAPIResponseError(
                f"Response {key=} with {value=} has unexpected type. "
                f"Expected {key_type}, found {type(value)}"
            )
    if resp:
        raise UnexpectedGoolabsAPIResponseError(
            f"{response=} has redundant keys - {resp.keys()}"
        )


def response_processing_method(keys: Iterable[tuple[str, type]] = tuple()) -> Callable:
    def function_wrapper(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(
            response: dict, optional_keys: Iterable[tuple[str, type] | None] = tuple()
        ) -> Any:
            try:
                _match_response_for_error(response)
                _compare_keys_with_response(
                    response,
                    [
                        *keys,
                        *filter(None, optional_keys),
                        ("request_id", str),
                    ],
                )
                return func(response)
            except UnexpectedGoolabsAPIResponseError as exception:
                raise UnexpectedGoolabsAPIResponseError(
                    f"{exception=} inside {response=} processed with {func.__name__}"
                )

        return wrapper

    return function_wrapper


def _validate_the_parameter_is_a_non_empty_string(
    parameter_name: str, parameter_value: str
) -> None:
    match parameter_value:
        case str() if parameter_value:
            pass
        case _:
            raise InvalidArgsForGoolabsRequestError(
                f"Parameter '{parameter_name}' with {parameter_value=} is not a non-empty string"
            )


def _validate_non_default_parameters_are_not_empty_strings(
    func: Callable, args: tuple, kwargs: dict
) -> None:
    non_default_arg_names = [
        arg_name
        for arg_name, parameter in inspect.signature(func).parameters.items()
        if parameter.default is inspect.Parameter.empty
    ]
    non_default_arg_names.remove("self")
    for arg_name in copy(non_default_arg_names):
        if arg_name in kwargs:
            _validate_the_parameter_is_a_non_empty_string(arg_name, kwargs[arg_name])
            non_default_arg_names.remove(arg_name)
    for index, parameter_value in enumerate(args[: len(non_default_arg_names)]):
        _validate_the_parameter_is_a_non_empty_string(
            non_default_arg_names[index], parameter_value
        )


def goolabs_methods_class(cls: Any, logger: Logger = getLogger(__name__)) -> Any:
    def goolabs_service_method(method: Callable) -> Callable:
        @wraps(method)
        def method_wrapper(self: cls, *args: Any, **kwargs: Any) -> Any:
            logger.info(
                f"Started processing {args=} and {kwargs=} with {method.__name__} method."
            )
            try:
                _validate_non_default_parameters_are_not_empty_strings(
                    method, args, kwargs
                )
                result = method(self, *args, **kwargs)
                logger.info(
                    f"Successfully got {result=} {method.__name__} method called with {args=} and {kwargs=}."
                )
                return result
            except (
                InvalidArgsForGoolabsRequestError,
                UnexpectedGoolabsAPIResponseError,
            ) as exception:
                logger.error(
                    f"Goolabs {exception=} occurred in {method.__name__} method called with {args=} and {kwargs=}."
                )
                raise exception
            except HTTPError as exception:
                logger.error(
                    f"HTTP {exception=} occurred in {method.__name__} method called with {args=} and {kwargs=}."
                )
                raise exception

        return method_wrapper

    def class_wrapper(cls: Any) -> Any:
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith("_"):
                setattr(cls, name, goolabs_service_method(method))
        return cls

    return class_wrapper(cls)


def convert_the_datetime_value_to_goolabs_format(
    datetime_value: str | datetime | None,
) -> str | None:
    # Used in args processing
    match datetime_value:
        case None:
            return None
        case str():
            try:
                return GoolabsDatetime.from_goolabs_format(datetime_value).isoformat()
            except ValueError:
                raise InvalidArgsForGoolabsRequestError(
                    f"{datetime_value=} has unexpected time format"
                )
        case datetime():
            return datetime_value.isoformat()
        case _:
            raise InvalidArgsForGoolabsRequestError(f"{datetime_value=} unrecognised")


def convert_num_value_to_int_in_range(
    num_value: int | str | None, min_value: int = 1, max_value: int = 10
) -> int | None:
    match num_value:
        case None:
            return None
        case int() if min_value <= num_value <= max_value:
            return num_value
        case str() if num_value.isdecimal() and min_value <= (
            num := int(num_value)
        ) <= max_value:
            return num
        case _:
            raise InvalidArgsForGoolabsRequestError(
                f"{num_value=} has incorrect format"
            )


def check_if_the_value_is_in_type_enum(enum: Type[Enum], value: str) -> bool:
    return any(value == item.value for item in enum)


def convert_the_type_enum_value_to_string(
    enum: Type[Enum],
    type_enum_value: str | Enum | None,
    force_type_enum_value_be_not_none: bool = False,
) -> str | None:
    # Used in args processing
    match type_enum_value:
        case None:
            if force_type_enum_value_be_not_none:
                raise InvalidArgsForGoolabsRequestError(
                    f"{type_enum_value=} expected to suit {enum} is None"
                )
            return None
        case enum():
            return type_enum_value.value
        case str() if check_if_the_value_is_in_type_enum(enum, type_enum_value):
            return type_enum_value
        case _:
            raise InvalidArgsForGoolabsRequestError(
                f"{type_enum_value=} expected to suit {enum} have unexpected format"
            )


def convert_filters_to_goolabs_format(
    enum: Type[Enum], filters: Iterable[str | Enum] | str | None
) -> str | None:
    # Used in args processing
    match filters:
        case None:
            return None
        case str():
            return "|".join(
                convert_the_type_enum_value_to_string(enum, filter_value, True)
                for filter_value in filters.split("|")
            )
        case filters_list if isinstance(filters_list, Iterable):
            return "|".join(
                convert_the_type_enum_value_to_string(enum, filter_value, True)
                for filter_value in filters_list
            )
        case _:
            raise InvalidArgsForGoolabsRequestError(
                f"{filters=} expected to suit {enum} have unexpected format"
            )


def get_type_enum_from_response_filter_string(
    enum: Type[Enum], filter_string: str | None
) -> Enum | None:
    # Used in response processing
    if filter_string is None:
        return None
    if check_if_the_value_is_in_type_enum(enum, filter_string):
        return enum(filter_string)
    raise UnexpectedGoolabsAPIResponseError(
        f"{filter_string=} has unexpected format for {enum}"
    )


def get_type_enum_list_from_response_filters_string(
    enum: Type[Enum], filters: str | None = None
) -> list[Enum]:
    # Used in response processing
    match filters:
        case None:
            return [item for item in enum]
        case str(filter_string) if all(
            map(
                lambda x: check_if_the_value_is_in_type_enum(enum, x),
                filter_list := filter_string.split("|"),
            )
        ):
            return [item for item in enum if item.value in filter_list]
        case _:
            raise UnexpectedGoolabsAPIResponseError(
                f"{filters=} have unexpected format for {enum}"
            )
