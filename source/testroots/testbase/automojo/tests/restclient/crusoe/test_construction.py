"""
    .. module:: test_construction
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Construction and authentication tests for
                   :class:`CrusoeClient`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import pytest

from automojo.errors.exceptions import ConfigurationError

from automojo.credentials.basiccredential import BasicCredential

from automojo.restclient.crusoe.crusoeclient import CrusoeClient
from automojo.restclient.crusoe.apigroups.vpcsgroup import VpcsGroup
from automojo.restclient.crusoe.apigroups.vmsgroup import VmsGroup


def test_client_construction(crusoe_client: CrusoeClient) -> None:
    """
        The client exposes every api group after construction.
    """
    assert isinstance(crusoe_client.vpcs, VpcsGroup)
    assert isinstance(crusoe_client.vms, VmsGroup)
    assert crusoe_client.base_leaf == "/v1alpha5"
    return


def test_client_rejects_wrong_credential() -> None:
    """
        Constructing the client with a non-Crusoe credential raises
        ConfigurationError.
    """
    bad = BasicCredential(identifier="bad", categories=["basic"],
                          username="u", password="p")
    with pytest.raises(ConfigurationError):
        CrusoeClient(credential=bad)
    return


def test_sign_request_emits_headers(crusoe_client: CrusoeClient) -> None:
    """
        sign_request produces the access-key, timestamp, and signature
        headers.
    """
    headers = crusoe_client.sign_request(method="GET",
                                         leaf="/v1alpha5/projects/p/vpcs",
                                         body_bytes=None)
    assert headers["X-Crusoe-Access-Key"] == "AKID-TEST"
    assert len(headers["X-Crusoe-Signature"]) > 0
    assert "X-Crusoe-Timestamp" in headers
    return


def test_sign_request_is_body_sensitive(crusoe_client: CrusoeClient) -> None:
    """
        A different body produces a different signature.
    """
    sig_a = crusoe_client.sign_request(method="POST", leaf="/x",
                                       body_bytes=b"{}")
    sig_b = crusoe_client.sign_request(method="POST", leaf="/x",
                                       body_bytes=b'{"a":1}')
    assert sig_a["X-Crusoe-Signature"] != sig_b["X-Crusoe-Signature"]
    return
