"""
    .. module:: vpcsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`VpcsGroup` api group
                   exposing the Crusoe Cloud VPC endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Dict, List, Optional

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.interop.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from automojo.interop.crusoe.apigroups.groupsupport import (
    compose_leaf, iter_paged_items, raise_for_status, safe_json
)
from automojo.interop.crusoe.model.crusoevpc import CrusoeVpc
from automojo.interop.crusoe.specs.crusoevpcspec import CrusoeVpcSpec


class VpcsGroup(RestApiGroup):
    """
        :class:`VpcsGroup` exposes the Crusoe Cloud VPC endpoints — idempotent
        create, transparent cursor-paged list, and no-op delete.
    """

    def create(self, *, spec: CrusoeVpcSpec,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoeVpc:
        """
            Create a VPC, returning the existing record when a VPC with the
            same name already exists in the project.

            :param spec: The :class:`CrusoeVpcSpec` describing the VPC.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeVpc` record.
        """
        if spec is None:
            raise SemanticError("'spec' must be a CrusoeVpcSpec.")

        existing = self._find_by_name(project_id=spec.project_id,
                                      name=spec.name, aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", spec.project_id, "vpcs"])
        response = client.request(method="POST", leaf=leaf,
                                  json_body=spec.to_payload(), aspects=aspects)
        raise_for_status(response=response, action="create vpc")

        rtnval = CrusoeVpc.from_dict(safe_json(response=response))
        return rtnval

    def list(self, *, project_id: str,
             aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> List[CrusoeVpc]:
        """
            List every VPC in a project, following paging cursors.

            :param project_id: The owning project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CrusoeVpc` records.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "vpcs"])

        def _fetch(cursor: Optional[str]) -> Dict:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list vpcs")
            page = safe_json(response=response)
            return page

        rtnval: List[CrusoeVpc] = []
        for entry in iter_paged_items(fetch_page=_fetch, items_field="items"):
            rtnval.append(CrusoeVpc.from_dict(entry))
        return rtnval

    def delete(self, *, project_id: str, vpc_id: str,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> None:
        """
            Delete a VPC.  An unknown id is treated as already removed.

            :param project_id: The owning project identifier.
            :param vpc_id: The VPC identifier to delete.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        if vpc_id is None or len(vpc_id) == 0:
            raise SemanticError("'vpc_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "vpcs", vpc_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete vpc")
        return

    def _find_by_name(self, *, project_id: str, name: str,
                      aspects: AspectsCrusoe) -> Optional[CrusoeVpc]:
        """
            Find a VPC by name within a project.

            :param project_id: The owning project identifier.
            :param name: The VPC name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`CrusoeVpc`, or ``None``.
        """
        records = self.list(project_id=project_id, aspects=aspects)
        rtnval: Optional[CrusoeVpc] = None
        for record in records:
            if record.name == name:
                rtnval = record
                break
        return rtnval
