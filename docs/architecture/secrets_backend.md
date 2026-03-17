[← Back to README](../../README.md#platform-subsystems)  
# Secrets Backend

Secrets are retrieved from an external provider through a provider-agnostic abstraction layer.

The selected backend dynamically populates a shared runtime dictionary (`secrets[]`) that is consumed by the rest of the infrastructure.  
Roles never interact directly with the secrets provider.

<div style="display:flex; justify-content:center;">

<pre style="text-align:left;">
          secrets_service
         (bws, vault, etc.)
               │
               ▼
 roles/secrets_backend/tasks/&lt;provider&gt;/
               │
      ┌────────┼─────────┐
      ▼        ▼         ▼
check.yml install.yml fetch.yml
      │        │         │
      └────────┴─────────┘
               │
               ▼
        Populate secrets[]
               │
               ▼
     Connection Validation
       "connection-check"
               │
               ▼
      secrets[] consumed by roles
</pre>

</div>

This abstraction allows secret providers to be replaced without modifying the infrastructure roles.

- Detailed implementation notes are available in [docs/roles/secrets-backend_role](../roles/secrets_backend_role.md)