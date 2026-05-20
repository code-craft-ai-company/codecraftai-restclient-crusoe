"""
    .. module:: conftest
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Shared pytest fixtures for the Crusoe interop client tests.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import pytest

from automojo.credentials.crusoeapikeycredential import CrusoeApiKeyCredential

from automojo.interop.crusoe.crusoeclient import CrusoeClient


@pytest.fixture
def crusoe_credential() -> CrusoeApiKeyCredential:
    """
        Return a usable :class:`CrusoeApiKeyCredential` for tests.

        :returns: A populated credential instance.
    """
    rtnval = CrusoeApiKeyCredential(identifier="crusoe-test",
                                    categories=["cloud-venue"],
                                    access_key_id="AKID-TEST",
                                    secret="SECRET-TEST")
    return rtnval


@pytest.fixture
def crusoe_client(crusoe_credential: CrusoeApiKeyCredential) -> CrusoeClient:
    """
        Return a :class:`CrusoeClient` bound to the test credential.

        :param crusoe_credential: The credential fixture.

        :returns: A :class:`CrusoeClient` instance.
    """
    rtnval = CrusoeClient(credential=crusoe_credential)
    return rtnval
