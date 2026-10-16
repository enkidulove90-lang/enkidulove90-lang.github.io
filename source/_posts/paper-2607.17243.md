---
title: "LenGuard-GPC：面向空间推理强化学习的长度守卫与引导提示一致性"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.17243
arxiv_id: "2607.17243"
description: "论文针对多视图空间推理中GRPO强化学习存在的两个问题——稀疏结果奖励无法定位局部跨视图推理错误、以及朴素token-sum KL奖励会偏向过短回答——提出了LenGuard-GPC框架。"
---

> 论文：[arXiv 2607.17243](https://arxiv.org/abs/2607.17243) · 代码：[GitHub](https://github.com/taoxj2001/LenGuard-GPC) · PDF：[本地阅读](/papers/2607.17243.pdf)

论文针对多视图空间推理中GRPO强化学习存在的两个问题——稀疏结果奖励无法定位局部跨视图推理错误、以及朴素token-sum KL奖励会偏向过短回答——提出了LenGuard-GPC框架。该方法通过对比标准提示与引导提示下生成轨迹的token级预测分布，将KL散度作为密集过程级奖励信号，并引入分阶段长度奖励机制，在控制推理长度的同时避免短答案坍缩和边界寻求行为。在六个多视图空间推理基准上，LenGuard-GPC相比vanilla GRPO平均准确率提升2.0个百分点，相比基座模型提升5.9个百分点，同时缩短了平均响应长度。

## 研究问题

论文针对多视图空间推理中GRPO强化学习存在的两个问题——稀疏结果奖励无法定位局部跨视图推理错误、以及朴素token-sum KL奖励会偏向过短回答——提出了LenGuard-GPC框架。该方法通过对比标准提示与引导提示下生成轨迹的token级预测分布，将KL散度作为密集过程级奖励信号，并引入分阶段长度奖励机制，在控制推理长度的同时避免短答案坍缩和边界寻求行为。在六个多视图空间推理基准上，LenGuard-GPC相比vanilla GRPO平均准确率提升2.0个百分点，相比基座模型提升5.9个百分点，同时缩短了平均响应长度。

## 方法：核心思路与整体框架

论文在GRPO框架基础上，对每条采样轨迹同时计算标准提示和引导提示下的token级预测分布，以两者的KL散度作为密集一致性奖励。引导提示分布通过teacher forcing在固定轨迹上并行计算，避免二次生成。同时引入分阶段长度奖励，根据长度边界和奖励水平动态调节长度激励，与一致性奖励共同构成最终奖励函数。

![图 1：Figure 1: Overview ofLenGuard-GPCfor multi-view spatial reasoning. Within the staged interval [l , l ], LenGuard-GPC adaptively balances the negative KL-based consistency reward and the length bonus. When the mean per-token KL is high, the consistency reward dominates and encourages more concise reasoning. When the mean per-token KL is low, the length bonus becomes relatively stronger, preventing the model from collapsing into overly short and content-poor chains of thought.](/images/papers/2607.17243/428faa2d9215b9e54e6deef28047a0031030884be8972e2a1a4c842a698ab400.jpg)

*图 1 · 原图说明：Figure 1: Overview ofLenGuard-GPCfor multi-view spatial reasoning. Within the staged interval [l , l ], LenGuard-GPC adaptively balances the negative KL-based consistency reward and the length bonus. When the mean per-token KL is high, the consistency reward dominates and encourages more concise reasoning. When the mean per-token KL is low, the length bonus becomes relatively stronger, preventing the model from collapsing into overly short and content-poor chains of thought.*

**图示解释：** 论文在GRPO框架基础上，对每条采样轨迹同时计算标准提示和引导提示下的token级预测分布，以两者的KL散度作为密集一致性奖励。

## 创新点

1. 提出引导提示一致性奖励：对每条采样轨迹，同时计算标准提示和引导提示下的token级预测分布，将两者之间的KL散度作为GRPO兼容的密集过程级奖励信号，无需额外监督损失即可提供比结果奖励更细粒度的反馈。
2. 设计分阶段长度守卫机制：通过长度边界(l1,l2,l3)和奖励水平(r1,r2)控制长度奖励，在[l1,l2]区间内奖励从r1递增至r2，之后保持恒定至l3，动态平衡KL引导的简洁性与长度充分性，同时避免短答案坍缩和边界寻求行为。
3. 实现高效训练：引导提示分布通过teacher forcing在固定轨迹上并行计算，无需两次完整自回归生成，整体训练时间仅增加约1.6倍，且更短的轨迹进一步抵消了部分额外开销。
4. 验证跨域泛化能力：在训练分布外的基准（3DSR、BLINK、CV-Bench）上仍保持对vanilla GRPO的一致提升，表明该方法不会过拟合训练分布或牺牲通用推理能力。

## 实验：数据、基线与结果

### 数据集与设置

任务为多视图空间推理，训练数据来自多视图空间推理领域，MindCube仅用于评估不使用其训练集。具体数据规模、预处理方式和训练/验证/测试划分原文未披露。

### Benchmark 与结果

在六个多视图空间推理基准上，LenGuard-GPC平均准确率达到57.3%，相比vanilla GRPO的55.3%提升2.0个百分点，相比基座Qwen3-VL-8B-Instruct的51.4%提升5.9个百分点。在MMSI-Bench上从32.2%提升至36.1%（+3.9），MindCube从44.7%提升至48.4%，ViewSpatial从44.4%提升至46.9%。细粒度分析显示跨视图位置推理提升最大：Cam.-Obj.（+13.9）、Cam.-Reg.（+12.0）、Obj.-Reg.（+7.1）、Obj.-Obj.（+5.3）。在域外基准上也有小幅提升：3DSR从59.4%到60.1%，BLINK从65.7%到66.8%，CV-Bench从85.2%到85.5%。消融实验表明去掉分阶段长度奖励后MMSI-Bench准确率从36.1%降至33.5%。



### 消融实验

对比方法包括：RandomChoice、闭源模型Gemini-2.5-Pro和GPT-5、开源通用模型InternVL3-2B/8B、Qwen2.5-VL-3B/7B-Instruct、Qwen3-VL-2B/8B-Instruct、空间智能模型SpatialLadder-3B、Spatial-MLLM-4B、SpaceR-7B、ViLaSR-7B、Cambrian-S-3B/7B，以及vanilla GRPO。消融设置包括去掉分阶段长度奖励的变体。

## 总结

论文针对多视图空间推理中GRPO强化学习存在的两个问题——稀疏结果奖励无法定位局部跨视图推理错误、以及朴素token-sum KL奖励会偏向过短回答——提出了LenGuard-GPC框架。

## References

- LenGuard-GPC: Length Guarding with Guided-Prompt Consistency for Spatial Reasoning Reinforcement Learning：[arXiv 2607.17243](https://arxiv.org/abs/2607.17243)

- [代码：GitHub](https://github.com/taoxj2001/LenGuard-GPC)
- [PDF源文件](/papers/2607.17243.pdf)
