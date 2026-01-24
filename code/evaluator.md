# evaluator.py Documentation

## Overview

`evaluator.py` implements **Phase 3** of the Multi-LLM Collaborative Debate System: Evaluation and Analysis. It calculates quantitative metrics to assess system performance, compares against baselines, and generates comprehensive evaluation reports.

## Purpose

This module provides:
- System-level performance metrics (accuracy, consensus, improvement)
- Baseline comparisons (single LLM, majority vote)
- Judge performance analysis
- Category-wise breakdowns
- Answer matching with unit conversion support

## Main Functions

### Answer Matching

#### `normalize_answer(answer, answer_type)`
Normalizes answers for comparison, handling units, formatting, and edge cases.

**Parameters:**
- `answer` (str): Answer string to normalize
- `answer_type` (str): Type of answer (`"integer"`, `"float"`, `"string"`)

**Returns:**
- Normalized answer string (lowercase, whitespace cleaned, units converted)

**Features:**
- Removes currency symbols and prefixes
- Handles unit conversions (mm→m, cm→m, km→m, g→kg, ms→s)
- Normalizes numeric formatting
- Strips trailing zeros

#### `answers_match(answer1, answer2, answer_type)`
Checks if two answers match, with unit conversion support.

**Parameters:**
- `answer1` (str): First answer
- `answer2` (str): Second answer
- `answer_type` (str): Type of answer

**Returns:**
- `True` if answers match (after normalization and unit conversion), `False` otherwise

**Features:**
- Exact string matching after normalization
- Numeric comparison with tolerance (0.001)
- Unit conversion for length, mass, time
- Partial matching for string answers

### Data Loading

#### `load_problems()`
Loads problems with correct answers from dataset.

**Returns:**
- Dictionary mapping problem IDs to problem data

#### `load_results()`
Loads all final results from results directory.

**Returns:**
- Dictionary mapping problem IDs to final result data

#### `load_stage1_solutions()`
Loads all Stage 1 solutions for baseline comparison.

**Returns:**
- Dictionary mapping problem IDs to solution dictionaries

#### `load_stage3_refined()`
Loads all Stage 3 refined solutions.

**Returns:**
- Dictionary mapping problem IDs to refined solution dictionaries

### Metrics Calculation

#### `calculate_system_metrics(problems, results)`
Calculates overall system performance metrics.

**Returns:**
- Dictionary with:
  - `total_problems`: Total problems in dataset
  - `processed_problems`: Number of problems processed
  - `correct_final_answers`: Count of correct answers
  - `overall_accuracy`: Overall accuracy (0.0-1.0)
  - `by_category`: Category-wise breakdown

#### `calculate_improvement_rate(problems, stage1_solutions, refined_solutions)`
Calculates how often refinement improved answers.

**Returns:**
- Dictionary with:
  - `total_with_refinement`: Problems with refinement data
  - `improved`: Count of problems where refinement helped
  - `worsened`: Count where refinement hurt
  - `unchanged`: Count where refinement had no effect
  - `improvement_rate`: Percentage improved

#### `calculate_consensus_rate(problems, stage1_solutions, results=None)`
Calculates consensus patterns among solvers.

**Parameters:**
- `results` (dict, optional): If provided, only counts problems that completed pipeline

**Returns:**
- Dictionary with:
  - `total`: Total problems analyzed
  - `full_consensus`: All 3 solvers agreed
  - `partial_consensus`: 2 solvers agreed
  - `no_consensus`: All 3 disagreed
  - `consensus_rate`: Percentage with full consensus

#### `calculate_judge_accuracy(problems, results, stage1_solutions)`
Evaluates judge performance when solvers disagreed.

**Returns:**
- Dictionary with:
  - `total_disagreements`: Problems where solvers disagreed
  - `judge_correct`: Count of correct judge selections
  - `judge_accuracy`: Judge accuracy (0.0-1.0)
  - `majority_vote_correct`: Count of correct majority votes
  - `majority_vote_accuracy`: Majority vote accuracy (0.0-1.0)

### Baseline Comparisons

#### `run_single_llm_baseline(problems, model_name="gpt-4")`
Runs baseline: ask GPT-4 once per problem.

