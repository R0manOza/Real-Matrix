"""Stage 2: Peer review - each solver reviews the other two solutions."""

import json
import os
import time
from openai import OpenAI
from config import (
    OPENAI_API_KEY, TEMPERATURES, RAW_OUTPUTS_DIR,
    MAX_RETRIES, RETRY_DELAY
)

client = OpenAI(api_key=OPENAI_API_KEY)


def call_llm(model, messages, temperature=0.7, response_format=None):
    """Make API call with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            # Try with JSON format first (for models that support it)
            if response_format and response_format.get("type") == "json_object":
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
                            messages_with_json[-1][
                                "content"] += "\n\nIMPORTANT: Respond ONLY with valid JSON, no other text."

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
            else:
                # Regular text response
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise e


def review_solution(problem_text, reviewer_solution, solution_to_review, reviewer_id, target_solver_id):
    """Have a solver review another solver's solution.

    Args:
        problem_text: The original problem statement
        reviewer_solution: The reviewer's own solution (for context)
        solution_to_review: The solution being reviewed
        reviewer_id: ID of the solver doing the review (e.g., "solver_1")
        target_solver_id: ID of the solver whose solution is being reviewed (e.g., "solver_2")

    Returns:
        Dictionary with the review
    """
    model_name = reviewer_solution["model_name"]

    prompt = f"""You are a problem solver participating in a collaborative system. You have already solved a problem, and now you need to review another solver's solution.

Original Problem:
{problem_text}

Your Solution:
Reasoning Steps:
{chr(10).join(reviewer_solution.get('reasoning_steps', []))}
Final Answer: {reviewer_solution.get('final_answer', 'N/A')}
Approach: {reviewer_solution.get('approach', 'N/A')}

Solution to Review (from {target_solver_id}):
Reasoning Steps:
{chr(10).join(solution_to_review.get('reasoning_steps', []))}
Final Answer: {solution_to_review.get('final_answer', 'N/A')}
Approach: {solution_to_review.get('approach', 'N/A')}

Your task is to provide a thorough, constructive review. Analyze:
1. The correctness of the reasoning
2. Any errors or gaps in the logic
3. The quality of the approach
4. Whether the final answer seems correct
5. Strengths of the solution
6. Suggestions for improvement

Respond with a JSON object containing:
{{
  "strengths": ["Strength 1", "Strength 2", ...],
  "weaknesses": ["Weakness 1", "Weakness 2", ...],
  "errors": ["Error 1", "Error 2", ...] (if any),
  "suggestions": ["Suggestion 1", "Suggestion 2", ...],
  "overall_assessment": "Your overall assessment of this solution",
  "answer_correctness": "correct" | "incorrect" | "uncertain",
  "confidence": 0.0-1.0
}}"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert problem solver providing constructive peer reviews. Be thorough, fair, and specific in your feedback. Respond in JSON format."
        },
        {"role": "user", "content": prompt}
    ]

    print(f"    {reviewer_id} reviewing {target_solver_id}'s solution...")

    result = call_llm(
        model_name,
        messages,
        temperature=TEMPERATURES["reviewer"],
        response_format={"type": "json_object"}
    )

    review = {
        "reviewer_id": reviewer_id,
        "reviewer_model": model_name,
        "target_solver_id": target_solver_id,
        "target_model": solution_to_review.get("model_name", "unknown"),
        "strengths": result.get("strengths", []),
        "weaknesses": result.get("weaknesses", []),
        "errors": result.get("errors", []),
        "suggestions": result.get("suggestions", []),
        "overall_assessment": result.get("overall_assessment", ""),
        "answer_correctness": result.get("answer_correctness", "uncertain"),
        "confidence": result.get("confidence", 0.0),
        "raw_response": result
    }

    return review


def review_solutions(problem_id, problem_text, solutions):
    """Main function: Stage 2 peer review.

    Args:
        problem_id: Unique identifier for the problem
        problem_text: The problem statement
        solutions: Dictionary from Stage 1 with solver_1, solver_2, solver_3 solutions

    Returns:
        Dictionary with all reviews:
        {
            "solver_1": {
                "review_of_solver_2": {...},
                "review_of_solver_3": {...}
            },
            "solver_2": {
                "review_of_solver_1": {...},
                "review_of_solver_3": {...}
            },
            "solver_3": {
                "review_of_solver_1": {...},
                "review_of_solver_2": {...}
            }
        }
    """

    print(f"Stage 2: Peer review for problem {problem_id}")

    reviews = {}

    # Each solver reviews the other two
    solver_ids = ["solver_1", "solver_2", "solver_3"]

    for reviewer_id in solver_ids:
        if reviewer_id not in solutions:
            raise ValueError(f"Missing {reviewer_id} in solutions")

        reviewer_solution = solutions[reviewer_id]
        reviews[reviewer_id] = {}

        # Review the other two solvers
        for target_id in solver_ids:
            if target_id != reviewer_id:
                review = review_solution(
                    problem_text,
                    reviewer_solution,
                    solutions[target_id],
                    reviewer_id,
                    target_id
                )
                reviews[reviewer_id][f"review_of_{target_id}"] = review
                time.sleep(1)  # Rate limiting

    # Save all reviews
    output_file = os.path.join(RAW_OUTPUTS_DIR, f"{problem_id}_stage2_reviews.json")
    os.makedirs(RAW_OUTPUTS_DIR, exist_ok=True)

    output_data = {
        "problem_id": problem_id,
        "problem_text": problem_text,
        "reviews": reviews,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"  Generated 6 peer reviews (each solver reviewed 2 others)")
    print(f"  Reviews saved to: {output_file}")

    # Print summary
    for reviewer_id, review_dict in reviews.items():
        for review_key, review in review_dict.items():
            target = review_key.replace("review_of_", "")
            correctness = review.get("answer_correctness", "uncertain")
            print(f"    {reviewer_id} -> {target}: {correctness} (confidence: {review.get('confidence', 0.0):.2f})")

    return reviews


if __name__ == "__main__":
    # Example usage for testing
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Load Stage 1 solutions
    from config import PROBLEMS_FILE

    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        problems_data = json.load(f)

    test_problem = problems_data["problems"][0]

    # Load existing solutions
    solutions_file = os.path.join(RAW_OUTPUTS_DIR, f"{test_problem['id']}_stage1_solutions.json")

    if not os.path.exists(solutions_file):
        print(f"Error: Solutions file not found: {solutions_file}")
        print("Please run Stage 1 first: python code/solver.py")
        sys.exit(1)

    with open(solutions_file, 'r', encoding='utf-8') as f:
        solutions_data = json.load(f)

    try:
        reviews = review_solutions(
            test_problem["id"],
            test_problem["problem_text"],
            solutions_data["solutions"]
        )

        print("\n[OK] Stage 2 complete! Peer reviews generated successfully.")
        print(f"  Check: {RAW_OUTPUTS_DIR}/{test_problem['id']}_stage2_reviews.json")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        print("\nMake sure OPENAI_API_KEY is set in your environment or .env file")
