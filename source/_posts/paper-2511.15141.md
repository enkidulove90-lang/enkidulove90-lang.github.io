---
title: "ItemRAG：基于物品的检索增强生成推荐"
date: 2025-11-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2511.15141
arxiv_id: "2511.15141"
description: "本文提出ItemRAG，一种面向LLM推荐系统的基于物品的检索增强生成方法。"
---

> 论文：[arXiv 2511.15141](https://arxiv.org/abs/2511.15141) · 代码：[GitHub](https://github.com/kswoo97/ItemRAG) · PDF：[本地阅读](/papers/2511.15141.pdf)

本文提出ItemRAG，一种面向LLM推荐系统的基于物品的检索增强生成方法。核心创新在于将检索粒度从粗粒度的用户历史切换为细粒度的物品级别，通过结合物品共现关系和语义相似性来检索与目标物品或候选物品相关的信息，从而增强物品描述。该方法有效解决了传统基于用户检索方法中噪声大、对候选物品信息不足的问题，在标准推荐和冷启动物品推荐任务中均显著优于现有方法，Hit-Ratio@1提升最高达43%。

## 研究问题

本文提出ItemRAG，一种面向LLM推荐系统的基于物品的检索增强生成方法。核心创新在于将检索粒度从粗粒度的用户历史切换为细粒度的物品级别，通过结合物品共现关系和语义相似性来检索与目标物品或候选物品相关的信息，从而增强物品描述。该方法有效解决了传统基于用户检索方法中噪声大、对候选物品信息不足的问题，在标准推荐和冷启动物品推荐任务中均显著优于现有方法，Hit-Ratio@1提升最高达43%。

## 方法：核心思路与整体框架

ItemRAG首先为每个查询物品（用户历史或候选集中的物品）构建检索池，池中包含与该物品直接共现的物品，以及与语义相似物品共现的物品。然后，根据共现频率对池中物品进行加权采样，最后利用LLM对采样物品生成摘要，并将该摘要附加到原始物品描述中，用于最终的推荐提示。

![图 1：Figure 2: An example case of ItemRAG, our item-based RAG method. For retrieving relevant items for item ??, we first identify items that are co-purchased with (1) item ?? itself and/or (2) items whose textual descriptions are similar to that of item ??. Then, we sample a specified number of items from this pool, with selection probabilities proportional to their co-purchase frequencies with item ??. Subsequently, we prompt an LLM to generate a summary of the sampled items and incorporate the summary into the final recommendation prompt, guiding the LLM to understand the co-purchase patterns among items.](/images/papers/2511.15141/b05093034509c84f370357260f73eb5bb4c5b94ae45bd82c8590abbfc71793a3.jpg)

*图 1 · 原图说明：Figure 2: An example case of ItemRAG, our item-based RAG method. For retrieving relevant items for item ??, we first identify items that are co-purchased with (1) item ?? itself and/or (2) items whose textual descriptions are similar to that of item ??. Then, we sample a specified number of items from this pool, with selection probabilities proportional to their co-purchase frequencies with item ??. Subsequently, we prompt an LLM to generate a summary of the sampled items and incorporate the summary into the final recommendation prompt, guiding the LLM to understand the co-purchase patterns among items.*

**图示解释：** ItemRAG首先为每个查询物品（用户历史或候选集中的物品）构建检索池，池中包含与该物品直接共现的物品，以及与语义相似物品共现的物品。

## 创新点

1. 创新点1：提出基于物品的RAG范式。区别于传统的基于用户历史检索，ItemRAG对目标用户历史中的每个物品和每个候选物品进行细粒度检索增强，减少了噪声并提供了对推荐更直接相关的证据。
2. 创新点2：设计结合共现与语义的检索策略。针对冷启动物品，通过检索与语义相似物品共现的物品来扩展检索池；针对弱相关性问题，根据共现频率进行加权采样，优先选择信息量更大的物品。
3. 创新点3：提出共现频率加权的采样机制。在检索池中，依据物品对的共现频率计算采样权重，使得频繁共现、相关性强的物品更有可能被选中，从而提升检索质量。

## 实验：数据、基线与结果

### 数据集与设置

- Amazon Reviews数据集：Sports & Outdoors
- Amazon Reviews数据集：Toys & Games
- Amazon Reviews数据集：Beauty & Personal Care
- Amazon Reviews数据集：Arts, Crafts & Sewing

### Benchmark 与结果

在四个Amazon子数据集上，ItemRAG在20个评估设置中18个优于所有基线。与最强用户基线CoRAL相比，在Toys数据集上Hit-Ratio@1提升11%。在冷启动场景下，ItemRAG在所有设置中均最优，性能仅比标准设置平均下降1%。消融实验表明，去除候选增强、共现信息、语义相似物品或频率加权采样均会导致性能下降。



### 消融实验

论文未报告独立的消融实验。

## 总结

本文提出ItemRAG，一种面向LLM推荐系统的基于物品的检索增强生成方法。

## References

- ItemRAG: Item-Based Retrieval-Augmented Generation for LLM-Based Recommendation：[arXiv 2511.15141](https://arxiv.org/abs/2511.15141)

- [代码：GitHub](https://github.com/kswoo97/ItemRAG)
- [PDF源文件](/papers/2511.15141.pdf)
