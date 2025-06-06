"""
Version 0.3 of the satellite negotiator with improved negotiation strategy.

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date created: 14/04/2025
"""
from negmas import (
    SAONegotiator,
    AspirationNegotiator,
    ResponseType,
    Outcome,
    SAOState,
    make_issue
)
from negmas.preferences import LinearAdditiveUtilityFunction
from .base import BaseNegotiator
import logging

class NegotiatorV03(BaseNegotiator):
    """
    Version 0.3 of the satellite negotiator with improved negotiation strategy.
    This version ensures negotiations last longer by requiring more steps before acceptance.
    """
    negotiator_issues = [
        make_issue(name="reward", values=101),
        make_issue(name="memory", values=101)
    ]

    initiator_ufun = LinearAdditiveUtilityFunction(
        values = {
            "reward": lambda x: float(x) / 150.0,  # Higher reward = higher utility (0-0.67)
            "memory": lambda x: (100.0 - float(x)) / 150.0  # Lower memory = higher utility (0-0.67)
        },
        weights={"reward": 1.2, "memory": 0.8},  # Give more weight to reward
        issues=negotiator_issues
    )

    partner_ufun = LinearAdditiveUtilityFunction(
        values = {
            "reward": lambda x: float(x) / 200.0,  # Higher reward = higher utility (0-0.5)
            "memory": lambda x: (100.0 - float(x)) / 200.0  # Lower memory = higher utility (0-0.5)
        },
        weights={"reward": 0.8, "memory": 1.2},  # Give more weight to memory
        issues=negotiator_issues
    )

    def propose(self, state: SAOState, dest: str | None = None) -> Outcome | None:
        """
        Propose an outcome based on the current task's memory and reward requirements,
        considering the satellite's memory capacity and usage.
        """

        relative_time = state.relative_time
        if self.LOGGING_ENABLED:
            logging.info(f"\n[{self.name}] PROPOSE at time {relative_time:.2f}")
            logging.info(f"Task {self.task.id} - Reward: {self.task.reward_points}, Memory: {self.task.memory_required}")
            logging.info(f"Satellite memory: {self.satellite.available_memory}/{self.satellite.memory_capacity}")

        # Check if satellite has enough memory for the task
        memory_check = {
            "time": relative_time,
            "available_memory": self.satellite.available_memory,
            "required_memory": self.task.memory_required,
            "has_enough_memory": self.satellite.available_memory >= self.task.memory_required
        }
        self.negotiation_details["memory_checks"].append(memory_check)

        if self.satellite.available_memory < self.task.memory_required:
            if self.LOGGING_ENABLED:
                logging.info("  Not enough memory available for task")
            return None

        # Get all possible outcomes
        outcomes = list(self.nmi.outcome_space.enumerate_or_sample())
        if self.LOGGING_ENABLED:
            logging.info(f"  Considering {len(outcomes)} possible outcomes")

        # Calculate utilities for each outcome, considering task requirements and memory
        utilities = []
        for outcome in outcomes:
            # Calculate base utility from the utility function
            base_utility = self.ufun(outcome)

            # Adjust utility based on task requirements and memory availability
            reward_factor = self.task.reward_points / 1000.0
            memory_factor = self.task.memory_required / self.satellite.memory_capacity
            memory_availability_factor = self.satellite.available_memory / self.satellite.memory_capacity

            # Higher utility when more memory is available
            adjusted_utility = base_utility * (1 + reward_factor + (1 - memory_factor) + memory_availability_factor) / 4

            utility_calc = {
                "time": relative_time,
                "outcome": str(outcome),
                "base_utility": base_utility,
                "reward_factor": reward_factor,
                "memory_factor": memory_factor,
                "memory_availability_factor": memory_availability_factor,
                "adjusted_utility": adjusted_utility
            }
            self.negotiation_details["utility_calculations"].append(utility_calc)

            utilities.append((outcome, base_utility, adjusted_utility))

        utilities.sort(key=lambda x: x[2], reverse=True)  # Sort by adjusted utility

        # Time-based strategy
        if relative_time < 0.3:  # Early phase
            selected_idx = int(len(utilities) * 0.2)
            phase = "early"
        elif relative_time < 0.7:  # Middle phase
            selected_idx = int(len(utilities) * 0.4)
            phase = "middle"
        else:  # Late phase
            selected_idx = int(len(utilities) * 0.6)
            phase = "late"

        selected_outcome, base_utility, adjusted_utility = utilities[selected_idx]

        proposal_details = {
            "time": relative_time,
            "satellite": self.satellite.name,
            "phase": phase,
            "outcome": str(selected_outcome),
            "base_utility": base_utility,
            "adjusted_utility": adjusted_utility,
            "selected_index": selected_idx,
            "total_outcomes": len(outcomes)
        }
        self.negotiation_details["proposals"].append(proposal_details)

        return selected_outcome

    def respond(self, state: SAOState, source: str | None = None) -> ResponseType:
        """
        Respond to an offer considering the task's memory and reward requirements,
        and the satellite's memory capacity and usage.
        """
        offer = state.current_offer
        relative_time = state.relative_time

        if self.LOGGING_ENABLED:
            logging.info(f"\n[{self.name}] RESPOND at time {relative_time:.2f}")
            logging.info(f"Task {self.task.id} - Reward: {self.task.reward_points}, Memory: {self.task.memory_required}")
            logging.info(f"Satellite memory: {self.satellite.available_memory}/{self.satellite.memory_capacity}")

        if offer is None:
            if self.LOGGING_ENABLED:
                logging.info("  No offer to respond to")
            return ResponseType.REJECT_OFFER

        memory_check = {
            "time": relative_time,
            "available_memory": self.satellite.available_memory,
            "required_memory": self.task.memory_required,
            "has_enough_memory": self.satellite.available_memory >= self.task.memory_required
        }
        self.negotiation_details["memory_checks"].append(memory_check)

        if self.satellite.available_memory < self.task.memory_required:
            if self.LOGGING_ENABLED:
                logging.info("  Not enough memory available for task")
            return ResponseType.REJECT_OFFER

        base_utility = self.ufun(offer)

        reward_factor = self.task.reward_points / 1000.0
        memory_factor = self.task.memory_required / self.satellite.memory_capacity
        memory_availability_factor = self.satellite.available_memory / self.satellite.memory_capacity

        adjusted_utility = base_utility * (1 + reward_factor + (1 - memory_factor) + memory_availability_factor) / 4

        utility_calc = {
            "time": relative_time,
            "offer": str(offer),
            "base_utility": base_utility,
            "reward_factor": reward_factor,
            "memory_factor": memory_factor,
            "memory_availability_factor": memory_availability_factor,
            "adjusted_utility": adjusted_utility
        }
        self.negotiation_details["utility_calculations"].append(utility_calc)

        current_step = state.step
        total_steps = self.nmi.n_steps

        # Time-based acceptance threshold with more conservative early phase
        if relative_time < 0.3:  # Early phase
            base_threshold = 0.95  # Increased from 0.8 to make early phase more conservative
            phase = "early"
        elif relative_time < 0.7:  # Middle phase
            base_threshold = 0.7 + (0.95 - 0.7) * (1 - relative_time)  # Adjusted range
            phase = "middle"
        else:  # Late phase
            base_threshold = 0.5 + (0.7 - 0.5) * (1 - relative_time)  # Adjusted range
            phase = "late"

        threshold = base_threshold * (1 + reward_factor + (1 - memory_factor) + memory_availability_factor) / 4

        # Only accept if we're past the minimum steps and utility is above threshold
        # Require at least n_steps-1 steps before accepting
        if current_step < total_steps - 1:
            response = ResponseType.REJECT_OFFER
        else:
            response = ResponseType.ACCEPT_OFFER if adjusted_utility >= threshold else ResponseType.REJECT_OFFER

        response_details = {
            "time": relative_time,
            "satellite": self.satellite.name,
            "phase": phase,
            "offer": str(offer),
            "base_utility": base_utility,
            "adjusted_utility": adjusted_utility,
            "base_threshold": base_threshold,
            "adjusted_threshold": threshold,
            "response": response.name,
            "current_step": current_step,
            "total_steps": total_steps
        }
        self.negotiation_details["responses"].append(response_details)

        return response
