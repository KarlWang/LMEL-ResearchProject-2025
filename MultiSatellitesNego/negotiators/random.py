"""
Title: Random negotiator

Negotiator makes random proposals and responses.

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date: 14/04/2025
"""
from negmas import SAONegotiator, ResponseType, Outcome, SAOState
from .base import BaseNegotiator
import random

class RandomNegotiator(BaseNegotiator):
    """
    A simple negotiator that makes random proposals and responses.
    """

    def propose(self, state: SAOState, dest: str | None = None) -> Outcome | None:
        """
        Make a random proposal from the available outcomes.
        """
        # Check if satellite has enough memory for the task
        if self.satellite.available_memory < self.task.memory_required:
            return None

        # Get a random outcome
        return self.nmi.random_outcomes(1)[0]

    def respond(self, state: SAOState, source: str | None = None) -> ResponseType:
        """
        Randomly accept or reject offers.
        """
        # Check if satellite has enough memory for the task
        if self.satellite.available_memory < self.task.memory_required:
            return ResponseType.REJECT_OFFER

        # Randomly accept or reject
        return ResponseType.ACCEPT_OFFER if random.random() < 0.5 else ResponseType.REJECT_OFFER