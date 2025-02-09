# from flask import Flask, render_template, request, redirect, url_for
# from loguru import logger
#
# llm_bot_server = Flask(__name__)
# llm_bot_server.secret_key = '114514'
# @llm_bot_server.route('/settings', methods=['GET', 'POST'])
# # def settings():
# #     settings_dict=config_data
# #     if request.method == 'POST':
# #         # 重定向到设置页面（或任何你想要的页面）
# #         return redirect(url_for('settings'))
#
#
#     # 渲染设置页面，并传递当前配置
#     # return render_template('settings.html', settings=settings_dict)
#
# @llm_bot_server.route("/", methods=["GET"])
# def index():
#     return "该接口正常工作"
#
#
# @llm_bot_server.route("/", methods=["POST"])
# def get_data():
#     logger.info("收到上报消息:")
#     logger.info(request.get_json())
#     process =ProcessMessage(request.get_json())
#     if config_data['test']=="D":
#         process.send_message_deepseek()
#     if config_data['test']=="L":
#         process.send_message_langchain()
#     return "ok"