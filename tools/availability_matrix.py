"""
Tool: Availability Matrix Generator

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 29/05/2025
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import re
from textwrap import wrap
from MultiSatellitesNego.utils import generate_coverage_array, generate_coverage_console_table

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

assignments = [
  # sat1
  [
      {"task_id": 1, "tw_id": 0},
      {"task_id": 3, "tw_id": 1},
      {"task_id": 4, "tw_id": 0},
      {"task_id": 5, "tw_id": 0},
      {"task_id": 7, "tw_id": 1},
      {"task_id": 8, "tw_id": 0}
  ],

  # sat2
  [
      {"task_id": 2, "tw_id": 1},
      {"task_id": 3, "tw_id": 0},
      {"task_id": 4, "tw_id": 1},
      {"task_id": 6, "tw_id": 0},
      {"task_id": 9, "tw_id": 1},
      {"task_id": 10, "tw_id": 1}
  ],

  # sat3
  [
      {"task_id": 1, "tw_id": 1},
      {"task_id": 2, "tw_id": 0},
      {"task_id": 4, "tw_id": 0},
      {"task_id": 6, "tw_id": 1},
      {"task_id": 7, "tw_id": 1},
      {"task_id": 8, "tw_id": 0},
      {"task_id": 10, "tw_id": 1}
  ],

  # sat4
  [
      {"task_id": 1, "tw_id": 0},
      {"task_id": 4, "tw_id": 1},
      {"task_id": 5, "tw_id": 1},
      {"task_id": 8, "tw_id": 1},
      {"task_id": 10, "tw_id": 0},
      {"task_id": 16, "tw_id": 1}
  ],

  # sat5
  [
      {"task_id": 1, "tw_id": 1},
      {"task_id": 2, "tw_id": 0},
      {"task_id": 3, "tw_id": 1},
      {"task_id": 7, "tw_id": 0},
      {"task_id": 8, "tw_id": 1},
      {"task_id": 9, "tw_id": 0},
      {"task_id": 10, "tw_id": 0}
  ],

  # sat6
  [
      {"task_id": 1, "tw_id": 0},
      {"task_id": 4, "tw_id": 0},
      {"task_id": 5, "tw_id": 0},
      {"task_id": 7, "tw_id": 1},
      {"task_id": 15, "tw_id": 0},
      {"task_id": 16, "tw_id": 0}
  ],

  # sat7
  [
      {"task_id": 2, "tw_id": 1},
      {"task_id": 3, "tw_id": 0},
      {"task_id": 4, "tw_id": 1},
      {"task_id": 5, "tw_id": 1},
      {"task_id": 9, "tw_id": 1},
      {"task_id": 10, "tw_id": 1}
  ],

  # sat8
  [
      {"task_id": 1, "tw_id": 1},
      {"task_id": 2, "tw_id": 0},
      {"task_id": 4, "tw_id": 0},
      {"task_id": 6, "tw_id": 1},
      {"task_id": 7, "tw_id": 1},
      {"task_id": 8, "tw_id": 1},
      {"task_id": 10, "tw_id": 1}
  ],

    # sat9
    [
        {"task_id": 2, "tw_id": 1},
        {"task_id": 3, "tw_id": 0},
        {"task_id": 8, "tw_id": 1},
        {"task_id": 9, "tw_id": 1},
        {"task_id": 10, "tw_id": 0},
        {"task_id": 15, "tw_id": 1},
        {"task_id": 18, "tw_id": 0}
    ],

    # sat10
    [
        {"task_id": 7, "tw_id": 0},
        {"task_id": 8, "tw_id": 1},
        {"task_id": 9, "tw_id": 0},
        {"task_id": 12, "tw_id": 0},
        {"task_id": 15, "tw_id": 0},
        {"task_id": 20, "tw_id": 0}
    ],

    # sat11
    [
        {"task_id": 1, "tw_id": 0},
        {"task_id": 4, "tw_id": 0},
        {"task_id": 5, "tw_id": 0},
        {"task_id": 7, "tw_id": 1},
        {"task_id": 15, "tw_id": 0},
        {"task_id": 16, "tw_id": 0}
    ],

    # sat12
    [
        {"task_id": 2, "tw_id": 1},
        {"task_id": 3, "tw_id": 0},
        {"task_id": 6, "tw_id": 0},
        {"task_id": 9, "tw_id": 1},
        {"task_id": 19, "tw_id": 0},
        {"task_id": 20, "tw_id": 1}
    ],

    # sat13
    [
        {"task_id": 1, "tw_id": 1},
        {"task_id": 2, "tw_id": 0},
        {"task_id": 7, "tw_id": 1},
        {"task_id": 12, "tw_id": 1},
        {"task_id": 16, "tw_id": 0},
        {"task_id": 17, "tw_id": 1},
        {"task_id": 19, "tw_id": 1}
    ],

    # sat14
    [
        {"task_id": 2, "tw_id": 1},
        {"task_id": 8, "tw_id": 1},
        {"task_id": 14, "tw_id": 1},
        {"task_id": 15, "tw_id": 1},
        {"task_id": 19, "tw_id": 0},
        {"task_id": 20, "tw_id": 0}
    ],

    # sat15
    [
        {"task_id": 2, "tw_id": 0},
        {"task_id": 7, "tw_id": 0},
        {"task_id": 9, "tw_id": 0},
        {"task_id": 11, "tw_id": 0},
        {"task_id": 15, "tw_id": 0},
        {"task_id": 18, "tw_id": 1},
        {"task_id": 20, "tw_id": 0}
    ],

    # sat16
    [
        {"task_id": 1, "tw_id": 0},
        {"task_id": 5, "tw_id": 0},
        {"task_id": 13, "tw_id": 0},
        {"task_id": 14, "tw_id": 0},
        {"task_id": 16, "tw_id": 0},
        {"task_id": 19, "tw_id": 1}
    ],

    # sat17
    [
        {"task_id": 3, "tw_id": 0},
        {"task_id": 5, "tw_id": 1},
        {"task_id": 12, "tw_id": 1},
        {"task_id": 13, "tw_id": 1},
        {"task_id": 17, "tw_id": 0},
        {"task_id": 19, "tw_id": 0}
    ],

    # sat18
    [
        {"task_id": 1, "tw_id": 1},
        {"task_id": 2, "tw_id": 0},
        {"task_id": 14, "tw_id": 0},
        {"task_id": 17, "tw_id": 1},
        {"task_id": 18, "tw_id": 0},
        {"task_id": 19, "tw_id": 1},
        {"task_id": 20, "tw_id": 1}
    ],

    # sat19
    [
        {"task_id": 1, "tw_id": 0},
        {"task_id": 3, "tw_id": 0},
        {"task_id": 5, "tw_id": 1},
        {"task_id": 13, "tw_id": 1},
        {"task_id": 17, "tw_id": 0},
        {"task_id": 18, "tw_id": 0},
        {"task_id": 20, "tw_id": 0}
    ],

    # sat20
    [
        {"task_id": 2, "tw_id": 0},
        {"task_id": 7, "tw_id": 0},
        {"task_id": 9, "tw_id": 0},
        {"task_id": 10, "tw_id": 0},
        {"task_id": 11, "tw_id": 1},
        {"task_id": 13, "tw_id": 0}
    ]
]

class CompactArrayEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compact_keys = {'availability_matrix'}

    def iterencode(self, o, _one_shot=False):
        def _compact(obj):
            if isinstance(obj, dict):
                return {k: _compact(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                # Check if it's inside a dict with a compact key
                # This is a bit hacky, but works
                return obj
            else:
                return obj

        chunks = super().iterencode(o, _one_shot)
        json_str = ''.join(chunks)

        # Compact the arrays for the specified keys
        import re
        # Finds the availability_matrix arrays and compacts them
        def compact_array(match):
            arr = match.group(1)
            arr = arr.replace('\n', '').replace(' ', '')
            arr = re.sub(r',+', ',', arr)
            return f'"availability_matrix": [{arr}]'

        json_str = re.sub(
            r'"availability_matrix": \[(.*?)\]',
            lambda m: f'"availability_matrix": [{",".join(m.group(1).split())}]',
            json_str,
            flags=re.DOTALL
        )
        return [json_str]

def main():

    if len(sys.argv) < 2:
        print("Please specify the setup JSON file\n")
        sys.exit(1)

    json_file = sys.argv[1]
    with open(json_file, 'r') as file:
        data = json.load(file)

    tsk_list = data['tasks']

    am = generate_coverage_array(tsk_list, assignments)

    satellites = data["satellites"]
    for i, satellite in enumerate(satellites):
        if i < len(am):
            satellite["availability_matrix"] = am[i]
        else:
            print(f"Warning: No coverage data for satellite {satellite['name']}")

    json_str = json.dumps(data, indent=4)

    # Replace availability_matrix content with a compact version
    def compact_matrix(match):
        numbers = re.findall(r'\d+', match.group(0))
        compact = ', '.join(numbers)
        return f'"availability_matrix": [{compact}]'

    # Replace all availability_matrix arrays with compact versions
    json_str = re.sub(
        r'"availability_matrix":\s*\[[^\]]*\]',
        compact_matrix,
        json_str
    )

    with open(json_file, 'w') as f:
        f.write(json_str)

    print(f"Availability matrices updated and saved to '{json_file}'")

    generate_coverage_console_table(satellites, tsk_list)


if __name__ == "__main__":
    main()
