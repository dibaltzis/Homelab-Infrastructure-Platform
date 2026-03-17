[← Back to README](../../README.md#platform-subsystems)

# Ingress Architecture

External access to services is defined declaratively through `ingress_services`.  
Each service definition provides the metadata required to generate reverse proxy routes, authentication policies, and dashboard entries.

`ingress_services` acts as the single source of truth for all externally exposed services.

---

## Example Service Definitions

```yaml
ingress_services:

  authelia:
    host_prefix: auth
    upstream: authelia
    port: 9091
    requires_auth: false
    dashboard:
      show: false

  gitea:
    host_prefix: gitea
    upstream: gitea
    port: 3000
    requires_auth: true
    dashboard:
      show: true
      category: dev
      icon: https://cdn.simpleicons.org/gitea
```

The service metadata is then used to generate the ingress infrastructure automatically.

<div style="display:flex; justify-content:center;">

<pre style="text-align:left;">
ingress_services
(service definitions)
        │
        ▼
Service Metadata
┌───────────────────────────┐
│ host_prefix               │
│ upstream                  │
│ port                      │
│ requires_auth             │
│ dashboard visibility      │
└───────────────┬───────────┘
                │
                ▼
        Template Rendering
     ┌──────────┼───────────┐
     ▼          ▼           ▼
nginx routes  auth rules  dashboard config
                │
                ▼
      Generated Infrastructure
     ┌──────────┼───────────┐
     ▼          ▼           ▼
reverse proxy  auth gateway  service dashboard
</pre>

</div>

This architecture allows ingress configuration to be defined once and automatically rendered into the reverse proxy, authentication gateway, and service dashboard.

## Generated Dashboard Example

The dashboard UI is automatically generated from the same `ingress_services` definitions used to configure the reverse proxy and authentication policies.

<p align="center">
  <img src="../images/dashboard.png" alt="Generated Service Dashboard" width="900">
</p>