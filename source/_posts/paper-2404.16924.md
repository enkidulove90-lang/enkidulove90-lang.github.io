---
title: "大语言模型时代的生成式搜索与推荐综述"
date: 2024-04-01
year: 2024
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2404.16924
arxiv_id: "2404.16924"
description: "本文是首篇从统一视角全面综述生成式搜索与生成式推荐的论文。"
---

> 论文：[arXiv 2404.16924](https://arxiv.org/abs/2404.16924) · PDF：[本地阅读](/papers/2404.16924.pdf)

本文是首篇从统一视角全面综述生成式搜索与生成式推荐的论文。作者抽象出一个统一的生成式范式框架，将现有工作分解为查询/用户表述、文档/物品标识符、训练和推理四个阶段，并据此对现有方法进行分类和比较。论文首次系统总结了生成式搜索的发展，区分了生成式搜索与生成式推荐各自的独特挑战，识别了开放问题并展望了下一代信息获取范式。

## 研究问题

本文是首篇从统一视角全面综述生成式搜索与生成式推荐的论文。作者抽象出一个统一的生成式范式框架，将现有工作分解为查询/用户表述、文档/物品标识符、训练和推理四个阶段，并据此对现有方法进行分类和比较。论文首次系统总结了生成式搜索的发展，区分了生成式搜索与生成式推荐各自的独特挑战，识别了开放问题并展望了下一代信息获取范式。

## 方法：核心思路与整体框架

论文采用综述方法论，首先回顾机器学习和深度学习时代的搜索与推荐范式，然后界定生成式范式的范围，抽象出统一框架。基于该框架，分别对生成式搜索和生成式推荐的方法进行归类分析，涵盖查询/用户表述、标识符设计、训练策略和推理方式。最后进行深度讨论，比较两个领域的异同，识别开放问题并展望未来方向。

![图 2：{Major milestones in the development of generative search.}](/images/papers/2404.16924/figure_002_timeline_search_v2.png)

*图 2 · 原图说明：{Major milestones in the development of generative search.}*

**图示解释：** 论文采用综述方法论，首先回顾机器学习和深度学习时代的搜索与推荐范式，然后界定生成式范式的范围，抽象出统一框架。

## 创新点

1. 首次从统一视角综述生成式搜索与生成式推荐，抽象出包含查询/用户表述、文档/物品标识符、训练、推理四阶段的统一框架，将现有工作映射到不同阶段以凸显优劣势。
2. 首次系统总结生成式搜索的发展，全面梳理了数值ID、标题、N-gram、码本、多视图标识符等文档标识符类型，并从语义性、区分性、可更新性、训练方式和适用场景等维度进行对比分析。
3. 深入对比生成式搜索与生成式推荐的异同，识别开放问题并展望下一代信息获取范式，强调两个领域相互启发、协同发展的关系。

## 实验：数据、基线与结果

### 数据集与设置

本文为综述论文，未开展原创实验。文中汇总了所综述方法使用的数据集与任务，包括文档级检索、段落级检索、对话式问答、多跳问答和跨语言检索等。部分方法对数据集进行了重构，如NQ320K、TriviaQA子集和MSMARCO子集。原文未披露统一的训练/验证/测试划分。

### Benchmark 与结果

本文为综述论文，未开展统一实验，因此未报告统一的性能数值对比。文中汇总了各方法在各自实验中的表现，例如DSI在NQ320K等数据集上验证了生成式检索的可行性，MINDER等多视图标识符方法在NQ、TriviaQA、MSMARCO上验证了有效性，DSI(scaling up)发现生成式搜索在小规模语料上可与先进双编码器竞争，但扩展到百万级段落仍是未解决的挑战。具体性能提升百分比原文未统一披露。

![图 1：Comparison of the three paradigms for search and recommendation, \ie machine learning-based, deep learning-based, and generative search and recommendation. ``rec.'' denotes ``recommendation''.](/images/papers/2404.16924/figure_001_paradigms.png)

*图 1 · 原图说明：Comparison of the three paradigms for search and recommendation, \ie machine learning-based, deep learning-based, and generative search and recommendation. ``rec.'' denotes ``recommendation''.*

**图示解释：** 本文为综述论文，未开展统一实验，因此未报告统一的性能数值对比。

![图 3：{Statistics of six representative datasets in search and recommendation. ``Int.'' denotes ``Interactions'' and ``Rec.'' denotes ``Recommendation''. The results are based on the LLaMA2 tokenizer . The user formulation for generative recommendation includes task descriptions and the user's historical interactions with item titles.}](/images/papers/2404.16924/figure_004_dataset_statistics.png)

*图 3 · 原图说明：{Statistics of six representative datasets in search and recommendation. ``Int.'' denotes ``Interactions'' and ``Rec.'' denotes ``Recommendation''. The results are based on the LLaMA2 tokenizer . The user formulation for generative recommendation includes task descriptions and the user's historical interactions with item titles.}*

**图示解释：** 本文为综述论文，未开展统一实验，因此未报告统一的性能数值对比。

### 消融实验

本文为综述论文，未设置统一的对比基线和消融实验。文中汇总了各方法自身采用的对比方法，主要包括传统检索方法（如BM25、双编码器）和其他生成式搜索方法。

## 总结

本文是首篇从统一视角全面综述生成式搜索与生成式推荐的论文。

## References

- A Survey of Generative Search and Recommendation in the Era of Large Language Models：[arXiv 2404.16924](https://arxiv.org/abs/2404.16924)

- [PDF源文件](/papers/2404.16924.pdf)
