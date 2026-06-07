"""
    .. module:: crusoevm
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeVm` typed model
                   record for a Crusoe Cloud virtual machine.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class CrusoeVm:
    """
        Typed record describing a Crusoe Cloud virtual machine.

        Hand-authored from the documented Crusoe Cloud API per the §9.2a
        codegen decision recorded in ``AGENTS.md``.
    """

    def __init__(self, *, vm_id: str, name: str, instance_type: str,
                 location: Optional[str] = None, state: Optional[str] = None,
                 project_id: Optional[str] = None,
                 subnet_id: Optional[str] = None,
                 placement_group_id: Optional[str] = None,
                 network_interfaces: Optional[List[Dict[str, Any]]] = None,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeVm` record.

            :param vm_id: The Crusoe-assigned VM identifier.
            :param name: The VM name.
            :param instance_type: The Crusoe instance type / SKU.
            :param location: Optional Crusoe location string.
            :param state: Optional lifecycle state string.
            :param project_id: Optional owning project identifier.
            :param subnet_id: Optional attached subnet identifier.
            :param placement_group_id: Optional IB partition / placement
                group identifier.
            :param network_interfaces: Optional list of NIC dicts.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.vm_id = vm_id
        self.name = name
        self.instance_type = instance_type
        self.location = location
        self.state = state
        self.project_id = project_id
        self.subnet_id = subnet_id
        self.placement_group_id = placement_group_id
        self.network_interfaces: List[Dict[str, Any]] = (
            network_interfaces if network_interfaces is not None else []
        )
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrusoeVm":
        """
            Build a :class:`CrusoeVm` from a Crusoe API payload.

            :param data: The decoded API payload.

            :returns: A populated :class:`CrusoeVm`.
        """
        vm_id = data.get("id", data.get("vm_id", ""))
        name = data.get("name", "")
        instance_type = data.get("type", data.get("instance_type", ""))
        location = data.get("location", None)
        state = data.get("state", None)
        project_id = data.get("project_id", None)
        subnet_id = data.get("subnet_id", None)
        placement_group_id = data.get("ib_partition_id",
                                      data.get("placement_group_id", None))
        network_interfaces = data.get("network_interfaces", None)
        labels = data.get("labels", None)

        rtnval = cls(vm_id=vm_id, name=name, instance_type=instance_type,
                     location=location, state=state, project_id=project_id,
                     subnet_id=subnet_id,
                     placement_group_id=placement_group_id,
                     network_interfaces=network_interfaces, labels=labels)
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`CrusoeVm` to a canonical API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this VM.
        """
        rtnval: Dict[str, Any] = {
            "id": self.vm_id,
            "name": self.name,
            "type": self.instance_type,
            "location": self.location,
            "state": self.state,
            "project_id": self.project_id,
            "subnet_id": self.subnet_id,
            "ib_partition_id": self.placement_group_id,
            "network_interfaces": self.network_interfaces,
            "labels": self.labels,
        }
        return rtnval
