import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import subprocess

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

    @filter.command("wordle")
    async def handle_empty_mention(self, event: AstrMessageEvent, length: int = 5):
        """wordle指令"""
        try:
            new_wordle = WordleGameAsync()
            await new_wordle.start_game(length)
            yield event.plain_result(f"请发送一个长度为{length}的英文单词~\n你有10分钟的时间")

            # 注册一个会话控制器，设置超时时间为 10 分钟
            @session_waiter(timeout=600, record_history_chains=False) 
            async def empty_mention_waiter(controller: SessionController, event: AstrMessageEvent):
                
                if not event.message_str or not event.message_str.strip():
                    return # 默默结束，不回复任何消息，不打扰玩家打字
                
                # 转换为纯小写并去除两端空格，防止因大小写导致校验失败
                idiom = event.message_str.strip().lower() 

                if idiom == "退出":   
                    await new_wordle.close_game()
                    await event.send(event.plain_result("已退出wordle~"))
                    controller.stop()    # 停止会话控制器
                    return

                # 校验是否全是纯英文字母
                flag = True
                for i in idiom:
                    if i < 'a' or i > 'z':
                        flag = False

                # 如果长度不对或者包含非字母，直接拦截并要求重新输入
                if len(idiom) != length or not flag:
                    await event.send(event.plain_result(f"输入不合法！请输入一个长度为 {length} 的纯英文单词。"))
                    controller.keep(timeout=600, reset_timeout=True) # 保持会话
                    return

                fg = await new_wordle.submit(idiom)
                
                if fg == 0:
                    # 【核心修复】改为使用 await event.send 发送，不再使用 yield
                    await event.send(event.plain_result("词典中没有这个单词呀，不算次数，请重新输入~"))
                    return
                    
                elif fg == 1:
                    await new_wordle.close_game()
                    user_name = event.get_sender_name()
                    await event.send(event.plain_result(f"🎉 恭喜{user_name}，答案完全正确！"))
                    
                    message_result = event.make_result()
                    message_result.chain = [Comp.Image.fromFileSystem("guess0.jpg")] 
                    await event.send(message_result)
                    controller.stop()    # 答对了，结束游戏
                    return
                    
                elif fg == 2:
                    await new_wordle.close_game()
                    # 游戏失败时，顺便把正确答案展示出来，体验更好
                    await event.send(event.plain_result(f"非常遗憾，次数已用光！正确答案是: {new_wordle.target_word}"))
                    
                    message_result = event.make_result()
                    message_result.chain = [Comp.Image.fromFileSystem("guess0.jpg")] 
                    await event.send(message_result)
                    controller.stop()    # 输了，结束游戏
                    return
                elif fg == 4:
                    await event.send(event.plain_result("你已经猜过这个单词了"))
                    return

                # fg == 3: 单词存在但没猜中，发送当前进度的图片
                message_result = event.make_result()
                message_result.chain = [Comp.Image.fromFileSystem("guess0.jpg")] 
                await event.send(message_result) 

                # 【核心新增】关键：只要游戏还没输/没赢，就必须重置时间，继续等待下一个单词
                #controller.keep(timeout=600, reset_timeout=True) 

            try:
                await empty_mention_waiter(event)
            except TimeoutError as _: 
                await new_wordle.close_game()
                yield event.plain_result("时间到，非常遗憾，没有人猜出正确答案>_<")
            except Exception as e:
                yield event.plain_result("发生错误，请联系管理员: " + str(e))
            finally:
                event.stop_event()
        except Exception as e:
            logger.error("handle_empty_mention error: " + str(e))