**Parameters:**
- `problems` (dict): Dictionary of problems
- `model_name` (str): Model to use (default: `"gpt-4"`)

**Returns:**
- Dictionary with:
  - `answers`: Problem ID → answer mapping
  - `correct`: Count of correct answers
  - `total`: Total problems processed
  - `accuracy`: Overall accuracy

**Note:** This makes API calls and may take time.

#### `calculate_majority_vote_baseline(problems, stage1_solutions, results=None)`
Calculates baseline: majority vote of 3 independent solutions.

**Parameters:**
- `results` (dict, optional): If provided, only counts problems that completed pipeline

**Returns:**
- Dictionary with:
  - `answers`: Problem ID → majority answer mapping
  - `correct`: Count of correct answers
  - `total`: Total problems analyzed
  - `accuracy`: Overall accuracy

### Main Evaluation

#### `evaluate_all(include_baselines=True)`
Runs complete evaluation pipeline.

**Parameters:**
- `include_baselines` (bool): Whether to run single-LLM baseline (makes API calls)

**Returns:**
- Dictionary with all metrics:
  ```python
  {
      "system_metrics": {...},
      "improvement_metrics": {...},
      "consensus_metrics": {...},
      "judge_metrics": {...},
      "baselines": {
          "majority_vote": {...},
          "single_llm": {...}  # If include_baselines=True
      }
  }
  ```

#### `save_evaluation(evaluation, filename='evaluation_results.json')`
Saves evaluation results to JSON file.

**Parameters:**
- `evaluation` (dict): Evaluation results dictionary
- `filename` (str): Output filename

## Unit Conversion Support

The evaluator handles unit conversions for numeric answers:
- **Length**: mm → m, cm → m, km → m
- **Mass**: g → kg, mg → kg
- **Time**: ms → s
- **Composite units**: m/s, m/s², rad/s² (kept as-is)

This prevents false negatives when answers are equivalent but use different units (e.g., "30 mm" vs "0.03 m").

## Dependencies

### Internal
- `config.py`: File paths, API key

### External
- `openai`: For single-LLM baseline (optional)

### Standard Library
- `json`: JSON file operations
- `os`: File system operations
- `re`: Regular expressions for answer parsing
- `collections.Counter`: For majority vote calculation
- `typing`: Type hints

## Example Usage

### Run Full Evaluation
```python
from evaluator import evaluate_all, save_evaluation

evaluation = evaluate_all(include_baselines=True)
save_evaluation(evaluation)
```

### Skip Single-LLM Baseline (Saves API Calls)
```python
evaluation = evaluate_all(include_baselines=False)
```

### Command-Line Usage
```bash
python code/evaluator.py
```

Skip baselines:
```bash
python code/evaluator.py --skip-baselines
```

## Output Format

The evaluation JSON includes:
- **System Metrics**: Overall accuracy, category breakdowns
- **Improvement Metrics**: Refinement impact statistics
- **Consensus Metrics**: Agreement patterns
- **Judge Metrics**: Judge vs. majority vote performance
- **Baselines**: Comparison to simpler methods

## Integration

- **Input**: Reads from `data/problems.json`, `data/results/`, `data/raw_outputs/`
- **Output**: Saves to `data/results/evaluation_results.json`
- **Used by**: `plotter.py` to generate visualizations
- **Called by**: `run_evaluation.py` as part of evaluation pipeline

## Key Features

- **Robust Answer Matching**: Handles unit conversions, formatting variations
- **Comprehensive Metrics**: Covers all aspects of system performance
- **Baseline Comparisons**: Quantifies improvement over simple methods
- **Category Analysis**: Breaks down performance by problem type
- **Consistency**: Only counts problems that completed full pipeline

## Important Notes

1. **Unit Conversion**: The evaluator was enhanced to handle unit conversions, significantly improving accuracy detection (e.g., from 20% to 40% in one case).

2. **Pipeline Completion**: Metrics only count problems that completed the full pipeline (have a `_final_result.json` file), ensuring consistency.

3. **API Calls**: The single-LLM baseline makes API calls. Use `--skip-baselines` to avoid this if you only want to analyze existing results.

4. **Answer Types**: Supports `integer`, `float`, and `string` answer types with appropriate matching logic for each.
