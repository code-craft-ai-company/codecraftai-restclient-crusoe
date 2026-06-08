# Design

## Overview

`CrusoeClient` is a `RestClientBase` subclass for `api.crusoecloud.com`.
The shape is AWS-like: project → VPC → subnet → security group → VM/disk,
with placement groups carrying the IB interconnect dimension that makes
Crusoe interesting for HPC workloads. Async operations return typed
`CrusoeTaskHandle` instances.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  codecraftai-provisioning / venues / crusoe               │
└──────────┬─────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  CrusoeClient                                          │
│   RestClientBase + AspectsRest                         │
│   API groups: vpcs, subnets, security-groups,          │
│     ssh-keys, disks, placement-groups, vms, images,    │
│     tags, operations                                   │
└──────────┬─────────────────────────────────────────────┘
           │ HTTPS, HMAC-signed
           ▼
┌────────────────────────────────────────────────────────┐
│  api.crusoecloud.com                                   │
└────────────────────────────────────────────────────────┘
```

---

## Data Model

`model/`: `crusoevpc.py`, `crusoesubnet.py`, `crusoesecuritygroup.py`,
`crusoesshkey.py`, `crusoedisk.py`, `crusoeplacementgroup.py`, `crusoevm.py`,
`crusoeimage.py`, `crusoeoperationresult.py`, `crusoetaskhandle.py`.

`specs/`: `crusoevpcspec.py`, `crusoesubnetspec.py`,
`crusoesecuritygroupspec.py`, `crusoediskspec.py`,
`crusoeplacementgroupspec.py`, `crusoevmlaunchspec.py`.

Exceptions: `CrusoeAuthenticationError`, `CrusoeCidrValidationError`,
`CrusoePlacementMismatchError`.

---

## Module Layout

```
source/packages/ccai/restclient/crusoe/
├── crusoeclient.py
├── aspectscrusoe.py
├── apigroups/{vpcsgroup, subnetsgroup, securitygroupsgroup, sshkeysgroup,
│              disksgroup, placementgroupsgroup, vmsgroup, imagesgroup,
│              tagsgroup, operationsgroup}.py
├── model/
├── specs/
└── exceptions/
```

---

## See Also

- `codecraftai-restclient-base/specs/restapigroup-enhancements/`
- `codecraftai-restclient-base/specs/task-handle-base/`
- `codecraftai-provisioning/specs/venue-crusoe/`
- `codecraftai-credentials/specs/crusoe-credentials/`

---

## Testing Strategy

Example-based tests cover authentication, idempotent VPC/subnet/SG/SSH
key/placement-group creation, VM launch happy path, and HTTP-error
reclassification.

Property-based tests (hypothesis) are **required** for:
1. **Paging cursor traversal** for every `list_*` endpoint.
2. **URL composition** — per-segment percent-encoding, empty/`None` rejection.
3. **Idempotent retry semantics** within and beyond budget.
4. **CIDR containment** — for any randomly-generated VPC CIDR and
   subnet CIDR pair, `create_subnet` rejects with `CrusoeCidrValidationError`
   iff the subnet is not contained in the VPC.
5. **`CrusoeTaskHandle.wait`** termination correctness against arbitrary
   monotonic mock status streams.
