"""
🐍 贪吃蛇互动教程
一步一步教你用 Pygame 写出贪吃蛇游戏
"""
import pygame
import random
import sys
import os

# ====================================================================
#  配置
# ====================================================================
WINDOW_W, WINDOW_H = 1280, 720
HEADER_H = 52
BOTTOM_H = 90
CONTENT_Y = HEADER_H
CONTENT_H = WINDOW_H - HEADER_H - BOTTOM_H
CODE_W = 620
GAP = 16
DEMO_X = CODE_W + GAP
DEMO_W = WINDOW_W - DEMO_X - 20
FPS = 60
PANEL_BG = (18, 18, 28)
HEADER_BG = (28, 28, 42)
BOTTOM_BG = (24, 24, 36)
CODE_BG = (13, 13, 22)
LINE_NUM_BG = (20, 20, 32)

# ====================================================================
#  颜色主题
# ====================================================================
COLOR_KEYWORD = (86, 156, 214)    # 关键字 - 蓝
COLOR_STRING = (206, 145, 120)    # 字符串 - 橙
COLOR_COMMENT = (106, 153, 85)    # 注释 - 绿
COLOR_NUMBER = (181, 206, 168)    # 数字 - 浅绿
COLOR_BUILTIN = (220, 220, 170)   # 内置函数 - 黄
COLOR_FUNC = (220, 220, 170)      # 函数名
COLOR_CLASS = (78, 201, 176)      # 类名 - 青
COLOR_PUNCT = (212, 212, 212)     # 标点/运算符
COLOR_TEXT = (212, 212, 212)      # 普通文本
COLOR_LINE_NUM = (100, 100, 120)  # 行号
COLOR_HIGHLIGHT = (255, 255, 100) # 高亮行
WHITE = (230, 230, 240)
GRAY = (140, 140, 160)
BUTTON_BG = (50, 50, 70)
BUTTON_HOVER = (70, 70, 100)
GREEN = (0, 200, 80)
RED = (220, 40, 40)

KEYWORDS = {
    'import', 'from', 'def', 'class', 'if', 'elif', 'else', 'for', 'while',
    'return', 'True', 'False', 'None', 'in', 'not', 'and', 'or', 'as', 'with',
    'try', 'except', 'finally', 'break', 'continue', 'pass', 'self', 'yield',
    'lambda', 'global', 'nonlocal', 'raise', 'assert', 'del',
}
BUILTIN_NAMES = {'pygame', 'random', 'sys', 'time', 'math', 'os'}

# ====================================================================
#  简易语法高亮
# ====================================================================
def parse_tokens(line):
    """将一行代码解析为 (text, color) 片段"""
    tokens = []
    i = 0
    n = len(line)
    while i < n:
        # 注释
        if line[i] == '#':
            tokens.append((line[i:], COLOR_COMMENT))
            break
        # 字符串
        if line[i] in ('"', "'"):
            quote = line[i]
            j = i + 1
            while j < n:
                if line[j] == '\\':
                    j += 2
                    continue
                if line[j] == quote:
                    j += 1
                    break
                j += 1
            tokens.append((line[i:j], COLOR_STRING))
            i = j
            continue
        # 三引号字符串
        if i + 2 < n and line[i:i+3] in ('"""', "'''"):
            q = line[i:i+3]
            j = i + 3
            while j < n:
                if line[j:j+3] == q:
                    j += 3
                    break
                j += 1
            tokens.append((line[i:j], COLOR_STRING))
            i = j
            continue
        # 数字
        if line[i].isdigit():
            j = i
            while j < n and (line[j].isalnum() or line[j] == '.'):
                j += 1
            tokens.append((line[i:j], COLOR_NUMBER))
            i = j
            continue
        # 标识符或关键字
        if line[i].isalpha() or line[i] == '_':
            j = i
            while j < n and (line[j].isalnum() or line[j] == '_'):
                j += 1
            word = line[i:j]
            if word in KEYWORDS:
                tokens.append((word, COLOR_KEYWORD))
            elif word in BUILTIN_NAMES:
                tokens.append((word, COLOR_BUILTIN))
            elif word[0].isupper():
                tokens.append((word, COLOR_CLASS))
            else:
                tokens.append((word, COLOR_TEXT))
            i = j
            continue
        # 其他字符
        tokens.append((line[i], COLOR_PUNCT))
        i += 1
    return tokens

# ====================================================================
#  Demo 基类和各个步骤

# ---- Font helpers (cross-platform CJK + emoji support) ----
_CJK_FONT_CACHE = {}
_EMOJI_FONT_CACHE = {}

def _load_cjk_font(size):
    """Load a font supporting CJK characters. Uses match_font first (most reliable), then direct paths."""
    if size in _CJK_FONT_CACHE:
        return _CJK_FONT_CACHE[size]

    # Strategy 1: Use match_font with known CJK font names (works on macOS, Linux, Windows)
    for name in [
        "Hiragino Sans GB",   # macOS Chinese
        "PingFang SC",         # macOS PingFang
        "STHeiti",             # macOS STHeiti
        "Heiti SC",            # macOS Heiti
        "Noto Sans CJK SC",    # Linux Noto
        "Noto Sans CJK",       # Linux Noto alt
        "WenQuanYi Micro Hei", # Linux WenQuanYi
        "Microsoft YaHei",     # Windows
        "SimHei",              # Windows
        "DengXian",            # Windows DengXian
    ]:
        try:
            path = pygame.font.match_font(name)
            if path:
                f = pygame.font.Font(path, size)
                # Verify it can actually render CJK (width should be reasonable)
                test_w = f.render("\u4f60", True, WHITE).get_width()
                if test_w >= 10:
                    _CJK_FONT_CACHE[size] = f
                    return f
        except Exception:
            pass

    # Strategy 2: Try known absolute paths directly
    direct_paths = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for path in direct_paths:
        if os.path.exists(path):
            try:
                f = pygame.font.Font(path, size)
                test_w = f.render("\u4f60", True, WHITE).get_width()
                if test_w >= 10:
                    _CJK_FONT_CACHE[size] = f
                    return f
            except Exception:
                pass

    # Final fallback: default font (won't render CJK but won't crash)
    f = pygame.font.Font(None, size)
    _CJK_FONT_CACHE[size] = f
    return f

