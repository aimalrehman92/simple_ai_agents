# Simple AI Agents

A collection of small tool-using agents built from scratch with Python and the OpenAI API.

The repository focuses on the mechanics behind a basic agent:

1. The language model decides whether it needs a tool.
2. Python parses the requested action.
3. The selected function is executed.
4. The result is returned to the model as an observation.
5. The loop continues until the model produces a final answer.

No LangChain, LlamaIndex, or agent framework is used.

## Agents

| Folder | Agent | What it does |
|---|---|---|
| `01_research_agent` | Research Agent | Searches arXiv, retrieves paper details, and calculates paper age |
| `02_expense_agent` | Expense Agent | Records expenses, calculates totals, and checks budgets |
| `03_text_analysis_agent` | Text Analysis Agent | Counts text, estimates reading time, extracts keywords, and analyzes writing style |
| `04_file_organizer_agent` | File Organizer Agent | Inspects, classifies, previews, and organizes files by type |
| `05_dataset_inspector_agent` | Dataset Inspector Agent | Loads CSV files and inspects columns, missing values, rows, and summary statistics |
| `06_study_planner_agent` | Study Planner Agent | Estimates study time, prioritizes topics, and creates schedules |
| `07_code_reviewer_agent` | Python Code Reviewer Agent | Checks syntax, structure, line length, function size, and docstrings |
| `08_notes_agent` | Notes Agent | Lists, searches, opens, and summarizes local Markdown and text notes |
| `09_product_comparison_agent` | Product Comparison Agent | Compares user-provided products by price, rating, features, and budget |
| `10_statistics_agent` | Statistics Agent | Calculates descriptive statistics, z-scores, classification metrics, and correlation |

## Repository structure

```text
simple_ai_agents/
├── shared/
│   ├── __init__.py
│   ├── agent.py
│   └── chatbot.py
├── 01_research_agent/
├── 02_expense_agent/
├── 03_text_analysis_agent/
├── 04_file_organizer_agent/
├── 05_dataset_inspector_agent/
├── 06_study_planner_agent/
├── 07_code_reviewer_agent/
├── 08_notes_agent/
├── 09_product_comparison_agent/
├── 10_statistics_agent/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

Each agent defines its own tools, prompt, and entry point. The reusable chatbot wrapper and execution loop live in `shared/`.

## How the agent loop works

The model requests a tool using a simple text format:

```text
Thought: I need to inspect the dataset.
Action: get_column_names: {}
PAUSE
```

Python extracts the action name and input, checks that the tool is allowed, and executes the corresponding function.

The tool result is returned to the model:

```text
Observation: age, income, occupation
```

The model then either requests another tool or produces a final answer.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Add your OpenAI API key to `.env`:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

Before running an agent, make the key available to the current shell:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

On Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

## Running an agent

Run commands from the repository root:

```bash
python 01_research_agent/main.py
```

Replace the folder name with the agent you want to use.

## Design choices

- One reusable execution loop
- Ordinary Python functions as tools
- Explicit tool allowlists
- Structured JSON tool inputs
- Maximum-turn limits
- No API calls during module imports
- Minimal third-party dependencies
- Tools that can be tested independently of the language model

## Scope

These agents are intentionally small. They are meant to expose the core mechanics of tool use, action parsing, observation handling, and multi-step execution before introducing larger agent frameworks.
