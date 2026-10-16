---
title: "FOCUS：基于耦合松弛与双粒度缩放的FP4优化"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.01847
arxiv_id: "2608.01847"
description: "论文提出FOCUS，一种面向MXFP4和NVFP4格式的端到端训练后量化（PTQ）框架。"
---

> 论文：[arXiv 2608.01847](https://arxiv.org/abs/2608.01847) · 代码：[GitHub](https://github.com/tencent/AngelSlim) · PDF：[本地阅读](/papers/2608.01847.pdf)

论文提出FOCUS，一种面向MXFP4和NVFP4格式的端到端训练后量化（PTQ）框架。核心洞察是量化尺度（quantization scale）在推理时不被存储，因此无需遵循硬件强制的低精度格式和块粒度约束。FOCUS沿精度和粒度两个维度释放量化尺度的优化空间：耦合松弛缩放（CRS）引入可学习的全精度系数，将量化尺度优化从离散低精度空间提升到连续空间；双粒度缩放（DGS）在子块级别分配量化尺度，捕捉块内局部权重变化。实验表明FOCUS在两种FP4格式下均达到SOTA精度，且无额外推理开销。

## 研究问题

论文提出FOCUS，一种面向MXFP4和NVFP4格式的端到端训练后量化（PTQ）框架。核心洞察是量化尺度（quantization scale）在推理时不被存储，因此无需遵循硬件强制的低精度格式和块粒度约束。FOCUS沿精度和粒度两个维度释放量化尺度的优化空间：耦合松弛缩放（CRS）引入可学习的全精度系数，将量化尺度优化从离散低精度空间提升到连续空间；双粒度缩放（DGS）在子块级别分配量化尺度，捕捉块内局部权重变化。实验表明FOCUS在两种FP4格式下均达到SOTA精度，且无额外推理开销。

## 方法：核心思路与整体框架

FOCUS冻结原始模型权重，仅优化权重量化尺度。基线方法将尺度维护为FP16副本，前向传播时通过STE量化为硬件格式，使用KL-Top蒸馏损失端到端优化。CRS在此基础上引入可学习全精度系数c_i，定义量化尺度S_i^q = S_i^dq · c_i，其中S_i^dq为硬件合规的反量化尺度，c_i初始化为1。DGS进一步将每个块划分为K个子块，每个子块有独立系数c_i^k，量化尺度为S_i^dq · c_i^k。训练后所有系数被丢弃，仅存储FP4权重和反量化尺度。

![图 1：Figure 3: Overview of FOCUS. (a) End-to-end Scale Learning Baseline: learns FP8 scales via STE while weights are frozen during quantization and dequantization. (b) Coupled-Relaxation Scaling (CRS): introduces learnable relaxation coeficients for additional flexibility beyond FP8 precision. (c) Dual-Granularity Scaling (DGS): partitions each block into sub-blocks with independent coeficients for fine-grained scale adjustment. (d) Output Model: only FP4 weights and dequantization scales are stored, while quantization scales are discarded.](/images/papers/2608.01847/966cd100a2b1895042d0fed27684915935663075fb7de8a7e338c07b767500ac.jpg)

*图 1 · 原图说明：Figure 3: Overview of FOCUS. (a) End-to-end Scale Learning Baseline: learns FP8 scales via STE while weights are frozen during quantization and dequantization. (b) Coupled-Relaxation Scaling (CRS): introduces learnable relaxation coeficients for additional flexibility beyond FP8 precision. (c) Dual-Granularity Scaling (DGS): partitions each block into sub-blocks with independent coeficients for fine-grained scale adjustment. (d) Output Model: only FP4 weights and dequantization scales are stored, while quantization scales are discarded.*

**图示解释：** FOCUS在几乎所有设置下取得最低困惑度和最高平均准确率。

## 创新点

1. 关键洞察：量化尺度在推理时不被存储，因此不受硬件精度格式和块粒度约束，而现有方法将量化尺度与反量化尺度紧耦合，浪费了这一优化自由度。
2. 耦合松弛缩放（CRS）：引入可学习的全精度系数c_i，以乘法形式松弛量化尺度与反量化尺度的紧耦合，将优化从离散低精度空间提升到连续全精度空间，同时保持训练稳定性。
3. 双粒度缩放（DGS）：将每个硬件块（MXFP4为32元素，NVFP4为16元素）划分为子块（大小为8），每个子块分配独立的可学习系数，使量化尺度以比反量化尺度更细的粒度适应块内权重变化。
4. 无推理开销且框架兼容：FOCUS仅学习尺度参数，不修改权重，不依赖Hadamard变换等在线计算，部署模型保持标准MXFP4/NVFP4格式，与主流推理框架无缝兼容。

## 实验：数据、基线与结果

### 数据集与设置

在五个LLM上进行W4A4量化：LLaMA-3.1-8B-Instruct、LLaMA-3.2-1B-Instruct、LLaMA-3.2-3B-Instruct、Qwen3-4B、Qwen3-8B。校准集使用WikiText2训练集的1,248个样本，序列长度2,048。评估包括WikiText2和C4上的困惑度（序列长度2,048），五个零样本常识推理基准（ARC-C、ARC-E、HellaSwag、PIQA、Winogrande），以及GSM8K和MMLU上的CoT推理评估。

### Benchmark 与结果

FOCUS在几乎所有设置下取得最低困惑度和最高平均准确率。Qwen3-8B上，MXFP4 WikiText2困惑度9.76（FP16为9.73），NVFP4为9.47；NVFP4零样本平均准确率71.37%，恢复FP16的99.8%，优于RaZeR的70.54%。Qwen3-4B上，NVFP4平均准确率67.05%，恢复FP16的98.2%；MXFP4为65.65%，恢复96.2%。MXFP4下FOCUS在Qwen模型上比MR-GPTQ困惑度降低1.5-2.5点。CoT推理方面，LLaMA-3.1-8B上GSM8K达73.31%、MMLU达65.53%，分别超MR-GPTQ 0.9和2.1点；LLaMA-3.2-3B上超MR-GPTQ约4点。消融显示CRS和DGS均带来持续提升。



### 消融实验

MXFP4和NVFP4格式下均对比RTN、GPTQ、MR-GPTQ；NVFP4额外对比4over6和RaZeR（当前SOTA）。消融实验在Qwen3-4B上逐步添加CRS和DGS，与朴素尺度学习基线对比。

## 总结

论文提出FOCUS，一种面向MXFP4和NVFP4格式的端到端训练后量化（PTQ）框架。

## References

- FOCUS: FP4 Optimization via Coupled-Relaxation and Dual-Granularity Scaling：[arXiv 2608.01847](https://arxiv.org/abs/2608.01847)

- [代码：GitHub](https://github.com/tencent/AngelSlim)
- [PDF源文件](/papers/2608.01847.pdf)
