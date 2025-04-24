#!/usr/bin/env python3
"""
Agentic RAG Team Application
Conduct research on a specific topic, evaluate, critically appraise, and compile a final report.
"""

import os
import sys
import asyncio
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, cast
from functools import lru_cache
from agents import Agent, Runner, function_tool  # type: ignore
from duckduckgo_search import DDGS  # type: ignore
from dotenv import load_dotenv, find_dotenv  # type: ignore
import openai  # type: ignore
import argparse
import time
import datetime
import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv(find_dotenv())

# Set OpenAI API key from .env file
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)
openai.api_key = api_key

# Initialize rich console
console = Console()

# Create a cache directory
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_path(tool_name: str, query: str) -> Path:
    """Generate a unique cache file path based on tool name and query"""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return CACHE_DIR / f"{tool_name}_{query_hash}.json"

def load_from_cache(tool_name: str, query: str) -> Optional[List[Dict]]:
    """Load cached results if available"""
    cache_path = get_cache_path(tool_name, query)
    if cache_path.exists():
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None

def save_to_cache(tool_name: str, query: str, results: List[Dict]) -> None:
    """Save results to cache"""
    cache_path = get_cache_path(tool_name, query)
    try:
        with open(cache_path, "w") as f:
            json.dump(results, f)
    except IOError:
        pass  # Fail silently if cache can't be written

def safe_str(value: Any) -> str:
    """Safely convert any value to string, handling None values"""
    if value is None:
        return ""
    return str(value)

# --- Tool Definitions ---
@function_tool
def web_search(query: str, max_results: int) -> list:
    """
    Search the web for the given query using DuckDuckGo and return a list of results.
    Each result is a dict with 'title', 'url', and 'snippet'.

    Args:
        query: Search term or phrase
        max_results: Maximum number of results to return
    """
    # Check cache first
    cached_results = load_from_cache("web_search", query)
    if cached_results:
        return cached_results

    # If not in cache, perform search
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results)) or []

        formatted_results = []
        for r in raw_results:
            formatted_results.append({
                "title": safe_str(r.get("title")),
                "url": safe_str(r.get("href")),
                "snippet": safe_str(r.get("body")),
                "source": "DuckDuckGo"
            })

        # Save to cache
        save_to_cache("web_search", query, formatted_results)
        return formatted_results
    except Exception as e:
        return [{"title": "Search Error", "url": "", "snippet": f"Error performing web search: {str(e)}", "source": "Error"}]

@function_tool
def openalex_search(query: str, exact_phrase: bool, filter_field: Optional[str], max_results: int) -> list:
    """
    Search academic literature using the OpenAlex API.

    Args:
        query: Search term or query
        exact_phrase: Whether to search for the exact phrase (wrap in quotes)
        filter_field: Specific field to search (title, abstract, etc.)
        max_results: Maximum number of results to return
    """
    # Check cache first
    cache_key = f"{query}_{exact_phrase}_{filter_field}"
    cached_results = load_from_cache("openalex", cache_key)
    if cached_results:
        return cached_results

    # Format the query based on parameters
    if exact_phrase:
        formatted_query = f'"{query}"'
    else:
        formatted_query = query

    # Base URL for OpenAlex API
    base_url = "https://api.openalex.org/works"

    # Construct the appropriate URL based on filter field
    if filter_field is not None:
        url = f"{base_url}?filter={filter_field}.search:{formatted_query}"
    else:
        url = f"{base_url}?search={formatted_query}"

    # Add per_page parameter to limit results
    url += f"&per_page={max_results}"

    # Add email for polite usage if available
    email = os.getenv("OPENALEX_EMAIL", "")
    if email and email.strip():
        url += f"&mailto={email}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Process results
        results = []
        for work in data.get("results", []):
            # Extract author names
            authors = []
            for authorship in work.get("authorships", []):
                if authorship.get("author") and authorship["author"].get("display_name"):
                    authors.append(safe_str(authorship["author"]["display_name"]))

            authors_str = ", ".join(authors[:3])
            if len(authors) > 3:
                authors_str += f" and {len(authors) - 3} more"

            # Get DOI or landing page URL
            url = ""
            if work.get("doi"):
                url = f"https://doi.org/{work['doi']}"
            elif work.get("primary_location") and work["primary_location"].get("landing_page_url"):
                url = safe_str(work["primary_location"]["landing_page_url"])

            # Get title
            title = safe_str(work.get("title"))

            # Process abstract
            snippet = "No abstract available"
            abstract_data = work.get("abstract_inverted_index")
            if isinstance(abstract_data, dict):
                try:
                    # OpenAlex stores abstracts as inverted indices, need to reconstruct
                    abstract_words = []
                    for word, positions in abstract_data.items():
                        for position in positions:
                            while len(abstract_words) <= position:
                                abstract_words.append("")
                            abstract_words[position] = word
                    snippet = " ".join(abstract_words)
                except:
                    snippet = "Abstract available but could not be processed"

            # Format publication date
            pub_date = safe_str(work.get("publication_date"))

            # Create result
            result = {
                "title": title,
                "url": url,
                "snippet": snippet,
                "publication_date": pub_date,
                "authors": authors_str,
                "source": "OpenAlex"
            }

            results.append(result)

        # Save to cache
        save_to_cache("openalex", cache_key, results)
        return results

    except Exception as e:
        return [{"title": "Search Error", "url": "", "snippet": f"Error performing OpenAlex search: {str(e)}", "source": "Error"}]

