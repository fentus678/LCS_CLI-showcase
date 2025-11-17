from questionary import select, Separator
import questionary
import os
from os import system, name
import asyncio
import subprocess
import cli_manager.cli_tree_panel as cli_tree_panel
import transcode
import external_file_io
from pathlib import Path
import lcs_manager
import bfl_flux_manager
import cli_manager.cli_utils as cli_utils
import cli_manager.state as state


def clear():
    os.system("cls" if os.name == "nt" else "clear")

async def run_cli():
    clear()
    current_project_name = external_file_io.get_current_project_name()
    current_project_instance = external_file_io.get_current_instance_index()
    choice = await select(
        f"Project Name: {current_project_name} #{current_project_instance}",
        choices=[
            Separator(),
            "File",
            "Settings",
            "Run LCS",
            "Tree Panel",
            "Database",
            Separator(),
            "Exit"
     ]
    ).ask_async(patch_stdout=True)
    if choice == "File":
        await file()
    elif choice == "Settings":
        await main_menu_settings()
    elif choice == "Run LCS":
        await run_lcs()
    elif choice == "Tree Panel":
        external_file_io.assign_save_dir()
        await cli_tree_panel.tree_panel()
    elif choice == "Database":
        await set_database()
    elif choice == "Exit":
        print("👋 Program ended. Thank you for using!")
        return False
    return True

# file

async def file():
    while True:
        clear()
        current_project_name = external_file_io.get_current_project_name()
        current_project_instance = external_file_io.get_current_instance_index()
        project_title = f"Project Name: {current_project_name} #{current_project_instance}"
        choice = await select(
            project_title,
            choices=[
                Separator(),
                "Open Project",
                "Create Project",
                "Set Up Instance",
                "Export",
                Separator(),
                "Back"
        ]
        ).ask_async(patch_stdout=True)

        if_back_to_menu = False
        if choice == "Open Project":
            if_back_to_menu = await open_project()
        elif choice == "Create Project":
            if_back_to_menu= await create_project()
        elif choice == "Set Up Instance":
            if_back_to_menu = await setup_instance()
        elif choice == "Export":
            if_back_to_menu = await export()
        elif choice == "Back":
            return
        
        if if_back_to_menu == True:
            return

# open and create project

async def open_project():
    while True:
        clear()
        current_project_name = external_file_io.get_current_project_name()
        print(f"(Current: {current_project_name})") 

        options = assign_options("Open Project")
        
        choice = await select(
            f"Selcet Project ",
            options
        ).ask_async(patch_stdout=True)
        
        if choice == "Back":
            return False
        else:
            for option in options:
                if choice == option:
                    await replace_current_project(option)
                    external_file_io.open_project()
                    external_file_io.assign_save_dir()
                    return True
        
async def replace_current_project(project_name: str):
    external_file_io.set_current_project(project_name)
    input("\nPress Enter to return to the main menu...")

def parse_lcs_input(user_input: str) -> dict[str, list[str]] | None:
    tokens = user_input.strip().split()
    print("DEBUG tokens:", tokens)  # 👉 用來觀察實際分割結果
    result: dict[str, list[str]] = {}
    current_layer = None

    for token in tokens:
        token = token.strip()  # 先清理一下
        if not token:  # 空字串跳過
            continue

        if token.isalpha():  # Layer 名稱
            current_layer = token.upper()
            if current_layer in result:
                print(f"⚠️ Layer {current_layer} 已經定義過了")
                return None
            result[current_layer] = []
        elif token.isdigit():  # Stair 數量
            if current_layer is None:
                print(f"⚠️ 數字 {token} 前缺少 Layer 名稱")
                return None
            num = int(token)
            if num <= 0 or num > 10:
                print(f"⚠️ Layer {current_layer} 的 Stair 數必須在 1–10 之間 (得到 {num})")
                return None
            result[current_layer].append(str(num))
        else:
            print(f"⚠️ 非法輸入: {token!r}")
            return None

    # 確認每個 Layer 至少有一個 Stair
    for layer, stairs in result.items():
        if not stairs:
            print(f"⚠️ Layer {layer} 沒有任何 Stair 數量")
            return None

    return result

