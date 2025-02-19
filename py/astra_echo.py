import json
import os
import re
import requests
from flask import Flask, render_template, request, redirect, url_for
from loguru import logger
from utils import load_json_file, write_json_file
from openai import OpenAI, NOT_GIVEN
from astra_tools import AstraTools


class AstraEcho:
    def __init__(self):
        self.nickname:str
        self.sender:str
        self.llm_bot_server:Flask = Flask(__name__)
        self.tools:AstraTools | NOT_GIVEN
        self.config_data_path = "../config/config.json"
        self.config_data = load_json_file(self.config_data_path)
        self.port = self.config_data['AstraEcho']['port']
        self.temp = self.config_data['AstraEcho']['model_temp']
        self.request_method = self.config_data['AstraEcho']['request_method']
        self.is_write_memory = self.config_data['AstraEcho']['is_write_memory']
        self.is_use_tools =self.config_data['AstraEcho']['is_use_tools']
        if self.is_use_tools:
            self.tools = AstraTools()
        else:
            self.tools = NOT_GIVEN
        self.debug_mode = self.config_data['AstraEcho']['debug_mode']
        if self.request_method == "api":
            self.api_key = self.config_data['openai']['OPENAI_API_KEY']
            self.api_base = self.config_data['openai']['OPENAI_API_BASE']
            self.model = self.config_data['openai']['OPENAI_MODEL']
        elif self.request_method == "local":
            self.api_key = self.config_data['local']['LOCAL_API_KEY']
            self.api_base = self.config_data['local']['LOCAL_API_BASE']
            self.model = self.config_data['local']['LOCAL_MODEL']
        else:
            raise ValueError("Invalid configuration provided. Please check your config.")

        self.client = OpenAI(
            base_url=self.api_base,
            api_key=self.api_key,
        )
        self.uid:int
        self.session_data = {}

    def _reset_instance(self):
        """重新实例化自身，并替换当前实例"""
        # 创建一个新的实例
        new_instance = AstraEcho()
        # 将当前实例的属性复制到新实例
        new_instance.__dict__.update(self.__dict__)
        # 替换当前实例
        self.__dict__.update(new_instance.__dict__)

    def begin(self):
        """初始化flask服务的路由"""

        @self.llm_bot_server.route("/", methods=["GET"])
        def index():
            return "该接口正常工作"

        @self.llm_bot_server.route("/", methods=["POST"])
        def get_message_data():
            logger.info("收到上报消息:")
            logger.info(request.get_json())
            self.session_data = request.get_json()
            self.process_message(self.session_data)
            return "ok"

        @self.llm_bot_server.route('/setting')
        def setting():
            config = self.read_config()
            return render_template('index.html', config=config)

        # 编辑配置文件的页面
        @self.llm_bot_server.route('/edit', methods=['GET', 'POST'])
        def edit():
            config = self.read_config()
            if request.method == 'POST':
                # 更新配置文件
                for key in request.form:
                    keys = key.split('.')  # 支持嵌套键（如 "database.host"）
                    current = config
                    for k in keys[:-1]:
                        if k not in current:
                            current[k] = {}
                        current = current[k]
                    current[keys[-1]] = request.form[key]
                self.save_config(config)
                self._reset_instance()
                redirect(url_for('setting'))
                return redirect(url_for('setting'))
            return render_template('edit.html', config=config)

    def run(self):
        self.llm_bot_server.run(port=self.port, debug=self.debug_mode)

    def process_message(self, data: dict):
        if data['post_type'] == "message":
            if data.get('message_type') == 'private':
                if self.process_message_command_private():  # 如果是私聊信息
                    return "ok"
                self.process_private_message()

    def process_message_command_private(self) -> bool:
        command_dict = {
            "/获取会话": "获取当前会话信息",
            "/更改人格+ 你需要设定的人格 ": "更改当前会话中的人格"

        }
        message = self.session_data.get('raw_message')
        memory_json = self.load_private_memory()
        if message.strip().startswith("/获取会话"):
            resp = "当前会话信息为：\n"
            resp += f"窗口类型:\n"
            resp += f"QQ:{self.uid}+\n"
            resp += f"昵称:{self.nickname}+\n"
            resp += f"模型:{self.model}+\n"
            role_dict = memory_json['memory'][0]
            if role_dict['role'] == "system":
                resp += f"人格:{role_dict['content']}\n"
            else:
                resp += f"人格:未找到配置，人格文件出错！\n"
            resp += f"AstraEchoAI名称:{memory_json['config']['AI_Name']}"

        if message.strip().startswith("/"):
            resp = "test"

        else:
            return False
        self.send_private_message(self.uid, resp)
        return True

    def process_private_message(self):
        """处理私人信息"""
        self.sender = self.session_data.get('sender')  # 获取发送者信息
        message = self.session_data.get('raw_message')  # 获取原始信息
        self.uid = int(self.sender.get('user_id'))  # 获取信息发送者的 QQ号码
        self.nickname = self.sender.get('nickname')  # 获取信息发送者的 QQ昵称
        logger.info(f"收到私聊消息:{self.nickname}<{self.uid}>:{message}")
        memory_json = self.load_private_memory()
        memory_json['memory'].append({'role': 'user', 'content': message})
        chat_message = memory_json['memory']
        answer = ''
        if self.request_method == "local":
            answer = self.run_chat_local(chat_message)
        elif self.request_method == "api":
            answer = self.run_chat_openai(chat_message)
        resp = answer.choices[0].message.content
        logger.info(f"{self.model}模型返回消息:{resp}")
        if '<think>' in resp:
            pattern = r'<think>.*?</think>'
            resp = re.sub(pattern, '', resp, flags=re.DOTALL).strip()
        memory_json['memory'].append({'role': 'assistant', 'content': resp})
        if self.is_write_memory:
            self.write_private_memory(memory_json)
        self.send_private_message(uid=self.uid, message=resp)

    def run_chat_openai(self, message: list):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            tools=self.tools,
            timeout=10,
            top_p=self.temp
        )
        print(f"Response\n{response}")
        return response

    def run_chat_local(self, message: list):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            tools=self.tools,
            top_p=self.temp
        )
        print(f"Response\n{response}")
        return response

    def send_private_message(self, uid, message):
        try:
            print(message)
            res = requests.post(url=self.config_data['qq_bot']['cqhttp_url'] + "/send_private_msg",
                                params={'user_id': uid, 'message': message}).json()
            if res["status"] == "ok":
                logger.info("私聊消息发送成功")
                return "私聊消息发送成功"
            else:
                logger.info(res)
                logger.info("私聊消息发送失败，错误信息：" + str(res['wording']))
                return "私聊消息发送失败，错误信息：" + str(res['wording'])
        except Exception as error:
            logger.error("私聊消息发送失败")
            logger.error(error)
            return "私聊消息发送失败"

    def check_user_memory_folder(self, is_private: bool = False, is_group_bool: bool = False):
        if is_private:
            memory_path = f"../memory/private/{self.uid}"
            if not os.path.exists(memory_path):
                os.makedirs(memory_path)
                with open(memory_path + f"/{self.uid}.json", "w") as f:
                    data = {
                        "config": {
                            "AI_Name": "AstraEcho"
                        },
                        "memory": [{
                            "role": "system",
                            "content": "You' are a helpful assistant"
                        }
                        ]
                    }
                    f.write(json.dumps(data, indent=4, ensure_ascii=False))
                    f.close()
        if is_group_bool:
            memory_path = f"../memory/group/{self.uid}"
            if not os.path.exists(memory_path):
                os.makedirs(memory_path)
                with open(memory_path + f"/{self.uid}.json", "w") as f:
                    data = {
                        "config": {
                            "AI_Name": "AstraEcho"
                        },
                        "memory": [{
                            "role": "system",
                            "content": "You' are a helpful assistant"
                        }]
                    }
                    f.write(json.dumps(data, indent=4, ensure_ascii=False))
                    f.close()
        else:
            return "ERROR"

    def load_private_memory(self):
        self.check_user_memory_folder(is_private=True)
        memory_json = load_json_file(f"../memory/private/{self.uid}/{self.uid}.json")
        return memory_json

    def write_private_memory(self, data):
        write_json_file(f"../memory/private/{self.uid}/{self.uid}.json", data)

    def read_config(self):
        return self.config_data

    # 保存配置文件
    def save_config(self, config):
        with open(self.config_data_path, 'w') as f:
            json.dump(config, f, indent=4)  # 使用 indent 格式化 JSON
