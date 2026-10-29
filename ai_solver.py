"""
MUJ Assignment Agent - AI Solver
Uses Google Gemini API to solve assignment questions.
"""

import google.generativeai as genai
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from config import GEMINI_API_KEY, GEMINI_MODEL, STUDENT_NAME, STUDENT_REG_NO, STUDENT_COURSE, STUDENT_SECTION

console = Console()


def configure_gemini():
    """Initialize the Gemini API client."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        console.print("[red]Error:[/red] GEMINI_API_KEY not set in .env file!")
        console.print("  Get your free API key at: [link=https://aistudio.google.com/apikey]https://aistudio.google.com/apikey[/link]")
        raise ValueError("Missing GEMINI_API_KEY")
    
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel(GEMINI_MODEL)


SYSTEM_PROMPT = """You are a diligent university student writing assignment answers by hand.

RULES:
1. Write clear, well-structured answers appropriate for a university assignment.
2. For theory questions: provide comprehensive but concise answers with key points.
3. For math/science problems: show complete step-by-step working with formulas.
4. For programming questions: write clean, commented code with brief explanations.
5. Use proper formatting:
   - Start each answer with the question number (e.g., "Q1." or "Ans 1.")
   - Use bullet points or numbered lists where appropriate
   - Underline or emphasize key terms by wrapping them in *asterisks*
6. Keep language natural — like a student writing by hand, not a textbook.
7. Be accurate and thorough but avoid unnecessary filler.
8. For diagrams or figures, describe them textually (e.g., "[Diagram: ...]").
9. DO NOT use markdown headers (##), tables, or complex formatting.
   Use plain text with simple indentation and line breaks.
10. Keep line lengths reasonable (60-70 characters max) since this will be
    rendered as handwriting on A4 paper.

Student Info:
- Name: {student_name}
- Reg No: {student_reg_no}
- Course: {student_course}
- Section: {student_section}
"""


def solve_assignment(questions_text: str, subject: str = "") -> str:
    """
    Send the assignment questions to Gemini and get solved answers.
    
    Args:
        questions_text: The full text of the assignment questions
        subject: Optional subject name for context
    
    Returns:
        The solved assignment text
    """
    model = configure_gemini()
    
    system = SYSTEM_PROMPT.format(
        student_name=STUDENT_NAME,
        student_reg_no=STUDENT_REG_NO,
        student_course=STUDENT_COURSE,
        student_section=STUDENT_SECTION,
    )
    
    user_prompt = f"""Please solve the following assignment completely.
{"Subject: " + subject if subject else ""}

ASSIGNMENT QUESTIONS:
{questions_text}

Write complete, well-formatted answers for each question.
Remember to show all working for mathematical problems and write
clean code for programming questions. Keep the tone natural,
like a student writing by hand.
"""

    console.print("\n[cyan]🤖 Solving with Gemini AI...[/cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Thinking...", total=None)
        
        try:
            response = model.generate_content(
                [system, user_prompt],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=8192,
                ),
            )
            progress.update(task, description="Done!")
        except Exception as e:
            progress.update(task, description=f"[red]Error![/red]")
            console.print(f"\n[red]Gemini API Error:[/red] {e}")
            raise
    
    solved_text = response.text
    
    # Clean up any markdown artifacts that slipped through
    solved_text = solved_text.replace("```", "")
    solved_text = solved_text.replace("**", "*")
    
    word_count = len(solved_text.split())
    console.print(f"  [green]✓[/green] Generated {word_count} words of answers")
    
    return solved_text


def solve_individual_questions(questions: list[str], subject: str = "") -> list[str]:
    """
    Solve each question individually for better accuracy.
    
    Args:
        questions: List of individual question strings
        subject: Optional subject name
    
    Returns:
        List of answer strings
    """
    model = configure_gemini()
    answers = []
    
    system = SYSTEM_PROMPT.format(
        student_name=STUDENT_NAME,
        student_reg_no=STUDENT_REG_NO,
        student_course=STUDENT_COURSE,
        student_section=STUDENT_SECTION,
    )
    
    console.print(f"\n[cyan]🤖 Solving {len(questions)} questions individually...[/cyan]")
    
    for i, question in enumerate(questions, 1):
        console.print(f"\n  [dim]Question {i}/{len(questions)}[/dim]")
        
        user_prompt = f"""Solve this assignment question completely.
{"Subject: " + subject if subject else ""}

QUESTION:
{question}

Write a complete, well-formatted answer.
Show all working for math. Write clean code for programming.
Keep the tone natural — like a student writing by hand.
Keep line lengths under 65 characters.
"""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"  Solving Q{i}...", total=None)
            
            try:
                response = model.generate_content(
                    [system, user_prompt],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=4096,
                    ),
                )
                progress.update(task, description=f"  [green]Q{i} done![/green]")
            except Exception as e:
                progress.update(task, description=f"  [red]Q{i} failed![/red]")
                console.print(f"  [red]Error on Q{i}:[/red] {e}")
                answers.append(f"[Error solving Q{i}]")
                continue
        
        answer = response.text.replace("```", "").replace("**", "*")
        answers.append(answer)
    
    return answers