async def create_project():
    
    name = await asign_project_name()
    if not name:
        return False
    tree = await asign_LCS_structure()

    if tree:
        transcode.LCS_tree_inputForm = tree
        #external_file_io.generate_external_files(transcode.LCS_tree_inputForm)
        external_file_io.create_project(name,transcode.LCS_tree_inputForm)
        await replace_current_project(name)
        external_file_io.open_project()
        external_file_io.assign_save_dir()
        return True
    else:
        return False

async def asign_project_name():
    clear()
    print("(Type 'b' to go back)")
    while True:
        
        question_title = (
            "Assign Project name"
        )
        value = await questionary.text(question_title).ask_async()

        if value is None:  # 使用者可能按 Ctrl+C
            return None
        if value.lower() in ("b", "back"):
            return None
        elif value.strip():
            return value.strip()

async def asign_LCS_structure():
    clear()
    print("(Type 'b' to go back)")
    print("(e.g., A 2 B 2 C 1 1 → A with 2 stairs, B with 2 stairs, C with 2 stairs):")
    while True:
        
        question_title = (
            "Assign LCS structure "
        )
        value = await questionary.text(question_title).ask_async()

        if value is None:  # 使用者可能按 Ctrl+C
            return None
        if value.lower() in ("b", "back"):
            return None

        tree = parse_lcs_input(value)
        if tree:
            return tree
        else:
            clear()
            print("(Type 'b' to go back)")
            print("(e.g., A 2 B 2 C 1 1 → A with 2 stairs, B with 2 stairs, C with 2 stairs):")
            print("Invalid input. Please try again.")

# run lcs

async def run_lcs():
    clear()
    if lcs_manager.if_api_key_assigned == False:
        print("⚠️ OpenAI API Key not set. Please set it in Settings first.")
        input("\nPress Enter to return to the main menu...")
        return

    if_runned = False
    if not state.run_lcs_task and not state.reset_lcs_task:
        state.reset_lcs_task = asyncio.create_task(lcs_manager.reset_LCS())
        state.run_lcs_task = asyncio.create_task(lcs_manager.run_LCS())
        if_runned = True
    
    if state.run_lcs_task and state.reset_lcs_task:
        if not state.reset_lcs_task.done():
            print("LCS reset in progress...")
            input("\nPress Enter to return to the main menu...")
        elif state.reset_lcs_task.done() and not state.run_lcs_task.done():
            print("LCS is running...")
            input("\nPress Enter to return to the main menu...")
        elif state.run_lcs_task.done() and state.reset_lcs_task.done():
            if if_runned == False:
                state.reset_lcs_task = asyncio.create_task(lcs_manager.reset_LCS())
                state.run_lcs_task = asyncio.create_task(lcs_manager.run_LCS())
                if_runned = True
            print("LCS reset in progress...")
            input("\nPress Enter to return to the main menu...")
    return

# set up instance

async def open_instance():
    while True:
        clear()
        current_instance_index = external_file_io.get_current_instance_index()
        print(f"(Current: instance_{current_instance_index})")

        instance_names,instance_notes = assign_options("Open Instance")
        options = [f"{name}   ({note})" for name, note in zip(instance_names, instance_notes)]
        options.append("Back")
        choice = await select(
            "Options",
            options
        ).ask_async(patch_stdout=True)

        if choice == "Back":
            return False
        for option in options:
            if choice == option:
                instance_index = int(option.split()[0].split("_")[1])
                external_file_io.set_current_project_instance_index(instance_index)
                external_file_io.assign_save_dir()
                return True
        
async def create_instance():
    note = ""
    note = await assign_instance_note()
    if note is None:
        return
    while True:
        clear()
        choice = await select(
            f"Create Instance | Note: {note}",
            choices=[
                "Create from Template",
                "Create empty",
                "Cancel",
        ]
        ).ask_async(patch_stdout=True)

        if choice == "Create from Template":
            external_file_io.create_instance_from_instance_0(note)
            external_file_io.assign_save_dir()
            input("\nPress Enter to return to the main menu...")
            return True
        elif choice == "Create empty":
            external_file_io.create_empty_instance(note)
            input("\nPress Enter to return to the main menu...")
            return True
        elif choice == "Cancel":
            return False

