"""
    .. module:: test_apigroups
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Example-based tests for the Crusoe api groups — idempotent
                   create, VM launch, and HTTP-error reclassification.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import pytest
import requests_mock

from automojo.interop.crusoe.crusoeclient import CrusoeClient
from automojo.interop.crusoe.exceptions.crusoeexceptions import (
    CrusoeApiError, CrusoeAuthenticationError, CrusoeCidrValidationError,
    CrusoePlacementMismatchError
)
from automojo.interop.crusoe.specs.crusoeplacementgroupspec import (
    CrusoePlacementGroupSpec
)
from automojo.interop.crusoe.specs.crusoesecuritygroupspec import (
    CrusoeSecurityGroupSpec
)
from automojo.interop.crusoe.specs.crusoesubnetspec import CrusoeSubnetSpec
from automojo.interop.crusoe.specs.crusoevmlaunchspec import CrusoeVmLaunchSpec
from automojo.interop.crusoe.specs.crusoevpcspec import CrusoeVpcSpec


BASE = "https://api.crusoecloud.com/v1alpha5"


def test_create_vpc_idempotent(crusoe_client: CrusoeClient) -> None:
    """
        Creating a VPC twice with the same name returns the existing record
        the second time without a second POST.
    """
    with requests_mock.Mocker() as mock:
        mock.get("{}/projects/proj-1/vpcs".format(BASE),
                 json={"items": []})
        mock.post("{}/projects/proj-1/vpcs".format(BASE),
                  json={"id": "vpc-1", "name": "net-a",
                        "cidr_block": "10.0.0.0/16", "project_id": "proj-1"})
        spec = CrusoeVpcSpec(name="net-a", cidr="10.0.0.0/16",
                             project_id="proj-1")
        first = crusoe_client.vpcs.create(spec=spec)
        assert first.vpc_id == "vpc-1"

    with requests_mock.Mocker() as mock:
        mock.get("{}/projects/proj-1/vpcs".format(BASE),
                 json={"items": [{"id": "vpc-1", "name": "net-a",
                                  "cidr_block": "10.0.0.0/16",
                                  "project_id": "proj-1"}]})
        second = crusoe_client.vpcs.create(spec=spec)
        assert second.vpc_id == "vpc-1"
        post_calls = [r for r in mock.request_history if r.method == "POST"]
        assert len(post_calls) == 0
    return


def test_create_subnet_rejects_uncontained_cidr(
        crusoe_client: CrusoeClient) -> None:
    """
        A subnet CIDR outside the VPC CIDR is rejected before any request.
    """
    spec = CrusoeSubnetSpec(name="sn", cidr="192.168.0.0/24", vpc_id="vpc-1",
                            vpc_cidr="10.0.0.0/16", location="us-east1-a")
    with pytest.raises(CrusoeCidrValidationError):
        crusoe_client.subnets.create(spec=spec)
    return


def test_create_subnet_accepts_contained_cidr(
        crusoe_client: CrusoeClient) -> None:
    """
        A subnet CIDR contained in the VPC CIDR is created successfully.
    """
    with requests_mock.Mocker() as mock:
        mock.post("{}/vpcs/vpc-1/subnets".format(BASE),
                  json={"id": "sn-1", "name": "sn", "cidr_block": "10.0.1.0/24",
                        "vpc_id": "vpc-1"})
        spec = CrusoeSubnetSpec(name="sn", cidr="10.0.1.0/24", vpc_id="vpc-1",
                                vpc_cidr="10.0.0.0/16", location="us-east1-a")
        subnet = crusoe_client.subnets.create(spec=spec)
        assert subnet.subnet_id == "sn-1"
    return


def test_create_security_group_idempotent(
        crusoe_client: CrusoeClient) -> None:
    """
        Creating a security group whose name already exists returns the
        existing record.
    """
    with requests_mock.Mocker() as mock:
        mock.get("{}/vpcs/vpc-1/security-groups".format(BASE),
                 json={"items": [{"id": "sg-1", "name": "web",
                                  "vpc_id": "vpc-1"}]})
        spec = CrusoeSecurityGroupSpec(name="web", vpc_id="vpc-1")
        sg = crusoe_client.security_groups.create(spec=spec)
        assert sg.security_group_id == "sg-1"
        post_calls = [r for r in mock.request_history if r.method == "POST"]
        assert len(post_calls) == 0
    return


def test_set_security_group_rules(crusoe_client: CrusoeClient) -> None:
    """
        set_rules replaces the rule set and returns the updated record.
    """
    with requests_mock.Mocker() as mock:
        mock.patch("{}/vpcs/vpc-1/security-groups/sg-1".format(BASE),
                   json={"id": "sg-1", "name": "web", "vpc_id": "vpc-1",
                         "ingress_rules": [{"protocol": "tcp"}],
                         "egress_rules": []})
        result = crusoe_client.security_groups.set_rules(
            vpc_id="vpc-1", security_group_id="sg-1",
            ingress_rules=[{"protocol": "tcp"}], egress_rules=[])
        assert len(result.ingress_rules) == 1
    return


def test_register_ssh_key_idempotent(crusoe_client: CrusoeClient) -> None:
    """
        Registering an SSH key whose name exists returns the existing record.
    """
    with requests_mock.Mocker() as mock:
        mock.get("{}/projects/proj-1/ssh-keys".format(BASE),
                 json={"items": [{"id": "key-1", "name": "k",
                                  "public_key": "ssh-ed25519 AAAA"}]})
        key = crusoe_client.ssh_keys.register(project_id="proj-1", name="k",
                                              public_key="ssh-ed25519 AAAA")
        assert key.ssh_key_id == "key-1"
    return


def test_create_placement_group_idempotent(
        crusoe_client: CrusoeClient) -> None:
    """
        Creating an IB placement group whose name exists returns the existing
        record.
    """
    with requests_mock.Mocker() as mock:
        mock.get("{}/projects/proj-1/ib-partitions".format(BASE),
                 json={"items": [{"id": "ib-1", "name": "fabric",
                                  "interconnect": "infiniband"}]})
        spec = CrusoePlacementGroupSpec(name="fabric", project_id="proj-1")
        pg = crusoe_client.placement_groups.create(spec=spec)
        assert pg.placement_group_id == "ib-1"
        assert pg.interconnect == "infiniband"
    return


def test_launch_vm_happy_path(crusoe_client: CrusoeClient) -> None:
    """
        Launching a VM returns the record and an operation task handle.
    """
    with requests_mock.Mocker() as mock:
        mock.post("{}/projects/proj-1/instances".format(BASE),
                  json={"id": "vm-1", "name": "node-0", "type": "h100",
                        "operation": {"id": "op-1"}})
        spec = CrusoeVmLaunchSpec(name="node-0", instance_type="h100",
                                  location="us-east1-a", image_id="ubuntu-22",
                                  subnet_id="sn-1")
        vm, handle = crusoe_client.vms.launch(project_id="proj-1", spec=spec)
        assert vm.vm_id == "vm-1"
        assert handle is not None
        assert handle.task_id() == "op-1"
    return


def test_launch_vm_rejects_placement_mismatch(
        crusoe_client: CrusoeClient) -> None:
    """
        An IB placement group with a non-IB instance type is rejected before
        any request.
    """
    spec = CrusoeVmLaunchSpec(name="node-0", instance_type="c1.small",
                              location="us-east1-a", image_id="ubuntu-22",
                              subnet_id="sn-1",
                              placement_group_id="ib-1",
                              placement_group_interconnect="infiniband",
                              instance_type_supports_ib=False)
    with pytest.raises(CrusoePlacementMismatchError):
        crusoe_client.vms.launch(project_id="proj-1", spec=spec)
    return


def test_terminate_vm_noop_on_404(crusoe_client: CrusoeClient) -> None:
    """
        Terminating an already-terminated VM succeeds as a no-op.
    """
    with requests_mock.Mocker() as mock:
        mock.delete("{}/projects/proj-1/instances/vm-x".format(BASE),
                    status_code=404)
        handle = crusoe_client.vms.terminate(project_id="proj-1",
                                             vm_id="vm-x")
        assert handle is None
    return


def test_http_401_reclassified(crusoe_client: CrusoeClient) -> None:
    """
        An HTTP 401 reclassifies into CrusoeAuthenticationError.
    """
    with requests_mock.Mocker() as mock:
        mock.get("{}/projects/proj-1/vpcs".format(BASE),
                 status_code=401, text="unauthorized")
        with pytest.raises(CrusoeAuthenticationError):
            crusoe_client.vpcs.list(project_id="proj-1")
    return


def test_http_500_reclassified(crusoe_client: CrusoeClient) -> None:
    """
        An HTTP 500 reclassifies into CrusoeApiError.
    """
    with requests_mock.Mocker() as mock:
        mock.get("{}/projects/proj-1/vpcs".format(BASE),
                 status_code=500, text="boom")
        with pytest.raises(CrusoeApiError):
            crusoe_client.vpcs.list(project_id="proj-1")
    return


def test_delete_vpc_noop_on_404(crusoe_client: CrusoeClient) -> None:
    """
        Deleting an unknown VPC id succeeds as a no-op.
    """
    with requests_mock.Mocker() as mock:
        mock.delete("{}/projects/proj-1/vpcs/vpc-x".format(BASE),
                    status_code=404)
        crusoe_client.vpcs.delete(project_id="proj-1", vpc_id="vpc-x")
    return


def test_list_images(crusoe_client: CrusoeClient) -> None:
    """
        list_images returns CrusoeImage records with family + architecture.
    """
    with requests_mock.Mocker() as mock:
        mock.get("{}/projects/proj-1/images".format(BASE),
                 json={"items": [{"id": "ubuntu-22", "name": "Ubuntu 22.04",
                                  "family": "ubuntu", "version": "22.04",
                                  "architecture": "x86_64"}]})
        images = crusoe_client.images.list(project_id="proj-1")
        assert len(images) == 1
        assert images[0].family == "ubuntu"
    return


def test_apply_tags(crusoe_client: CrusoeClient) -> None:
    """
        apply_tags PATCHes a labels dict translated from the neutral tags.
    """
    with requests_mock.Mocker() as mock:
        mock.patch("{}/projects/proj-1/vpcs/vpc-1".format(BASE), json={})
        crusoe_client.tags.apply(project_id="proj-1", resource_type="vpc",
                                 resource_id="vpc-1",
                                 tags=[{"automojo-run-id": "r1"}])
        body = mock.request_history[0].json()
        assert body["labels"]["automojo-run-id"] == "r1"
    return
