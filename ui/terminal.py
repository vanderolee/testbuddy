"""
Terminal UI module with colored output.
"""
import os
from typing import Dict
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


console = Console()


def clear_screen() -> None:
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header() -> None:
    """Print application header."""
    header = Text("TestBuddy", style="bold cyan")
    console.print(Panel(header, border_style="cyan"))


def print_question(question_data: Dict) -> None:
    """
    Print formatted question.

    Args:
        question_data: Dictionary with 'question' and 'options' keys
    """
    question = question_data.get("question", "")
    options = question_data.get("options", [])

    # Print question
    console.print("\n[bold yellow]QUESTION:[/bold yellow]")
    console.print(question)

    # Print options (without marks yet)
    if options:
        console.print("\n[bold yellow]OPTIONS:[/bold yellow]")
        for opt in options:
            console.print(f"  {opt['label']}) {opt['text']}")


def print_answer(question_data: Dict, answer_data: Dict) -> None:
    """
    Print formatted answer with marked options.

    Args:
        question_data: Dictionary with 'question' and 'options' keys
        answer_data: Dictionary with 'correct_options' and 'explanation' keys
    """
    question = question_data.get("question", "")
    options = question_data.get("options", [])
    correct_options = answer_data.get("correct_options", [])
    explanation = answer_data.get("explanation", "")

    # Print question
    console.print("\n[bold yellow]QUESTION:[/bold yellow]")
    console.print(question)

    # Print options with marks
    if options:
        console.print("\n[bold yellow]OPTIONS:[/bold yellow]")
        for opt in options:
            label = opt['label']
            text = opt['text']

            if label in correct_options:
                console.print(f"  [green]✓ {label}) {text}[/green]")
            else:
                console.print(f"  [dim]✗ {label}) {text}[/dim]")

    # Print explanation
    if explanation:
        console.print("\n[bold yellow]EXPLANATION:[/bold yellow]")
        console.print(explanation)


def print_token_summary(summary: dict, request_tokens: dict = None) -> None:
    """
    Print token usage summary.

    Args:
        summary: Session summary from TokenTracker.get_summary()
        request_tokens: Optional current request token counts
    """
    console.print("\n" + "═" * 80)

    if request_tokens:
        req_total = request_tokens.get('input_tokens', 0) + request_tokens.get('output_tokens', 0)
        req_cost = (request_tokens.get('input_tokens', 0) / 1_000_000 * 3.0) + \
                   (request_tokens.get('output_tokens', 0) / 1_000_000 * 15.0)

        console.print(
            f"[cyan]This Request:[/cyan] {req_total:,} tokens | ${req_cost:.4f}"
        )

    console.print(
        f"[cyan]Session Total:[/cyan] {summary['total_tokens']:,} tokens | "
        f"${summary['total_cost']:.4f} | "
        f"{summary['requests']} requests"
    )
    console.print("═" * 80)


def print_waiting_message(trigger_key: str = "Cmd+Shift+F1", quit_key: str = "Cmd+Shift+Q") -> None:
    """
    Print waiting message with instructions.

    Args:
        trigger_key: Hotkey for triggering capture
        quit_key: Hotkey for quitting
    """
    console.print(
        f"\n[dim]Waiting for trigger... ({trigger_key} to capture, {quit_key} to quit)[/dim]"
    )


def print_processing() -> None:
    """Print processing message."""
    console.print("\n[yellow]Processing...[/yellow]")


def print_error(message: str) -> None:
    """
    Print error message.

    Args:
        message: Error message to display
    """
    console.print(f"\n[bold red]ERROR:[/bold red] {message}")


def print_success(message: str) -> None:
    """
    Print success message.

    Args:
        message: Success message to display
    """
    console.print(f"\n[bold green]✓[/bold green] {message}")


def print_welcome(trigger_key: str, quit_key: str, browser: str) -> None:
    """
    Print welcome message with configuration.

    Args:
        trigger_key: Hotkey for triggering capture
        quit_key: Hotkey for quitting
        browser: Target browser name
    """
    clear_screen()
    print_header()

    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Target Browser: [cyan]{browser}[/cyan]")
    console.print(f"  Trigger Key: [cyan]{trigger_key}[/cyan]")
    console.print(f"  Quit Key: [cyan]{quit_key}[/cyan]")

    print_waiting_message(trigger_key, quit_key)