async def assign_instance_note():
    clear()
    print("(Type 'b' to go back)")
    print("New instance number:", external_file_io.get_current_instance_index()+1)
    while True:
        
        question_title = (
            "Assign Instance note"
        )
        value = await questionary.text(question_title).ask_async()

        if value is None:  # 使用者可能按 Ctrl+C
            return None
        if value.lower() in ("b", "back"):
            return None
        elif value.strip():
            return value.strip()

# export

async def setup_instance():
    while True:
        clear()
        choice = await select(
            "Set Up Instance",
            choices=[
                "Open Existing",
                "Create New",
                "Back"
            ]
        ).ask_async(patch_stdout=True)

        if choice == "Open Existing":
            if_back_to_menu = await open_instance()
            if if_back_to_menu == True:
                return True
        elif choice == "Create New":
            if_back_to_menu= await create_instance()
            if if_back_to_menu == True:
                return True
        elif choice == "Back":
            break

def assign_export_by_stair_options():
    options = cli_utils.get_stair_names_list()
    options.append("Back")
    
    return options

def assign_export_options():
    options = [
        ".docx",
        ".png",
        "Back"
    ]
    return options

async def export():
    while True:
        clear()
        choices = assign_export_options()
        choice = await select(
            "Export",
            choices
        ).ask_async(patch_stdout=True)

        if choice in choices:
            if choice == "Back":
                return False
            elif choice == ".png":
                return await export_png()
            elif choice == ".docx":
                return await export_docx()
            else:
                external_file_io.export_docx(choice)
                #external_file_io.export_images(choice)
                return True

async def export_png():
    while True:
        clear()
        options = assign_export_by_stair_options()
        choice = await select(
            "Export image (.png)",
            options
        ).ask_async(patch_stdout=True)

        if choice in options:
            if choice == "Back":
                return False
            else:
                external_file_io.export_images(choice)
                return True

def assign_export_docx_options():
    options = [
        "Single Stair",
        "Compound",
        "Back"
    ]
    return options

async def export_docx():
    while True:
        clear()
        options = assign_export_docx_options()
        choice = await select(
            "Export .docx",
            options
        ).ask_async(patch_stdout=True)

        if choice in options:
            if choice == "Back":
                return False
            elif choice == "Single Stair":
                return await export_docx_single_stair()
            elif choice == "Compound":
                return await export_docx_compound()

async def export_docx_single_stair():
    while True:
        clear()
        options = assign_export_by_stair_options()
        choice = await select(
            "Export .docx (Single Stair)",
            options
        ).ask_async(patch_stdout=True)

        if choice in options:
            if choice == "Back":
                return False
            else:
                external_file_io.export_docx(choice)
                return True

def assign_export_docx_compound_options():
    options = [
        "Text + Images",
        "Images + Text",
        "Text + Text",
        Separator(),
        "Back"
    ]
    return options

async def export_docx_compound():
    while True:
        clear()
        options = assign_export_docx_compound_options()
        choice = await select(
            "Export .docx (Compound)",
            options
        ).ask_async(patch_stdout=True)

        if choice in options:
            if choice == "Back":
                return False
            elif choice in ("Text + Images", "Images + Text", "Text + Text"):
                return await export_docx_compound_features(choice)

def assign_export_docx_compound_features_second_stair(first_stair:str):
    stair_names = cli_utils.get_stair_names_list()
    _,first_branch_counts = cli_utils.get_branch_counts(first_stair)
    options = []
    for stair_name in stair_names:
        if stair_name != first_stair:
            _,second_branch_counts = cli_utils.get_branch_counts(stair_name)
            if first_branch_counts == second_branch_counts:
                options.append(stair_name)
    options.append("Back")
    return options

