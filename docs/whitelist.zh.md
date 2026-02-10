# 白名单与图层规则

## 白名单

`conf/whitelist.yaml` 是有效组件代码的唯一数据源。

### 类别

- **STA**（姿态）：角色身体姿势
- **EXP**（表情）：面部表情叠加
- **ACT**（动作）：角色动作动画
- **BG**（背景）：场景背景
- **CG**（CG插画）：替换整个图层合成的全场景插画（类似视觉小说/游戏中的CG场景）。当CG不为 `CG_None` 时，BG/STA/ACT/EXP 全部隐藏。

### 有效代码

| 类别 | 代码 |
|------|------|
| STA | `STA_Stand_Front`, `STA_Stand_Side`, `STA_Stand_Lean` |
| EXP | `EXP_Neutral`, `EXP_Thinking`, `EXP_Astonished`, `EXP_Concerned`, `EXP_Laugh`, `EXP_Smile_EyesClosed`, `EXP_PretendClueless` |
| ACT | `ACT_None`, `ACT_ArmsCrossed`, `ACT_PalmOpen`, `ACT_GlassesPush`, `ACT_HandOnHip`, `ACT_HeadTilt`, `ACT_MouthCover`, `ACT_ObjectPresent`, `ACT_WaveGreeting`, `ACT_WaveFarewell` |
| BG | `BG_Lab_Modern`, `BG_Garden_Rooftop`, `BG_Cafe_Starbucks` |
| CG | `CG_None`, `CG_PandorasTech` |

### 验证

所有场景事件都通过白名单验证。无效代码会自动修复为每个类别的默认（第一个）代码。

## 图层顺序

### 普通模式（`CG_None`）

```
底部 → 顶部：
BG → STA → ACT → EXP
```

### CG模式（CG不为 `CG_None`）

CG插画替换整个场景。BG、STA、ACT、EXP 全部隐藏。

此顺序在渲染器和前端中都强制执行。
