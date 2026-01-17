"""Stage 4: Final judgment - judge evaluates all solutions and selects the winner."""

import json
import os
import time
from openai import OpenAI
from config import (
    OPENAI_API_KEY, TEMPERATURES, RAW_OUTPUTS_DIR, RESULTS_DIR,
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


def judge_solutions(problem_text, solutions, reviews, refined_solutions, judge_info):
    """Have the judge evaluate all solutions and select the winner.
    
    Args:
        problem_text: The original problem statement
        solutions: Dictionary from Stage 1 with original solutions
        reviews: Dictionary from Stage 2 with all peer reviews
        refined_solutions: Dictionary from Stage 3 with refined solutions
        judge_info: Dictionary with judge's model information from role assignments
    
    Returns:
        Dictionary with the judgment
    """
    model_name = judge_info["model_name"]
    
    # Format all solutions for the prompt
    solutions_text = ""
    solver_ids = ["solver_1", "solver_2", "solver_3"]
    
    for solver_id in solver_ids:
        original = solutions[solver_id]
        refined = refined_solutions[solver_id]
        
        solutions_text += f"\n\n=== {solver_id.upper()} ===\n"
        solutions_text += f"Original Solution:\n"
        solutions_text += f"Reasoning: {chr(10).join(original.get('reasoning_steps', []))}\n"
        solutions_text += f"Answer: {original.get('final_answer', 'N/A')}\n"
        solutions_text += f"Confidence: {original.get('confidence', 0.0)}\n"
        
        solutions_text += f"\nRefined Solution:\n"
        solutions_text += f"Reasoning: {chr(10).join(refined.get('reasoning_steps', []))}\n"
        solutions_text += f"Answer: {refined.get('final_answer', 'N/A')}\n"
        solutions_text += f"Confidence: {refined.get('confidence', 0.0)}\n"
        solutions_text += f"Changed: {refined.get('changed_from_original', False)}\n"
        solutions_text += f"Improvement: {refined.get('improvement_explanation', 'N/A')}\n"
        
        # Add reviews of this solution
        solutions_text += f"\nPeer Reviews:\n"
        for reviewer_id in solver_ids:
            if reviewer_id != solver_id:
                review_key = f"review_of_{solver_id}"
                if review_key in reviews.get(reviewer_id, {}):
                    review = reviews[reviewer_id][review_key]
                    solutions_text += f"  {reviewer_id}: {review.get('overall_assessment', 'N/A')[:100]}...\n"
                    solutions_text += f"    Correctness: {review.get('answer_correctness', 'uncertain')}\n"
    
    prompt = f"""You are the judge in a collaborative problem-solving system. Your task is to evaluate all solutions (original and refined) and select the best final answer.

Original Problem:
{problem_text}

All Solutions and Reviews:
{solutions_text}

Your task:
1. Evaluate the quality and correctness of each solution (both original and refined versions)
2. Consider the peer reviews and how well critiques were addressed
3. Determine which solution is most likely to be correct
4. Select the winning solution and final answer

Respond with a JSON object containing:
{{
  "winner": "solver_1" | "solver_2" | "solver_3",
  "winning_answer": "The final answer you select",
  "evaluation": {{
    "solver_1": {{
      "original_score": 0.0-1.0,
      "refined_score": 0.0-1.0,
      "reasoning_quality": "excellent" | "good" | "fair" | "poor",
      "likely_correct": true/false
    }},
    "solver_2": {{...}},
    "solver_3": {{...}}
  }},
  "selection_reasoning": "Detailed explanation of why you selected this winner",
  "consensus_analysis": "Analysis of whether solvers agreed or disagreed",
  "confidence": 0.0-1.0
}}"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert judge evaluating problem solutions. Be thorough, objective, and decisive. Consider all evidence including peer reviews and refinements. Respond in JSON format."
        },
        {"role": "user", "content": prompt}
    ]

    print(f"    Judge ({model_name}) evaluating all solutions...")
    
    result = call_llm(
        model_name,
        messages,
        temperature=TEMPERATURES["judge"],
        response_format={"type": "json_object"}
    )
    
    judgment = {
        "judge_model": model_name,
        "winner": result.get("winner", ""),
        "winning_answer": result.get("winning_answer", ""),
        "evaluation": result.get("evaluation", {}),
        "selection_reasoning": result.get("selection_reasoning", ""),
        "consensus_analysis": result.get("consensus_analysis", ""),
        "confidence": result.get("confidence", 0.0),
        "raw_response": result
    }
    
    return judgment


def make_judgment(problem_id, problem_text, solutions, reviews, refined_solutions, role_assignments):
    """Main function: Stage 4 final judgment.
    
    Args:
        problem_id: Unique identifier for the problem
        problem_text: The problem statement
        solutions: Dictionary from Stage 1 with original solutions
        reviews: Dictionary from Stage 2 with all peer reviews
        refined_solutions: Dictionary from Stage 3 with refined solutions
        role_assignments: Dictionary from Stage 0 with judge information
    
    Returns:
        Dictionary with the judgment and winning answer
    """
    
    print(f"Stage 4: Final judgment for problem {problem_id}")
    
    if "judge" not in role_assignments:
        raise ValueError("Missing judge in role assignments")
    
    judgment = judge_solutions(
        problem_text,
        solutions,
        reviews,
        refined_solutions,
        role_assignments["judge"]
    )
    
    # Save judgment
    output_file = os.path.join(RAW_OUTPUTS_DIR, f"{problem_id}_stage4_judgment.json")
    os.makedirs(RAW_OUTPUTS_DIR, exist_ok=True)
    
    output_data = {
        "problem_id": problem_id,
        "problem_text": problem_text,
        "judgment": judgment,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Also save to results directory
    os.makedirs(RESULTS_DIR, exist_ok=True)
    results_file = os.path.join(RESULTS_DIR, f"{problem_id}_final_result.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"  Judge selected: {judgment['winner']}")
    print(f"  Winning answer: {judgment['winning_answer']}")
    print(f"  Confidence: {judgment.get('confidence', 0.0):.2f}")
    print(f"  Judgment saved to: {output_file}")
    print(f"  Final result saved to: {results_file}")
    
    return judgment


if __name__ == "__main__":
    # Example usage for testing
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load all previous stages
    from config import PROBLEMS_FILE
    
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        problems_data = json.load(f)
    
    test_problem = problems_data["problems"][0]
    
    # Load existing data from all stages
    solutions_file = os.path.join(RAW_OUTPUTS_DIR, f"{test_problem['id']}_stage1_solutions.json")
    reviews_file = os.path.join(RAW_OUTPUTS_DIR, f"{test_problem['id']}_stage2_reviews.json")
    refined_file = os.path.join(RAW_OUTPUTS_DIR, f"{test_problem['id']}_stage3_refined.json")
    roles_file = os.path.join(RAW_OUTPUTS_DIR, f"{test_problem['id']}_stage0_roles.json")
    
    missing_files = []
    if not os.path.exists(solutions_file):
        missing_files.append("Stage 1 (solver.py)")
    if not os.path.exists(reviews_file):
        missing_files.append("Stage 2 (reviewer.py)")
    if not os.path.exists(refined_file):
        missing_files.append("Stage 3 (refiner.py)")
    if not os.path.exists(roles_file):
        missing_files.append("Stage 0 (role_asigner.py)")
    
    if missing_files:
        print(f"Error: Missing required files. Please run:")
        for stage in missing_files:
            print(f"  - {stage}")
        sys.exit(1)
    
    with open(solutions_file, 'r', encoding='utf-8') as f:
        solutions_data = json.load(f)
    
    with open(reviews_file, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)
    
    with open(refined_file, 'r', encoding='utf-8') as f:
        refined_data = json.load(f)
    
    with open(roles_file, 'r', encoding='utf-8') as f:
        roles_data = json.load(f)
    
    try:
        judgment = make_judgment(
            test_problem["id"],
            test_problem["problem_text"],
            solutions_data["solutions"],
            reviews_data["reviews"],
            refined_data["refined_solutions"],
            roles_data["final_assignments"]
        )
        
        print("\n[OK] Stage 4 complete! Final judgment made.")
        print(f"  Winner: {judgment['winner']}")
        print(f"  Final Answer: {judgment['winning_answer']}")
        print(f"  Check: {RAW_OUTPUTS_DIR}/{test_problem['id']}_stage4_judgment.json")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure OPENAI_API_KEY is set in your environment or .env file")