def _load_emoji_font(size):
    """Load an emoji-capable font if available (returns None if not found)."""
    if size in _EMOJI_FONT_CACHE:
        return _EMOJI_FONT_CACHE[size]
    candidates = [
        "/System/Library/Fonts/Apple Color Emoji.ttc",
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "C:/Windows/Fonts/seguiemj.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                f = pygame.font.Font(path, size)
                _EMOJI_FONT_CACHE[size] = f
                return f
            except:
                pass
    _EMOJI_FONT_CACHE[size] = None
    return None

def _clean_text(text):
    """Strip emoji from text that can\'t render with CJK fonts."""
    reps = {
        "\U0001f40d": "",  # 🐍 snake
        "\U0001f3ae": "",  # 🎮 video game
        "\U0001f3af": "",  # 🎯 dart
        "\U0001f3c6": "",  # 🏆 trophy
        "\U0001f389": "",  # 🎉 party popper
        "\U0001f4fa": "",  # 📺 TV
        "\u2705": "",       # ✅ check
        "\u2713": "",       # ✓ check mark
        "\u25a0": "",       # ■
        "\u25a1": "",       # □
    }
    for ec, r in reps.items():
        text = text.replace(eval(f"'{ec}'"), r)
    return text

# ====================================================================
class DemoBase:
    """每个教程步骤的 demo 基类"""
    def setup(self):
        self.t = 0
    def update(self, events, dt):
        self.t += dt
    def draw(self, surface):
        pass
    def _get_cjk_font(self, size):
        """Get a CJK-capable font. Delegates to module-level _load_cjk_font."""
        return _load_cjk_font(size)


# ---------- Step 1: 初始化与窗口 ----------
class Demo1(DemoBase):
    """Step 1: 初始化与窗口 — 展示一个最简单的 Pygame 窗口"""
    def draw(self, surface):
        surface.fill((18, 18, 28))
        w, h = surface.get_size()
        cx, cy = w // 2, h // 2

        # 模拟游戏窗口 (匹配代码中的 screen.fill((20, 20, 30)))
        win_w = min(360, w - 60)
        win_h = min(360, h - 60)
        win_rect = pygame.Rect(cx - win_w // 2, cy - win_h // 2, win_w, win_h)
        pygame.draw.rect(surface, (20, 20, 30), win_rect)
        pygame.draw.rect(surface, (60, 60, 80), win_rect, 2, border_radius=8)

        # 标题栏
        title_bar = pygame.Rect(win_rect.x, win_rect.y, win_w, 30)
        pygame.draw.rect(surface, (40, 40, 60), title_bar,
                         border_top_left_radius=8, border_top_right_radius=8)

        # 窗口控制按钮（交通灯）
        from math import sin
        dots = [(win_rect.x + 12, win_rect.y + 10),
                (win_rect.x + 28, win_rect.y + 10),
                (win_rect.x + 44, win_rect.y + 10)]
        dot_colors = [(255, 95, 87), (255, 189, 46), (40, 200, 64)]
        for i, ((dx, dy), (r, g, b)) in enumerate(zip(dots, dot_colors)):
            bri = 0.8 + 0.2 * sin(self.t * 2 + i)
            pygame.draw.circle(surface, (int(r * bri), int(g * bri), int(b * bri)), (dx, dy), 6)

        # 窗口标题（匹配代码中的 set_caption）
        font = self._get_cjk_font(20)
        txt = font.render("贪吃蛇", True, (160, 160, 180))
        surface.blit(txt, (win_rect.x + 70, win_rect.y + 6))

class Demo2(DemoBase):
    def draw(self, surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        margin = 40
        grid_w = min(480, w - margin*2)
        grid_h = min(480, h - margin*2)
        cell = grid_w // 15
        grid_w = cell * 15
        grid_h = cell * 15
        gx = (w - grid_w) // 2
        gy = (h - grid_h) // 2

        # 绘制网格
        for row in range(16):
            y = gy + row * cell
            pygame.draw.line(surface, (50, 50, 70), (gx, y), (gx + grid_w, y))
        for col in range(16):
            x = gx + col * cell
            pygame.draw.line(surface, (50, 50, 70), (x, gy), (x, gy + grid_h))

        # 隔几个格子染色展示
        pulse = 0.3 + 0.3 * abs(__import__('math').sin(self.t * 2))
        for r in range(15):
            for c in range(15):
                if (r + c) % 3 == 0 and r % 2 == 0:
                    rect = (gx + c*cell + 1, gy + r*cell + 1, cell-2, cell-2)
                    alpha = int(60 + 60 * pulse)
                    pygame.draw.rect(surface, (alpha, alpha, 120), rect)

        font = self._get_cjk_font( 22)
        txt = font.render("网格布局 — 蛇将在格子上移动", True, GRAY)
        surface.blit(txt, (cx - txt.get_width()//2, gy + grid_h + 20))

# ---------- Step 3: 绘制蛇 ----------
class Demo3(DemoBase):
    def setup(self):
        super().setup()
        self.snake = [(7, 7), (6, 7), (5, 7)]

    def draw(self, surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        cell = 28
        off_x = (w - 15*cell) // 2
        off_y = (h - 15*cell) // 2

        for row in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x, off_y+row*cell), (off_x+15*cell, off_y+row*cell))
        for col in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x+col*cell, off_y), (off_x+col*cell, off_y+15*cell))

        for i, (x, y) in enumerate(self.snake):
            c = (0, 180, 70) if i == 0 else (0, 130, 50)
            rect = (off_x + x*cell + 2, off_y + y*cell + 2, cell-4, cell-4)
            pygame.draw.rect(surface, c, rect, border_radius=4)
            if i == 0:
                pygame.draw.rect(surface, (0, 220, 90), rect, 2, border_radius=4)

        font = self._get_cjk_font( 22)
        txt = font.render("蛇 = 一系列方格坐标 ", True, GRAY)
        surface.blit(txt, (w//2 - txt.get_width()//2, off_y + 15*cell + 20))

# ---------- Step 4: 蛇的移动 ----------
class Demo4(DemoBase):
    def setup(self):
        super().setup()
        self.snake = [(7, 7), (6, 7), (5, 7)]
        self.dir = (1, 0)
        self.move_timer = 0

    def update(self, events, dt):
        super().update(events, dt)
        self.move_timer += dt
        if self.move_timer > 0.25:
            self.move_timer = 0
            hx, hy = self.snake[0]
            new_head = (hx + self.dir[0], hy + self.dir[1])
            new_head = (new_head[0] % 15, new_head[1] % 15)
            self.snake.insert(0, new_head)
            self.snake.pop()

    def draw(self, surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        cell = 28
        off_x = (w - 15*cell) // 2
        off_y = (h - 15*cell) // 2

        for row in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x, off_y+row*cell), (off_x+15*cell, off_y+row*cell))
        for col in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x+col*cell, off_y), (off_x+col*cell, off_y+15*cell))

        for i, (x, y) in enumerate(self.snake):
            c = (0, 200, 80) if i == 0 else (0, 150, 60)
            rect = (off_x + x*cell + 2, off_y + y*cell + 2, cell-4, cell-4)
            pygame.draw.rect(surface, c, rect, border_radius=4)
            if i == 0:
                pygame.draw.rect(surface, (0, 255, 100), rect, 2, border_radius=4)

        # 方向箭头
        arrow = {1: "→", (-1): "←", (0, 1): "↓", (0, -1): "↑"}
        dir_name = arrow.get(self.dir, "→")
        font = self._get_cjk_font( 26)
        txt = font.render(f"移动方向: {dir_name}", True, WHITE)
        surface.blit(txt, (w//2 - txt.get_width()//2, off_y + 15*cell + 20))

# ---------- Step 5: 键盘控制 ----------
class Demo5(DemoBase):
    def setup(self):
        super().setup()
        self.snake = [(7, 7), (6, 7), (5, 7)]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.move_timer = 0

    def update(self, events, dt):
        super().update(events, dt)
        for e in events:
            if e.type == pygame.KEYDOWN:
                m = {pygame.K_UP: (0,-1), pygame.K_DOWN: (0,1), pygame.K_LEFT: (-1,0), pygame.K_RIGHT: (1,0),
                     pygame.K_w: (0,-1), pygame.K_s: (0,1), pygame.K_a: (-1,0), pygame.K_d: (1,0)}
                if e.key in m:
                    nd = m[e.key]
                    if nd[0] + self.dir[0] != 0 or nd[1] + self.dir[1] != 0:
                        self.next_dir = nd
        self.dir = self.next_dir
        self.move_timer += dt
        if self.move_timer > 0.2:
            self.move_timer = 0
            hx, hy = self.snake[0]
            new_head = (hx + self.dir[0], hy + self.dir[1])
            new_head = (new_head[0] % 15, new_head[1] % 15)
            self.snake.insert(0, new_head)
            self.snake.pop()

    def draw(self, surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        cell = 28
        off_x = (w - 15*cell) // 2
        off_y = (h - 15*cell) // 2
        for row in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x, off_y+row*cell), (off_x+15*cell, off_y+row*cell))
        for col in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x+col*cell, off_y), (off_x+col*cell, off_y+15*cell))
        for i, (x, y) in enumerate(self.snake):
            c = (0, 200, 80) if i == 0 else (0, 150, 60)
            rect = (off_x + x*cell + 2, off_y + y*cell + 2, cell-4, cell-4)
            pygame.draw.rect(surface, c, rect, border_radius=4)
            if i == 0:
                pygame.draw.rect(surface, (0, 255, 100), rect, 2, border_radius=4)
        font = self._get_cjk_font( 22)
        txt = font.render("按 方向键 / WASD 控制方向", True, (100, 200, 255))
        surface.blit(txt, (w//2 - txt.get_width()//2, off_y + 15*cell + 20))

# ---------- Step 6: 食物生成 ----------
class Demo6(DemoBase):
    def setup(self):
        super().setup()
        self.snake = [(7, 7), (6, 7), (5, 7)]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.move_timer = 0
        self.food = self._rand_food()

    def _rand_food(self):
        while True:
            f = (random.randint(0, 14), random.randint(0, 14))
            if f not in self.snake:
                return f

    def update(self, events, dt):
        super().update(events, dt)
        for e in events:
            if e.type == pygame.KEYDOWN:
                m = {pygame.K_UP: (0,-1), pygame.K_DOWN: (0,1), pygame.K_LEFT: (-1,0), pygame.K_RIGHT: (1,0),
                     pygame.K_w: (0,-1), pygame.K_s: (0,1), pygame.K_a: (-1,0), pygame.K_d: (1,0)}
                if e.key in m:
                    nd = m[e.key]
                    if nd[0] + self.dir[0] != 0 or nd[1] + self.dir[1] != 0:
                        self.next_dir = nd
        self.dir = self.next_dir
        self.move_timer += dt
        if self.move_timer > 0.2:
            self.move_timer = 0
            hx, hy = self.snake[0]
            new_head = (hx + self.dir[0], hy + self.dir[1])
            new_head = (new_head[0] % 15, new_head[1] % 15)
            self.snake.insert(0, new_head)
            self.snake.pop()

    def draw(self, surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        cell = 28
        off_x = (w - 15*cell) // 2
        off_y = (h - 15*cell) // 2
        for row in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x, off_y+row*cell), (off_x+15*cell, off_y+row*cell))
        for col in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x+col*cell, off_y), (off_x+col*cell, off_y+15*cell))
        for i, (x, y) in enumerate(self.snake):
            c = (0, 200, 80) if i == 0 else (0, 150, 60)
            rect = (off_x + x*cell + 2, off_y + y*cell + 2, cell-4, cell-4)
            pygame.draw.rect(surface, c, rect, border_radius=4)
            if i == 0:
                pygame.draw.rect(surface, (0, 255, 100), rect, 2, border_radius=4)
        # 食物
        fx, fy = self.food
        fr = (off_x + fx*cell + 2, off_y + fy*cell + 2, cell-4, cell-4)
        pygame.draw.rect(surface, RED, fr, border_radius=6)
        glow = 0.7 + 0.3 * __import__('math').sin(self.t * 4)
        pygame.draw.rect(surface, (int(255*glow), 50, 50), fr, 2, border_radius=6)
        font = self._get_cjk_font( 22)
        txt = font.render("食物随机出现 —— 去吃它！", True, GRAY)
        surface.blit(txt, (w//2 - txt.get_width()//2, off_y + 15*cell + 20))

# ---------- Step 7: 吃食物与成长 ----------
class Demo7(DemoBase):
    def setup(self):
        super().setup()
        self.snake = [(7, 7), (6, 7), (5, 7)]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.move_timer = 0
        self.score = 0
        self.food = self._rand_food()
        self.eat_flash = 0

    def _rand_food(self):
        while True:
            f = (random.randint(0, 14), random.randint(0, 14))
            if f not in self.snake:
                return f

    def update(self, events, dt):
        super().update(events, dt)
        self.eat_flash = max(0, self.eat_flash - dt)
        for e in events:
            if e.type == pygame.KEYDOWN:
                m = {pygame.K_UP: (0,-1), pygame.K_DOWN: (0,1), pygame.K_LEFT: (-1,0), pygame.K_RIGHT: (1,0),
                     pygame.K_w: (0,-1), pygame.K_s: (0,1), pygame.K_a: (-1,0), pygame.K_d: (1,0)}
                if e.key in m:
                    nd = m[e.key]
                    if nd[0] + self.dir[0] != 0 or nd[1] + self.dir[1] != 0:
                        self.next_dir = nd
        self.dir = self.next_dir
        self.move_timer += dt
        if self.move_timer > 0.2:
            self.move_timer = 0
            hx, hy = self.snake[0]
            new_head = (hx + self.dir[0], hy + self.dir[1])
            new_head = (new_head[0] % 15, new_head[1] % 15)
            self.snake.insert(0, new_head)
            # 吃食物检测
            if new_head == self.food:
                self.score += 1
                self.eat_flash = 0.3
                self.food = self._rand_food()
            else:
                self.snake.pop()

    def draw(self, surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        cell = 28
        off_x = (w - 15*cell) // 2
        off_y = (h - 15*cell) // 2
        for row in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x, off_y+row*cell), (off_x+15*cell, off_y+row*cell))
        for col in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x+col*cell, off_y), (off_x+col*cell, off_y+15*cell))
        for i, (x, y) in enumerate(self.snake):
            c = (0, 200, 80) if i == 0 else (0, 150, 60)
            rect = (off_x + x*cell + 2, off_y + y*cell + 2, cell-4, cell-4)
            pygame.draw.rect(surface, c, rect, border_radius=4)
            if i == 0:
                pygame.draw.rect(surface, (0, 255, 100), rect, 2, border_radius=4)
        fx, fy = self.food
        fr = (off_x + fx*cell + 2, off_y + fy*cell + 2, cell-4, cell-4)
        glow = 0.7 + 0.3 * __import__('math').sin(self.t * 4)
        pygame.draw.rect(surface, RED, fr, border_radius=6)
        pygame.draw.rect(surface, (int(255*glow), 50, 50), fr, 2, border_radius=6)
        # 得分
        font = self._get_cjk_font( 28)
        txt = font.render(f"Score: {self.score}  吃了 {self.score} 个！", True, WHITE)
        surface.blit(txt, (w//2 - txt.get_width()//2, off_y + 15*cell + 20))
        if self.eat_flash > 0:
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            flash = int(255 * self.eat_flash / 0.3)
            s.fill((255, 255, 100, flash // 3))
            surface.blit(s, (0, 0))

# ---------- Step 8: 碰撞检测 ----------
class Demo8(DemoBase):
    def setup(self):
        super().setup()
        self.reset_game()

    def reset_game(self):
        self.snake = [(7, 7), (6, 7), (5, 7)]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.move_timer = 0
        self.score = 0
        self.food = self._rand_food()
        self.dead = False
        self.dead_timer = 0

    def _rand_food(self):
        while True:
            f = (random.randint(0, 14), random.randint(0, 14))
            if f not in self.snake:
                return f

    def update(self, events, dt):
        super().update(events, dt)
        if self.dead:
            self.dead_timer += dt
            if self.dead_timer > 2:
                self.reset_game()
            return
        for e in events:
            if e.type == pygame.KEYDOWN:
                m = {pygame.K_UP: (0,-1), pygame.K_DOWN: (0,1), pygame.K_LEFT: (-1,0), pygame.K_RIGHT: (1,0),
                     pygame.K_w: (0,-1), pygame.K_s: (0,1), pygame.K_a: (-1,0), pygame.K_d: (1,0)}
                if e.key in m:
                    nd = m[e.key]
                    if nd[0] + self.dir[0] != 0 or nd[1] + self.dir[1] != 0:
                        self.next_dir = nd
        self.dir = self.next_dir
        self.move_timer += dt
        if self.move_timer > 0.2:
            self.move_timer = 0
            hx, hy = self.snake[0]
            new_head = (hx + self.dir[0], hy + self.dir[1])
            # 碰撞检测
            if new_head[0] < 0 or new_head[0] >= 15 or new_head[1] < 0 or new_head[1] >= 15:
                self.dead = True
                return
            if new_head in self.snake:
                self.dead = True
                return
            self.snake.insert(0, new_head)
            if new_head == self.food:
                self.score += 1
                self.food = self._rand_food()
            else:
                self.snake.pop()

    def draw(self, surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        cell = 28
        off_x = (w - 15*cell) // 2
        off_y = (h - 15*cell) // 2
        for row in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x, off_y+row*cell), (off_x+15*cell, off_y+row*cell))
        for col in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x+col*cell, off_y), (off_x+col*cell, off_y+15*cell))
        for i, (x, y) in enumerate(self.snake):
            c = (0, 200, 80) if i == 0 else (0, 150, 60)
            rect = (off_x + x*cell + 2, off_y + y*cell + 2, cell-4, cell-4)
            pygame.draw.rect(surface, c, rect, border_radius=4)
            if i == 0:
                pygame.draw.rect(surface, (0, 255, 100), rect, 2, border_radius=4)
        fx, fy = self.food
        fr = (off_x + fx*cell + 2, off_y + fy*cell + 2, cell-4, cell-4)
        pygame.draw.rect(surface, RED, fr, border_radius=6)
        pygame.draw.rect(surface, (255, 80, 80), fr, 2, border_radius=6)
        font = self._get_cjk_font( 22)
        if self.dead:
            txt = font.render("撞墙/撞自己了！2 秒后重新开始", True, RED)
        else:
            txt = font.render("⚠️ 碰到墙壁或自己身体就 Game Over", True, GRAY)
        surface.blit(txt, (w//2 - txt.get_width()//2, off_y + 15*cell + 20))
        font2 = self._get_cjk_font( 24)
        txt2 = font2.render(f"Score: {self.score}", True, WHITE)
        surface.blit(txt2, (w//2 - txt2.get_width()//2, off_y + 15*cell + 45))

# ---------- Step 9: 游戏结束画面 ----------
class Demo9(DemoBase):
    def setup(self):
        super().setup()
        self.start_time = self.t
        self.show_over = False

    def update(self, events, dt):
        super().update(events, dt)
        if self.t > 3 and not self.show_over:
            self.show_over = True
        if self.show_over and self.t > 7:
            self.t = 0
            self.show_over = False

    def draw(self, surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        if not self.show_over:
            # 正常游戏画面
            cell = 28
            off_x = (w - 15*cell) // 2
            off_y = (h - 15*cell) // 2
            for row in range(16):
                pygame.draw.line(surface, (40, 40, 55), (off_x, off_y+row*cell), (off_x+15*cell, off_y+row*cell))
            for col in range(16):
                pygame.draw.line(surface, (40, 40, 55), (off_x+col*cell, off_y), (off_x+col*cell, off_y+15*cell))
            snake = [(7,7),(6,7),(5,7)]
            for i, (x, y) in enumerate(snake):
                c = (0, 200, 80) if i == 0 else (0, 150, 60)
                rect = (off_x + x*cell + 2, off_y + y*cell + 2, cell-4, cell-4)
                pygame.draw.rect(surface, c, rect, border_radius=4)
            fr = (off_x + 10*cell + 2, off_y + 7*cell + 2, cell-4, cell-4)
            pygame.draw.rect(surface, RED, fr, border_radius=6)
            font = self._get_cjk_font( 22)
            txt = font.render(" 游戏中... (3 秒后撞墙演示)", True, GRAY)
            surface.blit(txt, (w//2 - txt.get_width()//2, off_y + 15*cell + 20))
        else:
            # 游戏结束画面
            s = pygame.Surface((w, h))
            s.fill((0, 0, 0))
            s.set_alpha(160)
            surface.blit(s, (0, 0))
            font = self._get_cjk_font( 52)
            txt = font.render("GAME OVER", True, RED)
            surface.blit(txt, (w//2 - txt.get_width()//2, h//2 - 60))
            font2 = self._get_cjk_font( 32)
            txt2 = font2.render(f"Score: 8 ", True, WHITE)
            surface.blit(txt2, (w//2 - txt2.get_width()//2, h//2))
            font3 = self._get_cjk_font( 22)
            txt3 = font3.render("按 SPACE 重新开始  |  按 ESC 退出", True, GRAY)
            surface.blit(txt3, (w//2 - txt3.get_width()//2, h//2 + 50))
            font4 = self._get_cjk_font( 18)
            txt4 = font4.render("(演示自动循环)", True, (80, 80, 100))
            surface.blit(txt4, (w//2 - txt4.get_width()//2, h//2 + 80))

# ---------- Step 10: 完整游戏 ----------
class Demo10(DemoBase):
    def setup(self):
        super().setup()
        self.snake = [(7, 7), (6, 7), (5, 7)]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.move_timer = 0
        self.score = 0
        self.food = self._rand_food()
        self.dead = False
        self.waiting = False

    def _rand_food(self):
        while True:
            f = (random.randint(0, 14), random.randint(0, 14))
            if f not in self.snake:
                return f

    def update(self, events, dt):
        super().update(events, dt)
        if self.dead:
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    self.setup()
            return
        for e in events:
            if e.type == pygame.KEYDOWN:
                m = {pygame.K_UP: (0,-1), pygame.K_DOWN: (0,1), pygame.K_LEFT: (-1,0), pygame.K_RIGHT: (1,0),
                     pygame.K_w: (0,-1), pygame.K_s: (0,1), pygame.K_a: (-1,0), pygame.K_d: (1,0)}
                if e.key in m:
                    nd = m[e.key]
                    if nd[0] + self.dir[0] != 0 or nd[1] + self.dir[1] != 0:
                        self.next_dir = nd
        self.dir = self.next_dir
        self.move_timer += dt
        if self.move_timer > 0.18:
            self.move_timer = 0
            hx, hy = self.snake[0]
            new_head = (hx + self.dir[0], hy + self.dir[1])
            if new_head[0] < 0 or new_head[0] >= 15 or new_head[1] < 0 or new_head[1] >= 15:
                self.dead = True
                return
            if new_head in self.snake:
                self.dead = True
                return
            self.snake.insert(0, new_head)
            if new_head == self.food:
                self.score += 1
                self.food = self._rand_food()
            else:
                self.snake.pop()

    def draw(self, surface):
        surface.fill((20, 20, 30))
        w, h = surface.get_size()
        cell = 28
        off_x = (w - 15*cell) // 2
        off_y = (h - 15*cell) // 2
        for row in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x, off_y+row*cell), (off_x+15*cell, off_y+row*cell))
        for col in range(16):
            pygame.draw.line(surface, (40, 40, 55), (off_x+col*cell, off_y), (off_x+col*cell, off_y+15*cell))
        for i, (x, y) in enumerate(self.snake):
            c = (0, 200, 80) if i == 0 else (0, 150, 60)
            rect = (off_x + x*cell + 2, off_y + y*cell + 2, cell-4, cell-4)
            pygame.draw.rect(surface, c, rect, border_radius=4)
            if i == 0:
                pygame.draw.rect(surface, (0, 255, 100), rect, 2, border_radius=4)
        fx, fy = self.food
        fr = (off_x + fx*cell + 2, off_y + fy*cell + 2, cell-4, cell-4)
        glow = 0.7 + 0.3 * __import__('math').sin(self.t * 4)
        pygame.draw.rect(surface, RED, fr, border_radius=6)
        pygame.draw.rect(surface, (int(255*glow), 50, 50), fr, 2, border_radius=6)
        # 分数条
        bar_y = off_y + 15*cell + 15
        pygame.draw.rect(surface, (40, 40, 55), (off_x, bar_y, 15*cell, 36), border_radius=6)
        font = self._get_cjk_font( 26)
        txt = font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(txt, (w//2 - txt.get_width()//2, bar_y + 6))
        if self.dead:
            # Game Over 覆盖层
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            surface.blit(s, (0, 0))
            font2 = self._get_cjk_font( 48)
            t1 = font2.render("GAME OVER", True, RED)
            surface.blit(t1, (w//2 - t1.get_width()//2, h//2 - 50))
            font3 = self._get_cjk_font( 28)
            t2 = font3.render(f"Score: {self.score} ", True, WHITE)
            surface.blit(t2, (w//2 - t2.get_width()//2, h//2 + 10))
            font4 = self._get_cjk_font( 22)
            t3 = font4.render("按 SPACE 重新开始", True, GRAY)
            surface.blit(t3, (w//2 - t3.get_width()//2, h//2 + 55))

# ====================================================================
#  教程步骤定义
# ====================================================================
STEPS = [
    {
        "title": "Step 1: 初始化 Pygame",
        "desc": "用 pygame.init() 初始化所有模块，创建窗口，进入主循环。"
                " 这是所有 Pygame 程序的起点。",
        "code": '''\
import pygame
import random
import sys

pygame.init()
screen = pygame.display.set_mode(
    (600, 600)
)
pygame.display.set_caption(
    "贪吃蛇"
)
clock = pygame.time.Clock()

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    screen.fill((20, 20, 30))
    pygame.display.flip()
    clock.tick(10)

pygame.quit()''',
        "demo": Demo1(),
    },
    {
        "title": "Step 2: 绘制网格",
        "desc": "蛇在网格上移动。我们用常量定义格子大小和数量，"
                "然后用循环画出网格线。",
        "code": '''\
CELL_SIZE = 30
GRID_W = 20
GRID_H = 20
WIDTH = CELL_SIZE * GRID_W
HEIGHT = CELL_SIZE * GRID_H

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

# 画网格
for x in range(0, WIDTH, CELL_SIZE):
    pygame.draw.line(
        screen, (50,50,70),
        (x, 0), (x, HEIGHT)
    )
for y in range(0, HEIGHT, CELL_SIZE):
    pygame.draw.line(
        screen, (50,50,70),
        (0, y), (WIDTH, y)
    )''',
        "demo": Demo2(),
    },
    {
        "title": "Step 3: 绘制蛇",
        "desc": "蛇是一个坐标列表，每个元素是 (x, y)。"
                "遍历列表在对应格子上画方块，蛇头用亮色区分。",
        "code": '''\
# Snake 用列表表示
snake = [(10, 10), (9, 10), (8, 10)]

# 绘制
for i, (x, y) in enumerate(snake):
    color = (0, 200, 80)  # 蛇头绿色
    if i > 0:
        color = (0, 150, 60)  # 蛇身深绿
    rect = (x * CELL_SIZE + 2,
            y * CELL_SIZE + 2,
            CELL_SIZE - 4,
            CELL_SIZE - 4)
    pygame.draw.rect(
        screen, color, rect,
        border_radius=4
    )''',
        "demo": Demo3(),
    },
    {
        "title": "Step 4: 蛇的移动",
        "desc": "每一帧将新头部插入列表头部，移除尾部，"
                "蛇看起来就在移动了。用方向向量控制走向。",
        "code": '''\
direction = (1, 0)  # 右

# 移动逻辑
hx, hy = snake[0]
new_head = (
    hx + direction[0],
    hy + direction[1]
)
snake.insert(0, new_head)
snake.pop()  # 删除尾部
# 没吃到食物时删尾部
# 吃到了就保留 -> 变长''',
        "demo": Demo4(),
    },
    {
        "title": "Step 5: 键盘控制",
        "desc": "监听 KEYDOWN 事件，根据按键改变方向。"
                "注意不能原地掉头——左右互斥、上下互斥。",
        "code": '''\
# 在事件循环中
if e.type == pygame.KEYDOWN:
    if e.key == pygame.K_UP:
        if direction != (0, 1):
            direction = (0, -1)
    elif e.key == pygame.K_DOWN:
        if direction != (0, -1):
            direction = (0, 1)
    elif e.key == pygame.K_LEFT:
        if direction != (1, 0):
            direction = (-1, 0)
    elif e.key == pygame.K_RIGHT:
        if direction != (-1, 0):
            direction = (1, 0)

# 也支持 WASD
# K_w, K_s, K_a, K_d''',
        "demo": Demo5(),
    },
    {
        "title": "Step 6: 食物生成",
        "desc": "用 random.randint 随机选一个格子放食物，"
                "但要保证不在蛇身上。用红色方块标出。",
        "code": '''\
def random_food(snake):
    while True:
        x = random.randint(0, GRID_W-1)
        y = random.randint(0, GRID_H-1)
        if (x, y) not in snake:
            return (x, y)

food = random_food(snake)

# 绘制食物
rect = (food[0] * CELL_SIZE + 2,
        food[1] * CELL_SIZE + 2,
        CELL_SIZE - 4,
        CELL_SIZE - 4)
pygame.draw.rect(
    screen, (220, 40, 40),
    rect, border_radius=6
)''',
        "demo": Demo6(),
    },
    {
        "title": "Step 7: 吃食物与成长",
        "desc": "当蛇头碰到食物时，不删尾部（snake.insert 但不 pop），"
                "蛇就变长了。同时加 1 分，生成新食物。",
        "code": '''\
# 移动蛇
hx, hy = snake[0]
new_head = (hx + dx, hy + dy)
snake.insert(0, new_head)

# 检查是否吃到食物
if new_head == food:
    score += 1
    food = random_food(snake)
    # 不 pop → 蛇变长
else:
    snake.pop()  # 没吃到 → 删尾部''',
        "demo": Demo7(),
    },
    {
        "title": "Step 8: 碰撞检测",
        "desc": "每移动一步检查：新头部是否超出边界？"
                "是否撞到自己的身体？任一条件成立 → Game Over。",
        "code": '''\
# 墙壁碰撞
if (new_head[0] < 0 or
    new_head[0] >= GRID_W or
    new_head[1] < 0 or
    new_head[1] >= GRID_H):
    game_over = True

# 自身碰撞
if new_head in snake[1:]:
    game_over = True''',
        "demo": Demo8(),
    },
    {
        "title": "Step 9: 游戏结束画面",
        "desc": "Game Over 时显示结束界面、最终分数，"
                "让玩家按空格重新开始或按 ESC 退出。",
        "code": '''\
if game_over:
    # 显示结束画面
    screen.fill((20, 20, 30))
    draw_text("GAME OVER", 52, RED,
              WIDTH//2, HEIGHT//2 - 40)
    draw_text(f"Score: {score}", 32,
              WHITE, WIDTH//2, HEIGHT//2 + 20)
    draw_text("SPACE 重新开始 | "
              "ESC 退出", 22, GRAY,
              WIDTH//2, HEIGHT//2 + 80)
    pygame.display.flip()
    # 等待输入...''',
        "demo": Demo9(),
    },
    {
        "title": "Step 10: 完整贪吃蛇",
        "desc": "把所有模块组合起来就是完整的贪吃蛇！"
                "试试在右侧玩游戏吧。按方向键控制，空格重新开始。",
        "code": '''\
恭喜学完所有步骤！

完整版 = 
  初始化
+ 网格绘制
+ 蛇的移动与控制
+ 食物生成
+ 吃食物→变长→加分
+ 碰撞检测
+ 游戏结束与重启

现在去右侧玩一玩完整游戏吧！
按 方向键/WASD 控制''',
        "demo": Demo10(),
    },
]

# ====================================================================
#  主程序
# ====================================================================
class TutorialApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("贪吃蛇互动教程 — 一步一步学 Pygame")
        self.clock = pygame.time.Clock()
        self.font_code = self._get_mono_font(17)
        self.font_code_bold = self._get_mono_font(18, bold=True)
        self.font_normal = self._get_cjk_font( 24)
        self.font_small = self._get_cjk_font( 20)
        self.font_title = self._get_cjk_font( 30)
        self.font_big = self._get_cjk_font( 40)
        self.running = True
        self.step_idx = 0
        self.hover_prev = False
        self.hover_next = False
        self.demo_surface = pygame.Surface((DEMO_W, CONTENT_H))
        self.step_total = len(STEPS)
        self.restart_demo()

    def _get_cjk_font(self, size):
        return _load_cjk_font(size)

    def _get_mono_font(self, size, bold=False):
        # Try monospace fonts, but verify CJK support before using them.
        # Menlo / SF Mono on macOS exist but lack CJK glyphs -> fall back.
        mono_cjk_paths = [
            "/System/Library/Fonts/Menlo.ttc",          # macOS - no CJK but fallback works
            "/System/Library/Fonts/SF-Mono-Regular.otf", # macOS SF Mono
        ]
        for path in mono_cjk_paths:
            if os.path.exists(path):
                try:
                    f = pygame.font.Font(path, size)
                    test_w = f.render("你", True, WHITE).get_width()
                    if test_w >= 10:
                        return f
                    # Font loaded but has no CJK glyphs - skip it
                except:
                    pass

        # Fallback: use the CJK font directly so Chinese characters actually render
        return _load_cjk_font(size)

    def restart_demo(self):
        step = STEPS[self.step_idx]
        step["demo"].setup()

    def draw_header(self):
        pygame.draw.rect(self.screen, HEADER_BG, (0, 0, WINDOW_W, HEADER_H))
        ti = self.font_big.render("贪吃蛇互动教程", True, WHITE)
        self.screen.blit(ti, (18, (HEADER_H - ti.get_height()) // 2))
        prog = self.font_normal.render(
            f"Step {self.step_idx + 1} / {self.step_total}", True, GRAY)
        self.screen.blit(prog, (WINDOW_W - prog.get_width() - 20,
                                (HEADER_H - prog.get_height()) // 2))
        pygame.draw.line(self.screen, (50, 50, 70), (0, HEADER_H),
                         (WINDOW_W, HEADER_H))

    def draw_bottom(self):
        pygame.draw.rect(self.screen, BOTTOM_BG, (0, WINDOW_H - BOTTOM_H,
                                                  WINDOW_W, BOTTOM_H))
        pygame.draw.line(self.screen, (50, 50, 70), (0, WINDOW_H - BOTTOM_H),
                         (WINDOW_W, WINDOW_H - BOTTOM_H))

        step = STEPS[self.step_idx]
        # 描述文字
        desc_lines = self._wrap_text(step["desc"], self.font_small, WINDOW_W - 300)
        for i, line in enumerate(desc_lines[:3]):
            c = GRAY if i == 0 else (120, 120, 140)
            r = self.font_small.render(line, True, c)
            self.screen.blit(r, (20, WINDOW_H - BOTTOM_H + 12 + i * 22))

        # Prev / Next 按钮
        mx, my = pygame.mouse.get_pos()
        btn_y = WINDOW_H - 40
        btn_h = 30
        btn_w = 100

        for label, active, idx_offset in [
            ("<< 上一步", self.step_idx > 0, -1),
            ("下一步 >>", self.step_idx < self.step_total - 1, 1),
        ]:
            if idx_offset == -1:
                bx, by = 20, btn_y
            else:
                bx, by = 130, btn_y
            hover = bx <= mx <= bx + btn_w and by <= my <= by + btn_h
            color = BUTTON_HOVER if (hover and active) else BUTTON_BG
            if not active:
                color = (35, 35, 50)
            pygame.draw.rect(self.screen, color, (bx, by, btn_w, btn_h),
                             border_radius=6)
            if active:
                pygame.draw.rect(self.screen, (80, 80, 110), (bx, by, btn_w, btn_h),
                                 1, border_radius=6)
            t = self.font_small.render(label, True,
                                       WHITE if active else (60, 60, 80))
            self.screen.blit(t, (bx + (btn_w - t.get_width()) // 2,
                                 by + (btn_h - t.get_height()) // 2 + 1))

    def _wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        cur = ""
        for w in words:
            test = cur + (" " if cur else "") + w
            if font.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def draw_code_panel(self):
        # 背景
        pygame.draw.rect(self.screen, CODE_BG,
                         (0, CONTENT_Y, CODE_W, CONTENT_H))
        pygame.draw.line(self.screen, (40, 40, 55),
                         (CODE_W, CONTENT_Y), (CODE_W, CONTENT_Y + CONTENT_H))

        step = STEPS[self.step_idx]
        code_lines = step["code"].split("\n")

        line_h = self.font_code.get_height() + 2
        start_y = CONTENT_Y + 14
        max_lines = (CONTENT_H - 28) // line_h

        # 从合适行开始显示（优先显示后部有内容的部分）
        display_start = max(0, len(code_lines) - max_lines)
        # 但如果代码很短则从开头显示
        if len(code_lines) <= max_lines:
            display_start = 0

        for i in range(display_start, min(len(code_lines), display_start + max_lines)):
            y = start_y + (i - display_start) * line_h
            line = code_lines[i]

            # 行号
            num = self.font_code.render(f"{i+1:2d}", True, COLOR_LINE_NUM)
            self.screen.blit(num, (8, y))

            # 高亮包含新概念的行（如果是步骤标题行不用高亮）
            x_offset = 44

            tokens = parse_tokens(line)
            for text, color in tokens:
                if text == '':
                    continue
                rendered = self.font_code.render(text, True, color)
                self.screen.blit(rendered, (x_offset, y))
                x_offset += rendered.get_width()

    def draw_demo_panel(self):
        # 背景
        pygame.draw.rect(self.screen, PANEL_BG,
                         (DEMO_X, CONTENT_Y, DEMO_W, CONTENT_H))
        self.demo_surface.fill(PANEL_BG)
        step = STEPS[self.step_idx]
        step["demo"].draw(self.demo_surface)
        # 标题角标
        title_bg = pygame.Surface((DEMO_W, 28), pygame.SRCALPHA)
        title_bg.fill((0, 0, 0, 80))
        self.demo_surface.blit(title_bg, (0, 0))
        if self.step_idx == 0:
            label = "效果预览"
        elif self.step_idx == self.step_total - 1:
            label = "完整游戏 (可操作)"
        else:
            label = "效果预览 (可操作)" if self.step_idx >= 4 else "效果预览"
        t = self.font_small.render(label, True, (180, 180, 200))
        self.demo_surface.blit(t, (10, 4))
        self.screen.blit(self.demo_surface, (DEMO_X, CONTENT_Y))

    def draw_step_title(self):
        # 代码面板顶部的步骤标题
        step = STEPS[self.step_idx]
        title_bg = pygame.Surface((CODE_W, 32), pygame.SRCALPHA)
        title_bg.fill((0, 0, 0, 100))
        self.screen.blit(title_bg, (0, CONTENT_Y))
        t = self.font_normal.render(f"  {step['title']}", True, COLOR_HIGHLIGHT)
        self.screen.blit(t, (6, CONTENT_Y + 4))

    def handle_click(self, pos):
        mx, my = pos
        btn_y = WINDOW_H - 40
        btn_w = 100
        btn_h = 30
        # Prev 按钮
        if 20 <= mx <= 20 + btn_w and btn_y <= my <= btn_y + btn_h:
            if self.step_idx > 0:
                self.step_idx -= 1
                self.restart_demo()
        # Next 按钮
        if 130 <= mx <= 130 + btn_w and btn_y <= my <= btn_y + btn_h:
            if self.step_idx < self.step_total - 1:
                self.step_idx += 1
                self.restart_demo()

    def handle_key(self, key):
        if key == pygame.K_LEFT:
            if self.step_idx > 0:
                self.step_idx -= 1
                self.restart_demo()
        elif key == pygame.K_RIGHT:
            if self.step_idx < self.step_total - 1:
                self.step_idx += 1
                self.restart_demo()
        elif key == pygame.K_ESCAPE:
            self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()

            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN:
                    self.handle_key(e.key)
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        self.handle_click(e.pos)

            # 更新 demo（传递键盘事件给 demo）
            step = STEPS[self.step_idx]
            demo_events = [e for e in events if e.type in (pygame.KEYDOWN, pygame.KEYUP)]
            step["demo"].update(demo_events, dt)

            # 绘制
            self.screen.fill(PANEL_BG)
            self.draw_header()
            self.draw_code_panel()
            self.draw_step_title()
            self.draw_demo_panel()
            self.draw_bottom()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    TutorialApp().run()
