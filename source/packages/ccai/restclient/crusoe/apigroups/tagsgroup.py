"""
    .. module:: tagsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`TagsGroup` api group
                   exposing the Crusoe Cloud resource tagging endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List

from ccai.errors.exceptions import SemanticError

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from ccai.restclient.crusoe.apigroups.groupsupport import (
    compose_leaf, raise_for_status
)


# Crusoe Cloud resource-type path segments keyed by the neutral kind name.
_RESOURCE_TYPE_PATHS = {
    "vpc": "vpcs",
    "subnet": "subnets",
    "security-group": "security-groups",
    "ssh-key": "ssh-keys",
    "disk": "disks",
    "placement-group": "ib-partitions",
    "vm": "instances",
    "instance": "instances",
}


def tags_to_labels(*, tags: List[Dict[str, str]]) -> Dict[str, str]:
    """
        Translate a neutral list-of-single-entry-dict tag set into the Crusoe
        labels-dict payload shape.

        :param tags: A list of single-entry tag dicts.

        :returns: A flattened label key/value dictionary.
    """
    rtnval: Dict[str, str] = {}
    for entry in tags:
        for key, value in entry.items():
            rtnval[key] = value
    return rtnval


class TagsGroup(RestApiGroup):
    """
        :class:`TagsGroup` exposes the Crusoe Cloud resource tagging endpoint.
        Neutral list-of-dict tags are translated into Crusoe's labels-dict
        payload shape internally.
    """

    def apply(self, *, project_id: str, resource_type: str, resource_id: str,
              tags: List[Dict[str, str]],
              aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> None:
        """
            Apply a key/value tag set to a resource by PATCH-ing its labels.

            :param project_id: The owning project identifier.
            :param resource_type: The neutral resource type key.
            :param resource_id: The venue-side resource identifier.
            :param tags: A list of single-entry tag dicts.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when the resource type is unknown.
        """
        if resource_id is None or len(resource_id) == 0:
            raise SemanticError("'resource_id' must be a non-empty string.")
        if tags is None:
            raise SemanticError("'tags' must be a list of tag dicts.")

        type_path = _RESOURCE_TYPE_PATHS.get(resource_type, None)
        if type_path is None:
            raise SemanticError(
                "Unknown resource_type {!r} for tagging.".format(resource_type)
            )

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, type_path,
                                      resource_id])
        body: Dict[str, Any] = {"labels": tags_to_labels(tags=tags)}
        response = client.request(method="PATCH", leaf=leaf,
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="apply tags")
        return
