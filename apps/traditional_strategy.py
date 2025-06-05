"""
Title: Traditional Strategy

This script analyse the traditional task allocation strategy,
which is a 2-stage, auction based method

Author: Zheng Wang
Email: wanzy133@mymail.unisa.edu.au
Supervisor: Dr. Jianglin Qiao

Date Created: 07/05/2025
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from negmas import SAOMechanism, TimeBasedConcedingNegotiator, AspirationNegotiator, SAONegotiator, ResponseType
from negmas.preferences import LinearAdditiveUtilityFunction as LUFun
from negmas.preferences.value_fun import LinearFun, IdentityFun, AffineFun
from negmas.preferences.crisp.mapping import MappingUtilityFunction
from negmas.outcomes import dict2outcome, make_issue, Outcome
import matplotlib.pyplot as plt
import pprint
from random import choice
from negmas import PolyAspiration, PresortingInverseUtilityFunction, PreferencesChangeType
from MultiSatellitesNego.negotiators.v05 import NegotiatorV05
from MultiSatellitesNego.satellite import Satellite
from MultiSatellitesNego.task import Task
from MultiSatellitesNego.utils import (
    calculate_average_memory_utilisation,
    calculate_average_reward,
    calculate_average_negotiation_rounds,
    calculate_negotiation_success_rate,
    is_satellite_available_for_task,
    calculate_task_allocation_success_rate
)

import json
import sys

PRINT_DEBUG = False

class AuctionNegotiator(SAONegotiator):
    _inv = None
    _partner_first = None
    _min = None
    _max = None
    _best = None
    _sat = None
    _task = None
    _negotiator_type = None

    def __init__(self, satellite: str | None = None, task: str | None = None, *args, **kwargs):
        # initialize the base SAONegoiator (MUST be done)
        super().__init__(*args, **kwargs)

        # Initialize the aspiration mixin to start at 1.0 and concede slowly
        self._asp = PolyAspiration(1.0, "linear")
        self._sat = satellite
        self._task = task
        self._negotiator_type = "satellite" if self._sat is not None else "task"

    def on_preferences_changed(self, changes):

        # create an initialize an invertor for my ufun
        changes = [_ for _ in changes if _.type not in (PreferencesChangeType.Scale,)]

        self._inv = PresortingInverseUtilityFunction(self.ufun)
        self._inv.init()


        # find worst and best outcomes for me
        worst, self._best = self.ufun.extreme_outcomes()

        # and the corresponding utility values
        self._min, self._max = self.ufun(worst), self.ufun(self._best)

        # MUST call parent to avoid being called again for no reason
        super().on_preferences_changed(changes)

    def respond(self, state, source: str):
        if PRINT_DEBUG:
            print(f"Step {state.step} ({state.relative_time}): offer from {state.last_negotiator}: {state.current_offer}")
            print(f"Now {self._negotiator_type} responding")

        offer = state.current_offer
        if offer is None:
            if PRINT_DEBUG:
                print(f"offer is None, rejecting\n")
            return ResponseType.REJECT_OFFER
        # set the partner's first offer when I receive it
        if not self._partner_first:
            self._partner_first = offer

        # SATELLITE LOGIC (BUYER)
        if self._negotiator_type == "satellite" and self._sat is not None:
            # Only hard constraint: reject if price exceeds available memory
            if offer[0] > self._sat["available_memory"]:
                if PRINT_DEBUG:
                    print(f"offer[0] > self._sat['available_memory'], rejecting\n")
                return ResponseType.REJECT_OFFER

            # Be more lenient: apply a discount to the aspiration level
            current_aspiration = ((self._max or 0) - (self._min or 0)) * self._asp.utility_at(
                state.relative_time
            ) * 0.8 + (self._min or 0)  # 20% discount on aspiration

            if self.ufun(offer) >= current_aspiration:
                if PRINT_DEBUG:
                    print(f"self.ufun(offer) >= current_aspiration, accepting\n")
                return ResponseType.ACCEPT_OFFER

            # Accept anyway in the final 20% of negotiation time if it's not terrible
            if state.relative_time > 0.8 and self.ufun(offer) > self._min * 1.2:
                if PRINT_DEBUG:
                    print(f"state.relative_time > 0.8 and self.ufun(offer) > self._min * 1.2, accepting\n")
                return ResponseType.ACCEPT_OFFER

            if PRINT_DEBUG:
                print(f"last rejecting\n")
            return ResponseType.REJECT_OFFER

        # TASK LOGIC (SELLER)
        elif self._negotiator_type == "task" and self._task is not None:
            min_req = self._task["memory_required"]
            if offer[0] < min_req:
                if PRINT_DEBUG:
                    print(f"offer[0] < min_req, rejecting\n")
                return ResponseType.REJECT_OFFER

            # Graduated acceptance thresholds based on time pressure
            if state.relative_time <= 0.3:
                # Early stages: be demanding - reject unless significantly above minimum
                if offer[0] < min_req * 1.5:  # Want 50% more than minimum
                    if PRINT_DEBUG:
                        print(f"offer[0] < min_req * 1.5, rejecting\n")
                    return ResponseType.REJECT_OFFER

            elif state.relative_time <= 0.5:
                # Middle stages: accept somewhat above minimum
                if offer[0] < min_req * 1.2:  # Want 20% more than minimum
                    if PRINT_DEBUG:
                        print(f"offer[0] < min_req * 1.2, rejecting\n")
                    return ResponseType.REJECT_OFFER

            elif state.relative_time <= 0.8:
                # Later stages: accept small premium
                if offer[0] < min_req * 1.02:  # Want 5% more than minimum
                    if PRINT_DEBUG:
                        print(f"offer[0] < min_req * 1.02, rejecting\n")
                    return ResponseType.REJECT_OFFER

            # Final stages: accept anything at or above minimum requirement
            if PRINT_DEBUG:
                print(f"accepting\n")
            return ResponseType.ACCEPT_OFFER

        # accept if the offer is not worse for me than what I would have offered
        if PRINT_DEBUG:
            print(f"accepting\n")
        return super().respond(state, source)

    def propose(self, state, dest: str | None = None):
        if PRINT_DEBUG:
            print(f"Step {state.step} ({state.relative_time}): offer from {state.last_negotiator}: {state.current_offer}")
            print(f"Now {self._negotiator_type} proposing\n")

        if self._inv is None:
            return

        # calculate the current aspiration level (utility level at which I will offer and accept)
        a = ((self._max or 0) - (self._min or 0)) * self._asp.utility_at(
            state.relative_time
        ) + (self._min or 0)

        # SATELLITE LOGIC (BUYER)
        if self._negotiator_type == "satellite" and self._sat is not None:
            available_memory = self._sat["available_memory"]

            # Find outcomes above the aspiration level
            outcomes = self._inv.some((a - 1e-6, self._max + 1e-6), False)
            if PRINT_DEBUG:
                print(f"available_memory: {available_memory}, outcomes: {len(outcomes)}")
            if not outcomes:
                return self._best

            # Filter to ensure price <= available_memory
            filtered_outcomes = [o for o in outcomes if o[0] <= available_memory]
            if not filtered_outcomes:
                return self._best

            # Get price range information from filtered outcomes
            min_price = min(o[0] for o in filtered_outcomes)
            max_price = max(o[0] for o in filtered_outcomes)
            price_range = max_price - min_price if max_price > min_price else 1

            # Early negotiation: offer based on memory capacity
            if state.relative_time < 0.4:
                # For satellites with more memory, be more generous
                # Calculate a target percentile based on memory size
                # Larger memory = higher percentile (more generous offer)
                memory_percentile = min(available_memory / 100, 0.7)  # Cap at 70th percentile

                # Convert percentile to target price within our filtered range
                target_price = min_price + (price_range * memory_percentile)

                # Find outcomes closest to this target
                sorted_outcomes = sorted(filtered_outcomes,
                                        key=lambda o: abs(o[0] - target_price))

                # Take one of the top few matches
                top_matches = sorted_outcomes[:min(3, len(sorted_outcomes))]
                return choice(top_matches)

            # Middle stages: adjust based on available memory
            elif state.relative_time < 0.7:
                # More memory = more willing to consider higher-priced outcomes
                # Scaled based on memory size
                flexibility = min(0.3 + (available_memory / 1000), 0.8)

                # Select outcomes based on this flexibility
                sorted_outcomes = sorted(filtered_outcomes, key=lambda o: o[0], reverse=True)
                selection_point = int(len(sorted_outcomes) * flexibility)
                selection_point = max(1, selection_point)  # Ensure at least 1

                # Choose from the higher-priced outcomes based on memory size
                candidate_outcomes = sorted_outcomes[:selection_point]
                return choice(candidate_outcomes)

            # Late negotiation: focus on reaching agreement
            else:
                # Still factor in memory capacity but with diminishing effect
                memory_factor = min(available_memory / 500, 0.5)

                # Sort outcomes by utility, with small boost for higher prices
                # based on memory capacity
                def custom_sort(outcome):
                    base_utility = self.ufun(outcome)
                    price_position = (outcome[0] - min_price) / price_range if price_range > 0 else 0
                    memory_boost = price_position * memory_factor
                    return base_utility + memory_boost

                sorted_outcomes = sorted(filtered_outcomes, key=custom_sort, reverse=True)

                # Select from top options
                selection_size = max(1, int(len(sorted_outcomes) * 0.2))
                return choice(sorted_outcomes[:selection_size])

            outcomes = filtered_outcomes

        # TASK LOGIC (SELLER)
        elif self._negotiator_type == "task" and self._task is not None:
            min_price = self._task["memory_required"]
            # find some outcomes above the aspiration level
            outcomes = self._inv.some((a - 1e-6, self._max + 1e-6), False)

            # If there are no outcomes above the aspiration level, offer my best outcome
            if not outcomes:
                return self._best

            filtered_outcomes = [o for o in outcomes if o[0] >= min_price]
            if not filtered_outcomes:
                highest_price = -1
                best_outcome = None
                for o in outcomes:
                    if o[0] > highest_price:
                        highest_price = o[0]
                        best_outcome = o
                return best_outcome or self._best

            # In early stages, start with higher offers (30% premium)
            if state.relative_time < 0.4:
                target_price = min_price * 1.3  # 30% higher than minimum

                # Find outcomes closest to (but not below) the target price
                best_match = None
                min_distance = float('inf')

                for o in filtered_outcomes:
                    # Only consider outcomes at or above target price in early stages
                    if o[0] >= target_price:
                        distance = abs(o[0] - target_price)
                        if distance < min_distance:
                            min_distance = distance
                            best_match = o

                # If we found a match at or above target price, return it
                if best_match:
                    return best_match

            # Use filtered outcomes for the rest of the logic
            outcomes = filtered_outcomes

        # else if I did not  receive anything from the partner, offer any outcome above the aspiration level
        if not self._partner_first:
            return choice(outcomes)
        else:
            # Find the outcome closest to the partner's first offer
            closest_outcome = min(outcomes, key=lambda o: sum((a - b)**2 for a, b in zip(o, self._partner_first)))
            return closest_outcome

def price_value_function(price):
    min_price = 20
    if price < min_price:
        return 0  # Zero utility below minimum price
    else:
        return price - min_price + 1  # Linear increase above minimum

def run_negotiation(cls, satellite, task, plot=False, n_steps=20):
    satellite_cls = cls
    task_cls = cls

    # create negotiation agenda (issues)
    # "* 2" is to make the range of prices larger to allow tasks for more aggressive proposals
    issues = [
        make_issue(name="price", values=range(0, int(task["memory_required"]) * 2 + 1))
    ]

    session = SAOMechanism(issues=issues, n_steps=n_steps)

    seller_utility = LUFun(
        values={
            "price": MappingUtilityFunction(
                mapping=lambda price: 0 if price < task["memory_required"] else price - task["memory_required"] + 1
            )
        },
        outcome_space=session.outcome_space,
    ).scale_max(1.0)

    buyer_utility = LUFun(
        values={
            "price": AffineFun(slope=-1, bias=9)
        },

        outcome_space=session.outcome_space,
        reserved_value=10.0,
    ).scale_max(1.0)

    session.add(satellite_cls(name=satellite["name"], satellite=satellite), ufun=buyer_utility)
    session.add(task_cls(name="task" + str(task["id"]), task=task), ufun=seller_utility)

    if PRINT_DEBUG:
        print(session.run())
    else:
        session.run()

    if plot:
        session.plot()
        plt.show()

    return session

def stage_1_task_distribution(tasks, satellites):
    print("\n--- Stage 1: Task Distribution ---")
    if PRINT_DEBUG:
        s = run_negotiation(AuctionNegotiator, satellites[0], tasks[1])
        pprint.pp(s.full_trace)
        agreement = s.state.agreement is not None
        if agreement:
            print(f"Agreement achieved: {s.state.agreement}")
    else:
        task_best_agreements = {}
        stage1_results = {
            'task_assignments': {},
            'satellite_memory': {},
            'agreement_prices': {},
            'negotiation_results': [],
            'availability_checks': 0
        }

        for tsk in tasks:
            task_id = tsk["id"]
            print(f"\n--- Negotiations for Task {task_id} ---")
            task_best_agreements[task_id] = {
                "price": 0,
                "satellite": None,
                "agreement": None
            }

            # Negotiate only with available satellites
            for sate in satellites:
                # Check if satellite is available for this task
                stage1_results['availability_checks'] += 1  # Count availability check
                if is_satellite_available_for_task(sate, tsk) < 0:
                    print(f"Skipping negotiation with {sate['name']} - not available for Task {task_id}\n")
                    continue

                print(f"Negotiation Task{task_id} vs {sate['name']}")
                s = run_negotiation(AuctionNegotiator, sate, tsk)

                # Track negotiation results
                negotiation_result = {
                    'task_id': task_id,
                    'satellite': sate['name'],
                    'agreement_reached': s.state.agreement is not None,
                    'rounds': s.state.step
                }
                stage1_results['negotiation_results'].append(negotiation_result)

                # Check if an agreement was reached
                if s.state.agreement is not None:
                    agreement_price = s.state.agreement[0]
                    print(f"Agreement reached at price: {agreement_price}")

                    # Update best agreement if this one has a higher price
                    if agreement_price > task_best_agreements[task_id]["price"]:
                        task_best_agreements[task_id] = {
                            "price": agreement_price,
                            "satellite": sate["name"],
                            "agreement": s.state.agreement
                        }
                else:
                    print("No agreement reached")

                print("\n")

            # Task updates price (memory required) according to the negotiation results
            # normally higher than the original price
            tsk['memory_required'] = task_best_agreements[task_id]['price']

            # Winner pays
            for s in satellites:
                if s['name'] == task_best_agreements[task_id]['satellite']:
                    s['available_memory'] -= task_best_agreements[task_id]['price']
                    print(f"{s['name']} paid {task_best_agreements[task_id]['price']}, left {s['available_memory']}")
                    break

        print("\n--- BEST AGREEMENTS FOR EACH TASK ---")
        for task_id, best in task_best_agreements.items():
            if best["satellite"] is not None:
                print(f"Task {task_id}: Best agreement with {best['satellite']} at price {best['price']}")
                for sat in satellites:
                    if sat["name"] == best["satellite"]:
                        # Store results
                        stage1_results['task_assignments'][task_id] = best["satellite"]
                        stage1_results['agreement_prices'][task_id] = best["price"]
            else:
                print(f"Task {task_id}: No agreements reached with any satellite")
                stage1_results['task_assignments'][task_id] = None
                stage1_results['agreement_prices'][task_id] = None

        for sat in satellites:
            stage1_results['satellite_memory'][sat["name"]] = sat["available_memory"]

        return stage1_results

def stage_2_finding_partner(tasks, satellites, stage1_results):
    print("\n--- Stage 2: Finding Partner ---")
    print("Current satellite memory status")
    for sat in satellites:
        print(f"{sat['name']}: Memory available: {sat['available_memory']}")

    for tsk in tasks:
        print(f"Task {tsk['id']} Memory required: {tsk['memory_required']}")

    stage2_results = {
        'negotiation_results': [],  # List to store negotiation results
        'availability_checks': 0  # Track availability checks
    }

    # For each task that was assigned in stage 1
    for task_id, assigned_satellite in stage1_results['task_assignments'].items():
        if assigned_satellite is None:
            print(f"\nTask {task_id}: No satellite assigned in stage 1, skipping partner search")
            continue

        print(f"\n--- Finding partner for Task {task_id} (Initiator: {assigned_satellite}) ---")

        # Get the task and initiator satellite
        task = next(t for t in tasks if t['id'] == task_id)
        initiator = next(s for s in satellites if s['name'] == assigned_satellite)

        # Create the negotiation mechanism.
        # The number of "steps" is fixed to 20 here - probably should be a parameter
        print(f"Initiator memory: {initiator['available_memory']}, task requires: {task["memory_required"]}")
        initiator_negotiator = NegotiatorV05(satellite=Satellite(**initiator), task=Task(**task))

        # Negotiate with other satellites for partner selection
        for potential_partner in satellites:
            if potential_partner['name'] == assigned_satellite:
                continue  # Skip the initiator satellite

            # Check if potential partner is available for the task
            stage2_results['availability_checks'] += 1  # Count availability check
            if is_satellite_available_for_task(potential_partner, task) < 0:
                print(f"Skipping {potential_partner['name']} - not available for Task {task_id}")
                continue

            print(f"Negotiating with potential partner: {potential_partner['name']} (available_memory: {potential_partner['available_memory']})")

            session = SAOMechanism(issues=NegotiatorV05.negotiator_issues, n_steps=20)
            session.add(initiator_negotiator, ufun=NegotiatorV05.initiator_ufun)
            partner_negotiator = NegotiatorV05(satellite=Satellite(**potential_partner), task=Task(**task))
            session.add(partner_negotiator, ufun=NegotiatorV05.partner_ufun)
            session.run()

            negotiation_result = {
                'task_id': task_id,
                'initiator': assigned_satellite,
                'partner': potential_partner['name'],
                'agreement_reached': session.state.agreement is not None,
                'rounds': session.state.step
            }
            stage2_results['negotiation_results'].append(negotiation_result)

            if session.state.agreement is not None:
                agreement = session.state.agreement
                print(f"Agreement reached with {potential_partner['name']}:")
                print(f"  Initiator reward: {agreement[0]}")
                print(f"  Initiator memory: {agreement[1]}")

                # Update satellite memories based on agreement
                initiator_memory_percentage = (float(agreement[1]) / 100)
                partner_pay = float(task["memory_required"]) - float(task["memory_required"]) * initiator_memory_percentage
                print(f"percentage: {initiator_memory_percentage}, partner needs to pay: {partner_pay}")
                initiator['available_memory'] += round(partner_pay)
                potential_partner['available_memory'] -= round(partner_pay)
                print(f"Updated memory:")
                print(f"  {initiator['name']}: {initiator['available_memory']}")
                print(f"  {potential_partner['name']}: {potential_partner['available_memory']}")

                # Update rewards
                initiator_reward = (float(agreement[0]) / 100) * float(task["reward_points"])
                partner_reward = float(task["reward_points"]) - initiator_reward
                print(f"Initiator reward: {initiator_reward}, partner reward: {partner_reward}")
                initiator['accumulated_reward'] += round(initiator_reward)
                potential_partner['accumulated_reward'] += round(partner_reward)
                print(f"Updated rewards:")
                print(f"  {initiator['name']}: {initiator['accumulated_reward']}")
                print(f"  {potential_partner['name']}: {potential_partner['accumulated_reward']}")

            else:
                print(f"No agreement reached with {potential_partner['name']}")

            session = None

    return stage2_results

def main():
    if len(sys.argv) < 2:
        print("Usage: python traditional_strategy.py <path_to_json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    setup_name = os.path.basename(json_file).replace('.json', '')

    PRINT_DEBUG = any(flag in sys.argv for flag in ["--debug", "-d"])

    with open(json_file, 'r') as file:
        data = json.load(file)

    tasks = data['tasks']
    satellites = data['satellites']

    print("\n---=== Traditional Strategy ===---")

    s1_results = stage_1_task_distribution(tasks, satellites)
    s2_results = stage_2_finding_partner(tasks, satellites, s1_results)

    # Calculate and display memory utilization metrics
    avg_utilisation, total_used, total_available = calculate_average_memory_utilisation(satellites)
    print("\n--- Memory Utilisation Metrics ---")
    print(f"Total Memory Available: {total_available}")
    print(f"Total Memory Used: {total_used}")
    print(f"Average Memory Utilisation: {avg_utilisation:.2f}%")

    # Calculate and display reward metrics
    avg_reward, total_reward, num_satellites = calculate_average_reward(satellites)
    print("\n--- Reward Metrics ---")
    print(f"Total Reward Points: {total_reward}")
    print(f"Number of Satellites: {num_satellites}")
    print(f"Average Reward per Satellite: {avg_reward:.2f}")

    # Calculate and display negotiation rounds metrics
    avg_rounds, total_rounds, num_negotiations = calculate_average_negotiation_rounds(s1_results, s2_results)
    print("\n--- Negotiation Rounds Metrics ---")
    print(f"Total Negotiation Rounds: {total_rounds}")
    print(f"Number of Negotiations: {num_negotiations}")
    print(f"Average Rounds per Negotiation: {avg_rounds:.2f}")

    # Calculate and display negotiation success rate metrics
    success_rate, successful_negotiations, total_negotiations = calculate_negotiation_success_rate(s1_results, s2_results)
    print("\n--- Negotiation Success Rate Metrics ---")
    print(f"Total Negotiations: {total_negotiations}")
    print(f"Successful Negotiations: {successful_negotiations}")
    print(f"Success Rate: {success_rate:.2f}%")

    # Calculate and display task allocation success rate metrics
    task_success_rate, successful_tasks, total_tasks = calculate_task_allocation_success_rate(s1_results, s2_results)
    print("\n--- Task Allocation Success Rate Metrics ---")
    print(f"Total Tasks: {total_tasks}")
    print(f"Successfully Allocated Tasks: {successful_tasks}")
    print(f"Task Allocation Success Rate: {task_success_rate:.2f}%")

    results_dict = {
        "setup_name": setup_name,
        "metrics": {
            "memory_utilisation": {
                "total_available": total_available,
                "total_used": total_used,
                "average": avg_utilisation
            },
            "rewards": {
                "total": total_reward,
                "average_per_satellite": avg_reward,
                "num_satellites": num_satellites
            },
            "negotiation": {
                "total_rounds": total_rounds,
                "num_negotiations": num_negotiations,
                "average_rounds": avg_rounds,
                "success_rate": success_rate,
                "successful_negotiations": successful_negotiations,
                "total_negotiations": total_negotiations
            },
            "task_allocation": {
                "success_rate": task_success_rate,
                "successful_tasks": successful_tasks,
                "total_tasks": total_tasks
            }
        }
    }

    # Save results to JSON file
    output_file = f'results/{setup_name}_traditional_results.json'
    os.makedirs('results', exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results_dict, f, indent=2)

    print(f"\nResults have been saved to {output_file}")

if __name__ == "__main__":
    main()
