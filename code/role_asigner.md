# role_asigner.py Documentation

## Overview

`role_asigner.py` implements **Stage 0** of the Multi-LLM Collaborative Debate System: Role Assignment. This stage uses self-assessment to dynamically assign roles (3 Solvers, 1 Judge) to the available LLM models based on their perceived strengths for each specific problem.

## Purpose

Rather than using fixed role assignments, the system:
- Allows each LLM to self-assess which role it's best suited for
- Assigns roles algorithmically based on confidence scores and preferences
- Adapts to problem characteristics (e.g., math vs. logic vs. game theory)

## Main Functions

### `self_assess_role(problem_text, model_name, model_id)`
Gets a self-assessment from a single LLM about which role it prefers.

**Parameters:**
- `problem_text` (str): The problem statement
- `model_name` (str): Name of the LLM model (e.g., `"gpt-4"`)
- `model_id` (str): Identifier for the model (e.g., `"model_1"`)

**Returns:**
- Dictionary containing:
  - `role_preferences`: Ordered list `["Solver", "Judge"]` or `["Judge", "Solver"]`
  - `confidence_by_role`: Dictionary with confidence scores for each role
  - `reasoning`: Explanation of preferences
  - `model_id`: Model identifier
  - `model_name`: Model name

### `assign_roles_algorithmically(self_assessments)`
Deterministically assigns roles based on self-assessments.

**Parameters:**
- `self_assessments` (list): List of 4 self-assessment dictionaries

**Returns:**
- Dictionary with role assignments:
  ```python
  {
      "solver_1": {...},  # Self-assessment dict
      "solver_2": {...},
      "solver_3": {...},
      "judge": {...}
  }
  ```

**Assignment Algorithm:**
1. Calculate scores for each role (confidence + preference boost)
2. Sort models by solver score (top 3 become solvers)
3. Sort models by judge score (top 1 becomes judge)
4. If judge is in solver list, swap with next best judge candidate

### `assign_roles(problem_id, problem_text)`
Main function that orchestrates the complete role assignment process.

**Parameters:**
- `problem_id` (str): Unique problem identifier
- `problem_text` (str): Problem statement

**Returns:**
- Dictionary with final role assignments (same structure as `assign_roles_algorithmically`)

**Output File:**
- Saves to: `data/raw_outputs/{problem_id}_stage0_roles.json`

## Role Assignment Process

1. **Self-Assessment**: Each of 4 models assesses its preferred role
2. **Score Calculation**: Confidence scores + preference bonuses
3. **Algorithmic Assignment**: Top 3 solvers, top 1 judge (with conflict resolution)
4. **Output**: Final assignments saved for use in subsequent stages

## LLM Prompt Structure

The self-assessment prompt includes:
- Problem statement
- Available roles (Solver, Judge)
- Instructions to provide preferences and confidence scores

## API Calls

- **4 API calls** (one per model)
- Uses models from `MODELS` config (typically 4 different models)
- Temperature: `TEMPERATURES["solver"]` (from config)
- Response format: JSON object

## Error Handling

- **API errors**: Retries with exponential backoff (via `call_llm`)
- **JSON parsing**: Handles markdown-wrapped JSON responses
- **Model compatibility**: Falls back to text-based JSON parsing if `response_format` not supported

## Dependencies

### Internal
- `config.py`: API key, models list, temperatures, paths, retry settings

### External
- `openai`: OpenAI API client

### Standard Library
- `json`: JSON parsing
- `os`: File operations
- `time`: Rate limiting

## Example Output Structure

```json
{
  "problem_id": "math_001",
  "self_assessments": [
    {
      "model_id": "model_1",
      "model_name": "gpt-4",
      "role_preferences": ["Solver", "Judge"],
      "confidence_by_role": {
        "Solver": 0.9,
        "Judge": 0.7
      },
      "reasoning": "I excel at step-by-step problem solving..."
    },
    ...
  ],
  "final_assignments": {
    "solver_1": {...},
    "solver_2": {...},
    "solver_3": {...},
    "judge": {...}
  }
}
```

## Integration

- **Input**: Problem statement
- **Output**: Used by all subsequent stages to know which model has which role
- **Called by**: `orchestrator.py` as the first stage of the pipeline

## Standalone Usage

Can be run independently for testing:

```bash
python code/role_asigner.py
```

This will:
1. Use a test problem
2. Get self-assessments from all 4 models
3. Assign roles algorithmically
4. Save results to `data/raw_outputs/`

## Key Features

- **Dynamic Assignment**: Roles adapt to problem characteristics
- **Self-Awareness**: LLMs assess their own strengths
- **Conflict Resolution**: Ensures judge is not also a solver
- **Transparency**: Saves both self-assessments and final assignments

## Model Compatibility

The `call_llm` function includes a fallback mechanism for models that don't support `response_format={"type": "json_object"}`:
1. First attempts with `response_format` parameter
2. If that fails with a `response_format` error, retries without it
3. Requests JSON in the prompt and parses from text response
4. Handles markdown code block wrapping
