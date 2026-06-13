# 🐍 用 Pygame 写贪吃蛇 —— 从零开始的互动教程

本教程将经典的**贪吃蛇**游戏拆解为 **10 个渐进步骤**，带你从 `pygame.init()` 开始，一步步写完一个完整的贪吃蛇游戏。每一步都可以运行程序，看到代码和效果的对应关系。

---

## 目录

- [准备工作](#准备工作)
- [核心概念：Pygame 游戏循环](#核心概念pygame-游戏循环)
- [Step 1 —— 初始化 Pygame](#step-1--初始化-pygame)
- [Step 2 —— 绘制网格](#step-2--绘制网格)
- [Step 3 —— 绘制蛇](#step-3--绘制蛇)
- [Step 4 —— 蛇的移动](#step-4--蛇的移动)
- [Step 5 —— 键盘控制](#step-5--键盘控制)
- [Step 6 —— 食物生成](#step-6--食物生成)
- [Step 7 —— 吃食物与成长](#step-7--吃食物与成长)
- [Step 8 —— 碰撞检测](#step-8--碰撞检测)
- [Step 9 —— 游戏结束画面](#step-9--游戏结束画面)
- [Step 10 —— 完整贪吃蛇](#step-10--完整贪吃蛇)
- [完整源代码](#完整源代码)
- [Pygame API 速查表](#pygame-api-速查表)
- [拓展练习](#拓展练习)

---

## 准备工作

### 安装

```bash
# Python 3.13+
python3 -m venv .venv
source .venv/bin/activate
pip install pygame
```

### 运行

```bash
python snake_tutorial.py
```

程序启动后会显示教程窗口。用 `←` `→` 方向键切换步骤，右侧实时预览效果。

---

## 核心概念：Pygame 游戏循环

所有 Pygame 程序都遵循同一个**游戏循环**（Game Loop）模式：

```python
# 1. 初始化
pygame.init()
screen = pygame.display.set_mode((宽度, 高度))

# 2. 游戏循环
running = True
while running:
    # 2a. 处理事件（键盘、鼠标、窗口关闭）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2b. 更新游戏状态（移动、碰撞等）
    # ...

    # 2c. 绘制画面
    screen.fill((背景色))
    # ... 画蛇、画食物 ...
    pygame.display.flip()

# 3. 退出
pygame.quit()
```

这个循环每秒运行约 10-60 次（帧），每次循环称为一**帧**（frame）。理解了这一点，后面所有步骤都是在这个框架上"添砖加瓦"。

---

## Step 1 —— 初始化 Pygame

**目标：** 创建一个空白窗口，让它保持运行不闪退。

```python
import pygame
import random
import sys

pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("贪吃蛇")
clock = pygame.time.Clock()

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    screen.fill((20, 20, 30))
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
```

**新知识点：**

| API | 作用 |
|-----|------|
| `pygame.init()` | 初始化 Pygame，必须在所有操作之前调用 |
| `pygame.display.set_mode((w, h))` | 创建一个 `w×h` 像素的窗口 |
| `pygame.display.set_caption(str)` | 设置窗口标题 |
| `pygame.event.get()` | 获取事件列表（按键、鼠标、关闭等） |
| `pygame.QUIT` | 用户点击关闭按钮的事件类型 |
| `screen.fill(color)` | 用颜色填充整个屏幕 |
| `pygame.display.flip()` | 将绘制内容刷新到屏幕上（必须调用才可见） |
| `pygame.time.Clock()` / `clock.tick(n)` | 限制帧率为 n FPS |
| `pygame.quit()` | 退出时清理资源 |

> **为什么需要 `clock.tick()`？** 没有它，循环会跑到 CPU 的极限（几百帧/秒），白白消耗资源。用 `tick(10)` 限制为 10 FPS 就足够了。

---

## Step 2 —— 绘制网格

**目标：** 在窗口中画出网格线，让蛇"在格子上走"。

```python
CELL_SIZE = 30      # 每个格子 30px
GRID_W = 20         # 20 列
GRID_H = 20         # 20 行
WIDTH = CELL_SIZE * GRID_W
HEIGHT = CELL_SIZE * GRID_H

screen = pygame.display.set_mode((WIDTH, HEIGHT))

# 画竖线
for x in range(0, WIDTH, CELL_SIZE):
    pygame.draw.line(screen, (50, 50, 70), (x, 0), (x, HEIGHT))

# 画横线
for y in range(0, HEIGHT, CELL_SIZE):
    pygame.draw.line(screen, (50, 50, 70), (0, y), (WIDTH, y))
```

**新知识点：**

| API | 作用 |
|-----|------|
| `pygame.draw.line(surface, color, start, end)` | 画线段。`start` 和 `end` 是 `(x, y)` 元组 |

> **设计思路：** 蛇在"格子"上移动，每次走一格。用常量定义格子大小和数量，方便后续调整。

---

## Step 3 —— 绘制蛇

**目标：** 用列表表示蛇的身体，画在网格上。

```python
# 蛇 = 坐标列表，第 0 个是蛇头
snake = [(10, 10), (9, 10), (8, 10)]

# 遍历蛇身，画矩形
for seg in snake:
    x = seg[0] * CELL_SIZE  # 网格坐标 → 像素坐标
    y = seg[1] * CELL_SIZE
    rect = (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
    pygame.draw.rect(screen, (0, 200, 80), rect, border_radius=4)
```

**新知识点：**

| API | 作用 |
|-----|------|
| `pygame.draw.rect(surface, color, rect)` | 画矩形。`rect` 是 `(x, y, w, h)` 元组 |
| 坐标列表 | 用 `[(x1,y1), (x2,y2), ...]` 表示蛇身，非常直观 |

> **关键设计：** `CELL_SIZE - 2` 让蛇身格子和网格线之间留 1px 的间隙，视觉上更像"方格蛇"。

---

## Step 4 —— 蛇的移动

**目标：** 让蛇自动向一个方向移动。

```python
direction = (1, 0)  # 每帧向右走 1 格

# 移动逻辑（在主循环中）
move_timer += dt
if move_timer > 0.2:          # 每 0.2 秒移动一格
    move_timer = 0
    hx, hy = snake[0]
    new_head = (hx + direction[0], hy + direction[1])
    snake.insert(0, new_head)  # 头部新增
    snake.pop()                # 尾部删除 → 长度不变
```

**核心原理：** 蛇的"移动"就是：
1. 在蛇头前面加一个新格子（沿方向向量）
2. 删除蛇尾最后一个格子
3. 长度不变，但位置变了——看起来蛇在"走"

**新知识点：**

| 概念 | 说明 |
|------|------|
| 方向向量 | `(dx, dy)` 表示移动方向：`(1,0)` 右、`(-1,0)` 左、`(0,-1)` 上、`(0,1)` 下 |
| `dt`（delta time） | 每帧经过的秒数，用于实现"时间驱动"的移动而非"帧驱动" |

---

## Step 5 —— 键盘控制

**目标：** 用方向键和 WASD 改变蛇的移动方向。

```python
# 在事件循环中
if e.type == pygame.KEYDOWN:
    if e.key == pygame.K_UP or e.key == pygame.K_w:
        next_dir = (0, -1)      # 上
    elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
        next_dir = (0, 1)       # 下
    elif e.key == pygame.K_LEFT or e.key == pygame.K_a:
        next_dir = (-1, 0)      # 左
    elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
        next_dir = (1, 0)       # 右

# 防止反向：新方向和当前方向不能相反
if next_dir[0] + direction[0] != 0 or next_dir[1] + direction[1] != 0:
    direction = next_dir
```

**新知识点：**

| API | 作用 |
|-----|------|
| `pygame.KEYDOWN` | 按键按下事件 |
| `e.key` | 获取按下的具体键 |
| `pygame.K_UP` / `K_DOWN` / `K_LEFT` / `K_RIGHT` | 方向键常量 |
| `pygame.K_w` / `K_a` / `K_s` / `K_d` | WASD 键常量 |

> **防反向逻辑：** 如果当前向右 `(1,0)`，用户按左 `(-1,0)`，两者之和为 0，说明是反向，忽略。防止蛇"掉头咬自己"。

---

## Step 6 —— 食物生成

**目标：** 在网格上随机生成食物。

```python
def random_food(snake):
    while True:
        x = random.randint(0, GRID_W - 1)
        y = random.randint(0, GRID_H - 1)
        if (x, y) not in snake:       # 食物不能出现在蛇身上
            return (x, y)

food = random_food(snake)

# 画食物（在主循环绘制部分）
fx, fy = food
rect = (fx * CELL_SIZE + 2, fy * CELL_SIZE + 2,
        CELL_SIZE - 4, CELL_SIZE - 4)
pygame.draw.rect(screen, (220, 40, 40), rect, border_radius=6)
```

**新知识点：**

| API | 作用 |
|-----|------|
| `random.randint(a, b)` | 生成 `[a, b]` 范围内的随机整数 |

---

## Step 7 —— 吃食物与成长

**目标：** 蛇头碰到食物时，蛇变长并生成新食物。

```python
# 移动蛇
hx, hy = snake[0]
new_head = (hx + direction[0], hy + direction[1])
snake.insert(0, new_head)

# 碰撞检测：蛇头 == 食物位置
if new_head == food:
    score += 1
    food = random_food(snake)
    # 不 pop → 蛇自动变长
else:
    snake.pop()  # 没吃到 → 删除尾部，长度不变
```

**核心原理：** 吃食物就是"不删尾巴"——正常移动会 `snake.pop()` 删掉尾巴来保持长度；如果蛇头碰到了食物，就不删尾巴，蛇就自然长了一格。

---

## Step 8 —— 碰撞检测

**目标：** 蛇撞墙或撞到自己时，游戏结束。

```python
# 墙壁碰撞
if (new_head[0] < 0 or
    new_head[0] >= GRID_W or
    new_head[1] < 0 or
    new_head[1] >= GRID_H):
    game_over = True

# 自身碰撞
if new_head in snake[1:]:    # snake[1:] 是除蛇头外的身体
    game_over = True
```

> **`snake[1:]` 技巧：** 蛇头刚插入到 `snake[0]`，`snake[1:]` 是插入前的身体。如果蛇头的位置出现在了身体中——撞自己了。

---

## Step 9 —— 游戏结束画面

**目标：** 死亡后显示得分和重新开始提示。

```python
if game_over:
    screen.fill((20, 20, 30))
    # 显示 "Game Over"
    game_over_text = font.render("Game Over", True, (220, 40, 40))
    screen.blit(game_over_text, (WIDTH//2 - 100, HEIGHT//2 - 40))
    # 显示分数
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - 50, HEIGHT//2 + 20))
    # 提示按空格重来
    hint = font.render("Press SPACE to restart", True, GRAY)
    screen.blit(hint, (WIDTH//2 - 80, HEIGHT//2 + 80))
    pygame.display.flip()

    # 等待空格键
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                waiting = False
            elif e.type == pygame.QUIT:
                running = False
                waiting = False
    # 重置游戏状态
    if waiting == False:
        snake = [(10, 10), (9, 10), (8, 10)]
        direction = (1, 0)
        score = 0
        food = random_food(snake)
        game_over = False
```

**新知识点：**

| API | 作用 |
|-----|------|
| `font.render(text, antialias, color)` | 将文字渲染为图像 Surface |
| `surface.blit(source, (x, y))` | 将图像绘制到目标位置 |
| `pygame.K_SPACE` | 空格键常量 |

---

## Step 10 —— 完整贪吃蛇

**目标：** 把所有步骤整合起来，得到完整的可玩游戏。

将前面 9 步的代码组合在一起，就是完整的贪吃蛇游戏：

- Step 1 的初始化 + 游戏循环框架
- Step 2 的网格绘制
- Step 3~5 的蛇身数据结构 + 移动 + 键盘控制
- Step 6~7 的食物生成 + 吃食物成长
- Step 8~9 的碰撞检测 + 结束画面

程序启动后导航到 Step 10，右侧就是完整的可玩游戏。按 **W/A/S/D** 控制蛇的移动。

---

## 完整源代码

以下是完整贪吃蛇游戏的精简版源码（约 80 行），适合作为参考：

```python
import pygame
import random

# 初始化
pygame.init()
CELL, W, H = 30, 20, 20
screen = pygame.display.set_mode((CELL * W, CELL * H))
pygame.display.set_caption("贪吃蛇")
clock = pygame.time.Clock()

# 游戏状态
snake = [(10, 10), (9, 10), (8, 10)]
direction = (1, 0)
next_dir = (1, 0)
food = None
score = 0
game_over = False
move_timer = 0


def rand_food():
    while True:
        f = (random.randint(0, W - 1), random.randint(0, H - 1))
        if f not in snake:
            return f


food = rand_food()

running = True
while running:
    dt = clock.tick(60) / 1000.0

    # === 事件处理 ===
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if game_over and e.key == pygame.K_SPACE:
                snake = [(10, 10), (9, 10), (8, 10)]
                direction = next_dir = (1, 0)
                score = 0
                game_over = False
                food = rand_food()
            elif not game_over:
                key_map = {
                    pygame.K_w: (0, -1), pygame.K_s: (0, 1),
                    pygame.K_a: (-1, 0), pygame.K_d: (1, 0),
                }
                if e.key in key_map:
                    nd = key_map[e.key]
                    if nd[0] + direction[0] != 0 or nd[1] + direction[1] != 0:
                        next_dir = nd

    if game_over:
        screen.fill((20, 20, 30))
        font = pygame.font.Font(None, 36)
        go = font.render("Game Over", True, (220, 40, 40))
        sc = font.render(f"Score: {score}", True, (255, 255, 255))
        hint = font.render("Press SPACE", True, (140, 140, 160))
        screen.blit(go, (screen.get_width() // 2 - go.get_width() // 2, 200))
        screen.blit(sc, (screen.get_width() // 2 - sc.get_width() // 2, 250))
        screen.blit(hint, (screen.get_width() // 2 - hint.get_width() // 2, 300))
        pygame.display.flip()
        continue

    # === 更新 ===
    direction = next_dir
    move_timer += dt
    if move_timer > 0.15:
        move_timer = 0
        hx, hy = snake[0]
        new_head = (hx + direction[0], hy + direction[1])

        # 碰撞检测
        if (new_head[0] < 0 or new_head[0] >= W or
                new_head[1] < 0 or new_head[1] >= H or
                new_head in snake):
            game_over = True
            continue

        snake.insert(0, new_head)
        if new_head == food:
            score += 1
            food = rand_food()
        else:
            snake.pop()

    # === 绘制 ===
    screen.fill((20, 20, 30))

    # 网格
    for x in range(0, CELL * W, CELL):
        pygame.draw.line(screen, (35, 35, 55), (x, 0), (x, CELL * H))
    for y in range(0, CELL * H, CELL):
        pygame.draw.line(screen, (35, 35, 55), (0, y), (CELL * W, y))

    # 食物
    fx, fy = food
    pygame.draw.rect(screen, (220, 40, 40),
                     (fx * CELL + 2, fy * CELL + 2, CELL - 4, CELL - 4),
                     border_radius=6)

    # 蛇
    for i, (sx, sy) in enumerate(snake):
        color = (0, 220, 120) if i == 0 else (0, 180, 80)
        pygame.draw.rect(screen, color,
                         (sx * CELL + 1, sy * CELL + 1, CELL - 2, CELL - 2),
                         border_radius=4)

    # 分数
    font = pygame.font.Font(None, 28)
    score_surf = font.render(f"Score: {score}", True, (200, 200, 220))
    screen.blit(score_surf, (10, 10))

    pygame.display.flip()

pygame.quit()
```

---

## Pygame API 速查表

本教程涉及的所有 Pygame API 一览：

### 系统

| API | 说明 |
|-----|------|
| `pygame.init()` | 初始化所有模块 |
| `pygame.quit()` | 卸载所有模块，释放资源 |

### 窗口

| API | 说明 |
|-----|------|
| `pygame.display.set_mode((w, h))` | 创建窗口 |
| `pygame.display.set_caption(str)` | 设置标题 |
| `pygame.display.flip()` | 刷新画面 |

### 事件

| API | 说明 |
|-----|------|
| `pygame.event.get()` | 获取所有事件 |
| `pygame.QUIT` | 关闭窗口事件 |
| `pygame.KEYDOWN` / `KEYUP` | 按键按下/松开 |
| `pygame.K_UP/DOWN/LEFT/RIGHT` | 方向键 |
| `pygame.K_w/a/s/d` | WASD 键 |
| `pygame.K_SPACE` | 空格键 |
| `pygame.K_ESCAPE` | Esc 键 |

### 绘图

| API | 说明 |
|-----|------|
| `pygame.draw.rect(surface, color, (x,y,w,h))` | 矩形 |
| `pygame.draw.line(surface, color, start, end)` | 线段 |
| `pygame.draw.circle(surface, color, center, r)` | 圆形 |

### 其他

| API | 说明 |
|-----|------|
| `pygame.time.Clock()` / `clock.tick(n)` | 帧率控制 |
| `pygame.Surface((w, h))` | 创建画布 |
| `pygame.font.Font(path, size)` | 加载字体 |
| `font.render(text, aa, color)` | 渲染文字 |
| `surface.blit(source, (x, y))` | 贴图 |
| `pygame.Rect(x, y, w, h)` | 矩形对象 |
| `pygame.mouse.get_pos()` | 鼠标位置 |
| `pygame.SRCALPHA` | 透明画布标志 |

---

## 拓展练习

读完教程后，可以尝试自己添加这些功能：

| 难度 | 练习 |
|------|------|
| ⭐ | 添加音效（吃食物音效、死亡音效） |
| ⭐ | 让蛇的速度随分数增加而加快 |
| ⭐ | 添加最高分记录（保存到文件） |
| ⭐⭐ | 添加障碍物，碰到也会死亡 |
| ⭐⭐ | 支持双人对战模式 |
| ⭐⭐⭐ | 用不同的颜色画蛇身，形成渐变色 |

---

**作者：** Sync — [synb6662@gmail.com](mailto:synb6662@gmail.com)

**许可证：** MIT
