# Agentic RAG Research Team

A powerful research tool built with the OpenAI Agents SDK that leverages multiple search APIs to conduct comprehensive research, evaluation, critical appraisal, and report generation.

## Features

- **Multi-source research**: Integrates DuckDuckGo, OpenAlex and CrossRef APIs for comprehensive search
- **Efficient token usage**: Optimized prompts and caching to minimize OpenAI API costs
- **Hierarchical agent team**:
  - Research Agent: Gathers information from multiple sources
  - Evaluation Agent: Assesses source credibility and quality
  - Appraisal Agent: Analyzes methodological strengths and limitations
  - Report Agent: Compiles findings into a comprehensive report
- **Report generation**: Creates professionally formatted, academic-quality research reports
- **Local caching**: Stores search results to avoid redundant API calls

## Architecture

The application follows a sequential pipeline architecture with four specialized agents:

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
        │                     │                     │                     │
        │                     │                     │                     │
        └─────────────────────┴─────────────────────┴─────────────────────┘
                                       │
                                       ▼
                              ┌───────────────────┐
                              │                   │
                              │  Output Files     │
                              │  (Markdown)       │
                              │                   │
                              └───────────────────┘
```

1. **Research Agent**: Uses multiple search tools (DuckDuckGo, OpenAlex, CrossRef) to gather information
2. **Evaluation Agent**: Assesses source quality using the CRAAP test framework
3. **Appraisal Agent**: Analyzes research methodology and identifies biases
4. **Report Agent**: Synthesizes all findings into a professional report

## Enhanced Research with CrossRef Integration

The tool integrates the CrossRef API to significantly improve scholarly research capabilities:

- **Extensive Academic Database**: Access to over 100 million scholarly articles, books, conference proceedings, and more
- **Publication Metadata**: Retrieves rich metadata including authors, DOIs, publication dates, and publisher information
- **Citation Data**: Helps evaluate the academic impact and relevance of sources
- **Filtering Capabilities**: Filter results by publication type (journal article, book chapter, etc.)
- **DOI Resolution**: Direct links to original publications via Digital Object Identifiers

Combined with OpenAlex and DuckDuckGo search, this creates a powerful research pipeline that can access both scholarly and general web sources, providing a comprehensive view of any research topic.

## Token Efficiency Features

This tool implements several strategies to minimize OpenAI API token usage:

1. **Local caching**: Search results are cached to avoid redundant API calls
2. **Optimized prompts**: All agent instructions are concise and focused
3. **Strategic data passing**: Only relevant information is passed between agents
4. **Efficient formatting**: Compact markdown structures reduce token overhead
5. **Source limitation**: Searches are capped at 5 results by default to save tokens

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Rename the env.example.txt file to `.env`, and add in your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENALEX_EMAIL=your_email@example.com  # Optional but recommended for OpenAlex
   ```

## Usage

```bash
# Basic usage
python research_agent_team.py "Your research topic"

# With custom output file
python research_agent_team.py "Your research topic" -o my_report.md

# With verbose output to see full agent interactions
python research_agent_team.py "Your research topic" -v

# Clear the cache before running
python research_agent_team.py "Your research topic" --clear-cache

# Specify custom output and steps directories
python research_agent_team.py "Your research topic" -d ./my_outputs -s ./my_logs
```

## How It Works

1. **Research Phase**: The Research Agent breaks down your topic into key aspects and uses multiple search tools to find relevant information from the web and academic sources.

2. **Evaluation Phase**: The Evaluation Agent applies the CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose) to assess source quality and research thoroughness.

3. **Appraisal Phase**: The Appraisal Agent performs a meta-analysis of research quality, identifying cognitive biases, methodological strengths and weaknesses.

4. **Report Phase**: The Report Agent synthesizes findings into a comprehensive, well-structured report with citations.

## Outputs

The tool produces two main outputs for each research session:

1. **Research Report**: A comprehensive markdown document with executive summary, key findings, critical analysis, implications, and references.

2. **Process Log**: A detailed log of the research process including timestamps, agent actions, and processing details.

## Example Use Cases

### Academic Research
```bash
python research_agent_team.py "Recent advances in quantum computing algorithms"
```
Produces a scholarly report with academic sources and critical analysis of methodologies.

### Market Research
```bash
python research_agent_team.py "Electric vehicle market trends 2023"
```
Generates a comprehensive overview of market developments, statistics, and future projections.

### Policy Analysis
```bash
python research_agent_team.py "International climate policy effectiveness"
```
Creates a balanced assessment of global climate policies with analysis of different approaches.

### Literature Review
```bash
python research_agent_team.py "Machine learning applications in healthcare"
```
Compiles academic and industry sources to provide a thorough literature review on the topic.

## License

MIT

## Acknowledgements

This application utilizes:
- OpenAI's GPT models and Agents SDK
- DuckDuckGo's search API
- OpenAlex academic research API
- CrossRef's academic publications API
- Python's asyncio for efficient agent execution

## Project Structure

```
RAG/
├── main.py                   # Main entry point
├── requirements.txt          # Dependencies
├── .env                      # Environment variables
├── README.md                 # Documentation
├── USAGE_GUIDE.md            # Usage guide
├── cache/                    # Cache directory (auto-created)
├── output/                   # Output directory (auto-created)
├── steps_taken/              # Process logs directory (auto-created)
└── src/                      # Source code
    ├── agents/               # Agent definitions
    │   ├── __init__.py       # Exports all agents
    │   ├── research_agent.py # Research agent
    │   ├── evaluation_agent.py # Evaluation agent
    │   ├── appraisal_agent.py  # Appraisal agent
    │   └── report_agent.py     # Report agent
    ├── tools/                # Search tools
    │   ├── __init__.py       # Exports all tools
    │   ├── web_search.py     # DuckDuckGo search
    │   ├── openalex_search.py # OpenAlex search
    │   └── crossref_search.py # CrossRef search
    ├── utils/                # Utility functions
    │   ├── __init__.py       # Exports utilities
    │   ├── cache.py          # Cache utilities
    │   └── formatting.py     # Text formatting utils
    └── pipeline/             # Research pipeline
        ├── __init__.py       # Exports pipeline
        └── runner.py         # Pipeline execution
```

The modular organization provides several benefits:
- Clear separation of concerns
- Improved maintainability and extensibility
- Easier testing and debugging
- Better code reuse