# Copilot Instructions for LocalAI-Agent

## Project Overview
This project is a local AI agent framework that interacts with users via a command-line interface. It supports memory management, web search, and learning from various sources (PDF, EPUB, URLs) using modular extractors. The main entry point is `scripts/agent.py`.

## Key Components
- **scripts/agent.py**: Main CLI loop, orchestrates user input, memory, web search, and AI model interaction.
- **learn_from_pdf.py, learn_from_ebook.py, learn_from_url.py**: Extraction utilities for ingesting content from different sources.
- **memory.json**: Stores facts and notes, organized by category and key, case-insensitive.

## Memory Management
- Facts and notes are stored in `memory.json` (relative to `scripts/`).
- Use `save_fact(category, key, value)` and `add_note(category, note)` for structured memory.
- All category and key lookups are case-insensitive.

## User Input Patterns
- The CLI recognizes commands by prefix:
  - `remember that <category> <key>: <value>` → Save a fact
  - `note for <category>: <note>` → Add a note
  - `what is <category> <key>` → Recall a fact
  - `search for <query>` → Web search (DuckDuckGo)
  - `learn from url/pdf/epub <path or url>` → Ingest content
  - All other input is sent to the local AI model via `ask_ollama()`

## AI Model Integration
- Uses Ollama's local API (`http://localhost:11434/api/generate`) with the `mistral` model by default.
- The agent streams responses and prints them to the user.

## Project Conventions
- All memory operations are atomic and update `memory.json` in-place.
- Extraction modules must provide an `extract_text_from_*` function.
- Web search uses DuckDuckGo HTML scraping (not an API).
- All user-facing strings are emoji-prefixed for clarity.

## Extending the Agent
- To add new learning sources, create a new `learn_from_x.py` with an `extract_text_from_x()` function and import it in `agent.py`.
- To add new commands, extend the main loop in `agent.py` with a new `elif` block matching the input pattern.

## Example Workflow
1. User: `remember that python creator: Guido van Rossum`
2. User: `note for python: Interpreted language`
3. User: `what is python creator`
4. User: `search for AI agents in python`
5. User: `learn from pdf ./docs/ai.pdf`

## Troubleshooting
- If `memory.json` is missing, it is auto-created.
- If a module is missing, ensure it is in the `scripts/` directory and imported in `agent.py`.

---
_If any conventions or workflows are unclear, please provide feedback for further clarification._
