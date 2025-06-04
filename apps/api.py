"""
Title: Traditional Strategy

This script analyse the traditional task allocation strategy,
which is a 2-stage, auction based method

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 13/04/2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
from nego_app import create_results_dict, write_negotiation_results
from MultiSatellitesNego.task_generator import create_tasks, Task
from MultiSatellitesNego.satellite_generator import create_satellites, Satellite
from MultiSatellitesNego.coalition_generator import generate_coalition_tables, CoalitionTable, CoalitionPreference
from MultiSatellitesNego.negotiators import get_negotiator, NEGOTIATOR_REGISTRY
from MultiSatellitesNego.negotiation_config import SIMPLE_CITIES

app = FastAPI(
    title="Satellite Negotiation API",
    description="API for managing satellite negotiations and coalition formations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.last_results = None
app.satellites = None
app.tasks = None
app.coalition_tables = None

class NegotiationRequest(BaseModel):
    num_satellites: int = 3
    num_tasks: int = 5
    negotiator_version: str = "v05"
    initiator: str = ""

class NegotiationResponse(BaseModel):
    message: str
    timestamp: str
    results: Dict[str, Any]

class SatelliteResponse(BaseModel):
    message: str
    timestamp: str
    satellites: List[Dict[str, Any]]

class TaskResponse(BaseModel):
    message: str
    timestamp: str
    tasks: List[Dict[str, Any]]

class SaveDataRequest(BaseModel):
    filename: str

class LoadDataRequest(BaseModel):
    filename: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Satellite Negotiation API"}

@app.post("/create-satellites", response_model=SatelliteResponse)
async def create_satellites_endpoint(request: NegotiationRequest):
    try:
        satellites = create_satellites(num_satellites=request.num_satellites, cities=SIMPLE_CITIES)
        app.satellites = satellites

        all_satellite_ids = [f"sat{i+1}" for i in range(request.num_satellites)]
        app.coalition_tables = generate_coalition_tables(
            tasks=app.tasks if app.tasks else [],
            all_satellites=all_satellite_ids
        )

        satellites_dict = [
            {
                "name": sat.name,
                "memory_capacity": sat.memory_capacity,
                "available_memory": sat.available_memory,
                "coalition_table": {
                    "satellite": sat.name,
                    "preferences": [
                        {
                            "task_id": pref.task_id,
                            "preferred_satellites": pref.preferred_satellites,
                            "priority": pref.priority
                        }
                        for pref in app.coalition_tables[sat.name].preferences
                    ]
                }
            }
            for sat in satellites
        ]

        return SatelliteResponse(
            message="Satellites created successfully",
            timestamp=datetime.now().isoformat(),
            satellites=satellites_dict
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-tasks", response_model=TaskResponse)
async def create_tasks_endpoint(request: NegotiationRequest):
    try:
        tasks = create_tasks(num_tasks=request.num_tasks, cities=SIMPLE_CITIES)
        app.tasks = tasks

        tasks_dict = [
            {
                "id": task.id,
                "location_index": task.location_index,
                "time_window": task.time_window,
                "reward_points": task.reward_points,
                "memory_required": task.memory_required
            }
            for task in tasks
        ]

        return TaskResponse(
            message="Tasks created successfully",
            timestamp=datetime.now().isoformat(),
            tasks=tasks_dict
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start-negotiation", response_model=NegotiationResponse)
async def start_negotiation(request: NegotiationRequest):
    try:
        print(f"Starting negotiation with parameters:")
        print(f"Number of satellites: {request.num_satellites}")
        print(f"Number of tasks: {request.num_tasks}")
        print(f"Initiator: {request.initiator if request.initiator else 'All satellites'}")

        if not app.satellites or not app.tasks:
            print("Error: Satellites or tasks not created")
            raise HTTPException(status_code=400, detail="Satellites and tasks must be created first")

        app.last_results = None

        print(f"Getting negotiator version: {request.negotiator_version}")
        negotiator = get_negotiator(request.negotiator_version)

        if not app.coalition_tables:
            print("Error: Coalition tables not found")
            raise HTTPException(status_code=400, detail="Coalition tables must be created first")

        if request.initiator:
            # Single initiator mode
            if request.initiator not in app.coalition_tables:
                print(f"Error: Initiator {request.initiator} not found in coalition tables")
                raise HTTPException(status_code=400, detail=f"Initiator {request.initiator} not found in coalition tables")

            initiator_table = app.coalition_tables[request.initiator]
            print(f"Got initiator table for {request.initiator}")

            # Group preferences by task ID
            task_preferences = {}
            for pref in initiator_table.preferences:
                if pref.task_id not in task_preferences:
                    task_preferences[pref.task_id] = []
                task_preferences[pref.task_id].append(pref)

            print(f"Created task preferences for {len(task_preferences)} tasks")

            results_dict = create_results_dict(app.tasks, app.satellites, initiator_table, task_preferences)
            print("Created results dictionary")

            write_negotiation_results(negotiator, results_dict, task_preferences, app.tasks, app.satellites)
            print("Added negotiation results")

            app.last_results = results_dict

        else:
            # Multi-initiator mode
            print("Starting multi-initiator negotiations")
            all_satellite_ids = [sat.name for sat in app.satellites]
            all_negotiation_results = []

            for initiator_id in all_satellite_ids:
                print(f"\n=== Running negotiations with {initiator_id} as initiator ===")

                # Get the coalition table for this initiator
                initiator_table = app.coalition_tables[initiator_id]
                print(f"Retrieved coalition table for {initiator_id}")

                task_preferences = {}
                for pref in initiator_table.preferences:
                    if pref.task_id not in task_preferences:
                        task_preferences[pref.task_id] = []
                    task_preferences[pref.task_id].append(pref)

                print(f"Starting negotiations for {initiator_id}...")

                results_dict = create_results_dict(app.tasks, app.satellites, initiator_table, task_preferences)

                write_negotiation_results(negotiator, results_dict, task_preferences, app.tasks, app.satellites)

                all_negotiation_results.append(results_dict)

                print(f"Completed negotiations for {initiator_id}")

            final_results = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "satellites": all_negotiation_results[0]["satellites"],
                "tasks": all_negotiation_results[0]["tasks"],
                "coalition_tables": [result["coalition_table"] for result in all_negotiation_results],
                "negotiation_results": [result["negotiation_results"] for result in all_negotiation_results]
            }

            app.last_results = final_results
            results_dict = final_results

        return NegotiationResponse(
            message="Negotiation completed successfully",
            timestamp=datetime.now().isoformat(),
            results=results_dict
        )
    except Exception as e:
        print(f"Error in start_negotiation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/negotiation-results")
async def get_negotiation_results():
    try:
        if app.last_results is None:
            raise HTTPException(status_code=404, detail="No negotiation results found")
        return app.last_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-data")
async def save_data(request: SaveDataRequest):
    try:
        if app.satellites is None or app.tasks is None:
            raise HTTPException(status_code=400, detail="No data to save. Please create satellites and tasks first")

        data = {
            "satellites": [
                {
                    "name": sat.name,
                    "memory_capacity": sat.memory_capacity,
                    "available_memory": sat.available_memory,
                    "coalition_table": {
                        "satellite": sat.name,
                        "preferences": [
                            {
                                "task_id": pref.task_id,
                                "preferred_satellites": pref.preferred_satellites,
                                "priority": pref.priority
                            }
                            for pref in app.coalition_tables[sat.name].preferences
                        ]
                    }
                }
                for sat in app.satellites
            ],
            "tasks": [
                {
                    "id": task.id,
                    "location": task.location,
                    "start_time": task.start_time,
                    "duration": task.duration,
                    "reward_points": task.reward_points,
                    "memory_required": task.memory_required
                }
                for task in app.tasks
            ]
        }

        # Ensure the data directory exists
        os.makedirs("saved_data", exist_ok=True)

        filepath = os.path.join("saved_data", f"{request.filename}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        return {"message": f"Data saved successfully to {filepath}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load-data")
async def load_data(request: LoadDataRequest):
    try:
        filepath = os.path.join("saved_data", f"{request.filename}.json")
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"File {filepath} not found")

        with open(filepath, "r") as f:
            data = json.load(f)

        tasks = []
        for task_data in data["tasks"]:
            task = Task(
                id=task_data["id"],
                location=task_data["location"],
                start_time=task_data["start_time"],
                duration=task_data["duration"],
                reward_points=task_data["reward_points"],
                memory_required=task_data["memory_required"]
            )
            tasks.append(task)
        app.tasks = tasks

        satellites = []
        for sat_data in data["satellites"]:
            satellite = Satellite(
                name=sat_data["name"],
                memory_capacity=sat_data["memory_capacity"]
            )
            satellites.append(satellite)
        app.satellites = satellites

        coalition_tables = {}
        for sat_data in data["satellites"]:
            preferences = []
            for pref_data in sat_data["coalition_table"]["preferences"]:
                preference = CoalitionPreference(
                    task_id=pref_data["task_id"],
                    preferred_satellites=pref_data["preferred_satellites"],
                    priority=pref_data["priority"]
                )
                preferences.append(preference)

            coalition_table = CoalitionTable(sat_data["name"])
            coalition_table.preferences = preferences
            coalition_tables[sat_data["name"]] = coalition_table
        app.coalition_tables = coalition_tables

        return {
            "message": "Data loaded successfully",
            "satellites": data["satellites"],
            "tasks": data["tasks"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
