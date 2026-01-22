# Multi-LLM Collaborative Debate System

A system where three LLMs solve problems independently, cross-evaluate each other's solutions, refine based on peer feedback, and a fourth LLM judge selects the best final answer.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file with:

```
OPENAI_API_KEY=your-api-key-here
```

3. Make sure you have the data folder structure:

```
data/
├── problems.json
├── raw_outputs/
└── results/
```

## Running the System

### Running Individual Stages

#### Stage 0: Role Assignment

Assign roles to the 4 LLMs (3 Solvers, 1 Judge):

```bash
python code/role_asigner.py
```

This will run role assignment on the first problem in the dataset and save results to `data/raw_outputs/{problem_id}_stage0_roles.json`.

#### Stage 1: Solution Generation (Solvers)

Generate independent solutions from all 3 solvers:

```bash
python code/solver.py
```

This will:

- First run Stage 0 to get role assignments
- Then have each of the 3 solvers generate their own solution with step-by-step reasoning
- Save all solutions to `data/raw_outputs/{problem_id}_stage1_solutions.json`

Each solution includes:

- Step-by-step reasoning
- Final answer
- Confidence score
- Solution approach

#### Stage 2: Peer Review

Have each solver review the other two solutions:

```bash
python code/reviewer.py
```

**Prerequisites:** Stage 1 must be completed first.

This will:

- Have each of the 3 solvers review the other two solutions
- Generate structured reviews with strengths, weaknesses, errors, and suggestions
- Save all 6 peer reviews to `data/raw_outputs/{problem_id}_stage2_reviews.json`

Each review includes:

- `strengths`: List of what the solution does well
- `weaknesses`: Areas that need improvement
- `errors`: Any errors found in the reasoning or answer
- `suggestions`: Constructive suggestions for improvement
- `overall_assessment`: Summary of the review
- `answer_correctness`: Assessment of whether the answer is correct/incorrect/uncertain

#### Stage 3: Solution Refinement

Have solvers refine their solutions based on peer feedback:

```bash
python code/refiner.py
```

**Prerequisites:** Stages 1 and 2 must be completed first.

This will:

- Give each solver their 2 peer reviews
- Have them decide which critiques to accept or reject
- Generate refined solutions that address valid concerns
- Save all refined solutions to `data/raw_outputs/{problem_id}_stage3_refined.json`

Each refined solution includes:

- `critiques_accepted`: Which peer feedback was incorporated
- `critiques_rejected`: Which feedback was rejected (with explanations)
- `refinement_reasoning`: How the solution was refined
- `reasoning_steps`: Updated step-by-step reasoning
- `final_answer`: Refined final answer
- `changed_from_original`: Whether the solution changed
- `improvement_explanation`: How this version is better

#### Stage 4: Final Judgment

Have the judge evaluate all solutions and select the winner:

```bash
python code/judge.py
```

**Prerequisites:** Stages 0, 1, 2, and 3 must be completed first.

This will:

- Give the judge all original solutions, peer reviews, and refined solutions
- Have the judge evaluate and compare all solutions
- Select the winning solution and final answer
- Save judgment to `data/raw_outputs/{problem_id}_stage4_judgment.json`
- Save final result to `data/results/{problem_id}_final_result.json`

The judgment includes:

- `winner`: Which solver's solution won (solver_1, solver_2, or solver_3)
- `winning_answer`: The final answer selected
- `evaluation`: Detailed scores for each solver's original and refined solutions
- `selection_reasoning`: Why this solution was selected
- `consensus_analysis`: Analysis of agreement/disagreement among solvers
- `confidence`: Judge's confidence in the selection

### Running the Full Pipeline

Run the complete end-to-end pipeline using the orchestrator:

```bash
# Run first problem as a test
python code/main.py

# Run a specific problem by ID
python code/main.py --problem-id math_001

# Run all problems in the dataset
python code/main.py --all

# Run all problems starting from a specific index (for resuming)
python code/main.py --all --start-from 5

# Run a limited number of problems
python code/main.py --all --max-problems 10

# Skip certain stages (useful for testing or resuming)
python code/main.py --skip-stages "0,1"  # Skip stages 0 and 1
```

The orchestrator will:

- Load problems from `data/problems.json`
- Run all stages in sequence (0 → 1 → 2 → 3 → 4) for each problem
- Save all intermediate outputs automatically
- Log progress to `data/raw_outputs/orchestrator.log`
- Save progress after each problem to `data/results/progress.json`
- Generate final summary in `data/results/summary.json`
- Handle errors gracefully and continue with remaining problems

**Features:**

- Automatic stage dependency handling (loads previous stages if skipped)
- Comprehensive logging for debugging
- Progress tracking and resume capability
- Error recovery (continues with next problem if one fails)

## Project Structure

```
Real-Matrix/
├── data/
│   ├── problems.json              # Problem dataset
│   ├── raw_outputs/               # Intermediate stage outputs
│   └── results/                   # Final results and plots
├── code/
│   ├── config.py                  # Configuration
│   ├── dataset_builder.py         # Problem dataset creation
│   ├── role_assigner.py           # Stage 0: Role assignment
│   ├── solver.py                  # Stage 1: Solution generation
│   ├── reviewer.py                # Stage 2: Peer review
│   ├── refiner.py                 # Stage 3: Refinement
│   ├── judge.py                   # Stage 4: Final judgment
│   ├── orchestrator.py            # Workflow coordinator
│   ├── evaluator.py               # Metrics calculation
│   ├── plotter.py                 # Plot generation
│   └── main.py                    # Entry point
├── requirements.txt
└── README.md
```

