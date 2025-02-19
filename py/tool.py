import inspect
import re
from openai.types.chat import ChatCompletionMessageToolCall


# 定义 @astratool 装饰器
def astratool(func):
    """
    标记使用了 @astratool 装饰器的方法。
    """
    func.is_astratool = True  # 添加标记
    return func


class Tool:
    def __init__(self):
        """
        在实例化时提取所有使用了 @astratool 的方法信息
        """
        self.tool_methods:dict = {}  # 存储方法信息
        self.tool_list:list[dict] = []
        self._extract_tool_methods()

    def _extract_tool_methods(self):
        """
        提取所有使用了 @astratool 的方法信息。
        """
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, 'is_astratool') and method.is_astratool:
                # 获取方法签名和注释
                method_info = {
                    'name': name,
                    'method':method,
                    'doc': method.__doc__,
                    'signature': str(inspect.signature(method)),
                    'annotations': method.__annotations__,
                }
                self.tool_methods[name] = method_info
                self.tool_list.append(self._parse_function_info(name))

    def _parse_function_info(self, name) -> dict:
        """
        解析工具函数的信息
        :param name: 工具函数的名称
        :return: json格式的工具函数信息
        """
        method = self.tool_methods[name]
        model = {
            "type": "function",
            "function": {
                "name": "",
                "description": "",
                "parameters": {
                    "type": "object",
                    "properties": {
                    },
                    "required": []
                },
            }
        }
        name = method['name']
        model['function']['name'] = name
        function = model['function']
        comment = method['doc']
        # 提取函数描述
        try:
            function_description = re.search(r'^(.*?)(?=:param|:return|$)', comment, re.DOTALL)
            if function_description:
                function_description = function_description.group(1).strip()
                function['description'] = function_description
            else:
                function_description = None
                ValueError(f"Init failed ,method <{method['method'].__name__}> error")
        except TypeError as t:
            raise ValueError(f"Init failed ,method <{method['method'].__name__}> error")


            # 提取参数名称和描述
        params = re.findall(r':param (\w+):(.*?)(?=\n|$)', comment, re.DOTALL)
        if not params:
            params = None
        else:
            for param_name, param_desc in params:
                param_type = "string"
                # if param_type == "str":
                #     param_type = "string"
                param_value = {
                    "type": param_type,
                    "description": param_desc
                }
                function['parameters']['properties'].setdefault(param_name, param_value)
                function['parameters']['required'].append(param_name)
        # 提取返回值
        return_value = re.search(r':return:(.*?)(?=\n|$)', comment, re.DOTALL)
        if return_value:
            return_value = return_value.group(1).strip()
        else:
            return_value = None

        return model

    def tool_parser(self,tools_call: list[ChatCompletionMessageToolCall]):
        """
        工具解析器，用于将LLM生成的工具调用消息解析成可以执行的数据
        :param tools_call:
        :return:
        """
        function = tools_call[0].function
        arguments = function.arguments
        name = function.name
        print(f"Deepseek实例调用的函数名为<{name}>")
        print(f"Deepseek实例调用的函数<{name}>输入的参数为<{arguments}>")
        result = self.use_tool(name, arguments)
        print(result)

    def use_tool(self,name, arguments):
        func = self.tool_methods[name]['method']
        annotations = func.__annotations__
        arguments_dict = eval(arguments)
        # 打印参数名称和类型
        for param_name, param_type in annotations.items():
            if param_name != 'return':  # 排除返回值类型
                if arguments_dict[param_name]:
                    arguments_dict[param_name] = param_type(arguments_dict[param_name])
        values_tuple = tuple(arguments_dict.values())
        result = func(*values_tuple)
        return result

