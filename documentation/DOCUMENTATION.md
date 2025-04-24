# Research Agent Team: Technical Documentation

## System Architecture

The Research Agent Team is an LLM-powered research pipeline that combines multiple specialized agents to conduct comprehensive research on a given topic. The system architecture follows a sequential pipeline pattern where each agent performs a specific role in the research process.

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │     │               │
│  Research     │────▶│  Evaluation   │────▶│  Appraisal    │────▶│  Report       │
│  Agent        │     │  Agent        │     │  Agent        │     │  Agent        │
│               │     │               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
       │                     │                     │                     │
       ▼                     ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Research     │     │  Evaluation   │     │  Critical     │     │  Final        │
│  Results      │     │  Results      │     │  Appraisal    │     │  Report       │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
```

### Core Components

1. **Agent System**: Four specialized LLM agents with different roles and instructions
2. **Pipeline Orchestration**: Sequential execution with data passing between stages
3. **Web Search Tool**: DuckDuckGo search integration for retrieving information
4. **Output Generation**: Markdown report generation and process logging
5. **CLI Interface**: User-friendly command-line interface for triggering research

## Code Structure

The application is organized as a single Python script with several logical sections:

```
research_agent_team.py
├── Imports and Environment Setup
├── Agent Definitions
│   ├── Research Agent
│   ├── Evaluation Agent
│   ├── Appraisal Agent
│   └── Report Agent
├── Tool Definitions
│   └── Web Search
├── Pipeline Execution
│   └── run_pipeline()
└── CLI Interface
    └── main()
```

## Agent Definitions

### Research Agent

**Purpose**: Gathers information on a specified topic using web search tools.

**Prompting Strategy**:
- Instructed to explore the topic thoroughly
- Uses web search to gather relevant information
- Organizes findings into a structured report with sections
- Includes source URLs for all information
- Formats output as Markdown

**Input**: Research topic
**Output**: Markdown-formatted research findings with sources

### Evaluation Agent

**Purpose**: Evaluates the research findings for quality, accuracy, and comprehensiveness.

**Prompting Strategy**:
- Reviews the research report for factual accuracy
- Identifies potential biases or gaps in coverage
- Assesses the credibility of sources
- Suggests improvements or additional research areas
- Formats evaluation as structured Markdown

**Input**: Research findings from Research Agent
**Output**: Critical evaluation of research quality

### Appraisal Agent

**Purpose**: Performs a deeper critical analysis of both the research and its evaluation.

**Prompting Strategy**:
- Examines both research findings and evaluation
- Identifies underlying assumptions and methodological issues
- Considers alternative perspectives not covered
- Evaluates overall research approach
- Formats appraisal as structured Markdown

**Input**: Research findings and evaluation results
**Output**: Comprehensive critical appraisal

### Report Agent

**Purpose**: Synthesizes all previous work into a final, polished research report.

**Prompting Strategy**:
- Incorporates original research, evaluation, and appraisal
- Organizes content into a cohesive narrative
- Highlights key insights and findings
- Ensures proper citation and sourcing
- Formats as a professional Markdown report

**Input**: Research findings, evaluation, and appraisal
**Output**: Final research report

## Tool Implementation

### Web Search Tool (DDG Search)

The application leverages the DuckDuckGo search API through the `duckduckgo_search` Python package to retrieve real-time information from the web.

```python
from duckduckgo_search import DDGS

def web_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        return results
    except Exception as e:
        return f"Error during web search: {str(e)}"
```

**Configuration**:
- Maximum of 5 results per search query
- Results include title, body text, and URL
- Error handling for failed searches

## Academic Search Tool (OpenAlex API)

The application also includes a specialized academic search capability using the OpenAlex API, which provides access to scholarly articles, publications, and research papers.

```python
def openalex_search(query: str, exact_phrase: bool = False, filter_field: str = None):
    import requests

    # Format the query based on parameters
    formatted_query = f'"{query}"' if exact_phrase else query

    # Construct the appropriate URL
    base_url = "https://api.openalex.org/works"
    url = f"{base_url}?filter={filter_field}.search:{formatted_query}" if filter_field else f"{base_url}?search={formatted_query}"
    url += "&per_page=5"

    # Add email for polite usage
    email = os.getenv("OPENALEX_EMAIL", "")
    if email and email.strip():
        url += f"&mailto={email}"

    # Make the request and process results
    response = requests.get(url)
    data = response.json()

    # Format results with title, URL, authors, publication date, and abstract
    return processed_results
