"""
Tool: Coalition Table Generator

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 29/05/2025
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from MultiSatellitesNego.utils import generate_coalition_table

def main():
    if len(sys.argv) < 3:
        print("Usage: python coalition_table_generator.py <path_to_json_file> <initiator_satellite_name>")
        sys.exit(1)


    json_file = sys.argv[1]
    with open(json_file, 'r') as file:
        data = json.load(file)

    initiator_satellite_name = sys.argv[2]

    tasks = data['tasks']
    satellites = data['satellites']

    ret = generate_coalition_table(initiator_satellite_name, satellites, tasks)
    print(f"ret: {ret}")

if __name__ == "__main__":
    main()
