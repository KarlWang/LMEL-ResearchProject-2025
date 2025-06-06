"""
Title: Satellite Agent Module

This module defines the SatelliteAgent class which represents individual satellites
in the negotiation system. Each satellite has:
- Memory capacity
- Availability schedule for different locations
- Task commitment tracking
- Reward accumulation
- Coalition preferences

The SatelliteAgent class inherits from NegMAS Agent class to participate in
multilateral negotiations for task allocation.

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date created: 13/02/2025
Date updated for SimSatelliteWorld: 02/04/2025
"""

from negmas.situated import (
    Action,
    Agent,
    AgentWorldInterface,
    Breach,
    Contract,
    NoContractExecutionMixin,
    RenegotiationRequest,
    World    
)
from negmas import (
    make_issue,
    Preferences,
    UtilityFunction,
    LinearUtilityFunction,
    SAONegotiator,
    Negotiator,
    NegotiatorMechanismInterface,
    MechanismState
)
from negmas.outcomes import Issue

from typing import Dict, List, Tuple, Optional, Any, Callable, Collection
from collections import defaultdict
import numpy as np
from random import random
from random import sample, randint
from abc import ABC, abstractmethod
from MultiSatellitesNego.coalition import CoalitionTable

class SatellliteAgent(Agent, ABC):
    @abstractmethod
    def step(self):
        ...

    @abstractmethod
    def init(self):
        ...

    @abstractmethod
    def respond_to_negotiation_request(
        self,
        initiator: str,
        partners: List[str],
        mechanism: NegotiatorMechanismInterface,
    ) -> Optional[Negotiator]:
        ...

    def _respond_to_negotiation_request(
        self,
        initiator: str,
        partners: List[str],
        issues: List[Issue],
        annotation: Dict[str, Any],
        mechanism: NegotiatorMechanismInterface,
        role: Optional[str],
        req_id: Optional[str],
    ) -> Optional[Negotiator]:
        return self.respond_to_negotiation_request(initiator, partners, mechanism)

    def on_neg_request_rejected(self, req_id: str, by: Optional[List[str]]):
        pass

    def on_neg_request_accepted(
        self, req_id: str, mechanism: NegotiatorMechanismInterface
    ):
        pass

    def on_negotiation_failure(
        self,
        partners: List[str],
        annotation: Dict[str, Any],
        mechanism: NegotiatorMechanismInterface,
        state: MechanismState,
    ) -> None:
        pass

    def on_negotiation_success(
        self, contract: Contract, mechanism: NegotiatorMechanismInterface
    ) -> None:
        pass

    def set_renegotiation_agenda(
        self, contract: Contract, breaches: List[Breach]
    ) -> Optional[RenegotiationRequest]:
        pass

    def respond_to_renegotiation_request(
        self, contract: Contract, breaches: List[Breach], agenda: RenegotiationRequest
    ) -> Optional[Negotiator]:
        pass

    def on_contract_executed(self, contract: Contract) -> None:
        pass

    def on_contract_breached(
        self, contract: Contract, breaches: List[Breach], resolution: Optional[Contract]
    ) -> None:
        pass

class Satellite(SatellliteAgent):
    def __init__(self, 
                 name: str | None = None,
                 memory_capacity: int = 0,
                 available_memory: int = 0,
                 accumulated_reward: int = 0,
                 availability_matrix: Dict[str, List[bool]] = {},
                 coalition_table: CoalitionTable = {},
                 ufun: UtilityFunction | None = None):
        super().__init__()
        self.name = name if name is not None else f"sat{randint(0, 1000)}"
        self.memory_capacity = memory_capacity
        self.available_memory = available_memory
        self.accumulated_reward = accumulated_reward
        self.availability_matrix = availability_matrix
        self.task_commitments: Dict[int, int] = {}
        self.coalition_table = coalition_table if coalition_table else CoalitionTable(self.name)
        self.current_negotiations: Dict[int, List[str]] = {}
        self.task_assignments = []  # [(task_id, location, start_time, duration)]

    def init(self):
        pass

    def step(self):
        # get IDs of all ogher agents from the AWI
        print(f"[{self.name}] Stepping")

    def respond_to_negotiation_request(
        self,
        initiator: str,
        partners: List[str],
        mechanism: NegotiatorMechanismInterface,
    ) -> Optional[Negotiator]:
        print("Running: Satellite.respond_to_negotiation_request")
        pass