async def export_docx_compound_features(feature:str):
    if feature not in ("Text + Images", "Images + Text", "Text + Text"):
        return False
    first_stair =""
    second_stair =""
    while True:
        clear()
        options = assign_export_by_stair_options()
        choice = await select(
            f"Export .docx (Compound) | {feature} | First Stair",
            options
        ).ask_async(patch_stdout=True)

        if choice in options:
            if choice == "Back":
                return False
            else:
                first_stair = choice
                break
    while True:
        clear()
        options = assign_export_docx_compound_features_second_stair(first_stair)
        choice = await select(
            f"Export .docx (Compound) | {feature} | Second Stair",
            options
        ).ask_async(patch_stdout=True)

        if choice in options:
            if choice == "Back":
                return False
            else:
                second_stair = choice
                break
    if first_stair and second_stair:
        external_file_io.export_docx_compound(first_stair,second_stair,feature)
        return True
            
# main menu settings

async def main_menu_settings():
    clear()
    while True:
        
        choice = await select(
            f"Settings",
            choices=[
                Separator(),
                "Set Projects Path",
                "Set Export Path",
                "Set OpenAI API Key",
                "Set BFL Flux API Key",
                Separator(),
                "Back"
        ]
        ).ask_async(patch_stdout=True)

        if choice is None:  # 使用者可能按 Ctrl+C
            return None
        if choice.lower() in ("b", "back"):
            return None
        if choice == "Set Projects Path":
            await set_projects_path()
            external_file_io.assign_save_dir()
            return None
        if choice == "Set Export Path":
            await set_export_path()
            external_file_io.assign_export_dir()
            return None
        if choice == "Set OpenAI API Key":
            await set_api_key("OPENAI_API_KEY")
            lcs_manager.initialize_gpt_api()
            return None
        if choice == "Set BFL Flux API Key":
            await set_api_key("BFL_FLUX_API_KEY")
            bfl_flux_manager.initialize_bfl_flux_api()
            return None

async def set_projects_path():
    while True:
        clear()
        current_path = external_file_io.get_projects_root()
        print(f"Current Projects Path: {current_path}")
        choice = await select(
            f"Set Projects Path",
            choices=[
                "Reset to Default",
                "Assign New Path",
                "Back"
        ]
        ).ask_async(patch_stdout=True)

        if choice is None:  # 使用者可能按 Ctrl+C
            return None
        if choice.lower() in ("b", "back"):
            return None
        if choice == "Reset to Default":
            await reset_projects_path()
            return None
        if choice == "Assign New Path":
            path = await assign_projects_path()
            if path:
                print(f"Projects path set to: {path}")
                input("\nPress Enter to return to the main menu...")
            return None

async def reset_projects_path():
    external_file_io.set_cli_config_projects_path("data/saves/projects")
    path = external_file_io.get_projects_root()
    if not Path(path).exists():
        Path(path).mkdir(parents=True, exist_ok=True)
    print(f"Projects path reset to default: {path}")
    input("\nPress Enter to return to the main menu...")

async def assign_projects_path():
    clear()
    print("(Type 'b' to go back)")
    while True:
        
        question_title = (
            "Assign Project path (e.g., data/saves/projects)"
        )
        value = await questionary.text(question_title).ask_async()

        if value is None:  # 使用者可能按 Ctrl+C
            return None
        if value.lower() in ("b", "back"):
            return None
        elif value.strip():
            path = value.strip()
            external_file_io.set_cli_config_projects_path(path)
            if not Path(path).exists():
                Path(path).mkdir(parents=True, exist_ok=True)
            return 

async def set_export_path():
    while True:
        clear()
        current_path = external_file_io.get_export_path()
        print(f"Current Export Path: {current_path}")
        choice = await select(
            f"Set Export Path",
            choices=[
                "Reset to Default",
                "Assign New Path",
                "Back"
        ]
        ).ask_async(patch_stdout=True)

        if choice is None:  # 使用者可能按 Ctrl+C
            return None
        if choice.lower() in ("b", "back"):
            return None
        if choice == "Reset to Default":
            await reset_export_path()
            return None
        if choice == "Assign New Path":
            path = await assign_export_path()
            if path:
                print(f"Export path set to: {path}")
                input("\nPress Enter to return to the main menu...")
            return None

async def reset_export_path():
    external_file_io.set_cli_config_export_path("data/exports")
    path = external_file_io.get_export_path()
    if not Path(path).exists():
        Path(path).mkdir(parents=True, exist_ok=True)
    print(f"Export path reset to default: {path}")
    input("\nPress Enter to return to the main menu...")

