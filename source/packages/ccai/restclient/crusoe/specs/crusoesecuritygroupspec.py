"""
    .. module:: crusoesecuritygroupspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeSecurityGroupSpec`
                   request object for creating a Crusoe Cloud security group.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class CrusoeSecurityGroupSpec:
    """
        Request object describing a Crusoe Cloud security group to create.
    """

    def __init__(self, *, name: str, vpc_id: str,
                 ingress_rules: Optional[List[Dict[str, Any]]] = None,
                 egress_rules: Optional[List[Dict[str, Any]]] = None,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeSecurityGroupSpec`.

            :param name: The desired security group name.
            :param vpc_id: The parent VPC identifier.
            :param ingress_rules: Optional list of ingress rule dicts.
            :param egress_rules: Optional list of egress rule dicts.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.name = name
        self.vpc_id = vpc_id
        self.ingress_rules: List[Dict[str, Any]] = (
            ingress_rules if ingress_rules is not None else []
        )
        self.egress_rules: List[Dict[str, Any]] = (
            egress_rules if egress_rules is not None else []
        )
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    def to_payload(self) -> Dict[str, Any]:
        """
            Translate this spec into a Crusoe API request payload.

            :returns: The request payload dictionary.
        """
        rtnval: Dict[str, Any] = {
            "name": self.name,
            "vpc_id": self.vpc_id,
            "ingress_rules": list(self.ingress_rules),
            "egress_rules": list(self.egress_rules),
        }
        if len(self.labels) > 0:
            rtnval["labels"] = dict(self.labels)
        return rtnval
