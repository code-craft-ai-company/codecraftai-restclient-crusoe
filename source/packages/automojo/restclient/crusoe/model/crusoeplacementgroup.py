"""
    .. module:: crusoeplacementgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoePlacementGroup` typed
                   model record for a Crusoe Cloud IB-enabled placement group.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoePlacementGroup:
    """
        Typed record describing a Crusoe Cloud placement group.

        Crusoe realises co-located multi-node training fabrics through
        InfiniBand partitions; a placement group with
        ``interconnect="infiniband"`` maps to an IB partition.  Hand-authored
        from the documented Crusoe Cloud API per the §9.2a codegen decision
        recorded in ``AGENTS.md``.
    """

    def __init__(self, *, placement_group_id: str, name: str,
                 interconnect: str, project_id: Optional[str] = None,
                 state: Optional[str] = None,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoePlacementGroup` record.

            :param placement_group_id: The Crusoe-assigned identifier.
            :param name: The placement group name.
            :param interconnect: The interconnect fabric (e.g. ``infiniband``).
            :param project_id: Optional owning project identifier.
            :param state: Optional lifecycle state string.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.placement_group_id = placement_group_id
        self.name = name
        self.interconnect = interconnect
        self.project_id = project_id
        self.state = state
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrusoePlacementGroup":
        """
            Build a :class:`CrusoePlacementGroup` from a Crusoe API payload.

            :param data: The decoded API payload.

            :returns: A populated :class:`CrusoePlacementGroup`.
        """
        placement_group_id = data.get("id", data.get("ib_partition_id",
                                      data.get("placement_group_id", "")))
        name = data.get("name", "")
        interconnect = data.get("interconnect", "infiniband")
        project_id = data.get("project_id", None)
        state = data.get("state", None)
        labels = data.get("labels", None)

        rtnval = cls(placement_group_id=placement_group_id, name=name,
                     interconnect=interconnect, project_id=project_id,
                     state=state, labels=labels)
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`CrusoePlacementGroup` to a canonical
            API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this placement group.
        """
        rtnval: Dict[str, Any] = {
            "id": self.placement_group_id,
            "name": self.name,
            "interconnect": self.interconnect,
            "project_id": self.project_id,
            "state": self.state,
            "labels": self.labels,
        }
        return rtnval
