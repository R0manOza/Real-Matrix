# judge.py Documentation

## Overview

`judge.py` implements **Stage 4** of the Multi-LLM Collaborative Debate System: Final Judgment. In this stage, the judge (a dedicated LLM) evaluates all solutions (both original and refined) along with peer reviews, and selects the winning solution and final answer.

## Purpose

After all solvers have generated, reviewed, and refined their solutions, the judge:
- Evaluates the quality and correctness of all solutions
- Considers peer reviews and how critiques were addressed
- Determines which solution is most likely correct
- Selects the final winning answer

## Main Functions

### `judge_solutions(problem_text, solutions, reviews, refined_solutions, judge_info)`
Has the judge evaluate all solutions and select the winner.

**Parameters:**
- `problem_text` (str): Original problem statement
- `solutions` (dict): Dictionary from Stage 1 with original solutions
- `reviews` (dict): Dictionary from Stage 2 with all peer reviews
- `refined_solutions` (dict): Dictionary from Stage 3 with refined solutions
- `judge_info` (dict): Dictionary with judge's model information from role assignments

**Returns:**
- Dictionary containing:
  - `judge_model`: Model used by judge
  - `winner`: ID of winning solver (`"solver_1"`, `"solver_2"`, or `"solver_3"`)
  - `winning_answer`: The final answer selected
  - `evaluation`: Detailed evaluation of each solver:
    ```python
    {
        "solver_1": {
            "original_score": 0.0-1.0,
            "refined_score": 0.0-1.0,
            "reasoning_quality": "excellent" | "good" | "fair" | "poor",
            "likely_correct": true/false
        },
        "solver_2": {...},
        "solver_3": {...}
    }
    ```
  - `selection_reasoning`: Detailed explanation of winner selection
  - `consensus_analysis`: Analysis of solver agreement/disagreement
  - `confidence`: Confidence score (0.0-1.0)
  - `raw_response`: Full LLM response

### `make_judgment(problem_id, problem_text, solutions, reviews, refined_solutions, role_assignments)`
Main function that orchestrates the final judgment process.

**Parameters:**
- `problem_id` (str): Unique problem identifier
- `problem_text` (str): Problem statement
- `solutions` (dict): Dictionary from Stage 1 with original solutions
- `reviews` (dict): Dictionary from Stage 2 with all peer reviews
- `refined_solutions` (dict): Dictionary from Stage 3 with refined solutions
- `role_assignments` (dict): Dictionary from Stage 0 with judge information

**Returns:**
- Dictionary with the judgment (same structure as `judge_solutions`)

**Output Files:**
- `data/raw_outputs/{problem_id}_stage4_judgment.json`: Full judgment data
- `data/results/{problem_id}_final_result.json`: Final result (used by evaluator)

## Judgment Process

1. **Solution Review**: Judge examines all original and refined solutions
2. **Review Analysis**: Judge considers peer feedback and how critiques were addressed
3. **Evaluation**: Judge scores each solution on multiple dimensions
4. **Selection**: Judge determines which solution is most likely correct
5. **Justification**: Judge provides detailed reasoning for the selection

## LLM Prompt Structure

The judgment prompt includes:
- Original problem statement
- All solutions (original + refined) with:
  - Reasoning steps
  - Final answers
  - Confidence scores
  - Change indicators
  - Improvement explanations
- Peer reviews for each solution
- Instructions to evaluate and select the best answer

**Note:** The prompt construction has been optimized to reduce token usage by:
- Truncating reasoning steps (keeping first 3 and last 2)
- Limiting approach/improvement explanations to 200 characters
- Summarizing peer reviews (showing counts and 150-char summary)

## API Calls

- **1 API call** (judge evaluates all solutions in one call)
- Uses judge's model from Stage 0 role assignments
- Temperature: `TEMPERATURES["judge"]` (from config)
- Response format: JSON object

## Error Handling

- **Missing judge**: Raises `ValueError` if judge not in role assignments
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
- `time`: Rate limiting and timestamps

## Example Output Structure

```json
{
  "problem_id": "math_001",
  "problem_text": "...",
  "judgment": {
    "judge_model": "gpt-4",
    "winner": "solver_2",
    "winning_answer": "42",
    "evaluation": {
      "solver_1": {
        "original_score": 0.7,
        "refined_score": 0.8,
        "reasoning_quality": "good",
        "likely_correct": false
      },
      "solver_2": {
        "original_score": 0.9,
        "refined_score": 0.95,
        "reasoning_quality": "excellent",
        "likely_correct": true
      },
      "solver_3": {
        "original_score": 0.6,
        "refined_score": 0.65,
        "reasoning_quality": "fair",
        "likely_correct": false
      }
    },
    "selection_reasoning": "Solver 2's solution demonstrates...",
    "consensus_analysis": "Solvers disagreed initially, but...",
    "confidence": 0.92
  },
  "timestamp": "2024-01-01 12:00:00"
}
```

## Integration

- **Input**: Requires outputs from Stages 0, 1, 2, and 3
- **Output**: Final result used by `evaluator.py` to calculate system accuracy
- **Called by**: `orchestrator.py` as the final stage of the pipeline

## Standalone Usage

Can be run independently for testing:

```bash
python code/judge.py
```

This will:
1. Load the first problem from the dataset
2. Load existing outputs from Stages 0, 1, 2, and 3
3. Run judgment
4. Save results to `data/raw_outputs/` and `data/results/`

## Key Features

- **Comprehensive Evaluation**: Considers both original and refined solutions
- **Review Integration**: Takes peer feedback into account
- **Detailed Scoring**: Provides scores for multiple dimensions
- **Transparency**: Includes full reasoning for selection
- **Confidence Scoring**: Quantifies judge certainty
- **Token Optimization**: Prompt optimized to reduce API costs

## Token Usage Optimization

The judge stage was optimized to reduce token usage:
- **Reasoning Steps**: Truncated to first 3 and last 2 steps
- **Explanations**: Limited to 200 characters
- **Reviews**: Summarized with counts and 150-char summary

This significantly reduces input tokens while preserving critical information for judgment.
