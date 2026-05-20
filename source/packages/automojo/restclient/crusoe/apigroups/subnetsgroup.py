"""
    .. module:: subnetsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`SubnetsGroup` api group
                   exposing the Crusoe Cloud subnet endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import ipaddress
import os

from typing import Dict, List, Optional

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.restclient.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from automojo.restclient.crusoe.apigroups.groupsupport import (
    compose_leaf, iter_paged_items, raise_for_status, safe_json
)
from automojo.restclient.crusoe.exceptions.crusoeexceptions import (
    CrusoeCidrValidationError
)
from automojo.restclient.crusoe.model.crusoesubnet import CrusoeSubnet
from automojo.restclient.crusoe.specs.crusoesubnetspec import CrusoeSubnetSpec


def cidr_is_contained(*, child_cidr: str, parent_cidr: str) -> bool:
    """
        Test whether ``child_cidr`` is fully contained within ``parent_cidr``.

        :param child_cidr: The candidate subnet CIDR.
        :param parent_cidr: The enclosing VPC CIDR.

        :returns: ``True`` when contained, otherwise ``False``.

        :raises: :class:`CrusoeCidrValidationError` when either CIDR cannot
            be parsed.
    """
    try:
        parent = ipaddress.ip_network(parent_cidr, strict=False)
        child = ipaddress.ip_network(child_cidr, strict=False)
    except (TypeError, ValueError) as xcpt:
        err_msg_lines = ["Failed to parse a CIDR for subnet containment."]
        err_msg_lines.append("CHILD: {!r}".format(child_cidr))
        err_msg_lines.append("PARENT: {!r}".format(parent_cidr))
        err_msg_lines.append("CAUSE: {}".format(xcpt))
        err_msg = os.linesep.join(err_msg_lines)
        raise CrusoeCidrValidationError(err_msg) from None

    if parent.version != child.version:
        rtnval = False
        return rtnval

    rtnval = child.subnet_of(parent)
    return rtnval


class SubnetsGroup(RestApiGroup):
    """
        :class:`SubnetsGroup` exposes the Crusoe Cloud subnet endpoints —
        idempotent create with CIDR-containment validation, transparent
        cursor-paged list, and no-op delete.
    """

    def create(self, *, spec: CrusoeSubnetSpec,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoeSubnet:
        """
            Create a subnet after validating CIDR containment in the VPC.

            :param spec: The :class:`CrusoeSubnetSpec` describing the subnet.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeSubnet` record.

            :raises: :class:`CrusoeCidrValidationError` when the subnet CIDR
                is not contained within the VPC CIDR.
        """
        if spec is None:
            raise SemanticError("'spec' must be a CrusoeSubnetSpec.")

        contained = cidr_is_contained(child_cidr=spec.cidr,
                                      parent_cidr=spec.vpc_cidr)
        if contained is False:
            err_msg_lines = ["Subnet CIDR is not contained within the VPC."]
            err_msg_lines.append("SUBNET_CIDR: {}".format(spec.cidr))
            err_msg_lines.append("VPC_CIDR: {}".format(spec.vpc_cidr))
            err_msg = os.linesep.join(err_msg_lines)
            raise CrusoeCidrValidationError(err_msg)

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["vpcs", spec.vpc_id, "subnets"])
        response = client.request(method="POST", leaf=leaf,
                                  json_body=spec.to_payload(), aspects=aspects)
        raise_for_status(response=response, action="create subnet")

        rtnval = CrusoeSubnet.from_dict(safe_json(response=response))
        return rtnval

    def list(self, *, vpc_id: str,
             aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> List[CrusoeSubnet]:
        """
            List every subnet in a VPC, following paging cursors.

            :param vpc_id: The parent VPC identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CrusoeSubnet` records.
        """
        if vpc_id is None or len(vpc_id) == 0:
            raise SemanticError("'vpc_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["vpcs", vpc_id, "subnets"])

        def _fetch(cursor: Optional[str]) -> Dict:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list subnets")
            page = safe_json(response=response)
            return page

        rtnval: List[CrusoeSubnet] = []
        for entry in iter_paged_items(fetch_page=_fetch, items_field="items"):
            rtnval.append(CrusoeSubnet.from_dict(entry))
        return rtnval

    def delete(self, *, vpc_id: str, subnet_id: str,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> None:
        """
            Delete a subnet.  An unknown id is treated as already removed.

            :param vpc_id: The parent VPC identifier.
            :param subnet_id: The subnet identifier to delete.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        if subnet_id is None or len(subnet_id) == 0:
            raise SemanticError("'subnet_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["vpcs", vpc_id, "subnets", subnet_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete subnet")
        return
