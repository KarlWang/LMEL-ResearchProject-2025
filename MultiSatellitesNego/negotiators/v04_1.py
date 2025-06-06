"""
Version 0.4.1 of the satellite negotiator.

This is a simplified version of v0.4, which removed unused code in proposal()
and some memory usage related code in respond().

This version should not be used as the memory usage is not considered -
only use it for reference as it's directly copied from NegMAS example.

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date created: 18/04/2025
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

class NegotiatorV04_1(BaseNegotiator):
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
        print(f"on_preferences_changed: {changes}")
        # create an initialize an invertor for my ufun
        changes = [_ for _ in changes if _.type not in (PreferencesChangeType.Scale,)]

        self._inv = PresortingInverseUtilityFunction(self.ufun)
        self._inv.init()


        # find worst and best outcomes for me
        worest, self._best = self.ufun.extreme_outcomes()

        # and the corresponding utility values
        self._min, self._max = self.ufun(worest), self.ufun(self._best)
        print(f"self._min: {self._min}, self._max: {self._max}")
        # MUST call parent to avoid being called again for no reason
        super().on_preferences_changed(changes)

    def respond(self, state, source: str):

        offer = state.current_offer

        if offer is None:
            return ResponseType.REJECT_OFFER
        # set the partner's first offer when I receive it
        if not self._partner_first:
            self._partner_first = offer

        # accept if the offer is not worse for me than what I would have offered
        return super().respond(state, source)

    def propose(self, state, dest: str | None = None):

        if self._inv is None:
            print('self._inv is None')
            return

        # calculate my current aspiration level (utility level at which I will offer and accept)
        a = ((self._max or 0) - (self._min or 0)) * self._asp.utility_at(
            state.relative_time
        ) + (self._min or 0)
        print(f"self._max={self._max}, self._min={self._min}, a={a}")

        # find some outcomes (all if the outcome space is  discrete) above the aspiration level
        outcomes = self._inv.some((a - 1e-6, self._max + 1e-6), False)
        # If there are no outcomes above the aspiration level, offer my best outcome

        if not outcomes:
            return self._best

        # else if I did not  receive anything from the partner, offer any outcome above the aspiration level
        if not self._partner_first:
            print(f"choice(outcomes)={choice(outcomes)}")
            return choice(outcomes)

        # otherwise, offer the outcome most similar to the partner's first offer (above the aspiration level)
        nearest, ndist = None, float("inf")
        for o in outcomes:
            d = sum((a - b) * (a - b) for a, b in zip(o, self._partner_first))
            if d < ndist:
                nearest, ndist = o, d
        print(f"nearest={nearest}")
        return nearest