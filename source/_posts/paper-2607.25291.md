---
title: "CoSA：代理-内核协同设计的稀疏注意力加速长上下文推理"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.25291
arxiv_id: "2607.25291"
description: "论文提出CoSA，一种无需训练的两阶段块稀疏注意力方法，通过代理-内核协同设计解决长上下文推理中稀疏注意力精度与效率的权衡问题。"
---

> 论文：[arXiv 2607.25291](https://arxiv.org/abs/2607.25291) · 代码：[GitHub](https://github.com/Tencent/AngelSlim) · 代码：[GitHub](https://github.com/mit-hanlab/Block-Sparse-Attention) · PDF：[本地阅读](/papers/2607.25291.pdf)

论文提出CoSA，一种无需训练的两阶段块稀疏注意力方法，通过代理-内核协同设计解决长上下文推理中稀疏注意力精度与效率的权衡问题。CoSA将内核感知代理（KAP）与有序跳跃内核（OSK）通过单一的计算顺序掩码桥接：KAP在中等预算下选择重要块并规定其访问顺序，OSK据此通过页表重映射物理跳过冗余块，并利用在线Softmax统计进行内核内二次稀疏。该方法在主流LLM骨干和长上下文基准上以更低预算实现更高精度，在128K上下文下获得4.93倍注意力加速和2.53倍端到端预填充加速，性能退化可忽略。

## 研究问题

论文提出CoSA，一种无需训练的两阶段块稀疏注意力方法，通过代理-内核协同设计解决长上下文推理中稀疏注意力精度与效率的权衡问题。CoSA将内核感知代理（KAP）与有序跳跃内核（OSK）通过单一的计算顺序掩码桥接：KAP在中等预算下选择重要块并规定其访问顺序，OSK据此通过页表重映射物理跳过冗余块，并利用在线Softmax统计进行内核内二次稀疏。该方法在主流LLM骨干和长上下文基准上以更低预算实现更高精度，在128K上下文下获得4.93倍注意力加速和2.53倍端到端预填充加速，性能退化可忽略。

## 方法：核心思路与整体框架

CoSA采用两阶段无训练块稀疏注意力框架。第一阶段，KAP通过步长下采样查询和键，经Softmax、MaxPool和MaxNorm计算块重要性分数和HRM标志，通过标志分组排序生成计算顺序掩码，在中等预算下选择块并规定访问顺序。第二阶段，OSK消费该掩码，通过KV页重映射物理跳过未选中页，并利用在线Softmax的精确logits进行内核内跳跃，进一步稀疏化。两阶段通过计算顺序掩码桥接，代理塑造内核执行顺序，内核消费代理掩码驱动稀疏。

![图 1：Figure 4: Overview of CoSA. $\mathbf { M } _ { \mathrm { K A P } } .$ the KAP mask serves as a bridge between the co-designed proxy and kernel. Left: KAP estimates a per-block score together with the HRM flag. They are merged into the computation-order mask ${ \bf M } _ { \mathrm { K A P } }$ , which places HRM blocks first. Right: OSK consumes ${ \bf M } _ { \mathrm { K A P } }$ through KV page remapping, yielding three per-block patterns: ➀ mask-skipped, ➁ in-kernel skipped, and ➂ computed.](/images/papers/2607.25291/4e85b9243983bd21922df3e58da8f8c3082e6e64c009de6b5c222ab4bfdf2188.jpg)

*图 1 · 原图说明：Figure 4: Overview of CoSA. $\mathbf { M } _ { \mathrm { K A P } } .$ the KAP mask serves as a bridge between the co-designed proxy and kernel. Left: KAP estimates a per-block score together with the HRM flag. They are merged into the computation-order mask ${ \bf M } _ { \mathrm { K A P } }$ , which places HRM blocks first. Right: OSK consumes ${ \bf M } _ { \mathrm { K A P } }$ through KV page remapping, yielding three per-block patterns: ➀ mask-skipped, ➁ in-kernel skipped, and ➂ computed.*

**图示解释：** CoSA采用两阶段无训练块稀疏注意力框架。

## 创新点

1. 提出代理-内核协同设计原则，通过单一计算顺序掩码替代传统二值掩码，使代理不仅决定哪些块被保留，还规定内核中块的访问顺序，实现代理与内核的相互塑造。
2. 设计内核感知代理（KAP），利用顺序不变性输出计算顺序掩码，优先访问包含行最大值的块（HRM块），通过标志分组排序缓解内核内跳跃的保守性问题，在中等预算下实现第一阶段稀疏选择。
3. 设计有序跳跃内核（OSK），支持任意顺序页访问、物理页跳转和基于精确在线Softmax统计的内核内跳跃，实现第二阶段稀疏计算，将稀疏预算进一步压低，同时保持输出正确性。
4. 揭示现有块稀疏注意力的两个关键性质（预算依赖的代理保真度、在线Softmax的顺序不变性）和内核内跳跃的两个局限（密集QK乘法作为代理、跳跃保守性），为协同设计提供理论依据。

## 实验：数据、基线与结果

### 数据集与设置

实验任务为长上下文推理，包括RULER合成任务（4K至128K token长度）和LongBench-v2真实世界深度理解与推理任务（含w/o CoT和w/ CoT两种模式）。使用Llama-3.1-8B-Instruct和Qwen3-8B两个骨干模型。Qwen3-8B使用推荐采样参数，必要时通过YaRN扩展上下文至128K。仅对预填充阶段进行稀疏化，解码阶段保持密集。训练/验证/测试划分原文未披露。

### Benchmark 与结果

在RULER基准上，CoSA在Qwen3-8B和Llama-3.1-8B上均以最低预算（22%）取得稀疏方法中最佳平均准确率，分别为88.65%和88.41%，接近密集注意力（89.20%和88.97%）。在LongBench-v2上，CoSA在两种骨干和两种模式下均取得稀疏方法最佳平均，Qwen3-8B上为36.51%（预算15%），Llama-3.1-8B上为30.96%（预算17%）。消融实验显示，完整CoSA在Llama-3.1-8B上相比Base提升3.03%准确率同时降低18%预算。效率方面，128K上下文下注意力加速4.93倍，端到端TTFT加速2.53倍，4K长度下无性能退化。

![图 2：Figure C: Full remapping sweeps across Stage-1 budgets and skip scales. Each column fixes ${ { B } _ { \mathrm { S t a g e - 1 } } }$ . The Top row reports PPL and the Bottom row reports the in-kernel skip ratio as $\Delta$ varies. Remapping achieves a higher skip ratio at a fixed $\Delta$ and a lower PPL at a matched skip ratio. Red annotations highlight the matched-ratio PPL gain.](/images/papers/2607.25291/793761a8283ef1a3937fb56e453152e738698fb3d8e4f7e8fb79af4029f6329c.jpg)

*图 2 · 原图说明：Figure C: Full remapping sweeps across Stage-1 budgets and skip scales. Each column fixes ${ { B } _ { \mathrm { S t a g e - 1 } } }$ . The Top row reports PPL and the Bottom row reports the in-kernel skip ratio as $\Delta$ varies. Remapping achieves a higher skip ratio at a fixed $\Delta$ and a lower PPL at a matched skip ratio. Red annotations highlight the matched-ratio PPL gain.*

**图示解释：** 在RULER基准上，CoSA在Qwen3-8B和Llama-3.1-8B上均以最低预算（22%）取得稀疏方法中最佳平均准确率，分别为88.65%和88.41%，接近密集注意力（89.20%和88.97%）。

### 消融实验

对比方法包括MInference、FlexPrefill、XAttention三种强块稀疏注意力基线，以及FlashAttention-2作为全注意力基线。消融实验设置包括：Base（XAttention风格代理+二值掩码）、+KAP、+IKS（内核内跳跃）、+RMP（KV页重映射，即完整CoSA）。

## 总结

论文提出CoSA，一种无需训练的两阶段块稀疏注意力方法，通过代理-内核协同设计解决长上下文推理中稀疏注意力精度与效率的权衡问题。

## References

- CoSA: Accelerating Long-Context Inference via Proxy-Kernel Co-Designed Sparse Attention：[arXiv 2607.25291](https://arxiv.org/abs/2607.25291)

- [代码：GitHub](https://github.com/Tencent/AngelSlim)
- [代码：GitHub](https://github.com/mit-hanlab/Block-Sparse-Attention)
- [PDF源文件](/papers/2607.25291.pdf)
