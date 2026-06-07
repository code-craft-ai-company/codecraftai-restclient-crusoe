"""
    .. module:: sshkeysgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`SshKeysGroup` api group
                   exposing the Crusoe Cloud SSH key endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from ccai.errors.exceptions import SemanticError

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from ccai.restclient.crusoe.apigroups.groupsupport import (
    compose_leaf, iter_paged_items, raise_for_status, safe_json
)
from ccai.restclient.crusoe.model.crusoesshkey import CrusoeSshKey


class SshKeysGroup(RestApiGroup):
    """
        :class:`SshKeysGroup` exposes the Crusoe Cloud SSH key endpoints —
        idempotent register, list, and no-op delete.
    """

    def register(self, *, project_id: str, name: str, public_key: str,
                 aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoeSshKey:
        """
            Register an SSH key, returning the existing record when a key
            with the same name already exists.

            :param project_id: The owning project identifier.
            :param name: The SSH key name.
            :param public_key: The OpenSSH-format public key material.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeSshKey` record.
        """
        if name is None or len(name) == 0:
            raise SemanticError("'name' must be a non-empty string.")
        if public_key is None or len(public_key) == 0:
            raise SemanticError("'public_key' must be a non-empty string.")

        existing = self._find_by_name(project_id=project_id, name=name,
                                      aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "ssh-keys"])
        body: Dict[str, Any] = {"name": name, "public_key": public_key}
        response = client.request(method="POST", leaf=leaf,
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="register ssh key")

        rtnval = CrusoeSshKey.from_dict(safe_json(response=response))
        return rtnval

    def list(self, *, project_id: str,
             aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> List[CrusoeSshKey]:
        """
            List every SSH key in a project, following paging cursors.

            :param project_id: The owning project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CrusoeSshKey` records.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "ssh-keys"])

        def _fetch(cursor: Optional[str]) -> Dict:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list ssh keys")
            page = safe_json(response=response)
            return page

        rtnval: List[CrusoeSshKey] = []
        for entry in iter_paged_items(fetch_page=_fetch, items_field="items"):
            rtnval.append(CrusoeSshKey.from_dict(entry))
        return rtnval

    def delete(self, *, project_id: str, ssh_key_id: str,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> None:
        """
            Delete an SSH key.  An unknown id is treated as already removed.

            :param project_id: The owning project identifier.
            :param ssh_key_id: The SSH key identifier to delete.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        if ssh_key_id is None or len(ssh_key_id) == 0:
            raise SemanticError("'ssh_key_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "ssh-keys",
                                      ssh_key_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete ssh key")
        return

    def _find_by_name(self, *, project_id: str, name: str,
                      aspects: AspectsCrusoe) -> Optional[CrusoeSshKey]:
        """
            Find an SSH key by name within a project.

            :param project_id: The owning project identifier.
            :param name: The SSH key name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching record, or ``None``.
        """
        records = self.list(project_id=project_id, aspects=aspects)
        rtnval: Optional[CrusoeSshKey] = None
        for record in records:
            if record.name == name:
                rtnval = record
                break
        return rtnval
