import json
import click
from rich.console import Console
from rich.panel import Panel
from .plan_reviewer import PlanReviewer
from .troubleshooter import CITroubleshooter
from .human_approval_gate import HumanApprovalGate

console = Console()

@click.group()
def cli():
    """Agentic AI DevSecOps Companion for Terraform & CI/CD Pipelines."""
    pass

@cli.command()
@click.option("--plan", "-p", required=True, help="Path to Terraform plan JSON file.")
@click.option("--output", "-o", help="Optional path to output markdown report.")
def review(plan, output):
    """Review Terraform plan JSON, calculate blast radius, and evaluate security risk."""
    console.print(Panel.fit("[bold purple]🤖 Agentic AI Terraform Reviewer[/bold purple]\n[dim]Analyzing plan blast radius and security posture...[/dim]"))
    with open(plan, "r", encoding="utf-8") as f:
        data = json.load(f)

    reviewer = PlanReviewer(data)
    result = reviewer.analyze()

    markdown_report = HumanApprovalGate.generate_pr_comment(result)
    console.print(markdown_report)

    if output:
        with open(output, "w", encoding="utf-8") as out_f:
            out_f.write(markdown_report)
        console.print(f"\n[green]Report written to {output}[/green]")

@cli.command()
@click.option("--log", "-l", required=True, help="Path to CI/CD failure log file.")
def troubleshoot(log):
    """Diagnose CI/CD failure logs and provide automated root cause remediation."""
    console.print(Panel.fit("[bold blue]🔍 Agentic AI CI/CD Troubleshooter[/bold blue]\n[dim]Parsing execution logs for root cause...[/dim]"))
    with open(log, "r", encoding="utf-8") as f:
        content = f.read()

    troubleshooter = CITroubleshooter()
    diagnosis = troubleshooter.diagnose(content)

    console.print(f"\n[bold red]Issue Detected:[/bold red] {diagnosis['title']}")
    console.print(f"[bold yellow]Root Cause:[/bold yellow] {diagnosis['root_cause']}")
    console.print(f"\n[bold green]Recommended Fix:[/bold green]\n{diagnosis['remediation']}")

if __name__ == "__main__":
    cli()
