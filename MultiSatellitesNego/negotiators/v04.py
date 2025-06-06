"""
Version 04 of the satellite negotiator with improved negotiation strategy.

This version doesn't consider memory usage in propose().

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date created: 15/04/2025
"""
from negmas import (
    SAONegotiator,
    AspirationNegotiator,
    PolyAspiration,
    PresortingInverseUtilityFunction,
    PreferencesChangeType,
    ResponseType,
    Outcome,
    SAOState,
    make_issue
)
from negmas.preferences import LinearAdditiveUtilityFunction, LinearFun, IdentityFun, AffineFun
from .base import BaseNegotiator
from random import choice
import logging

class NegotiatorV04(BaseNegotiator):
    """
    Version 04 of the satellite negotiator with improved negotiation strategy.
    """
    _inv = None  # The ufun invertor (finds outcomes in a utility range)
    _partner_first = None  # The best offer of the partner (assumed best for it)
    _min = None  # The minimum of my utility function
    _max = None  # The maximum of my utility function
    _best = None  # The best outcome for me

    negotiator_issues = [
        make_issue(name="initiator_reward", values=101),
        make_issue(name="initiator_memory", values=101)
    ]

    initiator_ufun = LinearAdditiveUtilityFunction(
        values = {
            "initiator_reward": IdentityFun(),
            "initiator_memory": lambda x: (100.0 - float(x)) / 100.0,
        },
        weights={"reward": 1.2, "memory": 0.8},
        issues=negotiator_issues
    )

    partner_ufun = LinearAdditiveUtilityFunction(
        values = {
            "initiator_reward": lambda x: (100.0 - float(x)) / 100.0,
            "initiator_memory": lambda x: float(x) / 100.0
        },
        weights={"reward": 1.2, "memory": 0.8},
        issues=negotiator_issues
    )

    def __init__(self, *args, **kwargs):
        # initialize the base SAONegoiator (MUST be done)
        super().__init__(*args, **kwargs)

        # Initialize the aspiration mixin to start at 1.0 and concede slowly
        self._asp = PolyAspiration(1.0, "boulware")


    def on_preferences_changed(self, changes):

        # create an initialize an invertor for my ufun
        changes = [_ for _ in changes if _.type not in (PreferencesChangeType.Scale,)]
        if not changes:
            return

        self._inv = PresortingInverseUtilityFunction(self.ufun)
        self._inv.init()

        # find worst and best outcomes for me
        worest, self._best = self.ufun.extreme_outcomes()

        # and the corresponding utility values
        self._min, self._max = self.ufun(worest), self.ufun(self._best)

        # MUST call parent to avoid being called again for no reason
        super().on_preferences_changed(changes)

    def propose(self, state: SAOState, dest: str | None = None) -> Outcome | None:
        """
        Propose an outcome based on the current task's memory and reward requirements,
        considering the satellite's memory capacity and usage.
        """
        if self.LOGGING_ENABLED:
            logging.info(f"\n[{self.name}] PROPOSE at time {state.relative_time:.2f}")
            logging.info(f"Task {self.task.id} - Reward: {self.task.reward_points}, Memory: {self.task.memory_required}")
            logging.info(f"Satellite memory: {self.satellite.available_memory}/{self.satellite.memory_capacity}")


        # Check if satellite has enough memory for the task
        memory_check = {
            "time": state.relative_time,
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
                "time": state.relative_time,
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
        if state.relative_time < 0.3:  # Early phase
            selected_idx = int(len(utilities) * 0.2)
            phase = "early"
        elif state.relative_time < 0.7:  # Middle phase
            selected_idx = int(len(utilities) * 0.4)
            phase = "middle"
        else:  # Late phase
            selected_idx = int(len(utilities) * 0.6)
            phase = "late"

        selected_outcome, base_utility, adjusted_utility = utilities[selected_idx]

        proposal_details = {
            "time": state.relative_time,
            "satellite": self.satellite.name,
            "phase": phase,
            "outcome": str(selected_outcome),
            "base_utility": base_utility,
            "adjusted_utility": adjusted_utility,
            "selected_index": selected_idx,
            "total_outcomes": len(outcomes)
        }
        self.negotiation_details["proposals"].append(proposal_details)

        # Old return
        # return selected_outcome

        # calculate my current aspiration level (utility level at which I will offer and accept)
        a = ((self._max or 0) - (self._min or 0)) * self._asp.utility_at(
            state.relative_time
        ) + (self._min or 0)

        # find some outcomes (all if the outcome space is  discrete) above the aspiration level
        outcomes = self._inv.some((a - 1e-6, self._max + 1e-6), False)
        # If there are no outcomes above the aspiration level, offer my best outcome
        if not outcomes:
            return self._best

        # else if I did not  receive anything from the partner, offer any outcome above the aspiration level
        if not self._partner_first:
            return choice(outcomes)

        # otherwise, offer the outcome most similar to the partner's first offer (above the aspiration level)
        nearest, ndist = None, float("inf")
        for o in outcomes:
            d = sum((a - b) * (a - b) for a, b in zip(o, self._partner_first))
            if d < ndist:
                nearest, ndist = o, d
        return nearest

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
            return ResponseType.REJECT_OFFER

        # Calculate base utility
        base_utility = self.ufun(offer)

        # Adjust utility based on task requirements and memory
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

        # Get current step number and total steps from the mechanism
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

        response = super().respond(state, source)
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

        # set the partner's first offer when I receive it
        if not self._partner_first:
            self._partner_first = offer

        # accept if the offer is not worse for me than what I would have offered
        return response
