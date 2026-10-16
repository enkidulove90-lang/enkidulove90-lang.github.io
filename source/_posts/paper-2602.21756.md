---
title: "离线推理实现高效推荐"
date: 2026-02-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2602.21756
arxiv_id: "2602.21756"
description: "提出Persona4Rec框架，将LLM的推理过程从在线阶段转移到离线阶段，通过预计算物品的多视角可解释人物画像（persona），实现轻量级在线推理。"
---

> 论文：[arXiv 2602.21756](https://arxiv.org/abs/2602.21756) · 代码：[GitHub](https://github.com/legenduck/PERSONA4REC) · PDF：[本地阅读](/papers/2602.21756.pdf)

提出Persona4Rec框架，将LLM的推理过程从在线阶段转移到离线阶段，通过预计算物品的多视角可解释人物画像（persona），实现轻量级在线推理。该方法将推荐问题转化为用户-人物画像对齐任务，在保持推荐准确性的同时，将推理延迟降低数个数量级，并自然提供可解释的推荐理由。

## 研究问题

提出Persona4Rec框架，将LLM的推理过程从在线阶段转移到离线阶段，通过预计算物品的多视角可解释人物画像（persona），实现轻量级在线推理。该方法将推荐问题转化为用户-人物画像对齐任务，在保持推荐准确性的同时，将推理延迟降低数个数量级，并自然提供可解释的推荐理由。

## 方法：核心思路与整体框架

采用两阶段框架：离线阶段，使用LLM从物品元数据生成摘要，从用户评论提取方面（aspect），再综合生成多个结构化人物画像；通过LLM-as-a-judge选择用户-人物画像对齐对，训练轻量级编码器（基于BGE-M3）。在线阶段，编码用户历史交互为画像，与预计算的人物画像进行相似度计算，选择最佳匹配人物画像作为重排序分数。

![图 1：Figure 2: Overview of our Persona4Rec framework. The ofline process (Left) constructs item personas and trains a userpersona alignment encoder. The online process (Right) reranks candidates via eficient similarity scoring](/images/papers/2602.21756/335ea814ab1566a9ee7213c6b4352ff4c6c580e7c90f45a2e5be95ebeb77ff63.jpg)

*图 1 · 原图说明：Figure 2: Overview of our Persona4Rec framework. The ofline process (Left) constructs item personas and trains a userpersona alignment encoder. The online process (Right) reranks candidates via eficient similarity scoring*

**图示解释：** 采用两阶段框架：离线阶段，使用LLM从物品元数据生成摘要，从用户评论提取方面（aspect），再综合生成多个结构化人物画像；通过LLM-as-a-judge选择用户-人物画像对齐对，训练轻量级编码器（基于BGE-M3）。

## 创新点

1. 创新点1：提出离线人物画像构建机制，利用LLM对物品元数据和用户评论进行推理，为每个物品生成多个可解释的人物画像，每个画像代表一种不同的用户动机或偏好模式。
2. 创新点2：设计用户-人物画像对齐框架，通过LLM-as-a-judge范式为每个交互对选择最相关的人物画像，生成监督信号训练轻量级编码器，将用户画像和物品人物画像映射到共享语义空间。
3. 创新点3：构建人物画像索引的物品表示，在线推理时仅需计算用户画像与预计算人物画像的相似度，避免昂贵的实时LLM调用，实现亚毫秒级推理延迟。

## 实验：数据、基线与结果

### 数据集与设置

数据集：Amazon-Books (Amazon Reviews 2023)、Yelp (Philadelphia region restaurant and food)；划分：leave-one-out

### Benchmark 与结果

Persona4Rec在Amazon-Books和Yelp数据集上一致优于ZS-LLM、TALLRec、EXP3RT等LLM重排序基线。在Amazon-Books上，使用LightGCN作为候选生成器时，Persona4Rec在HR@10上达到0.1151（提升7.5%），NDCG@10达到0.0622（提升10.9%）。在冷启动场景中，对尾部物品的HR@10提升达18.8%。推理延迟仅0.52ms（CPU），比ZS-LLM（5537ms）快4个数量级，内存占用仅0.1GB。



### 消融实验

论文未报告独立的消融实验。

## 总结

提出Persona4Rec框架，将LLM的推理过程从在线阶段转移到离线阶段，通过预计算物品的多视角可解释人物画像（persona），实现轻量级在线推理。

## References

- Offline Reasoning for Efficient Recommendation: LLM-Empowered Persona-Profiled Item Indexing：[arXiv 2602.21756](https://arxiv.org/abs/2602.21756)

- [代码：GitHub](https://github.com/legenduck/PERSONA4REC)
- [PDF源文件](/papers/2602.21756.pdf)
