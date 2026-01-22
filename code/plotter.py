"""Phase 3: Plotting - Generate visualizations of evaluation results."""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from config import RESULTS_DIR


def load_evaluation(filename: str = 'evaluation_results.json') -> dict:
    """Load evaluation results."""
    filepath = os.path.join(RESULTS_DIR, filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Evaluation results not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_system_vs_baselines(evaluation: dict, save_path: str = None):
    """Plot system accuracy vs baseline methods."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    methods = []
    accuracies = []
    
    # System performance
    sm = evaluation['system_metrics']
    methods.append('Our System\n(Full Debate)')
    accuracies.append(sm['overall_accuracy'])
    
    # Baselines
    if 'majority_vote' in evaluation['baselines']:
        mv = evaluation['baselines']['majority_vote']
        methods.append('Majority Vote\n(3 Independent)')
        accuracies.append(mv['accuracy'])
    
    if 'single_llm' in evaluation['baselines']:
        sl = evaluation['baselines']['single_llm']
        methods.append('Single LLM\n(GPT-4 Once)')
        accuracies.append(sl['accuracy'])
    
    # Create bar plot
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    bars = ax.bar(methods, [a * 100 for a in accuracies], color=colors[:len(methods)], alpha=0.8)
    
    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{acc*100:.1f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_title('System Performance vs Baselines', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to: {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_accuracy_by_category(evaluation: dict, save_path: str = None):
    """Plot accuracy broken down by problem category."""
    sm = evaluation['system_metrics']
    
    if not sm.get('by_category'):
        print("No category data available")
        return
    
    categories = []
    accuracies = []
    counts = []
    
    for category, data in sm['by_category'].items():
        categories.append(category.replace('_', ' ').title())
        accuracies.append(data['accuracy'] * 100)
        counts.append(f"{data['correct']}/{data['total']}")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(categories, accuracies, color='#3498db', alpha=0.8)
    
    # Add value labels
    for bar, acc, count in zip(bars, accuracies, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{acc:.1f}%\n({count})',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_title('Accuracy by Problem Category', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to: {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_consensus_analysis(evaluation: dict, save_path: str = None):
    """Plot consensus rate breakdown."""
    cm = evaluation['consensus_metrics']
    
    labels = ['Full Consensus\n(All 3 Agree)', 'Partial Consensus\n(2 Agree)', 'No Consensus\n(All Different)']
    sizes = [cm['full_consensus'], cm['partial_consensus'], cm['no_consensus']]
    colors = ['#2ecc71', '#f39c12', '#e74c3c']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                      startangle=90, textprops={'fontsize': 11})
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    ax.set_title('Solver Consensus Analysis', fontsize=14, fontweight='bold', pad=20)
    
    # Add count annotations
    total = sum(sizes)
    for i, (label, size) in enumerate(zip(labels, sizes)):
        if size > 0:
            pct = (size / total) * 100
            ax.text(0, -1.3 - i*0.2, f'{label}: {size} problems ({pct:.1f}%)',
                   ha='center', fontsize=10, transform=ax.transAxes)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to: {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_refinement_impact(evaluation: dict, save_path: str = None):
    """Plot refinement impact (improved vs worsened vs unchanged)."""
    im = evaluation['improvement_metrics']
    
    labels = ['Improved', 'Unchanged', 'Worsened']
    sizes = [im['improved'], im['unchanged'], im['worsened']]
    colors = ['#2ecc71', '#95a5a6', '#e74c3c']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                      startangle=90, textprops={'fontsize': 11})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    ax.set_title('Refinement Impact on Solutions', fontsize=14, fontweight='bold', pad=20)
    
    total = sum(sizes)
    improvement_rate = im['improvement_rate'] * 100
    ax.text(0, -1.2, f'Improvement Rate: {improvement_rate:.1f}%',
           ha='center', fontsize=12, fontweight='bold', transform=ax.transAxes)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to: {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_judge_performance(evaluation: dict, save_path: str = None):
    """Plot judge accuracy vs majority vote when solvers disagreed."""
    jm = evaluation['judge_metrics']
    
    if jm['total_disagreements'] == 0:
        print("No disagreements found - cannot plot judge performance")
        return
    
    methods = ['Judge Selection', 'Majority Vote']
    accuracies = [jm['judge_accuracy'] * 100, jm['majority_vote_accuracy'] * 100]
    counts = [f"{jm['judge_correct']}/{jm['total_disagreements']}", 
              f"{jm['majority_vote_correct']}/{jm['total_disagreements']}"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#9b59b6', '#3498db']
    bars = ax.bar(methods, accuracies, color=colors, alpha=0.8)
    
    # Add value labels
    for bar, acc, count in zip(bars, accuracies, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{acc:.1f}%\n({count})',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Accuracy (%)', fontsize=12)
    ax.set_title(f'Judge vs Majority Vote\n(When Solvers Disagreed: {jm["total_disagreements"]} problems)',
                fontsize=14, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to: {save_path}")
    else:
        plt.show()
    
    plt.close()


def generate_all_plots(evaluation: dict = None, output_dir: str = None):
    """Generate all evaluation plots."""
    if evaluation is None:
        evaluation = load_evaluation()
    
    if output_dir is None:
        output_dir = RESULTS_DIR
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating plots...")
    
    # System vs Baselines
    plot_system_vs_baselines(evaluation, 
                            os.path.join(output_dir, 'system_vs_baselines.png'))
    
    # Accuracy by Category
    plot_accuracy_by_category(evaluation,
                              os.path.join(output_dir, 'accuracy_by_category.png'))
    
    # Consensus Analysis
    plot_consensus_analysis(evaluation,
                          os.path.join(output_dir, 'consensus_analysis.png'))
    
    # Refinement Impact
    plot_refinement_impact(evaluation,
                          os.path.join(output_dir, 'refinement_impact.png'))
    
    # Judge Performance
    plot_judge_performance(evaluation,
                          os.path.join(output_dir, 'judge_performance.png'))
    
    print(f"\nAll plots saved to: {output_dir}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate evaluation plots")
    parser.add_argument('--evaluation-file', type=str, default='evaluation_results.json',
                       help='Evaluation results JSON file')
    
    args = parser.parse_args()
    
    try:
        evaluation = load_evaluation(args.evaluation_file)
        generate_all_plots(evaluation)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run evaluator.py first to generate evaluation results.")
