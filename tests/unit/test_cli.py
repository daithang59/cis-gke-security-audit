from typer.testing import CliRunner
from cis_gke_audit.cli import app

runner = CliRunner()


def test_cli_list_rules():
    result = runner.invoke(app, ["list-rules"])
    assert result.exit_code == 0
    assert "Registered CIS Benchmark Rules" in result.stdout


def test_cli_audit_help():
    result = runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "--project" in result.stdout
