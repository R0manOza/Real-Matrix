"""Run complete evaluation and generate plots."""

import argparse
from evaluator import evaluate_all, save_evaluation
from plotter import generate_all_plots


def main():
    parser = argparse.ArgumentParser(description="Run complete evaluation and generate plots")
    parser.add_argument('--skip-baselines', action='store_true',
                       help='Skip running single-LLM baseline (saves API calls)')
    parser.add_argument('--skip-plots', action='store_true',
                       help='Skip generating plots')
    parser.add_argument('--evaluation-only', action='store_true',
                       help='Only run evaluation, skip plots')
    
    args = parser.parse_args()
    
    # Run evaluation
    print("="*80)
    print("PHASE 3: EVALUATION AND ANALYSIS")
    print("="*80)
    
    evaluation = evaluate_all(include_baselines=not args.skip_baselines)
    save_evaluation(evaluation)
    
    # Generate plots
    if not args.skip_plots and not args.evaluation_only:
        print("\n" + "="*80)
        print("GENERATING PLOTS")
        print("="*80)
        generate_all_plots(evaluation)
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETE!")
    print("="*80)
    print(f"Results saved to: data/results/evaluation_results.json")
    if not args.skip_plots and not args.evaluation_only:
        print(f"Plots saved to: data/results/")


if __name__ == "__main__":
    main()
