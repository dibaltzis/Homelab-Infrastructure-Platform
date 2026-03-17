[← Back to README](../../README.md#platform-subsystems)

# Backup & Restore

The platform implements automated backup and restore pipelines using rclone.  
The workflow is structured as mirrored stages to ensure predictable data protection and recovery.

<div style="display:flex; justify-content:center;">

<pre style="text-align:left;">
+-------------------------------+    +-------------------------------+
|            BACKUP             |    |            RESTORE            |
+-------------------------------+    +-------------------------------+
|   Initialize Backup Context   |    |  Initialize Restore Context   |
|               │               |    |               │               |
|               ▼               |    |               ▼               |
|       Pre Hooks (optional)    |    |       Pre Hooks (optional)    |
|               │               |    |               │               |
|               ▼               |    |               ▼               |
|        Archive Creation       |    |    Force Restore (optional)   |
|               │               |    |               │               |
|               ▼               |    |               ▼               |
|      Encryption (optional)    |    |   Check restore_done Marker   |
|               │               |    |               │               |
|               ▼               |    |               ▼               |
|   Upload Artifact (rclone)    |    |   Download Artifact (rclone)  |
|               │               |    |               │               |
|               ▼               |    |               ▼               |
|      Upload Verification      |    |    Download Verification      |
|               │               |    |               │               |
|               ▼               |    |               ▼               |
|   Retention Policy (optional) |    |  Decrypt Artifact (optional)  |
|               │               |    |               │               |
|               ▼               |    |               ▼               |
|           Post Hooks          |    | Unarchive Artifact (optional) |
|                               |    |               │               |
|                               |    |               ▼               |
|                               |    |         Cleanup Stage         |
|                               |    |               │               |
|                               |    |               ▼               |
|                               |    |           Post Hooks          |
+-------------------------------+    +-------------------------------+
</pre>

</div>

The mirrored design ensures that backup artifacts can be restored through the same staged pipeline used to create them.

- Detailed implementation notes: [Back & Restore rclone role ](../roles/rclone_role.md)