async def assign_export_path():
    clear()
    print("(Type 'b' to go back)")
    while True:
        
        question_title = (
            "Assign Export path (e.g., data/exports)"
        )
        value = await questionary.text(question_title).ask_async()

        if value is None:  # 使用者可能按 Ctrl+C
            return None
        if value.lower() in ("b", "back"):
            return None
        elif value.strip():
            path = value.strip()
            external_file_io.set_cli_config_export_path(path)
            if not Path(path).exists():
                Path(path).mkdir(parents=True, exist_ok=True)
            return 

async def set_api_key(key_name: str):
    clear()
    print("(Type 'b' to go back)")
    print(f"(Current {key_name}: {'Set' if os.getenv(key_name) else 'Not Set'})")
    while True:
        
        question_title = (
            f"Set {key_name}"
        )
        value = await questionary.text(question_title).ask_async()

        if value is None:  # 使用者可能按 Ctrl+C
            return None
        if value.lower() in ("b", "back"):
            return None
        elif value.strip():
            set_environment_variable(key_name, value.strip())
            return

def set_environment_variable(key: str, value: str):
    subprocess.run(["setx", key, value], shell=True)
    os.environ[key] = value

# set database

def assign_database_choices():
    choices=[]

    for i in range(16):
        data_text = external_file_io.get_db_data(i)
        data_text = cli_utils.wrap_text_by_width(data_text)
        if data_text == "":
            choices.append(f"{i+1}")
        else:
            choices.append(f"{i+1} {data_text}")

    choices.append(Separator())
    choices.append("Back")
    return choices   

async def set_database():
    while True:
        clear()
        options = assign_database_choices()
        choice = await select(
            "Database",
            options
        ).ask_async(patch_stdout=True)

        i = 0
        for option in options:
            if choice == "Back":
                return
            elif choice == option:
                await set_db_text(i)
            i = i+1  
            
async def set_db_text(db_index):
    question_title = f"No.{db_index+1}"

    current_value = external_file_io.get_db_data(db_index)

    clear()
    print("(Type 'b' to go back, 'c' to clear saved text)")
    print("(Press Ctrl + U to clear the line)")

    while True:
        value = await questionary.text(
            f"{question_title}",
            default=current_value or ""  # 預設填入既有內容
        ).ask_async()

        
        if value is None:   
            return
        if value.lower() == "b" or value.lower() == "back":
            return
        if value != "":
            external_file_io.set_db_data(db_index,value)
            return
        
# utils

def scan_projects(projects_root: str | Path) -> list[str]:
    """回傳專案資料夾名稱清單"""
    root = Path(projects_root)
    if not root.exists():
        return []
    return [p.name for p in root.iterdir() if p.is_dir()]

def assign_options(option_type: str):
    if option_type == "Open Project":
        projects_root = Path(external_file_io.get_projects_root())  # 這裡可以從 config 讀
        choices = scan_projects(projects_root)
        choices.append("Back")   # 永遠加一個返回選項
        return choices
    elif option_type == "Open Instance":
        current_project_dir = Path(external_file_io.get_current_project_path())
        instance_dirs = [
            d.name for d in current_project_dir.iterdir()
            if d.is_dir() and d.name.startswith("instance_")
        ]
        #從新到舊排序
        instance_dirs.sort(key=lambda x: int(x.split("_")[1]), reverse=True)
        #確保 instance_0 在最前面
        if "instance_0" in instance_dirs:
            instance_dirs.remove("instance_0")
            instance_dirs.insert(0, "instance_0") 
        choices = instance_dirs + ["Back"]

        instance_note = []
        #尋找每個 instance 的 note
        for instance in instance_dirs:
            instance_dir = current_project_dir / (instance if instance != "template (instance_0)" else "instance_0")
            instance_note_path = instance_dir / "instance_note.json"
            if instance_note_path.exists():
                note_data = external_file_io.read_json_file(instance_note_path)
                instance_note.append(note_data.get("note", ""))
            else:
                instance_note.append("")
        
        return choices,instance_note
    else:
        choices=[
            "1",
            "2",
            "3",
            "Back" 
        ]
        return choices