## Workflow

1. **Stage 0**: 4 LLMs self-assess and roles are assigned (3 Solvers, 1 Judge)
2. **Stage 1**: 3 Solvers independently generate solutions
3. **Stage 2**: Each Solver reviews the other two solutions
4. **Stage 3**: Solvers refine their solutions based on peer feedback
5. **Stage 4**: Judge evaluates all solutions and selects the winner

## Viewing Results

After running each stage, you can view the outputs:

```bash
# Stage 0: Role assignments
cat data/raw_outputs/math_001_stage0_roles.json

# Stage 1: Solutions
cat data/raw_outputs/math_001_stage1_solutions.json

# Stage 2: Peer reviews
cat data/raw_outputs/math_001_stage2_reviews.json

# Stage 3: Refined solutions
cat data/raw_outputs/math_001_stage3_refined.json

# Stage 4: Final judgment
cat data/raw_outputs/math_001_stage4_judgment.json
cat data/results/math_001_final_result.json
```

Or open the JSON files in any text editor. Each stage's output contains:

**Stage 1 (Solutions):**

- `reasoning_steps`: Array of step-by-step reasoning
- `final_answer`: The solver's final answer
- `confidence`: Confidence score (0.0-1.0)
- `approach`: Description of the solution method
- `model_name`: Which model generated the solution

**Stage 2 (Reviews):**

- `strengths`, `weaknesses`, `errors`, `suggestions`: Structured feedback
- `overall_assessment`: Summary evaluation
- `answer_correctness`: Assessment of correctness

**Stage 3 (Refined Solutions):**

- `critiques_accepted/rejected`: What feedback was incorporated
- `refinement_reasoning`: How the solution was improved
- `changed_from_original`: Whether changes were made
- Updated `reasoning_steps` and `final_answer`

**Stage 4 (Judgment):**

- `winner`: Winning solver ID
- `winning_answer`: Final selected answer
- `evaluation`: Scores for all solutions
- `selection_reasoning`: Why this solution won

## Stage Dependencies

The stages must be run in order:

1. **Stage 0** → Role Assignment (can run independently)
2. **Stage 1** → Solutions (requires Stage 0, or runs it automatically)
3. **Stage 2** → Reviews (requires Stage 1)
4. **Stage 3** → Refinement (requires Stages 1 & 2)
5. **Stage 4** → Judgment (requires Stages 0, 1, 2, & 3)

Each stage checks for required previous stages and will show an error if dependencies are missing.

## Phase 3: Evaluation and Analysis

After running the full pipeline on problems, you can evaluate system performance:

### Running Evaluation

```bash
# Run complete evaluation (includes baselines and plots)
python code/run_evaluation.py

# Skip single-LLM baseline to save API calls
python code/run_evaluation.py --skip-baselines

# Only run evaluation, skip plots
python code/run_evaluation.py --evaluation-only
```

Or run components separately:

```bash
# Run evaluation only
python code/evaluator.py

# Skip single-LLM baseline
python code/evaluator.py --skip-baselines

# Generate plots from existing evaluation
python code/plotter.py
```

### Evaluation Metrics

The evaluation calculates:

**System-Level Performance:**
- **Overall Accuracy**: % of problems solved correctly by final answer
- **Improvement Rate**: % of problems where refinement improved initial answers
- **Consensus Rate**: % of problems where all 3 Solvers reached same answer
- **Judge Accuracy**: When Solvers disagree, does Judge pick the correct one?

**Baseline Comparisons:**
- **Single-LLM Baseline**: Accuracy of "just ask GPT-4 once"
- **Majority Vote Baseline**: 3 independent solutions, pick majority answer
- **Your System**: Full debate with refinement

**Outputs:**
- `data/results/evaluation_results.json` - Complete evaluation data
- `data/results/system_vs_baselines.png` - Comparison chart
- `data/results/accuracy_by_category.png` - Performance by problem type
- `data/results/consensus_analysis.png` - Consensus breakdown
- `data/results/refinement_impact.png` - Refinement effectiveness
- `data/results/judge_performance.png` - Judge vs majority vote

## Notes
- if it is needed and we didn't provide it , pls tell us if we should have given you acess to the api key 
- All intermediate outputs are saved to `data/raw_outputs/` for debugging
- Final results are saved to `data/results/`
- Make sure you have API credits available - this makes many API calls per problem:
  - Stage 0: 4 API calls (role assessments)
  - Stage 1: 3 API calls (solutions)
  - Stage 2: 6 API calls (peer reviews)
  - Stage 3: 3 API calls (refinements)
  - Stage 4: 1 API call (judgment)
  - **Total: ~17 API calls per problem**
- All modules automatically handle models that don't support JSON response format
- You can run stages separately to inspect intermediate results before proceeding
## Side note : RUNNING THIS WAS TOO RICH FOR MY BLOOD ... WE STILL DID IT THO 
