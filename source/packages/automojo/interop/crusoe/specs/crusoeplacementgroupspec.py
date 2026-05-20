"""
    .. module:: crusoeplacementgroupspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoePlacementGroupSpec`
                   request object for creating a Crusoe placement group.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoePlacementGroupSpec:
    """
        Request object describing a Crusoe Cloud placement group to create.

        A placement group with ``interconnect="infiniband"`` maps to a Crusoe
        IB partition used to co-locate multi-node training instances.
    """

    def __init__(self, *, name: str, project_id: str,
                 interconnect: str = "infiniband",
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoePlacementGroupSpec`.

            :param name: The desired placement group name.
            :param project_id: The owning project identifier.
            :param interconnect: The interconnect fabric (e.g. ``infiniband``).
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.name = name
        self.project_id = project_id
        self.interconnect = interconnect
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    def to_payload(self) -> Dict[str, Any]:
        """
            Translate this spec into a Crusoe API request payload.

            :returns: The request payload dictionary.
        """
        rtnval: Dict[str, Any] = {
            "name": self.name,
            "interconnect": self.interconnect,
        }
        if len(self.labels) > 0:
            rtnval["labels"] = dict(self.labels)
        return rtnval
