"""SMB and NFS sharing management tools."""

from __future__ import annotations

from typing import Any

from truenas_mcp.client import TruenasError, build_filters, build_options
from truenas_mcp.server import READ_ONLY, READ_ONLY_MODE, get_client, logger, mcp, truenas_errors

# --- SMB Sharing Tools ---


def do_list_smb_shares(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.sharing.smb.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_smb_shares(
    name: str | None = None,
    path: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List SMB shares.

    Args:
        name: Filter by share name
        path: Filter by path
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name, path=path)
    options = build_options(limit=limit, offset=offset)
    return do_list_smb_shares(get_client(), filters or None, options or None)


def do_get_smb_share(client, name: str) -> dict[str, Any]:
    filters = build_filters(name=name)
    results = client.api.sharing.smb.query(filters, build_options(limit=1))
    if not results:
        raise TruenasError(f"SMB share not found: {name}")
    return results[0]


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_smb_share(name: str) -> dict[str, Any]:
    """Get detailed information about a specific SMB share."""
    return do_get_smb_share(get_client(), name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def smb_config() -> dict[str, Any]:
    """Get global SMB configuration."""
    return get_client().api.smb.config()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def smb_bindip_choices() -> list[str]:
    """Get available bind IP choices for SMB."""
    return get_client().api.smb.bindip_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def smb_unixcharset_choices() -> list[str]:
    """Get available Unix charset choices for SMB."""
    return get_client().api.smb.unixcharset_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def smb_presets() -> dict[str, Any]:
    """Get SMB preset configurations."""
    return get_client().api.sharing.smb.presets()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def smb_get_acl(path: str) -> dict[str, Any]:
    """Get SMB ACL for a path."""
    return get_client().api.sharing.smb.getacl(path)


def _register_create_smb_share():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "create_smb_share", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def create_smb_share(
        name: str,
        path: str,
        comment: str | None = None,
        browseable: bool = True,
        read_only: bool = False,
        guest_ok: bool = False,
        hosts_allow: str | None = None,
        hosts_deny: str | None = None,
        vfs_objects: list[str] | None = None,
        fruit: bool = False,
        fruit_encoding: str = "native",
        fruit_metadata: str = "netatalk",
        fruit_resource: str = "file",
        recyclebin: bool = False,
        recyclebin_preserve: bool = True,
        recyclebin_versions: bool = False,
        recyclebin_keeptree: bool = True,
        recyclebin_touch: bool = False,
        recyclebin_minsize: str | None = None,
        recyclebin_maxsize: str | None = None,
        recyclebin_exclude: list[str] | None = None,
        recyclebin_exclude_dir: list[str] | None = None,
        acl: bool = True,
        home: bool = False,
        abe: bool = False,
        shadow_copy: bool = False,
    ) -> dict[str, Any]:
        """Create an SMB share.

        Args:
            name: Share name
            path: Filesystem path
            comment: Description
            browseable: Show in browse list
            read_only: Read-only share
            guest_ok: Allow guest access
            hosts_allow: Hosts allow list
            hosts_deny: Hosts deny list
            vfs_objects: VFS modules
            fruit: Enable Apple fruit extensions
            fruit_encoding: Fruit encoding
            fruit_metadata: Fruit metadata
            fruit_resource: Fruit resource fork
            recyclebin: Enable recycle bin
            recyclebin_preserve: Preserve directory structure
            recyclebin_versions: Keep versions
            recyclebin_keeptree: Keep directory tree
            recyclebin_touch: Update timestamp
            recyclebin_minsize: Minimum file size
            recyclebin_maxsize: Maximum file size
            recyclebin_exclude: Exclude patterns
            recyclebin_exclude_dir: Exclude directories
            acl: Use ACLs
            home: Home directory share
            abe: Access-based enumeration
            shadow_copy: Enable shadow copies
        """
        body = {
            "name": name,
            "path": path,
            "browseable": browseable,
            "read_only": read_only,
            "guest_ok": guest_ok,
            "fruit": fruit,
            "fruit_encoding": fruit_encoding,
            "fruit_metadata": fruit_metadata,
            "fruit_resource": fruit_resource,
            "recyclebin": recyclebin,
            "recyclebin_preserve": recyclebin_preserve,
            "recyclebin_versions": recyclebin_versions,
            "recyclebin_keeptree": recyclebin_keeptree,
            "recyclebin_touch": recyclebin_touch,
            "acl": acl,
            "home": home,
            "abe": abe,
            "shadow_copy": shadow_copy,
        }
        if comment:
            body["comment"] = comment
        if hosts_allow:
            body["hosts_allow"] = hosts_allow
        if hosts_deny:
            body["hosts_deny"] = hosts_deny
        if vfs_objects:
            body["vfs_objects"] = vfs_objects
        if recyclebin_minsize:
            body["recyclebin_minsize"] = recyclebin_minsize
        if recyclebin_maxsize:
            body["recyclebin_maxsize"] = recyclebin_maxsize
        if recyclebin_exclude:
            body["recyclebin_exclude"] = recyclebin_exclude
        if recyclebin_exclude_dir:
            body["recyclebin_exclude_dir"] = recyclebin_exclude_dir
        return await get_client().api.sharing.smb.create(body)


def _register_update_smb_share():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "update_smb_share", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def update_smb_share(name: str, **kwargs) -> dict[str, Any]:
        """Update an SMB share."""
        return await get_client().api.sharing.smb.update(name, kwargs)


def _register_delete_smb_share():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "delete_smb_share", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def delete_smb_share(name: str) -> dict[str, Any]:
        """Delete an SMB share."""
        return await get_client().api.sharing.smb.delete(name)


def _register_set_smb_acl():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "set_smb_acl", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def set_smb_acl(path: str, acl: list[dict]) -> dict[str, Any]:
        """Set SMB ACL for a path."""
        return await get_client().api.sharing.smb.setacl(path, {"acl": acl})


def _register_update_smb_config():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "update_smb_config", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def update_smb_config(**kwargs) -> dict[str, Any]:
        """Update global SMB configuration."""
        return await get_client().api.smb.update(kwargs)


# --- NFS Sharing Tools ---


def do_list_nfs_shares(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.sharing.nfs.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_nfs_shares(
    id: int | None = None,
    path: str | None = None,
    network: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List NFS shares.

    Args:
        id: Filter by share ID
        path: Filter by path (single path)
        network: Filter by network (single CIDR)
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(id=id, path=path, network=network)
    options = build_options(limit=limit, offset=offset)
    return do_list_nfs_shares(get_client(), filters or None, options or None)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_nfs_share(id: int) -> dict[str, Any]:
    """Get detailed information about a specific NFS share."""
    return get_client().api.sharing.nfs.get_instance(id)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def nfs_bindip_choices() -> list[str]:
    """Get available bind IP choices for NFS."""
    return get_client().api.nfs.bindip_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def nfs_config() -> dict[str, Any]:
    """Get global NFS configuration."""
    return get_client().api.nfs.config()


def _register_create_nfs_share():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "create_nfs_share", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def create_nfs_share(
        paths: list[str],
        networks: list[str] | None = None,
        comment: str | None = None,
        ro: bool = False,
        maproot_user: str | None = None,
        maproot_group: str | None = None,
        mapall_user: str | None = None,
        mapall_group: str | None = None,
        security: list[str] | None = None,
        alldirs: bool = False,
        quiet: bool = False,
    ) -> dict[str, Any]:
        if networks is None:
            networks = ["0.0.0.0/0"]
        if security is None:
            security = ["sys"]
        """Create an NFS share.

        Args:
            paths: List of paths to share
            networks: Allowed networks (CIDR)
            comment: Description
            ro: Read-only
            maproot_user: Map root to user
            maproot_group: Map root to group
            mapall_user: Map all to user
            mapall_group: Map all to group
            security: Security flavors (sys, krb5, etc.)
            alldirs: Allow subdirectory mounts
            quiet: Quiet mode
        """
        body = {
            "paths": paths,
            "networks": networks,
            "ro": ro,
            "security": security,
            "alldirs": alldirs,
            "quiet": quiet,
        }
        if comment:
            body["comment"] = comment
        if maproot_user:
            body["maproot_user"] = maproot_user
        if maproot_group:
            body["maproot_group"] = maproot_group
        if mapall_user:
            body["mapall_user"] = mapall_user
        if mapall_group:
            body["mapall_group"] = mapall_group
        return await get_client().api.sharing.nfs.create(body)


def _register_update_nfs_share():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "update_nfs_share", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def update_nfs_share(id: int, **kwargs) -> dict[str, Any]:
        """Update an NFS share."""
        return await get_client().api.sharing.nfs.update(id, kwargs)


def _register_delete_nfs_share():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "delete_nfs_share", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def delete_nfs_share(id: int) -> dict[str, Any]:
        """Delete an NFS share."""
        return await get_client().api.sharing.nfs.delete(id)


def _register_update_nfs_config():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "update_nfs_config", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def update_nfs_config(**kwargs) -> dict[str, Any]:
        """Update global NFS configuration."""
        return await get_client().api.nfs.update(kwargs)


# Register all write tools
_register_create_smb_share()
_register_update_smb_share()
_register_delete_smb_share()
_register_set_smb_acl()
_register_update_smb_config()
_register_create_nfs_share()
_register_update_nfs_share()
_register_delete_nfs_share()
_register_update_nfs_config()
