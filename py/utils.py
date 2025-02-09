import os
import json

import requests
# import tiktoken


def get_path():
    path = os.path.abspath(os.getcwd())
    return path


def get_parent_path():
    path = os.path.abspath(os.getcwd())
    parent_dir = os.path.dirname(path)
    return parent_dir


def load_json_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        file = f.read()
        config_data = json.loads(file)
        return config_data


def write_json_file(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json_file = json.dumps(data, indent=4, ensure_ascii=False)
        f.write(json_file)
        f.close()


# def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
#     # Returns the number of tokens in a text string.
#     encoding = tiktoken.get_encoding(encoding_name)
#     num_tokens = len(encoding.encode(string))
#     return num_tokens


def search_serper_online(question, api_key):
    url = "https://cn2us02.opapi.win/api/v1/openapi/search/serper/v1"
    payload = {
        'q': question,
        'cache': '3',
        'gl': 'us',
        'hl': 'en',
        'page': '1',
        'num=': '10'
    }
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Authorization': api_key
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


def summary_answer(search_json):
    text = ""
    print("找到以下信息")
    for i in search_json["organic"]:
        try:
            text += (str(i['position']) + ". " + i["snippet"] + "\n")

        except:
            continue
    print(text)
    question = search_json["searchParameters"]["q"]
    url = "https://cn2us02.opapi.win/v1/chat/completions"

    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": f"请为我总结以下的几段文字，告诉我{question}是什么，尽可能的详细，包括时间地点人物"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    })
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Authorization': 'sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json()['choices'][0]['message']['content'])
    return response.json()['choices'][0]['message']['content']


def chat_with_gpt(system):
    url = "https://cn2us02.opapi.win/v1/chat/completions"

    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": system
            },
            # {
            #     "role": "user",
            #     "content": system
            # }
        ]
    })
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Authorization': 'sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    resp_json = response.json()
    print(resp_json)
    resp = resp_json['choices'][0]['message']['content']
    return resp

def check_user_memory_folder(uid:int,is_private:bool,is_group_bool):
    if is_private:
        pass


