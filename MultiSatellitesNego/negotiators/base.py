"""
Title: Base negotiator module

Base negotiator class that provides common functionality for all negotiators.

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date: 14/04/2025
"""
import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from negmas import SAONegotiator, ResponseType, Contract, UtilityFunction
from negmas import SAOState, Outcome
from negmas.common import MechanismState, NegotiatorMechanismInterface
from typing import Optional, Dict, Any
import logging
from task import Task
from satellite import Satellite

class BaseNegotiator(SAONegotiator):
    """Base class for all negotiators with common functionality."""

    LOGGING_ENABLED = True

    def __init__(self, satellite: Satellite, task: Task, ufun: UtilityFunction | None = None):
        super().__init__(name=f"Negotiator_{satellite.name}")
        self.ufun = ufun if ufun is not None else self.ufun
        self.satellite = satellite
        self.task = task
        self.negotiation_details = {
            "proposals": [],
            "responses": [],
            "utility_calculations": [],
            "memory_checks": []
        }
        if self.LOGGING_ENABLED:
            logging.info(f"Initialized negotiator for {self.name} on task {task.id}")
            logging.info(f"Memory: {satellite.available_memory}/{satellite.memory_capacity}")

    def on_preferences_changed(self, changes):
        super().on_preferences_changed(changes)

    def on_negotiation_start(self, state: SAOState):
        """Called when negotiation starts"""
        if self.LOGGING_ENABLED:
            logging.info(f"\n===== Negotiation Start! {self.name} =====")
            logging.info(f"Task {self.task.id} - Reward: {self.task.reward_points}, Memory: {self.task.memory_required}")
            logging.info(f"Satellite memory: {self.satellite.available_memory}/{self.satellite.memory_capacity}")

    def on_negotiation_failure(
        self,
        partners: list[str],
        annotation: dict[str, Any],
        mechanism: NegotiatorMechanismInterface,
        state: MechanismState,
    ) -> None:
        if self.LOGGING_ENABLED:
            logging.info(f"\n===== Negotiation Failed! {self.name} =====")
            logging.info(f"Partners: {partners}")
            logging.info(f"Task {self.task.id} - Reward: {self.task.reward_points}, Memory: {self.task.memory_required}")
            logging.info(f"Satellite memory: {self.satellite.available_memory}/{self.satellite.memory_capacity}")

    def on_negotiation_success(
        self, contract: Contract, mechanism: NegotiatorMechanismInterface
    ) -> None:
        if self.LOGGING_ENABLED:
            logging.info(f"\n===== Negotiation Succeeded! {self.name} =====")
            logging.info(f"Contract: {contract}")
            logging.info(f"Task {self.task.id} - Reward: {self.task.reward_points}, Memory: {self.task.memory_required}")
            logging.info(f"Satellite memory: {self.satellite.available_memory}/{self.satellite.memory_capacity}")

    def get_negotiation_details(self):
        """Return the detailed negotiation information"""
        return self.negotiation_details