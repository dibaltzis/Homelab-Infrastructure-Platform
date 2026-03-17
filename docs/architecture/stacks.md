[← Back to README](../../README.md#platform-subsystems)

# Stack Infrastructure

Service workloads are organized into independent container stacks.  
Each enabled stack is validated, prepared, and rendered through a reusable orchestration role before containers are deployed.

<div style="display:flex; justify-content:center;">

<pre style="text-align:left;">
 containers_active
 (enabled stacks)
        │
        ▼
 Validate & Prepare
 ┌────────────────────────┐
 │ ensure_stacks_vars.yml │
 │ create shared networks │
 │ validate stack exists  │
 └───────────┬────────────┘
             │
             ▼
        roles/stacks/
             │
   ┌─────────┼───────────────┬─────────┬───── ...
   ▼         ▼               ▼
 ingress   monitor        database
   │         │               │
 tasks/    tasks/          tasks/
 templates templates       templates
 handlers  handlers
 files     files
             │
             ▼
        Load stack role
        stacks/<stack>
             │
             ▼
        stack_setup.yml
             │
      ┌──────┼──────────────┐
      ▼      ▼              ▼
    dirs  templates        files
             │
             ▼
          Stack ready
     (containers deploy)
</pre>

</div>

This structure allows service stacks to share the same deployment framework while keeping their configuration and templates isolated.

- Detailed implementation notes are available in [docs/roles/stacks_role](../roles/stacks_role.md)