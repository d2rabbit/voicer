import json
from  loguru import  logger
import os


current_path = os.getcwd()
# LOG_DIR = "log"
# os.makedirs(LOG_DIR, exist_ok=True)

# 添加日志处理器到文件
# logger.add(
#     # os.path.join(LOG_DIR, "app_{time}.log"),
#     format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
#     level="INFO"
#     # rotation="100 MB",
#     # retention="30 days",
#     # compression="zip"
# )

# def logger():
#     return logger

command_file = f"{current_path}/command.json"

# def init_config():
#     try:
#         if os.path.exists(command_file) and os.path.isfile(command_file):
#             print("命令配置文件已存在")
#             return True
#         init_command_file(command_file)
#         return True
#     except Exception as e:
#         print(f"命令配置文件初始化异常: {e}")
#         return False


def init_command_file(file_path):
    logger.info("初始化命令配置文件")
    commands = get_init_commands()
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(commands, file, ensure_ascii=False, indent=4)


def get_init_commands():
    commands = [
        {"command": ["返回", "上一页"], "pinyin": ["fanhui", "shangyiye"], "description": "返回上一页", "commandKey": "back_last"},
        {"command": ["返回首页", "首页"], "pinyin": ["fanhuishouye", "shouye"], "description": "返回首页", "commandKey": "back_map"},
        {"command": ["厂区", "前往厂区"], "pinyin": ["changqu"], "description": "前往厂区页面", "commandKey": "back_home"},
        {"command": ["车间", "前往车间"], "pinyin": ["chejian"], "description": "前往车间页面", "commandKey": "back_birdCamera"}
    ]
    return commands

def get_command_list():
    with open(command_file, 'r', encoding='utf-8') as file:
        command_string = file.read()
        return json.loads(command_string)

def get_command_key(instruction):
    command_models = get_command_list()
    # logger.info(f"目前存在的命令：{command_models}")
    for command_model in command_models:
        if any(keyword in instruction for keyword in command_model['pinyin']) or \
           any(keyword in instruction for keyword in command_model['command']):
            return command_model
    return None


# if __name__ == "__main__":
#     if init_config():
#         instruction = "返回首页"
#         command_key = get_command_key(instruction)
#         print(f"指令 '{instruction}' 对应的命令键为: {command_key}")