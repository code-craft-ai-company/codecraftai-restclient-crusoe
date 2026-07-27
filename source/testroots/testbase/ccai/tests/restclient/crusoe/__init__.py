"""
    Originates the Crusoe client test resources into this scope.

    Both are plain constructions that accumulate no state across tests, so
    package-scope origination is appropriate and sharing them is free. A
    resource that a test mutates would instead be attached to the test case.

    The credential is originated BEFORE the client: resources are created in
    the order they are originated, and the client's factory consumes the
    credential.
"""

from ccai import testbase

from ccai.tests.restclient.crusoe.factories import (
    create_crusoe_credential,
    create_crusoe_client
)

testbase.originate.parameter(create_crusoe_credential,
                             identifier="crusoe_credential")
testbase.originate.parameter(create_crusoe_client, identifier="crusoe_client")
