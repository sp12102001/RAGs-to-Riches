"""
Agent definitions for the research pipeline
"""

from src.agents.research_agent import research_agent
from src.agents.evaluation_agent import evaluation_agent
from src.agents.appraisal_agent import appraisal_agent
from src.agents.report_agent import report_agent

# Export all agents
__all__ = ["research_agent", "evaluation_agent", "appraisal_agent", "report_agent"]