@function_tool
def crossref_search(query: str, filter_type: Optional[str], rows: int) -> list:
    """
    Search for academic publications using the CrossRef API.

    Args:
        query: Search term or phrase
        filter_type: Filter by type (journal-article, book, conference-paper, etc.)
        rows: Maximum number of results to return
    """
    # Check cache first
    cache_key = f"{query}_{filter_type}_{rows}"
    cached_results = load_from_cache("crossref", cache_key)
    if cached_results:
        return cached_results

    # Base URL for CrossRef API
    base_url = "https://api.crossref.org/works"

    # Build parameters
    params = {
        "query": query,
        "rows": rows,
        "sort": "relevance",
        "order": "desc",
    }

    # Add filter if specified
    if filter_type:
        params["filter"] = f"type:{filter_type}"

    # Make the request
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("message", {}).get("items", []):
            # Extract authors
            authors = []
            for author in item.get("author", []):
                name_parts = []
                if "given" in author:
                    name_parts.append(safe_str(author["given"]))
                if "family" in author:
                    name_parts.append(safe_str(author["family"]))
                if name_parts:
                    authors.append(" ".join(name_parts))

            authors_str = ", ".join(authors[:3])
            if len(authors) > 3:
                authors_str += f" and {len(authors) - 3} more"

            # Extract publication details
            pub_date = ""
            date_parts = []
            if "published-print" in item and item["published-print"].get("date-parts"):
                date_parts = item["published-print"]["date-parts"][0]
            elif "published-online" in item and item["published-online"].get("date-parts"):
                date_parts = item["published-online"]["date-parts"][0]

            if date_parts:
                pub_date = "-".join([safe_str(part) for part in date_parts])

            # Extract journal/publisher
            container = ""
            if item.get("container-title") and item["container-title"]:
                container = safe_str(item["container-title"][0])

            publisher = safe_str(item.get("publisher"))

            # Get title
            title = ""
            if item.get("title") and item["title"]:
                title = safe_str(item["title"][0])

            # Get DOI URL
            url = ""
            if "DOI" in item:
                url = f"https://doi.org/{item['DOI']}"

            # Format snippet from abstract or title
            snippet = safe_str(item.get("abstract"))
            if not snippet:
                if container:
                    snippet = f"Published in {container}"
                elif publisher:
                    snippet = f"Published by {publisher}"
                else:
                    snippet = ""

            result = {
                "title": title,
                "url": url,
                "snippet": snippet,
                "authors": authors_str,
                "publication_date": pub_date,
                "journal": container,
                "publisher": publisher,
                "source": "CrossRef"
            }

            results.append(result)

        # Save to cache
        save_to_cache("crossref", cache_key, results)
        return results

    except Exception as e:
        return [{"title": "Search Error", "url": "", "snippet": f"Error performing CrossRef search: {str(e)}", "source": "Error"}]

# --- Agent Definitions ---
research_agent = Agent(
    name="Research Agent",
    instructions="""
You are an expert research agent that efficiently gathers information on a topic.

PROCESS:
1. Break down the topic into 1-3 key aspects to investigate
2. For each aspect, use the appropriate search tool:
   - web_search: General web results via DuckDuckGo
   - openalex_search: Academic articles and research papers
   - crossref_search: Academic publications with DOIs and citation data

3. Choose the most appropriate search tool based on what you're looking for:
   - For general knowledge: web_search
   - For academic/scientific content: openalex_search or crossref_search
   - For recent statistics or news: web_search
   - For peer-reviewed publications: crossref_search

4. Analyze findings to identify key points, contradictions, and consensus
5. Avoid redundant searches and prioritize diverse, high-quality sources

OUTPUT: A markdown summary with:
1. Clear section headings
2. 5-8 key insights with evidence and sources
3. Brief source credibility assessment
4. Important statistics/data points
5. Proper attribution (titles and URLs)
6. 2-3 primary takeaways

Ensure efficient token usage by being concise but thorough.
""",
    tools=[web_search, openalex_search, crossref_search],
)

