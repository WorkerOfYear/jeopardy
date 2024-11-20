from urllib.parse import urlencode

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response


def json_response(data: dict | None = None, status: str = "ok") -> Response:
    return aiohttp_json_response(
        data={
            "status": status,
            "data": data or {},
        }
    )


def error_json_response(
    http_status: int,
    status: str = "error",
    message: str | None = None,
    data: dict | None = None,
):
    return aiohttp_json_response(
        status=http_status,
        data={
            "status": status,
            "message": str(message),
            "data": data or {},
        },
    )


def make_url(base_url, *uris, **params):
    url = base_url.rstrip("/")
    for uri in uris:
        _uri = uri.strip("/")
        url = "{}/{}".format(url, _uri) if _uri else url
    if params:
        url = "{}?{}".format(url, urlencode(params))
    return url
