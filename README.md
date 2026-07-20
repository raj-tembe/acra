# acra-cli

Agentic CLI for LLM-powered research, task execution, code generation, workflow automation, memory, and sandboxed validation.

`acra-cli` is an installable Python package that provides the `acra` command-line tool and a reusable LangGraph-based agent workflow. Install the package as `acra-cli`, run it from the terminal as `acra`, and import the Python package as `acra`.

It is built for developers who want a local CLI for asking an LLM-powered agent to research, plan, generate code, validate generated projects, and keep workflow context across runs.

> Status: beta. The package is usable, but some CLI command groups are still scaffolds. The most complete surfaces today are installation, provider configuration, profile setup, key management, the interactive shell, research workflows, and Python-level workflow APIs.

## Highlights

- Installable PyPI package: `acra-cli`
- Console command: `acra`
- Python import package: `acra`
- Interactive CLI shell powered by Typer, Rich, and prompt-toolkit
- LangGraph workflow with planner, researcher, coder, executor, critic, memory, and human nodes
- Provider support for Gemini, OpenAI, Groq, Ollama, and HuggingFace
- Configuration profiles stored in `~/.acra/config.json`
- OS keyring support for API keys
- Research command with depth, sources, formatting, output, JSON, and memory options
- Generated project saving and validation
- ChromaDB-backed vector memory and JSON workflow memory modules
- Optional extras for provider-specific dependencies and checkpoint backends

## What's New in 0.1.5

### New features

- Provider credentials can now be stored with `acra keys` and used directly by Gemini, OpenAI, Groq, and HuggingFace Cloud workflows.
- The configuration wizard stores provider and research credentials outside the plaintext profile file, using the OS keyring when available and a permission-restricted local fallback otherwise.
- Long-running task and research commands show a live progress spinner.
- Task and research results are rendered as readable summaries, findings, sources, and generated-file lists instead of raw workflow state.
- Commands launched from the interactive shell now stream their output live.

### Bug fixes

- Fixed saved provider keys not being read by LLM initialization.
- Fixed profile setup writing API and research keys to plaintext configuration.
- Fixed interactive-shell commands buffering output until completion.
- Fixed unwieldy raw dictionary and message-object output after task or research runs.

## Requirements

- Python `>=3.11`
- At least one supported LLM provider or local inference backend
- Optional: Docker, if you use execution paths that run generated projects in containers

## Installation

Install the base package:

```bash
pip install acra-cli
```

Install provider-specific extras as needed:

```bash
pip install "acra-cli[openai]"
pip install "acra-cli[groq]"
pip install "acra-cli[ollama]"
pip install "acra-cli[huggingface]"
```

Install checkpointing extras:

```bash
pip install "acra-cli[sqlite]"
pip install "acra-cli[postgres]"
```

Install multiple extras together:

```bash
pip install "acra-cli[openai,groq,sqlite]"
```

After installation, run:

```bash
acra
```

or:

```bash
python -m acra
```

## Quick Start

Configure a provider:

```bash
export LLM_PROVIDER=gemini
export GOOGLE_GEMINI_API_KEY="your-key"
```

Start the interactive shell:

```bash
acra
```

Create a local configuration profile:

```bash
acra config init
```

Show the active profile:

```bash
acra config show
```

Store a key in your OS keyring:

```bash
acra keys set GEMINI_API_KEY
```

Run a research workflow:

```bash
acra research research "Compare LangGraph and CrewAI for code-generation workflows"
```

The repeated `research research` is intentional in the current CLI: the first `research` is the command group and the second `research` is the subcommand.

## Provider Configuration

`acra` reads provider settings from environment variables. Select the active backend with:

```bash
export LLM_PROVIDER=gemini
```

Supported values:

- `gemini`
- `openai`
- `groq`
- `ollama`
- `huggingface_local`
- `huggingface_cloud`

Common optional setting:

```bash
export LLM_TEMPERATURE=0.6
```

### Gemini

Gemini support is included in the base package dependencies.

