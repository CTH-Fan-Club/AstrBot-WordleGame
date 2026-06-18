from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    def run(self, ame: AstrMessageEvent):
        if ame.message_str == "helloworld":
            return True, tuple([True, "Hello World!!", "helloworld"])
        else:
            return False, None
        
    def info(self):
        return {
            "name": "helloworld",
            "desc": "测试插件",
            "help": "测试插件, 回复 helloworld 即可触发",
            "version": "v1.2",
            "author": "Soulter"
        }
