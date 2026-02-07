import importlib.metadata

import typing as t


def _get_version() -> str:
    package_name: str = __name__.split(".")[0]
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        pass
    return "unknown"


__version__: t.Final[str] = _get_version()

__all__ = [
    "__version__",
]
