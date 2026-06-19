import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import subprocess

def ensure_playwright():
    try:
        import playwright
    except ImportError:
        print("⚠️ 未找到 Playwright，正在自动安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

ensure_playwright()
import astrbot.api.message_components as Comp
from astrbot.core.utils.session_waiter import (
    session_waiter,
    SessionController,
)
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from .wordle import WordleGameAsync

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    #@filter.command("wordle")
    #async def wordle(self, event: AstrMessageEvent):
    #   """这是一个 wordle 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
    #    user_name = event.get_sender_name()
    #    message_str = event.message_str # 用户发的纯文本消息字符串
    #    message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
    #    logger.info(message_chain)
    #    new_wordle=WordleGameAsync();
    #    await new_wordle.start_game();
    #    yield event.plain_result(f"开始Wordle, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    @filter.command("wordle")
    async def handle_empty_mention(self, event: AstrMessageEvent):
        """wordle具体实现"""
        try:
            new_wordle=WordleGameAsync();
            await new_wordle.start_game();
            yield event.plain_result("请发送一个长度为5的英文单词~")

            # 具体的会话控制器使用方法
            @session_waiter(timeout=60, record_history_chains=False) # 注册一个会话控制器，设置超时时间为 60 秒，不记录历史消息链
            async def empty_mention_waiter(controller: SessionController, event: AstrMessageEvent):
                idiom = event.message_str # 用户发来的成语，假设是 "一马当先"

                if idiom == "退出":   # 假设用户想主动退出成语接龙，输入了 "退出"
                    await event.send(event.plain_result("已退出wordle~"))
                    controller.stop()    # 停止会话控制器，会立即结束。
                    return

                if len(idiom) != 5:
                    return

                # ...
                new_wordle.submit_guess(idiom)
                message_result = event.make_result()
                message_result.chain = [Comp.Plain("先见之明")] # import astrbot.api.message_components as Comp
                await event.send(message_result) # 发送回复，不能使用 yield

                controller.keep(timeout=60, reset_timeout=True) # 重置超时时间为 60s，如果不重置，则会继续之前的超时时间计时。

                # controller.stop() # 停止会话控制器，会立即结束。
                # 如果记录了历史消息链，可以通过 controller.get_history_chains() 获取历史消息链

            try:
                await empty_mention_waiter(event)
            except TimeoutError as _: # 当超时后，会话控制器会抛出 TimeoutError
                yield event.plain_result("你超时了！")
            except Exception as e:
                yield event.plain_result("发生错误，请联系管理员: " + str(e))
            finally:
                event.stop_event()
        except Exception as e:
            logger.error("handle_empty_mention error: " + str(e))
        