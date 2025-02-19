import json

import requests

from tool import Tool, astratool


class AstraTools(Tool):
    """
    这里是 Astra Echo 的工具类，用于编写自定义工具
    编写函数的规范:
    1.所有函数必须添加 @astratool 装饰器
    2.函数输入的变量必须给予类型限定，例如： a:int ,x:str , c:None
    3.必须添加注释


    下方编写了两个示例函数
    """

    @astratool
    def sum(self, x: int, y: int):
        """
        Get the result of adding two numbers, the user should supply two numbers to start with.
        :param x: First number.
        :param y: Second number
        :return: the plus
        """
        return x + y

    @astratool
    def multiply(self, a: int, b: int):
        """
        Multiply two numbers.
        :param a: First number.
        :param b: Second number.
        :return: The product.
        """
        return a * b

    @astratool
    def turn_light(self, state: str):
        """
        Change the light ,for example turn_on and turn_off
        :param state:The state you should change you MUST input 'turn_on' or 'turn off' command and Do not omit '_'
        :return:
        """
        if state == "turn off":
            state = "turn_off"
        elif state == "turn on":
            state = "turn_on"
        api = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZjUwNWQ2ZDVkOTM0M2Q1OGY2NjlmYjJiNWM1OTVjYiIsImlhdCI6MTczOTYzMzM5MywiZXhwIjoyMDU0OTkzMzkzfQ.3Hm6AheiI78wmI5y_jE8xM8-BOeSVwSK4Agwe7uxmdc"
        post_url = "http://192.168.31.190:8123/api/services/light/" + state
        headers = {
            "Authorization": "Bearer " + api,
            "content-type": "application/json",

        }
        data = {
            "entity_id": "light.yeelink_lamp22_0a61_light"

        }
        post_response = requests.request("POST", post_url, headers=headers, data=json.dumps(data))
        print(post_response)
        print(post_response.json())
        return "success"
