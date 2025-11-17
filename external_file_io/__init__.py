from .config_files import *
from .file_generators import *
from .lcs_runtime_io import *
from .stair_settings_io import *
from .node_settings_io import *
from .utils import *
from .state import *
from .database_io import *
from .file_exporters import *

def test_1():
    # 建立資料夾
    save_dir = Path("data/saves")
    #Path("C:/Users/file")
    save_dir.mkdir(parents=True, exist_ok=True)

    # 寫入 JSON
    #save_data = {"score": 1200, "player": "Bob"}
    #with open(save_dir / "save1.json", "w", encoding="utf-8") as f:
        #json.dump(save_data, f, indent=2)

    # 讀取 JSON
    with open(save_dir / "save1.json", "r", encoding="utf-8") as f:
        loaded = json.load(f)