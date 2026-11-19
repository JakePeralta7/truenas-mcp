"""System, hardware, disk, network, and certificate management tools."""

from __future__ import annotations

from typing import Any

from truenas_mcp.client import build_filters, build_options
from truenas_mcp.server import READ_ONLY, READ_ONLY_MODE, get_client, logger, mcp, truenas_errors

# --- System Info Tools ---

@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def system_info() -> dict[str, Any]:
    """Get general system information."""
    return get_client().api.system.info()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def system_general_config() -> dict[str, Any]:
    """Get general system configuration."""
    return get_client().api.system.general.config()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def system_security_info() -> dict[str, Any]:
    """Get security information."""
    return get_client().api.system.security.info()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def system_security_config() -> dict[str, Any]:
    """Get security configuration."""
    return get_client().api.system.security.config()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def system_ntp_servers() -> list[dict[str, Any]]:
    """List NTP servers."""
    return get_client().api.system.ntpserver.query()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def system_country_choices() -> list[dict[str, Any]]:
    """Get available country choices."""
    return get_client().api.system.general.country_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def system_fips_available() -> bool:
    """Check if FIPS is available."""
    return get_client().api.system.security.info.fips_available()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def system_fips_enabled() -> bool:
    """Check if FIPS is enabled."""
    return get_client().api.system.security.info.fips_enabled()


def _register_reboot():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "reboot", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def reboot(delay: int = 0) -> dict[str, Any]:
        """Reboot the system.
        
        Args:
            delay: Delay in seconds
        """
        return await get_client().api.system.reboot(delay)


def _register_shutdown():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "shutdown", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def shutdown(delay: int = 0) -> dict[str, Any]:
        """Shutdown the system.
        
        Args:
            delay: Delay in seconds
        """
        return await get_client().api.system.shutdown(delay)


def _register_update_general():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "update_system_general", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def update_system_general(**kwargs) -> dict[str, Any]:
        """Update general system configuration.
        
        Args:
            **kwargs: Properties to update (hostname, language, timezone, etc.)
        """
        return await get_client().api.system.general.update(kwargs)


def _register_update_security():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "update_system_security", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def update_system_security(**kwargs) -> dict[str, Any]:
        """Update system security configuration."""
        return await get_client().api.system.security.update(kwargs)


def _register_create_ntp_server():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "create_ntp_server", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def create_ntp_server(
        address: str,
        burst: bool = False,
        iburst: bool = True,
        prefer: bool = False,
        minpoll: int = 6,
        maxpoll: int = 10,
    ) -> dict[str, Any]:
        """Create an NTP server configuration."""
        body = {
            "address": address,
            "burst": burst,
            "iburst": iburst,
            "prefer": prefer,
            "minpoll": minpoll,
            "maxpoll": maxpoll,
        }
        return await get_client().api.system.ntpserver.create(body)


def _register_delete_ntp_server():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "delete_ntp_server", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def delete_ntp_server(id: int) -> dict[str, Any]:
        """Delete an NTP server configuration."""
        return await get_client().api.system.ntpserver.delete(id)


# --- Disk Tools ---

