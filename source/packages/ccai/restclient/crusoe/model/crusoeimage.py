"""
    .. module:: crusoeimage
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeImage` typed model
                   record for a Crusoe Cloud machine image.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict


class CrusoeImage:
    """
        Typed record describing a Crusoe Cloud machine image.

        Hand-authored from the documented Crusoe Cloud API per the §9.2a
        codegen decision recorded in ``AGENTS.md``.
    """

    def __init__(self, *, image_id: str, name: str, family: str,
                 version: str, architecture: str) -> None:
        """
            Initialize a :class:`CrusoeImage` record.

            :param image_id: The Crusoe-assigned image identifier / alias.
            :param name: The image name.
            :param family: The image family (ubuntu, debian, ...).
            :param version: The image version string.
            :param architecture: The image architecture (x86_64, arm64).

            :returns: ``None``.
        """
        self.image_id = image_id
        self.name = name
        self.family = family
        self.version = version
        self.architecture = architecture
        return

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrusoeImage":
        """
            Build a :class:`CrusoeImage` from a Crusoe API payload.

            :param data: The decoded API payload.

            :returns: A populated :class:`CrusoeImage`.
        """
        image_id = data.get("id", data.get("image_id", data.get("name", "")))
        name = data.get("name", "")
        family = data.get("family", "")
        version = data.get("version", "")
        architecture = data.get("architecture", "x86_64")

        rtnval = cls(image_id=image_id, name=name, family=family,
                     version=version, architecture=architecture)
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`CrusoeImage` to a canonical API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this image.
        """
        rtnval: Dict[str, Any] = {
            "id": self.image_id,
            "name": self.name,
            "family": self.family,
            "version": self.version,
            "architecture": self.architecture,
        }
        return rtnval
