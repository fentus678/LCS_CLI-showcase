import asyncio
import os
import logging
#logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
import transcode
import external_file_io
import bfl_flux_manager
from openai import AsyncOpenAI

if_api_key_assigned: bool = False

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    openai_api_key = ""
client = AsyncOpenAI(api_key=openai_api_key)
messages = [{"role": "user", "content": ""},]
all_tasks = []

def initialize_gpt_api():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        openai_api_key = ""
    global if_api_key_assigned
    if openai_api_key != "":
        if_api_key_assigned = True

def reset_LCS_recursive(node):
    external_file_io.clean_node_record(node)
    for child in node.children:
        reset_LCS_recursive(child)

async def run_LCS_recursive(node):
    if node.parent:
        await node.parent.asyncio_event.wait()
    
    #await asyncio.sleep(0.1)

    node.response_text = await run_chat(node)
    await run_image_generation(node)
    external_file_io.proccess_db_write(node)
    external_file_io.write_execution_status(node,"done")
    #print_node_chat(node)

    if external_file_io.get_if_enableBranch(node) == False:
        return
    
    node.asyncio_event.set()
    tasks = [asyncio.create_task(run_LCS_recursive(child)) for child in node.children]
    if tasks:
        await asyncio.gather(*tasks)  # 等待所有子節點完成
 
async def run_chat(node):
    prompt_list = external_file_io.get_prompt(node)
    assignment_prompt_text = external_file_io.get_assignment_prompt(node)
    response_text = ""

    if external_file_io.get_execution_status(node) == "done":
        return node.response_text

    external_file_io.clean_node_record(node)
    external_file_io.write_execution_status(node,"running")
    messages = []

    if prompt_list:
        for prompt_text in prompt_list:
            if prompt_text == "":
                break
            messages.append({"role": "user", "content": prompt_text})
        
            response_completion = await client.chat.completions.create(model="gpt-5-mini", messages=messages)
            response_text = response_completion.choices[0].message.content
            messages.append({"role": "assistant", "content": response_text})

            external_file_io.add_record(node,prompt_text=prompt_text, response_text=response_text)
    
    if assignment_prompt_text != "":
        messages.append({"role": "user", "content": assignment_prompt_text})
        #messages = [{"role": "user", "content": assignment_prompt_text}]
        response_list = []  # 先存起來

        # 先拿第一個回覆
        response_completion = await client.chat.completions.create(model="gpt-5-mini",messages=messages)
        response_text = response_completion.choices[0].message.content
        messages.append({"role": "assistant", "content": response_text})
        response_list.append(response_text)

        # 針對每個 child，依序再問
        for i in range(len(node.children)):
            # 加入新問題
            messages.append({"role": "user", "content": f"{i+1}."})

            # 呼叫 API
            response_completion = await client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages
            )
            response_text = response_completion.choices[0].message.content

            # 把回答也加進去，並存起來
            messages.append({"role": "assistant", "content": response_text})
            response_list.append(response_text)

        external_file_io.add_assignment_record(node,prompt_text=assignment_prompt_text, response_list=response_list)

    return response_text

async def run_image_generation(node):
    prompt_text = external_file_io.get_image_generation_prompt(node)
    if prompt_text == "":
        return
    
    image_url = await bfl_flux_manager.flux_generate_image(prompt_text)
    if image_url != "":
        external_file_io.add_image_url_record(node,image_url)
        external_file_io.add_image_record(node,image_url)

def print_node_chat(node):
    if node.parent:
        print(f"node：{node.name} parent text：{node.parent.response_text} response：{node.response_text}" )
    else:
        print(f"node：{node.name} first text：{node.response_text}")

async def reset_LCS(): 
    LCS_tree_recursionForm_roots, _ = transcode.input_to_recursionForm(transcode.LCS_tree_inputForm)
    for i in LCS_tree_recursionForm_roots:
        reset_LCS_recursive(i)

async def run_LCS():
    LCS_tree_recursionForm_roots, _ = transcode.input_to_recursionForm(transcode.LCS_tree_inputForm)
    await asyncio.gather(*(run_LCS_recursive(i) for i in LCS_tree_recursionForm_roots))


#external_file_io.generate_external_files(transcode.LCS_tree_inputForm)
#external_file_io.clean_db()