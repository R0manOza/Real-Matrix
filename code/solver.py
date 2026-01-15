"""Stage 1: Independent solution generation by each solver."""

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


def generate_solution(problem_text, solver_info, solver_id):
    """Have a solver generate an independent solution with step-by-step reasoning.
    
    Args:
        problem_text: The problem statement
        solver_info: Dictionary with solver's model info from role assignments
        solver_id: Identifier like "solver_1", "solver_2", "solver_3"
    
    Returns:
        Dictionary with the solution and metadata
    """
    model_name = solver_info["model_name"]
    model_id = solver_info.get("model_id", solver_id)
    
    prompt = f"""You are a problem solver in a collaborative system. Your task is to solve the following problem independently, showing all your reasoning step-by-step.

Problem:
{problem_text}

Instructions:
1. Read the problem carefully and understand what is being asked
2. Show your reasoning step-by-step
3. Work through the solution methodically
4. Provide a clear final answer
5. Explain how you arrived at your answer

Respond with a JSON object containing:
{{
  "reasoning_steps": [
    "Step 1: ...",
    "Step 2: ...",
    ...
  ],
  "final_answer": "Your final answer here",
  "confidence": 0.0-1.0,
  "approach": "Brief description of your solution approach"
}}"""

    messages = [
        {
            "role": "system", 
            "content": "You are an expert problem solver. Provide detailed step-by-step reasoning and a clear final answer in JSON format."
        },
        {"role": "user", "content": prompt}
    ]

    print(f"    Generating solution from {model_name} ({solver_id})...")
    
    result = call_llm(
        model_name, 
        messages, 
        temperature=TEMPERATURES["solver"],
        response_format={"type": "json_object"}
    )
    
    # Add metadata
    solution = {
        "solver_id": solver_id,
        "model_name": model_name,
        "model_id": model_id,
        "problem_text": problem_text,
        "reasoning_steps": result.get("reasoning_steps", []),
        "final_answer": result.get("final_answer", ""),
        "confidence": result.get("confidence", 0.0),
        "approach": result.get("approach", ""),
        "raw_response": result
    }
    
    return solution


def solve_problem(problem_id, problem_text, role_assignments):
    """Main function: Stage 1 solution generation.
    
    Args:
        problem_id: Unique identifier for the problem
        problem_text: The problem statement
        role_assignments: Dictionary from Stage 0 with solver_1, solver_2, solver_3, judge
    
    Returns:
        Dictionary with all three solutions:
        {
            "solver_1": {...},
            "solver_2": {...},
            "solver_3": {...}
        }
    """
    
    print(f"Stage 1: Solution generation for problem {problem_id}")
    
    solutions = {}
    
    # Generate solution from each of the 3 solvers
    for solver_id in ["solver_1", "solver_2", "solver_3"]:
        if solver_id not in role_assignments:
            raise ValueError(f"Missing {solver_id} in role assignments")
        
        solver_info = role_assignments[solver_id]
        solution = generate_solution(problem_text, solver_info, solver_id)
        solutions[solver_id] = solution
        
        time.sleep(1)  # Rate limiting between API calls
    
    # Save all solutions
    output_file = os.path.join(RAW_OUTPUTS_DIR, f"{problem_id}_stage1_solutions.json")
    os.makedirs(RAW_OUTPUTS_DIR, exist_ok=True)
    
    output_data = {
        "problem_id": problem_id,
        "problem_text": problem_text,
        "solutions": solutions,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"  Generated 3 independent solutions")
    print(f"  Solutions saved to: {output_file}")
    
    # Print summary
    for solver_id, solution in solutions.items():
        answer_preview = solution["final_answer"][:50] + "..." if len(solution["final_answer"]) > 50 else solution["final_answer"]
        print(f"    {solver_id}: {answer_preview} (confidence: {solution['confidence']:.2f})")
    
    return solutions


if __name__ == "__main__":
    # Example usage for testing
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load a test problem
    from config import PROBLEMS_FILE
    
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        problems_data = json.load(f)
    
    test_problem = problems_data["problems"][0]
    
    # Create mock role assignments (in real usage, this comes from Stage 0)
    from role_asigner import assign_roles
    
    try:
        print("First running Stage 0 to get role assignments...")
        role_assignments = assign_roles(test_problem["id"], test_problem["problem_text"])
        
        print("\n" + "="*60)
        print("Now running Stage 1 to generate solutions...")
        print("="*60 + "\n")
        
        solutions = solve_problem(
            test_problem["id"], 
            test_problem["problem_text"], 
            role_assignments
        )
        
        print("\n[OK] Stage 1 complete! Solutions generated successfully.")
        print(f"  Check: {RAW_OUTPUTS_DIR}/{test_problem['id']}_stage1_solutions.json")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure OPENAI_API_KEY is set in your environment or .env file")
