import queue
import threading
import time
from time import sleep
import json
import os

import pyaudio
from funasr import AutoModel
# from modelscope import snapshot_download
from pypinyin import lazy_pinyin

from cfg import get_command_key
from loguru import logger

from text_speech import text_to_speech
from web_socket import WebSocketServer

CHUNK = 8000
CHUNK_HALF = 8000
RATE = 16000
# 识别模型
current_path = os.getcwd()
# print(f"当前路径{current_path}")
with open(f"{current_path}/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
# 模型下载

# model_dir_par = snapshot_download('iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch',cache_dir="models")
model_dir_par = config["model"]
print(model_dir_par)
# model_dir_par = "E:\\codING\\voice_assistant\\model"
# model_dir_con = "../model/conformer_asr_nat-zh-cn-16k"

# model =

RECORD_SECONDS = 5  # 每5秒处理一次

# COMMAND_KEY = "输出"
# COMMAND_KEY_PINYIN = "shuchu"
HOT_KEY = "小小"
HOT_KEY_PINYIN = "Xiaoxiao "


# model_pipeline_par = pipeline(
#     task=Tasks.auto_speech_recognition,
#     model=model_dir_par,
#     model_revision="master",
#     device="cuda:0", )
# model_pipeline_con = pipeline(
#     task=Tasks.auto_speech_recognition,
#     model=model_dir_con,
#     model_revision="master",
#     device="cuda:0", )


def convert_to_pinyin(text):
    return lazy_pinyin(text)


class RealtimeSpeechRecognition:
    def __init__(self):
        self.is_awake = False
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
        self.key = ""
        self.key_py = ""
        self.command_key = ""
        self.command_key_pinyin = ""
        self.command_key_desc = ""
        self.audio_text = ""
        self.audio_text_pinyin = ""
        self.command_key_get = get_command_key
        self.model_par = AutoModel(model=model_dir_par,
                                   model_revision="master",
                                   trust_remote_code=False,
                                   disable_update=True,
                                   device="cuda:0")
        # self.model_par = model_pipeline_par
        # self.model_con = model_pipeline_con
        # self.vosk = vosk_service.VoskService()
        self.audio_queue = queue.Queue()
        self.is_running = True
        self.lock = threading.Lock()  # 添加锁来同步
        self.last_activation_time = time.time()
        self.logger = logger
        self.server = WebSocketServer(host="127.0.0.1", port=8080)

    # socket部分
    def send_command_to_client(self, key):
        self.logger.info(f"发送指令：{key}")
        self.server.queue_message(key)

    def socket_start(self):
        self.server.server_start()

    def audio_capture(self):
        while self.is_running:
            data = self.stream.read(CHUNK_HALF)
            self.audio_queue.put(data)
            sleep(0.5)

    def audio_to_text(self):
        while self.is_running:
            sleep(0.8)
            if len(self.audio_text) > 100:
                self.audio_text = ""
                self.audio_text_pinyin = ""
            texts = self.process_audio()
            if len(texts) > 0:
                self.audio_text += texts[0]
                self.audio_text_pinyin += texts[1]
            self.logger.info(f"识别到的结果{self.audio_text}_{self.audio_text_pinyin}")

    def model_par_get(self, audio_data):
        text = ""
        texts = []
        try:
            # texts = self.model_par(audio_data)
            texts = self.model_par.generate(audio_data,
                                            language="zh",
                                            use_itn=True)
            if len(texts) >= 0:
                text = texts[0]["text"]
            self.logger.info(f"model_par_get：{texts}")
        except Exception as e:
            self.logger.info(f"model_par_get：{texts}")
            self.logger.error(f"model_par_get 识别异常：{e}")
            if len(texts) >= 0:
                return texts[0]["text"]
            else:
                return ""
        self.logger.info(f"model_par_get识别结果：{text}")
        return text

    # def model_con_get(self, audio_data):
    #     texts = []
    #     text = ""
    #     try:
    #         texts = self.model_con(audio_data)
    #         self.logger.info(f"model_con_get：{texts}")
    #         if len(texts) >= 0:
    #             text = texts[0]["text"]
    #     except Exception as e:
    #         self.logger.error(f"model_con_get 识别异常：{e}")
    #         if len(texts) >= 0:
    #             return texts[0]["text"]
    #         else:
    #             return ""
    #     self.logger.info(f"model_con_get识别结果：{text}")
    #     return text

    def recognize_audio(self, audio_data):
        text = ""
        try:
            # 语音识别
            result_par = self.model_par_get(audio_data)
            if result_par is not None and len(result_par) >= 0:
                text += result_par
        except Exception as e:
            self.logger.error(f"recognize_audio 识别结果整合异常：{e}")
            return text

        return text

    def process_audio(self):
        result = []
        audio_data = b''
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            if not self.audio_queue.empty():
                audio_data += self.audio_queue.get()
            else:
                time.sleep(0.01)

        if audio_data:
            text = self.recognize_audio(audio_data)
            self.logger.info(f"recognize_audio的识别结果：{text}")
            if text.strip():  # 只有在识别到非空文本时才输出
                pinyin = convert_to_pinyin(text)
                result = [text, "".join(pinyin)]
        return result

    def hot_key_check(self):
        while self.is_running:
            if self.is_awake:
                sleep(1)
            else:
                # self.audio_text = ""
                # if len(texts) > 0:
                #     self.key += texts[0]
                #     self.key_py += texts[1]
                key = self.audio_text
                key_py = self.audio_text_pinyin
                key.replace(" ", "")
                key_py.replace(" ", "")
                self.audio_text = ""
                self.audio_text_pinyin = ""
                if len(key) > 0:
                    self.logger.info(f"当前识别结果：{key}_{key_py}")
                if (not self.is_awake) and (HOT_KEY in key or HOT_KEY_PINYIN in key_py.lower()):
                    self.last_activation_time = time.time()
                    self.is_awake = True
                    self.logger.info("唤醒成功")
                    self.send_command_to_client("请说出指令")
                    text_to_speech("请说出指令")
                #     self.key = ""
                #     self.key_py = ""
                # if len(self.key) > 100:
                #     self.key = ""
                #     self.key_py = ""

            time.sleep(0.2)

    def get_command(self, command, command_pinyin):
        key = ""
        try:
            object = self.command_key_get(command)
            if object is not None and len(object) > 0:
                key = object["commandKey"]
                self.command_key_desc = object["description"]
            else:
                object = self.command_key_get(command_pinyin)
                if object is not None and len(object) > 0:
                    key = object["commandKey"]
                    self.command_key_desc = object["description"]
                else:
                    return key
        except Exception as e:
            self.logger.error(f"关键字异常：{e}")
        return key

    def command_key_check(self):
        while self.is_running:
            if not self.is_awake:
                sleep(0.5)
            else:
                # texts = self.audio_text
                # self.audio_text = ""
                # if len(texts) > 0:
                #     self.command_key += texts[0]
                #     self.command_key_pinyin += texts[1]

                current_time = time.time()
                if self.is_awake:
                    command_key = self.audio_text
                    command_key_pinyin = self.audio_text_pinyin
                    self.audio_text = ""
                    self.audio_text_pinyin = ""
                    if len(command_key) > 0:
                        self.logger.info(f"当前指令识别：{command_key}_{command_key_pinyin}")
                    key = self.get_command(command_key, command_key_pinyin)
                    if (key is not None) and len(key) > 0 and (current_time - self.last_activation_time) <= 15:
                        self.send_command_to_client(key)
                        if len(self.command_key_desc) > 0:
                            text_to_speech(self.command_key_desc)
                        # asyncio.run(self.send_websocket_message("命令已激活: " + self.command_key))
                        # self.command_key = ""
                        # self.command_key_pinyin = ""
                        self.is_awake = False
                    elif current_time - self.last_activation_time > 15:
                        self.logger.warning("超时，重置唤醒状态")
                        self.is_awake = False
                        self.send_command_to_client("没有检测到指令，请重新唤醒")
                        text_to_speech("没有检测到指令关键词，请重新唤醒")
                        time.sleep(1)
                    # else:
                    #     tmps = self.audio_text
                    #     self.audio_text = ""
                    #     self.logger.warning("未识别到命令key,累计获取的结果:" + ".".join(tmps))
                    #     if len(self.command_key) > 500:
                    #         self.command_key = ""
                    #         self.command_key_pinyin = ""
                    #     if len(tmps) != 0:
                    #         self.command_key += tmps[0]
                    #         self.command_key_pinyin += tmps[1]

    def run(self):
        ws_thread = threading.Thread(target=self.socket_start)
        audio_thread = threading.Thread(target=self.audio_capture)
        text_thread = threading.Thread(target=self.audio_to_text)
        hot_key_check_thread = threading.Thread(target=self.hot_key_check)
        command_key_check_thread = threading.Thread(target=self.command_key_check)

        audio_thread.start()
        text_thread.start()
        hot_key_check_thread.start()
        command_key_check_thread.start()
        ws_thread.start()
        text_to_speech("语音助手已启动")

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.info("停止录音.")
            self.is_running = False
            self.server.server_stop()

        audio_thread.join()
        text_thread.join()
        hot_key_check_thread.join()
        command_key_check_thread.join()
        ws_thread.join()

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


def main():
    recognizer = RealtimeSpeechRecognition()
    recognizer.run()


if __name__ == "__main__":
    main()
