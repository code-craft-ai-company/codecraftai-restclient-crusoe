"""
    .. module:: crusoeclient
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeClient` REST client
                   for the Crusoe Cloud API (``api.crusoecloud.com``).

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import base64
import hashlib
import hmac
import json
import os
import time

from typing import Any, Dict, Optional, Union

from requests import Response, Session

from ccai.errors.exceptions import ConfigurationError

from ccai.credentials.crusoeapikeycredential import CrusoeApiKeyCredential

from ccai.restclient.base.restclientbase import RestClientBase

from ccai.restclient.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from ccai.restclient.crusoe.apigroups.disksgroup import DisksGroup
from ccai.restclient.crusoe.apigroups.imagesgroup import ImagesGroup
from ccai.restclient.crusoe.apigroups.operationsgroup import OperationsGroup
from ccai.restclient.crusoe.apigroups.placementgroupsgroup import (
    PlacementGroupsGroup
)
from ccai.restclient.crusoe.apigroups.securitygroupsgroup import (
    SecurityGroupsGroup
)
from ccai.restclient.crusoe.apigroups.sshkeysgroup import SshKeysGroup
from ccai.restclient.crusoe.apigroups.subnetsgroup import SubnetsGroup
from ccai.restclient.crusoe.apigroups.tagsgroup import TagsGroup
from ccai.restclient.crusoe.apigroups.vmsgroup import VmsGroup
from ccai.restclient.crusoe.apigroups.vpcsgroup import VpcsGroup


CRUSOE_API_HOST = "api.crusoecloud.com"

CRUSOE_API_BASE_LEAF = "/v1alpha5"


class CrusoeClient(RestClientBase):
    """
        :class:`CrusoeClient` is the typed, aspect-driven REST client for the
        Crusoe Cloud API.  It is built on :class:`RestClientBase` and exposes
        the Crusoe surface — VPCs, subnets, security groups, SSH keys, disks,
        IB placement groups, virtual machines, images, tagging, and async
        operations — through per-domain api groups.

        Authentication uses a :class:`CrusoeApiKeyCredential` (access key id +
        secret).  Every outbound request is HMAC-signed: the access key id,
        an RFC-3339 timestamp, and an HMAC-SHA256 signature over the canonical
        request string are carried on request headers.  All HTTP behaviour is
        carried by :class:`AspectsCrusoe`; no behaviour-modifying decorators
        are used.
    """

    def __init__(self, *, credential: CrusoeApiKeyCredential,
                 host: str = CRUSOE_API_HOST,
                 base_leaf: str = CRUSOE_API_BASE_LEAF,
                 aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> None:
        """
            Initialize the Crusoe Cloud REST client.

            :param credential: A :class:`CrusoeApiKeyCredential` carrying the
                access key id and secret.
            :param host: Override host name for the REST endpoint.
            :param base_leaf: API base path prefix (e.g. ``/v1alpha5``).
            :param aspects: Default :class:`AspectsCrusoe` applied when a call
                omits an explicit aspects argument.

            :returns: ``None``.

            :raises: :class:`ConfigurationError` when ``credential`` is not a
                :class:`CrusoeApiKeyCredential` or is missing material.
        """
        if not isinstance(credential, CrusoeApiKeyCredential):
            err_msg_lines = ["CrusoeClient requires a CrusoeApiKeyCredential."]
            err_msg_lines.append("EXPECTED: CrusoeApiKeyCredential")
            err_msg_lines.append("FOUND: {}".format(type(credential).__name__))
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        access_key_id = credential.access_key_id
        secret = credential.secret
        if access_key_id is None or len(access_key_id) == 0:
            raise ConfigurationError(
                "CrusoeClient credential is missing the access key id."
            )
        if secret is None or len(secret) == 0:
            raise ConfigurationError(
                "CrusoeClient credential is missing the secret."
            )

        super().__init__(host=host, credential=credential, aspects=aspects)

        self._base_leaf = base_leaf
        self._access_key_id = access_key_id
        self._secret = secret

        self._vpcs = VpcsGroup(self)
        self._subnets = SubnetsGroup(self)
        self._security_groups = SecurityGroupsGroup(self)
        self._ssh_keys = SshKeysGroup(self)
        self._disks = DisksGroup(self)
        self._placement_groups = PlacementGroupsGroup(self)
        self._vms = VmsGroup(self)
        self._images = ImagesGroup(self)
        self._tags = TagsGroup(self)
        self._operations = OperationsGroup(self)
        return

    @property
    def base_leaf(self) -> str:
        """
            The API base path prefix for this client.

            :returns: The base leaf string.
        """
        rtnval = self._base_leaf
        return rtnval

    @property
    def vpcs(self) -> VpcsGroup:
        """
            The VPCs api group.

            :returns: The :class:`VpcsGroup` instance.
        """
        rtnval = self._vpcs
        return rtnval

    @property
    def subnets(self) -> SubnetsGroup:
        """
            The subnets api group.

            :returns: The :class:`SubnetsGroup` instance.
        """
        rtnval = self._subnets
        return rtnval

    @property
    def security_groups(self) -> SecurityGroupsGroup:
        """
            The security groups api group.

            :returns: The :class:`SecurityGroupsGroup` instance.
        """
        rtnval = self._security_groups
        return rtnval

    @property
    def ssh_keys(self) -> SshKeysGroup:
        """
            The SSH keys api group.

            :returns: The :class:`SshKeysGroup` instance.
        """
        rtnval = self._ssh_keys
        return rtnval

    @property
    def disks(self) -> DisksGroup:
        """
            The disks api group.

            :returns: The :class:`DisksGroup` instance.
        """
        rtnval = self._disks
        return rtnval

    @property
    def placement_groups(self) -> PlacementGroupsGroup:
        """
            The placement groups api group.

            :returns: The :class:`PlacementGroupsGroup` instance.
        """
        rtnval = self._placement_groups
        return rtnval

    @property
    def vms(self) -> VmsGroup:
        """
            The virtual machines api group.

            :returns: The :class:`VmsGroup` instance.
        """
        rtnval = self._vms
        return rtnval

    @property
    def images(self) -> ImagesGroup:
        """
            The images api group.

            :returns: The :class:`ImagesGroup` instance.
        """
        rtnval = self._images
        return rtnval

    @property
    def tags(self) -> TagsGroup:
        """
            The tags api group.

            :returns: The :class:`TagsGroup` instance.
        """
        rtnval = self._tags
        return rtnval

    @property
    def operations(self) -> OperationsGroup:
        """
            The operations api group.

            :returns: The :class:`OperationsGroup` instance.
        """
        rtnval = self._operations
        return rtnval

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def request(self, *, method: str, leaf: str,
                params: Optional[Dict[str, str]] = None,
                json_body: Optional[Union[Dict[str, Any], list]] = None,
                headers: Optional[Dict[str, str]] = None,
                aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> Response:
        """
            Issue a single HMAC-signed REST call against the Crusoe API.

            :param method: HTTP method to invoke.
            :param leaf: API leaf path beginning with ``/``.
            :param params: Optional query-string parameters.
            :param json_body: Optional dict/list serialized as the body.
            :param headers: Optional additional request headers.
            :param aspects: Behaviour-control aspects for the call.

            :returns: The :class:`Response` object from the call.
        """
        call_url = self._format_call_url(leaf)
        send_timeouts = (aspects.connection_timeout, aspects.inactivity_timeout)

        body_bytes: Optional[bytes] = None
        if json_body is not None:
            body_bytes = json.dumps(json_body).encode("utf-8")

        signed_headers = self.sign_request(method=method, leaf=leaf,
                                           body_bytes=body_bytes)
        send_headers: Dict[str, str] = {"Accept": "application/json"}
        if body_bytes is not None:
            send_headers["Content-Type"] = "application/json"
        send_headers.update(signed_headers)
        if headers is not None:
            send_headers.update(headers)

        session = self._signed_session(aspects=aspects)
        response: Response = session.request(method=method, url=call_url,
                                             params=params, data=body_bytes,
                                             headers=send_headers,
                                             timeout=send_timeouts,
                                             verify=self._verify_certificate)
        rtnval = response
        return rtnval

    def sign_request(self, *, method: str, leaf: str,
                     body_bytes: Optional[bytes]) -> Dict[str, str]:
        """
            Compute the HMAC-SHA256 signature headers for a Crusoe request.

            The canonical request string joins the HTTP method, the request
            leaf path, an RFC-3339 timestamp, and the SHA256 hex digest of
            the request body.  The signature is the base64-encoded HMAC of
            that string keyed by the credential secret.

            :param method: HTTP method.
            :param leaf: API leaf path beginning with ``/``.
            :param body_bytes: The raw request body, or ``None``.

            :returns: A dictionary of signature headers.
        """
        timestamp = self._timestamp()

        effective_body = body_bytes
        if effective_body is None:
            effective_body = b""

        body_digest = hashlib.sha256(effective_body).hexdigest()

        canonical_lines = [method.upper(), leaf, timestamp, body_digest]
        canonical = "\n".join(canonical_lines)

        signature_bytes = hmac.new(
            self._secret.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature_bytes).decode("utf-8")

        rtnval: Dict[str, str] = {
            "X-Crusoe-Access-Key": self._access_key_id,
            "X-Crusoe-Timestamp": timestamp,
            "X-Crusoe-Signature": signature,
            "Authorization": "Bearer {0}:{1}".format(self._access_key_id,
                                                     signature),
        }
        return rtnval

    def _signed_session(self, *, aspects: AspectsCrusoe) -> Session:
        """
            Return a :class:`Session` to issue the request through.

            :param aspects: Behaviour-control aspects, which may supply a
                pre-created session for tests.

            :returns: A :class:`Session` instance.
        """
        if aspects.session is not None:
            rtnval = aspects.session
            return rtnval

        if self._session is None:
            session = Session()
            session.verify = self._verify_certificate
            self._session = session

        rtnval = self._session
        return rtnval

    def _timestamp(self) -> str:
        """
            Produce an RFC-3339 UTC timestamp for request signing.

            :returns: The timestamp string.
        """
        rtnval = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return rtnval
