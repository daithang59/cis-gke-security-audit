"""Smoke tests verifying that the package and its submodules import cleanly."""

import importlib

import cis_gke_audit


def test_package_import_and_version():
    """Verify that cis_gke_audit can be imported and has a valid version."""
    assert hasattr(cis_gke_audit, "__version__")
    assert isinstance(cis_gke_audit.__version__, str)
    assert len(cis_gke_audit.__version__) > 0


def test_submodules_importable():
    """Verify that all core subpackages can be imported without error."""
    submodules = [
        "cis_gke_audit.collectors",
        "cis_gke_audit.evaluation",
        "cis_gke_audit.normalizers",
        "cis_gke_audit.reporting",
        "cis_gke_audit.rules",
        "cis_gke_audit.cli",
    ]
    for mod_name in submodules:
        mod = importlib.import_module(mod_name)
        assert mod is not None
