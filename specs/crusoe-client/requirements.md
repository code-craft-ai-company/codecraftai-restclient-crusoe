# Requirements

## Introduction

The `crusoe-client` feature provides a REST client for Crusoe Cloud's
`api.crusoecloud.com`. Crusoe is AWS-shaped (VPC/subnet/SG/VM/disk) with
first-class InfiniBand placement groups for multi-node GPU training. This
client exposes those primitives so the `venue-crusoe` provisioner in
`automojo-provisioning` can implement the neutral lifecycle.

Transport is REST on `RestClientBase`. Authentication uses
`CrusoeApiKeyCredential` (access key id + secret). Every behaviour-bearing
method accepts `aspects: AspectsRest = DEFAULT_CRUSOE_ASPECTS`.

---

## Requirements

### Requirement 1: Authenticate Against the Crusoe API

**User Story:** As a provisioner, I want to authenticate with a typed
credential.

#### Acceptance Criteria

1. WHEN the client is constructed with a `CrusoeApiKeyCredential` THE
   SYSTEM SHALL configure `RestClientBase` with HMAC-signed request
   authentication sourced from the credential.
2. WHEN the credential is missing the access key id or secret THE SYSTEM
   SHALL raise `ConfigurationError`.
3. WHEN HTTP 401/403 is returned THE SYSTEM SHALL reclassify into
   `CrusoeAuthenticationError`.

### Requirement 2: Manage VPCs and Subnets

**User Story:** As a provisioner, I want to create, list, and delete VPCs
and subnets idempotently.

#### Acceptance Criteria

1. WHEN the caller invokes `create_vpc(spec, aspects)` THE SYSTEM SHALL
   POST the request and return a `CrusoeVpc` record.
2. WHEN a VPC with the same name in the same project already exists THE
   SYSTEM SHALL return the existing record.
3. WHEN the caller invokes `list_vpcs(project_id, aspects)` and `list_subnets(vpc_id, aspects)` THE SYSTEM SHALL follow paging cursors transparently.
4. WHEN the caller invokes `create_subnet(spec, aspects)` and the subnet
   CIDR is not contained within the VPC CIDR THE SYSTEM SHALL raise
   `CrusoeCidrValidationError` before issuing the request.
5. WHEN the caller invokes `delete_vpc(vpc_id, aspects)` or
   `delete_subnet(subnet_id, aspects)` against an unknown id THE SYSTEM
   SHALL succeed as a no-op.

### Requirement 3: Manage Security Groups

**User Story:** As a provisioner, I want to manage security groups and
their ingress/egress rules.

#### Acceptance Criteria

1. WHEN the caller invokes `create_security_group(spec, aspects)` THE
   SYSTEM SHALL POST the request and return a `CrusoeSecurityGroup`.
2. WHEN a security group with the same name in the same VPC already
   exists THE SYSTEM SHALL return the existing record.
3. WHEN the caller invokes `set_security_group_rules(sg_id, ingress, egress, aspects)`
   THE SYSTEM SHALL replace the rule set with the supplied lists.
4. WHEN `delete_security_group(sg_id, aspects)` is called against an
   unknown id THE SYSTEM SHALL succeed as a no-op.

### Requirement 4: Manage SSH Keys

**User Story:** As a provisioner, I want to register and delete SSH keys.

#### Acceptance Criteria

1. WHEN the caller invokes `register_ssh_key(name, public_key, aspects)`
   THE SYSTEM SHALL POST and return `CrusoeSshKey`.
2. WHEN a key with the same name exists THE SYSTEM SHALL return the
   existing record.
3. WHEN `delete_ssh_key(key_id, aspects)` is called against an unknown
   id THE SYSTEM SHALL succeed as a no-op.

### Requirement 5: Manage Disks

**User Story:** As a provisioner, I want to create, attach, detach, and
delete disks.

#### Acceptance Criteria

