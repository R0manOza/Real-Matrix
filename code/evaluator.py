"""Phase 3: Evaluation and Analysis - Calculate metrics and compare to baselines."""

import json
import os
import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
from config import PROBLEMS_FILE, RESULTS_DIR, RAW_OUTPUTS_DIR


def normalize_answer(answer: str, answer_type: str) -> str:
    """Normalize answer for comparison (remove whitespace, currency symbols, handle units, etc.)."""
    if not answer:
        return ""
    
    answer = str(answer).strip()
    
    # Remove currency symbols and common prefixes
    answer = re.sub(r'^\$', '', answer)
    answer = re.sub(r'^USD\s*', '', answer, flags=re.IGNORECASE)
    
    # Remove common suffixes
    answer = re.sub(r'\s*(dollars?|USD|units?)$', '', answer, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    answer = ' '.join(answer.split())
    
    # For integers/floats, handle unit conversions and remove trailing zeros
    if answer_type in ['integer', 'float']:
        # Try to extract number and unit
        unit_match = re.search(r'([\d.]+)\s*(mm|cm|m|km|kg|g|mg|s|ms|rad/s\^?2?|m/s\^?2?|m/s|N|J|W|Hz|°|degrees?)?', answer, re.IGNORECASE)
        if unit_match:
            num_str = unit_match.group(1)
            unit = unit_match.group(2) if unit_match.group(2) else None
            
            try:
                num = float(num_str)
                
                # Convert units to base SI units (meters for length, etc.)
                if unit:
                    unit_lower = unit.lower()
                    # Length conversions (to meters)
                    if unit_lower in ['km']:
                        num = num * 1000
                    elif unit_lower in ['cm']:
                        num = num / 100
                    elif unit_lower in ['mm']:
                        num = num / 1000
                    # Mass conversions (to kg) - not used in our problems but good to have
                    elif unit_lower in ['g']:
                        num = num / 1000
                    elif unit_lower in ['mg']:
                        num = num / 1000000
                    # Time conversions (to seconds)
                    elif unit_lower in ['ms']:
                        num = num / 1000
                    # For angular velocity (rad/s^2), keep as is
                    # For velocity (m/s), keep as is
                    # For acceleration (m/s^2), keep as is
                
                # Format number
                if num == int(num):
                    answer = str(int(num))
                else:
                    # Round to reasonable precision
                    answer = f"{num:.6f}".rstrip('0').rstrip('.')
            except ValueError:
                pass  # Keep as is if not a number
        else:
            # No unit, just try to parse as number
            try:
                if '.' in answer:
                    num = float(answer)
                    if num == int(num):
                        answer = str(int(num))
                    else:
                        answer = f"{num:.6f}".rstrip('0').rstrip('.')
                else:
                    num = int(answer)
                    answer = str(num)
            except ValueError:
                pass  # Keep as is if not a number
    
    return answer.lower()


def extract_number_and_unit(answer: str) -> tuple:
    """Extract numeric value and unit from answer string."""
    # Try to match number with optional unit
    match = re.search(r'([\d.]+)\s*(mm|cm|m|km|kg|g|mg|s|ms|rad/s\^?2?|m/s\^?2?|m/s|N|J|W|Hz|°|degrees?|cm|mm)?', answer, re.IGNORECASE)
    if match:
        try:
            num = float(match.group(1))
            unit = match.group(2).lower() if match.group(2) else None
            return num, unit
        except (ValueError, AttributeError):
            pass
    
    # Try to parse as plain number
    try:
        num = float(answer.strip())
        return num, None
    except ValueError:
        return None, None


def convert_to_base_unit(value: float, unit: str) -> float:
    """Convert value to base SI unit."""
    if not unit:
        return value
    
    unit = unit.lower()
    
    # Length conversions (to meters)
    if unit in ['km']:
        return value * 1000
    elif unit in ['cm']:
        return value / 100
    elif unit in ['mm']:
        return value / 1000
    # Mass conversions (to kg)
    elif unit in ['g']:
        return value / 1000
    elif unit in ['mg']:
        return value / 1000000
    # Time conversions (to seconds)
    elif unit in ['ms']:
        return value / 1000
    # For composite units (m/s, m/s^2, rad/s^2), return as is
    # These need special handling - for now, don't convert
    else:
        return value


def answers_match(answer1: str, answer2: str, answer_type: str) -> bool:
    """Check if two answers match (with normalization and unit conversion)."""
    norm1 = normalize_answer(answer1, answer_type)
    norm2 = normalize_answer(answer2, answer_type)
    
    # Exact match after normalization
    if norm1 == norm2:
        return True
    
    # For numeric answers, try numeric comparison with unit conversion
    if answer_type in ['integer', 'float']:
        # Extract numbers and units
        num1, unit1 = extract_number_and_unit(answer1)
        num2, unit2 = extract_number_and_unit(answer2)
        
        if num1 is not None and num2 is not None:
            # Try direct comparison first
            if abs(num1 - num2) < 0.001:
                return True
            
            # Try unit conversion if units are present
            if unit1 or unit2:
                # Convert both to base units (meters for length)
                base1 = convert_to_base_unit(num1, unit1) if unit1 else num1
                base2 = convert_to_base_unit(num2, unit2) if unit2 else num2
                
                # Compare converted values
                if abs(base1 - base2) < 0.001:
                    return True
                
                # Also try the other way - if one has unit and other doesn't, 
                # assume the unitless one is in base units
                if unit1 and not unit2:
                    if abs(convert_to_base_unit(num1, unit1) - num2) < 0.001:
                        return True
                elif unit2 and not unit1:
                    if abs(num1 - convert_to_base_unit(num2, unit2)) < 0.001:
                        return True
        
        # Fallback: try simple float comparison of normalized strings
        try:
            num1 = float(norm1)
            num2 = float(norm2)
            if abs(num1 - num2) < 0.001:
                return True
        except ValueError:
            pass
    
    # For string answers, check if one contains the other (for partial matches)
    if answer_type == 'string':
        if norm1 in norm2 or norm2 in norm1:
            return True
    
    return False


def load_problems() -> Dict[str, Dict]:
    """Load problems with correct answers."""
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    problems = {}
    for problem in data['problems']:
        problems[problem['id']] = {
            'correct_answer': problem['correct_answer'],
            'answer_type': problem['answer_type'],
            'category': problem['category'],
            'problem_text': problem['problem_text']
        }
    
    return problems


def load_results() -> Dict[str, Dict]:
    """Load all final results from results directory."""
    results = {}
    
    if not os.path.exists(RESULTS_DIR):
        return results
    
    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith('_final_result.json'):
            problem_id = filename.replace('_final_result.json', '')
            filepath = os.path.join(RESULTS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results[problem_id] = data
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
    
    return results


def load_stage1_solutions() -> Dict[str, Dict]:
    """Load all Stage 1 solutions for baseline comparison."""
    solutions = {}
    
    if not os.path.exists(RAW_OUTPUTS_DIR):
        return solutions
    
    for filename in os.listdir(RAW_OUTPUTS_DIR):
        if filename.endswith('_stage1_solutions.json'):
            problem_id = filename.replace('_stage1_solutions.json', '')
            filepath = os.path.join(RAW_OUTPUTS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    solutions[problem_id] = data.get('solutions', {})
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
    
    return solutions


def load_stage3_refined() -> Dict[str, Dict]:
    """Load all Stage 3 refined solutions."""
    refined = {}
    
    if not os.path.exists(RAW_OUTPUTS_DIR):
        return refined
    
    for filename in os.listdir(RAW_OUTPUTS_DIR):
        if filename.endswith('_stage3_refined.json'):
            problem_id = filename.replace('_stage3_refined.json', '')
            filepath = os.path.join(RAW_OUTPUTS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    refined[problem_id] = data.get('refined_solutions', {})
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
    
    return refined


def calculate_system_metrics(problems: Dict, results: Dict) -> Dict:
    """Calculate system-level performance metrics."""
    metrics = {
        'total_problems': len(problems),
        'processed_problems': len(results),
        'correct_final_answers': 0,
        'overall_accuracy': 0.0,
        'by_category': {}
    }
    
    correct_count = 0
    
    for problem_id, result_data in results.items():
        if problem_id not in problems:
            continue
        
        problem = problems[problem_id]
        correct_answer = problem['correct_answer']
        answer_type = problem['answer_type']
        category = problem['category']
        
        # Get final answer from judge
        winning_answer = result_data.get('judgment', {}).get('winning_answer', '')
        
        if answers_match(winning_answer, correct_answer, answer_type):
            correct_count += 1
        
        # Track by category
        if category not in metrics['by_category']:
            metrics['by_category'][category] = {
                'total': 0,
                'correct': 0,
                'accuracy': 0.0
            }
        
        metrics['by_category'][category]['total'] += 1
        if answers_match(winning_answer, correct_answer, answer_type):
            metrics['by_category'][category]['correct'] += 1
    
    metrics['correct_final_answers'] = correct_count
    if len(results) > 0:
        metrics['overall_accuracy'] = correct_count / len(results)
    
    # Calculate category accuracies
    for category in metrics['by_category']:
        cat_data = metrics['by_category'][category]
        if cat_data['total'] > 0:
            cat_data['accuracy'] = cat_data['correct'] / cat_data['total']
    
    return metrics


def calculate_improvement_rate(problems: Dict, stage1_solutions: Dict, refined_solutions: Dict) -> Dict:
    """Calculate how often refinement improved answers."""
    metrics = {
        'total_with_refinement': 0,
        'improved': 0,
        'worsened': 0,
        'unchanged': 0,
        'improvement_rate': 0.0
    }
    
    for problem_id in stage1_solutions:
        if problem_id not in problems or problem_id not in refined_solutions:
            continue
        
        problem = problems[problem_id]
        correct_answer = problem['correct_answer']
        answer_type = problem['answer_type']
        
        # Get original answers
        original_answers = {}
        for solver_id, solution in stage1_solutions[problem_id].items():
            original_answers[solver_id] = solution.get('final_answer', '')
        
        # Get refined answers
        refined_answers = {}
        for solver_id, refined in refined_solutions[problem_id].items():
            refined_answers[solver_id] = refined.get('final_answer', '')
        
        # Check if any solver improved
        any_improved = False
        any_worsened = False
        
        for solver_id in original_answers:
            original = original_answers[solver_id]
            refined = refined_answers.get(solver_id, original)
            
            original_correct = answers_match(original, correct_answer, answer_type)
            refined_correct = answers_match(refined, correct_answer, answer_type)
            
            if not original_correct and refined_correct:
                any_improved = True
            elif original_correct and not refined_correct:
                any_worsened = True
        
        metrics['total_with_refinement'] += 1
        if any_improved:
            metrics['improved'] += 1
        elif any_worsened:
            metrics['worsened'] += 1
        else:
            metrics['unchanged'] += 1
    
    if metrics['total_with_refinement'] > 0:
        metrics['improvement_rate'] = metrics['improved'] / metrics['total_with_refinement']
    
    return metrics


def calculate_consensus_rate(problems: Dict, stage1_solutions: Dict, results: Dict = None) -> Dict:
    """Calculate consensus rate (when all 3 solvers agreed).
    
    Args:
        problems: Dictionary of all problems
        stage1_solutions: Dictionary of Stage 1 solutions
        results: Optional dictionary of final results - if provided, only counts problems that completed pipeline
    """
    metrics = {
        'total': 0,
        'full_consensus': 0,  # All 3 agree
        'partial_consensus': 0,  # 2 agree
        'no_consensus': 0,  # All different
        'consensus_rate': 0.0
    }
    
    for problem_id in stage1_solutions:
        if problem_id not in problems:
            continue
        
        # If results provided, only count problems that completed the pipeline
        if results is not None and problem_id not in results:
            continue
        
        answers = []
        for solver_id, solution in stage1_solutions[problem_id].items():
            answers.append(solution.get('final_answer', ''))
        
        # Normalize answers for comparison
        problem = problems[problem_id]
        answer_type = problem['answer_type']
        normalized = [normalize_answer(a, answer_type) for a in answers]
        
        unique_answers = len(set(normalized))
        
        metrics['total'] += 1
        if unique_answers == 1:
            metrics['full_consensus'] += 1
        elif unique_answers == 2:
            metrics['partial_consensus'] += 1
        else:
            metrics['no_consensus'] += 1
    
    if metrics['total'] > 0:
        metrics['consensus_rate'] = metrics['full_consensus'] / metrics['total']
    
    return metrics


def calculate_judge_accuracy(problems: Dict, results: Dict, stage1_solutions: Dict) -> Dict:
    """Calculate judge accuracy when solvers disagreed."""
    metrics = {
        'total_disagreements': 0,
        'judge_correct': 0,
        'judge_accuracy': 0.0,
        'majority_vote_correct': 0,
        'majority_vote_accuracy': 0.0
    }
    
    for problem_id in results:
        if problem_id not in problems or problem_id not in stage1_solutions:
            continue
        
        problem = problems[problem_id]
        correct_answer = problem['correct_answer']
        answer_type = problem['answer_type']
        
        # Get original answers
        answers = []
        for solver_id, solution in stage1_solutions[problem_id].items():
            answers.append(solution.get('final_answer', ''))
        
        # Check if there's disagreement
        normalized = [normalize_answer(a, answer_type) for a in answers]
        unique_answers = len(set(normalized))
        
        if unique_answers > 1:  # There's disagreement
            metrics['total_disagreements'] += 1
            
            # Check judge's answer
            winning_answer = results[problem_id].get('judgment', {}).get('winning_answer', '')
            judge_correct = answers_match(winning_answer, correct_answer, answer_type)
            
            if judge_correct:
                metrics['judge_correct'] += 1
            
            # Check majority vote
            answer_counts = Counter(normalized)
            majority_answer = answer_counts.most_common(1)[0][0]
            majority_correct = answers_match(majority_answer, correct_answer, answer_type)
            
            if majority_correct:
                metrics['majority_vote_correct'] += 1
    
    if metrics['total_disagreements'] > 0:
        metrics['judge_accuracy'] = metrics['judge_correct'] / metrics['total_disagreements']
        metrics['majority_vote_accuracy'] = metrics['majority_vote_correct'] / metrics['total_disagreements']
    
    return metrics


def run_single_llm_baseline(problems: Dict, model_name: str = "gpt-4") -> Dict:
    """Run baseline: just ask GPT-4 once per problem."""
    from openai import OpenAI
    from config import OPENAI_API_KEY
    import time
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    results = {}
    
    print(f"Running single-LLM baseline with {model_name}...")
    
    for problem_id, problem in problems.items():
        problem_text = problem['problem_text']
        
        prompt = f"""Solve the following problem. Provide a clear, concise answer.

Problem:
{problem_text}

Respond with only the final answer, no explanation needed."""
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a problem solver. Provide only the final answer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            answer = response.choices[0].message.content.strip()
            results[problem_id] = answer
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"Error processing {problem_id}: {e}")
            results[problem_id] = ""
    
    # Calculate accuracy
    correct = 0
    for problem_id, answer in results.items():
        if problem_id in problems:
            problem = problems[problem_id]
            if answers_match(answer, problem['correct_answer'], problem['answer_type']):
                correct += 1
    
    accuracy = correct / len(results) if results else 0.0
    
    return {
        'answers': results,
        'correct': correct,
        'total': len(results),
        'accuracy': accuracy
    }


def calculate_majority_vote_baseline(problems: Dict, stage1_solutions: Dict, results: Dict = None) -> Dict:
    """Calculate baseline: majority vote of 3 independent solutions.
    
    Args:
        problems: Dictionary of all problems
        stage1_solutions: Dictionary of Stage 1 solutions
        results: Optional dictionary of final results - if provided, only counts problems that completed pipeline
    """
    baseline_results = {}
    correct = 0
    
    for problem_id in stage1_solutions:
        if problem_id not in problems:
            continue
        
        # If results provided, only count problems that completed the pipeline
        if results is not None and problem_id not in results:
            continue
        
        problem = problems[problem_id]
        answer_type = problem['answer_type']
        
        # Get all 3 answers
        answers = []
        for solver_id, solution in stage1_solutions[problem_id].items():
            answers.append(solution.get('final_answer', ''))
        
        # Normalize and count
        normalized = [normalize_answer(a, answer_type) for a in answers]
        answer_counts = Counter(normalized)
        
        # Get majority (most common)
        if answer_counts:
            majority_answer = answer_counts.most_common(1)[0][0]
            baseline_results[problem_id] = majority_answer
            
            # Check if correct
            if answers_match(majority_answer, problem['correct_answer'], answer_type):
                correct += 1
    
    accuracy = correct / len(baseline_results) if baseline_results else 0.0
    
    return {
        'answers': baseline_results,
        'correct': correct,
        'total': len(baseline_results),
        'accuracy': accuracy
    }


def evaluate_all(include_baselines: bool = True) -> Dict:
    """Run complete evaluation."""
    print("Loading data...")
    problems = load_problems()
    results = load_results()
    stage1_solutions = load_stage1_solutions()
    refined_solutions = load_stage3_refined()
    
    print(f"Loaded {len(problems)} problems, {len(results)} results")
    
    evaluation = {
        'system_metrics': calculate_system_metrics(problems, results),
        'improvement_metrics': calculate_improvement_rate(problems, stage1_solutions, refined_solutions),
        'consensus_metrics': calculate_consensus_rate(problems, stage1_solutions, results),
        'judge_metrics': calculate_judge_accuracy(problems, results, stage1_solutions),
        'baselines': {}
    }
    
    # Calculate majority vote baseline
    print("Calculating majority vote baseline...")
    evaluation['baselines']['majority_vote'] = calculate_majority_vote_baseline(problems, stage1_solutions, results)
    
    # Run single LLM baseline if requested
    if include_baselines:
        print("Running single-LLM baseline (this will make API calls)...")
        evaluation['baselines']['single_llm'] = run_single_llm_baseline(problems)
    
    return evaluation


def save_evaluation(evaluation: Dict, filename: str = 'evaluation_results.json'):
    """Save evaluation results to JSON."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    filepath = os.path.join(RESULTS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(evaluation, f, indent=2, ensure_ascii=False)
    
    print(f"Evaluation results saved to: {filepath}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate system performance")
    parser.add_argument('--skip-baselines', action='store_true', 
                       help='Skip running single-LLM baseline (saves API calls)')
    
    args = parser.parse_args()
    
    evaluation = evaluate_all(include_baselines=not args.skip_baselines)
    
    # Print summary
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    
    sm = evaluation['system_metrics']
    print(f"\nSystem Performance:")
    print(f"  Overall Accuracy: {sm['overall_accuracy']:.1%} ({sm['correct_final_answers']}/{sm['processed_problems']})")
    
    im = evaluation['improvement_metrics']
    print(f"\nRefinement Impact:")
    print(f"  Improvement Rate: {im['improvement_rate']:.1%} ({im['improved']}/{im['total_with_refinement']})")
    print(f"  Improved: {im['improved']}, Worsened: {im['worsened']}, Unchanged: {im['unchanged']}")
    
    cm = evaluation['consensus_metrics']
    print(f"\nConsensus:")
    print(f"  Full Consensus Rate: {cm['consensus_rate']:.1%} ({cm['full_consensus']}/{cm['total']})")
    print(f"  Full: {cm['full_consensus']}, Partial: {cm['partial_consensus']}, None: {cm['no_consensus']}")
    
    jm = evaluation['judge_metrics']
    print(f"\nJudge Performance (when solvers disagreed):")
    print(f"  Judge Accuracy: {jm['judge_accuracy']:.1%} ({jm['judge_correct']}/{jm['total_disagreements']})")
    print(f"  Majority Vote Accuracy: {jm['majority_vote_accuracy']:.1%} ({jm['majority_vote_correct']}/{jm['total_disagreements']})")
    
    if 'majority_vote' in evaluation['baselines']:
        mv = evaluation['baselines']['majority_vote']
        print(f"\nBaseline - Majority Vote:")
        print(f"  Accuracy: {mv['accuracy']:.1%} ({mv['correct']}/{mv['total']})")
    
    if 'single_llm' in evaluation['baselines']:
        sl = evaluation['baselines']['single_llm']
        print(f"\nBaseline - Single LLM:")
        print(f"  Accuracy: {sl['accuracy']:.1%} ({sl['correct']}/{sl['total']})")
    
    print("\n" + "="*80)
    
    # Save results
    save_evaluation(evaluation)
