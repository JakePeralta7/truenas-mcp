"""Application/Container management tools."""

from __future__ import annotations

from typing import Any

from truenas_mcp.client import TruenasError, build_filters, build_options
from truenas_mcp.server import READ_ONLY, READ_ONLY_MODE, get_client, logger, mcp, truenas_errors

# --- App Tools ---

def do_list_apps(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.app.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_apps(
    name: str | None = None,
    state: str | None = None,  # RUNNING, STOPPED, etc.
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List applications (containers/charts).
    
    Args:
        name: Filter by app name
        state: Filter by app state
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name, state=state)
    options = build_options(limit=limit, offset=offset)
    return do_list_apps(get_client(), filters or None, options or None)


def do_get_app(client, name: str) -> dict[str, Any]:
    filters = build_filters(name=name)
    results = client.api.app.query(filters, build_options(limit=1))
    if not results:
        raise TruenasError(f"App not found: {name}")
    return results[0]


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_app(name: str) -> dict[str, Any]:
    """Get detailed information about a specific application."""
    return do_get_app(get_client(), name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_available() -> list[dict[str, Any]]:
    """Get available applications from catalog."""
    return get_client().api.app.available()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_categories() -> list[dict[str, Any]]:
    """Get available application categories."""
    return get_client().api.app.categories()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_certificate_choices() -> list[dict[str, Any]]:
    """Get available certificate choices for apps."""
    return get_client().api.app.certificate_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_gpu_choices() -> list[dict[str, Any]]:
    """Get available GPU choices for apps."""
    return get_client().api.app.gpu_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_ip_choices() -> list[dict[str, Any]]:
    """Get available IP choices for apps."""
    return get_client().api.app.ip_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_latest(name: str) -> dict[str, Any]:
    """Get latest version info for an app."""
    return get_client().api.app.latest(name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_outdated_docker_images() -> list[dict[str, Any]]:
    """Get list of outdated docker images."""
    return get_client().api.app.outdated_docker_images()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_used_ports() -> list[dict[str, Any]]:
    """Get ports currently in use by apps."""
    return get_client().api.app.used_ports()


def _register_start_app():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "start_app", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def start_app(name: str) -> dict[str, Any]:
        """Start an application."""
        return await get_client().api.app.start(name)


def _register_stop_app():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "stop_app", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def stop_app(name: str) -> dict[str, Any]:
        """Stop an application."""
        return await get_client().api.app.stop(name)


def _register_restart_app():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "restart_app", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def restart_app(name: str) -> dict[str, Any]:
        """Restart an application."""
        return await get_client().api.app.restart(name)


def _register_redeploy_app():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "redeploy_app", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def redeploy_app(name: str, force: bool = False) -> dict[str, Any]:
        """Redeploy an application.
        
        Args:
            name: App name
            force: Force redeploy even if no changes
        """
        return await get_client().api.app.redeploy(name, force=force)


def _register_update_app():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "update_app", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def update_app(name: str, **kwargs) -> dict[str, Any]:
        """Update an application configuration.
        
        Args:
            name: App name
            **kwargs: Properties to update
        """
        return await get_client().api.app.update(name, kwargs)


def _register_delete_app():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "delete_app", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def delete_app(name: str, remove_data: bool = False) -> dict[str, Any]:
        """Delete an application.
        
        Args:
            name: App name
            remove_data: Remove associated data (PVCs, etc.)
        """
        return await get_client().api.app.delete(name, remove_data=remove_data)


# --- App Image Tools ---

@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_image_list() -> list[dict[str, Any]]:
    """List all app images."""
    return get_client().api.app.image.query()


def _register_app_image_pull():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "app_image_pull", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def app_image_pull(image: str, tag: str = "latest") -> dict[str, Any]:
        """Pull a docker image.
        
        Args:
            image: Image name (e.g., nginx, linuxserver/plex)
            tag: Image tag
        """
        return await get_client().api.app.image.pull(image, tag)


def _register_app_image_delete():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "app_image_delete", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def app_image_delete(image: str, tag: str | None = None) -> dict[str, Any]:
        """Delete a docker image.
        
        Args:
            image: Image name
            tag: Image tag (optional, deletes all tags if omitted)
        """
        return await get_client().api.app.image.delete(image, tag)


# --- App Registry Tools ---

@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_registry_list() -> list[dict[str, Any]]:
    """List configured container registries."""
    return get_client().api.app.registry.query()


def _register_app_registry_create():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "app_registry_create", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def app_registry_create(
        url: str,
        username: str | None = None,
        password: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a container registry configuration.
        
        Args:
            url: Registry URL (e.g., docker.io, ghcr.io)
            username: Username for auth
            password: Password/token for auth
            description: Description
        """
        body = {"url": url}
        if username:
            body["username"] = username
        if password:
            body["password"] = password
        if description:
            body["description"] = description
        return await get_client().api.app.registry.create(body)


def _register_app_registry_delete():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "app_registry_delete", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def app_registry_delete(id: int) -> dict[str, Any]:
        """Delete a container registry configuration."""
        return await get_client().api.app.registry.delete(id)


# --- IX Volume Tools ---

@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def app_ix_volume_query() -> list[dict[str, Any]]:
    """Query IX volumes."""
    return get_client().api.app.ix_volume.query()


def _register_app_ix_volume_create():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "app_ix_volume_create", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def app_ix_volume_create(
        name: str,
        dataset: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create an IX volume for app storage.
        
        Args:
            name: Volume name
            dataset: Parent dataset
            description: Description
        """
        body = {"name": name, "dataset": dataset}
        if description:
            body["description"] = description
        return await get_client().api.app.ix_volume.create(body)


# Register all write tools
_register_start_app()
_register_stop_app()
_register_restart_app()
_register_redeploy_app()
_register_update_app()
_register_delete_app()
_register_app_image_pull()
_register_app_image_delete()
_register_app_registry_create()
_register_app_registry_delete()
_register_app_ix_volume_create()
