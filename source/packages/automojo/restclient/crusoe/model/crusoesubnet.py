"""
    .. module:: crusoesubnet
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeSubnet` typed model
                   record for a Crusoe Cloud subnet.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoeSubnet:
    """
        Typed record describing a Crusoe Cloud subnet.

        Hand-authored from the documented Crusoe Cloud API per the §9.2a
        codegen decision recorded in ``AGENTS.md``.
    """

    def __init__(self, *, subnet_id: str, name: str, cidr: str,
                 vpc_id: str, location: Optional[str] = None,
                 state: Optional[str] = None,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeSubnet` record.

            :param subnet_id: The Crusoe-assigned subnet identifier.
            :param name: The subnet name.
            :param cidr: The subnet CIDR block.
            :param vpc_id: The parent VPC identifier.
            :param location: Optional Crusoe location string.
            :param state: Optional lifecycle state string.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.subnet_id = subnet_id
        self.name = name
        self.cidr = cidr
        self.vpc_id = vpc_id
        self.location = location
        self.state = state
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrusoeSubnet":
        """
            Build a :class:`CrusoeSubnet` from a Crusoe API payload.

            :param data: The decoded API payload.

            :returns: A populated :class:`CrusoeSubnet`.
        """
        subnet_id = data.get("id", data.get("subnet_id", ""))
        name = data.get("name", "")
        cidr = data.get("cidr_block", data.get("cidr", ""))
        vpc_id = data.get("vpc_id", "")
        location = data.get("location", None)
        state = data.get("state", None)
        labels = data.get("labels", None)

        rtnval = cls(subnet_id=subnet_id, name=name, cidr=cidr, vpc_id=vpc_id,
                     location=location, state=state, labels=labels)
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`CrusoeSubnet` to a canonical API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this subnet.
        """
        rtnval: Dict[str, Any] = {
            "id": self.subnet_id,
            "name": self.name,
            "cidr_block": self.cidr,
            "vpc_id": self.vpc_id,
            "location": self.location,
            "state": self.state,
            "labels": self.labels,
        }
        return rtnval
