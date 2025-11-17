

from pathlib import Path
import json
import file_format
from pathlib import Path
CONFIG_DIR = Path("data/saves")
CONFIG_FILE = CONFIG_DIR / "cli_config.json"

from .config_files import *
from .lcs_runtime_io import *

# 檔案生成相關函式

def generate_external_files(inputForm):
    directory = Path("data/saves")
    directory.mkdir(parents=True, exist_ok=True)

    create_stair_data(directory,inputForm)
    create_prompts(directory,inputForm)
    create_project_settings(directory,inputForm)
    create_shared_database(directory)

def create_project(project_name: str, inputForm: dict):
    """
    建立新的專案資料夾，並在裡面生成 instance_0
    """
    config = read_cli_config()
    projects_root = Path(config["projects_path"])

    # 專案目錄 & instance_0
    project_dir = projects_root / project_name
    instance0_dir = project_dir / "instance_0"
    instance0_dir.mkdir(parents=True, exist_ok=True)

    # 呼叫你原本的檔案生成函式
    create_project_config(project_name,project_dir,inputForm)
    create_instance_note(instance0_dir, "Template")
    create_stair_data(instance0_dir, inputForm)
    create_prompts(instance0_dir, inputForm)
    create_project_settings(instance0_dir, inputForm)
    create_shared_database(instance0_dir)

    return project_dir

def create_project_config(project_name,directory,inputForm):
    project_config_data = file_format.project_config_format.copy()
    project_config_data["project_name"] = project_name
    project_config_data["LCS_tree_form"] = inputForm
    project_config_data["instance_index"] = 0
    project_config_data["instance_count"] = 1

    file_name = f"project_config.json"   
    file_path = directory / file_name    
    create_json_files(file_path, project_config_data)

def create_instance_note(directory,note=""):
    instance_note_data = file_format.instance_note_format.copy()
    instance_note_data["note"] = note

    file_name = f"instance_note.json"   
    file_path = directory / file_name    
    create_json_files(file_path, instance_note_data)   

def create_stair_data(directory,inputForm):
    
    total_branch_num = 1
    for layer_name, layer_sturture in inputForm.items():
        stair_num = 0
        
        for stair_index, branch_num in enumerate(layer_sturture):
            stair_num += 1
            # 判斷檔名
            stair_name = get_stair_name(layer_name=layer_name,stair_index=stair_index)
            file_name = f"{stair_name}.json"
            file_path = directory / file_name
            
            total_branch_num *= int(branch_num)
            
            project_settings_data = []
            for i in range(int(total_branch_num)):
                temp_format = file_format.stair_data_format.copy()
                temp_format["node_name"] = f"{stair_name}-{i+1}"
                project_settings_data.append(temp_format)
                
            #project_settings_data = [{"basic": 0, "s1": "None"} for _ in range(int(total_branch_num))]

            create_json_files(file_path, project_settings_data)

def create_prompts(directory,inputForm):
    stair_save_data = []
    
    for layer_name, layer_sturture in inputForm.items():
        for stair_index, branch_num in enumerate(layer_sturture):
            stair_name = get_stair_name(layer_name=layer_name,stair_index=stair_index)

            prompts_format = file_format.prompts_format.copy()
            prompts_format["stair_name"] = stair_name
            stair_save_data.append(prompts_format)
            #stair_save_data.append({"stair": stair_name, "branch number": branch_num})
            

    file_name = f"prompts.json"   
    file_path = directory / file_name    
    create_json_files(file_path, stair_save_data)

def create_project_settings(directory,inputForm):
    stair_save_data = []
    for layer_name, layer_sturture in inputForm.items():
        for stair_index, branch_num in enumerate(layer_sturture):
            stair_name = get_stair_name(layer_name=layer_name,stair_index=stair_index)

            project_settings_format = file_format.project_settings_format.copy()
            project_settings_format["stair_name"] = stair_name
            stair_save_data.append(project_settings_format)
            #stair_save_data.append({"stair": stair_name, "branch number": branch_num})
            

    file_name = f"project_settings.json"   
    file_path = directory / file_name    
    create_json_files(file_path, stair_save_data)

