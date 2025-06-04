"""
Tool: Availability Matrix Interpreter

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 29/05/2025
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from MultiSatellitesNego.utils import interpret_satellite_availability

tasks = [
    {
      "id": 1,
      "location_index": "1",
      "time_window": [{"start_time": 14, "end_time": 17}, {"start_time": 21, "end_time": 24}],
      "reward_points": 533,
      "memory_required": 954
    },
    {
      "id": 2,
      "location_index": "2",
      "time_window": [{"start_time": 1, "end_time": 2}, {"start_time": 9, "end_time": 10}],
      "reward_points": 402,
      "memory_required": 473
    },
    {
      "id": 3,
      "location_index": "3",
      "time_window": [{"start_time": 9, "end_time": 10}, {"start_time": 14, "end_time": 15}],
      "reward_points": 791,
      "memory_required": 793
    },
    {
      "id": 4,
      "location_index": "4",
      "time_window": [{"start_time": 9, "end_time": 12}, {"start_time": 21, "end_time": 24}],
      "reward_points": 545,
      "memory_required": 160
    },
    {
      "id": 5,
      "location_index": "5",
      "time_window": [{"start_time": 7, "end_time": 9}, {"start_time": 13, "end_time": 15}, {"start_time": 19, "end_time": 21}],
      "reward_points": 749,
      "memory_required": 570
    },
    {
      "id": 6,
      "location_index": "6",
      "time_window": [{"start_time": 9, "end_time": 11}, {"start_time": 21, "end_time": 23}],
      "reward_points": 768,
      "memory_required": 1002
    },
    {
      "id": 7,
      "location_index": "7",
      "time_window": [{"start_time": 12, "end_time": 14}, {"start_time": 0, "end_time": 2}],
      "reward_points": 967,
      "memory_required": 1562
    },
    {
      "id": 8,
      "location_index": "8",
      "time_window": [{"start_time": 15, "end_time": 16}, {"start_time": 3, "end_time": 4}],
      "reward_points": 854,
      "memory_required": 1234
    },
    {
      "id": 9,
      "location_index": "9",
      "time_window": [{"start_time": 18, "end_time": 19}, {"start_time": 6, "end_time": 7}],
      "reward_points": 677,
      "memory_required": 1567
    },
    {
      "id": 10,
      "location_index": "10",
      "time_window": [{"start_time": 8, "end_time": 9}, {"start_time": 20, "end_time": 22}],
      "reward_points": 344,
      "memory_required": 999
    }
]

sat = {
    "name": "sat1",
    "memory_capacity": 2945,
    "available_memory": 2945,
    "accumulated_reward": 0,
    "availability_matrix": [
                0, 0, 0, 0, 0, 0, 0, 7,
                0, 0, 0, 11, 12, 13, 14, 15,
                16, 17, 18, 19, 20, 21, 22, 23,
                24, 25, 26, 27, 5, 5, 30, 31,
                32, 33, 34, 35, 36, 37, 3, 3,
                40, 4, 42, 43, 44, 45, 46, 47,
                48, 5, 50, 51, 52, 53, 54, 55,
                56, 1, 58, 59, 60, 61, 8, 63,
                64, 65, 66, 67, 68, 69, 70, 71,
                72, 73, 74, 75, 76, 77, 78, 79,
                80, 81, 82, 83, 84, 85, 86, 87,
                88, 89, 90, 91, 92, 93, 94, 95
            ]
}

def main():

    ret = interpret_satellite_availability(sat, tasks)
    print(f"Result: {ret}")


if __name__ == "__main__":
    main()