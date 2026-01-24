# main.py Documentation

## Overview

`main.py` is the main entry point for the Multi-LLM Collaborative Debate System. It provides a command-line interface for running the full pipeline on individual problems or batches of problems.

## Purpose

This module orchestrates the execution of the debate system through a user-friendly CLI, allowing users to:
- Run the full pipeline on a specific problem
- Process all problems in the dataset
- Resume processing from a specific index
- Skip specific stages for debugging or resuming interrupted runs

## Command-Line Arguments

### `--problem-id <id>`
Process a specific problem by its ID (e.g., `math_001`, `physics_002`).

**Example:**
```bash
python code/main.py --problem-id math_001
```

### `--all`
Process all problems in the dataset sequentially.

**Example:**
```bash
python code/main.py --all
```

### `--start-from <index>`
Start processing from a specific problem index (0-based). Useful for resuming interrupted batch runs.

**Example:**
```bash
python code/main.py --all --start-from 5
```

### `--max-problems <count>`
Limit the number of problems to process. Useful for testing on a subset.

**Example:**
```bash
python code/main.py --all --max-problems 10
```

### `--skip-stages <stages>`
Skip specific stages (comma-separated). Stages are numbered 0-4:
- `0`: Role Assignment
- `1`: Solution Generation
- `2`: Peer Review
- `3`: Solution Refinement
- `4`: Final Judgment

**Example:**
```bash
python code/main.py --problem-id math_001 --skip-stages 0,1
```

This will load existing Stage 0 and Stage 1 outputs and continue from Stage 2.

## Default Behavior

If no arguments are provided, `main.py` runs the first problem in the dataset as a test.

## Output

The script logs progress to both:
- Console (stdout)
- Log file: `data/raw_outputs/orchestrator.log`

For each problem, it displays:
- Problem ID and preview
- Stage completion status
- Final winner and answer
- Any errors encountered

## Error Handling

- **Missing problem**: Exits with error code 1 if specified problem ID not found
- **Keyboard interrupt**: Gracefully handles Ctrl+C, exits with code 130
- **Fatal errors**: Logs full traceback and exits with code 1

## Dependencies

- `orchestrator.py`: Core pipeline execution
- `config.py`: Configuration and paths
- Python standard library: `argparse`, `sys`, `os`, `logging`

## Example Usage Scenarios

### Scenario 1: Test on Single Problem
```bash
python code/main.py --problem-id math_001
```

### Scenario 2: Process All Problems
```bash
python code/main.py --all
```

### Scenario 3: Resume from Problem 10
```bash
python code/main.py --all --start-from 10
```

### Scenario 4: Process First 5 Problems
```bash
python code/main.py --all --max-problems 5
```

### Scenario 5: Skip Early Stages (Resume)
```bash
python code/main.py --problem-id math_001 --skip-stages 0,1,2
```

## Integration

This module serves as the primary user interface for the system. It delegates actual execution to `orchestrator.py`, which coordinates all stages of the debate pipeline.
