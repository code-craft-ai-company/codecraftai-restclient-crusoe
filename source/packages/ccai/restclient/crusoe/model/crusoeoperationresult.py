"""
    .. module:: crusoeoperationresult
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`CrusoeOperationResult`
                   typed model record for a Crusoe Cloud async operation.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional


class CrusoeOperationResult:
    """
        Typed record describing the status of a Crusoe Cloud long-running
        operation.

        Hand-authored from the documented Crusoe Cloud API per the §9.2a
        codegen decision recorded in ``AGENTS.md``.
    """

    def __init__(self, *, operation_id: str, state: str,
                 progress: int = 0, error: Optional[str] = None,
                 result: Optional[Dict[str, Any]] = None) -> None:
        """
            Initialize a :class:`CrusoeOperationResult` record.

            :param operation_id: The Crusoe-assigned operation identifier.
            :param state: The operation state string as reported by Crusoe.
            :param progress: Integer percent-complete (0-100).
            :param error: Optional error string when the operation failed.
            :param result: Optional result sub-payload (e.g. created id).

            :returns: ``None``.
        """
        self.operation_id = operation_id
        self.state = state
        self.progress = progress
        self.error = error
        self.result: Dict[str, Any] = result if result is not None else {}
        return

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrusoeOperationResult":
        """
            Build a :class:`CrusoeOperationResult` from a Crusoe API payload.

            :param data: The decoded API payload.

            :returns: A populated :class:`CrusoeOperationResult`.
        """
        operation_id = data.get("id", data.get("operation_id", ""))
        state = data.get("state", data.get("status", ""))
        progress = data.get("progress", 0)
        error = data.get("error", None)
        result = data.get("result", None)

        rtnval = cls(operation_id=operation_id, state=state,
                     progress=progress, error=error, result=result)
        return rtnval

    def to_dict(self) -> Dict[str, Any]:
        """
            Serialize this :class:`CrusoeOperationResult` to a canonical
            API payload.

            The emitted keys match the primary key names that
            :meth:`from_dict` reads, so ``from_dict(to_dict(x))``
            reconstructs an equal record.

            :returns: A dictionary payload describing this operation.
        """
        rtnval: Dict[str, Any] = {
            "id": self.operation_id,
            "state": self.state,
            "progress": self.progress,
            "error": self.error,
            "result": self.result,
        }
        return rtnval
