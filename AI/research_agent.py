"""
Research Agent Framework
Uses LangChain agents with Perplexity search tool for enhanced research capabilities
"""

import os
from typing import Dict, Any, Optional
import streamlit as st
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_core.messages import SystemMessage, HumanMessage

from AI.langchain_llm import get_chat_model
from keys.config import PERPLEXITY_API_KEY


# Tool definitions
def perplexity_search(query: str) -> str:
    """
    Search using Perplexity API for real-time, citation-backed information
    
    Args:
        query: Search query string
        
    Returns:
        Search results with citations
    """
    if not PERPLEXITY_API_KEY:
        return "Error: Perplexity API key not configured. Please add PERPLEXITY_API_KEY to secrets."
    
    try:
        import requests
        
        # Perplexity API endpoint
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",  # Fast, cost-effective search model
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant. Provide accurate, citation-backed information."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.2,
            "max_tokens": 2000,
            "return_citations": True,
            "return_images": False
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract content and citations
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        citations = data.get("citations", [])
        
        # Format response with citations
        result = content
        if citations:
            result += "\n\n**Sources:**\n"
            for i, citation in enumerate(citations[:5], 1):  # Limit to top 5 citations
                result += f"{i}. {citation}\n"
        
        return result
        
    except requests.exceptions.Timeout:
        return "Error: Perplexity API request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error calling Perplexity API: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


# Create the Perplexity search tool
perplexity_tool = Tool(
    name="perplexity_search",
    func=perplexity_search,
    description=(
        "Search for current, factual information using Perplexity AI. "
        "Use this to find recent data, statistics, best practices, case studies, "
        "and real-world examples. Returns citation-backed results. "
        "Input should be a clear, specific search query."
    )
)


# ReAct Agent prompt template
RESEARCH_AGENT_PROMPT = """You are a learning experience design research assistant with access to search tools.

Your goal is to conduct thorough research based on the instructions and context provided.

You have access to the following tools:

{tools}

Tool names: {tool_names}

Use the following format:

Question: the research task you must complete
Thought: think about what information you need and what tool to use
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action (a specific search query)
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have enough information to provide a comprehensive answer
Final Answer: your detailed research output based on all observations

IMPORTANT GUIDELINES:
- Use the search tool multiple times with different queries to gather comprehensive information
- Always cite sources when using search results
- Synthesize information from multiple searches into a coherent output
- Focus on recent, relevant, and authoritative information
- When instructed by the prompts, structure your output according to those instructions

Begin!

Question: {input}

{agent_scratchpad}"""


def create_research_agent(model_name: str, temperature: float = 0.7) -> AgentExecutor:
    """
    Create a LangChain research agent with Perplexity search tool
    
    Args:
        model_name: Name of the LLM model to use
        temperature: Sampling temperature
        
    Returns:
        AgentExecutor ready to perform research tasks
    """
    # Get the chat model
    llm = get_chat_model(model_name, temperature=temperature, max_tokens=15000)
    
    # Define available tools
    tools = [perplexity_tool]
    
    # Create prompt template
    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        template=RESEARCH_AGENT_PROMPT
    )
    
    # Create the ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # Show reasoning steps
        max_iterations=10,  # Allow multiple search queries
        handle_parsing_errors=True,
        return_intermediate_steps=True  # Track tool usage for LangSmith
    )
    
    return agent_executor


def run_research_agent(
    combined_prompt: str,
    context: Dict[str, Any],
    model_name: str,
    step_name: str = "research"
) -> Optional[str]:
    """
    Run the research agent with prompts and context
    
    Args:
        combined_prompt: System instructions (meta + module prompts)
        context: Dictionary with topic and other context data
        model_name: Name of the LLM model to use
        step_name: Name of the workflow step (for logging)
        
    Returns:
        Generated research content or None on error
    """
    try:
        # Create the agent
        agent = create_research_agent(model_name)
        
        # Format the input for the agent
        # Combine prompts (instructions) with context (data to work with)
        context_str = "\n\n".join([f"**{k}:** {v}" for k, v in context.items()])
        
        agent_input = f"""
**INSTRUCTIONS:**
{combined_prompt}

**CONTEXT:**
{context_str}

Based on the instructions and context above, conduct thorough research and generate the requested output.
Use the search tool to find current, relevant information to enhance your research.
"""
        
        # Run the agent
        result = agent.invoke({"input": agent_input})
        
        # Extract the final answer
        output = result.get("output", "")
        
        if not output:
            st.error("Agent did not produce any output")
            return None
        
        return output
        
    except Exception as e:
        st.error(f"Error running research agent: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None


def get_agent_metadata(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from agent execution for logging
    
    Args:
        result: Agent execution result
        
    Returns:
        Dictionary with execution metadata
    """
    metadata = {
        "tool_calls": 0,
        "tools_used": [],
        "iterations": 0
    }
    
    try:
        intermediate_steps = result.get("intermediate_steps", [])
        metadata["iterations"] = len(intermediate_steps)
        
        for step in intermediate_steps:
            if len(step) >= 2:
                action = step[0]
                if hasattr(action, 'tool'):
                    tool_name = action.tool
                    metadata["tool_calls"] += 1
                    if tool_name not in metadata["tools_used"]:
                        metadata["tools_used"].append(tool_name)
        
    except Exception as e:
        print(f"Error extracting agent metadata: {e}")
    
    return metadata

