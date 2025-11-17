
cli_config_format = {
  "projects_path": "",
  "export_path": "",
  "current_project": {
    "project_name"  : "",
    "LCS_tree_form": [],
    "instance_index" : ""
  }
}

project_config_format = {
    "project_name": "",
    "LCS_tree_form": "",
    "instance_index": 0,
    "instance_count": 1
}

instance_note_format = {
    "note": ""
}

prompts_format = {
    "stair_name": "",
    "prompts": {
        "default_prompt_note": "",
        "default_prompt_list": [""]*4,
        "assignment_prompt_note": "",
        "assignment_prompt": ""
    }
}

stair_data_format = {
    "node_name": "",
    "node_info": {
        "execution_status": "pending",  # pending, running, done
        "prompt_record": [],
        "response_record": [],
        "assignment_prompt_record": "",
        "assignment_record": [],
        "flux_image_url": ""
    },
    "node_settings": {
        "branch":{
            "enabled": True
        },
        "write_to_database": {
            "enabled": False,
            "input_index": 0,       #response  
            "output_index": 0       #database
        },
        "retry": {
            "enabled": False,
            "prompt_override_list": []
        }
    }
}

project_settings_format = {
    "stair_name": "",
	"stair_settings": {
        "import_from_database": {
            "enabled": False,
            "input_index": 0,          #database      
            "output_type":"assignment",   # or "default prompt"  prompt
	        "output_index": 0          #prompt
        },
        "pass_data_to_branches": {
            "enabled": True,
            "input_index": 0,          #response      
            "output_type":"assignment",   # or "default prompt"  branches_prompt
	        "output_index": 0          #branches_prompt
        },
        "assignment": {
            "enabled": True,    
            "output_type":"assignment",   # or "default prompt" branches_prompt
            "output_index": 0          #branches_prompt
        },
        "image_generation": {
            "enabled": False, 
            "input_index": 0,          #response
        }
	}
}

shared_database_format = {
	"data_list": [""]*16
}
