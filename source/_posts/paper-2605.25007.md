---
title: "元模态智能体：缺失模态候选重排序"
date: 2026-05-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2605.25007
arxiv_id: "2605.25007"
description: "本文提出Meta-Modal Agent (MMA)，将冷启动推荐中的模态缺失问题从静态表示学习重新定义为顺序证据路由问题。"
---

> 论文：[arXiv 2605.25007](https://arxiv.org/abs/2605.25007) · PDF：[本地阅读](/papers/2605.25007.pdf)

本文提出Meta-Modal Agent (MMA)，将冷启动推荐中的模态缺失问题从静态表示学习重新定义为顺序证据路由问题。MMA是一个基于LLM的候选池重排序器，通过强化学习在掩码模态片段上训练，学习在工具调用失败时动态切换证据源。实验表明，MMA-Auto在OOMA NDCG@10上提升4.0%，在全目录重排序NDCG@10上提升12.7%，优于强静态基线。

## 研究问题

本文提出Meta-Modal Agent (MMA)，将冷启动推荐中的模态缺失问题从静态表示学习重新定义为顺序证据路由问题。MMA是一个基于LLM的候选池重排序器，通过强化学习在掩码模态片段上训练，学习在工具调用失败时动态切换证据源。实验表明，MMA-Auto在OOMA NDCG@10上提升4.0%，在全目录重排序NDCG@10上提升12.7%，优于强静态基线。

## 方法：核心思路与整体框架

MMA采用基于LLM的智能体框架，将重排序过程建模为POMDP。智能体通过调用文本、图像、图结构等工具收集证据，将Null返回值作为观测更新历史。使用PPO算法在7种缺失模式片段上训练，奖励函数结合最终排序NDCG和工具调用成本。训练后，智能体在推理时仅通过上下文自适应路由。

![图 1：Figure 1: Overview of MMA. The agent receives a shared candidate pool, routes among available evidence tools, treats Null returns as observations, and outputs candidate scores that are fused with first-stage retrieval scores for reranking.](/images/papers/2605.25007/769bea42d48c848a7e8c729c6803e77bccad124df56307ec6eaf6a8e6ce27f42.jpg)

*图 1 · 原图说明：Figure 1: Overview of MMA. The agent receives a shared candidate pool, routes among available evidence tools, treats Null returns as observations, and outputs candidate scores that are fused with first-stage retrieval scores for reranking.*

**图示解释：** MMA采用基于LLM的智能体框架，将重排序过程建模为POMDP。

## 创新点

1. 创新点1：将冷启动缺失模态问题形式化为部分可观测马尔可夫决策过程(POMDP)，将失败的工具调用视为观测信号而非静默特征丢弃，使模型能从Null返回值中学习路由策略。
2. 创新点2：提出平衡缺失任务训练方法，通过均匀采样不同缺失模式（如单模态、双模态缺失）的片段，确保模型在罕见但关键的冷启动场景下也能获得充分训练。
3. 创新点3：设计无oracle的候选评分与融合协议，MMA仅对第一阶段检索器提供的固定候选池进行评分，并通过验证集选择的融合权重与检索分数结合，严格隔离了重排序与检索的贡献。

## 实验：数据、基线与结果

### 数据集与设置

数据集：Amazon-Baby、Amazon-Sports、Yelp (2022 release)

### Benchmark 与结果

在OOMA（仅单模态可用）设置下，MMA-Auto在Baby、Sports、Yelp上NDCG@10分别提升3.5%、4.0%、4.8%，平均提升4.0%（从0.1645到0.1711）。全目录重排序中，MMA-Auto在固定检索池上平均NDCG@10从0.0178提升至0.0201（相对提升12.7%），HR@10从0.0385提升至0.0427。与确定性路由基线RuleRouter-Fuse相比，MMA-Auto平均OOMA NDCG@10从0.1578提升至0.1711。



### 消融实验

论文未报告独立的消融实验。

## 总结

本文提出Meta-Modal Agent (MMA)，将冷启动推荐中的模态缺失问题从静态表示学习重新定义为顺序证据路由问题。

## References

- Meta-Modal Agent: Sequential Evidence Routing for Missing-Modality Candidate Reranking：[arXiv 2605.25007](https://arxiv.org/abs/2605.25007)

- [PDF源文件](/papers/2605.25007.pdf)
