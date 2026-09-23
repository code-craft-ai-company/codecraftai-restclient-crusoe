"""
    .. module:: crusoetaskhandle
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeTaskHandle`, an
                   :class:`ITaskHandle` implementation that polls a Crusoe
                   Cloud operation to completion.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import time

from typing import TYPE_CHECKING

from ccai.errors.exceptions import SemanticError

from ccai.interfaces.itaskhandle import TaskResult, TaskState

from ccai.restclient.crusoe.aspectscrusoe import (
    AspectsCrusoe, DEFAULT_CRUSOE_ASPECTS
)
from ccai.restclient.crusoe.model.crusoeoperationresult import (
    CrusoeOperationResult
)


if TYPE_CHECKING:
    from ccai.restclient.crusoe.apigroups.operationsgroup import OperationsGroup


TERMINAL_TASK_STATES = (
    TaskState.SUCCEEDED, TaskState.FAILED, TaskState.CANCELLED
)

# Map Crusoe operation state strings onto the neutral TaskState enum.
_STATE_MAP = {
    "pending": TaskState.PENDING,
    "queued": TaskState.PENDING,
    "running": TaskState.RUNNING,
    "in_progress": TaskState.RUNNING,
    "succeeded": TaskState.SUCCEEDED,
    "success": TaskState.SUCCEEDED,
    "complete": TaskState.SUCCEEDED,
    "completed": TaskState.SUCCEEDED,
    "done": TaskState.SUCCEEDED,
    "failed": TaskState.FAILED,
    "error": TaskState.FAILED,
    "cancelled": TaskState.CANCELLED,
    "canceled": TaskState.CANCELLED,
}


def map_operation_state(*, state: str) -> TaskState:
    """
        Map a Crusoe operation state string onto a neutral :class:`TaskState`.

        Unknown states are treated as :attr:`TaskState.RUNNING` so the poll
        loop continues until a recognised terminal state appears or the
        completion budget elapses.

        :param state: The Crusoe operation state string.

        :returns: The corresponding :class:`TaskState`.
    """
    normalized = ""
    if state is not None:
        normalized = state.strip().lower()

    rtnval = _STATE_MAP.get(normalized, TaskState.RUNNING)
    return rtnval


class CrusoeTaskHandle:
    """
        :class:`CrusoeTaskHandle` is a synchronous-poll handle on a Crusoe
        Cloud long-running operation.  It implements the
        :class:`ccai.interfaces.itaskhandle.ITaskHandle` protocol; the
        poll loop pacing is controlled entirely by the supplied aspects.
    """

    def __init__(self, *, operation_id: str,
                 operations_group: "OperationsGroup") -> None:
        """
            Initialize a :class:`CrusoeTaskHandle`.

            :param operation_id: The Crusoe-assigned operation identifier.
            :param operations_group: The :class:`OperationsGroup` used to
                fetch operation status.

            :returns: ``None``.
        """
        self._operation_id = operation_id
        self._operations_group = operations_group
        self._last_observed_state: TaskState = TaskState.PENDING
        return

    def task_id(self) -> str:
        """
            Return the Crusoe operation identifier.

            :returns: The operation identifier string.
        """
        rtnval = self._operation_id
        return rtnval

    def is_done(self) -> bool:
        """
            Report whether the last observed state is terminal.

            :returns: ``True`` when the last observed state is terminal.
        """
        rtnval = self._last_observed_state in TERMINAL_TASK_STATES
        return rtnval

    def wait(self, *,
             aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> TaskResult:
        """
            Poll the Crusoe operation until a terminal state is reached.

            :param aspects: Behaviour control supplying the poll interval and
                completion timeout.

            :returns: A terminal :class:`TaskResult`.

            :raises: :class:`SemanticError` when interval/timeout are not
                positive; :class:`TimeoutError` when the budget elapses.
        """
        interval = aspects.completion_interval
        timeout = aspects.completion_timeout

        if interval <= 0:
            raise SemanticError(
                "CrusoeTaskHandle.wait requires completion_interval > 0."
            )
        if timeout <= 0:
            raise SemanticError(
                "CrusoeTaskHandle.wait requires completion_timeout > 0."
            )

        start = time.monotonic()
        deadline = start + timeout

        rtnval = None
        while True:
            operation = self._operations_group.get(
                operation_id=self._operation_id, aspects=aspects
            )
            state = map_operation_state(state=operation.state)
            self._last_observed_state = state

            if state in TERMINAL_TASK_STATES:
                rtnval = self._assemble_result(state=state,
                                               operation=operation)
                break

            now = time.monotonic()
            if now >= deadline:
                err_msg = (
                    "CrusoeTaskHandle.wait timed out after {0}s for "
                    "operation {1!r} (last observed state {2!r}).".format(
                        timeout, self._operation_id, state
                    )
                )
                raise TimeoutError(err_msg)

            time.sleep(interval)

        return rtnval

    def cancel(self, *,
               aspects: AspectsCrusoe = DEFAULT_CRUSOE_ASPECTS) -> None:
        """
            Request cancellation of the in-flight operation.

            The Crusoe Cloud operations API does not expose a cancel verb;
            this method is a no-op when the operation is already terminal and
            otherwise raises :class:`NotImplementedError`.

            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`NotImplementedError` when the operation is not
                yet terminal.
        """
        if self._last_observed_state in TERMINAL_TASK_STATES:
            return None

        err_msg = (
            "Crusoe Cloud operations do not support cancellation; "
            "operation {0!r} cannot be cancelled.".format(self._operation_id)
        )
        raise NotImplementedError(err_msg)

    def _assemble_result(self, *, state: TaskState,
                         operation: CrusoeOperationResult) -> TaskResult:
        """
            Build a :class:`TaskResult` from a terminal operation record.

            :param state: The terminal :class:`TaskState`.
            :param operation: The :class:`CrusoeOperationResult` payload.

            :returns: The assembled :class:`TaskResult`.
        """
        rtnval = TaskResult(task_id=self._operation_id, state=state,
                            progress=operation.progress,
                            error=operation.error, payload=operation.result)
        return rtnval
