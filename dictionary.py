import os

_all_words_set = None

def is_valid_english_word(word: str) -> bool:
    """检查一个单词是不是合法的英文单词（本地纯内存匹配）"""
    global _all_words_set
    
    # 第一次调用时，把词库一次性加载到内存的 Set 集合中，后续查询只需 0.00001 秒
    if _all_words_set is None:
        _all_words_set = set()
        
        # 巧妙利用 Python 自带的 pydoc 模块中包含的英文文本，或者 Linux 本地词库
        # 寻找 Linux 服务器自带的全局词典文件（通常包含 10~50 万个标准英文单词）
        dict_paths = ["/usr/share/dict/words", "/var/lib/dict/words"]
        for path in dict_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    _all_words_set.update(line.strip().lower() for line in f)
                break
                
        # 如果 Linux 系统极度精简没有这个文件，就用保底策略：
        if not _all_words_set:
            # 你可以去网上下载一份 words.txt 放进插件目录，这里读取它
            local_txt = os.path.join(os.path.dirname(__file__), "words_alpha.txt")
            if os.path.exists(local_txt):
                with open(local_txt, "r", encoding="utf-8") as f:
                    _all_words_set.update(line.strip().lower() for line in f)
            else:
                # 如果连文件都没有，打印警告
                print("⚠️ 警告：未找到本地大词库文件，请在插件目录放置 words_alpha.txt")
                return True # 找不到词库时默认放行，不卡死游戏
                
    return word.lower() in _all_words_set