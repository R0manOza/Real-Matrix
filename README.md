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

### Running the Full Pipeline

Run the main script (when implemented):

```bash
python code/main.py
```

This will:

- Load problems from `data/problems.json`
- Run the full debate workflow for each problem
- Generate evaluation metrics
- Create plots in `data/results/`

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

After running Stage 1, you can view the generated solutions:

```bash
# View the solutions file (example for first problem)
cat data/raw_outputs/math_001_stage1_solutions.json
```

Or open the JSON file in any text editor. Each solution contains:

- `reasoning_steps`: Array of step-by-step reasoning
- `final_answer`: The solver's final answer
- `confidence`: Confidence score (0.0-1.0)
- `approach`: Description of the solution method
- `model_name`: Which model generated the solution

## Notes

- All intermediate outputs are saved to `data/raw_outputs/` for debugging
- Results and plots are saved to `data/results/`
- Make sure you have API credits available - this makes many API calls per problem
- The solver module automatically handles models that don't support JSON response format
