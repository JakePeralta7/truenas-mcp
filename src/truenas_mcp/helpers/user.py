"""User and Group management tools."""

from __future__ import annotations

from typing import Any

from truenas_mcp.client import TruenasError, build_filters, build_options
from truenas_mcp.server import READ_ONLY, READ_ONLY_MODE, get_client, logger, mcp, truenas_errors

# --- User Tools ---

def do_list_users(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.user.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_users(
    username: str | None = None,
    uid: int | None = None,
    builtin: bool | None = None,
    enabled: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List users.
    
    Args:
        username: Filter by username
        uid: Filter by UID
        builtin: Filter by builtin status
        enabled: Filter by enabled status
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(username=username, uid=uid, builtin=builtin, enabled=enabled)
    options = build_options(limit=limit, offset=offset)
    return do_list_users(get_client(), filters or None, options or None)


def do_get_user(client, username: str) -> dict[str, Any]:
    filters = build_filters(username=username)
    results = client.api.user.query(filters, build_options(limit=1))
    if not results:
        raise TruenasError(f"User not found: {username}")
    return results[0]


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_user(username: str) -> dict[str, Any]:
    """Get detailed information about a specific user."""
    return do_get_user(get_client(), username)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_next_uid() -> int:
    """Get the next available UID."""
    return get_client().api.user.get_next_uid()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def user_shell_choices() -> list[str]:
    """Get available shell choices."""
    return get_client().api.user.shell_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def has_local_administrator_set_up() -> bool:
    """Check if a local administrator has been set up."""
    return get_client().api.user.has_local_administrator_set_up()


def _register_create_user():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "create_user", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def create_user(
        username: str,
        full_name: str,
        password: str,
        group_create: bool = True,
        uid: int | None = None,
        shell: str = "/bin/sh",
        home: str | None = None,
        email: str | None = None,
        sshpubkey: str | None = None,
        lock: bool = False,
        sudo: bool = False,
        group: str | None = None,
        groups: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new user.
        
        Args:
            username: Username
            full_name: Full name
            password: Password
            group_create: Create a group with same name
            uid: Specific UID (optional)
            shell: Login shell
            home: Home directory
            email: Email address
            sshpubkey: SSH public key
            lock: Lock account
            sudo: Add to sudoers
            group: Primary group
            groups: Additional groups
        """
        body = {
            "username": username,
            "full_name": full_name,
            "password": password,
            "group_create": group_create,
            "shell": shell,
            "lock": lock,
            "sudo": sudo,
        }
        if uid is not None:
            body["uid"] = uid
        if home:
            body["home"] = home
        if email:
            body["email"] = email
        if sshpubkey:
            body["sshpubkey"] = sshpubkey
        if group:
            body["group"] = group
        if groups:
            body["groups"] = groups
        return await get_client().api.user.create(body)


def _register_update_user():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "update_user", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def update_user(username: str, **kwargs) -> dict[str, Any]:
        """Update a user.
        
        Args:
            username: Username
            **kwargs: Properties to update (full_name, email, shell, etc.)
        """
        return await get_client().api.user.update(username, kwargs)


def _register_delete_user():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "delete_user", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def delete_user(username: str, remove_home: bool = False) -> dict[str, Any]:
        """Delete a user.
        
        Args:
            username: Username
            remove_home: Remove home directory
        """
        return await get_client().api.user.delete(username, remove_home=remove_home)


def _register_set_password():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "set_user_password", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def set_user_password(username: str, password: str) -> dict[str, Any]:
        """Set a user's password."""
        return await get_client().api.user.set_password(username, password)


def _register_renew_2fa_secret():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "renew_user_2fa_secret", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def renew_user_2fa_secret(username: str) -> dict[str, Any]:
        """Renew a user's 2FA secret."""
        return await get_client().api.user.renew_2fa_secret(username)


def _register_unset_2fa_secret():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "unset_user_2fa_secret", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def unset_user_2fa_secret(username: str) -> dict[str, Any]:
        """Unset a user's 2FA secret."""
        return await get_client().api.user.unset_2fa_secret(username)


# --- Group Tools ---

def do_list_groups(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.group.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_groups(
    name: str | None = None,
    gid: int | None = None,
    builtin: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List groups.
    
    Args:
        name: Filter by group name
        gid: Filter by GID
        builtin: Filter by builtin status
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name, gid=gid, builtin=builtin)
    options = build_options(limit=limit, offset=offset)
    return do_list_groups(get_client(), filters or None, options or None)


def do_get_group(client, name: str) -> dict[str, Any]:
    filters = build_filters(name=name)
    results = client.api.group.query(filters, build_options(limit=1))
    if not results:
        raise TruenasError(f"Group not found: {name}")
    return results[0]


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_group(name: str) -> dict[str, Any]:
    """Get detailed information about a specific group."""
    return do_get_group(get_client(), name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_next_gid() -> int:
    """Get the next available GID."""
    return get_client().api.group.get_next_gid()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def group_has_password_enabled_user(name: str) -> bool:
    """Check if group has a password-enabled user."""
    return get_client().api.group.has_password_enabled_user(name)


def _register_create_group():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "create_group", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def create_group(
        name: str,
        gid: int | None = None,
        sudo: bool = False,
        users: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new group.
        
        Args:
            name: Group name
            gid: Specific GID (optional)
            sudo: Add to sudoers
            users: Initial users to add
        """
        body = {"name": name, "sudo": sudo}
        if gid is not None:
            body["gid"] = gid
        if users:
            body["users"] = users
        return await get_client().api.group.create(body)


def _register_update_group():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "update_group", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def update_group(name: str, **kwargs) -> dict[str, Any]:
        """Update a group.
        
        Args:
            name: Group name
            **kwargs: Properties to update (gid, sudo, users)
        """
        return await get_client().api.group.update(name, kwargs)


def _register_delete_group():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "delete_group", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def delete_group(name: str) -> dict[str, Any]:
        """Delete a group."""
        return await get_client().api.group.delete(name)


# Register all write tools
_register_create_user()
_register_update_user()
_register_delete_user()
_register_set_password()
_register_renew_2fa_secret()
_register_unset_2fa_secret()
_register_create_group()
_register_update_group()
_register_delete_group()
