"""
Research pipeline runner that coordinates the execution of the agent workflow
"""

import os
import time
import asyncio
from typing import Dict, Optional
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from agents import Runner  # type: ignore

from src.agents import (
    research_agent,
    evaluation_agent,
    appraisal_agent,
    report_agent
)
from src.utils.formatting import (
    sanitize_filename,
    get_timestamp,
    get_formatted_time,
    get_formatted_duration
)

# Initialize rich console
console = Console()

async def run_pipeline(
    topic: str,
    output_file: Optional[str] = None,
    verbose: bool = False,
    output_dir: str = "output",
    steps_dir: str = "steps_taken"
) -> Dict[str, str]:
    """
    Run the full research pipeline on the given topic

    Args:
        topic: The research topic
        output_file: Optional path to save the output file (default: auto-generated)
        verbose: Whether to show verbose output
        output_dir: Directory to save output files
        steps_dir: Directory to save process logs

    Returns:
        Dict containing paths to output files
    """
    # Create directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(steps_dir, exist_ok=True)

    # Generate filenames with timestamp and sanitized topic
    timestamp = get_timestamp()
    sanitized_topic = sanitize_filename(topic)  # Limit length and sanitize

    # Output files
    if not output_file:
        output_file = os.path.join(output_dir, f"{sanitized_topic}_{timestamp}.md")
    steps_file = os.path.join(steps_dir, f"{sanitized_topic}_steps_{timestamp}.md")

    # Initialize steps log content
    steps_log = [
        f"# Research Process: {topic}",
        f"*Generated on: {get_formatted_time()}*",
        "\n## Process Overview",
        "This document details the step-by-step process used by our AI research pipeline:",
        "1. **Research Phase**: Web searches and information gathering",
        "2. **Evaluation Phase**: Critical assessment of source quality and findings",
        "3. **Appraisal Phase**: Meta-analysis of research methodology and limitations",
        "4. **Report Phase**: Synthesis of findings into comprehensive final report",
        "\n## Detailed Process Log\n"
    ]

    # Print the initial process overview to terminal
    console.print("[bold cyan]# Research Process Started[/]")
    console.print(f"[bold]Topic:[/] {topic}")
    console.print(f"[bold]Started at:[/] {get_formatted_time()}\n")
    console.print("[bold]Process Overview:[/]")
    console.print("1. [bold]Research Phase:[/] Web searches and information gathering")
    console.print("2. [bold]Evaluation Phase:[/] Critical assessment of source quality and findings")
    console.print("3. [bold]Appraisal Phase:[/] Meta-analysis of research methodology and limitations")
    console.print("4. [bold]Report Phase:[/] Synthesis of findings into comprehensive final report\n")

    try:
        # STEP 1: Research
        console.print(Panel(f"[bold blue]STEP 1/4: Researching Topic: {topic}[/]", expand=False), style="blue")
        step_start = time.time()

        # Add to steps log
        steps_log.append("### STEP 1: Research Phase")
        steps_log.append(f"- **Topic**: {topic}")
        steps_log.append("- **Process**: Using search tools to gather relevant information")
        steps_log.append("- **Agent Instructions**: Break down topic, conduct searches with appropriate tools")
        steps_log.append(f"- **Started**: {get_formatted_time()}\n")

        # Print the step details to terminal
        console.print("[bold blue]Research Phase[/]")
        console.print("[dim]- Process: Using search tools to gather relevant information")
        console.print("- Agent Instructions: Break down topic, conduct searches with appropriate tools")
        console.print(f"- Started: {get_formatted_time()}[/]\n")

        research_result = await Runner.run(research_agent, topic)
        research_output = research_result.final_output

        # Add search details to steps log
        steps_log.append("#### Research Details:")
        steps_log.append("- Multiple search tools used to gather information from various sources")
        steps_log.append("- Search queries and sources processed by the research agent")

        # Print research output
        console.print("[bold cyan]## Research Summary[/]")
        console.print(Markdown(research_output))

        if verbose:
            console.print("[dim][Full research result][/]")
            console.print(research_result)

        duration = time.time() - step_start
        console.print(f"[dim][Research step duration: {duration:.2f}s][/]\n")

        # Update steps log with completion info
        steps_log.append(f"- **Completed**: {get_formatted_time()}")
        steps_log.append(f"- **Duration**: {duration:.2f} seconds")
        steps_log.append("- **Output**: Research summary with key findings and sources\n")

        # Print completion info to terminal
        console.print(f"[dim]Research Phase completed at: {get_formatted_time()}")
        console.print(f"Duration: {duration:.2f} seconds[/]\n")

        # STEP 2: Evaluation
        console.print(Panel("[bold green]STEP 2/4: Evaluation[/]", expand=False), style="green")
        step_start = time.time()

        # Add to steps log
        steps_log.append("### STEP 2: Evaluation Phase")
        steps_log.append("- **Process**: Critically assessing the quality and credibility of research findings")
        steps_log.append("- **Agent Instructions**: Apply CRAAP test to sources, evaluate research quality")
        steps_log.append(f"- **Started**: {get_formatted_time()}\n")

        # Print the step details to terminal
        console.print("[bold green]Evaluation Phase[/]")
        console.print("[dim]- Process: Critically assessing the quality and credibility of research findings")
        console.print("- Agent Instructions: Apply CRAAP test to sources, evaluate research quality")
        console.print(f"- Started: {get_formatted_time()}[/]\n")

        # Step 2: Evaluation
        evaluation_result = await Runner.run(evaluation_agent, research_output)
        evaluation_output = evaluation_result.final_output

        # Print evaluation output
        console.print("[bold magenta]## Evaluation[/]")
        console.print(Markdown(evaluation_output))

        if verbose:
            console.print("[dim][Full evaluation result][/]")
            console.print(evaluation_result)

        duration = time.time() - step_start
        console.print(f"[dim][Evaluation step duration: {duration:.2f}s][/]\n")

        # Update steps log
        steps_log.append(f"- **Completed**: {get_formatted_time()}")
        steps_log.append(f"- **Duration**: {duration:.2f} seconds")
        steps_log.append("- **Output**: Critical evaluation of sources and research quality\n")

        # Print completion info to terminal
        console.print(f"[dim]Evaluation Phase completed at: {get_formatted_time()}")
        console.print(f"Duration: {duration:.2f} seconds[/]\n")

        # STEP 3: Critical Appraisal
        console.print(Panel("[bold yellow]STEP 3/4: Critical Appraisal[/]", expand=False), style="yellow")
        step_start = time.time()

        # Add to steps log
        steps_log.append("### STEP 3: Critical Appraisal Phase")
        steps_log.append("- **Process**: Meta-analysis of research methodology and limitations")
        steps_log.append("- **Agent Instructions**: Identify biases, analyze methodological soundness, detect knowledge gaps")
        steps_log.append(f"- **Started**: {get_formatted_time()}\n")

        # Print the step details to terminal
        console.print("[bold yellow]Critical Appraisal Phase[/]")
        console.print("[dim]- Process: Meta-analysis of research methodology and limitations")
        console.print("- Agent Instructions: Identify biases, analyze methodological soundness, detect knowledge gaps")
        console.print(f"- Started: {get_formatted_time()}[/]\n")

        # Step 3: Critical Appraisal
        appraisal_result = await Runner.run(appraisal_agent, evaluation_output)
        appraisal_output = appraisal_result.final_output

        # Print appraisal output
        console.print("[bold yellow]## Critical Appraisal[/]")
        console.print(Markdown(appraisal_output))

        if verbose:
            console.print("[dim][Full appraisal result][/]")
            console.print(appraisal_result)

        duration = time.time() - step_start
        console.print(f"[dim][Appraisal step duration: {duration:.2f}s][/]\n")

        # Update steps log
        steps_log.append(f"- **Completed**: {get_formatted_time()}")
        steps_log.append(f"- **Duration**: {duration:.2f} seconds")
        steps_log.append("- **Output**: Analysis of methodological strengths/weaknesses and knowledge gaps\n")

        # Print completion info to terminal
        console.print(f"[dim]Critical Appraisal Phase completed at: {get_formatted_time()}")
        console.print(f"Duration: {duration:.2f} seconds[/]\n")

        # STEP 4: Final Report
        console.print(Panel("[bold red]STEP 4/4: Generating Final Report[/]", expand=False), style="red")
        step_start = time.time()

        # Add to steps log
        steps_log.append("### STEP 4: Report Generation Phase")
        steps_log.append("- **Process**: Synthesizing all findings into comprehensive final report")
        steps_log.append("- **Agent Instructions**: Create well-structured report with executive summary and key sections")
        steps_log.append(f"- **Started**: {get_formatted_time()}\n")

        # Print the step details to terminal
        console.print("[bold red]Report Generation Phase[/]")
        console.print("[dim]- Process: Synthesizing all findings into comprehensive final report")
        console.print("- Agent Instructions: Create well-structured report with executive summary and key sections")
        console.print(f"- Started: {get_formatted_time()}[/]\n")

        # Create a more token-efficient input by summarizing key points
        combined_input = (
            f"Research Summary:\n{research_output}\n\n"
            f"Evaluation:\n{evaluation_output}\n\n"
            f"Appraisal:\n{appraisal_output}\n\n"
            f"Create a comprehensive research report on: {topic}"
        )
        report_result = await Runner.run(report_agent, combined_input)
        report_output = report_result.final_output

        # Print report output
        console.print("[bold white on red]## Final Report[/]")
        console.print(Markdown(report_output))

        if verbose:
            console.print("[dim][Full report result][/]")
            console.print(report_result)

        duration = time.time() - step_start
        console.print(f"[dim][Final report step duration: {duration:.2f}s][/]\n")

        # Update steps log
        steps_log.append(f"- **Completed**: {get_formatted_time()}")
        steps_log.append(f"- **Duration**: {duration:.2f} seconds")
        steps_log.append("- **Output**: Final comprehensive research report\n")

        # Print completion info to terminal
        console.print(f"[dim]Report Generation Phase completed at: {get_formatted_time()}")
        console.print(f"Duration: {duration:.2f} seconds[/]\n")

        # Save final report to output file
        with open(output_file, "w") as f:
            f.write(report_output)
        console.print(f"[bold green]Report saved to: {output_file}[/]")

        # Save steps log
        with open(steps_file, "w") as f:
            f.write("\n".join(steps_log))
        console.print(f"[bold green]Process log saved to: {steps_file}[/]")

        # Print final summary
        console.print("\n[bold cyan]# Research Process Completed[/]")
        console.print(f"[bold]Topic:[/] {topic}")
        console.print(f"[bold]Completed at:[/] {get_formatted_time()}")
        console.print(f"[bold]Output files:[/]")
        console.print(f"- Report: {output_file}")
        console.print(f"- Process log: {steps_file}")

        # Return paths for use by caller
        return {
            "report_file": output_file,
            "steps_file": steps_file
        }

    except Exception as e:
        console.print(f"[bold red]Error during pipeline execution: {str(e)}[/]")
        # Save what we have so far in case of error
        try:
            with open(steps_file, "w") as f:
                steps_log.append(f"\n### ERROR: {str(e)}")
                f.write("\n".join(steps_log))
            console.print(f"[bold yellow]Partial process log saved to: {steps_file}[/]")
        except:
            pass
        raise