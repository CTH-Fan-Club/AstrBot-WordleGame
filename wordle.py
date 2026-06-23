import asyncio
import aiohttp
import os
import random
from PIL import Image, ImageDraw, ImageFont
from .lexicon import cet_words

class WordleGameAsync:
    def __init__(self):
        self.target_word = ""
        self.length = 5
        self.guesses = []  # 存储每一次猜测的单词和颜色结果
        self.max_attempts = 6
        self.is_active = False

        # 定义 Wordle 的标准配色
        self.COLOR_GREEN = (106, 170, 100)   # 存在且位置正确
        self.COLOR_YELLOW = (201, 180, 88)   # 存在但位置错误
        self.COLOR_GRAY = (120, 124, 126)    # 不存在
        self.COLOR_BG = (255, 255, 255)      # 背景色
        self.COLOR_BORDER = (211, 214, 218)  # 空白方块边框色
        self.COLOR_TEXT_WHITE = (255, 255, 255)

    async def start_game(self, length: int = 5):
        """游戏开始，指定单词长度 (2-11)，从国内离线四六级词库中随机抽词"""
        self.length = max(2, min(11, length))
        if length > 5:
            self.max_attempts = 6 + length - 5
        else:
            self.max_attempts = 6
        self.guesses = []
        self.is_active = True

        print(f"正在启动游戏，目标单词长度为 {self.length}...")

        # ====== 2. 核心修改：直接使用从 lexicon.py 导入的 cet_words ======
        # 过滤出符合玩家指定长度(self.length)的四六级单词
        valid_pool = [w.upper() for w in cet_words if len(w) == self.length]
        # ==============================================================

        # 如果词库里正好有这个长度的词，就随机抽一个；如果没有，就用保底单词
        if valid_pool:
            self.target_word = random.choice(valid_pool)
            print(f"成功从国内四六级词库中抽取单词！同长度候选词还有 {len(valid_pool)} 个。")
        else:
            # 极端长度下的兜底方案（全A填充）
            self.target_word = "APPLE"[:self.length].ljust(self.length, 'A').upper()

        print(f"游戏已成功开始！请发送一个长度为 {self.length} 的四六级英文单词。")

    async def _check_word_online(self, word: str) -> bool:
        """从本地全量词库中校验单词是否存在"""
        from .dictionary import is_valid_english_word
        return is_valid_english_word(word)

    def _evaluate_guess(self, guess: str) -> list:
        """评估猜测单词，返回颜色列表"""
        target = list(self.target_word)
        guess_list = list(guess)
        colors = [self.COLOR_GRAY] * self.length
        
        # 统计目标单词中每个字母的数量，处理重复字母的情况
        target_counts = {}
        for char in target:
            target_counts[char] = target_counts.get(char, 0) + 1

        # 第一遍扫描：找出所有完全匹配的（绿色）
        for i in range(self.length):
            if guess_list[i] == target[i]:
                colors[i] = self.COLOR_GREEN
                target_counts[guess_list[i]] -= 1

        # 第二遍扫描：找出位置错误但存在的（黄色）
        for i in range(self.length):
            if colors[i] == self.COLOR_GREEN:
                continue
            char = guess_list[i]
            if char in target_counts and target_counts[char] > 0:
                colors[i] = self.COLOR_YELLOW
                target_counts[char] -= 1

        return colors

    def _draw_image(self, save_path="guess0.jpg"):
        """根据当前的猜测记录，使用 PIL 绘制结果图片"""
        cell_size = 62
        margin = 10
        width = self.length * (cell_size + margin) + margin
        height = self.max_attempts * (cell_size + margin) + margin

        img = Image.new('RGB', (width, height), self.COLOR_BG)
        draw = ImageDraw.Draw(img)

        # 尝试加载粗体字体，如果 Linux 找不到则使用默认字体
        try:
            # 常见 Linux 字体路径
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except IOError:
            try:
                # 常见 Windows 字体
                font = ImageFont.truetype("arialbd.ttf", 36)
            except IOError:
                font = ImageFont.load_default()

        for row in range(self.max_attempts):
            for col in range(self.length):
                x0 = margin + col * (cell_size + margin)
                y0 = margin + row * (cell_size + margin)
                x1 = x0 + cell_size
                y1 = y0 + cell_size

                if row < len(self.guesses):
                    # 已猜测的行：绘制带颜色的实心方块和白色文字
                    word, colors = self.guesses[row]
                    char = word[col]
                    color = colors[col]
                    
                    draw.rectangle([x0, y0, x1, y1], fill=color)
                    
                    # 计算文字居中
                    bbox = draw.textbbox((0, 0), char, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                    text_x = x0 + (cell_size - text_w) / 2
                    text_y = y0 + (cell_size - text_h) / 2 - bbox[1]
                    
                    draw.text((text_x, text_y), char, fill=self.COLOR_TEXT_WHITE, font=font)
                else:
                    # 未猜测的行：绘制空心灰色边框
                    draw.rectangle([x0, y0, x1, y1], outline=self.COLOR_BORDER, width=2)

        img.save(save_path)
        print(f"图片已生成: {save_path}")

    async def submit(self, word: str) -> bool:
        """提交单词，检查并在当前目录生成图片"""
        if not self.is_active:
            print("游戏未在进行中。")
            return 0

        word = word.upper()
        if len(word) != self.length:
            print(f"长度错误！请输入一个长度为 {self.length} 的单词。")
            return 0

        print(f"正在联网核对词典: {word}...")
        # 联网验证单词是否合法
        is_valid = await self._check_word_online(word)
        if not is_valid:
            print(f"提交失败：词典中不存在单词 '{word}'！")
            return 0

        check_word = self.target_word.upper() # 记得转大写，因为 guesses 里存的都是大写

        if any(word == check_word for word, _ in self.guesses):
            print("这个单词之前已经猜过啦！")
            return 4

        # 计算颜色判定并保存记录
        colors = self._evaluate_guess(word)
        self.guesses.append((word, colors))

        # 绘制并保存图片
        self._draw_image("guess0.jpg")

        # 判断游戏是否结束
        if word == self.target_word:
            print("🎉 恭喜你，答案完全正确！")
            self.is_active = False
            return 1
        elif len(self.guesses) >= self.max_attempts:
            print(f"游戏结束！正确的单词是: {self.target_word}")
            self.is_active = False
            return 2

        return 3

    async def close_game(self):
        """清理数据并结束游戏"""
        self.is_active = False
        self.guesses = []
        print("游戏已强制关闭。")