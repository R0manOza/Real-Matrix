# refiner.py Documentation

## Overview

`refiner.py` implements **Stage 3** of the Multi-LLM Collaborative Debate System: Solution Refinement. In this stage, each solver reviews the peer feedback they received and refines their original solution accordingly.

## Purpose

After receiving peer reviews in Stage 2, solvers have the opportunity to:
- Evaluate the validity of critiques
- Address valid concerns
- Improve their solutions based on feedback
- Maintain their original answer if they believe critiques are invalid

## Main Functions

### `refine_solution(problem_text, original_solution, reviews, solver_id)`
Refines a single solver's solution based on peer reviews.

**Parameters:**
- `problem_text` (str): Original problem statement
- `original_solution` (dict): Solver's original solution from Stage 1
- `reviews` (list): List of two review dictionaries from other solvers
- `solver_id` (str): ID of the solver (e.g., `"solver_1"`)

**Returns:**
- Dictionary containing:
  - `solver_id`: Solver identifier
  - `model_name`: LLM model used
  - `original_solution`: Reference to original solution
  - `critiques_accepted`: List of accepted critiques
  - `critiques_rejected`: List of rejected critiques with explanations
  - `refinement_reasoning`: Explanation of refinement process
  - `reasoning_steps`: Updated step-by-step reasoning
  - `final_answer`: Refined final answer
  - `confidence`: Confidence score (0.0-1.0)
  - `changed_from_original`: Boolean indicating if answer changed
  - `improvement_explanation`: Explanation of improvements
  - `raw_response`: Full LLM response

### `refine_solutions(problem_id, problem_text, solutions, reviews)`
Main function that orchestrates refinement for all three solvers.

**Parameters:**
- `problem_id` (str): Unique problem identifier
- `problem_text` (str): Problem statement
- `solutions` (dict): Dictionary from Stage 1 with all three solutions
- `reviews` (dict): Dictionary from Stage 2 with all peer reviews

**Returns:**
- Dictionary with refined solutions:
  ```python
  {
      "solver_1": {...},
      "solver_2": {...},
      "solver_3": {...}
  }
  ```

**Output File:**
- Saves to: `data/raw_outputs/{problem_id}_stage3_refined.json`

## Refinement Process

1. **Review Analysis**: Each solver receives two peer reviews
2. **Critique Evaluation**: Solver decides which critiques are valid
3. **Solution Update**: Solver refines reasoning and/or answer
4. **Justification**: Solver explains changes (or why they kept original)

## LLM Prompt Structure

The refinement prompt includes:
- Original problem statement
- Solver's original solution (reasoning steps, answer, approach)
- Peer reviews (strengths, weaknesses, errors, suggestions)
- Instructions to evaluate critiques and refine solution

## API Calls

- **3 API calls** (one per solver)
- Uses solver's original model from Stage 1
- Temperature: `TEMPERATURES["solver"]` (from config)
- Response format: JSON object

## Error Handling

- **Missing solutions**: Raises `ValueError` if solver not found
- **Missing reviews**: Raises `ValueError` if reviews incomplete
- **API errors**: Retries with exponential backoff (via `call_llm`)
- **JSON parsing**: Handles markdown-wrapped JSON responses

## Dependencies

### Internal
- `config.py`: API key, temperatures, paths, retry settings

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
  "problem_text": "...",
  "refined_solutions": {
    "solver_1": {
      "solver_id": "solver_1",
      "model_name": "gpt-4",
      "critiques_accepted": ["Missing edge case", "Calculation error"],
      "critiques_rejected": ["Approach is wrong"],
      "refinement_reasoning": "...",
      "reasoning_steps": ["Step 1: ...", "Step 2: ..."],
      "final_answer": "42",
      "confidence": 0.95,
      "changed_from_original": true,
      "improvement_explanation": "Fixed calculation error..."
    },
    "solver_2": {...},
    "solver_3": {...}
  },
  "timestamp": "2024-01-01 12:00:00"
}
```

## Integration

- **Input**: Requires Stage 1 (solutions) and Stage 2 (reviews)
- **Output**: Used by Stage 4 (judge) to evaluate final solutions
- **Called by**: `orchestrator.py` as part of the full pipeline

## Standalone Usage

Can be run independently for testing:

```bash
python code/refiner.py
```

This will:
1. Load the first problem from the dataset
2. Load existing Stage 1 and Stage 2 outputs
3. Run refinement
4. Save results to `data/raw_outputs/`

## Key Features

- **Selective Acceptance**: Solvers can accept or reject critiques
- **Transparency**: Tracks which critiques were accepted/rejected
- **Change Tracking**: Records whether the answer changed
- **Confidence Scoring**: Maintains confidence levels after refinement
