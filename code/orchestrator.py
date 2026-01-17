"""Orchestrator: Coordinates the full debate workflow end-to-end."""

import json
import os
import time
import logging
from datetime import datetime
from config import PROBLEMS_FILE, RAW_OUTPUTS_DIR, RESULTS_DIR

# Import all stage modules
from role_asigner import assign_roles
from solver import solve_problem
from reviewer import review_solutions
from refiner import refine_solutions
from judge import make_judgment

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(RAW_OUTPUTS_DIR, 'orchestrator.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_problems():
    """Load problems from the dataset."""
    if not os.path.exists(PROBLEMS_FILE):
        raise FileNotFoundError(f"Problems file not found: {PROBLEMS_FILE}")
    
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"Loaded {len(data['problems'])} problems from dataset")
    return data['problems']


def run_full_pipeline(problem, skip_stages=None):
    """Run the complete debate pipeline for a single problem.
    
    Args:
        problem: Problem dictionary with id, problem_text, etc.
        skip_stages: Optional list of stage numbers to skip (e.g., [0, 1] to skip stages 0 and 1)
    
    Returns:
        Dictionary with results from all stages
    """
    problem_id = problem['id']
    problem_text = problem['problem_text']
    
    logger.info(f"=" * 80)
    logger.info(f"Processing problem: {problem_id}")
    logger.info(f"Problem: {problem_text[:100]}...")
    logger.info(f"=" * 80)
    
    results = {
        "problem_id": problem_id,
        "problem_text": problem_text,
        "stages_completed": [],
        "errors": [],
        "start_time": datetime.now().isoformat()
    }
    
    skip_stages = skip_stages or []
    
    try:
        # Stage 0: Role Assignment
        if 0 not in skip_stages:
            logger.info(f"\n[Stage 0] Role Assignment")
            try:
                role_assignments = assign_roles(problem_id, problem_text)
                results["stage0_roles"] = role_assignments
                results["stages_completed"].append(0)
                logger.info(f"[Stage 0] ✓ Complete")
            except Exception as e:
                logger.error(f"[Stage 0] ✗ Error: {e}")
                results["errors"].append({"stage": 0, "error": str(e)})
                raise  # Can't continue without roles
        
        # Load roles if Stage 0 was skipped
        else:
            logger.info(f"[Stage 0] Skipped - loading from file")
            roles_file = os.path.join(RAW_OUTPUTS_DIR, f"{problem_id}_stage0_roles.json")
            if os.path.exists(roles_file):
                with open(roles_file, 'r', encoding='utf-8') as f:
                    roles_data = json.load(f)
                role_assignments = roles_data["final_assignments"]
            else:
                raise FileNotFoundError(f"Stage 0 output not found: {roles_file}")
        
        # Stage 1: Solution Generation
        if 1 not in skip_stages:
            logger.info(f"\n[Stage 1] Solution Generation")
            try:
                solutions = solve_problem(problem_id, problem_text, role_assignments)
                results["stage1_solutions"] = solutions
                results["stages_completed"].append(1)
                logger.info(f"[Stage 1] ✓ Complete")
            except Exception as e:
                logger.error(f"[Stage 1] ✗ Error: {e}")
                results["errors"].append({"stage": 1, "error": str(e)})
                raise  # Can't continue without solutions
        
        # Load solutions if Stage 1 was skipped
        else:
            logger.info(f"[Stage 1] Skipped - loading from file")
            solutions_file = os.path.join(RAW_OUTPUTS_DIR, f"{problem_id}_stage1_solutions.json")
            if os.path.exists(solutions_file):
                with open(solutions_file, 'r', encoding='utf-8') as f:
                    solutions_data = json.load(f)
                solutions = solutions_data["solutions"]
            else:
                raise FileNotFoundError(f"Stage 1 output not found: {solutions_file}")
        
        # Stage 2: Peer Review
        if 2 not in skip_stages:
            logger.info(f"\n[Stage 2] Peer Review")
            try:
                reviews = review_solutions(problem_id, problem_text, solutions)
                results["stage2_reviews"] = reviews
                results["stages_completed"].append(2)
                logger.info(f"[Stage 2] ✓ Complete")
            except Exception as e:
                logger.error(f"[Stage 2] ✗ Error: {e}")
                results["errors"].append({"stage": 2, "error": str(e)})
                raise  # Can't continue without reviews
        
        # Load reviews if Stage 2 was skipped
        else:
            logger.info(f"[Stage 2] Skipped - loading from file")
            reviews_file = os.path.join(RAW_OUTPUTS_DIR, f"{problem_id}_stage2_reviews.json")
            if os.path.exists(reviews_file):
                with open(reviews_file, 'r', encoding='utf-8') as f:
                    reviews_data = json.load(f)
                reviews = reviews_data["reviews"]
            else:
                raise FileNotFoundError(f"Stage 2 output not found: {reviews_file}")
        
        # Stage 3: Solution Refinement
        if 3 not in skip_stages:
            logger.info(f"\n[Stage 3] Solution Refinement")
            try:
                refined_solutions = refine_solutions(problem_id, problem_text, solutions, reviews)
                results["stage3_refined"] = refined_solutions
                results["stages_completed"].append(3)
                logger.info(f"[Stage 3] ✓ Complete")
            except Exception as e:
                logger.error(f"[Stage 3] ✗ Error: {e}")
                results["errors"].append({"stage": 3, "error": str(e)})
                raise  # Can't continue without refined solutions
        
        # Load refined solutions if Stage 3 was skipped
        else:
            logger.info(f"[Stage 3] Skipped - loading from file")
            refined_file = os.path.join(RAW_OUTPUTS_DIR, f"{problem_id}_stage3_refined.json")
            if os.path.exists(refined_file):
                with open(refined_file, 'r', encoding='utf-8') as f:
                    refined_data = json.load(f)
                refined_solutions = refined_data["refined_solutions"]
            else:
                raise FileNotFoundError(f"Stage 3 output not found: {refined_file}")
        
        # Stage 4: Final Judgment
        if 4 not in skip_stages:
            logger.info(f"\n[Stage 4] Final Judgment")
            try:
                judgment = make_judgment(
                    problem_id,
                    problem_text,
                    solutions,
                    reviews,
                    refined_solutions,
                    role_assignments
                )
                results["stage4_judgment"] = judgment
                results["stages_completed"].append(4)
                results["winning_answer"] = judgment["winning_answer"]
                results["winner"] = judgment["winner"]
                logger.info(f"[Stage 4] ✓ Complete")
                logger.info(f"[Stage 4] Winner: {judgment['winner']}")
                logger.info(f"[Stage 4] Final Answer: {judgment['winning_answer']}")
            except Exception as e:
                logger.error(f"[Stage 4] ✗ Error: {e}")
                results["errors"].append({"stage": 4, "error": str(e)})
                # Don't raise - judgment failure doesn't invalidate previous stages
        
        results["end_time"] = datetime.now().isoformat()
        results["success"] = len(results["errors"]) == 0
        
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Problem {problem_id} processing complete")
        logger.info(f"Stages completed: {results['stages_completed']}")
        if results["errors"]:
            logger.warning(f"Errors encountered: {len(results['errors'])}")
        logger.info(f"{'=' * 80}\n")
        
    except Exception as e:
        logger.error(f"Fatal error processing problem {problem_id}: {e}")
        results["errors"].append({"stage": "fatal", "error": str(e)})
        results["end_time"] = datetime.now().isoformat()
        results["success"] = False
    
    return results