def do_list_disks(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.disk.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_disks(
    name: str | None = None,
    serial: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List physical disks.
    
    Args:
        name: Filter by disk name (e.g., ada0, nvme0)
        serial: Filter by serial number
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name, serial=serial)
    options = build_options(limit=limit, offset=offset)
    return do_list_disks(get_client(), filters or None, options or None)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def disk_temperature_alerts() -> dict[str, Any]:
    """Get disk temperature alerts."""
    return get_client().api.disk.temperature_alerts()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def disk_get_info(name: str) -> dict[str, Any]:
    """Get detailed information for a specific disk."""
    return get_client().api.device.get_info(name)


# --- Network Interface Tools ---

def do_list_interfaces(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.interface.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_interfaces(
    name: str | None = None,
    type: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List network interfaces.
    
    Args:
        name: Filter by interface name
        type: Filter by type (PHYSICAL, VLAN, BRIDGE, LAGG, etc.)
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name, type=type)
    options = build_options(limit=limit, offset=offset)
    return do_list_interfaces(get_client(), filters or None, options or None)


# --- Certificate Tools ---

def do_list_certificates(client, filters=None, options=None) -> list[dict[str, Any]]:
    kwargs = {}
    if filters:
        kwargs["filters"] = filters
    if options:
        kwargs["options"] = options
    return client.api.certificate.query(**kwargs)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_certificates(
    name: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """List SSL certificates.
    
    Args:
        name: Filter by certificate name
        limit: Maximum number of results
        offset: Number of results to skip
    """
    filters = build_filters(name=name)
    options = build_options(limit=limit, offset=offset)
    return do_list_certificates(get_client(), filters or None, options or None)


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def certificate_acme_server_choices() -> list[dict[str, Any]]:
    """Get available ACME server choices."""
    return get_client().api.certificate.acme_server_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def certificate_country_choices() -> list[dict[str, Any]]:
    """Get available country choices for certificates."""
    return get_client().api.certificate.country_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def certificate_ec_curve_choices() -> list[dict[str, Any]]:
    """Get available EC curve choices."""
    return get_client().api.certificate.ec_curve_choices()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def certificate_extended_key_usage_choices() -> list[dict[str, Any]]:
    """Get available extended key usage choices."""
    return get_client().api.certificate.extended_key_usage_choices()


def _register_create_certificate():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "create_certificate", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def create_certificate(
        name: str,
        type: str,  # CERTIFICATE, CSR, etc.
        country: str,
        state: str,
        city: str,
        organization: str,
        organizational_unit: str | None = None,
        common_name: str | None = None,
        email: str | None = None,
        key_type: str = "RSA",
        key_length: int = 2048,
        ec_curve: str | None = None,
        san: list[str] | None = None,
        extended_key_usage: list[str] | None = None,
        lifetime: int = 365,
    ) -> dict[str, Any]:
        """Create a certificate or CSR.
        
        Args:
            name: Certificate name
            type: CERTIFICATE or CSR
            country: Country code
            state: State/province
            city: City
            organization: Organization
            organizational_unit: Organizational unit
            common_name: Common name
            email: Email address
            key_type: RSA or EC
            key_length: RSA key length
            ec_curve: EC curve (if EC)
            san: Subject Alternative Names
            extended_key_usage: Extended key usages
            lifetime: Certificate lifetime in days
        """
        body = {
            "name": name,
            "type": type,
            "country": country,
            "state": state,
            "city": city,
            "organization": organization,
            "key_type": key_type,
            "key_length": key_length,
            "lifetime": lifetime,
        }
        if organizational_unit:
            body["organizational_unit"] = organizational_unit
        if common_name:
            body["common_name"] = common_name
        if email:
            body["email"] = email
        if ec_curve:
            body["ec_curve"] = ec_curve
        if san:
            body["san"] = san
        if extended_key_usage:
            body["extended_key_usage"] = extended_key_usage
        return await get_client().api.certificate.create(body)


def _register_delete_certificate():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "delete_certificate", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def delete_certificate(id: int) -> dict[str, Any]:
        """Delete a certificate."""
        return await get_client().api.certificate.delete(id)


# --- IPMI Tools ---

@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def ipmi_is_loaded() -> bool:
    """Check if IPMI is loaded."""
    return get_client().api.ipmi.is_loaded()


# --- Boot Environment Tools ---

@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def list_boot_environments() -> list[dict[str, Any]]:
    """List boot environments."""
    return get_client().api.boot.environment.query()


@mcp.tool(annotations=READ_ONLY)
@truenas_errors
async def get_boot_environment(name: str) -> dict[str, Any]:
    """Get boot environment details."""
    return get_client().api.boot.environment.get_instance(name)


def _register_activate_boot_environment():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "activate_boot_environment", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def activate_boot_environment(name: str, reboot: bool = False) -> dict[str, Any]:
        """Activate a boot environment.
        
        Args:
            name: Boot environment name
            reboot: Reboot after activation
        """
        return await get_client().api.boot.environment.activate(name, reboot)


def _register_create_boot_environment():
    if READ_ONLY_MODE:
        logger.info("skipping_write_tool", extra={"tool": "create_boot_environment", "reason": "read_only_mode"})
        return

    @mcp.tool()
    async def create_boot_environment(name: str, source: str | None = None) -> dict[str, Any]:
        """Create a boot environment.
        
        Args:
            name: New boot environment name
            source: Source boot environment (optional)
        """
        body = {"name": name}
        if source:
            body["source"] = source
        return await get_client().api.boot.environment.create(body)


# Register all write tools
_register_reboot()
_register_shutdown()
_register_update_general()
_register_update_security()
_register_create_ntp_server()
_register_delete_ntp_server()
_register_create_certificate()
_register_delete_certificate()
_register_activate_boot_environment()
_register_create_boot_environment()
