# Usage Guide: RAGs to Riches

This guide provides detailed instructions for using the RAGs to Riches tool to conduct comprehensive research on any topic.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (GPT-4 access required)
- Internet connection for API access

### Setup

1. Ensure you have created a `.env` file with your API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENALEX_EMAIL=your_email@example.com  # Optional but recommended
   ```

2. Activate your virtual environment:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

## Basic Usage

The tool is designed to be simple to use. At its most basic, you can run:

```bash
python main.py "Your research topic"
```

Replace "Your research topic" with any subject you want to research. The more specific your topic, the more focused the research will be.

## Command-line Options

```
usage: main.py [-h] [-d OUTPUT_DIR] [-s STEPS_DIR] [-o OUTPUT_FILE]
                              [-v] [--clear-cache] topic [topic ...]

RAGs to Riches Application

positional arguments:
  topic                 Topic to research

options:
  -h, --help            show this help message and exit
  -d OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to save output files (default: output)
  -s STEPS_DIR, --steps-dir STEPS_DIR
                        Directory to save process logs (default: steps_taken)
  -o OUTPUT, --output OUTPUT_FILE
                        Path to save final report (Markdown)
  -v, --verbose         Verbose mode: show full intermediate results and timings
  --clear-cache         Clear the search cache before running
```

## Advanced Usage Examples

### Research with Custom Output Location

Specify a custom filename for the output report:

```bash
python main.py "Quantum computing applications" -o reports/quantum_computing.md
```

### Verbose Output for Debugging

When you want to see the full agent responses and detailed processing:

```bash
python main.py "Climate change mitigation strategies" -v
```

### Managing the Cache

Clear the search cache before running a new research session:

```bash
python main.py "Renewable energy trends" --clear-cache
```

The cache helps reduce token usage and speeds up repeated searches, but you may want to clear it when:
- You need the most up-to-date information
- Previous search results may be influencing new research
- You're experiencing issues with stale data

#### How the Cache Works

The tool automatically creates a `cache` directory to store search results. Each search query generates a unique hash-based filename for its results. Benefits of the caching system:

- **Reduced API calls**: Avoids redundant searches for the same queries
- **Faster execution**: Subsequent runs with similar searches are much faster
- **Lower token usage**: Fewer API calls means fewer tokens consumed
- **Persistence**: Research data remains available between sessions

The cache is particularly useful when refining your research on similar topics or when running multiple research sessions on related subjects.

## Understanding the Output

The tool produces two main outputs for each research session:

### 1. Research Report

The main research report is saved as a Markdown file in the specified output directory (default: `output/`). The report follows this structure:

- **Executive Summary**: Concise overview of key findings
- **Introduction**: Context and scope of the research
- **Key Findings**: Main insights organized thematically
- **Critical Analysis**: Assessment of source quality and methodological limitations
- **Implications**: Practical significance and questions for further investigation
- **Conclusion**: Synthesis of key insights
- **References**: Properly formatted source citations

### 2. Process Log

The process log is saved in the specified steps directory (default: `steps_taken/`). This log provides transparency into the research process:

- **Research Phase**: Details on searches performed and information gathered
- **Evaluation Phase**: Source quality assessment results
- **Appraisal Phase**: Analysis of methodological strengths and weaknesses
- **Report Phase**: Final synthesis process

Each phase includes timestamps, durations, and key outputs.

## Search Tool Capabilities

The system integrates three primary search tools that work together to provide comprehensive research:

### 1. DuckDuckGo Web Search
- **Best for**: General knowledge, recent events, news articles, websites
- **Syntax**: `web_search(query="search term", max_results=5)`
- **Strengths**: Up-to-date information, broad coverage, diverse sources
- **Example topics**: "current events", "news topics", "general information"

### 2. OpenAlex Academic Search
- **Best for**: Scientific articles, research papers, academic publications
- **Syntax**: `openalex_search(query="search term", exact_phrase=False, filter_field=None, max_results=5)`
- **Features**:
  - `exact_phrase=True` for searching exact phrases
  - `filter_field="title"` to search only in titles (can also use "abstract" or other fields)
- **Strengths**: Academic focus, abstract access, author information
- **Example topics**: "scientific research", "academic papers", "scholarly work"

### 3. CrossRef Academic Search
- **Best for**: Publications with DOIs, citation data, journal articles
- **Syntax**: `crossref_search(query="search term", filter_type=None, rows=5)`
- **Features**:
  - `filter_type="journal-article"` to focus on specific publication types (can also use "book-chapter", "conference-paper", etc.)
- **Strengths**: Extensive publication metadata, DOI resolution, publisher information
- **Example topics**: "peer-reviewed research", "journal publications"

The Research Agent automatically selects the most appropriate search tool based on the nature of your query and the type of information needed.

## Tips for Effective Research

1. **Be specific**: "The impact of climate change on coral reefs" will yield better results than "climate change"

2. **Consider scope**: Very broad topics may result in more general findings; narrower topics allow deeper analysis

3. **Allow sufficient time**: The research process typically takes 3-5 minutes depending on topic complexity

4. **Review the process log**: Check what sources were examined to identify potential gaps

5. **Use verbose mode sparingly**: It provides valuable insight but increases console output substantially

6. **Leverage the cache**: For related research topics, the cache speeds up processing and reduces API calls

7. **Combine with traditional research**: Use the tool's output as a starting point for deeper research

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure your `.env` file is in the project root directory
   - Verify your API key is correct and has GPT-4 access

2. **Search Tool Errors**:
   - Check your internet connection
   - Verify you're not experiencing rate limiting from DuckDuckGo, OpenAlex, or CrossRef
   - Try running with `--clear-cache` if you suspect cached data issues

3. **Performance Issues**:
   - For large reports, ensure you have sufficient RAM available
   - Complex topics may take longer to process

4. **Cache-Related Issues**:
   - If you get stale or outdated results, use the `--clear-cache` option
   - If the cache directory becomes very large, you can safely delete it (it will be recreated)

### Getting Help

If you encounter issues not covered in this guide:

1. Check the console output for error messages
2. Review the process log for clues about where the process failed
3. File an issue on the project repository with details about the problem