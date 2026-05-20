=========================================
Automation Mojo Interop - Crusoe Cloud
=========================================

The ``automojo-interop-crusoe`` package is the venue-specific REST client for Crusoe
Cloud, a GPU-first cloud whose API at ``api.crusoecloud.com`` is closely AWS-shaped: VPCs,
subnets, security groups, virtual machines, disks, and InfiniBand-enabled placement
groups. Crusoe's relatively conventional shape makes it the simplest cloud-shaped AI venue
to slot into the neutral ``CloudProvisioner`` model defined in ``automojo-provisioning``.

Highlights
==========

- ``CrusoeClient`` — a ``RestClientBase`` subclass covering compute, networking, storage, SSH-key, and image lookups.
- InfiniBand placement groups — the placement-group primitive that makes Crusoe interesting for multi-node training.
- Typed task handles — long-running operations (instance create, disk attach, snapshot) return typed task handles so the provisioner's verify stage can wait on them with caller-controlled aspects.
- Neutral provisioning model — exercises the ``CloudAcceleratorSpec`` + ``CloudInterconnect`` extensions defined in §7.1 of the design plan.
- Aspects-driven transport — every behaviour-bearing call accepts ``aspects: AspectsRest = DEFAULT_CRUSOE_ASPECTS``; credentials enter as typed ``CrusoeApiKeyCredential`` instances from ``automojo-credentials``.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/automojo/interop/crusoe/`` - Package source code.
- ``source/testroots/testbase/automojo/tests/interop/crusoe/`` - TestBase test roots.
- ``specs/`` - Requirements, design, and task documentation (Kiro-style).
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-environment

Running Tests
=============

.. code-block:: bash

   source .venv/bin/activate
   PYTHONPATH=source/packages:source/testroots/testbase python -m pytest source/testroots -q

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
