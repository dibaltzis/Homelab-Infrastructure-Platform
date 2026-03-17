[← Back to README](../../README.md#documentation) 
# Secrets Backend Role

> Provider-agnostic secret abstraction layer for Ansible infrastructure.

The `secrets_backend` role decouples infrastructure orchestration from the secret storage backend by exposing a single unified runtime interface:

```
secrets
```

All other roles consume secrets exclusively from this dictionary.  
They do not depend on provider type, authentication method, CLI tooling, or retrieval logic.

This establishes a stable abstraction boundary and allows secret providers to be replaced without modifying:

- Stack roles
- Service roles
- Inventory structure
- Playbooks


## Table of Contents

- [Architectural Intent](#architectural-intent)
- [Design Principles](#design-principles)
- [Execution Model](#execution-model)
- [Execution Flow](#execution-flow)
- [Required Variables](#required-variables)
- [Bitwarden (bws) Backend](#bitwarden-bws-backend)
- [Connection Validation](#connection-validation)
- [Secret Namespace Model](#secret-namespace-model)
- [Runtime Output](#runtime-output)
- [Repository Cleanliness Model](#repository-cleanliness-model)

# Architectural Intent

The role enforces strict separation between:

- Infrastructure orchestration
- Secret provider implementation

Backend selection is dynamic and controlled via:

```
secrets_service
```

Provider logic is isolated inside:

```
roles/secrets_backend/tasks/<provider>/
```

Adding a new provider requires only:

- Implementing `check.yml`, `install.yml`, and `fetch.yml`
- Selecting it via `secrets_service`

No consuming role requires changes.


# Design Principles

- Provider-agnostic consumption model
- Dynamic backend selection
- Runtime secret injection
- Controller-side retrieval
- Externalized credential handling
- Explicit validation contract


# Execution Model

The role executes on:

```
localhost (Ansible controller)
```

Using:

- `delegate_to: localhost`
- `run_once: true`

Secrets are retrieved on the controller and injected as runtime facts.  
No secret retrieval occurs on managed hosts.


# Execution Flow

```
Select backend
        │
        ▼
Check client availability
        │
        ▼
Install backend client (if needed)
        │
        ▼
Initialize empty secrets dictionary
        │
        ▼
Fetch secrets
        │
        ▼
Validate connection-check secret
```


# Required Variables

Defined in:

```
inventories/<env>/group_vars/all/trust/secrets_backend.yml
```

| Variable | Purpose |
|----------|----------|
| `secrets_service` | Select backend implementation |
| `bws_version` | Required CLI version |
| `bws_install_path` | CLI installation path |
| `secrets_prefix` | Secret namespace filter prefix |

Backend credentials are loaded dynamically from an external file excluded via `.gitignore`:

```
bws_credentials.yml
```

Example:

```yaml
bws_project_id: "uuid"
bws_access_token: "token_value"
```

Runtime injection:

```yaml
bws_credentials: "{{ lookup('file', playbook_dir ~ '/../bws_credentials.yml') | from_yaml }}"

bws_project_id: "{{ bws_credentials.bws_project_id }}"
BWS_ACCESS_TOKEN: "{{ bws_credentials.bws_access_token }}"
```

No credential material exists inside the repository.


# Bitwarden (bws) Backend

Current implementation:

```
bws (Bitwarden Secrets Manager CLI)
```

Located in:

```
roles/secrets_backend/tasks/bws/
```

### Phases

**check.yml**
- Verify CLI presence at `bws_install_path`
- Validate version
- Set `secrets_backend_client_installed` boolean flag

**install.yml**
- Detect system architecture
- Download correct release
- Install binary
- Verify version

**fetch.yml**
- List project secrets
- Filter by `secrets_prefix`
- Strip prefix
- Build runtime `secrets` dictionary

All sensitive operations use `no_log: true`.


# Connection Validation

The role enforces a strict validation contract:

```
'connection-check' in secrets
secrets['connection-check'] == "it_works"
```

Failure aborts execution.

This guarantees:

- Backend connectivity
- Valid authentication
- Correct project selection
- Proper prefix filtering
- Successful dictionary construction


# Secret Namespace Model

Secrets follow a structured path-like format.

Example:

```
ansible/stacks_envs/dev/gitea/database/name
```

Structure:

| Segment | Meaning |
|----------|----------|
| `ansible` | Automation namespace |
| `stacks_envs` | Variable domain |
| `dev` | Environment |
| `gitea` | Service |
| `database` | Component |
| `name` | Attribute |

A reference list of all secret keys currently used by the infrastructure is maintained in `docs/secrets_schema.txt`.

> This file contains only secret paths (no values) and serves as documentation of the secret namespace as well as a migration aid when changing secret backends.

Only secrets matching `secrets_prefix` are imported.

After filtering, the prefix is removed.

Bitwarden key:

```
ansible/stacks_envs/dev/gitea/database/name
```

Runtime key:

```
stacks_envs/dev/gitea/database/name
```

This prevents backend-specific naming from leaking into infrastructure logic.


# Runtime Output

After execution, a global fact is available:

```
secrets:
  stacks_envs/dev/gitea/database/name: ...
  stacks_envs/dev/gitea/database/user: ...
  stacks_envs/dev/gitea/database/password: ...
```

Example usage:

```
GITEA_DB_NAME: "{{ secrets['stacks_envs/dev/gitea/database/name'] }}"
```

# Repository Cleanliness Model

- No secret values exist in the repository
- Backend credentials are externalized
- `.gitignore` prevents accidental commits
- Backend authentication remains outside version control

The role provides a stable, extensible secret abstraction layer while keeping infrastructure logic provider-independent.