```bash
export LLM_PROVIDER=gemini
export GEMINI_MODEL=gemini-2.5-flash
export GOOGLE_GEMINI_API_KEY="your-key"
```

`GEMINI_API_KEY` is also accepted as a fallback credential variable.

### OpenAI

```bash
pip install "acra-cli[openai]"

export LLM_PROVIDER=openai
export OPENAI_MODEL=gpt-4o-mini
export OPENAI_API_KEY="your-key"
```

### Groq

```bash
pip install "acra-cli[groq]"

export LLM_PROVIDER=groq
export GROQ_MODEL=llama-3.3-70b-versatile
export GROQ_API_KEY="your-key"
```

### Ollama

```bash
pip install "acra-cli[ollama]"

export LLM_PROVIDER=ollama
export OLLAMA_MODEL=mistral
export OLLAMA_BASE_URL=http://localhost:11434
```

Make sure Ollama is running:

```bash
ollama serve
```

### HuggingFace Cloud

```bash
pip install "acra-cli[huggingface]"

export LLM_PROVIDER=huggingface_cloud
export HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1
export HF_API_KEY="your-token"
```

### HuggingFace Local

```bash
pip install "acra-cli[huggingface]"

export LLM_PROVIDER=huggingface_local
export HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1
export HF_DEVICE=cpu
```

Use `HF_DEVICE=cuda` for compatible GPU environments.

## Configuration Profiles

Profiles are stored in:

```text
~/.acra/config.json
```

Create or update the default profile:

```bash
acra config init
```

Create a named profile:

```bash
acra config init --profile work
```

Show a profile:

```bash
acra config show
acra config show --profile work
```

The setup wizard prompts for:

- provider
- model
- provider API key
- theme
- workspace path
- research API keys

## Key Management

`acra` can store credentials in your operating system keyring.

Set a key interactively:

```bash
acra keys set OPENAI_API_KEY
```

Set a key directly:

```bash
acra keys set OPENAI_API_KEY "your-key"
```

List key status:

```bash
acra keys list
```

Delete a key:

```bash
acra keys delete OPENAI_API_KEY
```

Supported provider key names are `GEMINI_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`, and `HF_API_KEY`. Keys are stored in your OS keyring when it is available. On systems without a keyring backend, acra uses a local credentials file with owner-only permissions.

Research key names:

```bash
acra keys set research.web
acra keys set research.github
acra keys set research.docs
acra keys set research.arxiv
```

Environment fallback variables:

- `GEMINI_API_KEY` or `GOOGLE_GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `HF_API_KEY`
- `ACRA_RESEARCH_WEB_KEY`
- `ACRA_RESEARCH_GITHUB_KEY`
- `ACRA_RESEARCH_DOCS_KEY`
- `ACRA_RESEARCH_ARXIV_KEY`

## CLI Usage

Run the top-level help after installation:

```bash
acra --help
```

Global options include:

- `--profile`
- `--workspace`
- `--no-memory`
- `--dry-run`
- `--json`
- `--verbose` / `-v`
- `--quiet` / `-q`
- `--timeout`

### Interactive Shell

Running `acra` without a subcommand starts the shell:

```bash
acra
```

You can also launch it explicitly:

```bash
acra serve
```

Inside the shell, type commands such as:

```text
config show
keys list
research research "What are good approaches for agent memory?"
memory list
session list
graph show
exit
```

### Research

Run:

```bash
acra research research "What is the best architecture for a local-first AI coding agent?"
```

Options:

- `--depth`: `shallow`, `standard`, or `deep`
- `--sources`: comma-separated source list
- `--format`: `citations`, `summary`, or `detailed`
- `--output`: write output to a file
- `--save`: persist research output into memory
- `--follow-up`: keep the session open for follow-up questions
- `--no-memory`: skip memory persistence
- `--profile`: select a profile
- `--json`: output JSON
- `--verbose` / `-v`: show detailed output

Examples:

```bash
acra research research "Survey Python sandboxing options" --depth deep
```

```bash
acra research research "Compare ChromaDB and FAISS for agent memory" \
  --sources web,github,arxiv \
  --format detailed \
  --output research-report.md
