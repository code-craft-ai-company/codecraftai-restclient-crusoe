"""
    .. module:: crusoedisk
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeDisk` typed model
                   record for a Crusoe Cloud disk.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoeDisk:
    """
        Typed record describing a Crusoe Cloud disk.

        Hand-authored from the documented Crusoe Cloud API per the §9.2a
        codegen decision recorded in ``AGENTS.md``.
    """

    def __init__(self, *, disk_id: str, name: str, size_gib: int,
                 disk_type: str, location: Optional[str] = None,
                 state: Optional[str] = None,
                 attached_to: Optional[str] = None,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeDisk` record.

            :param disk_id: The Crusoe-assigned disk identifier.
            :param name: The disk name.
            :param size_gib: The disk size in gibibytes.
            :param disk_type: The Crusoe disk type string.
            :param location: Optional Crusoe location string.
            :param state: Optional lifecycle state string.
            :param attached_to: Optional VM identifier the disk is attached to.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.disk_id = disk_id
        self.name = name
        self.size_gib = size_gib
        self.disk_type = disk_type
        self.location = location
        self.state = state
        self.attached_to = attached_to
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrusoeDisk":
        """
            Build a :class:`CrusoeDisk` from a Crusoe API payload.

            :param data: The decoded API payload.

            :returns: A populated :class:`CrusoeDisk`.
        """
        disk_id = data.get("id", data.get("disk_id", ""))
        name = data.get("name", "")
        size_gib = data.get("size_gib", data.get("size", 0))
        disk_type = data.get("type", data.get("disk_type", ""))
        location = data.get("location", None)
        state = data.get("state", None)
        attached_to = data.get("attached_to", None)
        labels = data.get("labels", None)

        rtnval = cls(disk_id=disk_id, name=name, size_gib=size_gib,
                     disk_type=disk_type, location=location, state=state,
                     attached_to=attached_to, labels=labels)
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`CrusoeDisk` to a canonical API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this disk.
        """
        rtnval: Dict[str, Any] = {
            "id": self.disk_id,
            "name": self.name,
            "size_gib": self.size_gib,
            "type": self.disk_type,
            "location": self.location,
            "state": self.state,
            "attached_to": self.attached_to,
            "labels": self.labels,
        }
        return rtnval
