# 评估框架

评估框架**独立于单元测试**。它通过渲染场景并与标准 PNG 比较来进行视觉回归测试。

## 结构

```
evaluation/
├── cases/      # 场景输入 JSON 文件
├── expected/   # 标准 PNG 图片
├── output/     # 渲染的 PNG（生成的）
└── diffs/      # 失败时的差异图片
```

## 运行评估

```bash
uv run talk2scene eval.run=true
```

## 工作原理

1. 对于 `evaluation/cases/` 中的每个 `.json` 用例：
   - 渲染场景为 PNG
   - 与 `evaluation/expected/` 中的期望 PNG 比较
   - 如果差异超过容差，写入差异图片
2. 生成 JSON 报告和文本摘要

## 测试 vs 评估

| | tests/ | evaluation/ |
|---|--------|-------------|
| 类型 | 单元测试 | 视觉回归 |
| 工具 | pytest | 内置运行器 |
| 检查 | 逻辑正确性 | 渲染正确性 |
| 产物 | - | PNG 渲染 + 差异图 |
