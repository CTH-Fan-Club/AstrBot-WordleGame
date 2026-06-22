import asyncio
from playwright.async_api import async_playwright

# 注意这里的类名叫 WordleGameAsync，必须和 main.py 里的导入一致
class WordleGameAsync:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.current_row = 0

    async def start_game(self):
        print("正在启动游戏，请稍候...")
        self.playwright = await async_playwright().start()
        # 【修改这里】将 headless=False 改为 True，让浏览器在后台静默运行
        self.browser = await self.playwright.chromium.launch(headless=True) 
        self.page = await self.browser.new_page()
        await self.page.goto("https://www.wordle.name/")
        await self.page.wait_for_load_state("networkidle")
        print("游戏已成功开始！可以输入答案了。")

    async def submit_guess(self, word: str):
        if len(word) != 5:
            print("请输入一个5位字母的单词！")
            return
        
        word = word.upper()
        print(f"\n正在提交猜测: {word}")
        
        await self.page.keyboard.type(word)
        await self.page.keyboard.press("Enter")
        
        await asyncio.sleep(3.0)
        # 注意：这里换成了相对路径，图片会保存在你运行机器人的当前目录下
        await self.page.screenshot(path="guess0.jpg")

        try:
            content = await self.page.content()
            if "win" in content.lower():
                print("🎉 恭喜你！答案完全正确！")
                return True
                
            print("结果已在浏览器中显示，请观察方块颜色。")
            self.current_row += 1
            
        except Exception as e:
            print(f"解析结果时出错: {e}")
            
        return False

    async def close_game(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("游戏已关闭。")