"""Virtual Machine management tools."""

from __future__ import annotations

from typing import Any

from truenas_mcp.client import TruenasError, build_filters, build_options
from truenas_mcp.server import READ_ONLY, READ_ONLY_MODE, get_client, logger, mcp, truenas_errors

# --- VM Tools ---

def do_list_vms(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.vm.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_vms(
    name: str | None = None,
    status: str | None = None,  # RUNNING, STOPPED, etc.
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List virtual machines.
    
    Args:
        name: Filter by VM name
        status: Filter by VM status
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name, status=status)
    options = build_options(limit=limit, offset=offset)
    return do_list_vms(get_client(), filters or None, options or None)


def do_get_vm(client, name: str) -> dict[str, Any]:
    filters = build_filters(name=name)
    results = client.api.vm.query(filters, build_options(limit=1))
    if not results:
        raise TruenasError(f"VM not found: {name}")
    return results[0]


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_vm(name: str) -> dict[str, Any]:
    """Get detailed information about a specific VM."""
    return do_get_vm(get_client(), name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def vm_status(name: str) -> dict[str, Any]:
    """Get the power status of a VM."""
    return get_client().api.vm.status(name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_vm_console(name: str) -> dict[str, Any]:
    """Get console connection information for a VM."""
    return get_client().api.vm.get_console(name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def vm_get_display_web_uri(name: str) -> dict[str, Any]:
    """Get the web display URI for a VM's VNC/Spice console."""
    return get_client().api.vm.get_display_web_uri(name)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_vm_devices(name: str) -> list[dict[str, Any]]:
    """List devices attached to a VM."""
    return get_client().api.vm.device.query(build_filters(vm=name))


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def vm_get_available_memory() -> dict[str, Any]:
    """Get available memory for VM allocation."""
    return get_client().api.vm.get_available_memory()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def vm_cpu_model_choices() -> list[dict[str, Any]]:
    """Get available CPU model choices for VMs."""
    return get_client().api.vm.cpu_model_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def vm_guest_architecture_and_machine_choices() -> list[dict[str, Any]]:
    """Get available guest architecture and machine type choices."""
    return get_client().api.vm.guest_architecture_and_machine_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def vm_bootloader_ovmf_choices() -> list[dict[str, Any]]:
    """Get available OVMF bootloader choices."""
    return get_client().api.vm.bootloader_ovmf_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def vm_resolution_choices() -> list[dict[str, Any]]:
    """Get available display resolution choices."""
    return get_client().api.vm.resolution_choices()


def _register_start_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "start_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def start_vm(name: str) -> dict[str, Any]:
        """Start a virtual machine."""
        return await get_client().api.vm.start(name)


def _register_stop_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "stop_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def stop_vm(name: str, force: bool = False) -> dict[str, Any]:
        """Stop a virtual machine.
        
        Args:
            name: VM name
            force: Force power off
        """
        return await get_client().api.vm.stop(name, force=force)


def _register_restart_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "restart_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def restart_vm(name: str, force: bool = False) -> dict[str, Any]:
        """Restart a virtual machine.
        
        Args:
            name: VM name
            force: Force restart
        """
        return await get_client().api.vm.restart(name, force=force)


def _register_poweroff_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "poweroff_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def poweroff_vm(name: str) -> dict[str, Any]:
        """Power off a virtual machine (hard shutdown)."""
        return await get_client().api.vm.poweroff(name)


def _register_suspend_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "suspend_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def suspend_vm(name: str) -> dict[str, Any]:
        """Suspend a virtual machine (save state to disk)."""
        return await get_client().api.vm.suspend(name)


def _register_resume_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "resume_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def resume_vm(name: str) -> dict[str, Any]:
        """Resume a suspended virtual machine."""
        return await get_client().api.vm.resume(name)


def _register_create_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "create_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def create_vm(
        name: str,
        description: str | None = None,
        vcpus: int = 2,
        memory: int = 2048,  # MiB
        bootloader: str = "UEFI",  # UEFI, GRUB
        cpu_model: str = "host-passthrough",
        machine: str = "q35",
        autostart: bool = False,
        timezone: str = "UTC",
        shutdown_timeout: int = 90,
        devices: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Create a new virtual machine.
        
        Args:
            name: VM name
            description: Description
            vcpus: Number of virtual CPUs
            memory: Memory in MiB
            bootloader: UEFI or GRUB
            cpu_model: CPU model (e.g., host-passthrough, Haswell-noTSX)
            machine: Machine type (e.g., q35, pc-q35)
            autostart: Start on boot
            timezone: Timezone
            shutdown_timeout: Shutdown timeout in seconds
            devices: List of device configs (disks, nics, etc.)
        """
        body = {
            "name": name,
            "vcpus": vcpus,
            "memory": memory,
            "bootloader": bootloader,
            "cpu_model": cpu_model,
            "machine": machine,
            "autostart": autostart,
            "timezone": timezone,
            "shutdown_timeout": shutdown_timeout,
        }
        if description:
            body["description"] = description
        if devices:
            body["devices"] = devices
        return await get_client().api.vm.create(body)


def _register_delete_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "delete_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def delete_vm(name: str, force: bool = False) -> dict[str, Any]:
        """Delete a virtual machine.
        
        Args:
            name: VM name
            force: Force deletion
        """
        return await get_client().api.vm.delete(name, force=force)


def _register_update_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "update_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def update_vm(name: str, **kwargs) -> dict[str, Any]:
        """Update a virtual machine configuration.
        
        Args:
            name: VM name
            **kwargs: Properties to update (vcpus, memory, bootloader, etc.)
        """
        return await get_client().api.vm.update(name, kwargs)


def _register_clone_vm():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "clone_vm", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def clone_vm(name: str, new_name: str, description: str | None = None) -> dict[str, Any]:
        """Clone a virtual machine.
        
        Args:
            name: Source VM name
            new_name: New VM name
            description: Description for clone
        """
        body = {"new_name": new_name}
        if description:
            body["description"] = description
        return await get_client().api.vm.clone(name, body)


def _register_vm_device_create():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "vm_device_create", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def vm_device_create(vm: str, dtype: str, attributes: dict) -> dict[str, Any]:
        """Add a device to a VM.
        
        Args:
            vm: VM name
            dtype: Device type (DISK, NIC, CDROM, etc.)
            attributes: Device-specific attributes
        """
        body = {"vm": vm, "dtype": dtype, "attributes": attributes}
        return await get_client().api.vm.device.create(body)


def _register_vm_device_delete():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "vm_device_delete", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def vm_device_delete(vm: str, device_id: int) -> dict[str, Any]:
        """Remove a device from a VM."""
        return await get_client().api.vm.device.delete(vm, device_id)


def _register_vm_device_update():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "vm_device_update", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def vm_device_update(vm: str, device_id: int, attributes: dict) -> dict[str, Any]:
        """Update a VM device."""
        return await get_client().api.vm.device.update(vm, device_id, attributes)


# Register all write tools
_register_start_vm()
_register_stop_vm()
_register_restart_vm()
_register_poweroff_vm()
_register_suspend_vm()
_register_resume_vm()
_register_create_vm()
_register_delete_vm()
_register_update_vm()
_register_clone_vm()
_register_vm_device_create()
_register_vm_device_delete()
_register_vm_device_update()
