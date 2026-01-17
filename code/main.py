"""Main entry point for the Multi-LLM Collaborative Debate System."""

import argparse
import sys
import os

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator import run_full_pipeline, run_all_problems, load_problems
import logging

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-LLM Collaborative Debate System - Full Pipeline"
    )
    
    parser.add_argument(
        '--problem-id',
        type=str,
        help='Process a specific problem by ID (e.g., math_001)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all problems in the dataset'
    )
    
    parser.add_argument(
        '--start-from',
        type=int,
        default=0,
        help='Start from this problem index (for resuming)'
    )
    
    parser.add_argument(
        '--max-problems',
        type=int,
        help='Maximum number of problems to process'
    )
    
    parser.add_argument(
        '--skip-stages',
        type=str,
        help='Comma-separated list of stage numbers to skip (e.g., "0,1" to skip stages 0 and 1)'
    )
    
    args = parser.parse_args()
    
    # Parse skip stages
    skip_stages = []
    if args.skip_stages:
        try:
            skip_stages = [int(s.strip()) for s in args.skip_stages.split(',')]
        except ValueError:
            logger.error("Invalid skip-stages format. Use comma-separated numbers (e.g., '0,1')")
            sys.exit(1)
    
    try:
        if args.problem_id:
            # Run specific problem
            problems = load_problems()
            problem = next((p for p in problems if p['id'] == args.problem_id), None)
            
            if not problem:
                logger.error(f"Problem '{args.problem_id}' not found in dataset")
                sys.exit(1)
            
            logger.info(f"Processing problem: {args.problem_id}")
            result = run_full_pipeline(problem, skip_stages=skip_stages)
            
            if result.get("success"):
                logger.info(f"\n✓ Successfully processed {args.problem_id}")
                logger.info(f"Winner: {result.get('winner', 'N/A')}")
                logger.info(f"Final Answer: {result.get('winning_answer', 'N/A')}")
            else:
                logger.error(f"\n✗ Failed to process {args.problem_id}")
                sys.exit(1)
        
        elif args.all:
            # Run all problems
            logger.info("Processing all problems in dataset...")
            results = run_all_problems(
                start_from=args.start_from,
                max_problems=args.max_problems
            )
            
            successful = sum(1 for r in results if r.get("success", False))
            total = len(results)
            
            logger.info(f"\n{'=' * 80}")
            logger.info(f"Batch processing complete!")
            logger.info(f"Successful: {successful}/{total}")
            logger.info(f"{'=' * 80}")
        
        else:
            # Default: run first problem as test
            problems = load_problems()
            if not problems:
                logger.error("No problems found in dataset")
                sys.exit(1)
            
            logger.info("Running test on first problem (use --all to process all, or --problem-id for specific)")
            result = run_full_pipeline(problems[0], skip_stages=skip_stages)
            
            if result.get("success"):
                logger.info(f"\n✓ Test complete!")
                logger.info(f"Winner: {result.get('winner', 'N/A')}")
                logger.info(f"Final Answer: {result.get('winning_answer', 'N/A')}")
            else:
                logger.error(f"\n✗ Test failed")
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
