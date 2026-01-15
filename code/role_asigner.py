"""Stage 0: Role assignment through self-assessment."""

import json
import os
import time
from openai import OpenAI
from config import OPENAI_API_KEY, MODELS, TEMPERATURES, RAW_OUTPUTS_DIR, MAX_RETRIES, RETRY_DELAY

client = OpenAI(api_key=OPENAI_API_KEY)


def call_llm(model, messages, temperature=0.7):
    """Make API call with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            # Try with JSON format first (for models that support it)
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as json_error:
                # Fallback: request JSON in the prompt and parse from text
                if "response_format" in str(json_error).lower():
                    messages_with_json = messages.copy()
                    if messages_with_json[-1]["role"] == "user":
                        messages_with_json[-1]["content"] += "\n\nIMPORTANT: Respond ONLY with valid JSON, no other text."
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages_with_json,
                        temperature=temperature
                    )
                    content = response.choices[0].message.content.strip()
                    # Try to extract JSON if wrapped in markdown code blocks
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    return json.loads(content)
                else:
                    raise json_error
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise e


def self_assess_role(problem_text, model_name, model_id):
    """Have an LLM self-assess which role it prefers."""

    prompt = f"""You are participating in a collaborative problem-solving system. You will be given a problem and asked to assess which role you'd be best suited for.

Problem:
{problem_text}

Available roles:
- Solver: Generate independent solutions with step-by-step reasoning
- Judge: Evaluate multiple solutions and select the best one

Respond with a JSON object containing:
{{
  "role_preferences": ["Solver", "Judge"] (ordered by preference),
  "confidence_by_role": {{
    "Solver": 0.0-1.0,
    "Judge": 0.0-1.0
  }},
  "reasoning": "Brief explanation of why you chose these preferences"
}}"""

    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides self-assessments in JSON format."},
        {"role": "user", "content": prompt}
    ]

    result = call_llm(model_name, messages, temperature=TEMPERATURES["solver"])
    result["model_id"] = model_id
    result["model_name"] = model_name
    return result


def assign_roles_algorithmically(self_assessments):
    """Stage 0.5: Deterministically assign roles based on self-assessments."""

    # Calculate scores for each role
    solver_scores = []
    judge_scores = []

    for i, assessment in enumerate(self_assessments):
        solver_score = assessment["confidence_by_role"].get("Solver", 0.0)
        judge_score = assessment["confidence_by_role"].get("Judge", 0.0)

        # Boost score if it's the preferred role
        if assessment["role_preferences"][0] == "Solver":
            solver_score += 0.1
        if assessment["role_preferences"][0] == "Judge":
            judge_score += 0.1

        solver_scores.append((i, solver_score, assessment))
        judge_scores.append((i, judge_score, assessment))

    # Sort by scores
    solver_scores.sort(key=lambda x: x[1], reverse=True)
    judge_scores.sort(key=lambda x: x[1], reverse=True)

    # Assign top 3 as solvers, top 1 as judge
    solver_indices = [solver_scores[i][0] for i in range(3)]
    judge_index = judge_scores[0][0]

    # If judge is in solver list, swap with next best judge
    if judge_index in solver_indices:
        for idx, score, _ in judge_scores[1:]:
            if idx not in solver_indices:
                judge_index = idx
                break

    assignments = {
        "solver_1": self_assessments[solver_indices[0]],
        "solver_2": self_assessments[solver_indices[1]],
        "solver_3": self_assessments[solver_indices[2]],
        "judge": self_assessments[judge_index]
    }

    return assignments


def assign_roles(problem_id, problem_text):
    """Main function: Stage 0 role assignment.

    Args:
        problem_id: Unique identifier for the problem
        problem_text: The problem statement

    Returns:
        Dictionary with role assignments:
        {
            "solver_1": {...},
            "solver_2": {...},
            "solver_3": {...},
            "judge": {...}
        }
    """

    print(f"Stage 0: Role assignment for problem {problem_id}")

    # Get self-assessments from all 4 models
    self_assessments = []
    model_list = list(MODELS.items())

    for role_key, model_name in model_list:
        print(f"  Getting self-assessment from {model_name} ({role_key})...")
        assessment = self_assess_role(problem_text, model_name, role_key)
        self_assessments.append(assessment)
        time.sleep(1)  # Rate limiting

    # Algorithmically assign roles
    assignments = assign_roles_algorithmically(self_assessments)

    # Save assignments
    output_file = os.path.join(RAW_OUTPUTS_DIR, f"{problem_id}_stage0_roles.json")
    os.makedirs(RAW_OUTPUTS_DIR, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "problem_id": problem_id,
            "self_assessments": self_assessments,
            "final_assignments": assignments
        }, f, indent=2, ensure_ascii=False)

    print(f"  Assigned roles:")
    for role, info in assignments.items():
        print(
            f"    {role}: {info['model_name']} (confidence: {info['confidence_by_role'].get(info['role_preferences'][0], 'N/A')})")

    return assignments


if __name__ == "__main__":
    # Example usage for testing
    test_problem = {
        "id": "test_1",
        "problem_text": "In how many ways can you tile a 3×8 rectangle with 2×1 dominoes?"
    }

    try:
        assignments = assign_roles(test_problem["id"], test_problem["problem_text"])
        print("\nRole assignment complete!")
        print(f"Final assignments saved to: {RAW_OUTPUTS_DIR}/{test_problem['id']}_stage0_roles.json")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure OPENAI_API_KEY is set in your environment or .env file")