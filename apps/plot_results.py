"""
Title: Results Plotting Script

This script creates plots comparing traditional and coalition strategies.

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 05/06/2025
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

# The desired order of setups
SETUP_ORDER = ['5t5s', '5t10s', '10t5s', '10t10s', '20t20s']

def load_results():
    """Load all result files from the results directory."""
    results = {
        'traditional': {},
        'coalition': {}
    }

    for filename in os.listdir('results'):
        if filename.endswith('_results.json'):
            with open(os.path.join('results', filename), 'r') as f:
                data = json.load(f)
                setup_name = data['setup_name']
                if 'traditional' in filename:
                    results['traditional'][setup_name] = data
                elif 'coalition' in filename:
                    results['coalition'][setup_name] = data

    return results

def get_ordered_data(results, metric_path):
    """Get data in the desired order for a specific metric."""
    traditional_data = []
    coalition_data = []

    for setup in SETUP_ORDER:
        if setup in results['traditional'] and setup in results['coalition']:
            traditional_value = results['traditional'][setup]
            coalition_value = results['coalition'][setup]
            for key in metric_path:
                traditional_value = traditional_value[key]
                coalition_value = coalition_value[key]
            traditional_data.append(traditional_value)
            coalition_data.append(coalition_value)

    return traditional_data, coalition_data

def plot_memory_utilisation(results):
    """Plot memory utilisation comparison."""
    traditional_util, coalition_util = get_ordered_data(
        results,
        ['metrics', 'memory_utilisation', 'average']
    )

    plt.figure(figsize=(10, 6))
    x = np.arange(len(SETUP_ORDER))
    width = 0.35

    plt.bar(x - width/2, traditional_util, width, label='Traditional Strategy')
    plt.bar(x + width/2, coalition_util, width, label='Coalition Strategy')

    plt.xlabel('Setup Configuration')
    plt.ylabel('Memory Utilisation (%)')
    plt.title('Memory Utilisation Comparison')
    plt.xticks(x, SETUP_ORDER)
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Add percentage formatter to y-axis
    plt.gca().yaxis.set_major_formatter(PercentFormatter())

    plt.tight_layout()
    plt.savefig('results/memory_utilisation.png')
    plt.close()

def plot_reward_comparison(results):
    """Plot reward comparison."""
    traditional_reward, coalition_reward = get_ordered_data(
        results,
        ['metrics', 'rewards', 'average_per_satellite']
    )

    plt.figure(figsize=(10, 6))
    x = np.arange(len(SETUP_ORDER))
    width = 0.35

    plt.bar(x - width/2, traditional_reward, width, label='Traditional Strategy')
    plt.bar(x + width/2, coalition_reward, width, label='Coalition Strategy')

    plt.xlabel('Setup Configuration')
    plt.ylabel('Average Reward per Satellite')
    plt.title('Reward Distribution Comparison')
    plt.xticks(x, SETUP_ORDER)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/reward_comparison.png')
    plt.close()

def plot_negotiation_success(results):
    """Plot negotiation success rate comparison."""
    traditional_success, coalition_success = get_ordered_data(
        results,
        ['metrics', 'negotiation', 'success_rate']
    )

    plt.figure(figsize=(10, 6))
    x = np.arange(len(SETUP_ORDER))
    width = 0.35

    plt.bar(x - width/2, traditional_success, width, label='Traditional Strategy')
    plt.bar(x + width/2, coalition_success, width, label='Coalition Strategy')

    plt.xlabel('Setup Configuration')
    plt.ylabel('Success Rate (%)')
    plt.title('Negotiation Success Rate Comparison')
    plt.xticks(x, SETUP_ORDER)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.gca().yaxis.set_major_formatter(PercentFormatter())

    plt.tight_layout()
    plt.savefig('results/negotiation_success.png')
    plt.close()

def plot_task_allocation_success(results):
    """Plot task allocation success rate comparison."""
    traditional_success, coalition_success = get_ordered_data(
        results,
        ['metrics', 'task_allocation', 'success_rate']
    )

    plt.figure(figsize=(10, 6))
    x = np.arange(len(SETUP_ORDER))
    width = 0.35

    plt.bar(x - width/2, traditional_success, width, label='Traditional Strategy')
    plt.bar(x + width/2, coalition_success, width, label='Coalition Strategy')

    plt.xlabel('Setup Configuration')
    plt.ylabel('Success Rate (%)')
    plt.title('Task Allocation Success Rate Comparison')
    plt.xticks(x, SETUP_ORDER)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.gca().yaxis.set_major_formatter(PercentFormatter())

    plt.tight_layout()
    plt.savefig('results/task_allocation_success.png')
    plt.close()

def plot_negotiation_rounds(results):
    """Plot average negotiation rounds comparison."""
    traditional_rounds, coalition_rounds = get_ordered_data(
        results,
        ['metrics', 'negotiation', 'average_rounds']
    )

    plt.figure(figsize=(10, 6))
    x = np.arange(len(SETUP_ORDER))
    width = 0.35

    plt.bar(x - width/2, traditional_rounds, width, label='Traditional Strategy')
    plt.bar(x + width/2, coalition_rounds, width, label='Coalition Strategy')

    plt.xlabel('Setup Configuration')
    plt.ylabel('Average Rounds')
    plt.title('Average Negotiation Rounds Comparison')
    plt.xticks(x, SETUP_ORDER)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/negotiation_rounds.png')
    plt.close()

def main():
    plt.style.use('seaborn-v0_8')
    results = load_results()

    plot_memory_utilisation(results)
    plot_reward_comparison(results)
    plot_negotiation_success(results)
    plot_task_allocation_success(results)
    plot_negotiation_rounds(results)

    print("All plots have been generated in the 'results' directory.")

if __name__ == "__main__":
    main()