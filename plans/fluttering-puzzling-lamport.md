# Paimon Prime Dashboard - Playful Geometric UI 改造计划

## 1. 色彩方案重设计

### 主色调 - 新蓝色方案

当前 #007AFF (Apple System Blue) 的问题：
- 过于企业化/科技感
- 缺乏活力和趣味性
- 与 Playful Geometric 的 Memphis Group 美学不匹配

**推荐新蓝色: #3366FF (Vibrant Blue)**

对比分析：
| 颜色 | Hex | 特点 |
|------|-----|------|
| 当前蓝 | #007AFF | 冷淡、企业化、iOS系统蓝 |
| **推荐蓝** | #3366FF | 活力、饱和度高、更有趣味 |
| 备选1 | #2563EB | Tailwind Blue 600, 现代感强 |
| 备选2 | #4F46E5 | 带紫调的靛蓝，更潮流 |

### 完整色板

```typescript
const playfulColors = {
  primary: {
    main: '#3366FF',      // Vibrant Blue - 主色
    light: '#6699FF',     // 亮蓝
    dark: '#0044CC',      // 深蓝
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#FF6B9D',      // Bubblegum Pink - 辅色
    light: '#FF9BC1',
    dark: '#CC4477',
  },
  accent: {
    yellow: '#FFD93D',    // Sunshine Yellow
    mint: '#6FEDD6',      // Mint Green
    coral: '#FF8C69',     // Coral
  },
  background: {
    default: '#FFF8F0',   // Warm Cream
    paper: '#FFFFFF',
    dark: '#1A1A2E',      // Deep Navy (暗色模式)
  },
  grey: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#EEEEEE',
    800: '#424242',
    900: '#212121',
  },
}
```

## 2. 设计 Token 定义

### 字体系统

```typescript
typography: {
  fontFamily: '"Plus Jakarta Sans", "Inter", sans-serif',
  h1: { fontFamily: '"Outfit", sans-serif', fontWeight: 800 },
  h2: { fontFamily: '"Outfit", sans-serif', fontWeight: 700 },
  h3: { fontFamily: '"Outfit", sans-serif', fontWeight: 700 },
  h4: { fontFamily: '"Outfit", sans-serif', fontWeight: 600 },
  button: { fontFamily: '"Plus Jakarta Sans"', fontWeight: 700, textTransform: 'none' },
}
```

### 圆角系统

```typescript
shape: {
  borderRadius: 16,  // 基础圆角
}

// 自定义圆角变量
const radius = {
  sm: 8,      // 小元素
  md: 16,     // 卡片、按钮
  lg: 24,     // 大容器
  full: 9999, // 药丸形状
}
```

### 阴影系统 - Hard Shadow (核心特色)

```typescript
// 去除所有模糊阴影，使用硬边阴影
shadows: [
  'none',
  '2px 2px 0px rgba(0,0,0,0.15)',   // elevation 1
  '4px 4px 0px rgba(0,0,0,0.15)',   // elevation 2 - 主要使用
  '6px 6px 0px rgba(0,0,0,0.15)',   // elevation 3
  '8px 8px 0px rgba(0,0,0,0.2)',    // elevation 4
  // ... 其余全部设为 '4px 4px 0px rgba(0,0,0,0.15)'
]
```

### 边框系统

```typescript
// Chunky borders - 粗边框特色
border: {
  thin: '2px solid',
  medium: '3px solid',
  thick: '4px solid',
}
```

## 3. 组件样式改造

### 3.1 MuiCard (Sticker Card 风格)

```typescript
MuiCard: {
  styleOverrides: {
    root: {
      borderRadius: 16,
      border: '3px solid #1A1A2E',
      boxShadow: '4px 4px 0px #1A1A2E',
      transition: 'transform 0.2s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.2s',
      '&:hover': {
        transform: 'translate(-2px, -2px)',
        boxShadow: '6px 6px 0px #1A1A2E',
      },
    },
  },
},
```

### 3.2 MuiButton (Candy Button 风格)

```typescript
MuiButton: {
  styleOverrides: {
    root: {
      borderRadius: 12,
      fontWeight: 700,
      textTransform: 'none',
      border: '3px solid #1A1A2E',
      boxShadow: '4px 4px 0px #1A1A2E',
      transition: 'all 0.15s cubic-bezier(0.34,1.56,0.64,1)',
      '&:hover': {
        transform: 'translate(-2px, -2px)',
        boxShadow: '6px 6px 0px #1A1A2E',
      },
      '&:active': {
        transform: 'translate(2px, 2px)',
        boxShadow: '2px 2px 0px #1A1A2E',
      },
    },
    containedPrimary: {
      backgroundColor: '#3366FF',
      '&:hover': { backgroundColor: '#2255EE' },
    },
    containedSecondary: {
      backgroundColor: '#FF6B9D',
      '&:hover': { backgroundColor: '#EE5A8C' },
    },
  },
},
```

### 3.3 MuiChip (Tag/Badge 风格)