```

**Features**:
- Academic-focused search results
- Support for exact phrase matching
- Field-specific searching (title, abstract, etc.)
- Author information and publication dates
- DOI links to academic papers
- Abstract text extraction from OpenAlex's inverted index format

## Pipeline Workflow

### Initialization

1. Parse command-line arguments
2. Create output directories if they don't exist
3. Generate unique filenames based on topic and timestamp

### Execution Flow

1. **Research Phase**:
   - Log start time
   - Execute Research Agent with topic
   - Save research findings
   - Log completion time

2. **Evaluation Phase**:
   - Log start time
   - Execute Evaluation Agent with research findings
   - Save evaluation results
   - Log completion time

3. **Appraisal Phase**:
   - Log start time
   - Execute Appraisal Agent with research and evaluation results
   - Save appraisal results
   - Log completion time

4. **Report Generation Phase**:
   - Log start time
   - Execute Report Agent with all previous results
   - Save final report
   - Log completion time

### Logging

- Each step is logged with start/end times and duration
- Process log is saved to a separate file
- Verbose mode provides additional console output

## CLI Interface

The application implements a command-line interface using Python's `argparse` module with the following parameters:

| Argument | Short | Long | Default | Description |
|----------|-------|------|---------|-------------|
| Topic | - | - | (required) | Research topic to investigate |
| Output Directory | `-d` | `--output-dir` | `output/` | Directory for final report |
| Steps Directory | `-s` | `--steps-dir` | `steps_taken/` | Directory for process logs |
| Output File | `-o` | `--output-file` | (auto-generated) | Custom filename for report |
| Verbose | `-v` | `--verbose` | `False` | Enable verbose output |

## Output Generation

### Final Report

The final report is generated as a Markdown file with the following structure:

```markdown
# [Topic] Research Report

## Executive Summary
...

## 1. Introduction
...

## 2. Key Findings
...

## 3. Critical Analysis
...

## 4. Implications
...

## 5. Conclusion
...

## References
...
```

### Process Log

The process log records the full workflow with timing information:

```markdown
# Research Process: [Topic]
*Generated on: YYYY-MM-DD HH:MM:SS*

## Process Overview
...

## Detailed Process Log

### STEP 1: Research Phase
...

### STEP 2: Evaluation Phase
...

### STEP 3: Appraisal Phase
...

### STEP 4: Report Generation Phase
...
```

## Error Handling

The application implements several error handling mechanisms:

1. **Agent Execution**: Errors during agent execution are captured and reported
2. **Web Search**: Failed searches return error messages rather than failing silently
3. **File Operations**: Directory creation errors are reported with clear messages
4. **API Failures**: OpenAI API errors are handled with appropriate error messages

## Customization Guide

### Modifying Agent Instructions

To modify an agent's behavior, locate its definition in the code and adjust the content parameter:

```python
research_agent = {
    "model": "gpt-4-turbo",
    "content": """
    You are a Research Agent. Your task is to...
    [MODIFY INSTRUCTIONS HERE]
    """
}
```

### Adding New Agents

To add a new agent to the pipeline:

1. Define the new agent with appropriate instructions
2. Modify the `run_pipeline()` function to include the new agent
3. Update the process logging to include the new step
4. Ensure data is properly passed between all agents

### Changing Search Provider

The application uses DuckDuckGo by default, but can be modified to use other search providers:

1. Install the appropriate package for the desired search API
2. Modify the `web_search()` function to use the new provider
3. Update error handling for the new search implementation

## API Reference

### Core Functions

#### `run_pipeline(topic, output_dir, steps_dir, output_file, verbose)`

Executes the full research pipeline on a given topic.

**Parameters:**
- `topic` (str): Research topic to investigate
- `output_dir` (str): Directory to save the final report
- `steps_dir` (str): Directory to save process logs
- `output_file` (str, optional): Custom filename for the final report
- `verbose` (bool): Whether to print verbose output

**Returns:**
- `output_path` (str): Path to the generated report
- `steps_path` (str): Path to the process log

#### `web_search(query)`

Performs a web search using DuckDuckGo.

**Parameters:**
- `query` (str): Search query string

**Returns:**
- `results` (list): List of search results with title, body, and URL

### Helper Functions

#### `generate_filenames(topic, output_dir, steps_dir, output_file)`

Generates filenames for the report and process log.

**Parameters:**
- `topic` (str): Research topic
- `output_dir` (str): Output directory for report
- `steps_dir` (str): Output directory for process log
- `output_file` (str, optional): Custom filename for report

**Returns:**
- `output_path` (str): Path for final report
- `steps_path` (str): Path for process log

## Dependencies

The application requires the following Python packages:

- `openai`: For accessing OpenAI's API
- `duckduckgo_search`: For web search functionality
- `python-dotenv`: For loading environment variables
- `argparse`: For command-line interface (standard library)
- `os`, `sys`, `time`, `datetime`, `asyncio`: Standard library modules

## Security Considerations

1. **API Key Management**: The application uses environment variables to store API keys
2. **Input Sanitization**: User inputs are sanitized before use in critical operations
3. **Error Exposure**: Error messages are controlled to avoid revealing sensitive information

## Performance Optimization

1. **Rate Limiting**: The web search tool is designed to respect rate limits
2. **Output Buffering**: Large outputs are properly buffered to conserve memory
3. **Timeout Handling**: API calls include timeout handling to prevent indefinite waiting

## Future Enhancements

Potential improvements to consider:

1. **Parallel Agent Execution**: Run some agents in parallel for faster results
2. **Additional Search Sources**: Integrate multiple search providers for broader coverage
3. **Interactive Mode**: Add an interactive mode for refining research questions
4. **Export Formats**: Support additional output formats (PDF, HTML, etc.)
5. **Caching Layer**: Add caching for search results to improve performance
6. **GUI Interface**: Develop a graphical interface for non-technical users