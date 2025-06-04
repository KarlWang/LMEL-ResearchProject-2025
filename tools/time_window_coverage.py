"""
Tool: Time Window Checker

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 29/05/2025
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from MultiSatellitesNego.utils import check_task_coverage, is_satellite_available_for_task

satellites = [
    {
        "name": "sat1",
        "availability_matrix": [
            0, 0, 2, 0, 0, 0, 0, 0,
            8, 9, 2, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            24, 25, 26, 27, 5, 5, 30, 31,
            32, 33, 34, 35, 36, 37, 3, 3,
            40, 4, 42, 43, 44, 45, 46, 47,
            48, 5, 50, 51, 52, 53, 54, 55,
            56, 1, 58, 59, 60, 61, 62, 63,
            8, 65, 66, 67, 68, 69, 70, 71,
            72, 73, 74, 75, 76, 77, 78, 79,
            80, 81, 82, 83, 84, 85, 86, 87,
            88, 8, 90, 1, 92, 93, 94, 95
        ]
    },
    {
        "name": "sat4",
        "availability_matrix": [
            0, 2, 2, 0, 0, 0, 0, 0,
            8, 9, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            24, 25, 26, 27, 5, 5, 30, 31,
            32, 33, 34, 35, 36, 37, 3, 3,
            40, 4, 42, 43, 44, 45, 46, 47,
            48, 5, 50, 51, 52, 53, 54, 55,
            56, 1, 58, 59, 60, 61, 62, 63,
            8, 65, 66, 67, 68, 69, 70, 71,
            72, 73, 74, 75, 76, 77, 78, 79,
            80, 81, 82, 83, 84, 85, 86, 87,
            88, 8, 90, 1, 92, 93, 94, 95
        ]
    },
    {
        "name": "sat7",
        "availability_matrix": [
            0, 0, 0, 0, 0, 0, 0, 0,
            8, 9, 10, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            24, 25, 26, 27, 5, 5, 30, 31,
            32, 33, 34, 35, 36, 37, 3, 3,
            40, 4, 42, 43, 44, 45, 46, 47,
            48, 49, 2, 51, 52, 53, 54, 55,
            56, 1, 58, 59, 60, 61, 62, 63,
            8, 65, 66, 67, 68, 69, 70, 71,
            72, 73, 74, 75, 76, 77, 78, 79,
            80, 81, 82, 83, 84, 85, 86, 87,
            88, 8, 90, 1, 92, 93, 94, 95
        ]
    }
]

tasks = [
   {
        "id": 1,
        "location_index": "2",
        "time_window": [{"start_time": 0, "end_time": 1}, {"start_time": 12, "end_time": 13}]
    }
]

def main():

    if len(sys.argv) < 2:
        sat_list = satellites
        tsk_list = tasks
    else:
        json_file = sys.argv[1]
        with open(json_file, 'r') as file:
            data = json.load(file)

        tsk_list = data['tasks']
        sat_list = data['satellites']

    print(f"Check if a satellite available for a task:")
    print(f"{is_satellite_available_for_task(sat_list[2], tsk_list[0])}")

    print('Coverage Detailed Information')
    ret = check_task_coverage(tsk_list, sat_list)
    print(f"ret: {ret}")

if __name__ == "__main__":
    main()