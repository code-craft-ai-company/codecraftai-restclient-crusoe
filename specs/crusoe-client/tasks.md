# Implementation Plan — Crusoe Client

## Package Skeleton

- [x] 1. Create `source/packages/automojo/restclient/crusoe/` package tree.
- [x] 2. Add `aspectscrusoe.py` with `DEFAULT_CRUSOE_ASPECTS`.

## Client Core

- [x] 3. Implement `CrusoeClient(RestClientBase)` with HMAC-signed request auth.
- [x] 4. Implement URL composition helper.
- [x] 5. Implement HTTP-error reclassification into typed exceptions.

## Data Model & Specs

- [x] 6. Implement model dataclasses for VPC, subnet, SG, SSH key, disk, placement group, VM, image, operation result.
- [x] 7. Implement spec dataclasses for VPC/subnet/SG/disk/placement-group/VM-launch.
- [x] 8. Implement `CrusoeTaskHandle` against `ITaskHandle`.

## API Groups

- [x] 9. Implement `VpcsGroup` (create/list/delete) with idempotent create.
- [x] 10. Implement `SubnetsGroup` (create/list/delete) with CIDR-containment validation.
- [x] 11. Implement `SecurityGroupsGroup` (create/list/delete + set-rules).
- [x] 12. Implement `SshKeysGroup` (register/list/delete) with idempotency.
- [x] 13. Implement `DisksGroup` (create/attach/detach/delete) with task handles.
- [x] 14. Implement `PlacementGroupsGroup` (create/list/delete) supporting IB interconnect.
- [x] 15. Implement `VmsGroup` (launch/get/list/power-on/power-off/terminate) with placement-mismatch validation.
- [x] 16. Implement `ImagesGroup.list`.
- [x] 17. Implement `TagsGroup.apply`.
- [x] 18. Implement `OperationsGroup.get` consumed by `CrusoeTaskHandle.wait`.

## Paging

- [x] 19. Transparent cursor traversal for every `list_*`.

## Tests — Example-Based

- [x] 20. Construction tests.
- [x] 21. Idempotent create tests for VPC, SG, SSH key, placement group.
- [x] 22. VM launch happy path.
- [x] 23. HTTP-error reclassification tests.

## Tests — Property-Based (hypothesis)

- [x] 24. Paging traversal totality.
- [x] 25. URL composition determinism + per-segment encoding + rejection.
- [x] 26. Idempotent-retry equivalence.
- [x] 27. CIDR containment correctness for subnet vs VPC.
- [x] 28. `CrusoeTaskHandle.wait` terminal-state correctness.

## Integration

- [ ] 29. Smoke-test fixture for live Crusoe API.
