"""
    .. module:: groupsupport
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains shared helpers used by the Crusoe
                   api-group classes — URL composition, paging, and HTTP
                   error reclassification.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

from typing import Any, Callable, Dict, Iterator, List, Optional
from urllib.parse import quote

from requests import Response

from automojo.errors.exceptions import SemanticError

from automojo.interop.crusoe.exceptions.crusoeexceptions import (
    CrusoeApiError, CrusoeAuthenticationError
)


def encode_segment(*, segment: str) -> str:
    """
        Percent-encode a single URL path segment.

        Each segment is encoded independently with no characters left
        unescaped beyond the unreserved set, so embedded slashes and other
        reserved characters cannot break out of the segment.

        :param segment: The path segment to encode.

        :returns: The percent-encoded segment.

        :raises: :class:`SemanticError` when the segment is ``None`` or empty.
    """
    if segment is None:
        raise SemanticError("URL path segment must not be None.")
    if not isinstance(segment, str):
        raise SemanticError("URL path segment must be a string.")
    if len(segment) == 0:
        raise SemanticError("URL path segment must not be empty.")

    rtnval = quote(segment, safe="")
    return rtnval


def compose_leaf(*, base: str, segments: List[str]) -> str:
    """
        Compose a leaf path by percent-encoding each segment independently
        and joining them under ``base``.

        :param base: The API base path (e.g. ``/v1alpha5``).
        :param segments: The ordered list of path segments to encode.

        :returns: The composed leaf path beginning with ``/``.

        :raises: :class:`SemanticError` when any segment is empty / ``None``.
    """
    if segments is None:
        raise SemanticError("compose_leaf requires a non-None segments list.")

    encoded: List[str] = []
    for segment in segments:
        encoded.append(encode_segment(segment=segment))

    trimmed_base = base
    if trimmed_base.endswith("/"):
        trimmed_base = trimmed_base[:-1]

    joined = "/".join(encoded)
    rtnval = "{0}/{1}".format(trimmed_base, joined)
    return rtnval


def raise_for_status(*, response: Response, action: str) -> None:
    """
        Reclassify a non-2xx Crusoe response into a typed exception.

        HTTP 401 and 403 reclassify into :class:`CrusoeAuthenticationError`;
        every other non-2xx status reclassifies into :class:`CrusoeApiError`.

        :param response: The :class:`Response` to inspect.
        :param action: A short description of the attempted action.

        :returns: ``None``.

        :raises: :class:`CrusoeAuthenticationError`, :class:`CrusoeApiError`.
    """
    status = response.status_code
    if 200 <= status < 300:
        return

    err_msg_lines = ["Crusoe API call failed: {}.".format(action)]
    err_msg_lines.append("STATUS: {}".format(status))
    err_msg_lines.append("RESPONSE:")
    err_msg_lines.append(response.text)
    err_msg = os.linesep.join(err_msg_lines)

    if status == 401 or status == 403:
        raise CrusoeAuthenticationError(err_msg)

    raise CrusoeApiError(err_msg)


def safe_json(*, response: Response) -> Dict[str, Any]:
    """
        Parse a response body as a JSON object, degrading to an empty dict.

        :param response: The :class:`Response` to parse.

        :returns: The decoded object, or an empty dict.
    """
    try:
        payload = response.json()
    except ValueError:
        rtnval: Dict[str, Any] = {}
        return rtnval

    if not isinstance(payload, dict):
        rtnval = {}
        return rtnval

    rtnval = payload
    return rtnval


def iter_paged_items(*, fetch_page: Callable[[Optional[str]], Dict[str, Any]],
                     items_field: str = "items",
                     cursor_field: str = "next_page_token"
                     ) -> Iterator[Dict[str, Any]]:
    """
        Iterate a cursor-paginated Crusoe list endpoint.

        The traversal yields every item across every page; it terminates
        when the page payload reports no further cursor token.

        :param fetch_page: Callable accepting the current cursor token
            (``None`` on the first call) and returning a page dict.
        :param items_field: Name of the items field on each page payload.
        :param cursor_field: Name of the next-cursor field on each page.

        :returns: An iterator over the item dictionaries.
    """
    cursor: Optional[str] = None
    while True:
        page = fetch_page(cursor)

        items = page.get(items_field, None)
        if items is None:
            items = []

        for item in items:
            yield item

        next_cursor = page.get(cursor_field, None)
        if next_cursor is None or len(str(next_cursor)) == 0:
            break
        cursor = next_cursor
    return
