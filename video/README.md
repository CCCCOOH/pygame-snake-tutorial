# 🎬 项目宣传视频

使用 [Remotion](https://remotion.dev) + [inference.sh](https://inference.sh) 渲染。

## 文件

- `snake_promo.tsx` — Remotion 组件源码（40 秒宣传视频）

## 渲染

```bash
# 安装 belt CLI
brew install inference-sh/tap/belt
belt login

# 渲染视频
belt app run infsh/remotion-render --input '{
  "code": "'"$(cat snake_promo.tsx | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"'",
  "duration_seconds": 40,
  "fps": 30,
  "width": 1920,
  "height": 1080
}'
```

## 视频内容

| 时间 | 场景 |
|------|------|
| 0-4s | 开场：标题 + 蛇 emoji 动画 |
| 4-12s | 10 个步骤卡片展示 |
| 12-22s | API 悬浮提示 + 点击跳转文档演示 |
| 22-32s | 完整贪吃蛇游戏动画 |
| 32-40s | 设置菜单 + GitHub CTA |
