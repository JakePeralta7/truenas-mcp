"""WebSocket JSON-RPC client wrapper for TrueNAS middleware.

Provides a small wrapper around `pytruenas.TrueNASClient` so domain
helpers never touch the raw client directly. Handles connection lifecycle,
error conversion, and provides query/filter helpers.
"""

from __future__ import annotations

from typing import Any

from pytruenas import TrueNASClient


class TruenasError(Exception):
    """Wrapper for TrueNAS errors to avoid importing pytruenas in server.py."""
    pass


# Re-export for convenience
__all__ = [
    "TruenasClientWrapper",
    "TruenasError",
    "create_client",
    "build_filters",
    "build_options",
    "build_filter_or",
    "build_filter_and",
]


class TruenasClientWrapper:
    """Wrapper around TrueNASClient providing synchronous API access."""

    def __init__(self, client: TrueNASClient):
        self._client = client

    @property
    def api(self):
        return self._client.api

    def query(self, namespace: str, method: str, *args, **kwargs):
        """Call a query method on the API namespace (synchronous)."""
        api_ns = getattr(self._client.api, namespace)
        meth = getattr(api_ns, method)
        return meth(*args, **kwargs)


def _create_client_async(settings) -> TrueNASClient:
    """Create and authenticate a TrueNASClient."""
    from pytruenas.auth import Credentials

    if settings.local:
        # Local connection via unix socket - no auth needed
        client = TrueNASClient()
    else:
        client = TrueNASClient(
            settings.url,
            verify=settings.verify_ssl,
        )
        # Create credentials with API key (and optional username)
        creds = Credentials.from_host_credentials(
            username=settings.username,
            api_key=settings.api_key,
        )
        client.login(creds)
    return client


def create_client(settings) -> TruenasClientWrapper:
    """Create a TrueNASClientWrapper with authenticated connection."""
    client = _create_client_async(settings)
    return TruenasClientWrapper(client)


def build_filters(**kwargs: Any) -> list[list]:
    """Convert keyword args to TrueNAS filter format.
    
    Example:
        build_filters(name="mypool", status="HEALTHY")
        -> [["name", "=", "mypool"], ["status", "=", "HEALTHY"]]
    """
    filters = []
    for k, v in kwargs.items():
        if v is not None:
            filters.append([k, "=", v])
    return filters


def build_options(
    limit: int | None = None,
    offset: int | None = None,
    order_by: str | list[str] | None = None,
    select: list[str] | None = None,
    count: bool = False,
) -> dict[str, Any]:
    """Build query options dict for TrueNAS API."""
    opts: dict[str, Any] = {}
    if limit is not None:
        opts["limit"] = limit
    if offset is not None:
        opts["offset"] = offset
    if order_by is not None:
        opts["order_by"] = order_by
    if select is not None:
        opts["select"] = select
    if count:
        opts["count"] = True
    return opts


def build_filter_or(
    *conditions: list[list],
) -> list:
    """Build an OR filter from multiple conditions.
    
    Example:
        build_filter_or(
            ["name", "=", "pool1"],
            ["name", "=", "pool2"]
        )
        -> [["OR", [["name", "=", "pool1"]], [["name", "=", "pool2"]]]]
    """
    if not conditions:
        return []
    if len(conditions) == 1:
        return conditions[0]
    result: list = ["OR"]
    for cond in conditions:
        result.append(cond)
    return result


def build_filter_and(
    *conditions: list[list],
) -> list:
    """Build an AND filter from multiple conditions."""
    if not conditions:
        return []
    if len(conditions) == 1:
        return conditions[0]
    result: list = ["AND"]
    for cond in conditions:
        result.append(cond)
    return result
