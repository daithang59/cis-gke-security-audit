"""CLI entrypoint for CIS GKE Security Audit."""

import typer
from rich.console import Console

app = typer.Typer(
    name="cis-gke-audit",
    help="CIS Benchmark Security Audit tool for Google Kubernetes Engine (GKE)",
)
console = Console()


@app.command()
def audit(
    project_id: str = typer.Option(..., "--project", "-p", help="GCP Project ID"),
    cluster_name: str = typer.Option(..., "--cluster", "-c", help="GKE Cluster Name"),
    location: str = typer.Option(..., "--location", "-l", help="GKE Region or Zone"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, md"),
) -> None:
    """Run CIS benchmark audit against a GKE cluster."""
    console.print("[bold green]Starting CIS GKE Security Audit[/bold green]")
    console.print(f"Project: [cyan]{project_id}[/cyan] | Cluster: [cyan]{cluster_name}[/cyan] ({location})")
    console.print(f"Format: [yellow]{output_format}[/yellow]")
    console.print("[dim]Audit engine initialized. Ready to execute collectors and evaluation rules.[/dim]")


@app.command()
def list_rules() -> None:
    """List available CIS GKE benchmark rules."""
    console.print("[bold blue]Registered CIS Benchmark Rules:[/bold blue]")
    console.print("- Section 5.1: Control Plane & Cluster Configuration")
    console.print("- Section 5.2: Worker Nodes & Host Security")
    console.print("- Section 5.3: Network Policies & VPC Configuration")
    console.print("- Section 5.4: IAM & Service Account Access Controls")


if __name__ == "__main__":
    app()
