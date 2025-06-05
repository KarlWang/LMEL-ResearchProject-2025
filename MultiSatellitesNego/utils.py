"""
Title: Utils

The helper functions

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 26/05/2025
"""

import random
import json

def calculate_average_memory_utilisation(satellites):
    """
    Calculate the average memory utilisation across all satellites.
    Returns a tuple of (average_utilisation, total_used, total_available)
    """
    total_used = 0
    total_available = 0

    for sat in satellites:
        used_memory = sat['memory_capacity'] - sat['available_memory']
        total_used += used_memory
        total_available += sat['memory_capacity']

    if total_available == 0:
        return 0, 0, 0

    average_utilisation = (total_used / total_available) * 100
    return average_utilisation, total_used, total_available


def calculate_average_reward(satellites):
    """
    Calculate the average reward points across all satellites.
    Returns a tuple of (average_reward, total_reward, num_satellites)
    """
    total_reward = 0
    num_satellites = len(satellites)

    for sat in satellites:
        total_reward += sat['accumulated_reward']

    if num_satellites == 0:
        return 0, 0, 0

    average_reward = total_reward / num_satellites
    return average_reward, total_reward, num_satellites


def calculate_average_negotiation_rounds(stage1_results, stage2_results=None):
    """
    Calculate the average number of negotiation rounds across all successful negotiations
    from both Stage 1 and Stage 2.
    Returns a tuple of (average_rounds, total_rounds, num_negotiations)
    """
    total_rounds = 0
    num_negotiations = 0

    # Count Stage 1 negotiations
    for result in stage1_results['negotiation_results']:
        if result['agreement_reached']:
            total_rounds += result['rounds']
            num_negotiations += 1

    # Count Stage 2 negotiations
    if stage2_results:
        for result in stage2_results['negotiation_results']:
            if result['agreement_reached']:
                total_rounds += result['rounds']
                num_negotiations += 1

    if num_negotiations == 0:
        return 0, 0, 0

    average_rounds = total_rounds / num_negotiations
    return average_rounds, total_rounds, num_negotiations


def calculate_negotiation_success_rate(stage1_results, stage2_results=None):
    """
    Calculate the success rate of negotiations across both Stage 1 and Stage 2.
    Returns a tuple of (success_rate, successful_negotiations, total_negotiations)
    """
    successful_negotiations = 0
    total_negotiations = 0

    # Count Stage 1 negotiations
    for result in stage1_results['negotiation_results']:
        total_negotiations += 1
        if result['agreement_reached']:
            successful_negotiations += 1

    # Count Stage 2 negotiations
    if stage2_results:
        for result in stage2_results['negotiation_results']:
            total_negotiations += 1
            if result['agreement_reached']:
                successful_negotiations += 1

    # Add availability checks to total negotiations
    if 'availability_checks' in stage1_results:
        total_negotiations += stage1_results['availability_checks']
    if stage2_results and 'availability_checks' in stage2_results:
        total_negotiations += stage2_results['availability_checks']

    if total_negotiations == 0:
        return 0, 0, 0

    success_rate = (successful_negotiations / total_negotiations) * 100
    return success_rate, successful_negotiations, total_negotiations

def is_satellite_available_for_task(satellite, task):
    # Check coverage for this task and satellite
    coverage_details = check_task_coverage([task], [satellite])
    task_id = task["id"]
    windows_coverage = coverage_details.get(task_id, {}).get("time_windows_coverage", [])

    for window_info in windows_coverage:
        if window_info["covered"]:
            return window_info["window_index"]
    return -1


def check_task_coverage(tasks, satellites):
    results = {}
    for task in tasks:
        task_id = task["id"]
        task_loc = int(task["location_index"])
        task_result = {
            "time_windows_coverage": [],
            "fully_covered": True
        }

        for window_index, window in enumerate(task["time_window"]):
            start = window["start_time"]
            end = window["end_time"]
            start_slot = start * 4
            end_slot = end * 4
            window_covered = False
            covered_slots = []
            covered_satellites = []

            for slot in range(start_slot, end_slot):
                for satellite in satellites:
                    if satellite["availability_matrix"][slot] == task_loc:
                        window_covered = True
                        covered_slots.append(slot)
                        covered_satellites.append(satellite["name"])
                        break  # Stop checking satellites for this slot
                if window_covered:
                    break  # Stop checking slots if coverage found

            if not window_covered:
                task_result["fully_covered"] = False

            task_result["time_windows_coverage"].append({
                "window_index": window_index,
                "start_time": start,
                "end_time": end,
                "covered": window_covered,
                "covered_slots": covered_slots,
                "covered_satellites": covered_satellites
            })

        results[task_id] = task_result
    return results

