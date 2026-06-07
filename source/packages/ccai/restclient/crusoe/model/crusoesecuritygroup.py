"""
    .. module:: crusoesecuritygroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeSecurityGroup` typed
                   model record for a Crusoe Cloud security group.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional


class CrusoeSecurityGroup:
    """
        Typed record describing a Crusoe Cloud security group.

        Hand-authored from the documented Crusoe Cloud API per the §9.2a
        codegen decision recorded in ``AGENTS.md``.
    """

    def __init__(self, *, security_group_id: str, name: str, vpc_id: str,
                 ingress_rules: Optional[List[Dict[str, Any]]] = None,
                 egress_rules: Optional[List[Dict[str, Any]]] = None,
                 state: Optional[str] = None,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeSecurityGroup` record.

            :param security_group_id: The Crusoe-assigned identifier.
            :param name: The security group name.
            :param vpc_id: The parent VPC identifier.
            :param ingress_rules: Optional list of ingress rule dicts.
            :param egress_rules: Optional list of egress rule dicts.
            :param state: Optional lifecycle state string.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.security_group_id = security_group_id
        self.name = name
        self.vpc_id = vpc_id
        self.ingress_rules: List[Dict[str, Any]] = (
            ingress_rules if ingress_rules is not None else []
        )
        self.egress_rules: List[Dict[str, Any]] = (
            egress_rules if egress_rules is not None else []
        )
        self.state = state
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrusoeSecurityGroup":
        """
            Build a :class:`CrusoeSecurityGroup` from a Crusoe API payload.

            :param data: The decoded API payload.

            :returns: A populated :class:`CrusoeSecurityGroup`.
        """
        security_group_id = data.get("id", data.get("security_group_id", ""))
        name = data.get("name", "")
        vpc_id = data.get("vpc_id", "")
        ingress_rules = data.get("ingress_rules", None)
        egress_rules = data.get("egress_rules", None)
        state = data.get("state", None)
        labels = data.get("labels", None)

        rtnval = cls(security_group_id=security_group_id, name=name,
                     vpc_id=vpc_id, ingress_rules=ingress_rules,
                     egress_rules=egress_rules, state=state, labels=labels)
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`CrusoeSecurityGroup` to a canonical
            API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this security group.
        """
        rtnval: Dict[str, Any] = {
            "id": self.security_group_id,
            "name": self.name,
            "vpc_id": self.vpc_id,
            "ingress_rules": self.ingress_rules,
            "egress_rules": self.egress_rules,
            "state": self.state,
            "labels": self.labels,
        }
        return rtnval
