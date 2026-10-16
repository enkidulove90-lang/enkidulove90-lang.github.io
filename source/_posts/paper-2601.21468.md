---
title: "MemOCR：面向高效长程推理的布局感知视觉记忆"
date: 2026-01-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2601.21468
arxiv_id: "2601.21468"
description: "论文提出 MemOCR，一种多模态记忆智能体，将智能体的历史记忆从一维文本流转变为二维视觉画布，通过视觉布局实现自适应信息密度。"
---

> 论文：[arXiv 2601.21468](https://arxiv.org/abs/2601.21468) · PDF：[本地阅读](/papers/2601.21468.pdf)

论文提出 MemOCR，一种多模态记忆智能体，将智能体的历史记忆从一维文本流转变为二维视觉画布，通过视觉布局实现自适应信息密度。MemOCR 包含两个阶段：文本域的记忆草稿（用 Markdown 等富文本格式标注视觉优先级）和视觉域的记忆阅读（将富文本渲染为图像，以视觉 patch token 作为记忆预算）。通过 GRPO 强化学习与预算感知训练目标，MemOCR 在极端记忆预算下仍能保持关键证据可读，在多个长上下文 QA 基准上显著优于文本记忆基线，并在 16 token 预算下实现约 8 倍的有效上下文利用率提升。

## 研究问题

论文提出 MemOCR，一种多模态记忆智能体，将智能体的历史记忆从一维文本流转变为二维视觉画布，通过视觉布局实现自适应信息密度。MemOCR 包含两个阶段：文本域的记忆草稿（用 Markdown 等富文本格式标注视觉优先级）和视觉域的记忆阅读（将富文本渲染为图像，以视觉 patch token 作为记忆预算）。通过 GRPO 强化学习与预算感知训练目标，MemOCR 在极端记忆预算下仍能保持关键证据可读，在多个长上下文 QA 基准上显著优于文本记忆基线，并在 16 token 预算下实现约 8 倍的有效上下文利用率提升。

## 方法：核心思路与整体框架

MemOCR 将长程智能体记忆管理形式化为有限上下文下的预算分配问题。方法上，智能体在文本域增量维护富文本记忆（Markdown 格式），通过标题、加粗、字号等格式显式编码视觉优先级；随后轻量渲染器将富文本渲染为 2D 记忆图像，以视觉 patch token 数量作为记忆预算。训练采用 GRPO 强化学习，结合三种预算感知任务（标准 QA、增强记忆 QA、增强问题 QA），阅读行为使用任务特定优势更新，草稿行为使用聚合优势更新，从而学习在极端压缩下保持关键证据可见的布局策略。

![图 1：Figure 7. Case study at an extreme memory budget (16 tokens). (Left) The textual baseline fails due to hard truncation of the context. (Middle) MemOCR without layout control fails because uniform text becomes unreadable after down-sampling. (Right) MemOCR preserves the crucial evidence “Gene MacLellan” through adaptive layout, enabling correct reasoning even at low resolution.](/images/papers/2601.21468/8ded92beebf30e4c851ff408a0e4e69922a0cba01fb8b0b5c34ee0ad13d08b4a.jpg)

*图 1 · 原图说明：Figure 7. Case study at an extreme memory budget (16 tokens). (Left) The textual baseline fails due to hard truncation of the context. (Middle) MemOCR without layout control fails because uniform text becomes unreadable after down-sampling. (Right) MemOCR preserves the crucial evidence “Gene MacLellan” through adaptive layout, enabling correct reasoning even at low resolution.*

**图示解释：** 在 10K 上下文全预算下，MemOCR 平均准确率达 74.6%，超过最强基线 MemAgent 的 67.8%。

## 创新点

1. 提出从一维文本记忆到二维视觉记忆的范式转变，将历史表示为图像而非 token 流，通过视觉显著性（标题、加粗、字号）实现非均匀预算分配，解耦信息密度与 token 成本。
2. 设计两阶段记忆生命周期：文本域的记忆草稿（增量维护富文本记忆并分配视觉优先级）和视觉域的记忆阅读（轻量渲染器将富文本编译为 2D 图像，作为唯一工作上下文），并通过分辨率调整灵活控制预算。
3. 提出预算感知的强化学习训练目标，构建标准 QA、增强记忆 QA（4× 下采样）和增强问题 QA 三种互补任务，防止智能体采用均匀中等字号的捷径策略，迫使关键证据在极端压缩下仍保持可见。

## 实验：数据、基线与结果

### 数据集与设置

训练使用 HotpotQA，并用干扰文档填充至约 30K token。评估使用多跳 HotpotQA 和 2Wiki，以及单跳 NQ 和 TriviaQA，上下文填充至 10K/30K/100K token。由于长上下文 QA 耗时，遵循 Yu et al. 将四个基准随机下采样至 128 个样本。评估时使用固定干扰文档采样种子以保证可比性。LOCOMO 用于零样本对话记忆评估。

### Benchmark 与结果

在 10K 上下文全预算下，MemOCR 平均准确率达 74.6%，超过最强基线 MemAgent 的 67.8%。在 16 token 极端预算下，MemOCR 保持 62.2% 平均准确率，仅相对下降 16.6%，而 MemAgent 从 67.8% 降至 31.6%（下降 53.3%）。在 TriviaQA 10K 上下文下，MemOCR 在 16 token 时达到 80.8%，甚至高于 1024 token 时的 79.6%。与无限存储的 RAG 方法相比，MemOCR 在 10K 上下文 B=1024 时达 74.6%，超过最佳无限预算基线 HyMem 的 56.4% 达 18.2 个百分点。跨模型迁移中，GPT-4o 读取 MemOCR 记忆在 HotpotQA 10K 下达 87.7%，超过原生 Qwen2.5-VL 的 84.8%。LOCOMO 零样本评估中，MemOCR 在所有预算下均优于 Mem-α。

![图 2：Figure 8. Failure Mode Analysis under Resource Constraints (16-token budget). (Top) In comparative reasoning (i.e., to choose among two candidates), while the layout successfully highlights entity headers, the body text containing crucial attributes is compressed into unreadable noise during downsampling. (Bottom) When the rich-text memory length exceeds the visual canvas capacity, the forced font scaling drops below the visual encoder’s resolution threshold, resulting in information loss.](/images/papers/2601.21468/1b434ef24e833e7fbb912a55d8efdf1100c56a17b852f0b3ddae450c8dbff5e8.jpg)

*图 2 · 原图说明：Figure 8. Failure Mode Analysis under Resource Constraints (16-token budget). (Top) In comparative reasoning (i.e., to choose among two candidates), while the layout successfully highlights entity headers, the body text containing crucial attributes is compressed into unreadable noise during downsampling. (Bottom) When the rich-text memory length exceeds the visual canvas capacity, the forced font scaling drops below the visual encoder’s resolution threshold, resulting in information loss.*

**图示解释：** 在 10K 上下文全预算下，MemOCR 平均准确率达 74.6%，超过最强基线 MemAgent 的 67.8%。

### 消融实验

对比两类基线：(1) 原始历史记忆，包括 Qwen2.5-Instruct、R1-Distill Qwen、Qwen2.5-1M-Instruct；(2) 文本摘要记忆，包括 Mem0、Mem-α、MemAgent。此外还与 RAG 记忆方法（SimpleMem、LightMem、HyMem）对比。消融设置包括 MemOCR w/o Visual Layout（保留视觉模态但移除格式线索）和 w/o Layout 变体。

## 总结

论文提出 MemOCR，一种多模态记忆智能体，将智能体的历史记忆从一维文本流转变为二维视觉画布，通过视觉布局实现自适应信息密度。

## References

- MemOCR: Layout-Aware Visual Memory for Efficient Long-Horizon Reasoning：[arXiv 2601.21468](https://arxiv.org/abs/2601.21468)

- [PDF源文件](/papers/2601.21468.pdf)
