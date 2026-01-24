# orchestrator.py Documentation

## Overview

`orchestrator.py` is the core coordination module that executes the complete Multi-LLM Collaborative Debate System pipeline. It manages the sequential execution of all five stages, handles dependencies, saves intermediate outputs, and tracks progress.

## Purpose

The orchestrator:
- Coordinates execution of all debate stages (0-4)
- Manages file I/O for intermediate and final results
- Handles stage dependencies and skipping
- Provides logging and progress tracking
- Saves progress checkpoints for batch processing

## Main Functions

### `load_problems()`
Loads all problems from the dataset file (`data/problems.json`).

**Returns:**
- List of problem dictionaries

**Raises:**
- `FileNotFoundError` if problems file doesn't exist

### `run_full_pipeline(problem, skip_stages=None)`
Executes the complete debate pipeline for a single problem.

**Parameters:**
- `problem` (dict): Problem dictionary with `id`, `problem_text`, etc.
- `skip_stages` (list, optional): List of stage numbers to skip (e.g., `[0, 1]`)

**Returns:**
- Dictionary containing:
  - `problem_id`: Problem identifier
  - `problem_text`: Original problem statement
  - `stages_completed`: List of completed stage numbers
  - `errors`: List of errors encountered
  - `start_time` / `end_time`: ISO format timestamps
  - `success`: Boolean indicating overall success
  - Stage-specific outputs (e.g., `stage0_roles`, `stage1_solutions`, etc.)
  - `winning_answer`: Final selected answer
  - `winner`: ID of winning solver

**Stage Execution:**
1. **Stage 0**: Role Assignment (`role_asigner.py`)
2. **Stage 1**: Solution Generation (`solver.py`)
3. **Stage 2**: Peer Review (`reviewer.py`)
4. **Stage 3**: Solution Refinement (`refiner.py`)
5. **Stage 4**: Final Judgment (`judge.py`)

**Stage Skipping:**
If a stage is skipped, the orchestrator attempts to load its output from the corresponding file in `data/raw_outputs/`. If the file doesn't exist, it raises a `FileNotFoundError`.

### `run_all_problems(problems=None, start_from=0, max_problems=None)`
Runs the full pipeline on multiple problems.

**Parameters:**
- `problems` (list, optional): List of problem dictionaries. If `None`, loads from file.
- `start_from` (int): Index to start from (for resuming)
- `max_problems` (int, optional): Maximum number of problems to process

**Returns:**
- List of result dictionaries (one per problem)

**Progress Tracking:**
- Saves progress after each problem to `data/results/progress.json`
- Saves final summary to `data/results/summary.json`
- Handles `KeyboardInterrupt` gracefully

## File Structure

### Input Files
- `data/problems.json`: Problem dataset

### Output Files (per problem)
- `data/raw_outputs/{problem_id}_stage0_roles.json`: Role assignments
- `data/raw_outputs/{problem_id}_stage1_solutions.json`: Initial solutions
- `data/raw_outputs/{problem_id}_stage2_reviews.json`: Peer reviews
- `data/raw_outputs/{problem_id}_stage3_refined.json`: Refined solutions
- `data/raw_outputs/{problem_id}_stage4_judgment.json`: Final judgment
- `data/results/{problem_id}_final_result.json`: Final result (copy of stage4)

### Batch Processing Files
- `data/results/progress.json`: Progress checkpoint
- `data/results/summary.json`: Final batch summary
- `data/raw_outputs/orchestrator.log`: Log file

## Error Handling

- **Stage failures**: Errors are logged and added to the `errors` list
- **Missing files**: Raises `FileNotFoundError` when skipping stages with missing outputs
- **Fatal errors**: Catches exceptions, logs them, and marks result as unsuccessful
- **Keyboard interrupt**: Handled gracefully in batch processing

## Logging

Logs are written to:
- Console (INFO level)
- `data/raw_outputs/orchestrator.log` (INFO level)

Log format: `%(asctime)s - %(levelname)s - %(message)s`

## Dependencies

### Internal Modules
- `role_asigner.py`: Stage 0
- `solver.py`: Stage 1
- `reviewer.py`: Stage 2
- `refiner.py`: Stage 3
- `judge.py`: Stage 4

### Configuration
- `config.py`: File paths, directories

### Standard Library
- `json`: JSON serialization
- `os`: File operations
- `time`: Timestamps
- `logging`: Logging infrastructure
- `datetime`: Timestamp generation

## Example Usage

### Direct Usage (from Python)
```python
from orchestrator import run_full_pipeline, load_problems

problems = load_problems()
result = run_full_pipeline(problems[0])
print(f"Winner: {result['winner']}")
print(f"Answer: {result['winning_answer']}")
```

### Batch Processing
```python
from orchestrator import run_all_problems

results = run_all_problems(start_from=0, max_problems=10)
successful = sum(1 for r in results if r.get("success", False))
print(f"Processed {successful}/{len(results)} successfully")
```

## Integration

This module is the central coordinator called by `main.py`. It imports and orchestrates all stage modules, ensuring proper sequencing and data flow between stages.