```typescript
MuiChip: {
  styleOverrides: {
    root: {
      borderRadius: 9999, // pill shape
      fontWeight: 600,
      border: '2px solid #1A1A2E',
      boxShadow: '2px 2px 0px #1A1A2E',
    },
    colorPrimary: {
      backgroundColor: '#3366FF',
      color: '#FFFFFF',
    },
  },
},
```

### 3.4 MuiTextField (Decorated Input)

```typescript
MuiTextField: {
  styleOverrides: {
    root: {
      '& .MuiOutlinedInput-root': {
        borderRadius: 12,
        border: '3px solid #1A1A2E',
        boxShadow: '3px 3px 0px #1A1A2E',
        backgroundColor: '#FFFFFF',
        '&:hover': {
          borderColor: '#3366FF',
        },
        '&.Mui-focused': {
          borderColor: '#3366FF',
          boxShadow: '3px 3px 0px #3366FF',
        },
        '& fieldset': {
          border: 'none', // 移除默认 fieldset 边框
        },
      },
    },
  },
},
```

## 4. 动画系统

### CSS Keyframes (globals.css)

```css
@keyframes bounce-in {
  0% { transform: scale(0.9); opacity: 0; }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes wiggle {
  0%, 100% { transform: rotate(-3deg); }
  50% { transform: rotate(3deg); }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

@keyframes pulse-grow {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```

### Bounce Easing

```typescript
const bounceEasing = 'cubic-bezier(0.34, 1.56, 0.64, 1)';
```

## 5. 装饰元素系统

### 几何装饰组件

```tsx
// 圆点装饰
const DotPattern = () => (
  <Box sx={{
    position: 'absolute',
    width: 8, height: 8,
    borderRadius: '50%',
    bgcolor: 'accent.yellow',
  }} />
);

// 星星装饰
const StarDecoration = () => (
  <Box component="span" sx={{
    display: 'inline-block',
    '&::before': { content: '"★"' },
    color: '#FFD93D',
    animation: 'wiggle 2s infinite',
  }} />
);

// 波浪线装饰
const WavyLine = () => (
  <Box sx={{
    height: 4,
    background: 'repeating-linear-gradient(90deg, #3366FF 0px, #3366FF 10px, transparent 10px, transparent 20px)',
  }} />
);
```

## 6. 文件修改清单

### Phase 1: 基础设施 (theme + globals)

| 文件 | 改动内容 |
|------|----------|
| `src/config/theme.ts` | 完全重写 palette, typography, shadows, components |
| `src/app/globals.css` | 添加字体导入, keyframes, 工具类 |

### Phase 2: PP Dashboard 组件

| 文件 | 改动内容 |
|------|----------|
| `src/components/pp/PPDashboard.tsx` | 应用新卡片样式、布局调整 |
| `src/components/pp/NavChart.tsx` | 图表配色更新 |
| `src/components/pp/AssetAllocation.tsx` | 饼图/条形图配色 |
| `src/components/pp/TransactionPanel.tsx` | 按钮、Tab 样式 |
| `src/components/pp/DepositForm.tsx` | 输入框、按钮样式 |
| `src/components/pp/WithdrawForm.tsx` | 输入框、按钮样式 |

### Phase 3: 装饰元素添加

| 文件 | 改动内容 |
|------|----------|
| `src/components/common/GeometricDecorations.tsx` | 新建：几何装饰组件库 |
| `src/components/pp/PPDashboard.tsx` | 添加装饰元素 |

## 7. 实施顺序

```
Step 1: 更新 theme.ts - 色彩、字体、阴影、组件样式
        ↓
Step 2: 更新 globals.css - 字体导入、动画keyframes、工具类
        ↓
Step 3: 更新 PPDashboard.tsx - 主要布局和样式
        ↓
Step 4: 更新子组件 - NavChart, AssetAllocation, TransactionPanel
        ↓
Step 5: 添加几何装饰元素
        ↓
Step 6: 测试和微调
```

## 8. 视觉效果预览

### 改造前 vs 改造后

| 元素 | 改造前 | 改造后 |
|------|--------|--------|
| 卡片 | 柔和阴影、大圆角、无边框 | 硬阴影(4px)、粗边框(3px)、hover位移 |
| 按钮 | 柔和阴影、渐变 | 硬阴影、纯色、按压回弹 |
| 色彩 | #007AFF 企业蓝 | #3366FF 活力蓝 + 粉/黄/薄荷点缀 |
| 字体 | Inter | Outfit(标题) + Plus Jakarta Sans(正文) |
| 动效 | 淡入淡出 | Bounce弹性动画 |

## 9. 风险和注意事项

1. **字体加载**: 需要确保 Google Fonts 正确加载 Outfit 和 Plus Jakarta Sans
2. **阴影性能**: 硬阴影比模糊阴影性能更好，无需担心
3. **向后兼容**: 改动仅影响 PP Dashboard，不影响其他页面
4. **响应式**: 需确保新样式在移动端正常显示

---

**确认后即可开始实施 Phase 1**
