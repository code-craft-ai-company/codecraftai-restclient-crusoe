"""
    .. module:: factories
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Test resource factories for the Crusoe client tests.

    Replaces conftest.py. testbase does not read pytest conftest files, so the
    fixtures there were invisible to the runner and every test that asked for
    one errored with a NameError from inside the generated sequence.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from collections.abc import Generator

from ccai import testbase

from ccai.credentials.crusoeapikeycredential import CrusoeApiKeyCredential

from ccai.restclient.crusoe.crusoeclient import CrusoeClient


@testbase.register.resource_factory()
def create_crusoe_credential(
        constraints=None) -> Generator[CrusoeApiKeyCredential, None, None]:
    """
        Yield a usable :class:`CrusoeApiKeyCredential` for tests.

        :param constraints: Optional constraint dictionary.

        :returns: A generator yielding a populated credential instance.
    """
    rtnval = CrusoeApiKeyCredential(identifier="crusoe-test",
                                    categories=["cloud-venue"],
                                    access_key_id="AKID-TEST",
                                    secret="SECRET-TEST")
    yield rtnval


@testbase.register.resource_factory()
def create_crusoe_client(
        crusoe_credential: CrusoeApiKeyCredential,
        constraints=None) -> Generator[CrusoeClient, None, None]:
    """
        Yield a :class:`CrusoeClient` bound to the test credential.

        :param crusoe_credential: The credential resource.
        :param constraints: Optional constraint dictionary.

        :returns: A generator yielding a :class:`CrusoeClient` instance.
    """
    rtnval = CrusoeClient(credential=crusoe_credential)
    yield rtnval
