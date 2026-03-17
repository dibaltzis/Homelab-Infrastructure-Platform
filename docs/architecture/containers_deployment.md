[← Back to README](../../README.md#platform-subsystems)

# Container Deployment Pipeline

After stack infrastructure is prepared, containers are deployed and reconciled through a staged deployment pipeline.  
Each enabled stack is validated, deployed, and optionally post-configured to ensure services reach their desired state.

<div style="display:flex; justify-content:center;">

<pre style="text-align:left;">
     List of enabled stacks
        (containers_active)
               │
               ▼
        Preflight Checks
           (checks.yml)
               │
               ▼
       For each &lt;stack&gt;
               │
               ▼
  ┌──────────────────────────┐
  │   Reconcile Stack Infra  │
  │     stacks/&lt;stack&gt;/      │
  │      infra_config.yml    │
  └─────────────┬────────────┘
                │
                ▼
        Deploy Containers
        docker compose up
                │
                ▼
  ┌──────────────────────────┐
  │    Post Configure Stack  │
  │     stacks/&lt;stack&gt;/      │
  │      post_config.yml     │
  └──────────────────────────┘
</pre>

</div>

This pipeline ensures that stack infrastructure, container deployment, and post-deployment configuration are applied consistently across all services.

- Detailed implementation notes are available in [docs/roles/containers_role](../roles/containers_deployment_role.md)