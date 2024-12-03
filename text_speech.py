import pyttsx3



# 获取语音列表
# voices = engine.getProperty('voices')

def text_to_speech(text):
    # 初始化tts引擎
    engine = pyttsx3.init()
    # 设置音量（0到1之间）
    engine.setProperty('volume', 1.0)
    # 设置语速
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)
    # 要说的文本
    text = text
    # 清除之前的文本
    engine.say(text)
    # 播放音频
    engine.runAndWait()
