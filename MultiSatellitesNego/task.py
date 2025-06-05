"""
Title: Task Class

This module defines the Task class which represents a 'complex' task.
A task has properties like location, time window, memory requirements and rewards.
Each task requires a certain amount of satellite memory.

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date: 13/02/2025
"""

class Task:
    def __init__(self, id, location_index, time_window, reward_points, memory_required):
        """
        Initialize a Task object.

        Args:
            id: Unique identifier for the task
            location_index: Index of the location where the task needs to be performed
            time_window: List of time windows when the task can be performed
            reward_points: Points awarded for completing the task
            memory_required: Amount of memory required to perform the task
        """
        self.id = id
        self.location_index = location_index
        self.time_window = time_window
        self.reward_points = reward_points
        self.memory_required = memory_required

    def __str__(self):
        """Return a string representation of the Task object."""
        return f"Task(id={self.id}, location_index={self.location_index}, time_window={self.time_window}, reward_points={self.reward_points}, memory_required={self.memory_required})"