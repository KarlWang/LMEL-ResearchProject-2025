"""
Title: Negotiation Application File

This module is the entry of the Negotiation Application

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 02/04/2025
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from negmas import (
    SAOMechanism,
    SAONegotiator,
    MappingUtilityFunction,
    Issue,
    Outcome,
    ResponseType
)
from negmas.preferences import LinearAdditiveUtilityFunction as LUFun, LinearFun, IdentityFun, AffineFun
from MultiSatellitesNego.negotiation_config import ISSUES, SIMPLE_CITIES
from MultiSatellitesNego.negotiation_config import INITIATOR_UTILITY, PARTNER_UTILITY
from MultiSatellitesNego.task_generator import create_tasks
from MultiSatellitesNego.satellite_generator import create_satellites
from MultiSatellitesNego.negotiators import get_negotiator, NEGOTIATOR_REGISTRY
from MultiSatellitesNego.coalition_generator import generate_coalition_tables
from datetime import datetime
import matplotlib.pyplot as plt
import json
import argparse
import numpy as np

def create_results_dict(tasks, satellites, coalition_table, task_preferences):
    """
    Create a dictionary containing all the information needed for the negotiation results.

    Args:
        tasks: List of Task objects
        satellites: List of Satellite objects
        coalition_table: CoalitionTable object for the initiator
        task_preferences: Dictionary mapping task IDs to lists of preferences

    Returns:
        Dictionary containing all the information
    """
    results_dict = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "satellites": [
            {
                "name": sat.name,
                "memory_capacity": sat.memory_capacity,
                "available_memory": sat.available_memory
            }
            for sat in satellites
        ],
        "tasks": [
            {
                "id": task.id,
                "location_index": task.location_index,
                "time_window": task.time_window,
                "reward_points": task.reward_points,
                "memory_required": task.memory_required
            }
            for task in tasks
        ],
        "coalition_table": {
            "satellite": coalition_table.satellite_id,
            "preferences": [
                {
                    "task_id": pref.task_id,
                    "preferred_satellites": pref.preferred_satellites,
                    "priority": pref.priority
                }
                for pref in coalition_table.preferences
            ]
        },
        "negotiation_results": []
    }

    return results_dict

def write_negotiation_results(cls, results_dict, task_preferences, tasks, satellites, plot=False, n_steps: int = 10):

    for task_id, prefs in sorted(task_preferences.items()):
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            continue

        task_result = {
            "task_id": task_id,
            "location_index": task.location_index,
            "initiator": results_dict["coalition_table"]["satellite"],
            "negotiations": []
        }

        # Get the task's required number of satellites
        # This needs to be calculated properly instead of being hard-coded.
        # The easist set up could be each task time window one satellite, so
        # required_satellites = (number of time windows)
        required_satellites = 2

        # Try each coalition in order of priority
        for pref in sorted(prefs, key=lambda p: p.priority):
            if len(pref.preferred_satellites) + 1 != required_satellites:
                continue

            # Create negotiation session with specified number of steps
            # The issues argument probabaly should be the negotiator's issues - see traditional_strategy.py
            session = SAOMechanism(issues=ISSUES, n_steps=n_steps)

            # Get the initiator satellite from the coalition table
            initiator_name = results_dict["coalition_table"]["satellite"]
            initiator = next((s for s in satellites if s.name == initiator_name), None)
            if not initiator:
                continue

            # Add initiator with task information
            initiator_negotiator = cls(initiator, task)
            session.add(initiator_negotiator, ufun=cls.initiator_ufun)

            # Add all partners in the coalition with task information
            partner_negotiators = []
            for partner_id in pref.preferred_satellites:
                partner = next((s for s in satellites if s.name == partner_id), None)
                if partner:
                    partner_negotiator = cls(partner, task)
                    partner_negotiators.append(partner_negotiator)
                    session.add(partner_negotiator, ufun=cls.partner_ufun)

            result = session.run()
            if plot:
                session.plot()
                plt.show()

            agreement = session.state.agreement is not None

            if agreement:
                print(f"Agreement achieved: {session.state.agreement} - {initiator_negotiator} and {partner_negotiator}")

                try:
                    current_memory_init = float(initiator_negotiator.satellite.available_memory)
                    current_memory_part = float(partner_negotiator.satellite.available_memory)
                    task_memory = float(task.memory_required)

                    # Calculate memory percentage based on task requirement
                    memory_percentage_init = float(session.state.agreement[1] / 100)

                    # Calculate new available memory
                    new_memory_init = round(current_memory_init - task_memory * memory_percentage_init)
                    new_memory_part = round(current_memory_part - task_memory * (1 - memory_percentage_init))

                    # Update satellite's available memory
                    initiator_negotiator.satellite.available_memory = new_memory_init
                    partner_negotiator.satellite.available_memory = new_memory_part

                    print(f"{initiator_negotiator.satellite.name} memory update: {current_memory_init} -> {new_memory_init} (Contribution: {task_memory} * {memory_percentage_init*100:.1f}% = {task_memory * memory_percentage_init})")
                    print(f"{partner_negotiator.satellite.name} memory update: {current_memory_part} -> {new_memory_part} (Contribution: {task_memory} * {(1-memory_percentage_init)*100:.1f}% = {task_memory * (1-memory_percentage_init)})")

                    # Calculate reward distribution
                    reward_percentage_init = float(session.state.agreement[0] / 100)
                    total_reward = float(task.reward_points)
                    initiator_reward = round(total_reward * reward_percentage_init)
                    partner_reward = round(total_reward - initiator_reward)

                    initiator_negotiator.satellite.accumulated_reward += initiator_reward
                    partner_negotiator.satellite.accumulated_reward += partner_reward

                    print(f"{initiator_negotiator.satellite.name} reward update: {initiator_negotiator.satellite.accumulated_reward-initiator_reward} -> {initiator_negotiator.satellite.accumulated_reward} (Earned: {total_reward} * {reward_percentage_init*100:.1f}% = {initiator_reward})")
                    print(f"{partner_negotiator.satellite.name} reward update: {partner_negotiator.satellite.accumulated_reward-partner_reward} -> {partner_negotiator.satellite.accumulated_reward} (Earned: {total_reward} * {(1-reward_percentage_init)*100:.1f}% = {partner_reward})")
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Failed to update memory and rewards - {str(e)}")

            # Collect negotiation details from all negotiators
            negotiation_details = {
                "memory_checks": [],
                "utility_calculations": [],
                "proposals": [],
                "responses": []
            }

            # Combine details from all negotiators
            if initiator_negotiator:
                details = initiator_negotiator.get_negotiation_details()
                negotiation_details["memory_checks"].extend(details["memory_checks"])
                # Only keep the final utility calculation for each phase
                utility_calcs = details["utility_calculations"]
                if utility_calcs:
                    # Group by phase and keep only the last calculation in each phase
                    phase_calcs = {}
                    for calc in utility_calcs:
                        time = calc["time"]
                        if time < 0.3:
                            phase = "early"
                        elif time < 0.7:
                            phase = "middle"
                        else:
                            phase = "late"
                        phase_calcs[phase] = calc
                    negotiation_details["utility_calculations"] = list(phase_calcs.values())
                negotiation_details["proposals"].extend(details["proposals"])
                negotiation_details["responses"].extend(details["responses"])

            for partner_negotiator in partner_negotiators:
                details = partner_negotiator.get_negotiation_details()
                negotiation_details["memory_checks"].extend(details["memory_checks"])
                # Only keep the final utility calculation for each phase
                utility_calcs = details["utility_calculations"]
                if utility_calcs:
                    # Group by phase and keep only the last calculation in each phase
                    phase_calcs = {}
                    for calc in utility_calcs:
                        time = calc["time"]
                        if time < 0.3:
                            phase = "early"
                        elif time < 0.7:
                            phase = "middle"
                        else:
                            phase = "late"
                        phase_calcs[phase] = calc
                    negotiation_details["utility_calculations"].extend(phase_calcs.values())
                negotiation_details["proposals"].extend(details["proposals"])
                negotiation_details["responses"].extend(details["responses"])

            # Sort all details by time
            for key in negotiation_details:
                if key == "utility_calculations":
                    # Sort utility calculations by phase (early, middle, late)
                    negotiation_details[key].sort(key=lambda x: (
                        0 if x["time"] < 0.3 else (1 if x["time"] < 0.7 else 2),
                        x["time"]
                    ))
                else:
                    negotiation_details[key].sort(key=lambda x: x["time"])

            negotiation_result = {
                "coalition": pref.preferred_satellites,
                "priority": pref.priority,
                "result": str(result),
                "agreement": agreement,
                "agreement_details": str(session.state.agreement) if agreement else None,
                "negotiation_details": negotiation_details
            }

            task_result["negotiations"].append(negotiation_result)

            if agreement:
                break

        results_dict["negotiation_results"].append(task_result)


def run_negotiation(negotiator_version: str, num_satellites: int, num_tasks: int, plot: bool = False, n_steps: int = 10):
    """Run the negotiation with the specified parameters."""
    print("\n=== Starting Satellite Negotiation ===")
    print(f"Negotiator: {negotiator_version}")
    print(f"Number of Satellites: {num_satellites}")
    print(f"Number of Tasks: {num_tasks}")
    print(f"Number of Steps: {n_steps}")
    print(f"Plot Negotiation: {'Yes' if plot else 'No'}")

    negotiator_class = get_negotiator(negotiator_version)

    satellites = create_satellites(num_satellites=num_satellites, cities=SIMPLE_CITIES)
    all_satellite_ids = [f"sat{i+1}" for i in range(num_satellites)]

    for sat in satellites:
        print(f"1. @#$@#$@#$@#$ {sat.memory_capacity}, {sat.available_memory}, {sat.accumulated_reward}")

    tasks = create_tasks(num_tasks=num_tasks, cities=SIMPLE_CITIES)

    for tsk in tasks:
        print(f"Reward cost of task {tsk.id}: {float(tsk.memory_required/tsk.reward_points):.2f}")

    coalition_tables = generate_coalition_tables(
        tasks=tasks,
        all_satellites=all_satellite_ids
    )

    all_negotiation_results = []

    for initiator_id in all_satellite_ids:
        print(f"\n=== Running negotiations with {initiator_id} as initiator ===")

        initiator_table = coalition_tables[initiator_id]
        print(f"Retrieved coalition table for {initiator_id}")

        task_preferences = {}
        for pref in initiator_table.preferences:
            if pref.task_id not in task_preferences:
                task_preferences[pref.task_id] = []
            task_preferences[pref.task_id].append(pref)

        print(f"Starting negotiations for {initiator_id}...")

        results_dict = create_results_dict(tasks, satellites, initiator_table, task_preferences)

        write_negotiation_results(negotiator_class, results_dict, task_preferences, tasks, satellites, plot=plot, n_steps=n_steps)

        all_negotiation_results.append(results_dict)

        print(f"Completed negotiations for {initiator_id}")

    total_memory_used = sum(sat.memory_capacity - sat.available_memory for sat in satellites)
    total_memory_capacity = sum(sat.memory_capacity for sat in satellites)
    average_utilization = (total_memory_used / total_memory_capacity) * 100 if total_memory_capacity > 0 else 0

    rewards = [sat.accumulated_reward for sat in satellites]
    gini_coefficient = gini(np.asarray(rewards))

    for sat in satellites:
        print(f"3. @#$@#$@#$@#$ {sat.memory_capacity}, {sat.available_memory}, {sat.accumulated_reward}")

    final_results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "satellites": all_negotiation_results[0]["satellites"],
        "tasks": all_negotiation_results[0]["tasks"],
        "coalition_tables": [result["coalition_table"] for result in all_negotiation_results],
        "negotiation_results": [result["negotiation_results"] for result in all_negotiation_results],
        "final_states": {
            satellite.name: {
                "initial_memory": satellite.memory_capacity,
                "final_available_memory": satellite.available_memory,
                "final_reward": satellite.accumulated_reward,
                "memory_utilization": f"{((satellite.memory_capacity - satellite.available_memory) / satellite.memory_capacity * 100):.1f}%",
                "memory_cost": f"{(satellite.memory_capacity - satellite.available_memory) / satellite.accumulated_reward:.2f}"
            }
            for satellite in satellites
        },
        "strategy_performance": {
            "average_memory_utilisation": f"{average_utilization:.2f}%",
            "average_reward_per_satellite": f"{sum(sat.accumulated_reward for sat in satellites) / num_satellites:.2f}",
            "average_memory_cost": f"{sum(sat.memory_capacity - sat.available_memory for sat in satellites) / sum(sat.accumulated_reward for sat in satellites):.2f}",
            "gini_coefficient": f"{gini_coefficient:.2f}"
        }
    }

    with open("negotiation_results.json", "w") as f:
        json.dump(final_results, f, indent=2)

    print("\n=== Negotiation Complete ===")
    print(f"Strategy Performance: {final_results['strategy_performance']}")
    print("Results have been written to negotiation_results.json")

def gini(rewards: np.ndarray) -> float:
    """Calculate the Gini coefficient of inequality for a given array of rewards.

    Args:
        rewards: A numpy array of reward points earned by satellites.

    Returns:
        The Gini coefficient (float between 0 and 1), where 0 is perfect equality.
    """
    if len(rewards) < 2:
        return 0.0  # No inequality with 0 or 1 element

    rewards = np.sort(rewards)  # Sort in ascending order
    n = len(rewards)
    index = np.arange(1, n + 1)

    total = np.sum(rewards)
    if total == 0:
        return 0.0

    sum_i_yi = np.sum(index * rewards)
    gini_coeff = (2 * sum_i_yi) / (n * total) - (n + 1) / n

    return max(0.0, gini_coeff)

def main():
    parser = argparse.ArgumentParser(description='Run satellite negotiations with customizable parameters.')

    parser.add_argument(
        '--negotiator', '-n',
        type=str,
        required=True,
        choices=list(NEGOTIATOR_REGISTRY.keys()),
        help='Negotiator version to use'
    )

    parser.add_argument(
        '--satellites', '-s',
        type=int,
        required=True,
        help='Number of satellites'
    )

    parser.add_argument(
        '--tasks', '-t',
        type=int,
        required=True,
        help='Number of tasks'
    )

    parser.add_argument(
        '--steps', '-st',
        type=int,
        default=10,
        help='Number of steps in each negotiation session (default: 10)'
    )

    parser.add_argument(
        '--plot', '-p',
        action='store_true',
        help='Plot negotiation results (default: False)'
    )

    args = parser.parse_args()

    run_negotiation(
        negotiator_version=args.negotiator,
        num_satellites=args.satellites,
        num_tasks=args.tasks,
        plot=args.plot,
        n_steps=args.steps
    )

if __name__ == "__main__":
    main()
