# 🖥️ 浏览器前端

前端加载 JSONL 事件并在浏览器中进行场景图层动画。

## ⏯️ 模式

### ⏪ 回放模式
从头开始播放事件，基于时间戳控制时序。

### 📡 实时模式
显示最新事件，轮询新事件。

## 🍰 图层顺序

### 普通模式（`CG_None`）

```mermaid
block-beta
    columns 1
    EXP["EXP — 表情 (z-index: 4)"]
    ACT["ACT — 动作 (z-index: 3)"]
    STA["STA — 姿态 (z-index: 2)"]
    BG["BG — 背景 (z-index: 1)"]
```

### CG模式（CG不为 `CG_None`）

```mermaid
block-beta
    columns 1
    CG["CG — 全场景插画\n（替换 BG、STA、ACT、EXP）"]
```

## ▶️ 使用方法

1. 🌐 在浏览器中打开 `web/index.html`
2. 📂 加载 `.jsonl` 文件
3. 📁 设置素材基础路径
4. ⏯️ 点击 **Replay** 或 **Realtime**
