# Dynamic Task Allocation for Multi-satellite System with Automated Negotiation

This repo hosts the code for the LMEL Research Project (UniSA, 2025): **Dynamic Task Allocation for Multi-satellite System with Automated Negotiation via Basilisk**.

## Instructions

### Run the experiments

* Coalition table-based strategy:

Usage: `python coalition_strategy.py <path_to_setup_json_file>`

Example:
```bash
LMEL-ResearchProject-2025$ python apps/coalition_strategy.py saved_data/10t5s.json
```

* Traditional strategy:

Usage: `python traditional_strategy.py <path_to_setup_json_file>`

Example:
```bash
LMEL-ResearchProject-2025$ python apps/traditional_strategy.py saved_data/5t5s.json
```

* Plot results

1. Make sure the result JSON files are generated in **results/**
2. Run `python apps/plot_results.py`. For example:
```bash
LMEL-ResearchProject-2025$ python apps/plot_results.py
```

### Run the front-end tool

Please follow these steps to run the front-end tool:

1. Start the FastAPI server
```
$ python apps/api.py
```

2. Open another terminal, run the following commands:
```
cd front-end

# Install Node.js dependencies (only needed for the first time)
npm install

# Start the React development server
npm start
```

The default browser should launch the front-end tool page automatically. If it doesn't do that for you, please visit http://localhost:3000 from your local machine.

### Add a new negotiator

1. Create a new Python file in the MultiSatellitesNego/negotiators/ directory. For example, **v06.py**
2. Use **v05.py** as the template for **v06.py**. For example, something like this:

```python
"""
Version 0.6 of the satellite negotiator.

Author: Your Name
Email: your.email@example.com
Date created: DD/MM/YYYY
"""
from negmas import (
    SAONegotiator, 
    ResponseType, 
    Outcome, 
    SAOState,
    make_issue
)
from negmas.preferences import LinearAdditiveUtilityFunction, IdentityFun
from .base import BaseNegotiator

class NegotiatorV06(BaseNegotiator):
    """
    Version 0.6 of the satellite negotiator.
    Add your description here.
    """
......
```

3. Edit the **MultiSatellitesNego/negotiators/__ init __.py** file to add your new negotiator:
```
# Add this import at the top with other imports
from .v06 import NegotiatorV06

# Add your negotiator to the registry
NEGOTIATOR_REGISTRY = {
    "v02": NegotiatorV02,
    "v03": NegotiatorV03,
    "v031": NegotiatorV03_1,
    "v04": NegotiatorV04,
    "v041": NegotiatorV04_1,
    "v05": NegotiatorV05,
    "v06": NegotiatorV06,  # Add your new negotiator here
    "random": RandomNegotiator
}
```

4. Test the negotiator

Use **nego_app.py** to test the negotiator. Its usage is as below:

```
usage: nego_app.py [-h] --negotiator {v02,v03,v031,v04,v041,v05,v06,random} --satellites SATELLITES --tasks TASKS
                   [--steps STEPS] [--plot]
```
The arguments `--negotiator/-n`, `--satellites/-s`, `--tasks/-t` are required. For example, use v06 negotiator, with 5 satellites and 10 tasks, maximum 25 steps for one negotiation:

```
$ python apps/nego_app.py -n v06 -s 5 -t 10 --steps 25
```

### Tools

#### Coverage table viewer

`$ python tools/coverage_table.py saved_data/20t20s.json `

#### Availability matrix generator

1. Update the `assignments` in **availability_matrix.py** to suit your needs.
2. Run the following comand:

`$ python tools/availability_matrix.py saved_data/20t20s.json`

#### Coalition table generator

For example: generate the coalition table for "sat10" in the setup of "5t10s":

`$ python tools/coalition_table_generator.py saved_data/5t10s.json sat10`

#### Satellite time window availability checker:

`$ python tools/time_window_coverage.py saved_data/5t5s.json`

#### Availability matrix interpreter

1. Update the `availability_matrix` of `sat` in **availability_matrix_interpret.py** to the availability matrix you want to interpret.
2. Run the following command:

`$ python tools/availability_matrix_interpret.py`
