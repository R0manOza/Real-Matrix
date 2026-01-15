"""Stage 3: Refinement - solvers refine their solutions based on peer feedback."""

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


def refine_solution(problem_text, original_solution, reviews, solver_id):
    """Have a solver refine their solution based on peer reviews.

    Args:
        problem_text: The original problem statement
        original_solution: The solver's original solution
        reviews: List of two review dictionaries from other solvers
        solver_id: ID of the solver (e.g., "solver_1")

    Returns:
        Dictionary with the refined solution
    """
    model_name = original_solution["model_name"]

    # Format reviews for the prompt
    reviews_text = ""
    for i, review in enumerate(reviews, 1):
        reviewer_id = review.get("reviewer_id", f"Reviewer {i}")
        reviews_text += f"\n\nReview from {reviewer_id}:\n"
        reviews_text += f"Strengths: {', '.join(review.get('strengths', []))}\n"
        reviews_text += f"Weaknesses: {', '.join(review.get('weaknesses', []))}\n"
        if review.get('errors'):
            reviews_text += f"Errors: {', '.join(review.get('errors', []))}\n"
        reviews_text += f"Suggestions: {', '.join(review.get('suggestions', []))}\n"
        reviews_text += f"Overall: {review.get('overall_assessment', 'N/A')}\n"
        reviews_text += f"Answer Correctness: {review.get('answer_correctness', 'uncertain')}"

    prompt = f"""You previously solved a problem and received peer reviews. Now you need to refine your solution based on the feedback.

Original Problem:
{problem_text}

Your Original Solution:
Reasoning Steps:
{chr(10).join(original_solution.get('reasoning_steps', []))}
Final Answer: {original_solution.get('final_answer', 'N/A')}
Approach: {original_solution.get('approach', 'N/A')}

Peer Reviews:
{reviews_text}

Your task:
1. Carefully consider each review
2. Decide which critiques are valid and should be addressed
3. Decide which critiques you disagree with and why
4. Produce a refined solution that addresses valid concerns
5. If you believe your original solution was correct, you may keep it but explain why

Respond with a JSON object containing:
{{
  "critiques_accepted": ["Critique 1", "Critique 2", ...],
  "critiques_rejected": ["Critique 1", "Critique 2", ...] (with explanations),
  "refinement_reasoning": "Explanation of how you refined your solution",
  "reasoning_steps": [
    "Step 1: ...",
    "Step 2: ...",
    ...
  ],
  "final_answer": "Your refined final answer",
  "confidence": 0.0-1.0,
  "changed_from_original": true/false,
  "improvement_explanation": "How this version is better (or why you kept the original)"
}}"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert problem solver who can thoughtfully incorporate peer feedback. Be critical but fair in evaluating critiques. Respond in JSON format."
        },
        {"role": "user", "content": prompt}
    ]

    print(f"    Refining solution from {model_name} ({solver_id})...")

    result = call_llm(
        model_name,
        messages,
        temperature=TEMPERATURES["solver"],
        response_format={"type": "json_object"}
    )

    refined_solution = {
        "solver_id": solver_id,
        "model_name": model_name,
        "original_solution": original_solution,
        "critiques_accepted": result.get("critiques_accepted", []),
        "critiques_rejected": result.get("critiques_rejected", []),
        "refinement_reasoning": result.get("refinement_reasoning", ""),
        "reasoning_steps": result.get("reasoning_steps", []),
        "final_answer": result.get("final_answer", ""),
        "confidence": result.get("confidence", 0.0),
        "changed_from_original": result.get("changed_from_original", False),
        "improvement_explanation": result.get("improvement_explanation", ""),
        "raw_response": result
    }

    return refined_solution


def refine_solutions(problem_id, problem_text, solutions, reviews):
    """Main function: Stage 3 solution refinement.

    Args:
        problem_id: Unique identifier for the problem
        problem_text: The problem statement
        solutions: Dictionary from Stage 1 with solver_1, solver_2, solver_3 solutions
        reviews: Dictionary from Stage 2 with all peer reviews

    Returns:
        Dictionary with all refined solutions:
        {
            "solver_1": {...},
            "solver_2": {...},
            "solver_3": {...}
        }
    """

    print(f"Stage 3: Solution refinement for problem {problem_id}")

    refined_solutions = {}
    solver_ids = ["solver_1", "solver_2", "solver_3"]

    for solver_id in solver_ids:
        if solver_id not in solutions:
            raise ValueError(f"Missing {solver_id} in solutions")
        if solver_id not in reviews:
            raise ValueError(f"Missing {solver_id} in reviews")

        # Get the two reviews of this solver's solution
        # Reviews are structured as: reviews[reviewer_id]["review_of_{solver_id}"]
        solver_reviews = []
        for reviewer_id in solver_ids:
            if reviewer_id != solver_id:
                review_key = f"review_of_{solver_id}"
                if review_key in reviews[reviewer_id]:
                    solver_reviews.append(reviews[reviewer_id][review_key])

        if len(solver_reviews) != 2:
            raise ValueError(f"Expected 2 reviews for {solver_id}, got {len(solver_reviews)}")

        refined_solution = refine_solution(
            problem_text,
            solutions[solver_id],
            solver_reviews,
            solver_id
        )
        refined_solutions[solver_id] = refined_solution

        time.sleep(1)  # Rate limiting

    # Save all refined solutions
    output_file = os.path.join(RAW_OUTPUTS_DIR, f"{problem_id}_stage3_refined.json")
    os.makedirs(RAW_OUTPUTS_DIR, exist_ok=True)

    output_data = {
        "problem_id": problem_id,
        "problem_text": problem_text,
        "refined_solutions": refined_solutions,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"  Generated 3 refined solutions")
    print(f"  Refined solutions saved to: {output_file}")

    # Print summary
    for solver_id, refined in refined_solutions.items():
        changed = "CHANGED" if refined.get("changed_from_original", False) else "UNCHANGED"
        answer_preview = refined["final_answer"][:50] + "..." if len(refined["final_answer"]) > 50 else refined[
            "final_answer"]
        print(f"    {solver_id}: {answer_preview} ({changed}, confidence: {refined.get('confidence', 0.0):.2f})")

    return refined_solutions


if __name__ == "__main__":
    # Example usage for testing
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Load Stage 1 solutions and Stage 2 reviews
    from config import PROBLEMS_FILE

    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        problems_data = json.load(f)

    test_problem = problems_data["problems"][0]

    # Load existing solutions
    solutions_file = os.path.join(RAW_OUTPUTS_DIR, f"{test_problem['id']}_stage1_solutions.json")
    reviews_file = os.path.join(RAW_OUTPUTS_DIR, f"{test_problem['id']}_stage2_reviews.json")

    if not os.path.exists(solutions_file):
        print(f"Error: Solutions file not found: {solutions_file}")
        print("Please run Stage 1 first: python code/solver.py")
        sys.exit(1)

    if not os.path.exists(reviews_file):
        print(f"Error: Reviews file not found: {reviews_file}")
        print("Please run Stage 2 first: python code/reviewer.py")
        sys.exit(1)

    with open(solutions_file, 'r', encoding='utf-8') as f:
        solutions_data = json.load(f)

    with open(reviews_file, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)

    try:
        refined = refine_solutions(
            test_problem["id"],
            test_problem["problem_text"],
            solutions_data["solutions"],
            reviews_data["reviews"]
        )

        print("\n[OK] Stage 3 complete! Refined solutions generated successfully.")
        print(f"  Check: {RAW_OUTPUTS_DIR}/{test_problem['id']}_stage3_refined.json")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        print("\nMake sure OPENAI_API_KEY is set in your environment or .env file")
