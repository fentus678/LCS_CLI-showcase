from questionary import select, Separator
import questionary
import os
from os import system, name
import cli_manager.cli_stair_panel as cli_stair_panel
import transcode
import external_file_io

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def assign_overview_options():
    choices = []
    prefixes = []
    tree_struct = transcode.LCS_tree_inputForm
    
    for key, values in tree_struct.items():
        for idx, _ in enumerate(values, start=1):
            prefix = "├─" if idx < len(values) else "└─"
            if idx == 1:
                choices.append(f"{key}")   # 第一個用 key 本身
                prefixes.append("")  # 第一個沒有前綴
            else:
                choices.append(f"{key}{idx}")  # 後面加序號
                prefixes.append(prefix)
    #choices.append("Back")
    return choices,prefixes 

async def tree_panel():
    while True:
        clear()
        stair_names,option_prefixes = assign_overview_options()
        options = [f"{prefix} {name}" for prefix, name in zip(option_prefixes, stair_names)]
        
        options.append("Back")
        choice = await select(
            "Overview",
            options
        ).ask_async(patch_stdout=True)

        if choice == "Back":
            return
        
        n=0
        for option in options:
            if choice == option:
               stair_name = stair_names[n]
               await cli_stair_panel.stair_panel(stair_name)
            n+= 1

