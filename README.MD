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

### Add a new negotiator