# from loguru import logger
# from agent import Agent
# from send_message import SendMessage
# class ProcessMessage:
#     def __init__(self,data:dict):
#         self.data = data
#         self.time =data['time']
#         self.self_id =data['self_id']
#         self.post_type=data['post_type']
#         self.uid=None
#     def send_message_deepseek(self):
#         if self.post_type =="message":
#             if self.data.get('message_type') == 'private':# 如果是私聊信息
#                 sender = self.data.get('sender') # 获取发送者信息
#                 message = self.data.get('raw_message')  # 获取原始信息
#                 self.uid = sender.get('user_id')  # 获取信息发送者的 QQ号码
#                 nickname = sender.get('nickname') # 获取信息发送者的 QQ昵称
#                 logger.info(f"收到私聊消息:{nickname}({self.uid}):{message}")
#                 agent =Agent(uid=self.uid,nickname=nickname)
#                 answer = agent.run_deepseek_agent(message)
#                 logger.info(f"Agent返回消息:{answer}")
#                 SendMessage.send_private_message(uid=self.uid,message=answer)
#             # if self.data.get('message_type') == 'group':# 如果是私聊信息
#             #     messages =self.data.get('message')
#             #     li=[]
#             #     for message in messages:
#             #         if message['type']=="forward":
#             #             content =message['data']['content']
#             #             for i in content:
#             #                 for j in i['message']:
#             #                     if j['type']=="image":
#             #                         url=j['data']['url']
#             #                         li.append(url)
#             #                         print(url)
#             #     for i in li:
#             #         try:
#             #             parent_dir = get_parent_path()
#             #             path = f"{parent_dir}\\resource/sexy_img/group_sexy_img"
#             #             if not os.path.exists(path):
#             #                 os.makedirs(path)
#             #             files = os.listdir(path)  # 读入文件夹
#             #             num_png = len(files)
#             #             img_path = ""
#             #             headers = {
#             #                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
#             #             }
#             #             req = requests.get(
#             #                 url=i, headers=headers,verify=False
#             #             )
#             #             content = req.content
#             #             b = content
#             #             img_io = io.BytesIO(b)
#             #             img = Image.open(img_io)
#             #             print(img.format)
#             #             if url[-3:] == "png":
#             #                 img_path = f"{path}\\1-30_{num_png + 1}.png"
#             #                 with open(img_path, "wb") as f:
#             #                     f.write(content)
#             #                     f.close()
#             #             elif url[-3:] == "jpg":
#             #                 img_path = f"{path}\\1-30_{num_png + 1}.jpg"
#             #                 with open(img_path, "wb") as f:
#             #                     f.write(content)
#             #                     f.close()
#             #         except Exception as e:
#             #             print(f"err:{e}")
#             #
#             #
#             #     # self.uid = sender.get('user_id')  # 获取信息发送者的 QQ号码
#             #     # nickname = sender.get('nickname') # 获取信息发送者的 QQ昵称
#
#
#
#
