"""
    .. module:: imagesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`ImagesGroup` api group
                   exposing the Crusoe Cloud machine image endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Dict, List, Optional

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.restclient.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from automojo.restclient.crusoe.apigroups.groupsupport import (
    compose_leaf, iter_paged_items, raise_for_status, safe_json
)
from automojo.restclient.crusoe.model.crusoeimage import CrusoeImage


class ImagesGroup(RestApiGroup):
    """
        :class:`ImagesGroup` exposes the Crusoe Cloud machine image lookup
        endpoint, with transparent cursor-paged traversal.
    """

    def list(self, *, project_id: str,
             aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> List[CrusoeImage]:
        """
            List every available machine image, following paging cursors.

            :param project_id: The owning project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CrusoeImage` records.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "images"])

        def _fetch(cursor: Optional[str]) -> Dict:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list images")
            page = safe_json(response=response)
            return page

        rtnval: List[CrusoeImage] = []
        for entry in iter_paged_items(fetch_page=_fetch, items_field="items"):
            rtnval.append(CrusoeImage.from_dict(entry))
        return rtnval
