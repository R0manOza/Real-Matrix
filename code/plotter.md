# plotter.py Documentation

## Overview

`plotter.py` generates visualizations for the evaluation results of the Multi-LLM Collaborative Debate System. It creates publication-quality plots showing system performance, baseline comparisons, and detailed metrics.

## Purpose

This module provides data visualization capabilities to:
- Compare system performance against baselines
- Show accuracy breakdown by problem category
- Analyze solver consensus patterns
- Visualize refinement impact
- Evaluate judge performance

## Main Functions

### `load_evaluation(filename='evaluation_results.json')`
Loads evaluation results from JSON file.

**Parameters:**
- `filename` (str): Name of evaluation results file

**Returns:**
- Dictionary containing evaluation metrics

**Raises:**
- `FileNotFoundError` if evaluation file doesn't exist

### `plot_system_vs_baselines(evaluation, save_path=None)`
Creates a bar chart comparing system accuracy to baseline methods.

**Parameters:**
- `evaluation` (dict): Evaluation results dictionary
- `save_path` (str, optional): Path to save plot (PNG format)

**Output:**
- Bar chart with:
  - Our System (Full Debate)
  - Majority Vote Baseline
  - Single LLM Baseline
- Accuracy percentages displayed on bars

### `plot_accuracy_by_category(evaluation, save_path=None)`
Shows accuracy broken down by problem category.

**Parameters:**
- `evaluation` (dict): Evaluation results dictionary
- `save_path` (str, optional): Path to save plot

**Output:**
- Bar chart with one bar per category
- Shows accuracy percentage and count (correct/total) for each category

### `plot_consensus_analysis(evaluation, save_path=None)`
Visualizes consensus patterns among solvers.

**Parameters:**
- `evaluation` (dict): Evaluation results dictionary
- `save_path` (str, optional): Path to save plot

**Output:**
- Pie chart showing:
  - Full Consensus (All 3 agree)
  - Partial Consensus (2 agree)
  - No Consensus (All different)
- Includes count annotations

### `plot_refinement_impact(evaluation, save_path=None)`
Shows how refinement affected solutions.

**Parameters:**
- `evaluation` (dict): Evaluation results dictionary
- `save_path` (str, optional): Path to save plot

**Output:**
- Pie chart showing:
  - Improved (refinement made answer correct)
  - Unchanged (no change in correctness)
  - Worsened (refinement made answer incorrect)
- Displays improvement rate

### `plot_judge_performance(evaluation, save_path=None)`
Compares judge accuracy to majority vote when solvers disagreed.

**Parameters:**
- `evaluation` (dict): Evaluation results dictionary
- `save_path` (str, optional): Path to save plot

**Output:**
- Bar chart comparing:
  - Judge Selection accuracy
  - Majority Vote accuracy
- Only includes problems where solvers disagreed
- Shows count (correct/total) for each method

### `generate_all_plots(evaluation=None, output_dir=None)`
Generates all evaluation plots at once.

**Parameters:**
- `evaluation` (dict, optional): Evaluation results. If `None`, loads from file.
- `output_dir` (str, optional): Directory to save plots. Defaults to `RESULTS_DIR`.

**Output Files:**
- `system_vs_baselines.png`
- `accuracy_by_category.png`
- `consensus_analysis.png`
- `refinement_impact.png`
- `judge_performance.png`

## Plot Specifications

### Format
- **Resolution**: 300 DPI
- **Format**: PNG
- **Size**: 10x6 inches (standard plots)
- **Style**: Clean, publication-ready

### Color Scheme
- Success/Positive: `#2ecc71` (green)
- Info/Neutral: `#3498db` (blue), `#95a5a6` (gray)
- Warning: `#f39c12` (orange)
- Error/Negative: `#e74c3c` (red)
- Special: `#9b59b6` (purple for judge)

### Features
- Value labels on bars
- Grid lines for readability
- Bold titles and labels
- Percentage formatting
- Count annotations where relevant

## Dependencies

### Internal
- `config.py`: Results directory path

### External
- `matplotlib`: Plotting library
- `numpy`: Numerical operations

### Standard Library
- `json`: JSON file loading
- `os`: File operations

## Example Usage

### Generate All Plots
```python
from plotter import generate_all_plots

generate_all_plots()
```

### Generate Specific Plot
```python
from plotter import load_evaluation, plot_system_vs_baselines

evaluation = load_evaluation()
plot_system_vs_baselines(evaluation, 'my_plot.png')
```

### Command-Line Usage
```bash
python code/plotter.py
```

Or with custom evaluation file:
```bash
python code/plotter.py --evaluation-file my_evaluation.json
```

## Integration

- **Input**: Requires `evaluator.py` to run first and generate `evaluation_results.json`
- **Output**: Saves PNG files to `data/results/`
- **Called by**: `run_evaluation.py` as part of the evaluation pipeline

## File Locations

### Input
- `data/results/evaluation_results.json`: Default evaluation file

### Output
- `data/results/system_vs_baselines.png`
- `data/results/accuracy_by_category.png`
- `data/results/consensus_analysis.png`
- `data/results/refinement_impact.png`
- `data/results/judge_performance.png`

## Error Handling

- **Missing evaluation file**: Raises `FileNotFoundError` with helpful message
- **Missing category data**: Prints warning and skips category plot
- **No disagreements**: Skips judge performance plot if no solver disagreements

## Key Features

- **Publication Quality**: High-resolution, professional styling
- **Comprehensive**: Covers all major evaluation metrics
- **Flexible**: Can generate individual plots or all at once
- **Informative**: Includes value labels and annotations
- **Consistent**: Uniform styling across all plots