def create_shared_database(directory):
    shared_database_data = file_format.shared_database_format.copy()

    file_name = f"shared_database.json"   
    file_path = directory / file_name    
    create_json_files(file_path, shared_database_data)

def create_empty_instance(note=""):
    """
    在現有專案中建立新的 instance 資料夾
    """
    project_name = get_current_project_name()
    if not project_name:
        return None

    config = read_cli_config()
    projects_root = Path(config["projects_path"])
    project_dir = projects_root / project_name

    if not project_dir.exists():
        raise FileNotFoundError(f"專案資料夾不存在：{project_dir}")

    # 讀取專案設定檔以取得 LCS_tree_form
    project_config_path = project_dir / "project_config.json"
    if not project_config_path.exists():
        raise FileNotFoundError(f"找不到專案設定檔：{project_config_path}")

    project_config = json.loads(project_config_path.read_text(encoding="utf-8"))
    inputForm = project_config.get("LCS_tree_form", {})

    # 找出下一個 instance index
    project_config = json.loads(project_config_path.read_text(encoding="utf-8"))

    instance_count = project_config.get("instance_count", 1)  
    instance_count = instance_count+1

    new_instance_dir = project_dir / f"instance_{instance_count-1}"
    new_instance_dir.mkdir(parents=True, exist_ok=True)

    # 紀錄新的 instance index 回專案設定檔
    project_config["instance_count"] = instance_count

    project_config_path.write_text(json.dumps(project_config, indent=4, ensure_ascii=False), encoding="utf-8")

    # 呼叫你原本的檔案生成函式
    create_instance_note(new_instance_dir, note)
    create_stair_data(new_instance_dir, inputForm)
    create_prompts(new_instance_dir, inputForm)
    create_project_settings(new_instance_dir, inputForm)
    create_shared_database(new_instance_dir)

    set_current_project_instance_index(instance_count-1)

    return new_instance_dir

def create_instance_from_instance_0(note=""):
    """
    在現有專案中建立新的 instance 資料夾，內容從 instance_0 複製
    """
    project_name = get_current_project_name()
    if not project_name:
        return None

    config = read_cli_config()
    projects_root = Path(config["projects_path"])
    project_dir = projects_root / project_name

    if not project_dir.exists():
        raise FileNotFoundError(f"專案資料夾不存在：{project_dir}")

    instance0_dir = project_dir / "instance_0"
    if not instance0_dir.exists():
        raise FileNotFoundError(f"找不到 instance_0 資料夾：{instance0_dir}")

    # 找出下一個 instance index
    project_config_path = project_dir / "project_config.json"
    if not project_config_path.exists():
        raise FileNotFoundError(f"找不到專案設定檔：{project_config_path}")

    project_config = json.loads(project_config_path.read_text(encoding="utf-8"))

    instance_count = project_config.get("instance_count", 1)  
    instance_count = instance_count+1

    new_instance_dir = project_dir / f"instance_{instance_count-1}"
    new_instance_dir.mkdir(parents=True, exist_ok=True)

    # 複製 instance_0 的所有檔案到新的 instance 資料夾
    for item in instance0_dir.iterdir():
        if item.is_file() and item.suffix == ".json":
            target_file = new_instance_dir / item.name
            target_file.write_text(item.read_text(encoding="utf-8"), encoding="utf-8")

    # 更改 instance_note.json 的 note
    instance_note_path = new_instance_dir / "instance_note.json"
    #if instance_note_path.exists():
    instance_note = json.loads(instance_note_path.read_text(encoding="utf-8"))
    instance_note["note"] = note
    instance_note_path.write_text(json.dumps(instance_note, indent=4, ensure_ascii=False), encoding="utf-8")

    # 紀錄新的 instance index 回專案設定檔
    project_config["instance_count"] = instance_count

    project_config_path.write_text(json.dumps(project_config, indent=4, ensure_ascii=False), encoding="utf-8")

    set_current_project_instance_index(instance_count-1)

    return new_instance_dir

def create_json_files(file_path,save_data):

    if not file_path.exists():  
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)




