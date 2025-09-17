"""Routes package utilities: centralized blueprint registration.

Auto-discovers Flask Blueprint instances in modules under app.routes and
registers them with the provided url_prefix.
"""

from __future__ import annotations

import importlib
import pkgutil
from flask import Blueprint, Flask

def register_blueprints(
    app: Flask, package: str = "app.routes", url_prefix: str = "/api"
) -> None:
    """Import all modules in the routes package and register any Blueprint instances found.

    - Discovers modules via pkgutil (excluding subpackages by default)
    - Registers attributes that are instances of flask.Blueprint
    - Applies a common url_prefix (default: /api)
    """
    pkg = importlib.import_module(package)
    # pkg.__path__ is a list-like of paths where the package's modules live
    for _finder, mod_name, is_pkg in pkgutil.iter_modules(pkg.__path__):  # type: ignore[attr-defined]
        if is_pkg or mod_name.startswith("_"):
            continue
        module = importlib.import_module(f"{package}.{mod_name}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, Blueprint):
                app.register_blueprint(attr, url_prefix=url_prefix)
