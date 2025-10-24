# Copilot Instructions for ChattingCustoms

## Project Overview
This project implements a modular chatbot system for customs/trade-related queries, with a focus on Singapore customs workflows. The main logic is in `src/chattingcustoms/`, with specialized bots in `core/` and utility functions in `helper/`.

## Architecture & Data Flow
- **Entry Points:** Main scripts are in `src/chattingcustoms/` (e.g., `main.py`, `main_complex.py`).
- **Chatbot Logic:** Each chatbot (e.g., `tno_chatbot.py`, `expert_trader_chatbot.py`) encapsulates domain-specific rules and response logic.
- **Routing:** `router.py` dispatches queries to the appropriate chatbot.
- **Helpers:** Shared utilities (file, geo, key, network, prompt) are in `helper/`.
- **Data:**
  - `datastore/appData/threatData.csv` and `datastore/ragData/GeoLite2-City.mmdb` are used for threat and geolocation lookups.
  - Extraction and rule logic in chatbots often reference these data sources.

## Key Patterns & Conventions
- **Prompt Engineering:** System/user messages are constructed and passed to `prompt_util.get_completion_from_messages()` for LLM interaction. See `tno_chatbot.py` for step-by-step reasoning prompts.
- **Rule-Based Decisions:** Business logic is encoded as multi-step rules in plain text blocks (see `data` in `tno_chatbot.py`).
- **XML-like Input:** Some chatbots expect user queries in XML-like format and extract fields using a defined mapping (see `extraction_list`).
- **Error Handling:** Responses like `YOUARELATE`, `NOEMPTYDATEOFDEPARTURE`, etc., are returned for specific rule violations.
- **Markdown Output:** All chatbot responses are returned in markdown, with step-by-step explanations.

## Developer Workflows
- **No explicit build step**; run main scripts directly (e.g., `python src/chattingcustoms/main.py`).
- **Testing:** No standard test suite detected; validate changes by running main scripts and checking chatbot responses.
- **Debugging:** Add print statements or inspect intermediate variables in main/chatbot files.

## Integration Points
- **External Data:** Ensure CSV and MMDB files are present in `datastore/` for full functionality.
- **LLM/Prompt API:** All chatbots rely on `prompt_util` for LLM completions; adapt this for different LLM providers if needed.

## Examples
- To add a new rule, update the `data` block in the relevant chatbot and adjust extraction logic as needed.
- To support a new input format, modify the XML extraction and `is_user_query_xml` logic.

## Key Files
- `src/chattingcustoms/core/tno_chatbot.py`: Example of rule-based, stepwise reasoning and XML extraction.
- `src/chattingcustoms/core/router.py`: Query dispatch logic.
- `src/chattingcustoms/helper/prompt_util.py`: LLM interaction abstraction.

---

For questions or unclear conventions, review the main chatbot files and helper utilities for concrete examples.
