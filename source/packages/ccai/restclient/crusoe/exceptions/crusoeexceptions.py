"""
    .. module:: crusoeexceptions
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the typed exception classes raised by
                   the :class:`CrusoeClient` and its api groups.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


class CrusoeClientError(RuntimeError):
    """
        Base error type for every failure surfaced by the Crusoe client.
    """


class CrusoeAuthenticationError(CrusoeClientError):
    """
        Raised when the Crusoe API rejects a request with HTTP 401 or 403.
    """


class CrusoeCidrValidationError(CrusoeClientError):
    """
        Raised when a subnet CIDR is not contained within the parent VPC
        CIDR.  Raised before any request is issued.
    """


class CrusoePlacementMismatchError(CrusoeClientError):
    """
        Raised when a VM launch references a placement group whose
        interconnect does not match the requested instance type.  Raised
        before any request is issued.
    """


class CrusoeApiError(CrusoeClientError):
    """
        Raised when the Crusoe API returns a non-2xx, non-recoverable
        response that is not an authentication failure.
    """
