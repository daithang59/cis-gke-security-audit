import re

from typer.testing import CliRunner

from cis_gke_audit.cli import app

runner = CliRunner()


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)


def test_cli_list_rules():
    result = runner.invoke(app, ["list-rules"], env={"NO_COLOR": "1"})
    assert result.exit_code == 0
    assert "Registered CIS Benchmark Rules" in _strip_ansi(result.stdout)


def test_cli_audit_help():
    result = runner.invoke(app, ["audit", "--help"], env={"NO_COLOR": "1"})
    assert result.exit_code == 0
    clean_stdout = _strip_ansi(result.stdout)
    assert "--project" in clean_stdout
    assert "--cluster" in clean_stdout
    assert "--location" in clean_stdout
