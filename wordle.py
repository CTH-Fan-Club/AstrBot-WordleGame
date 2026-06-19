import asyncio
from playwright.async_api import async_playwright

class WordleGameAsync:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.current_row = 0

    async def start_game(self):
        print("正在启动游戏，请稍候...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False) 
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
        
        # 异步的 sleep
        await asyncio.sleep(1.5)
        await self.page.screenshot(path=r"C:\Users\Administrator\Desktop\guess0.png")

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

# ================= 异步调用示例 =================
async def main():
    game = WordleGameAsync()
    await game.start_game()
    
    try:
        await game.submit_guess("AUDIO")
        await game.submit_guess("PLANT")
        await asyncio.sleep(5) 
    finally:
        await game.close_game()

if __name__ == "__main__":
    asyncio.run(main())