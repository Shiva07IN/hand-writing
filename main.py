"""
MUJ Assignment Agent - CLI Interface
Main entry point with beautiful Rich-powered terminal UI.

Usage:
    python main.py                          # Interactive mode
    python main.py solve <file>             # Solve an assignment file
    python main.py convert <file>           # Convert text to handwritten PDF
    python main.py full <file> [--subject]  # Full pipeline: read → solve → PDF
"""

import sys
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich import box

from config import INPUT_DIR, OUTPUT_DIR, FONTS_DIR, GEMINI_API_KEY
from assignment_reader import read_assignment, extract_questions
from ai_solver import solve_assignment, solve_individual_questions
from handwriting_generator import generate_handwritten_pdf

console = Console()

BANNER = r"""
[bold cyan]
  ╔══════════════════════════════════════════════════════════╗
  ║                                                          ║
  ║    ✍️  MUJ Assignment Agent                              ║
  ║    ─────────────────────────                             ║
  ║    Read → Solve → Handwritten PDF                        ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
[/bold cyan]
"""


def show_banner():
    """Display the application banner."""
    console.print(BANNER)


def check_setup():
    """Verify that all prerequisites are met."""
    issues = []
    
    # Check API key
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        issues.append("❌ GEMINI_API_KEY not configured in .env")
    else:
        issues.append("✅ Gemini API key configured")
    
    # Check fonts
    fonts = list(FONTS_DIR.glob("*.ttf")) + list(FONTS_DIR.glob("*.otf"))
    if fonts:
        issues.append(f"✅ Handwriting font found: {fonts[0].name}")
    else:
        issues.append("⚠️  No custom handwriting font (will use system fallback)")
        issues.append(f"   Place a .ttf font in: {FONTS_DIR}")
    
    # Check input directory
    input_files = list(INPUT_DIR.glob("*"))
    assignments = [f for f in input_files if f.suffix.lower() in (".pdf", ".docx", ".doc", ".txt")]
    issues.append(f"📁 Input folder: {len(assignments)} assignment file(s) found")
    
    panel = Panel(
        "\n".join(issues),
        title="[bold]System Check[/bold]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    
    return all("❌" not in i for i in issues)


def list_input_files() -> list[Path]:
    """List all assignment files in the input directory."""
    extensions = {".pdf", ".docx", ".doc", ".txt", ".md"}
    files = sorted([
        f for f in INPUT_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
    ])
    
    if not files:
        console.print(f"\n[yellow]No assignment files found in:[/yellow] {INPUT_DIR}")
        console.print(f"  Place your PDF/DOCX/TXT files there and try again.\n")
        return []
    
    table = Table(
        title="📄 Available Assignment Files",
        box=box.ROUNDED,
        border_style="cyan",
    )
    table.add_column("#", style="bold", width=4)
    table.add_column("Filename", style="green")
    table.add_column("Type", style="cyan")
    table.add_column("Size", justify="right", style="dim")
    
    for i, f in enumerate(files, 1):
        size_kb = f.stat().st_size / 1024
        table.add_row(
            str(i),
            f.name,
            f.suffix.upper(),
            f"{size_kb:.1f} KB",
        )
    
    console.print()
    console.print(table)
    
    return files


def select_file(files: list[Path]) -> Path | None:
    """Let the user select a file from the list."""
    if not files:
        return None
    
    choice = Prompt.ask(
        "\n[bold]Select file number[/bold]",
        choices=[str(i) for i in range(1, len(files) + 1)],
        default="1",
    )
    return files[int(choice) - 1]


def run_full_pipeline(file_path: Path, subject: str = ""):
    """Run the complete pipeline: Read → Solve → Generate PDF."""
    console.print("\n" + "═" * 60)
    console.print("[bold cyan]  📋 FULL PIPELINE: Read → Solve → Handwritten PDF[/bold cyan]")
    console.print("═" * 60)
    
    # Step 1: Read the assignment
    console.print("\n[bold]Step 1/3:[/bold] Reading assignment file...")
    raw_text = read_assignment(file_path)
    
    if not raw_text.strip():
        console.print("[red]Failed to extract text from the file.[/red]")
        return
    
    # Show preview
    preview = raw_text[:500] + ("..." if len(raw_text) > 500 else "")
    console.print(Panel(
        preview,
        title="[bold]Assignment Preview[/bold]",
        border_style="dim",
        padding=(1, 2),
    ))
    
    # Step 2: Solve with AI
    console.print("\n[bold]Step 2/3:[/bold] Solving with AI...")
    
    try:
        solved_text = solve_assignment(raw_text, subject)
    except Exception as e:
        console.print(f"[red]Failed to solve: {e}[/red]")
        return
    
    # Show solution preview
    sol_preview = solved_text[:600] + ("..." if len(solved_text) > 600 else "")
    console.print(Panel(
        sol_preview,
        title="[bold]Solution Preview[/bold]",
        border_style="green",
        padding=(1, 2),
    ))
    
    # Step 3: Generate handwritten PDF
    console.print("\n[bold]Step 3/3:[/bold] Generating handwritten PDF...")
    
    output_name = f"{file_path.stem}_solved.pdf"
    pdf_path = generate_handwritten_pdf(
        solved_text,
        output_filename=output_name,
        subject=subject,
        include_header=True,
    )
    
    # Also save the raw solution text
    txt_path = OUTPUT_DIR / f"{file_path.stem}_solution.txt"
    txt_path.write_text(solved_text, encoding="utf-8")
    
    # Done!
    console.print("\n" + "═" * 60)
    console.print("[bold green]  ✅ ASSIGNMENT COMPLETE![/bold green]")
    console.print("═" * 60)
    console.print(f"\n  📝 Handwritten PDF : [bold]{pdf_path}[/bold]")
    console.print(f"  📄 Raw solution    : [bold]{txt_path}[/bold]")
    console.print()


def run_convert_only(file_path: Path = None, text: str = None, subject: str = ""):
    """Convert existing text to handwritten PDF (no AI solving)."""
    console.print("\n[bold cyan]  ✍️ TEXT → HANDWRITTEN PDF[/bold cyan]\n")
    
    if file_path:
        text = read_assignment(file_path)
    elif not text:
        console.print("Enter/paste your text (press Enter twice to finish):")
        lines = []
        empty_count = 0
        while True:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append("")
            else:
                empty_count = 0
                lines.append(line)
        text = "\n".join(lines)
    
    if not text.strip():
        console.print("[red]No text provided.[/red]")
        return
    
    output_name = f"{file_path.stem}_handwritten.pdf" if file_path else "handwritten_output.pdf"
    
    pdf_path = generate_handwritten_pdf(
        text,
        output_filename=output_name,
        subject=subject,
        include_header=True,
    )
    
    console.print(f"\n[green]✅ Done![/green] PDF saved: [bold]{pdf_path}[/bold]\n")


def interactive_mode():
    """Run the interactive menu."""
    show_banner()
    
    if not check_setup():
        console.print("\n[yellow]Please fix the issues above before continuing.[/yellow]")
        console.print("Copy [bold].env.example[/bold] to [bold].env[/bold] and configure your settings.\n")
    
    while True:
        console.print()
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        table.add_column("Option", style="bold cyan", width=6)
        table.add_column("Description")
        
        table.add_row("[1]", "🚀 Full Pipeline (Read → Solve → Handwritten PDF)")
        table.add_row("[2]", "✍️  Convert Text → Handwritten PDF (no AI)")
        table.add_row("[3]", "🤖 Solve Only (just get AI answers, no PDF)")
        table.add_row("[4]", "📄 Read & Preview Assignment File")
        table.add_row("[5]", "⚙️  Check Setup")
        table.add_row("[0]", "🚪 Exit")
        
        console.print(Panel(table, title="[bold]Menu[/bold]", border_style="cyan"))
        
        choice = Prompt.ask("[bold]Choose option[/bold]", choices=["0", "1", "2", "3", "4", "5"], default="1")
        
        if choice == "0":
            console.print("\n[dim]Goodbye! 👋[/dim]\n")
            break
        
        elif choice == "1":
            files = list_input_files()
            file_path = select_file(files)
            if file_path:
                subject = Prompt.ask("[bold]Subject name[/bold] (optional)", default="")
                run_full_pipeline(file_path, subject)
        
        elif choice == "2":
            files = list_input_files()
            if files:
                use_file = Confirm.ask("Convert from a file?", default=True)
                if use_file:
                    file_path = select_file(files)
                    if file_path:
                        subject = Prompt.ask("[bold]Subject name[/bold] (optional)", default="")
                        run_convert_only(file_path=file_path, subject=subject)
                else:
                    run_convert_only()
            else:
                run_convert_only()
        
        elif choice == "3":
            files = list_input_files()
            file_path = select_file(files)
            if file_path:
                raw_text = read_assignment(file_path)
                if raw_text:
                    subject = Prompt.ask("[bold]Subject name[/bold] (optional)", default="")
                    try:
                        solved = solve_assignment(raw_text, subject)
                        out_path = OUTPUT_DIR / f"{file_path.stem}_solution.txt"
                        out_path.write_text(solved, encoding="utf-8")
                        console.print(Panel(
                            solved[:2000] + ("..." if len(solved) > 2000 else ""),
                            title="[bold green]Solution[/bold green]",
                            border_style="green",
                        ))
                        console.print(f"\n[green]Saved:[/green] {out_path}\n")
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
        
        elif choice == "4":
            files = list_input_files()
            file_path = select_file(files)
            if file_path:
                raw_text = read_assignment(file_path)
                if raw_text:
                    console.print(Panel(
                        raw_text[:3000] + ("..." if len(raw_text) > 3000 else ""),
                        title=f"[bold]{file_path.name}[/bold]",
                        border_style="cyan",
                    ))
                    questions = extract_questions(raw_text)
                    console.print(f"\n  [dim]Detected {len(questions)} question(s)[/dim]")
        
        elif choice == "5":
            check_setup()


def main():
    """Entry point."""
    args = sys.argv[1:]
    
    if not args:
        interactive_mode()
        return
    
    command = args[0].lower()
    
    if command == "full" and len(args) >= 2:
        file_path = Path(args[1])
        subject = args[3] if len(args) > 3 and args[2] == "--subject" else ""
        run_full_pipeline(file_path, subject)
    
    elif command == "solve" and len(args) >= 2:
        file_path = Path(args[1])
        raw_text = read_assignment(file_path)
        if raw_text:
            subject = args[3] if len(args) > 3 and args[2] == "--subject" else ""
            solved = solve_assignment(raw_text, subject)
            out_path = OUTPUT_DIR / f"{file_path.stem}_solution.txt"
            out_path.write_text(solved, encoding="utf-8")
            console.print(f"\n[green]Saved:[/green] {out_path}")
    
    elif command == "convert" and len(args) >= 2:
        file_path = Path(args[1])
        run_convert_only(file_path=file_path)
    
    elif command in ("help", "--help", "-h"):
        console.print(Panel(
            """[bold]Usage:[/bold]
  python main.py                          Interactive mode
  python main.py full <file> [--subject]  Full pipeline
  python main.py solve <file>             AI solve only
  python main.py convert <file>           Text → handwritten PDF""",
            title="[bold]MUJ Assignment Agent[/bold]",
            border_style="cyan",
        ))
    
    else:
        console.print(f"[red]Unknown command:[/red] {command}")
        console.print("Run [bold]python main.py --help[/bold] for usage.")


if __name__ == "__main__":
    main()
