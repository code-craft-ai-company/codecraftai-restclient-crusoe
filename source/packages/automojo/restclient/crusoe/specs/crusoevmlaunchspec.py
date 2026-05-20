"""
    .. module:: crusoevmlaunchspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeVmLaunchSpec` request
                   object for launching a Crusoe Cloud virtual machine.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class CrusoeVmLaunchSpec:
    """
        Request object describing a Crusoe Cloud virtual machine to launch.

        When ``placement_group_id`` is supplied the
        ``placement_group_interconnect`` field SHALL describe its interconnect
        so the client can reject an interconnect/instance-type mismatch
        before issuing the launch.
    """

    def __init__(self, *, name: str, instance_type: str, location: str,
                 image_id: str, subnet_id: str,
                 ssh_key_ids: Optional[List[str]] = None,
                 security_group_ids: Optional[List[str]] = None,
                 disk_ids: Optional[List[str]] = None,
                 placement_group_id: Optional[str] = None,
                 placement_group_interconnect: Optional[str] = None,
                 instance_type_supports_ib: bool = False,
                 user_data: Optional[str] = None,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeVmLaunchSpec`.

            :param name: The desired VM name.
            :param instance_type: The Crusoe instance type / SKU.
            :param location: The Crusoe location for the VM.
            :param image_id: The image identifier / alias to boot from.
            :param subnet_id: The subnet identifier to attach.
            :param ssh_key_ids: Optional list of SSH key identifiers.
            :param security_group_ids: Optional list of security group ids.
            :param disk_ids: Optional list of disk identifiers to attach.
            :param placement_group_id: Optional IB placement group id.
            :param placement_group_interconnect: Optional interconnect of
                the referenced placement group.
            :param instance_type_supports_ib: Whether the requested instance
                type supports InfiniBand placement.
            :param user_data: Optional cloud-init user-data payload.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.name = name
        self.instance_type = instance_type
        self.location = location
        self.image_id = image_id
        self.subnet_id = subnet_id
        self.ssh_key_ids: List[str] = (
            ssh_key_ids if ssh_key_ids is not None else []
        )
        self.security_group_ids: List[str] = (
            security_group_ids if security_group_ids is not None else []
        )
        self.disk_ids: List[str] = disk_ids if disk_ids is not None else []
        self.placement_group_id = placement_group_id
        self.placement_group_interconnect = placement_group_interconnect
        self.instance_type_supports_ib = instance_type_supports_ib
        self.user_data = user_data
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    def to_payload(self) -> Dict[str, Any]:
        """
            Translate this spec into a Crusoe API request payload.

            :returns: The request payload dictionary.
        """
        rtnval: Dict[str, Any] = {
            "name": self.name,
            "type": self.instance_type,
            "location": self.location,
            "image": self.image_id,
            "subnet_id": self.subnet_id,
        }
        if len(self.ssh_key_ids) > 0:
            rtnval["ssh_key_ids"] = list(self.ssh_key_ids)
        if len(self.security_group_ids) > 0:
            rtnval["security_group_ids"] = list(self.security_group_ids)
        if len(self.disk_ids) > 0:
            rtnval["disk_ids"] = list(self.disk_ids)
        if self.placement_group_id is not None:
            rtnval["ib_partition_id"] = self.placement_group_id
        if self.user_data is not None:
            rtnval["user_data"] = self.user_data
        if len(self.labels) > 0:
            rtnval["labels"] = dict(self.labels)
        return rtnval