def run_all_problems(problems=None, start_from=0, max_problems=None):
    """Run the full pipeline on all problems (or a subset).
    
    Args:
        problems: Optional list of problems. If None, loads from file.
        start_from: Index to start from (for resuming)
        max_problems: Maximum number of problems to process (None = all)
    
    Returns:
        List of results for each problem
    """
    if problems is None:
        problems = load_problems()
    
    if max_problems:
        problems = problems[start_from:start_from + max_problems]
    else:
        problems = problems[start_from:]
    
    logger.info(f"Processing {len(problems)} problems (starting from index {start_from})")
    
    all_results = []
    
    for i, problem in enumerate(problems, start=start_from):
        logger.info(f"\n{'#' * 80}")
        logger.info(f"Problem {i+1}/{len(problems) + start_from}: {problem['id']}")
        logger.info(f"{'#' * 80}")
        
        try:
            result = run_full_pipeline(problem)
            all_results.append(result)
            
            # Save progress after each problem
            progress_file = os.path.join(RESULTS_DIR, 'progress.json')
            os.makedirs(RESULTS_DIR, exist_ok=True)
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_processed": len(all_results),
                    "current_index": i,
                    "results": all_results
                }, f, indent=2, ensure_ascii=False)
            
        except KeyboardInterrupt:
            logger.warning("Interrupted by user")
            break
        except Exception as e:
            logger.error(f"Failed to process problem {problem['id']}: {e}")
            all_results.append({
                "problem_id": problem['id'],
                "success": False,
                "error": str(e)
            })
    
    # Save final summary
    summary = {
        "total_problems": len(problems),
        "processed": len(all_results),
        "successful": sum(1 for r in all_results if r.get("success", False)),
        "failed": sum(1 for r in all_results if not r.get("success", False)),
        "results": all_results,
        "timestamp": datetime.now().isoformat()
    }
    
    summary_file = os.path.join(RESULTS_DIR, 'summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n{'=' * 80}")
    logger.info(f"Batch processing complete!")
    logger.info(f"Total: {summary['total_problems']}, Successful: {summary['successful']}, Failed: {summary['failed']}")
    logger.info(f"Summary saved to: {summary_file}")
    logger.info(f"{'=' * 80}")
    
    return all_results


if __name__ == "__main__":
    import sys
    
    # Example usage
    if len(sys.argv) > 1:
        # Run specific problem by ID
        problem_id = sys.argv[1]
        problems = load_problems()
        problem = next((p for p in problems if p['id'] == problem_id), None)
        
        if problem:
            run_full_pipeline(problem)
        else:
            logger.error(f"Problem {problem_id} not found")
    else:
        # Run first problem as test
        problems = load_problems()
        if problems:
            logger.info("Running test on first problem...")
            run_full_pipeline(problems[0])
        else:
            logger.error("No problems found in dataset")
