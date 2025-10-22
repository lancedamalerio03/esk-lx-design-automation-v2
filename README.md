# esk-lx-design-automation-v2

## 🚀 LX Design Automation with LangChain

Automated learning experience design and sprint generation system powered by LangChain, supporting multiple LLM providers with comprehensive tracking.

### ✨ Recent Updates

**Phase 2: Agentic Workflows** ✅ NEW!
- 🔍 **Research agents** with real-time search capabilities
- **Perplexity integration** for citation-backed research
- **Automatic agent activation** for Topic and Model Research stages
- Visible reasoning in LangSmith traces
- Enhanced research quality with current information

**Phase 1: LangChain Integration** ✅
- Multi-provider LLM support (OpenAI + Gemini)
- Uses `init_chat_model()` - LangChain's standardized approach
- LangSmith integration for detailed AI call tracking
- Free testing with Gemini Flash models (including 2.5!)
- Dual tracking: Google Sheets + LangSmith

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys:**
   See [LANGCHAIN_SETUP.md](LANGCHAIN_SETUP.md) for detailed setup instructions

3. **Run the app:**
   ```bash
   streamlit run main.py
   ```

### Available LLM Providers

- **OpenAI**: GPT-5, GPT-4.1, GPT-4o, o3 models
- **Gemini**: Flash 2.5 (FREE 🆓), Flash 1.5, Pro 1.5
- **Claude**: Sonnet 4.5, Sonnet 4, 3.7, 3.5, Opus, Haiku
- **Perplexity**: Sonar Reasoning Pro, Sonar Reasoning (reasoning models)

**Agent Search Tool:** Perplexity Sonar Search (separate from reasoning models)

### Documentation

**Phase 2 (Agents):**
- [Phase 2 Complete Guide](PHASE2_COMPLETE.md) - Agentic workflows implementation & testing
- [Perplexity Setup](PERPLEXITY_SETUP.md) - Get your API key and configure search

**Phase 1 (LangChain):**
- [LangChain Setup Guide](LANGCHAIN_SETUP.md) - Complete setup and configuration
- [LangChain Best Practices](LANGCHAIN_BEST_PRACTICES.md) - Why we use `init_chat_model()`
- [Prompt Architecture](PROMPT_ARCHITECTURE_EXPLAINED.md) - How prompts combine with context

**General:**
- [Migration Plan](langchain-migration-plan.plan.md) - Full migration roadmap
- [Claude Context](CLAUDE.md) - Project background and architecture

### Features

1. **Topic Research** - 🔍 Agent-enhanced research with real-time search
2. **Client Conversation** - Generate client transcripts and extract information
3. **Model Deliverable** - 🔍 Agent-enhanced model research + deliverable creation
4. **PRD Generation** - Comprehensive Product Requirements Documents
5. **Sprint Backlog** - Coming soon

🔍 = Research agent with Perplexity search automatically enabled

### Support

For setup issues or questions, refer to [LANGCHAIN_SETUP.md](LANGCHAIN_SETUP.md)
