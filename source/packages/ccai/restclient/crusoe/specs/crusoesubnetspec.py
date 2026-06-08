"""
    .. module:: crusoesubnetspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeSubnetSpec` request
                   object for creating a Crusoe Cloud subnet.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoeSubnetSpec:
    """
        Request object describing a Crusoe Cloud subnet to create.
    """

    def __init__(self, *, name: str, cidr: str, vpc_id: str,
                 vpc_cidr: str, location: str,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeSubnetSpec`.

            :param name: The desired subnet name.
            :param cidr: The desired subnet CIDR block.
            :param vpc_id: The parent VPC identifier.
            :param vpc_cidr: The parent VPC CIDR (used for containment check).
            :param location: The Crusoe location for the subnet.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.name = name
        self.cidr = cidr
        self.vpc_id = vpc_id
        self.vpc_cidr = vpc_cidr
        self.location = location
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    def to_payload(self) -> Dict[str, Any]:
        """
            Translate this spec into a Crusoe API request payload.

            :returns: The request payload dictionary.
        """
        rtnval: Dict[str, Any] = {
            "name": self.name,
            "cidr_block": self.cidr,
            "vpc_id": self.vpc_id,
            "location": self.location,
        }
        if len(self.labels) > 0:
            rtnval["labels"] = dict(self.labels)
        return rtnval
