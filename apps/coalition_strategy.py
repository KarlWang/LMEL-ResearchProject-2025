"""
Title: Coalition tabse-based Strategy

This script analyse the coalition table-based task allocation strategy

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 27/05/2025
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from negmas import SAOMechanism, TimeBasedConcedingNegotiator, AspirationNegotiator, SAONegotiator, ResponseType
from negmas.preferences import LinearAdditiveUtilityFunction as LUFun
from negmas.preferences.value_fun import LinearFun, IdentityFun, AffineFun
from negmas.preferences.crisp.mapping import MappingUtilityFunction
from negmas.outcomes import dict2outcome, make_issue, Outcome
import matplotlib.pyplot as plt
import pprint
from random import choice
from negmas import PolyAspiration, PresortingInverseUtilityFunction, PreferencesChangeType
from MultiSatellitesNego.negotiators.v05 import NegotiatorV05
from MultiSatellitesNego.satellite import Satellite
from MultiSatellitesNego.task import Task
from MultiSatellitesNego.negotiators import get_negotiator, NEGOTIATOR_REGISTRY
from MultiSatellitesNego.utils import (
    calculate_average_memory_utilisation,
    calculate_average_reward,
    calculate_average_negotiation_rounds,
    calculate_negotiation_success_rate,
    calculate_task_allocation_success_rate
)

import json
import sys

PRINT_DEBUG = False

def run_negotiations(negotiator_version, satellites, tasks, plot=False, n_steps=20):

    print("\nNegotiations Starting")

    negotiator_class = get_negotiator(negotiator_version)

    allocated_tasks = set()

    negotiation_results = []

    for sat in satellites:
        print(f"\n=== Running negotiations with {sat['name']} as initiator ===")
        initiator_table = sat['coalition_table']

        task_preferences = {}
        for pref in initiator_table['preferences']:
            if pref['task_id'] not in task_preferences:
                task_preferences[pref['task_id']] = []
            task_preferences[pref['task_id']].append(pref)

        for task_id, prefs in sorted(task_preferences.items()):
            # Skip if task has already been allocated
            if task_id in allocated_tasks:
                print(f"Task {task_id} already allocated, skipping...")
                continue

            task = next((t for t in tasks if t['id'] == task_id), None)
            if not task:
                continue

            task_result = {
                "task_id": task_id,
                "location": task['location_index'],
                "initiator": sat['name'],
                "negotiations": []
            }

            required_satellites = 2
            # Try each coalition in order of priority
            for pref in sorted(prefs, key=lambda p: p['priority']):

                # This check... more thinking needed
                if len(pref['preferred_satellites']) + 1 != required_satellites:
                    continue

                session = SAOMechanism(issues=negotiator_class.negotiator_issues, n_steps=n_steps)
                initiator = sat
                initiator_negotiator = negotiator_class(Satellite(**initiator), Task(**task))
                session.add(initiator_negotiator, ufun=negotiator_class.initiator_ufun)

                # Add all partners in the coalition with task information
                # At this stage, only one partner
                partner_negotiators = []
                for partner_id in pref['preferred_satellites']:
                    partner = next((s for s in satellites if s['name'] == partner_id), None)
                    if partner:
                        partner_negotiator = negotiator_class(Satellite(**partner), Task(**task))
                        partner_negotiators.append(partner_negotiator)
                        session.add(partner_negotiator, ufun=negotiator_class.partner_ufun)
                print(f"Task {task_id}: {initiator['name']} vs {pref['preferred_satellites']}")

                result = session.run()
                agreement = session.state.agreement is not None

                negotiation_result = {
                    'task_id': task_id,
                    'initiator': initiator['name'],
                    'partners': pref['preferred_satellites'],
                    'agreement_reached': agreement,
                    'rounds': session.state.step
                }
                negotiation_results.append(negotiation_result)

                if agreement:
                    print(f"Agreement achieved: {session.state.agreement} - {initiator_negotiator} and {partner_negotiator}")

                    # Calculate new memory for initiator and partner
                    current_memory_init = float(initiator['available_memory'])
                    current_memory_part = float(partner['available_memory'])
                    task_memory = float(task['memory_required'])
                    memory_percentage_init = float(session.state.agreement[1] / 100)
                    new_memory_init = round(current_memory_init - task_memory * memory_percentage_init)
                    new_memory_part = round(current_memory_part - task_memory * (1 - memory_percentage_init))

                    # Update satellite's available memory in the original list
                    initiator['available_memory'] = new_memory_init
                    partner['available_memory'] = new_memory_part

                    # Also update the negotiator objects for consistency
                    initiator_negotiator.satellite.available_memory = new_memory_init
                    partner_negotiator.satellite.available_memory = new_memory_part

                    # Update rewards
                    initiator_reward = (float(session.state.agreement[0]) / 100) * float(task["reward_points"])
                    partner_reward = float(task["reward_points"]) - initiator_reward
                    initiator['accumulated_reward'] += round(initiator_reward)
                    partner['accumulated_reward'] += round(partner_reward)

                    # Mark task as allocated
                    allocated_tasks.add(task_id)
                    break

    return {
        'negotiation_results': negotiation_results,
        'allocated_tasks': allocated_tasks
    }

def main():

    if len(sys.argv) < 2:
        print("Usage: python coalition_strategy.py <path_to_json_file>")
        sys.exit(1)

    json_file = sys.argv[1]

    PRINT_DEBUG = any(flag in sys.argv for flag in ["--debug", "-d"])

    with open(json_file, 'r') as file:
        data = json.load(file)

    tasks = data['tasks']
    satellites = data['satellites']

    print("\n--- Task Information ---")
    for t in tasks:
        print(f"Task {t['id']}: Memory Required: {t['memory_required']}")

    print("\n--- Satellite Information ---")
    for sat in satellites:
        print(f"{sat['name']}: Memory Capacity: {sat['available_memory']}")

    results = run_negotiations("v05", satellites, tasks)

    # Calculate and display memory utilisation metrics
    avg_utilisation, total_used, total_available = calculate_average_memory_utilisation(satellites)
    print("\n--- Memory Utilisation Metrics ---")
    print(f"Total Memory Available: {total_available}")
    print(f"Total Memory Used: {total_used}")
    print(f"Average Memory Utilisation: {avg_utilisation:.2f}%")

    # Calculate and display reward metrics
    avg_reward, total_reward, num_satellites = calculate_average_reward(satellites)
    print("\n--- Reward Metrics ---")
    print(f"Total Reward Points: {total_reward}")
    print(f"Number of Satellites: {num_satellites}")
    print(f"Average Reward per Satellite: {avg_reward:.2f}")

    # Calculate and display negotiation rounds metrics
    avg_rounds, total_rounds, num_negotiations = calculate_average_negotiation_rounds(results)
    print("\n--- Negotiation Rounds Metrics ---")
    print(f"Total Negotiation Rounds: {total_rounds}")
    print(f"Number of Negotiations: {num_negotiations}")
    print(f"Average Rounds per Negotiation: {avg_rounds:.2f}")

    # Calculate and display negotiation success rate metrics
    success_rate, successful_negotiations, total_negotiations = calculate_negotiation_success_rate(results)
    print("\n--- Negotiation Success Rate Metrics ---")
    print(f"Total Negotiations: {total_negotiations}")
    print(f"Successful Negotiations: {successful_negotiations}")
    print(f"Success Rate: {success_rate:.2f}%")

    # Calculate and display task allocation success rate metrics
    total_tasks = len(tasks)
    successful_tasks = len(results['allocated_tasks'])
    task_success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    print("\n--- Task Allocation Success Rate Metrics ---")
    print(f"Total Tasks: {total_tasks}")
    print(f"Successfully Allocated Tasks: {successful_tasks}")
    print(f"Task Allocation Success Rate: {task_success_rate:.2f}%")

if __name__ == "__main__":
    main()