def format_coverage_array(coverage):
    """
    Formats a coverage array with 8 elements per row for better readability.

    Args:
        coverage (list): 96-element coverage array

    Returns:
        str: Formatted string with 8 elements per row, comma-separated, with trailing commas except for the last row
    """
    rows = []
    for i in range(0, len(coverage), 8):
        row = coverage[i:i+8]
        # Add trailing comma for all rows except the last one
        if i + 8 < len(coverage):
            rows.append(",".join(map(str, row)) + ",")
        else:
            rows.append(",".join(map(str, row)))
    return "\n".join(rows)

def generate_coverage_array(tasks, assignments_list):
    """
    Generates multiple 96-slot coverage arrays by placing task locations in random slots
    within their specified time windows.

    Args:
        tasks (list): List of tasks (each with 'id', 'location_index', 'time_window')
        assignments_list (list): List of assignment lists, where each assignment list contains
                               dictionaries of {"task_id": X, "tw_id": Y} specifying which
                               time window indices to use for each task

    Returns:
        list: List of 96-element arrays, each representing coverage for one assignment list
    """
    task_dict = {task["id"]: task for task in tasks}  # Faster lookup
    coverage_arrays = []

    for assignments in assignments_list:
        coverage = [0] * 96  # Initialize all slots to 0 (no coverage)

        for assignment in assignments:
            task = task_dict.get(assignment["task_id"])
            if not task:
                continue

            try:
                window = task["time_window"][assignment["tw_id"]]
            except IndexError:
                continue  # Skip invalid time window indices

            start_slot = window["start_time"] * 4
            end_slot = window["end_time"] * 4

            # Validate slot range
            if 0 <= start_slot < end_slot <= 96:
                # Pick a random 15-minute slot in this window
                chosen_slot = random.randint(start_slot, end_slot - 1)
                coverage[chosen_slot] = int(task["location_index"])

        coverage_arrays.append(coverage)

        # Print formatted coverage array
        print(f"\nCoverage Array {len(coverage_arrays)}:")
        print(format_coverage_array(coverage))

    return coverage_arrays

def interpret_satellite_availability(satellite, tasks):
    """
    For a given satellite and list of tasks, outputs which task's which time window(s)
    this satellite is available for, including location and time window indices.
    """
    results = {}
    availability = satellite["availability_matrix"]

    for task in tasks:
        task_id = task["id"]
        location_index = int(task["location_index"])
        results[task_id] = []

        for tw_idx, window in enumerate(task["time_window"]):
            start_slot = window["start_time"] * 4
            end_slot = window["end_time"] * 4
            # Check if any slot in this window matches the task's location
            for slot in range(start_slot, end_slot):
                if availability[slot] == location_index:
                    results[task_id].append({
                        "time_window_index": tw_idx,
                        "location_index": location_index,
                        "time_window": {"start_time": window["start_time"], "end_time": window["end_time"]}
                    })
                    break  # Only need to report the window once if any slot matches

        # Remove empty entries for tasks with no available windows
        if not results[task_id]:
            results.pop(task_id)

    return results

def generate_coverage_markdown_table(satellites, tasks):
    """
    Generates a Markdown table showing which satellites cover each time window of each task.
    Each row: task id | satellites for time_window[0] | satellites for time_window[1] | ...
    """
    max_windows = max(len(task["time_window"]) for task in tasks)
    header = ["Task ID"] + [f"Time Window {i}" for i in range(max_windows)]
    md_lines = [" | ".join(header), " | ".join(["---"] * len(header))]

    for task in tasks:
        row = [str(task["id"])]
        task_loc = int(task["location_index"])
        num_windows = len(task["time_window"])

        for tw_idx in range(max_windows):
            if tw_idx < num_windows:
                window = task["time_window"][tw_idx]
                start_slot = window["start_time"] * 4
                end_slot = window["end_time"] * 4
                covering_sats = [
                    sat["name"]
                    for sat in satellites
                    if any(sat["availability_matrix"][slot] == task_loc for slot in range(start_slot, end_slot))
                ]
                row.append(", ".join(covering_sats) if covering_sats else "-")
            else:
                row.append("-")
        md_lines.append(" | ".join(row))

    return "\n".join(md_lines)

