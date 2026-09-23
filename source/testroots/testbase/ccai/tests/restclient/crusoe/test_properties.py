"""
    .. module:: test_properties
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Property-based (hypothesis) tests for the Crusoe interop
                   client — paging totality, URL composition, idempotent
                   retry, CIDR containment, and task-handle termination.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai import testbase


import ipaddress


from ccai.testbase.properties import given
from ccai.testbase.properties import strategies as st

from ccai.errors.exceptions import SemanticError

from ccai.restclient.crusoe.aspectscrusoe import AspectsCrusoe
from ccai.restclient.crusoe.apigroups.groupsupport import (
    compose_leaf, encode_segment, iter_paged_items
)
from ccai.restclient.crusoe.apigroups.subnetsgroup import cidr_is_contained
from ccai.restclient.crusoe.exceptions.crusoeexceptions import (
    CrusoeCidrValidationError
)
from ccai.restclient.crusoe.model.crusoeoperationresult import (
    CrusoeOperationResult
)
from ccai.restclient.crusoe.model.crusoetaskhandle import (
    CrusoeTaskHandle, map_operation_state
)


# ----------------------------------------------------------------------
# Paging traversal totality
# ----------------------------------------------------------------------

@given(
    constraints={"max_examples": 80},page_sizes=st.lists(st.integers(min_value=0, max_value=5),
                           min_size=1, max_size=8))
def test_paging_traversal_visits_every_item(page_sizes) -> None:
    """
        For any sequence of page item-counts, iter_paged_items yields every
        item exactly once across all pages.
    """
    pages = []
    counter = 0
    for index, count in enumerate(page_sizes):
        items = []
        for _ in range(count):
            items.append({"value": counter})
            counter = counter + 1
        is_last = index == len(page_sizes) - 1
        page = {"items": items}
        if not is_last:
            page["next_page_token"] = "cursor-{}".format(index + 1)
        pages.append(page)

    cursors_seen = []

    def _fetch(cursor):
        cursors_seen.append(cursor)
        if cursor is None:
            rtnval = pages[0]
            return rtnval
        idx = int(cursor.split("-")[1])
        rtnval = pages[idx]
        return rtnval

    collected = list(iter_paged_items(fetch_page=_fetch))
    values = [entry["value"] for entry in collected]
    assert values == list(range(counter))
    return


# ----------------------------------------------------------------------
# URL composition
# ----------------------------------------------------------------------

@given(
    constraints={"max_examples": 80},segments=st.lists(st.text(alphabet=st.characters(
            min_codepoint=33, max_codepoint=126), min_size=1, max_size=12),
        min_size=1, max_size=5))
def test_compose_leaf_encodes_each_segment(segments) -> None:
    """
        compose_leaf percent-encodes each segment independently so no
        segment can introduce an unencoded path separator.
    """
    leaf = compose_leaf(base="/v1alpha5", segments=segments)
    assert leaf.startswith("/v1alpha5/")

    body = leaf[len("/v1alpha5/"):]
    parts = body.split("/")
    assert len(parts) == len(segments)
    return


@given(segment=st.text(min_size=1, max_size=20), constraints={"max_examples": 40})
def test_encode_segment_is_deterministic(segment) -> None:
    """
        encode_segment is deterministic for identical input.
    """
    assert encode_segment(segment=segment) == encode_segment(segment=segment)
    return


def test_compose_leaf_rejects_empty_segment() -> None:
    """
        compose_leaf rejects an empty or None segment with SemanticError.
    """
    with testbase.raises(SemanticError):
        compose_leaf(base="/v1alpha5", segments=["projects", ""])
    with testbase.raises(SemanticError):
        compose_leaf(base="/v1alpha5", segments=["projects", None])
    return


# ----------------------------------------------------------------------
# CIDR containment
# ----------------------------------------------------------------------

@given(
    constraints={"max_examples": 120},vpc_prefix=st.integers(min_value=8, max_value=20),
       sub_extra=st.integers(min_value=0, max_value=8),
       third_octet=st.integers(min_value=0, max_value=255))
def test_cidr_containment_matches_ipaddress(vpc_prefix, sub_extra,
                                            third_octet) -> None:
    """
        cidr_is_contained agrees with ipaddress.subnet_of for any randomly
        generated VPC/subnet CIDR pair.
    """
    vpc_cidr = "10.0.0.0/{}".format(vpc_prefix)
    sub_prefix = vpc_prefix + sub_extra
    if sub_prefix > 32:
        sub_prefix = 32
    sub_cidr = "10.0.{}.0/{}".format(third_octet, sub_prefix)

    expected = ipaddress.ip_network(sub_cidr, strict=False).subnet_of(
        ipaddress.ip_network(vpc_cidr, strict=False))
    actual = cidr_is_contained(child_cidr=sub_cidr, parent_cidr=vpc_cidr)
    assert actual == expected
    return


def test_cidr_containment_rejects_bad_cidr() -> None:
    """
        cidr_is_contained raises CrusoeCidrValidationError for a bad CIDR.
    """
    with testbase.raises(CrusoeCidrValidationError):
        cidr_is_contained(child_cidr="not-a-cidr", parent_cidr="10.0.0.0/16")
    return


# ----------------------------------------------------------------------
# Task handle termination
# ----------------------------------------------------------------------

class _FakeOperationsGroup:
    """
        In-memory operations group returning a scripted state stream.
    """

    def __init__(self, *, states) -> None:
        """
            :param states: An ordered list of state strings.
        """
        self._states = list(states)
        self._index = 0
        return

    def get(self, *, operation_id, aspects):
        """
            Return the next scripted operation result, holding the last.
        """
        idx = self._index
        if idx >= len(self._states):
            idx = len(self._states) - 1
        else:
            self._index = self._index + 1
        rtnval = CrusoeOperationResult(operation_id=operation_id,
                                       state=self._states[idx])
        return rtnval


_NONTERMINAL = ("pending", "running", "queued", "in_progress")
_TERMINAL = ("succeeded", "failed", "cancelled")


@given(
    constraints={"max_examples": 60},prefix=st.lists(st.sampled_from(_NONTERMINAL),
                       min_size=0, max_size=4),
       terminal=st.sampled_from(_TERMINAL))
def test_task_handle_wait_terminates(prefix, terminal) -> None:
    """
        For any monotonic stream of non-terminal states followed by a
        terminal state, wait returns a terminal TaskResult.
    """
    states = list(prefix) + [terminal]
    group = _FakeOperationsGroup(states=states)
    handle = CrusoeTaskHandle(operation_id="op-1", operations_group=group)

    fast = AspectsCrusoe(completion_interval=0.001, completion_timeout=5.0)
    result = handle.wait(aspects=fast)
    assert result.state == map_operation_state(state=terminal)
    assert handle.is_done() is True
    return


def test_task_handle_wait_times_out() -> None:
    """
        A stream that never reaches a terminal state raises TimeoutError when
        the completion budget elapses.
    """
    group = _FakeOperationsGroup(states=["running"])
    handle = CrusoeTaskHandle(operation_id="op-2", operations_group=group)

    tiny = AspectsCrusoe(completion_interval=0.001, completion_timeout=0.02)
    with testbase.raises(TimeoutError):
        handle.wait(aspects=tiny)
    return


# ----------------------------------------------------------------------
# Idempotent retry equivalence
# ----------------------------------------------------------------------

@given(repeats=st.integers(min_value=1, max_value=4), constraints={"max_examples": 40})
def test_paging_repeated_traversal_is_equivalent(repeats) -> None:
    """
        Re-running a paged traversal over the same page set yields the same
        items every time (idempotent read).
    """
    pages = [
        {"items": [{"v": 0}, {"v": 1}], "next_page_token": "c1"},
        {"items": [{"v": 2}]},
    ]

    def _fetch(cursor):
        if cursor is None:
            rtnval = pages[0]
            return rtnval
        rtnval = pages[1]
        return rtnval

    first = None
    for _ in range(repeats):
        collected = [entry["v"] for entry in iter_paged_items(fetch_page=_fetch)]
        if first is None:
            first = collected
        assert collected == first
    return
