"""truenas-mcp: an MCP server (stdio) for the TrueNAS WebSocket JSON-RPC API.

Configuration comes exclusively from environment variables; a single TrueNASClient
is created at startup. Domain helpers and tool registrations live in
``truenas_mcp.helpers.*`` and are imported here for side effects (registering
tools on the shared ``mcp`` server).
"""

from __future__ import annotations

import logging
import os
import threading
import uuid
from collections.abc import Callable, Mapping
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from truenas_mcp.client import TruenasClientWrapper, create_client

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}

READ_ONLY = ToolAnnotations(read_only_hint=True)

_DEFAULT_TIMEOUT = 30.0

_NAME = "truenas-mcp"
_VERSION = "0.1.0"

# Correlation ID for request tracing
correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)

# Module logger
logger = logging.getLogger(__name__)

# Global read-only mode flag (set in main() after loading settings)
READ_ONLY_MODE = False


@dataclass(frozen=True)
class Settings:
    url: str | None
    api_key: str | None
    username: str | None
    verify_ssl: bool
    timeout: float
    local: bool
    read_only: bool = False


def env_bool(name: str, env: Mapping[str, str], default: bool) -> bool:
    raw = env.get(name)
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise RuntimeError(f"Invalid boolean for {name}: {raw!r} (use true/false/1/0)")


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if env is None else env

    local = env_bool("TRUENAS_LOCAL", env, False)

    if local:
        # Local connection doesn't need URL or API key
        url = None
        api_key = None
        username = None
    else:
        url = env.get("TRUENAS_URL", "").strip()
        api_key = env.get("TRUENAS_API_KEY", "").strip()
        username = env.get("TRUENAS_USERNAME", "").strip() or None

        if not url:
            raise RuntimeError("TRUENAS_URL is required (or set TRUENAS_LOCAL=true)")
        if not api_key:
            raise RuntimeError("TRUENAS_API_KEY is required (or set TRUENAS_LOCAL=true)")

    timeout_raw = env.get("TRUENAS_TIMEOUT", "").strip()
    try:
        timeout = float(timeout_raw) if timeout_raw else _DEFAULT_TIMEOUT
    except ValueError:
        raise RuntimeError(f"Invalid TRUENAS_TIMEOUT: {timeout_raw!r}") from None
    if timeout <= 0:
        raise RuntimeError(f"TRUENAS_TIMEOUT must be positive: {timeout!r}")

    verify_ssl = env_bool("TRUENAS_VERIFY_SSL", env, True)
    read_only = env_bool("TRUENAS_READ_ONLY", env, False)

    return Settings(
        url=url.rstrip("/") if url else None,
        api_key=api_key,
        username=username,
        verify_ssl=verify_ssl,
        timeout=timeout,
        local=local,
        read_only=read_only,
    )


_client: TruenasClientWrapper | None = None
_client_lock = threading.Lock()


def set_client(client: TruenasClientWrapper | None) -> None:
    global _client
    _client = client


def get_client() -> TruenasClientWrapper:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = create_client(load_settings())
    return _client


def new_correlation_id() -> str:
    """Generate a new correlation ID for request tracing."""
    return uuid.uuid4().hex[:12]


def set_correlation_id(cid: str | None = None) -> str:
    """Set and return a correlation ID (generates new if not provided)."""
    cid = cid or new_correlation_id()
    correlation_id.set(cid)
    return cid


def get_correlation_id() -> str | None:
    """Get the current correlation ID."""
    return correlation_id.get()


def truenas_errors(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Convert TrueNAS/network/validation errors into RuntimeError (MCP isError)."""

    @wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        cid = set_correlation_id()
        logger.debug("tool_call_start", extra={"correlation_id": cid, "tool": fn.__name__, "args": _safe_args(args, kwargs)})
        try:
            result = await fn(*args, **kwargs)
            logger.debug("tool_call_end", extra={"correlation_id": cid, "tool": fn.__name__, "success": True})
            return result
        except Exception as exc:
            # Import here to avoid circular import
            from truenas_mcp.client import TruenasError
            if isinstance(exc, TruenasError):
                logger.error("tool_call_error", extra={"correlation_id": cid, "tool": fn.__name__, "error": str(exc)})
                raise RuntimeError(str(exc)) from exc
            logger.error("tool_call_error", extra={"correlation_id": cid, "tool": fn.__name__, "error": str(exc)})
            raise RuntimeError(str(exc).strip() or exc.__class__.__name__) from exc

    return wrapper


def _safe_args(args: tuple, kwargs: dict) -> dict:
    """Return a safe representation of args for logging (redact sensitive data)."""
    safe = {}
    for i, arg in enumerate(args):
        if isinstance(arg, str) and ("token" in arg.lower() or "secret" in arg.lower() or "password" in arg.lower() or "key" in arg.lower()):
            safe[f"arg_{i}"] = "[REDACTED]"
        else:
            safe[f"arg_{i}"] = str(arg)[:200]
    for k, v in kwargs.items():
        if "token" in k.lower() or "secret" in k.lower() or "password" in k.lower() or "key" in k.lower():
            safe[k] = "[REDACTED]"
        else:
            safe[k] = str(v)[:200]
    return safe


mcp = MCPServer(_NAME)


# Import domain modules for their `@mcp.tool` registration side effects.
# (Order matters only for readability; each module imports `mcp` and `get_client`
#  from this server module.)
from truenas_mcp.helpers import app, filesystem, pool, sharing, system, user, vm  # noqa: E402,F401


def main() -> None:
    global _client, READ_ONLY_MODE
    settings = load_settings()
    READ_ONLY_MODE = settings.read_only

    # Configure logging to stderr (never stdout for stdio transport)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s [%(correlation_id)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )

    logger.info("server_start", extra={"correlation_id": "init", "read_only": READ_ONLY_MODE, "version": _VERSION, "local": settings.local})

    _client = create_client(settings)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