evaluation_agent = Agent(
    name="Evaluation Agent",
    instructions="""
You are an expert evaluation agent. Assess research findings using the CRAAP test:
- Currency: Timeliness of information
- Relevance: Importance to the topic
- Authority: Source credentials
- Accuracy: Reliability and correctness
- Purpose: Intent and potential bias

Evaluate research quality on:
- Thoroughness
- Balance of perspectives
- Evidence quality
- Information gaps

OUTPUT: A concise markdown evaluation with:
1. Mini-CRAAP assessment for major sources
2. Strongest evidence and key weaknesses
3. Information gaps
4. Overall quality rating (1-10)
5. 2-3 improvement suggestions

Be thorough but token-efficient.
""",
)

appraisal_agent = Agent(
    name="Appraisal Agent",
    instructions="""
You are an expert appraisal agent analyzing research quality and limitations.

Analyze:
1. Meta-level strengths/weaknesses of the research
2. Potential cognitive biases (confirmation bias, etc.)
3. Methodological soundness (sampling, measurement, etc.)
4. Knowledge gaps and contradictions

OUTPUT: A concise markdown appraisal with:
1. Framework for understanding topic complexity
2. Cognitive biases impact
3. Methodological strengths/weaknesses
4. Knowledge gaps
5. Overall epistemic strength assessment
6. Future research directions

Be precise, scholarly, and token-efficient.
""",
)

report_agent = Agent(
    name="Report Agent",
    instructions="""
You are an expert report generation agent creating professional research reports.

Synthesize findings from research, evaluation, and appraisal into a report with:

# [Topic] Research Report

## Executive Summary
- 3-5 bullet points on key findings
- Primary implications

## 1. Introduction
- Topic context and research scope

## 2. Key Findings
- Thematic organization of major insights
- Evidence from credible sources
- Contrasting perspectives on controversial points

## 3. Critical Analysis
- Source quality assessment
- Methodological limitations
- Knowledge gaps
- Potential biases

## 4. Implications
- Practical significance
- Questions for further investigation

## 5. Conclusion
- Synthesis of key insights

## References
- Properly formatted citations

Be comprehensive yet concise, scholarly yet accessible.
""",
)