```

```bash
acra research research "LangGraph checkpointing options" \
  --format summary \
  --json
```

### Other Commands

Configuration:

```bash
acra config init
acra config show
```

Keys:

```bash
acra keys set GEMINI_API_KEY
acra keys list
acra keys delete GEMINI_API_KEY
```

Memory:

```bash
acra memory list
acra memory search "previous docker error"
acra memory clear
```

Sessions:

```bash
acra session list
acra session resume <session-id>
```

Graph:

```bash
acra graph show
acra graph run
```

Note: `memory`, `session`, and `graph` command groups are currently available but include placeholder handlers in this beta release. The underlying Python modules are more complete than the current CLI wrappers.

## Python Usage

The package exposes reusable workflow and configuration modules.

Run the compiled LangGraph workflow:

```python
from acra.graph.workflow import OmniAgentCallbacks, create_workflow

workflow = create_workflow()

result = workflow.invoke(
    {
        "user_request": "Build a small Python CLI that validates JSON files",
        "interactive": False,
        "retry_count": 0,
        "max_retries": 5,
    },
    config={"callbacks": [OmniAgentCallbacks()]},
)

print(result)
```

Use the LLM factory:

```python
from acra.agents.llm import llm

model = llm()
response = model.invoke("Say hello in one sentence.")

print(response.content if hasattr(response, "content") else response)
```

Load a profile:

```python
from acra.config.profile_manager import ProfileManager

profile = ProfileManager().load_profile()
print(profile)
```

Use JSON memory:

```python
from acra.agents.memory.memory_manager import get_memory_manager

memory = get_memory_manager("example-session")
memory.add_memory(
    "workflow_result",
    {
        "user_request": "Create a CLI",
        "execution_success": True,
        "quality_score": 8.5,
    },
)

print(memory.get_recent_memories(limit=3))
```

## Data Locations

Profile configuration:

```text
~/.acra/config.json
```

Application data is stored in a platform-specific user data directory resolved with `platformdirs`.

Override it with:

```bash
export OMNIAGENT_DATA_DIR=/path/to/acra-data
```

Important subdirectories:

- `credentials.json`: permission-restricted credential fallback when no OS keyring is available
- `projects/`: generated project files
- `memory/storage/`: JSON memory files
- `memory/chroma_db/`: ChromaDB vector memory
- `memory/checkpoints/data/`: workflow checkpoint data

## Current Beta Notes

- The package version is `0.1.5`.
- The top-level CLI currently attaches `serve`, `config`, `keys`, `research`, `memory`, `session`, `graph`, and `workspace`.
- The codebase contains additional command modules such as `brain`, `context`, `logs`, and `plugin`, but they are not currently attached to the top-level CLI.
- Some CLI command groups return placeholder output while the Python modules behind them continue to evolve.

## Troubleshooting

### Missing provider dependency

Install the matching extra:

```bash
pip install "acra-cli[openai]"
pip install "acra-cli[groq]"
pip install "acra-cli[ollama]"
pip install "acra-cli[huggingface]"
```

### Missing API key

Set the provider key:

```bash
export GOOGLE_GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GROQ_API_KEY="your-key"
export HF_API_KEY="your-token"
```

Or store it with:

```bash
acra keys set GEMINI_API_KEY
```

### Ollama connection failure

Start Ollama and make sure the model is available:

```bash
ollama serve
ollama pull mistral
```

Then configure:

```bash
export LLM_PROVIDER=ollama
export OLLAMA_MODEL=mistral
export OLLAMA_BASE_URL=http://localhost:11434
```

## License

`acra-cli` is licensed under the GNU Affero General Public License v3.

## Package Metadata

- PyPI package name: `acra-cli`
- Console command: `acra`
- Python import package: `acra`
- Version: `0.1.5`
- Python: `>=3.11`
- Console script: `acra=acra.cli:app_main`
- Author: Raj Tembe
