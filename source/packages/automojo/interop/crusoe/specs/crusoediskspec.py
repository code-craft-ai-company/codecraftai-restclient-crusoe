"""
    .. module:: crusoediskspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeDiskSpec` request
                   object for creating a Crusoe Cloud disk.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoeDiskSpec:
    """
        Request object describing a Crusoe Cloud disk to create.
    """

    def __init__(self, *, name: str, size_gib: int, location: str,
                 disk_type: str = "persistent-ssd",
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeDiskSpec`.

            :param name: The desired disk name.
            :param size_gib: The desired disk size in gibibytes.
            :param location: The Crusoe location for the disk.
            :param disk_type: The Crusoe disk type string.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.name = name
        self.size_gib = size_gib
        self.location = location
        self.disk_type = disk_type
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    def to_payload(self) -> Dict[str, Any]:
        """
            Translate this spec into a Crusoe API request payload.

            :returns: The request payload dictionary.
        """
        rtnval: Dict[str, Any] = {
            "name": self.name,
            "size_gib": self.size_gib,
            "location": self.location,
            "type": self.disk_type,
        }
        if len(self.labels) > 0:
            rtnval["labels"] = dict(self.labels)
        return rtnval
