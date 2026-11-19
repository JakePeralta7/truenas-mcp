"""Pool, dataset, snapshot, and scrub management tools."""

from __future__ import annotations

from typing import Any

from truenas_mcp.client import TruenasError, build_filters, build_options
from truenas_mcp.server import READ_ONLY, READ_ONLY_MODE, get_client, logger, mcp, truenas_errors

# --- Pool Tools ---


def do_list_pools(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.pool.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_pools(
    name: str | None = None,
    status: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List storage pools.

    Args:
        name: Filter by pool name
        status: Filter by pool status (e.g., HEALTHY, DEGRADED, FAULTED)
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name, status=status)
    options = build_options(limit=limit, offset=offset)
    return do_list_pools(get_client(), filters or None, options or None)


def do_get_pool(client, name: str) -> dict[str, Any]:
    filters = build_filters(name=name)
    results = client.api.pool.query(filters, build_options(limit=1))
    if not results:
        raise TruenasError(f"Pool not found: {name}")
    return results[0]


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_pool(name: str) -> dict[str, Any]:
    """Get detailed information about a specific pool."""
    return do_get_pool(get_client(), name)


def do_pool_status(client, name: str) -> dict[str, Any]:
    """Get detailed pool status including vdev topology."""
    # Use pool.get_instance which returns detailed status including topology
    return client.api.pool.get_instance(name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def pool_status(name: str) -> dict[str, Any]:
    """Get detailed status and health information for a pool including vdev topology."""
    return do_pool_status(get_client(), name)


def _register_create_pool():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "create_pool", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def create_pool(
        name: str,
        topology: dict,
        encryption: bool = False,
        encryption_options: dict | None = None,
    ) -> dict[str, Any]:
        """Create a new storage pool.

        Args:
            name: Pool name
            topology: Vdev topology dict
                (e.g., {"data": [{"type": "MIRROR", "disks": ["ada0", "ada1"]}]})
            encryption: Enable encryption
            encryption_options: Encryption options dict
        """
        body = {"name": name, "topology": topology}
        if encryption:
            body["encryption"] = True
            if encryption_options:
                body["encryption_options"] = encryption_options
        return await get_client().api.pool.create(body)


def _register_delete_pool():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "delete_pool", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def delete_pool(name: str, confirm: bool = False) -> dict[str, Any]:
        """Delete/destroy a storage pool.

        Args:
            name: Pool name
            confirm: Must be true to confirm destruction
        """
        if not confirm:
            raise TruenasError("Must set confirm=true to destroy a pool")
        return await get_client().api.pool.delete(name)


def _register_import_pool():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "import_pool", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def import_pool(
        name: str,
        guid: str | None = None,
        devices: list[str] | None = None,
    ) -> dict[str, Any]:
        """Import an existing pool.

        Args:
            name: Pool name
            guid: Pool GUID (optional)
            devices: Device paths (optional)
        """
        body: dict[str, Any] = {"name": name}
        if guid:
            body["guid"] = guid
        if devices:
            body["devices"] = devices
        return await get_client().api.pool.import_pool(body)


def _register_export_pool():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "export_pool", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def export_pool(name: str, cascade: bool = False) -> dict[str, Any]:
        """Export a pool.

        Args:
            name: Pool name
            cascade: Force export even if datasets are busy
        """
        return await get_client().api.pool.export(name, cascade)


def _register_pool_scrub():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "pool_scrub", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def pool_scrub(name: str, threshold: int | None = None) -> dict[str, Any]:
        """Start a scrub on a pool.

        Args:
            name: Pool name
            threshold: Days since last scrub before starting new one
        """
        body = {}
        if threshold is not None:
            body["threshold"] = threshold
        return await get_client().api.pool.scrub(name, body)


# --- Dataset Tools ---


def do_list_datasets(
    client, pool: str | None = None, filters=None, options=None
) -> list[dict[str, Any]]:
    f = filters or []
    if pool:
        f = f + build_filters(pool=pool)
    kwargs = {}
    if f:
        kwargs["filters"] = f
    if options:
        kwargs["options"] = options
    return client.api.pool.dataset.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_datasets(
    pool: str | None = None,
    name: str | None = None,
    type: str | None = None,  # filesystem, volume, snapshot
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List datasets (filesystems, volumes, snapshots).

    Args:
        pool: Filter by pool name
        name: Filter by dataset name
        type: Filter by type (filesystem, volume, snapshot)
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name, type=type)
    options = build_options(limit=limit, offset=offset)
    return do_list_datasets(get_client(), pool, filters or None, options or None)


def do_get_dataset(client, name: str) -> dict[str, Any]:
    """Get dataset by full name (pool/dataset)."""
    filters = build_filters(name=name)
    results = client.api.pool.dataset.query(filters, build_options(limit=1))
    if not results:
        raise TruenasError(f"Dataset not found: {name}")
    return results[0]


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_dataset(name: str) -> dict[str, Any]:
    """Get detailed information about a dataset."""
    return do_get_dataset(get_client(), name)


def _register_create_dataset():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "create_dataset", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def create_dataset(
        name: str,
        type: str = "FILESYSTEM",  # FILESYSTEM, VOLUME
        volsize: str | None = None,  # For volumes, e.g., "10G"
        compression: str | None = None,  # lz4, gzip, zstd, etc.
        atime: str | None = None,  # on, off, inherit
        recordsize: str | None = None,  # 512, 1k, 4k, 8k, 16k, 32k, 64k, 128k, 256k, 512k, 1M
        dedup: str | None = None,  # on, off, verify, inherit
        copies: int | None = None,  # 1, 2, 3
        sync: str | None = None,  # standard, always, disabled, inherit
        quota: str | None = None,
        refquota: str | None = None,
        reservation: str | None = None,
        refreservation: str | None = None,
    ) -> dict[str, Any]:
        """Create a new dataset.

        Args:
            name: Full dataset name (e.g., "pool/dataset")
            type: FILESYSTEM or VOLUME
            volsize: Size for volumes (e.g., "10G")
            compression: Compression algorithm
            atime: Access time behavior
            recordsize: Record size
            dedup: Deduplication setting
            copies: Number of copies
            sync: Sync behavior
            quota: Quota limit
            refquota: Reference quota
            reservation: Space reservation
            refreservation: Reference reservation
        """
        body: dict[str, Any] = {"name": name, "type": type}

        if type == "VOLUME" and volsize:
            body["volsize"] = volsize

        properties = {}
        if compression:
            properties["compression"] = compression
        if atime:
            properties["atime"] = atime
        if recordsize:
            properties["recordsize"] = recordsize
        if dedup:
            properties["dedup"] = dedup
        if copies:
            properties["copies"] = copies
        if sync:
            properties["sync"] = sync
        if quota:
            properties["quota"] = quota
        if refquota:
            properties["refquota"] = refquota
        if reservation:
            properties["reservation"] = reservation
        if refreservation:
            properties["refreservation"] = refreservation

        if properties:
            body["properties"] = properties

        return await get_client().api.pool.dataset.create(body)


def _register_delete_dataset():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "delete_dataset", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def delete_dataset(
        name: str, force: bool = False, recursive: bool = False
    ) -> dict[str, Any]:
        """Delete a dataset.

        Args:
            name: Full dataset name
            force: Force unmount
            recursive: Recursively delete children
        """
        return await get_client().api.pool.dataset.delete(name, force=force, recursive=recursive)


def _register_update_dataset():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "update_dataset", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def update_dataset(
        name: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Update dataset properties.

        Args:
            name: Full dataset name
            properties: Dict of properties to update (compression, atime, etc.)
        """
        return await get_client().api.pool.dataset.update(name, properties)


# --- Snapshot Tools ---


def do_list_snapshots(
    client, dataset: str | None = None, filters=None, options=None
) -> list[dict[str, Any]]:
    f = filters or []
    if dataset:
        f = f + build_filters(dataset=dataset)
    kwargs = {}
    if f:
        kwargs["filters"] = f
    if options:
        kwargs["options"] = options
    return client.api.pool.dataset.snapshot_query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_snapshots(
    dataset: str | None = None,
    name: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List ZFS snapshots.

    Args:
        dataset: Filter by parent dataset
        name: Filter by snapshot name
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name)
    options = build_options(limit=limit, offset=offset)
    return do_list_snapshots(get_client(), dataset, filters or None, options or None)


def _register_create_snapshot():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "create_snapshot", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def create_snapshot(
        dataset: str,
        name: str,
        recursive: bool = False,
        exclude: list[str] | None = None,
        vmware_sync: bool = False,
    ) -> dict[str, Any]:
        """Create a ZFS snapshot.

        Args:
            dataset: Parent dataset name
            name: Snapshot name
            recursive: Snapshot children recursively
            exclude: Datasets to exclude (for recursive)
            vmware_sync: VMware snapshot synchronization
        """
        body = {"dataset": dataset, "name": name, "recursive": recursive}
        if exclude:
            body["exclude"] = exclude
        if vmware_sync:
            body["vmware_sync"] = vmware_sync
        return await get_client().api.pool.dataset.create_snapshot(body)


def _register_delete_snapshot():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "delete_snapshot", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def delete_snapshot(name: str, force: bool = False) -> dict[str, Any]:
        """Delete a ZFS snapshot.

        Args:
            name: Full snapshot name (e.g., "pool/dataset@snapshot")
            force: Force deletion
        """
        return await get_client().api.pool.dataset.delete_snapshot(name, force=force)


def _register_rollback_snapshot():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "rollback_snapshot", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def rollback_snapshot(name: str) -> dict[str, Any]:
        """Rollback dataset to a snapshot.

        Args:
            name: Full snapshot name
        """
        return await get_client().api.pool.dataset.rollback(name)


# --- Snapshot Task Tools ---


def do_list_snapshot_tasks(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.pool.snapshottask.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_snapshot_tasks(
    pool: str | None = None,
    enabled: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List periodic snapshot tasks.

    Args:
        pool: Filter by pool
        enabled: Filter by enabled status
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(pool=pool, enabled=enabled)
    options = build_options(limit=limit, offset=offset)
    return do_list_snapshot_tasks(get_client(), filters or None, options or None)


def _register_create_snapshot_task():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool",
            extra={"tool": "create_snapshot_task", "reason": "read_only_mode"},
        )
        return

    @mcp.tool()
    async def create_snapshot_task(
        dataset: str,
        recursive: bool = True,
        exclude: list[str] | None = None,
        schedule: dict
        | None = None,  # {"minute": "0", "hour": "0", "dom": "*", "month": "*", "dow": "*"}
        naming_schema: str | None = None,  # e.g., "auto-%Y-%m-%d_%H-%M"
        lifetime: str | None = None,  # e.g., "1w", "30d"
        enabled: bool = True,
        vmware_sync: bool = False,
    ) -> dict[str, Any]:
        """Create a periodic snapshot task.

        Args:
            dataset: Dataset to snapshot
            recursive: Include child datasets
            exclude: Datasets to exclude
            schedule: Cron-style schedule dict
            naming_schema: Snapshot naming pattern
            lifetime: Retention period (e.g., "1w", "30d")
            enabled: Whether task is enabled
            vmware_sync: VMware synchronization
        """
        body = {
            "dataset": dataset,
            "recursive": recursive,
            "enabled": enabled,
            "vmware_sync": vmware_sync,
        }
        if exclude:
            body["exclude"] = exclude
        if schedule:
            body["schedule"] = schedule
        if naming_schema:
            body["naming_schema"] = naming_schema
        if lifetime:
            body["lifetime"] = lifetime
        return await get_client().api.pool.snapshottask.create(body)


def _register_delete_snapshot_task():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool",
            extra={"tool": "delete_snapshot_task", "reason": "read_only_mode"},
        )
        return

    @mcp.tool()
    async def delete_snapshot_task(id: int) -> dict[str, Any]:
        """Delete a periodic snapshot task."""
        return await get_client().api.pool.snapshottask.delete(id)


# --- Scrub Tools ---


def do_list_scrubs(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.pool.scrub.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_scrubs(
    pool: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List scrub tasks/status.

    Args:
        pool: Filter by pool
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(pool=pool)
    options = build_options(limit=limit, offset=offset)
    return do_list_scrubs(get_client(), filters or None, options or None)


def do_get_scrub(client, pool: str) -> dict[str, Any]:
    filters = build_filters(pool=pool)
    results = client.api.pool.scrub.query(filters, build_options(limit=1))
    if not results:
        raise TruenasError(f"Scrub not found for pool: {pool}")
    return results[0]


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_scrub(pool: str) -> dict[str, Any]:
    """Get scrub status for a pool."""
    return do_get_scrub(get_client(), pool)


def _register_create_scrub():
    if READ_ONLY_MODE:
        logger.info(
            "skipping_write_tool", extra={"tool": "create_scrub", "reason": "read_only_mode"}
        )
        return

    @mcp.tool()
    async def create_scrub(
        pool: str,
        threshold: int = 35,  # Days
        schedule: dict | None = None,
        enabled: bool = True,
    ) -> dict[str, Any]:
        """Create a scheduled scrub task.

        Args:
            pool: Pool name
            threshold: Days between scrubs
            schedule: Cron schedule dict
            enabled: Whether enabled
        """
        body = {"pool": pool, "threshold": threshold, "enabled": enabled}
        if schedule:
            body["schedule"] = schedule
        return await get_client().api.pool.scrub.create(body)


def _register_run_scrub():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "run_scrub", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def run_scrub(pool: str, threshold: int | None = None) -> dict[str, Any]:
        """Manually start a scrub on a pool.

        Args:
            pool: Pool name
            threshold: Override threshold for this run
        """
        body = {}
        if threshold is not None:
            body["threshold"] = threshold
        return await get_client().api.pool.scrub.run(pool, body)


# Register all write tools
_register_create_pool()
_register_delete_pool()
_register_import_pool()
_register_export_pool()
_register_pool_scrub()
_register_create_dataset()
_register_delete_dataset()
_register_update_dataset()
_register_create_snapshot()
_register_delete_snapshot()
_register_rollback_snapshot()
_register_create_snapshot_task()
_register_delete_snapshot_task()
_register_create_scrub()
_register_run_scrub()
