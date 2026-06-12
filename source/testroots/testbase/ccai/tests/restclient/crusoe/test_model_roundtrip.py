"""
    .. module:: test_model_roundtrip
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Round-trip tests verifying that every hand-authored Crusoe
                   model record is reconstructed exactly by
                   ``from_dict(to_dict(x))``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai.restclient.crusoe.model.crusoevpc import CrusoeVpc
from ccai.restclient.crusoe.model.crusoedisk import CrusoeDisk
from ccai.restclient.crusoe.model.crusoesubnet import CrusoeSubnet
from ccai.restclient.crusoe.model.crusoesecuritygroup import (
    CrusoeSecurityGroup
)
from ccai.restclient.crusoe.model.crusoevm import CrusoeVm
from ccai.restclient.crusoe.model.crusoeimage import CrusoeImage
from ccai.restclient.crusoe.model.crusoeoperationresult import (
    CrusoeOperationResult
)
from ccai.restclient.crusoe.model.crusoeplacementgroup import (
    CrusoePlacementGroup
)
from ccai.restclient.crusoe.model.crusoesshkey import CrusoeSshKey


def test_vpc_roundtrip() -> None:
    """
        A populated :class:`CrusoeVpc` survives ``from_dict(to_dict(x))``.
    """
    original = CrusoeVpc(vpc_id="vpc-1", name="net", cidr="10.0.0.0/16",
                         project_id="proj-1", state="active",
                         labels={"env": "prod"})
    rebuilt = CrusoeVpc.from_dict(original.to_dict())

    assert rebuilt.vpc_id == original.vpc_id
    assert rebuilt.name == original.name
    assert rebuilt.cidr == original.cidr
    assert rebuilt.project_id == original.project_id
    assert rebuilt.state == original.state
    assert rebuilt.labels == original.labels
    return


def test_disk_roundtrip() -> None:
    """
        A populated :class:`CrusoeDisk` survives ``from_dict(to_dict(x))``.
    """
    original = CrusoeDisk(disk_id="disk-1", name="data", size_gib=512,
                          disk_type="persistent-ssd", location="us-east1-a",
                          state="ready", attached_to="vm-1",
                          labels={"tier": "hot"})
    rebuilt = CrusoeDisk.from_dict(original.to_dict())

    assert rebuilt.disk_id == original.disk_id
    assert rebuilt.name == original.name
    assert rebuilt.size_gib == original.size_gib
    assert rebuilt.disk_type == original.disk_type
    assert rebuilt.location == original.location
    assert rebuilt.state == original.state
    assert rebuilt.attached_to == original.attached_to
    assert rebuilt.labels == original.labels
    return


def test_subnet_roundtrip() -> None:
    """
        A populated :class:`CrusoeSubnet` survives ``from_dict(to_dict(x))``.
    """
    original = CrusoeSubnet(subnet_id="sub-1", name="web",
                            cidr="10.0.1.0/24", vpc_id="vpc-1",
                            location="us-east1-a", state="active",
                            labels={"zone": "a"})
    rebuilt = CrusoeSubnet.from_dict(original.to_dict())

    assert rebuilt.subnet_id == original.subnet_id
    assert rebuilt.name == original.name
    assert rebuilt.cidr == original.cidr
    assert rebuilt.vpc_id == original.vpc_id
    assert rebuilt.location == original.location
    assert rebuilt.state == original.state
    assert rebuilt.labels == original.labels
    return


def test_security_group_roundtrip() -> None:
    """
        A populated :class:`CrusoeSecurityGroup` survives the round trip.
    """
    original = CrusoeSecurityGroup(security_group_id="sg-1", name="default",
                                   vpc_id="vpc-1",
                                   ingress_rules=[{"port": 22}],
                                   egress_rules=[{"port": 443}],
                                   state="active", labels={"role": "edge"})
    rebuilt = CrusoeSecurityGroup.from_dict(original.to_dict())

    assert rebuilt.security_group_id == original.security_group_id
    assert rebuilt.name == original.name
    assert rebuilt.vpc_id == original.vpc_id
    assert rebuilt.ingress_rules == original.ingress_rules
    assert rebuilt.egress_rules == original.egress_rules
    assert rebuilt.state == original.state
    assert rebuilt.labels == original.labels
    return


def test_vm_roundtrip() -> None:
    """
        A populated :class:`CrusoeVm` survives ``from_dict(to_dict(x))``.
    """
    original = CrusoeVm(vm_id="vm-1", name="worker",
                        instance_type="a100.8x", location="us-east1-a",
                        state="running", project_id="proj-1",
                        subnet_id="sub-1", placement_group_id="ibp-1",
                        network_interfaces=[{"name": "eth0"}],
                        labels={"app": "train"})
    rebuilt = CrusoeVm.from_dict(original.to_dict())

    assert rebuilt.vm_id == original.vm_id
    assert rebuilt.name == original.name
    assert rebuilt.instance_type == original.instance_type
    assert rebuilt.location == original.location
    assert rebuilt.state == original.state
    assert rebuilt.project_id == original.project_id
    assert rebuilt.subnet_id == original.subnet_id
    assert rebuilt.placement_group_id == original.placement_group_id
    assert rebuilt.network_interfaces == original.network_interfaces
    assert rebuilt.labels == original.labels
    return


def test_image_roundtrip() -> None:
    """
        A populated :class:`CrusoeImage` survives ``from_dict(to_dict(x))``.
    """
    original = CrusoeImage(image_id="img-1", name="ubuntu-22.04",
                           family="ubuntu", version="22.04",
                           architecture="x86_64")
    rebuilt = CrusoeImage.from_dict(original.to_dict())

    assert rebuilt.image_id == original.image_id
    assert rebuilt.name == original.name
    assert rebuilt.family == original.family
    assert rebuilt.version == original.version
    assert rebuilt.architecture == original.architecture
    return


def test_operation_result_roundtrip() -> None:
    """
        A populated :class:`CrusoeOperationResult` survives the round trip.
    """
    original = CrusoeOperationResult(operation_id="op-1", state="succeeded",
                                     progress=100, error=None,
                                     result={"id": "vm-1"})
    rebuilt = CrusoeOperationResult.from_dict(original.to_dict())

    assert rebuilt.operation_id == original.operation_id
    assert rebuilt.state == original.state
    assert rebuilt.progress == original.progress
    assert rebuilt.error == original.error
    assert rebuilt.result == original.result
    return


def test_placement_group_roundtrip() -> None:
    """
        A populated :class:`CrusoePlacementGroup` survives the round trip.
    """
    original = CrusoePlacementGroup(placement_group_id="ibp-1",
                                    name="fabric", interconnect="infiniband",
                                    project_id="proj-1", state="active",
                                    labels={"job": "llm"})
    rebuilt = CrusoePlacementGroup.from_dict(original.to_dict())

    assert rebuilt.placement_group_id == original.placement_group_id
    assert rebuilt.name == original.name
    assert rebuilt.interconnect == original.interconnect
    assert rebuilt.project_id == original.project_id
    assert rebuilt.state == original.state
    assert rebuilt.labels == original.labels
    return


def test_ssh_key_roundtrip() -> None:
    """
        A populated :class:`CrusoeSshKey` survives ``from_dict(to_dict(x))``.
    """
    original = CrusoeSshKey(ssh_key_id="key-1", name="laptop",
                            public_key="ssh-ed25519 AAAA...",
                            project_id="proj-1")
    rebuilt = CrusoeSshKey.from_dict(original.to_dict())

    assert rebuilt.ssh_key_id == original.ssh_key_id
    assert rebuilt.name == original.name
    assert rebuilt.public_key == original.public_key
    assert rebuilt.project_id == original.project_id
    return
