"""Tests for the client wrapper."""

from __future__ import annotations

from truenas_mcp.client import build_filter_and, build_filter_or, build_filters, build_options


def test_build_filters():
    """Test filter building."""
    # Simple filters
    assert build_filters(name="test", status="active") == [
        ["name", "=", "test"],
        ["status", "=", "active"],
    ]

    # None values excluded
    assert build_filters(name="test", status=None) == [
        ["name", "=", "test"],
    ]

    # Empty
    assert build_filters() == []


def test_build_options():
    """Test options building."""
    assert build_options(limit=10, offset=5) == {"limit": 10, "offset": 5}
    assert build_options(limit=10) == {"limit": 10}
    assert build_options(offset=5) == {"offset": 5}
    assert build_options(order_by="name") == {"order_by": "name"}
    assert build_options(select=["id", "name"]) == {"select": ["id", "name"]}
    assert build_options(count=True) == {"count": True}
    assert build_options() == {}


def test_build_filter_or():
    """Test OR filter building."""
    assert build_filter_or() == []
    # Single condition returned as-is
    assert build_filter_or(["name", "=", "a"]) == ["name", "=", "a"]
    # Multiple conditions wrapped in OR
    assert build_filter_or(["name", "=", "a"], ["name", "=", "b"]) == [
        "OR",
        ["name", "=", "a"],
        ["name", "=", "b"],
    ]


def test_build_filter_and():
    """Test AND filter building."""
    assert build_filter_and() == []
    # Single condition returned as-is
    assert build_filter_and(["name", "=", "a"]) == ["name", "=", "a"]
    # Multiple conditions wrapped in AND
    assert build_filter_and(["name", "=", "a"], ["status", "=", "active"]) == [
        "AND",
        ["name", "=", "a"],
        ["status", "=", "active"],
    ]
