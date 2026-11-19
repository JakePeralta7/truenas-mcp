"""Filesystem operations tools (list, read, write, permissions, ACLs)."""

from __future__ import annotations

from typing import Any

from truenas_mcp.server import READ_ONLY, READ_ONLY_MODE, get_client, logger, mcp, truenas_errors

# --- Filesystem Tools ---


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_directory(path: str, options: dict | None = None) -> list[dict[str, Any]]:
    """List directory contents.

    Args:
        path: Directory path (e.g., /mnt/pool/dataset)
        options: Additional options (e.g., {"follow_symlinks": true})
    """
    return get_client().api.filesystem.listdir(path, options or {})


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def read_file(path: str, options: dict | None = None) -> str:
    """Read file contents.

    Args:
        path: File path
        options: Additional options
    """
    return get_client().api.filesystem.get(path, options or {})


def _register_write_file():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "write_file", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def write_file(
        path: str, data: str, mode: str = "w", options: dict | None = None
    ) -> dict[str, Any]:
        """Write file contents.

        Args:
            path: File path
            data: File content
            mode: Write mode (w, a, x)
            options: Additional options
        """
        body: dict[str, Any] = {"data": data, "mode": mode}
        if options:
            body["options"] = options
        return await get_client().api.filesystem.put(path, body)


def _register_mkdir():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "mkdir", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def mkdir(path: str, mode: int = 0o755, parents: bool = True) -> dict[str, Any]:
        """Create a directory.

        Args:
            path: Directory path
            mode: Permissions mode (octal)
            parents: Create parent directories
        """
        return await get_client().api.filesystem.mkdir(path, mode=mode, parents=parents)


def _register_chown():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "chown", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def chown(path: str, uid: int | None = None, gid: int | None = None) -> dict[str, Any]:
        """Change file/directory ownership.

        Args:
            path: File/directory path
            uid: New UID (optional)
            gid: New GID (optional)
        """
        body = {}
        if uid is not None:
            body["uid"] = uid
        if gid is not None:
            body["gid"] = gid
        return await get_client().api.filesystem.chown(path, body)


def _register_set_permissions():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "set_permissions", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def set_permissions(path: str, mode: int, recursive: bool = False) -> dict[str, Any]:
        """Set file/directory permissions.

        Args:
            path: File/directory path
            mode: Permissions mode (octal, e.g., 0o755)
            recursive: Apply recursively
        """
        return await get_client().api.filesystem.setperm(
            path, {"mode": mode, "recursive": recursive}
        )


def _register_get_acl():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "get_acl", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def get_acl(path: str, options: dict | None = None) -> dict[str, Any]:
        """Get ACL for a file/directory.

        Args:
            path: File/directory path
            options: Additional options
        """
        return await get_client().api.filesystem.getacl(path, options or {})


def _register_set_acl():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "set_acl", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def set_acl(path: str, acl: list[dict], options: dict | None = None) -> dict[str, Any]:
        """Set ACL for a file/directory.

        Args:
            path: File/directory path
            acl: ACL entries list
            options: Additional options
        """
        body: dict[str, Any] = {"acl": acl}
        if options:
            body["options"] = options
        return await get_client().api.filesystem.setacl(path, body)


def _register_stat():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "stat", "reason": "read_only_mode"})
        return

    @mcp.tool()
    @truenas_errors
    async def stat(path: str, options: dict | None = None) -> dict[str, Any]:
        """Get file/directory status.

        Args:
            path: File/directory path
            options: Additional options
        """
        return get_client().api.filesystem.stat(path, options or {})


# --- ACL Template Tools ---


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_acl_templates() -> list[dict[str, Any]]:
    """List ACL templates."""
    return get_client().api.filesystem.acltemplate.query()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_acl_template(name: str) -> dict[str, Any]:
    """Get an ACL template by name."""
    return get_client().api.filesystem.acltemplate.get_instance(name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_acl_template_by_path(path: str) -> dict[str, Any]:
    """Get ACL template by path."""
    return get_client().api.filesystem.acltemplate.by_path(path)


def _register_create_acl_template():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "create_acl_template", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def create_acl_template(
        name: str,
        acl: list[dict],
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create an ACL template.

        Args:
            name: Template name
            acl: ACL entries
            description: Description
        """
        body = {"name": name, "acl": acl}
        if description:
            body["description"] = description
        return await get_client().api.filesystem.acltemplate.create(body)


def _register_update_acl_template():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "update_acl_template", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def update_acl_template(
        name: str, acl: list[dict], description: str | None = None
    ) -> dict[str, Any]:
        """Update an ACL template."""
        body: dict[str, Any] = {"acl": acl}
        if description:
            body["description"] = description
        return await get_client().api.filesystem.acltemplate.update(name, body)


def _register_delete_acl_template():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "delete_acl_template", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def delete_acl_template(name: str) -> dict[str, Any]:
        """Delete an ACL template."""
        return await get_client().api.filesystem.acltemplate.delete(name)


# Register all write tools
_register_write_file()
_register_mkdir()
_register_chown()
_register_set_permissions()
_register_get_acl()
_register_set_acl()
_register_stat()
_register_create_acl_template()
_register_update_acl_template()
_register_delete_acl_template()
