"""
    .. module:: disksgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`DisksGroup` api group
                   exposing the Crusoe Cloud disk endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional, Tuple

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.interop.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from automojo.interop.crusoe.apigroups.groupsupport import (
    compose_leaf, iter_paged_items, raise_for_status, safe_json
)
from automojo.interop.crusoe.model.crusoedisk import CrusoeDisk
from automojo.interop.crusoe.model.crusoetaskhandle import CrusoeTaskHandle
from automojo.interop.crusoe.specs.crusoediskspec import CrusoeDiskSpec


def extract_operation_id(*, payload: Dict[str, Any]) -> Optional[str]:
    """
        Extract a Crusoe operation identifier from a response payload.

        :param payload: The decoded API payload.

        :returns: The operation id, or ``None`` when the call was synchronous.
    """
    operation = payload.get("operation", None)
    if isinstance(operation, dict):
        op_id = operation.get("id", None)
        if op_id is not None and len(str(op_id)) > 0:
            rtnval: Optional[str] = str(op_id)
            return rtnval

    op_id = payload.get("operation_id", None)
    if op_id is not None and len(str(op_id)) > 0:
        rtnval = str(op_id)
        return rtnval

    rtnval = None
    return rtnval


class DisksGroup(RestApiGroup):
    """
        :class:`DisksGroup` exposes the Crusoe Cloud disk endpoints — create,
        attach, detach, list, and no-op delete.  Async operations return a
        :class:`CrusoeTaskHandle` alongside the disk record.
    """

    def create(self, *, project_id: str, spec: CrusoeDiskSpec,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS
               ) -> Tuple[CrusoeDisk, Optional[CrusoeTaskHandle]]:
        """
            Create a disk, returning the record and an optional task handle.

            :param project_id: The owning project identifier.
            :param spec: The :class:`CrusoeDiskSpec` describing the disk.
            :param aspects: Behaviour control for the call.

            :returns: A tuple of (:class:`CrusoeDisk`, optional
                :class:`CrusoeTaskHandle`).
        """
        if spec is None:
            raise SemanticError("'spec' must be a CrusoeDiskSpec.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "disks"])
        response = client.request(method="POST", leaf=leaf,
                                  json_body=spec.to_payload(), aspects=aspects)
        raise_for_status(response=response, action="create disk")

        payload = safe_json(response=response)
        disk = CrusoeDisk.from_dict(payload)
        handle = self._handle_for(payload=payload)

        rtnval = (disk, handle)
        return rtnval

    def attach(self, *, project_id: str, disk_id: str, instance_id: str,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoeTaskHandle:
        """
            Attach a disk to a VM.

            :param project_id: The owning project identifier.
            :param disk_id: The disk identifier to attach.
            :param instance_id: The VM identifier to attach the disk to.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeTaskHandle` for the attach operation.
        """
        rtnval = self._attach_detach(project_id=project_id, disk_id=disk_id,
                                     instance_id=instance_id, attach=True,
                                     aspects=aspects)
        return rtnval

    def detach(self, *, project_id: str, disk_id: str, instance_id: str,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoeTaskHandle:
        """
            Detach a disk from a VM.

            :param project_id: The owning project identifier.
            :param disk_id: The disk identifier to detach.
            :param instance_id: The VM identifier to detach the disk from.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeTaskHandle` for the detach operation.
        """
        rtnval = self._attach_detach(project_id=project_id, disk_id=disk_id,
                                     instance_id=instance_id, attach=False,
                                     aspects=aspects)
        return rtnval

    def list(self, *, project_id: str,
             aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> List[CrusoeDisk]:
        """
            List every disk in a project, following paging cursors.

            :param project_id: The owning project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CrusoeDisk` records.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "disks"])

        def _fetch(cursor: Optional[str]) -> Dict:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list disks")
            page = safe_json(response=response)
            return page

        rtnval: List[CrusoeDisk] = []
        for entry in iter_paged_items(fetch_page=_fetch, items_field="items"):
            rtnval.append(CrusoeDisk.from_dict(entry))
        return rtnval

    def delete(self, *, project_id: str, disk_id: str,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> None:
        """
            Delete a disk.  An unknown id is treated as already removed.

            :param project_id: The owning project identifier.
            :param disk_id: The disk identifier to delete.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.
        """
        if disk_id is None or len(disk_id) == 0:
            raise SemanticError("'disk_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "disks",
                                      disk_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            return

        raise_for_status(response=response, action="delete disk")
        return

    def _attach_detach(self, *, project_id: str, disk_id: str,
                       instance_id: str, attach: bool,
                       aspects: AspectsCrusoe) -> CrusoeTaskHandle:
        """
            Shared implementation for attach and detach.

            :param project_id: The owning project identifier.
            :param disk_id: The disk identifier.
            :param instance_id: The VM identifier.
            :param attach: ``True`` for attach, ``False`` for detach.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeTaskHandle` for the operation.
        """
        if disk_id is None or len(disk_id) == 0:
            raise SemanticError("'disk_id' must be a non-empty string.")
        if instance_id is None or len(instance_id) == 0:
            raise SemanticError("'instance_id' must be a non-empty string.")

        verb = "attach"
        if attach is False:
            verb = "detach"

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "disks",
                                      disk_id, verb])
        body: Dict[str, Any] = {"instance_id": instance_id}
        response = client.request(method="POST", leaf=leaf,
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response,
                         action="{} disk".format(verb))

        payload = safe_json(response=response)
        handle = self._handle_for(payload=payload)
        if handle is None:
            err_msg = (
                "Crusoe disk {0} response did not include an operation "
                "id.".format(verb)
            )
            raise SemanticError(err_msg)

        rtnval = handle
        return rtnval

    def _handle_for(self, *,
                    payload: Dict[str, Any]) -> Optional[CrusoeTaskHandle]:
        """
            Build a :class:`CrusoeTaskHandle` from a response payload.

            :param payload: The decoded API payload.

            :returns: A :class:`CrusoeTaskHandle`, or ``None`` when the call
                was synchronous.
        """
        operation_id = extract_operation_id(payload=payload)
        rtnval: Optional[CrusoeTaskHandle] = None
        if operation_id is not None:
            rtnval = CrusoeTaskHandle(
                operation_id=operation_id,
                operations_group=self.client.operations
            )
        return rtnval
