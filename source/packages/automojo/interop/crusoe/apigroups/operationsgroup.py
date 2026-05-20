"""
    .. module:: operationsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`OperationsGroup` api group
                   exposing the Crusoe Cloud long-running operation endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.interop.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from automojo.interop.crusoe.apigroups.groupsupport import (
    compose_leaf, raise_for_status, safe_json
)
from automojo.interop.crusoe.model.crusoeoperationresult import (
    CrusoeOperationResult
)


class OperationsGroup(RestApiGroup):
    """
        :class:`OperationsGroup` exposes the Crusoe Cloud operations endpoint
        consumed by :class:`CrusoeTaskHandle.wait` to poll async operations.
    """

    def get(self, *, operation_id: str,
            aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> CrusoeOperationResult:
        """
            Retrieve the status of a single Crusoe operation.

            :param operation_id: The Crusoe operation identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`CrusoeOperationResult` record.
        """
        if operation_id is None or len(operation_id) == 0:
            raise SemanticError("'operation_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(base=client.base_leaf,
                            segments=["operations", operation_id])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="get operation")

        rtnval = CrusoeOperationResult.from_dict(safe_json(response=response))
        return rtnval
