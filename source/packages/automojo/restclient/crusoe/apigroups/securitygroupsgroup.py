"""
    .. module:: securitygroupsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`SecurityGroupsGroup` api
                   group exposing the Crusoe Cloud security group endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.restclient.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from automojo.restclient.crusoe.apigroups.groupsupport import (
    compose_leaf, iter_paged_items, raise_for_status, safe_json
)
from automojo.restclient.crusoe.model.crusoesecuritygroup import (
    CrusoeSecurityGroup
)
from automojo.restclient.crusoe.specs.crusoesecuritygroupspec import (
    CrusoeSecurityGroupSpec
)


class SecurityGroupsGroup(RestApiGroup):
    """
        :class:`SecurityGroupsGroup` exposes the Crusoe Cloud security group
        endpoints — idempotent create, list, rule replacement, and no-op
        delete.
    """

    def create(self, *, spec: CrusoeSecurityGroupSpec,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoeSecurityGroup:
        """
            Create a security group, returning the existing record when one
            with the same name already exists in the VPC.

            :param spec: The :class:`CrusoeSecurityGroupSpec`.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeSecurityGroup` record.
        """
        if spec is None:
            raise SemanticError("'spec' must be a CrusoeSecurityGroupSpec.")

        existing = self._find_by_name(vpc_id=spec.vpc_id, name=spec.name,
                                      aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["vpcs", spec.vpc_id, "security-groups"])
        response = client.request(method="POST", leaf=leaf,
                                  json_body=spec.to_payload(), aspects=aspects)
        raise_for_status(response=response, action="create security group")

        rtnval = CrusoeSecurityGroup.from_dict(safe_json(response=response))
        return rtnval

    def list(self, *, vpc_id: str,
             aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> List[CrusoeSecurityGroup]:
        """
            List every security group in a VPC, following paging cursors.

            :param vpc_id: The parent VPC identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CrusoeSecurityGroup` records.
        """
        if vpc_id is None or len(vpc_id) == 0:
            raise SemanticError("'vpc_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["vpcs", vpc_id, "security-groups"])

        def _fetch(cursor: Optional[str]) -> Dict:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list security groups")
            page = safe_json(response=response)
            return page

        rtnval: List[CrusoeSecurityGroup] = []
        for entry in iter_paged_items(fetch_page=_fetch, items_field="items"):
            rtnval.append(CrusoeSecurityGroup.from_dict(entry))
        return rtnval

    def set_rules(self, *, vpc_id: str, security_group_id: str,
                  ingress_rules: List[Dict[str, Any]],
                  egress_rules: List[Dict[str, Any]],
                  aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoeSecurityGroup:
        """
            Replace the rule set on a security group with the supplied lists.

            :param vpc_id: The parent VPC identifier.
            :param security_group_id: The security group identifier.
            :param ingress_rules: The complete replacement ingress rule list.
            :param egress_rules: The complete replacement egress rule list.
            :param aspects: Behaviour control for the call.

            :returns: The updated :class:`CrusoeSecurityGroup` record.
        """
        if security_group_id is None or len(security_group_id) == 0:
            raise SemanticError(
                "'security_group_id' must be a non-empty string."
            )
        if ingress_rules is None:
            raise SemanticError("'ingress_rules' must be a list.")
        if egress_rules is None:
            raise SemanticError("'egress_rules' must be a list.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["vpcs", vpc_id, "security-groups",
                                      security_group_id])
        body: Dict[str, Any] = {
            "ingress_rules": list(ingress_rules),
            "egress_rules": list(egress_rules),
        }
        response = client.request(method="PATCH", leaf=leaf,
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response,
                         action="set security group rules")

        rtnval = CrusoeSecurityGroup.from_dict(safe_json(response=response))
        return rtnval

    def delete(self, *, vpc_id: str, security_group_id: str,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> None:
        """
            Delete a security group.  Unknown ids are treated as removed.

            :param vpc_id: The parent VPC identifier.
            :param security_group_id: The security group identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        if security_group_id is None or len(security_group_id) == 0:
            raise SemanticError(
                "'security_group_id' must be a non-empty string."
            )

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["vpcs", vpc_id, "security-groups",
                                      security_group_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete security group")
        return

    def _find_by_name(self, *, vpc_id: str, name: str,
                      aspects: AspectsCrusoe) -> Optional[CrusoeSecurityGroup]:
        """
            Find a security group by name within a VPC.

            :param vpc_id: The parent VPC identifier.
            :param name: The security group name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching record, or ``None``.
        """
        records = self.list(vpc_id=vpc_id, aspects=aspects)
        rtnval: Optional[CrusoeSecurityGroup] = None
        for record in records:
            if record.name == name:
                rtnval = record
                break
        return rtnval
