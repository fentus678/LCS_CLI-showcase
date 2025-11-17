# LCS_CLI-showcase

A modular, extensible CLI-based **Layered Collaboration System (LCS)** for orchestrating structured GPT workflows.

> **Note:** This repository is a preview of the system design and CLI interface.  
> The core implementation remains **private** and is not included in this repository.

---

##  Overview

This CLI tool manages a **tree-based collaboration workflow** between GPT agents, using a **recursive, rule-driven architecture** with structured prompts and response routing.

It is designed for structured AI-assisted workflows, such as:

-  Story generation (e.g., fantasy branching plots, character-driven arcs)
-  Game design pipelines (quests, characters, world-building)
-  Multi-agent simulation or narrative planning
-  AI-assisted content pipelines (e.g., blog/article outlines, scene expansion)

---

##  Features

-  **Layer-Stair-Node structure** for hierarchical collaboration
-  **Recursive GPT execution** with async support
-  Structured prompt system:
  - `prompt`, `response`, and `data passing` logic
  - `assignment_prompt` for diverging child tasks
-  Branch-specific controls:
  - `Pass Data to Branches`
  - `Assignment` (generate different content per branch)
  - `Import from Database`
-  Configurable via JSON-based saves
-  CLI panels for tree, stair, and node control
-  Async task tracking with status reporting

---

##  Sample CLI Screens

```bash
Main Menu
│
├── File
├── Settings
├── Run LCS
├── Tree Panel
│   └──  Overview
│       └── Stair Panel
│           └── Node Panel
├── Database
└── Exit
```

---

##  File Structure

```
project_root/
│
├── cli_manager/
│   ├── main_menu.py              # Main CLI interface
│   ├── cli_tree_panel.py         # Tree overview interface
│   ├── cli_stair_panel.py        # Stair-level controls
│   └── cli_node_settings.py      # Node-specific settings
│
├── external_file_io/
│   ├── file_exporters.py         # Export config/save files
│   ├── file_generators.py        # Auto-generate templates
│   ├── node_settings.py          # Handle per-node settings
│   └── stair_settings.py         # Handle stair-level settings
│
├── data/
│   ├── saves/                    # Save states for projects
│   └── configs/                  # Base configs and templates
│
├── lcs_manager.py                # Core recursive logic (private)
├── main.py                       # Entry point
└── README.md                     # You're here.
```

---

##  Disclaimer

This project showcases the structure and workflow design of the LCS CLI system.  
All GPT-agent recursive logic and sensitive content remain private. If you're interested in collaboration, feel free to reach out.

---
