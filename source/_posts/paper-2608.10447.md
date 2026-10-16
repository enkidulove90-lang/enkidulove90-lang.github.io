---
title: "基于模型融合的高效LLM推荐系统推理"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.10447
arxiv_id: "2608.10447"
description: "本文提出REAM（Reasoning-Head Aware Merging），这是首个面向推荐系统推理压缩的模型融合框架。"
---

> 论文：[arXiv 2608.10447](https://arxiv.org/abs/2608.10447) · 代码：[GitHub](https://github.com/linhledieu/REAM) · PDF：[本地阅读](/papers/2608.10447.pdf)

本文提出REAM（Reasoning-Head Aware Merging），这是首个面向推荐系统推理压缩的模型融合框架。针对慢思考推荐模型推理轨迹冗长、推理成本高的问题，REAM将模型融合建模为选择性迁移：以慢思考模型为锚点，将快思考模型的简洁生成行为按注意力头粒度注入。每个注意力头根据其对关键推理证据的贡献度和对参数变化的敏感度分配独立的融合系数，实现细粒度、可控的推理压缩。实验表明，REAM在三个基准数据集上将推理长度最多缩短24.3%，同时在推荐准确率上优于现有模型融合基线。

## 研究问题

本文提出REAM（Reasoning-Head Aware Merging），这是首个面向推荐系统推理压缩的模型融合框架。针对慢思考推荐模型推理轨迹冗长、推理成本高的问题，REAM将模型融合建模为选择性迁移：以慢思考模型为锚点，将快思考模型的简洁生成行为按注意力头粒度注入。每个注意力头根据其对关键推理证据的贡献度和对参数变化的敏感度分配独立的融合系数，实现细粒度、可控的推理压缩。实验表明，REAM在三个基准数据集上将推理长度最多缩短24.3%，同时在推荐准确率上优于现有模型融合基线。

## 方法：核心思路与整体框架

REAM将模型融合形式化为任务向量组合：以慢思考模型θ_S（RecZero）为锚点，将快思考模型θ_F（TALLRec，经全参数微调适配为直接评分预测）的任务向量Δ_F按注意力头分区，每个头分配系数α_b。系数由该头的推理重要性（基于决策时注意力质量）和参数敏感度联合决定，通过固定注入预算下的注水（water-filling）求解。方法无需额外训练，仅需少量校准样本估计注意力统计量。

![图 1：Figure 2: Overview of the proposed framework.](/images/papers/2608.10447/7832e3b02bc301f6487e52a39d48b82c29aa0bd89f882dd3222717def8d24fb5.jpg)

*图 1 · 原图说明：Figure 2: Overview of the proposed framework.*

**图示解释：** REAM将模型融合形式化为任务向量组合：以慢思考模型θ_S（RecZero）为锚点，将快思考模型θ_F（TALLRec，经全参数微调适配为直接评分预测）的任务向量Δ_F按注意力头分区，每个头分配系数α_b。

## 创新点

1. 首次将模型融合用于推荐系统推理压缩：不同于已有工作将模型融合用于多域/跨域/联邦推荐的知识整合，本文首次探索通过融合快思考与慢思考推荐模型来平衡推荐准确率与推理简洁性。
2. 注意力头粒度的选择性融合：现有通用融合方法在模型组件上使用统一融合系数，REAM则在单个注意力头级别进行细粒度融合，捕捉推荐推理中的异质模式，实现选择性注入快思考行为。
3. 基于推理重要性与参数敏感度的系数分配：每个注意力头根据其对关键推理证据的贡献度（推理重要性）和对参数变化的敏感度联合确定融合系数，从而在缩短推理的同时保护对预测至关重要的推理行为。
4. 揭示通用模型融合在推荐推理压缩中的局限：系统实验表明通用融合方法虽能缩短推理长度，但无法可靠保持慢思考模型的预测行为，甚至改变其评分行为（如RMSE改善但MAE恶化）。

## 实验：数据、基线与结果

### 数据集与设置

任务为评分预测（1-5分），使用Book、Music、Yelp三个基准数据集。慢思考模型为RecZero（生成三段结构化推理后输出评分），快思考模型为TALLRec（经全参数微调从二分类适配为直接评分预测）。数据预处理、训练/验证/测试划分细节原文未完整披露。

### Benchmark 与结果

在Book数据集上，Task Arithmetic和DARE+TA将生成长度压缩至253.13和252.81 tokens，但MAE分别恶化至0.6742和0.6835（θ_S为0.6650）。AIM+TA和ACM+TA同样恶化MAE至0.6805和0.6932。在Music数据集上，多数通用融合方法改善RMSE（如AIM+TA达0.8227 vs. θ_S的0.8510）但恶化MAE（0.5678 vs. 0.5433），表明评分行为分布发生改变。REAM在三个数据集上将推理长度最多缩短24.3%，同时在推荐准确率上优于所有竞争性融合基线。



### 消融实验

对比方法包括：Average Merging、Task Arithmetic、DARE、DARE+TA、DARE+TIES、AIM+TA、ACM+TA、RAIN-Merging，以及慢思考模型θ_S本身。消融设置涉及不同融合系数分配策略。

## 总结

本文提出REAM（Reasoning-Head Aware Merging），这是首个面向推荐系统推理压缩的模型融合框架。

## References

- Towards Efficient Reasoning in LLM-Based Recommender Systems via Model Merging：[arXiv 2608.10447](https://arxiv.org/abs/2608.10447)

- [代码：GitHub](https://github.com/linhledieu/REAM)
- [PDF源文件](/papers/2608.10447.pdf)
