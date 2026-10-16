---
title: "LLM驱动的隐蔽数据投毒攻击"
date: 2025-05-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2505.05196
arxiv_id: "2505.05196"
description: "本文系统研究了针对基于嵌入的检索增强推荐系统（RAG）的提供方数据投毒攻击。"
---

> 论文：[arXiv 2505.05196](https://arxiv.org/abs/2505.05196) · PDF：[本地阅读](/papers/2505.05196.pdf)

本文系统研究了针对基于嵌入的检索增强推荐系统（RAG）的提供方数据投毒攻击。作者形式化了在令牌编辑和语义相似性约束下的攻击，提出了三种基于LLM的文本重写攻击变体（情感编辑、邻居借用、链式重写），并证明仅修改项目描述中少量令牌即可有效提升长尾项目或打压热门项目，同时保持隐蔽性。实验在MovieLens数据集上使用两种LLM检索模块验证了攻击的有效性，揭示了RAG管道对元数据篡改的脆弱性。

## 研究问题

本文系统研究了针对基于嵌入的检索增强推荐系统（RAG）的提供方数据投毒攻击。作者形式化了在令牌编辑和语义相似性约束下的攻击，提出了三种基于LLM的文本重写攻击变体（情感编辑、邻居借用、链式重写），并证明仅修改项目描述中少量令牌即可有效提升长尾项目或打压热门项目，同时保持隐蔽性。实验在MovieLens数据集上使用两种LLM检索模块验证了攻击的有效性，揭示了RAG管道对元数据篡改的脆弱性。

## 方法：核心思路与整体框架

本文采用提供方数据投毒攻击方法。攻击者选择长尾（提升）或热门（打压）项目，使用LLM在10%令牌编辑预算和SBERT语义相似度≥0.80约束下重写项目描述。设计了三种攻击：情感编辑、邻居借用和链式攻击。在RAG推荐管道中，先由Sentence Transformer检索候选，再由OpenAI LLM重排序，评估攻击对项目排名和系统级指标（Recall@K, nDCG@K）的影响。

![图 1：High-level RAG architecture in a recommender setting. A retriever selects candidate items (step 1). An LLM uses these retrieved texts and user queries to re-rank or generate final recommendations (step 2). In our poisoning scenario (red arrow), an attacker subtly modifies item descriptions to alter how retrieval and generation perceive items.](/images/papers/2505.05196/figure_001_RAG_Attack_ver3.png)

*图 1 · 原图说明：High-level RAG architecture in a recommender setting. A retriever selects candidate items (step 1). An LLM uses these retrieved texts and user queries to re-rank or generate final recommendations (step 2). In our poisoning scenario (red arrow), an attacker subtly modifies item descriptions to alter how retrieval and generation perceive items.*

**图示解释：** 本文采用提供方数据投毒攻击方法。

## 创新点

1. 创新点1：形式化了面向RAG推荐系统的提供方文本重写攻击，定义了提升和打压两种对抗目标，并引入令牌编辑预算和语义相似性约束来量化攻击的隐蔽性。
2. 创新点2：设计了三种基于LLM的文本攻击变体：情感编辑（注入情感词）、邻居借用（从语义相似项目借用短语）和链式攻击（两者结合），均可在低编辑预算下实现有效攻击。
3. 创新点3：通过实验对比OpenAI和Sentence Transformer两种检索模块，发现基于LLM的管道对文本修改更敏感，揭示了生成式重排序会放大对抗性文本信号。

## 实验：数据、基线与结果

### 数据集与设置

实验任务：在MovieLens数据集上评估文本投毒攻击对RAG推荐系统的影响。数据规模：ml-latest-small（约100k评分）。预处理：将项目按流行度分为长尾（不流行）和短头（流行）两类。训练/验证/测试划分：原文未明确披露，但系统对修改后的描述进行重新索引或重新训练。

### Benchmark 与结果

实验表明，链式攻击在提升场景下最有效，在OpenAI管道中将项目平均排名从7.00降至4.67（降低33%），而情感和邻居攻击效果较温和。在打压场景中，链式攻击同样产生最大排名变化。OpenAI管道对文本修改比Sentence Transformer更敏感。系统级指标Recall和nDCG变化不大（最大下降约2-3个百分点），表明局部攻击主要影响目标项目可见性而非全局性能。



### 消融实验

主要对比方法：无攻击的原始描述（Original）作为基线。消融设置：对比三种攻击变体（Emotional, Neighborhood, Chain）的效果。

## 总结

本文系统研究了针对基于嵌入的检索增强推荐系统（RAG）的提供方数据投毒攻击。

## References

- Stealthy LLM-Driven Data Poisoning Attacks Against Embedding-Based Retrieval-Augmented Recommender Systems：[arXiv 2505.05196](https://arxiv.org/abs/2505.05196)

- [PDF源文件](/papers/2505.05196.pdf)
