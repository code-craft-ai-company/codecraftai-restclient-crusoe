"""
    .. module:: crusoevpc
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeVpc` typed model
                   record for a Crusoe Cloud VPC.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoeVpc:
    """
        Typed record describing a Crusoe Cloud VPC.

        Hand-authored from the documented Crusoe Cloud API per the §9.2a
        codegen decision recorded in ``AGENTS.md``.
    """

    def __init__(self, *, vpc_id: str, name: str, cidr: str,
                 project_id: str, state: Optional[str] = None,
                 labels: Optional[Dict[str, str]] = None) -> None:
        """
            Initialize a :class:`CrusoeVpc` record.

            :param vpc_id: The Crusoe-assigned VPC identifier.
            :param name: The VPC name.
            :param cidr: The VPC CIDR block.
            :param project_id: The owning project identifier.
            :param state: Optional lifecycle state string.
            :param labels: Optional label key/value mapping.

            :returns: ``None``.
        """
        self.vpc_id = vpc_id
        self.name = name
        self.cidr = cidr
        self.project_id = project_id
        self.state = state
        self.labels: Dict[str, str] = labels if labels is not None else {}
        return

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrusoeVpc":
        """
            Build a :class:`CrusoeVpc` from a Crusoe API payload dictionary.

            :param data: The decoded API payload.

            :returns: A populated :class:`CrusoeVpc`.
        """
        vpc_id = data.get("id", data.get("vpc_id", ""))
        name = data.get("name", "")
        cidr = data.get("cidr_block", data.get("cidr", ""))
        project_id = data.get("project_id", "")
        state = data.get("state", None)
        labels = data.get("labels", None)

        rtnval = cls(vpc_id=vpc_id, name=name, cidr=cidr,
                     project_id=project_id, state=state, labels=labels)
        return rtnval