def generate_coverage_console_table(satellites, tasks):
    """
    Prints a console-friendly table showing which satellites cover each time window of each task.
    Each row: task id | satellites for time_window[0] | satellites for time_window[1] | ...
    """
    max_windows = max(len(task["time_window"]) for task in tasks)
    headers = ["Task ID"] + [f"Time Window {i}" for i in range(max_windows)]

    data = []
    for task in tasks:
        row = [str(task["id"])]
        task_loc = int(task["location_index"])
        num_windows = len(task["time_window"])
        for tw_idx in range(max_windows):
            if tw_idx < num_windows:
                window = task["time_window"][tw_idx]
                start_slot = window["start_time"] * 4
                end_slot = window["end_time"] * 4
                covering_sats = [
                    sat["name"]
                    for sat in satellites
                    if any(sat["availability_matrix"][slot] == task_loc for slot in range(start_slot, end_slot))
                ]
                cell = ", ".join(covering_sats) if covering_sats else "-"
                row.append(cell)
            else:
                row.append("-")
        data.append(row)

    col_widths = [max(len(str(cell)) for cell in col) for col in zip(headers, *data)]

    def format_row(row):
        return " | ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths))

    print(format_row(headers))
    print("-+-".join("-" * width for width in col_widths))
    for row in data:
        print(format_row(row))

def check_task_coverage_detailed(tasks, satellites):
    results = {}
    for task in tasks:
        task_id = task["id"]
        task_loc = int(task["location_index"])
        task_result = {
            "time_windows_coverage": [],
            "fully_covered": True
        }
        for window_index, window in enumerate(task["time_window"]):
            start = window["start_time"]
            end = window["end_time"]
            start_slot = start * 4
            end_slot = end * 4
            window_covered = False
            for slot in range(start_slot, end_slot):
                slot_covered = False
                for satellite in satellites:
                    if satellite["availability_matrix"][slot] == task_loc:
                        slot_covered = True
                        break
                if slot_covered:
                    window_covered = True
                    break
            if not window_covered:
                task_result["fully_covered"] = False
            task_result["time_windows_coverage"].append({
                "window_index": window_index,
                "start_time": start,
                "end_time": end,
                "covered": window_covered
            })
        results[task_id] = task_result
    return results

def generate_coalition_table(initiator_name, satellites, tasks):
    """
    For each task, find all satellites (excluding initiator) that, together with the initiator,
    can fully cover all time windows. Rank partners by memory_capacity (descending).
    Output a console-friendly Python dict.
    """
    # Find the initiator satellite
    initiator = next((sat for sat in satellites if sat["name"] == initiator_name), None)
    if not initiator:
        raise ValueError(f"Initiator satellite {initiator_name} not found in satellites list")

    coalition_table = {
        "satellite": initiator_name,
        "preferences": []
    }
    # Exclude initiator from partners
    partners = [sat for sat in satellites if sat["name"] != initiator_name]
    for task in tasks:
        partner_candidates = []
        for partner in partners:
            sats_for_check = [initiator, partner]
            coverage = check_task_coverage_detailed([task], sats_for_check)
            if coverage[task["id"]]["fully_covered"]:
                partner_candidates.append(partner)
        # Sort by memory_capacity descending
        partner_candidates.sort(key=lambda s: s["memory_capacity"], reverse=True)
        for priority, partner in enumerate(partner_candidates, start=1):
            coalition_table["preferences"].append({
                "task_id": task["id"],
                "preferred_satellites": [partner["name"]],
                "priority": priority
            })
    # Print with double quotes using json
    print(json.dumps(coalition_table, indent=4))

# Example usage:
# generate_coalition_table(initiator, satellites, tasks)

def calculate_task_allocation_success_rate(stage1_results, stage2_results=None):
    """
    Calculate the success rate of task allocations across both Stage 1 and Stage 2.
    A task is considered successfully allocated if it has a partner in Stage 2.

    Returns a tuple of (success_rate, successfully_allocated_tasks, total_tasks)
    """
    total_tasks = len(stage1_results['task_assignments'])
    successfully_allocated_tasks = 0

    # Count tasks that were successfully allocated in Stage 1
    for task_id, assigned_satellite in stage1_results['task_assignments'].items():
        if assigned_satellite is not None:
            # Check if this task got a partner in Stage 2
            if stage2_results:
                for result in stage2_results['negotiation_results']:
                    if result['task_id'] == task_id and result['agreement_reached']:
                        successfully_allocated_tasks += 1
                        break
            else:
                # If no Stage 2 results, count Stage 1 assignments as successful
                successfully_allocated_tasks += 1

    if total_tasks == 0:
        return 0, 0, 0

    success_rate = (successfully_allocated_tasks / total_tasks) * 100
    return success_rate, successfully_allocated_tasks, total_tasks
