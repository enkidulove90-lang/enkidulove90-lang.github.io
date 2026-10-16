---
title: "基于偏好优化的LLM序列推荐Token选择方法"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.09605
arxiv_id: "2608.09605"
description: "论文提出TSPORec，一种面向LLM序列推荐的三阶段Token选择框架。"
---

> 论文：[arXiv 2608.09605](https://arxiv.org/abs/2608.09605) · 代码：[GitHub](https://github.com/WNQzhu/TSPORec.git) · PDF：[本地阅读](/papers/2608.09605.pdf)

论文提出TSPORec，一种面向LLM序列推荐的三阶段Token选择框架。该方法首先预训练基于LLM的推荐模型，然后冻结LLM主干并附加策略头，通过新设计的代理奖励函数学习Token选择策略，最后利用选出的信息性Token重训练模型。TSPORec能够从物品全文描述中自动识别关键Token，而非仅使用前几个Token，在提升推荐性能的同时显著降低推理开销。实验表明，在Amazon Books和Pixel数据集上，TSPORec相比六个基线方法最高提升29.29%的Recall和31.25%的NDCG，推理开销降低最高63.4%。

## 研究问题

论文提出TSPORec，一种面向LLM序列推荐的三阶段Token选择框架。该方法首先预训练基于LLM的推荐模型，然后冻结LLM主干并附加策略头，通过新设计的代理奖励函数学习Token选择策略，最后利用选出的信息性Token重训练模型。TSPORec能够从物品全文描述中自动识别关键Token，而非仅使用前几个Token，在提升推荐性能的同时显著降低推理开销。实验表明，在Amazon Books和Pixel数据集上，TSPORec相比六个基线方法最高提升29.29%的Recall和31.25%的NDCG，推理开销降低最高63.4%。

## 方法：核心思路与整体框架

TSPORec采用三阶段训练流水线。第一阶段，基于InfoNCE损失预训练用户LLM和物品LLM，物品嵌入取[ITEM]特殊Token的最后一层隐藏状态。第二阶段，冻结LLM主干，附加可学习策略头，通过query-key注意力机制计算每个Token的重要性分数，并基于两次独立采样的Token子序列构建代理奖励信号，使用策略梯度优化选择策略。第三阶段，利用学习到的策略选择高概率Token chunk，构建精炼数据集后重训练模型。

![图 1：Figure 1: Overview of TSPORec’s Three-Stage Training Pipeline: (1) LLM Pretraining, (2) Token Selection Policy Learning, (3) Token Selection and Retraining.](/images/papers/2608.09605/3c3c933526d8dd15434702eed8fc316d19daf924b0aa22ddf5fac45b602d5e74.jpg)

*图 1 · 原图说明：Figure 1: Overview of TSPORec’s Three-Stage Training Pipeline: (1) LLM Pretraining, (2) Token Selection Policy Learning, (3) Token Selection and Retraining.*

**图示解释：** TSPORec采用三阶段训练流水线。

## 创新点

1. 提出三阶段Token选择流水线：预训练LLM推荐模型、基于代理奖励学习Token选择策略、利用选定Token重训练模型，实现了从全文描述中自动识别信息性Token的目标，且在不同LLM和数据集上展现强泛化能力。
2. 设计了一种新颖的代理奖励函数，通过对比两次独立采样的Token子序列所构建的用户嵌入与完整物品嵌入之间的交叉熵损失，引导策略学习区分信息性Token与非信息性Token，解决了Token子集评估的指数级复杂度问题。
3. 采用双向评分机制计算Token重要性：同时利用标准注意力机制编码语义信息和预训练物品嵌入提供协同过滤信号，使Token选择能够联合捕获丰富语义与序列协同模式，优于单向的top-k logit选择策略。
4. 引入chunk级别的Token选择粒度控制，通过可调节的chunk大小在Token级和粗粒度选择之间灵活权衡，实验发现更细粒度的选择单元能带来更有效的Token选择效果。

## 实验：数据、基线与结果

### 数据集与设置

任务为序列推荐（Sequential Recommendation），预测用户下一个可能交互的物品。使用Amazon Books（694,898用户，686,624物品，10,053,086交互，密度2.1×10^-5）和Pixel（200,000用户，96,282物品，3,965,656交互，密度2.1×10^-4）两个公开数据集。采用leave-one-out评估协议：最近一次交互用于测试，倒数第二次用于验证，其余用于训练。物品描述截断至64、128、256个Token。Amazon Books使用标题和描述字段，Pixel使用标题、标签和描述文本特征。TSPORec保留前16个Token作为前缀。

### Benchmark 与结果

在Amazon Books数据集上，TSPORec相比SASRec最高提升29.29% Recall@K和31.25% NDCG@K，平均提升29.43%；在Pixel数据集上最高提升19.63% Recall@K和18.24% NDCG@K，平均提升16.79%。与HLLM(first-k)相比，TSPORec在Amazon Books上R@5从4.16提升至4.37，N@5从2.80提升至2.94。随机Token选择使HLLM性能提升从24.40%降至2.14%，top-k logit选择（+5.36%）甚至不如first-k基线（+24.40%）。效率方面，TSPORec仅用64个Token即可达到HLLM使用256个Token的性能，推理开销降低63.4%（物品嵌入离线预计算场景）和61.3%（在线服务场景）。泛化性方面，使用TinyLlama-1.1B时TSPORec平均提升4.12%，用于LLMinit初始化时提升3.76%。

![图 2：Figure 6: Comparison of token distributions selected by first-k and TSPORec.](/images/papers/2608.09605/42b9f36735a4a51ab181f7289bcf226e58d66c88e6c379b79c7379a6a2346b85.jpg)

*图 2 · 原图说明：Figure 6: Comparison of token distributions selected by first-k and TSPORec.*

**图示解释：** 在Amazon Books数据集上，TSPORec相比SASRec最高提升29.29% Recall@K和31.25% NDCG@K，平均提升29.43%；在Pixel数据集上最高提升19.63% Recall@K和18.24% NDCG@K，平均提升16.79%。

### 消融实验

对比四类基线方法：(1) 传统ID-based序列推荐模型SASRec和HSTU；(2) 语义初始化方法LLMinit；(3) 层次化LLM框架HLLM。此外，为研究Token选择影响，将基线适配不同Token选择策略（随机选择、top-k logit、first-k），共形成六个基线变体。消融实验包括：不同Token序列长度（64/128/256）、不同训练与选择chunk大小组合（T16S1/T16S8/T16S16/T16S32）、不同LLM主干（Qwen3-Embedding-0.6B和TinyLlama-1.1B）、不同下游SR模型（LLMinit）。

## 总结

论文提出TSPORec，一种面向LLM序列推荐的三阶段Token选择框架。

## References

- TSPORec: Token Selection via Preference Optimization for LLM-Based Sequential Recommendation：[arXiv 2608.09605](https://arxiv.org/abs/2608.09605)

- [代码：GitHub](https://github.com/WNQzhu/TSPORec.git)
- [PDF源文件](/papers/2608.09605.pdf)
