# truenas-mcp

MCP server (stdio) for the TrueNAS WebSocket JSON-RPC API. Provides tools for managing pools, VMs, applications, users, filesystems, disks, system configuration, sharing (SMB/NFS), and more.

## Installation

```bash
docker run -i --rm \
  -e TRUENAS_URL=wss://nas.example.com/api/current \
  -e TRUENAS_API_KEY=your-api-key \
  ghcr.io/jakeperalta7/truenas-mcp:latest
```

Or build locally:

```bash
docker build -t truenas-mcp .
docker run -i --rm \
  -e TRUENAS_URL=wss://nas.example.com/api/current \
  -e TRUENAS_API_KEY=your-api-key \
  truenas-mcp
```

## Configuration

Configure via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TRUENAS_URL` | Yes* | - | WebSocket URL (e.g., `wss://nas.example.com/api/current`) |
| `TRUENAS_API_KEY` | Yes* | - | API key string or path to key file |
| `TRUENAS_USERNAME` | No | - | Username for API key auth (TrueNAS 26+) |
| `TRUENAS_VERIFY_SSL` | No | `true` | Verify SSL certificates |
| `TRUENAS_TIMEOUT` | No | `30.0` | Request timeout in seconds |
| `TRUENAS_READ_ONLY` | No | `false` | Disable write tools |
| `TRUENAS_LOCAL` | No | `false` | Connect to local Unix socket (no auth) |

*Either `TRUENAS_URL` + `TRUENAS_API_KEY` OR `TRUENAS_LOCAL=true` required.

### Local Connection (Running on TrueNAS)

When running on the TrueNAS host itself, use the local Unix socket:

```bash
TRUENAS_LOCAL=true truenas-mcp
```

No API key or URL needed - connects to `ws+unix:///var/run/middleware/middlewared.sock`.

### Remote Connection

```bash
TRUENAS_URL=wss://nas.example.com/api/current \
TRUENAS_API_KEY=1-abcdef123456... \
TRUENAS_USERNAME=admin \
TRUENAS_VERIFY_SSL=true \
truenas-mcp
```

## Available Tools

### Pools & Storage
- `list_pools` - List storage pools
- `get_pool` - Get pool details
- `pool_status` - Get pool health/status
- `create_pool` - Create new pool
- `delete_pool` - Destroy pool
- `import_pool` - Import existing pool
- `export_pool` - Export pool
- `pool_scrub` - Start scrub
- `list_datasets` - List datasets
- `get_dataset` - Get dataset details
- `create_dataset` - Create dataset
- `delete_dataset` - Delete dataset
- `update_dataset` - Update dataset properties
- `list_snapshots` - List snapshots
- `create_snapshot` - Create snapshot
- `delete_snapshot` - Delete snapshot
- `rollback_snapshot` - Rollback to snapshot
- `list_snapshot_tasks` - List periodic snapshot tasks
- `create_snapshot_task` - Create snapshot task
- `delete_snapshot_task` - Delete snapshot task
- `list_scrubs` - List scrub tasks
- `get_scrub` - Get scrub status
- `create_scrub` - Create scheduled scrub
- `run_scrub` - Manually run scrub

### Virtual Machines
- `list_vms` - List VMs
- `get_vm` - Get VM details
- `vm_status` - Get VM power status
- `start_vm` - Start VM
- `stop_vm` - Stop VM
- `restart_vm` - Restart VM
- `poweroff_vm` - Hard power off
- `suspend_vm` - Suspend VM
- `resume_vm` - Resume VM
- `create_vm` - Create VM
- `delete_vm` - Delete VM
- `update_vm` - Update VM config
- `clone_vm` - Clone VM
- `get_vm_console` - Get console info
- `vm_get_display_web_uri` - Get web console URI
- `list_vm_devices` - List VM devices
- `vm_device_create` - Add device
- `vm_device_delete` - Remove device
- `vm_device_update` - Update device

