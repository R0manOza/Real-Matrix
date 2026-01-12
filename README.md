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

Run the main script:
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

## Notes

- All intermediate outputs are saved to `data/raw_outputs/` for debugging
- Results and plots are saved to `data/results/`
- Make sure you have API credits available - this makes many API calls per problem

