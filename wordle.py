from playwright.sync_api import sync_playwright
import time

class WordleGame:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.current_row = 0  # 记录当前是第几次猜测（Wordle通常有6次机会）

    def start_game(self):
        """
        开始游戏：初始化浏览器并打开网站
        """
        print("正在启动游戏，请稍候...")
        self.playwright = sync_playwright().start()
        # headless=False 可以让你在屏幕上看到浏览器操作，调试完可以改成 True
        self.browser = self.playwright.chromium.launch(headless=False) 
        self.page = self.browser.new_page()
        self.page.goto("https://www.wordle.name/")
        
        # 等待页面完全加载
        self.page.wait_for_load_state("networkidle")
        
        # 很多 Wordle 网站首次打开会有弹窗（如规则说明），如果是，可以取消下面这行的注释来关闭它
        # self.page.click("button.close-btn") # 需要根据实际弹窗的按钮修改选择器
        
        print("游戏已成功开始！可以输入答案了。")

    def submit_guess(self, word: str):
        """
        传入答案并让程序判断是否正确
        :param word: 5个字母的单词字符串，例如 'AUDIO'
        """
        if len(word) != 5:
            print("请输入一个5位字母的单词！")
            return
        
        word = word.upper() # 统一转换为大写
        print(f"\n正在提交猜测: {word}")
        
        # 模拟键盘输入单词
        self.page.keyboard.type(word)
        # 模拟按下回车键提交
        self.page.keyboard.press("Enter")
        
        # 等待翻牌动画结束（通常1-2秒）
        time.sleep(1.5)
        self.page.screenshot(path=r"C:\Users\Administrator\Desktop\guess0.png")
        #path=r"C:\Users\Administrator\Desktop\guess0.png"
        # 判断结果
        # 注意：这里的定位器(Selector)需要根据目标网站的实际 HTML 结构微调
        # 这里假设每一行的方块都在一个 row 容器里，且每个方块有表明状态的 class（如 correct, present, absent）
        try:
            # 获取当前行所有方块的状态
            # 这里的选择器假设：第几行的第几个方块。
            # 具体的 class 命名需要你在浏览器右键“检查”中看一下该网站是用什么命名的，比如有的网站叫 [data-state='correct']
            
            # 示例：获取刚刚输入的这一行方块的评判结果
            letters_status = []
            
            # 这里用通用的逻辑，具体选择器需要根据 www.wordle.name 实际页面进行微调
            # 下面是一个伪代码形式的提取，你需要根据实际网页源码修改方块的选择器
            # cells = self.page.locator(f"你的行选择器 >> 你的方块选择器").all()
            
            # 为了让你直观看到效果，这里演示如何检查是否“完全正确（全绿）”
            # 如果网站在赢了之后会弹窗或显示特定文字（如 "Splendid", "Genius" 或恭喜弹窗）：
            if "win" in self.page.content().lower() or self.check_if_won():
                print("🎉 恭喜你！答案完全正确！")
                return True
                
            print("结果已在浏览器中显示，请观察方块颜色。")
            self.current_row += 1
            
        except Exception as e:
            print(f"解析结果时出错: {e}")
            
        return False

    def check_if_won(self):
        """你可以根据游戏结束时的特定元素来判断是否胜利"""
        # 比如：判断是否有分享按钮出现，或者某个成功的提示框
        return False

    def close_game(self):
        """关闭游戏和浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("游戏已关闭。")

# ================= 交互式使用示例 =================
if __name__ == "__main__":
    game = WordleGame()
    
    # 1. 调用函数开始游戏
    game.start_game()
    
    try:
        # 2. 传入你的第一个答案
        game.submit_guess("AUDIO")
        
        # 3. 传入第二个答案
        game.submit_guess("PLANT")
        
        # 可以在这里写循环，或者写你的自动化算法...
        time.sleep(5) # 停留一会儿让你看一眼浏览器
        
    finally:
        # 4. 结束游戏
        game.close_game()