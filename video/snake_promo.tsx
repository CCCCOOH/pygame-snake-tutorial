import { useCurrentFrame, useVideoConfig, spring, interpolate, AbsoluteFill, Sequence } from "remotion";

// Color palette matching the app's dark theme
const BG = "#14141e";
const SURFACE = "#1e1e30";
const GREEN = "#00c850";
const GREEN_DARK = "#00a040";
const RED = "#dc2828";
const YELLOW = "#e2b714";
const BLUE = "#569cd6";
const WHITE = "#e8e8f0";
const GRAY = "#8888a0";
const GRAY_DARK = "#4a4a60";
const GRID_COLOR = "#2a2a3a";

// ---- Helper: Animated counter ----
function AnimatedNumber({ value, frame, startFrame }: { value: number; frame: number; startFrame: number }) {
  const progress = spring({ frame: frame - startFrame, fps: 30, config: { damping: 12, stiffness: 100 } });
  const display = Math.round(interpolate(progress, [0, 1], [0, value]));
  return <span>{Math.min(display, value)}</span>;
}

// ---- Scene 1: Opening Title (0-4s) ----
function OpeningTitle() {
  const frame = useCurrentFrame();
  const titleOpacity = interpolate(frame, [0, 15], [0, 1]);
  const subtitleOpacity = interpolate(frame, [15, 30], [0, 1]);
  const snakeY = spring({ frame, fps: 30, config: { damping: 8, stiffness: 60 }, from: -80, to: 0 });
  const scale = spring({ frame, fps: 30, config: { damping: 10, stiffness: 80 } });

  return (
    <AbsoluteFill style={{ backgroundColor: BG, display: "flex", justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      {/* Snake emoji */}
      <div style={{ fontSize: 100, transform: `translateY(${snakeY}px) scale(${scale})`, marginBottom: 20 }}>
        🐍
      </div>
      {/* Title */}
      <h1 style={{
        color: WHITE, fontSize: 72, fontWeight: 800, opacity: titleOpacity,
        letterSpacing: 4, textAlign: "center", margin: 0,
        textShadow: `0 0 40px ${GREEN}40`,
      }}>
        贪吃蛇互动教程
      </h1>
      {/* Subtitle */}
      <p style={{
        color: GRAY, fontSize: 28, opacity: subtitleOpacity, marginTop: 12,
        fontWeight: 400, letterSpacing: 1,
      }}>
        从零开始学 Pygame · 10 个渐进步骤
      </p>
      {/* Green line decoration */}
      <div style={{
        width: interpolate(frame, [20, 40], [0, 240]),
        height: 3, backgroundColor: GREEN, marginTop: 30,
        opacity: interpolate(frame, [25, 40], [0, 1]),
        borderRadius: 2,
      }} />
    </AbsoluteFill>
  );
}

// ---- Scene 2: Step Progression (4-12s) ----
const STEPS = [
  "初始化 Pygame",
  "绘制网格",
  "绘制蛇",
  "蛇的移动",
  "键盘控制",
  "食物生成",
  "吃食物成长",
  "碰撞检测",
  "游戏结束",
  "完整贪吃蛇",
];

function StepProgression() {
  const frame = useCurrentFrame();
  const localFrame = frame - 120; // starts at 4s (120 frames)

  return (
    <AbsoluteFill style={{ backgroundColor: BG, display: "flex", justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <h2 style={{ color: YELLOW, fontSize: 36, margin: 0, marginBottom: 30, opacity: interpolate(localFrame, [0, 15], [0, 1]) }}>
        📖 10 个渐进步骤
      </h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "center", maxWidth: 1000 }}>
        {STEPS.map((step, i) => {
          const cardDelay = i * 8;
          const cardOpacity = interpolate(localFrame, [cardDelay, cardDelay + 15], [0, 1]);
          const cardScale = spring({ frame: localFrame - cardDelay, fps: 30, config: { damping: 10, stiffness: 120 } });
          const isHighlight = i === 9;
          return (
            <div key={i} style={{
              backgroundColor: SURFACE,
              borderRadius: 10,
              padding: "12px 20px",
              opacity: cardOpacity,
              transform: `scale(${cardScale})`,
              border: isHighlight ? `2px solid ${GREEN}` : `1px solid ${GRAY_DARK}`,
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}>
              <span style={{ color: GRAY, fontSize: 18, fontWeight: 700 }}>0{i + 1}</span>
              <span style={{ color: isHighlight ? GREEN : WHITE, fontSize: 20, fontWeight: 600 }}>{step}</span>
            </div>
          );
        })}
      </div>
      {/* Animated snake on grid */}
      <SnakeOnGrid localFrame={localFrame - 60} />
    </AbsoluteFill>
  );
}

function SnakeOnGrid({ localFrame }: { localFrame: number }) {
  const opacity = interpolate(localFrame, [0, 20], [0, 1]);
  const gridSize = 6;
  const cellSize = 16;
  const snake = [
    [3, 3], [2, 3], [1, 3], [0, 3], [0, 2], [0, 1],
  ];

  // Animate snake moving
  const moveOffset = Math.floor(interpolate(localFrame, [30, 150], [0, 8], { extrapolateRight: "clamp" }));
  const displaySnake = snake.map(([x, y]) => [x + moveOffset, y]);

  return (
    <div style={{ marginTop: 40, opacity, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{
        display: "grid",
        gridTemplateColumns: `repeat(${gridSize + 8}, ${cellSize}px)`,
        gap: 1,
        backgroundColor: GRID_COLOR,
        padding: 2,
        borderRadius: 4,
      }}>
        {Array.from({ length: gridSize * (gridSize + 8) }, (_, i) => {
          const row = Math.floor(i / (gridSize + 8));
          const col = i % (gridSize + 8);
          const isSnake = displaySnake.some(([sx, sy]) => sx === col && sy === row);
          const isHead = displaySnake[0]?.[0] === col && displaySnake[0]?.[1] === row;
          const isFood = col === gridSize + 4 && row === 2;
          return (
            <div key={i} style={{
              width: cellSize, height: cellSize,
              backgroundColor: isHead ? GREEN : isSnake ? GREEN_DARK : isFood ? RED : SURFACE,
              borderRadius: isHead || isFood ? 3 : 1,
            }} />
          );
        })}
      </div>
      <p style={{ color: GRAY, fontSize: 16, marginTop: 10 }}>蛇身 = 坐标列表</p>
    </div>
  );
}

// ---- Scene 3: API Features (12-22s) ----
function APIFeatures() {
  const frame = useCurrentFrame();
  const localFrame = frame - 360; // starts at 12s

  const codeOpacity = interpolate(localFrame, [0, 15], [0, 1]);
  const tooltipOpacity = interpolate(localFrame, [40, 55], [0, 1]);
  const tooltipY = interpolate(localFrame, [40, 55], [-20, 0]);
  const docsOpacity = interpolate(localFrame, [80, 95], [0, 1]);
  const docsScale = spring({ frame: localFrame - 80, fps: 30, config: { damping: 8, stiffness: 120 } });

  return (
    <AbsoluteFill style={{ backgroundColor: BG, display: "flex", justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <h2 style={{ color: YELLOW, fontSize: 36, margin: 0, marginBottom: 30 }}>
        💡 代码即教程
      </h2>

      {/* Mock code panel */}
      <div style={{
        backgroundColor: SURFACE, borderRadius: 12, padding: "20px 28px",
        opacity: codeOpacity, border: `1px solid ${GRAY_DARK}`, position: "relative",
        minWidth: 500,
      }}>
        <div style={{ color: GRAY, fontSize: 14, fontFamily: "monospace" }}>
          <span style={{ color: BLUE }}>import</span> pygame{"\n"}
          <span style={{ color: BLUE }}>import</span> random{"\n\n"}
          pygame.<span style={{ color: YELLOW }}>init</span>(){"\n"}
          screen = pygame.display.<span style={{ color: YELLOW, textDecoration: "underline", textUnderlineOffset: 3 }}>set_mode</span>
          (<span style={{ color: "#ce9178" }}>(600, 600)</span>){"\n"}
          pygame.display.<span style={{ color: YELLOW, textDecoration: "underline", textUnderlineOffset: 3 }}>set_caption</span>
          (<span style={{ color: "#ce9178" }}>"贪吃蛇"</span>)
        </div>

        {/* Tooltip on hover */}
        <div style={{
          position: "absolute", top: 60, right: -220,
          backgroundColor: "#2a2a40e8", borderRadius: 8,
          padding: "10px 16px", opacity: tooltipOpacity,
          transform: `translateY(${tooltipY}px)`,
          border: `1px solid ${GRAY_DARK}`, width: 200,
        }}>
          <p style={{ color: YELLOW, fontSize: 14, margin: 0, fontWeight: 700 }}>pygame.display.set_caption</p>
          <p style={{ color: GRAY, fontSize: 12, margin: "4px 0 0 0" }}>设置窗口标题栏文字</p>
        </div>
      </div>

      {/* Click to docs */}
      <div style={{
        marginTop: 24, opacity: docsOpacity, transform: `scale(${docsScale})`,
        display: "flex", alignItems: "center", gap: 10,
        backgroundColor: SURFACE, borderRadius: 10, padding: "12px 24px",
        border: `1px solid ${BLUE}40`,
      }}>
        <span style={{ fontSize: 28 }}>🔗</span>
        <div>
          <p style={{ color: WHITE, fontSize: 18, margin: 0, fontWeight: 600 }}>点击 API → 跳转官方文档</p>
          <p style={{ color: GRAY, fontSize: 13, margin: "2px 0 0 0" }}>pygame.org/docs</p>
        </div>
      </div>
    </AbsoluteFill>
  );
}

// ---- Scene 4: Gameplay Demo (22-32s) ----
function GameplayDemo() {
  const frame = useCurrentFrame();
  const localFrame = frame - 660; // starts at 22s

  const gridSize = 15;
  const cellSize = 28;
  const snakePath = [
    [7, 7], [8, 7], [9, 7], [9, 6], [9, 5], [8, 5], [7, 5], [7, 6],
    [7, 7], [7, 8], [7, 9], [8, 9], [9, 9], [10, 9], [10, 8], [10, 7],
  ];
  const foodPositions = [
    [10, 7], [11, 5], [7, 5], [10, 9], [4, 7],
  ];

  const step = Math.floor(interpolate(localFrame, [0, 280], [0, snakePath.length + 1], { extrapolateRight: "clamp" }));
  const currentSnake = snakePath.slice(Math.max(0, step - 4), step + 1);
  const foodIdx = Math.floor(interpolate(localFrame, [0, 280], [0, foodPositions.length], { extrapolateRight: "clamp" }));
  const currentFood = foodPositions[Math.min(foodIdx, foodPositions.length - 1)];
  const score = Math.floor(interpolate(localFrame, [0, 280], [0, 5], { extrapolateRight: "clamp" }));
  const opacity = interpolate(localFrame, [0, 15], [0, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: BG, display: "flex", justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <h2 style={{ color: YELLOW, fontSize: 36, margin: 0, marginBottom: 20 }}>
        🎮 完整可游玩
      </h2>

      <div style={{ opacity, position: "relative" }}>
        {/* Grid background */}
        <div style={{
          display: "grid",
          gridTemplateColumns: `repeat(${gridSize}, ${cellSize}px)`,
          gap: 1, backgroundColor: GRID_COLOR, padding: 2, borderRadius: 6,
        }}>
          {Array.from({ length: gridSize * gridSize }, (_, i) => {
            const row = Math.floor(i / gridSize);
            const col = i % gridSize;
            const isSnake = currentSnake.some(([sx, sy]) => sx === col && sy === row);
            const isHead = currentSnake.length > 0 && currentSnake[currentSnake.length - 1]?.[0] === col && currentSnake[currentSnake.length - 1]?.[1] === row;
            const isFood = currentFood[0] === col && currentFood[1] === row && !isSnake;
            return (
              <div key={i} style={{
                width: cellSize, height: cellSize,
                backgroundColor: isHead ? GREEN : isSnake ? GREEN_DARK : isFood ? RED : SURFACE,
                borderRadius: isHead ? 5 : isFood ? 8 : 2,
                transition: "background-color 0.1s",
              }} />
            );
          })}
        </div>

        {/* Score overlay */}
        <div style={{
          position: "absolute", top: -36, left: 0,
          color: WHITE, fontSize: 18, fontWeight: 700,
          display: "flex", alignItems: "center", gap: 6,
        }}>
          🍎 Score: {score}
        </div>

        {/* WASD controls hint */}
        <div style={{
          position: "absolute", bottom: -36, left: 0, right: 0,
          display: "flex", justifyContent: "center", gap: 8,
        }}>
          {["W", "A", "S", "D"].map((k, i) => (
            <div key={i} style={{
              width: 28, height: 28, backgroundColor: SURFACE,
              borderRadius: 6, display: "flex", justifyContent: "center",
              alignItems: "center", border: `1px solid ${GRAY_DARK}`,
              color: GRAY, fontSize: 14, fontWeight: 700,
            }}>
              {k}
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
}

// ---- Scene 5: Settings + CTA (32-40s) ----
function SettingsCTA() {
  const frame = useCurrentFrame();
  const localFrame = frame - 960; // starts at 32s

  const menuOpacity = interpolate(localFrame, [0, 15], [0, 1]);
  const menuScale = spring({ frame: localFrame, fps: 30, config: { damping: 10, stiffness: 100 } });
  const githubOpacity = interpolate(localFrame, [80, 100], [0, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: BG, display: "flex", justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      {/* Settings menu mockup */}
      <div style={{
        opacity: menuOpacity, transform: `scale(${menuScale})`,
        backgroundColor: "#1c1c2e", borderRadius: 14, padding: "30px 50px",
        border: `2px solid ${GRAY_DARK}50`, width: 360, position: "relative",
      }}>
        <h3 style={{ color: WHITE, fontSize: 28, margin: 0, textAlign: "center", marginBottom: 20 }}>⚙️ 设置</h3>
        <div style={{ backgroundColor: SURFACE, borderRadius: 8, padding: "10px 16px", marginBottom: 10, textAlign: "center" }}>
          <span style={{ color: WHITE, fontSize: 18 }}>🖥️ 进入全屏</span>
        </div>
        <div style={{ backgroundColor: "#3a1a1a", borderRadius: 8, padding: "10px 16px", marginBottom: 16, textAlign: "center" }}>
          <span style={{ color: RED, fontSize: 18 }}>🚪 退出程序</span>
        </div>
        <div style={{ borderTop: `1px solid ${GRAY_DARK}`, paddingTop: 14, textAlign: "center" }}>
          <p style={{ color: GRAY, fontSize: 14, margin: 0 }}>作者：Sync</p>
          <p style={{ color: YELLOW, fontSize: 14, margin: "4px 0 0 0", textDecoration: "underline" }}>
            📧 synb6662@gmail.com
          </p>
        </div>
      </div>

      {/* GitHub CTA */}
      <div style={{
        marginTop: 40, opacity: githubOpacity, textAlign: "center",
      }}>
        <p style={{ color: WHITE, fontSize: 28, margin: 0, fontWeight: 700 }}>
          ⭐ 在 GitHub 上查看源码
        </p>
        <p style={{ color: BLUE, fontSize: 20, margin: "8px 0 0 0", fontFamily: "monospace" }}>
          github.com/CCCCOOH/pygame-snake-tutorial
        </p>
        <div style={{
          display: "flex", gap: 12, justifyContent: "center", marginTop: 16,
        }}>
          <span style={{ backgroundColor: SURFACE, borderRadius: 6, padding: "6px 16px", color: WHITE, fontSize: 16 }}>
            ⭐ Star
          </span>
          <span style={{ backgroundColor: SURFACE, borderRadius: 6, padding: "6px 16px", color: WHITE, fontSize: 16 }}>
            🍴 Fork
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
}

// ---- Main Composition ----
export default function Main() {
  return (
    <AbsoluteFill style={{ backgroundColor: BG, fontFamily: "system-ui, -apple-system, sans-serif" }}>
      <Sequence from={0} durationInFrames={120}>
        <OpeningTitle />
      </Sequence>
      <Sequence from={120} durationInFrames={240}>
        <StepProgression />
      </Sequence>
      <Sequence from={360} durationInFrames={300}>
        <APIFeatures />
      </Sequence>
      <Sequence from={660} durationInFrames={300}>
        <GameplayDemo />
      </Sequence>
      <Sequence from={960} durationInFrames={240}>
        <SettingsCTA />
      </Sequence>
    </AbsoluteFill>
  );
}