# --- Pipeline Execution ---
async def run_pipeline(topic: str, output_file: str | None = None, verbose: bool = False, output_dir: str = "output", steps_dir: str = "steps_taken"):
    # Create directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(steps_dir, exist_ok=True)

    # Generate filenames with timestamp and sanitized topic
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_topic = "".join(c if c.isalnum() else "_" for c in topic)[:50]  # Limit length and sanitize

    # Output files
    if not output_file:
        output_file = os.path.join(output_dir, f"{sanitized_topic}_{timestamp}.md")
    steps_file = os.path.join(steps_dir, f"{sanitized_topic}_steps_{timestamp}.md")

    # Initialize steps log content
    steps_log = [
        f"# Research Process: {topic}",
        f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "\n## Process Overview",
        "This document details the step-by-step process used by our AI research pipeline:",
        "1. **Research Phase**: Web searches and information gathering",
        "2. **Evaluation Phase**: Critical assessment of source quality and findings",
        "3. **Appraisal Phase**: Meta-analysis of research methodology and limitations",
        "4. **Report Phase**: Synthesis of findings into comprehensive final report",
        "\n## Detailed Process Log\n"
    ]

    try:
        # STEP 1: Research
        console.print(Panel(f"[bold blue]STEP 1/4: Researching Topic: {topic}[/]", expand=False), style="blue")
        step_start = time.time()

        # Add to steps log
        steps_log.append("### STEP 1: Research Phase")
        steps_log.append(f"- **Topic**: {topic}")
        steps_log.append("- **Process**: Using search tools to gather relevant information")
        steps_log.append("- **Agent Instructions**: Break down topic, conduct searches with appropriate tools")
        steps_log.append(f"- **Started**: {datetime.datetime.now().strftime('%H:%M:%S')}\n")

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
        console.print(f"[dim][Research step duration: {time.time() - step_start:.2f}s][/]\n")

        # Update steps log with completion info
        steps_log.append(f"- **Completed**: {datetime.datetime.now().strftime('%H:%M:%S')}")
        steps_log.append(f"- **Duration**: {time.time() - step_start:.2f} seconds")
        steps_log.append("- **Output**: Research summary with key findings and sources\n")

        # STEP 2: Evaluation
        console.print(Panel("[bold green]STEP 2/4: Evaluation[/]", expand=False), style="green")
        step_start = time.time()

        # Add to steps log
        steps_log.append("### STEP 2: Evaluation Phase")
        steps_log.append("- **Process**: Critically assessing the quality and credibility of research findings")
        steps_log.append("- **Agent Instructions**: Apply CRAAP test to sources, evaluate research quality")
        steps_log.append(f"- **Started**: {datetime.datetime.now().strftime('%H:%M:%S')}\n")

        # Step 2: Evaluation
        evaluation_result = await Runner.run(evaluation_agent, research_output)
        evaluation_output = evaluation_result.final_output

        # Print evaluation output
        console.print("[bold magenta]## Evaluation[/]")
        console.print(Markdown(evaluation_output))

        if verbose:
            console.print("[dim][Full evaluation result][/]")
            console.print(evaluation_result)
        console.print(f"[dim][Evaluation step duration: {time.time() - step_start:.2f}s][/]\n")

        # Update steps log
        steps_log.append(f"- **Completed**: {datetime.datetime.now().strftime('%H:%M:%S')}")
        steps_log.append(f"- **Duration**: {time.time() - step_start:.2f} seconds")
        steps_log.append("- **Output**: Critical evaluation of sources and research quality\n")

        # STEP 3: Critical Appraisal
        console.print(Panel("[bold yellow]STEP 3/4: Critical Appraisal[/]", expand=False), style="yellow")
        step_start = time.time()

        # Add to steps log
        steps_log.append("### STEP 3: Critical Appraisal Phase")
        steps_log.append("- **Process**: Meta-analysis of research methodology and limitations")
        steps_log.append("- **Agent Instructions**: Identify biases, analyze methodological soundness, detect knowledge gaps")
        steps_log.append(f"- **Started**: {datetime.datetime.now().strftime('%H:%M:%S')}\n")

        # Step 3: Critical Appraisal
        appraisal_result = await Runner.run(appraisal_agent, evaluation_output)
        appraisal_output = appraisal_result.final_output

        # Print appraisal output
        console.print("[bold yellow]## Critical Appraisal[/]")
        console.print(Markdown(appraisal_output))

        if verbose:
            console.print("[dim][Full appraisal result][/]")
            console.print(appraisal_result)
        console.print(f"[dim][Appraisal step duration: {time.time() - step_start:.2f}s][/]\n")

        # Update steps log
        steps_log.append(f"- **Completed**: {datetime.datetime.now().strftime('%H:%M:%S')}")
        steps_log.append(f"- **Duration**: {time.time() - step_start:.2f} seconds")
        steps_log.append("- **Output**: Analysis of methodological strengths/weaknesses and knowledge gaps\n")

        # STEP 4: Final Report
        console.print(Panel("[bold red]STEP 4/4: Generating Final Report[/]", expand=False), style="red")
        step_start = time.time()

        # Add to steps log
        steps_log.append("### STEP 4: Report Generation Phase")
        steps_log.append("- **Process**: Synthesizing all findings into comprehensive final report")
        steps_log.append("- **Agent Instructions**: Create well-structured report with executive summary and key sections")
        steps_log.append(f"- **Started**: {datetime.datetime.now().strftime('%H:%M:%S')}\n")

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
        console.print(f"[dim][Final report step duration: {time.time() - step_start:.2f}s][/]\n")

        # Update steps log
        steps_log.append(f"- **Completed**: {datetime.datetime.now().strftime('%H:%M:%S')}")
        steps_log.append(f"- **Duration**: {time.time() - step_start:.2f} seconds")
        steps_log.append("- **Output**: Final comprehensive research report\n")

        # Save final report to output file
        with open(output_file, "w") as f:
            f.write(report_output)
        console.print(f"[bold green]Report saved to: {output_file}[/]")

        # Save steps log
        with open(steps_file, "w") as f:
            f.write("\n".join(steps_log))
        console.print(f"[bold green]Process log saved to: {steps_file}[/]")

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

def main():
    parser = argparse.ArgumentParser(description="Agentic RAG Team Application")
    parser.add_argument("-d", "--output-dir", dest="output_dir", default="output", help="Directory to save output files (default: output)")
    parser.add_argument("-s", "--steps-dir", dest="steps_dir", default="steps_taken", help="Directory to save process logs (default: steps_taken)")
    parser.add_argument("topic", nargs='+', help="Topic to research")
    parser.add_argument("-o", "--output", dest="output_file", help="Path to save final report (Markdown)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode: show full intermediate results and timings")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the search cache before running")
    args = parser.parse_args()

    # Clear cache if requested
    if args.clear_cache and CACHE_DIR.exists():
        for cache_file in CACHE_DIR.glob("*.json"):
            try:
                cache_file.unlink()
            except:
                pass
        print("Cache cleared")

    topic = " ".join(args.topic)
    asyncio.run(run_pipeline(topic, args.output_file, args.verbose, args.output_dir, args.steps_dir))

if __name__ == "__main__":
    main()