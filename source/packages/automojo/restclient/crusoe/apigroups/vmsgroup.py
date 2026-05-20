"""
    .. module:: vmsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`VmsGroup` api group
                   exposing the Crusoe Cloud virtual machine endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

from typing import Dict, List, Optional, Tuple

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.restclient.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from automojo.restclient.crusoe.apigroups.disksgroup import extract_operation_id
from automojo.restclient.crusoe.apigroups.groupsupport import (
    compose_leaf, iter_paged_items, raise_for_status, safe_json
)
from automojo.restclient.crusoe.exceptions.crusoeexceptions import (
    CrusoePlacementMismatchError
)
from automojo.restclient.crusoe.model.crusoetaskhandle import CrusoeTaskHandle
from automojo.restclient.crusoe.model.crusoevm import CrusoeVm
from automojo.restclient.crusoe.specs.crusoevmlaunchspec import CrusoeVmLaunchSpec


class VmsGroup(RestApiGroup):
    """
        :class:`VmsGroup` exposes the Crusoe Cloud virtual machine endpoints —
        launch (with placement-mismatch validation), get, list, power-cycle,
        and no-op terminate.
    """

    def launch(self, *, project_id: str, spec: CrusoeVmLaunchSpec,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS
               ) -> Tuple[CrusoeVm, Optional[CrusoeTaskHandle]]:
        """
            Launch a virtual machine.

            When ``spec`` references an InfiniBand placement group but the
            requested instance type does not support InfiniBand placement,
            a :class:`CrusoePlacementMismatchError` is raised before the
            request is issued.

            :param project_id: The owning project identifier.
            :param spec: The :class:`CrusoeVmLaunchSpec` describing the VM.
            :param aspects: Behaviour control for the call.

            :returns: A tuple of (:class:`CrusoeVm`, optional
                :class:`CrusoeTaskHandle`).

            :raises: :class:`CrusoePlacementMismatchError` when the placement
                group interconnect is incompatible with the instance type.
        """
        if spec is None:
            raise SemanticError("'spec' must be a CrusoeVmLaunchSpec.")

        self._validate_placement(spec=spec)

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "instances"])
        response = client.request(method="POST", leaf=leaf,
                                  json_body=spec.to_payload(), aspects=aspects)
        raise_for_status(response=response, action="launch vm")

        payload = safe_json(response=response)
        vm = CrusoeVm.from_dict(payload)

        operation_id = extract_operation_id(payload=payload)
        handle: Optional[CrusoeTaskHandle] = None
        if operation_id is not None:
            handle = CrusoeTaskHandle(operation_id=operation_id,
                                      operations_group=client.operations)

        rtnval = (vm, handle)
        return rtnval

    def get(self, *, project_id: str, vm_id: str,
            aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoeVm:
        """
            Retrieve a single VM by identifier.

            :param project_id: The owning project identifier.
            :param vm_id: The VM identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeVm` record.
        """
        if vm_id is None or len(vm_id) == 0:
            raise SemanticError("'vm_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "instances",
                                      vm_id])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="get vm")

        rtnval = CrusoeVm.from_dict(safe_json(response=response))
        return rtnval

    def list(self, *, project_id: str,
             aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> List[CrusoeVm]:
        """
            List every VM in a project, following paging cursors.

            :param project_id: The owning project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`CrusoeVm` records.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "instances"])

        def _fetch(cursor: Optional[str]) -> Dict:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list vms")
            page = safe_json(response=response)
            return page

        rtnval: List[CrusoeVm] = []
        for entry in iter_paged_items(fetch_page=_fetch, items_field="items"):
            rtnval.append(CrusoeVm.from_dict(entry))
        return rtnval

    def power_on(self, *, project_id: str, vm_id: str,
                 aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> Optional[CrusoeTaskHandle]:
        """
            Power on a VM.

            :param project_id: The owning project identifier.
            :param vm_id: The VM identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeTaskHandle`, or ``None`` when the call
                completed synchronously.
        """
        rtnval = self._power_action(project_id=project_id, vm_id=vm_id,
                                    action="start", aspects=aspects)
        return rtnval

    def power_off(self, *, project_id: str, vm_id: str,
                  aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> Optional[CrusoeTaskHandle]:
        """
            Power off a VM.

            :param project_id: The owning project identifier.
            :param vm_id: The VM identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeTaskHandle`, or ``None`` when the call
                completed synchronously.
        """
        rtnval = self._power_action(project_id=project_id, vm_id=vm_id,
                                    action="stop", aspects=aspects)
        return rtnval

    def terminate(self, *, project_id: str, vm_id: str,
                  aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> Optional[CrusoeTaskHandle]:
        """
            Terminate a VM.  An already-terminated id is treated as a no-op.

            :param project_id: The owning project identifier.
            :param vm_id: The VM identifier to terminate.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeTaskHandle`, or ``None`` when the VM was
                already absent or terminated synchronously.
        """
        if vm_id is None or len(vm_id) == 0:
            raise SemanticError("'vm_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "instances",
                                      vm_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        status = response.status_code
        if status == 404:
            rtnval: Optional[CrusoeTaskHandle] = None
            return rtnval

        raise_for_status(response=response, action="terminate vm")

        payload = safe_json(response=response)
        operation_id = extract_operation_id(payload=payload)
        rtnval = None
        if operation_id is not None:
            rtnval = CrusoeTaskHandle(operation_id=operation_id,
                                      operations_group=client.operations)
        return rtnval

    def _power_action(self, *, project_id: str, vm_id: str, action: str,
                      aspects: AspectsCrusoe) -> Optional[CrusoeTaskHandle]:
        """
            Shared implementation for power-on and power-off.

            :param project_id: The owning project identifier.
            :param vm_id: The VM identifier.
            :param action: One of ``start`` or ``stop``.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeTaskHandle`, or ``None``.
        """
        if vm_id is None or len(vm_id) == 0:
            raise SemanticError("'vm_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["projects", project_id, "instances",
                                      vm_id, action])
        response = client.request(method="POST", leaf=leaf, aspects=aspects)
        raise_for_status(response=response,
                         action="{} vm".format(action))

        payload = safe_json(response=response)
        operation_id = extract_operation_id(payload=payload)
        rtnval: Optional[CrusoeTaskHandle] = None
        if operation_id is not None:
            rtnval = CrusoeTaskHandle(operation_id=operation_id,
                                      operations_group=client.operations)
        return rtnval

    def _validate_placement(self, *, spec: CrusoeVmLaunchSpec) -> None:
        """
            Validate that a referenced IB placement group is compatible with
            the requested instance type.

            :param spec: The :class:`CrusoeVmLaunchSpec`.

            :returns: ``None``.

            :raises: :class:`CrusoePlacementMismatchError` when the placement
                group requires InfiniBand but the instance type does not
                support it.
        """
        if spec.placement_group_id is None:
            return

        interconnect = spec.placement_group_interconnect
        if interconnect is None:
            return

        if interconnect.strip().lower() != "infiniband":
            return

        if spec.instance_type_supports_ib is True:
            return

        err_msg_lines = [
            "Placement group interconnect is incompatible with the "
            "requested instance type."
        ]
        err_msg_lines.append("PLACEMENT_GROUP_ID: {}".format(
            spec.placement_group_id))
        err_msg_lines.append("PLACEMENT_INTERCONNECT: {}".format(interconnect))
        err_msg_lines.append("INSTANCE_TYPE: {}".format(spec.instance_type))
        err_msg = os.linesep.join(err_msg_lines)
        raise CrusoePlacementMismatchError(err_msg)