1. WHEN the caller invokes `create_disk(spec, aspects)` THE SYSTEM SHALL
   return a `CrusoeDisk` record and a `CrusoeTaskHandle` when the create
   is async.
2. WHEN the caller invokes `attach_disk(disk_id, instance_id, aspects)`
   or `detach_disk(disk_id, instance_id, aspects)` THE SYSTEM SHALL POST
   the request and return a `CrusoeTaskHandle`.
3. WHEN `delete_disk(disk_id, aspects)` is called against an unknown id
   THE SYSTEM SHALL succeed as a no-op.

### Requirement 6: Manage IB-Enabled Placement Groups

**User Story:** As a provisioner planning a multi-node training job, I
want to create InfiniBand-enabled placement groups so that nodes are
co-located on the right fabric.

#### Acceptance Criteria

1. WHEN the caller invokes `create_placement_group(spec, aspects)` with
   `interconnect="infiniband"` THE SYSTEM SHALL POST the request and
   return a `CrusoePlacementGroup`.
2. WHEN a placement group with the same name already exists THE SYSTEM
   SHALL return the existing record.
3. WHEN `delete_placement_group(group_id, aspects)` is called against
   an unknown id THE SYSTEM SHALL succeed as a no-op.

### Requirement 7: Launch and Manage Virtual Machines

**User Story:** As a provisioner, I want to launch, inspect, list,
power-cycle, and terminate VMs.

#### Acceptance Criteria

1. WHEN the caller invokes `launch_vm(spec, aspects)` THE SYSTEM SHALL
   POST the request and return both a `CrusoeVm` record and a
   `CrusoeTaskHandle` for the create operation.
2. WHEN the spec references a placement group with a different
   interconnect than the requested instance type supports THE SYSTEM
   SHALL raise `CrusoePlacementMismatchError` before issuing the request.
3. WHEN the caller invokes `get_vm(vm_id, aspects)`, `list_vms(project_id, aspects)`,
   `power_on_vm(vm_id, aspects)`, `power_off_vm(vm_id, aspects)`, or
   `terminate_vm(vm_id, aspects)` THE SYSTEM SHALL POST/GET as appropriate.
4. WHEN `terminate_vm` is called against an already-terminated id THE
   SYSTEM SHALL succeed as a no-op.

### Requirement 8: Image Lookup

**User Story:** As a provisioner resolving a neutral `CloudImage`, I want
to enumerate available images.

#### Acceptance Criteria

1. WHEN the caller invokes `list_images(aspects)` THE SYSTEM SHALL return
   `CrusoeImage` records with name, family, version, architecture.

### Requirement 9: Tagging

**User Story:** As a provisioner, I want to attach key/value tags to
resources.

#### Acceptance Criteria

1. WHEN the caller invokes `apply_tags(resource_type, resource_id, tags, aspects)`
   THE SYSTEM SHALL PATCH the resource with the supplied tag set.
2. THE SYSTEM SHALL accept tags as `List[Dict[str, str]]` and translate to
   Crusoe's payload shape internally.

### Requirement 10: Long-Running Task Handles

**User Story:** As a provisioner, I want async operations to return typed
task handles.

#### Acceptance Criteria

1. WHEN an API call returns an operation id THE SYSTEM SHALL return a
   `CrusoeTaskHandle` implementing `ITaskHandle`.
2. WHEN `handle.wait(aspects)` is invoked THE SYSTEM SHALL poll per
   aspects and SHALL raise `TimeoutError` when the budget elapses.

### Requirement 11: URL Composition for Nested Resources

#### Acceptance Criteria

1. WHEN composing nested URLs THE SYSTEM SHALL percent-encode each
   segment independently.
2. WHEN any identifier is empty or `None` THE SYSTEM SHALL raise
   `SemanticError`.

### Requirement 12: Aspects on Every Behaviour-Bearing Call

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsRest = DEFAULT_CRUSOE_ASPECTS`
   as a named-only parameter on every I/O method.
2. THE SYSTEM SHALL never apply behaviour-modifying decorators.