### Applications/Containers
- `list_apps` - List applications
- `get_app` - Get app details
- `start_app` - Start app
- `stop_app` - Stop app
- `restart_app` - Restart app
- `redeploy_app` - Redeploy app
- `update_app` - Update app config
- `delete_app` - Delete app
- `app_available` - List available apps
- `app_categories` - List app categories
- `app_latest` - Get latest app version
- `app_image_list` - List images
- `app_image_pull` - Pull docker image
- `app_image_delete` - Delete image
- `app_registry_list` - List registries
- `app_registry_create` - Create registry
- `app_registry_delete` - Delete registry
- `app_ix_volume_query` - Query IX volumes
- `app_ix_volume_create` - Create IX volume

### Users & Groups
- `list_users` - List users
- `get_user` - Get user details
- `create_user` - Create user
- `update_user` - Update user
- `delete_user` - Delete user
- `set_user_password` - Set password
- `renew_user_2fa_secret` - Renew 2FA
- `unset_user_2fa_secret` - Remove 2FA
- `list_groups` - List groups
- `get_group` - Get group details
- `create_group` - Create group
- `update_group` - Update group
- `delete_group` - Delete group

### Filesystem Operations
- `list_directory` - List directory contents
- `read_file` - Read file contents
- `write_file` - Write file
- `mkdir` - Create directory
- `chown` - Change ownership
- `set_permissions` - Set permissions
- `get_acl` - Get ACL
- `set_acl` - Set ACL
- `stat` - Get file status
- `list_acl_templates` - List ACL templates
- `get_acl_template` - Get ACL template
- `create_acl_template` - Create ACL template
- `update_acl_template` - Update ACL template
- `delete_acl_template` - Delete ACL template

### System & Hardware
- `system_info` - System information
- `system_general_config` - General config
- `system_security_info` - Security info
- `system_security_config` - Security config
- `system_ntp_servers` - List NTP servers
- `system_country_choices` - Country choices
- `system_fips_available` - FIPS availability
- `system_fips_enabled` - FIPS status
- `reboot` - Reboot system
- `shutdown` - Shutdown system
- `update_system_general` - Update general config
- `update_system_security` - Update security config
- `create_ntp_server` - Add NTP server
- `delete_ntp_server` - Remove NTP server
- `list_disks` - List physical disks
- `disk_temperature_alerts` - Disk temps
- `disk_get_info` - Disk details
- `list_interfaces` - List network interfaces
- `list_certificates` - List certificates
- `create_certificate` - Create certificate
- `delete_certificate` - Delete certificate
- `ipmi_is_loaded` - IPMI status
- `list_boot_environments` - List boot environments
- `get_boot_environment` - Get boot env
- `activate_boot_environment` - Activate boot env
- `create_boot_environment` - Create boot env

### Sharing (SMB/NFS)
- `list_smb_shares` - List SMB shares
- `get_smb_share` - Get SMB share
- `create_smb_share` - Create SMB share
- `update_smb_share` - Update SMB share
- `delete_smb_share` - Delete SMB share
- `set_smb_acl` - Set SMB ACL
- `smb_config` - SMB global config
- `update_smb_config` - Update SMB config
- `list_nfs_shares` - List NFS shares
- `get_nfs_share` - Get NFS share
- `create_nfs_share` - Create NFS share
- `update_nfs_share` - Update NFS share
- `delete_nfs_share` - Delete NFS share
- `nfs_config` - NFS global config
- `update_nfs_config` - Update NFS config

## Usage with MCP Client

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "truenas": {
      "command": "truenas-mcp",
      "env": {
        "TRUENAS_URL": "wss://nas.example.com/api/current",
        "TRUENAS_API_KEY": "your-api-key",
        "TRUENAS_USERNAME": "admin"
      }
    }
  }
}
```

## API Key Generation

1. In TrueNAS web UI, go to **Settings** > **API Keys**
2. Click **Add** to create a new API key
3. Set appropriate permissions for the user
4. Copy the generated key (shown only once)

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
pyright
```

## License

MIT