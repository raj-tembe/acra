# ACRA Usage Guide

ACRA is an agentic CLI for LLM-powered workflows, configuration, research, memory, and session management.

## 1. Installation

From the project root:

```bash
source .venv/bin/activate
pip install -e .
```

Run the CLI with:

```bash
python -m acra
```

Or, after installation:

```bash
acra
```

---

## 2. Start the interactive shell

The default entrypoint launches an interactive shell:

```bash
acra
```

or

```bash
python -m acra
```

From the shell, you can type commands such as:

```text
acra init
acra brain models
acra config show
serve
exit
```

---

## 3. Main commands

### `acra init`
Initializes a new profile configuration.

Use it when you want to create or update your local ACra profile.

```bash
acra init
```

This prompts for:
- provider
- model
- API key
- theme
- workspace path
- research configuration

---

### `acra brain`
Manages brain/provider-related configuration.

#### Subcommands

- `acra brain add <name> --provider <provider>`
  Add a new brain profile.

- `acra brain use <name>`
  Switch to an existing brain profile.

- `acra brain list`
  List configured brains.

- `acra brain test <name>`
  Test a brain profile.

- `acra brain models`
  List available models.

Example:

```bash
acra brain models
acra brain list
```

---

### `acra config`
Manages configuration profiles.

#### Subcommands

- `acra config init`
  Create or update a profile.

- `acra config show`
  Display the current profile configuration.

Example:

```bash
acra config init
acra config show
```

---

### `acra serve`
Launches the interactive ACra shell.

```bash
acra serve
```

If you are already inside the shell, you can also type:

```text
serve
```

---

### `acra research`
Runs research-related workflows.

Usage depends on the current implementation and extensions in your environment.

Example:

```bash
acra research
```

---

### `acra memory`
Works with memory-related operations.

#### Subcommands

- `acra memory list`
- `acra memory clear`
- `acra memory search`

Example:

```bash
acra memory list
```

---

### `acra session`
Handles session-related operations.

#### Subcommands

- `acra session list`
- `acra session resume`

Example:

```bash
acra session list
```

---

### `acra graph`
Manages graph-related commands.

#### Subcommands

- `acra graph show`
- `acra graph run`

Example:

```bash
acra graph show
```

---

### `acra keys`
Manages API keys and credentials.

#### Subcommands

- `acra keys set`
- `acra keys list`
- `acra keys delete`

Example:

```bash
acra keys list
```

---

### `acra workspace`
Provides workspace utility commands.

Example:

```bash
acra workspace
```

---

## 4. Common workflows

### Create a profile

```bash
acra init
```

### List available models

```bash
acra brain models
```

### Start the shell

```bash
acra serve
```

### Show active configuration

```bash
acra config show
```

### Exit the shell

Type:

```text
exit
```

---

## 5. Useful tips

- Run `acra --help` to see the full command list.
- Run `acra <command> --help` to see subcommand options.
- If a command group is invoked without a subcommand, ACra will show a help message.
- For interactive setup, use `acra init` and follow the prompts.

---

## 6. Example session

```bash
acra init
acra brain models
acra config show
acra serve
```

This should give you a basic working flow for setting up and using ACra.
