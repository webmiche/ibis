from __future__ import annotations

import sys
from importlib.metadata import EntryPoint
from typing import NamedTuple

import pytest

import ibis
from ibis.backends.base import BaseBackend


def test_backends_are_cached():
    assert isinstance(ibis.sqlite, BaseBackend)
    del ibis.sqlite  # delete to force recreation
    assert isinstance(ibis.sqlite, BaseBackend)
    assert ibis.sqlite is ibis.sqlite


def test_backends_tab_completion():
    assert isinstance(ibis.sqlite, BaseBackend)
    del ibis.sqlite  # delete to ensure not real attr
    assert "sqlite" in dir(ibis)
    assert isinstance(ibis.sqlite, BaseBackend)
    assert "sqlite" in dir(ibis)  # in dir even if already created


def test_missing_backend():
    msg = "If you are trying to access the 'foo' backend"
    with pytest.raises(AttributeError, match=msg):
        ibis.foo


def test_multiple_backends(mocker):
    class Distribution(NamedTuple):
        entry_points: list[EntryPoint]

    entrypoints = [
        EntryPoint(
            name="foo",
            value='ibis.backends.backend1',
            group="ibis.backends",
        ),
        EntryPoint(
            name="foo",
            value='ibis.backends.backend2',
            group="ibis.backends",
        ),
    ]
    if sys.version_info < (3, 10):
        return_value = {"ibis.backends": entrypoints}
    else:
        return_value = entrypoints

    mocker.patch("importlib.metadata.entry_points", return_value=return_value)

    msg = r"\d+ packages found for backend 'foo'"
    with pytest.raises(RuntimeError, match=msg):
        ibis.foo
