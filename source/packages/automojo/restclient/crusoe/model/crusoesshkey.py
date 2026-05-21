"""
    .. module:: crusoesshkey
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeSshKey` typed model
                   record for a Crusoe Cloud SSH key.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoeSshKey:
    """
        Typed record describing a Crusoe Cloud SSH key.

        Hand-authored from the documented Crusoe Cloud API per the §9.2a
        codegen decision recorded in ``AGENTS.md``.
    """

    def __init__(self, *, ssh_key_id: str, name: str,
                 public_key: str, project_id: Optional[str] = None) -> None:
        """
            Initialize a :class:`CrusoeSshKey` record.

            :param ssh_key_id: The Crusoe-assigned SSH key identifier.
            :param name: The SSH key name.
            :param public_key: The OpenSSH-format public key material.
            :param project_id: Optional owning project identifier.

            :returns: ``None``.
        """
        self.ssh_key_id = ssh_key_id
        self.name = name
        self.public_key = public_key
        self.project_id = project_id
        return

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrusoeSshKey":
        """
            Build a :class:`CrusoeSshKey` from a Crusoe API payload.

            :param data: The decoded API payload.

            :returns: A populated :class:`CrusoeSshKey`.
        """
        ssh_key_id = data.get("id", data.get("ssh_key_id", ""))
        name = data.get("name", "")
        public_key = data.get("public_key", "")
        project_id = data.get("project_id", None)

        rtnval = cls(ssh_key_id=ssh_key_id, name=name,
                     public_key=public_key, project_id=project_id)
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`CrusoeSshKey` to a canonical API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this SSH key.
        """
        rtnval: Dict[str, Any] = {
            "id": self.ssh_key_id,
            "name": self.name,
            "public_key": self.public_key,
            "project_id": self.project_id,
        }
        return rtnval
