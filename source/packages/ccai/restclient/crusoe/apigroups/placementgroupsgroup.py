"""
    .. module:: placementgroupsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`PlacementGroupsGroup` api
                   group exposing the Crusoe Cloud IB placement group
                   endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Dict, List, Optional

from ccai.errors.exceptions import SemanticError

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from ccai.restclient.crusoe.apigroups.groupsupport import (
    compose_leaf, iter_paged_items, raise_for_status, safe_json
)
from ccai.restclient.crusoe.model.crusoeplacementgroup import (
    CrusoePlacementGroup
)
from ccai.restclient.crusoe.specs.crusoeplacementgroupspec import (
    CrusoePlacementGroupSpec
)


class PlacementGroupsGroup(RestApiGroup):
    """
        :class:`PlacementGroupsGroup` exposes the Crusoe Cloud placement
        group (IB partition) endpoints — idempotent create, list, and no-op
        delete.
    """

    def create(self, *, spec: CrusoePlacementGroupSpec,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoePlacementGroup:
        """
            Create an IB-enabled placement group, returning the existing
            record when one with the same name already exists.

            :param spec: The :class:`CrusoePlacementGroupSpec`.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoePlacementGroup` record.
        """
        if spec is None:
            raise SemanticError("'spec' must be a CrusoePlacementGroupSpec.")

        existing = self._find_by_name(project_id=spec.project_id,
                                      name=spec.name, aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", spec.project_id,
                                      "ib-partitions"])
        response = client.request(method="POST", leaf=leaf,
                                  json_body=spec.to_payload(), aspects=aspects)
        raise_for_status(response=response, action="create placement group")

        rtnval = CrusoePlacementGroup.from_dict(safe_json(response=response))
        return rtnval

    def list(self, *, project_id: str,
             aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> List[CrusoePlacementGroup]:
        """
            List every placement group in a project, following paging
            cursors.

            :param project_id: The owning project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CrusoePlacementGroup` records.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id,
                                      "ib-partitions"])

        def _fetch(cursor: Optional[str]) -> Dict:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response,
                             action="list placement groups")
            page = safe_json(response=response)
            return page

        rtnval: List[CrusoePlacementGroup] = []
        for entry in iter_paged_items(fetch_page=_fetch, items_field="items"):
            rtnval.append(CrusoePlacementGroup.from_dict(entry))
        return rtnval

    def delete(self, *, project_id: str, placement_group_id: str,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> None:
        """
            Delete a placement group.  Unknown ids are treated as removed.

            :param project_id: The owning project identifier.
            :param placement_group_id: The placement group identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        if placement_group_id is None or len(placement_group_id) == 0:
            raise SemanticError(
                "'placement_group_id' must be a non-empty string."
            )

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id,
                                      "ib-partitions", placement_group_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete placement group")
        return

    def _find_by_name(self, *, project_id: str, name: str,
                      aspects: AspectsCrusoe) -> Optional[CrusoePlacementGroup]:
        """
            Find a placement group by name within a project.

            :param project_id: The owning project identifier.
            :param name: The placement group name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching record, or ``None``.
        """
        records = self.list(project_id=project_id, aspects=aspects)
        rtnval: Optional[CrusoePlacementGroup] = None
        for record in records:
            if record.name == name:
                rtnval = record
                break
        return rtnval
