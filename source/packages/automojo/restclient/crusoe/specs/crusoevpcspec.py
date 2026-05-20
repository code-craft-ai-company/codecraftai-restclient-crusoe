"""
    .. module:: crusoevpcspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeVpcSpec` request
                   object for creating a Crusoe Cloud VPC.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoeVpcSpec:
    """
        Request object describing a Crusoe Cloud VPC to create.
    """

    def __init__(self, *, name: str, cidr: str, project_id: str,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeVpcSpec`.

            :param name: The desired VPC name.
            :param cidr: The desired VPC CIDR block.
            :param project_id: The owning project identifier.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.name = name
        self.cidr = cidr
        self.project_id = project_id
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
        }
        if len(self.labels) > 0:
            rtnval["labels"] = dict(self.labels)
        return rtnval
