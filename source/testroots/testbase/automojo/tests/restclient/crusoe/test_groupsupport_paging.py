"""
    .. module:: test_groupsupport_paging
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Regression tests for ``iter_paged_items`` cursor
                   termination — guards against the cursor-cycle infinite
                   loop (audit RC-H3).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import pytest

from typing import Any, Dict, List, Optional

from automojo.restclient.crusoe.apigroups.groupsupport import iter_paged_items
from automojo.restclient.crusoe.exceptions.crusoeexceptions import CrusoeApiError


def test_iter_paged_items_terminates_on_empty_cursor():
    """
        An empty next-page token terminates traversal.
    """
    pages = [
        {"items": [{"id": "a"}], "next_page_token": "p2"},
        {"items": [{"id": "b"}], "next_page_token": ""},
    ]
    call_count = {"n": 0}

    def fetch_page(cursor: Optional[str]) -> Dict[str, Any]:
        index = call_count["n"]
        call_count["n"] = index + 1
        page = pages[index]
        return page

    collected: List[Dict[str, Any]] = list(iter_paged_items(fetch_page=fetch_page))

    assert len(collected) == 2
    return


def test_iter_paged_items_raises_on_cursor_cycle():
    """
        A repeated cursor token must raise :class:`CrusoeApiError` rather
        than loop forever (audit RC-H3).
    """
    def fetch_page(cursor: Optional[str]) -> Dict[str, Any]:
        page = {"items": [{"id": "x"}], "next_page_token": "stuck"}
        return page

    with pytest.raises(CrusoeApiError):
        list(iter_paged_items(fetch_page=fetch_page))
    return
