# TODO List

## Phase 1: Problem Dataset

- [ ] Come up with 7 math/logic problems that are actually hard
- [ ] Write 6 physics problems that need real formula work
- [ ] Create 6 logic puzzles with constraints (like the fish puzzle)
- [ ] Make 6 game theory problems about strategies
- [ ] Put all 25 problems into a JSON file with correct answers
- [ ] Test that each problem has a clear right answer we can check

## Phase 2: Core System

### Setup
- [ ] Set up config file for API keys and model settings
- [ ] Add OpenAI library to requirements
- [ ] Write basic error handling for API calls

### Stage 0: Role Assignment
- [ ] Make the 4 LLMs self-assess which role they want
- [ ] Write the algorithm that picks who gets which role
- [ ] Save role assignments somewhere

### Stage 1: Solvers
- [ ] Get each of the 3 solvers to generate their own solution
- [ ] Make sure they show step-by-step reasoning
- [ ] Save all three solutions with metadata

### Stage 2: Reviews
- [ ] Have each solver review the other two solutions
- [ ] Structure the reviews (strengths, weaknesses, errors, suggestions)
- [ ] Save all the peer reviews

### Stage 3: Refinement
- [ ] Give each solver their 2 reviews
- [ ] Make them decide which critiques to accept/reject
- [ ] Have them produce refined solutions
- [ ] Save the refined versions

### Stage 4: Judge
- [ ] Give judge all original solutions, reviews, and refined solutions
- [ ] Have judge pick the winner
- [ ] Return the winning answer

### Orchestration
- [ ] Wire everything together so it runs end-to-end
- [ ] Make sure intermediate outputs get saved
- [ ] Add logging so we can debug when things break

## Phase 3: Evaluation

- [ ] Calculate how many problems we got right overall
- [ ] Figure out how often refinement actually improved answers
- [ ] Check consensus rate (when all 3 solvers agreed)
- [ ] Measure judge accuracy when solvers disagreed
- [ ] Run baseline: just ask GPT-4 once per problem
- [ ] Run baseline: majority vote of 3 independent solutions
- [ ] Compare our system vs baselines
- [ ] Make plots showing all the results
- [ ] Save plots to results folder

## Polish

- [ ] Write README with setup instructions
- [ ] Test the whole pipeline on a few problems
- [ ] Make sure error handling works when API fails
- [ ] Clean up any messy code
- [ ] Double check all outputs are being saved properly

