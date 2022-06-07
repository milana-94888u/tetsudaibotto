from typing import Any, Callable, Literal
from urllib.parse import urljoin

from requests import Session


class GoolabsAPI:
    """
    Is responsible for calling methods of goolabs API.

    Args:
        app_id (str): the id of goolabs registered application
    """

    BASE_API_URL = "https://labs.goo.ne.jp/api/"
    API_NAMES = {
        "chrono",
        "entity",
        "hiragana",
        "keyword",
        "morph",
        "slot",
        "textpair",
    }

    def __init__(self, app_id: str, **kwargs: Any) -> None:
        self._app_id = app_id
        self._prepare_req_args(**kwargs)
        self._session = Session()

    def __getattr__(
        self,
        method_name: Literal[
            "chrono",
            "entity",
            "hiragana",
            "keyword",
            "morph",
            "slot",
            "textpair",
        ],
    ) -> Callable[..., dict]:
        if method_name not in self.API_NAMES:
            raise AttributeError(
                f"Cannot access or call this attribute {method_name}",
            )

        def make_goolabs_post_request(**kwargs: Any) -> dict:
            kwargs = {key: value for key, value in kwargs.items() if value is not None}
            response = self._session.post(
                urljoin(self.BASE_API_URL, method_name),
                json={"app_id": self._app_id} | kwargs,
                **self._req_args,
            )
            response.raise_for_status()
            return response.json()

        return make_goolabs_post_request

    def _prepare_req_args(self, **kwargs: Any) -> None:
        self._req_args = {"timeout": 30, "headers": {}}
        self._req_args.update(kwargs)
        self._req_args["headers"].update({"content-type": "application/json"})
