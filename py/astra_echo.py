from typing import overload
import requests
from flask import Flask, render_template, request, redirect, url_for
from loguru import logger
from py.utils import load_json_file,check_user_memory_folder
from openai import OpenAI

class AstraEcho:
    def __init__(self,
            port,
    ):
        self.port =port
        self.llm_bot_server=Flask(__name__)
        self.config_data=load_json_file('../config/config.json')
        self.api_key=self.config_data['openai']['OPENAI_API_KEY']
        self.api_base=self.config_data['openai']['OPENAI_API_BASE']
        self.model=self.config_data['openai']['OPENAI_MODEL']
        self.client=OpenAI(
            base_url=self.api_base,
            api_key=self.api_key,
        )
        self.uid =0
        self.session_data={}
    def begin(self):
        @self.llm_bot_server.route('/settings', methods=['GET', 'POST'])
        # def settings():
        #     settings_dict=config_data
        #     if request.method == 'POST':
        #         # 重定向到设置页面（或任何你想要的页面）
        #         return redirect(url_for('settings'))

        # 渲染设置页面，并传递当前配置
        # return render_template('settings.html', settings=settings_dict)

        @self.llm_bot_server.route("/", methods=["GET"])
        def index():
            return "该接口正常工作"

        @self.llm_bot_server.route("/", methods=["POST"])
        def get_message_data():
            logger.info("收到上报消息:")
            logger.info(request.get_json())
            self.session_data=request.get_json()
            self.process_message(self.session_data)
            return "ok"
    def run(self):
        self.llm_bot_server.run(port=self.port)
    def process_message(self,data:dict):
        if data['post_type'] == "message":
            if data.get('message_type') == 'private':  # 如果是私聊信息
                self.process_private_message()

    def process_private_message(self,):
        sender = self.session_data.get('sender')  # 获取发送者信息
        message = self.session_data.get('raw_message')  # 获取原始信息
        self.uid = int(sender.get('user_id'))  # 获取信息发送者的 QQ号码
        nickname = sender.get('nickname')  # 获取信息发送者的 QQ昵称
        logger.info(f"收到私聊消息:{nickname}<{self.uid}>:{message}")

        check_user_memory_folder(self.uid,)
        chat_message = [{'role': 'user', 'content': message}]
        answer = self.run_chat(chat_message)
        resp = answer.choices[0].message.content
        logger.info(f"{self.model}模型返回消息:{resp}")
        self.send_private_message(uid=self.uid, message=resp)
    @overload
    def run_chat(self,message:list):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            timeout=10
        )
        print(f"Response\n{response}")
        return response
    def run_chat(self,message:list):
        return "ok"
    def send_private_message(self,uid, message):
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

    # def send_message_deepseek(self):
    #     if self.post_type == "message":
    #         if self.data.get('message_type') == 'private':  # 如果是私聊信息
    #             sender = self.data.get('sender')  # 获取发送者信息
    #             message = self.data.get('raw_message')  # 获取原始信息
    #             self.uid = sender.get('user_id')  # 获取信息发送者的 QQ号码
    #             nickname = sender.get('nickname')  # 获取信息发送者的 QQ昵称
    #             logger.info(f"收到私聊消息:{nickname}({self.uid}):{message}")
    #             agent = Agent(uid=self.uid, nickname=nickname)
    #             answer = agent.run_deepseek_agent(message)
    #             logger.info(f"Agent返回消息:{answer}")
    #             SendMessage.send_private_message(uid=self.uid, message=answer)

