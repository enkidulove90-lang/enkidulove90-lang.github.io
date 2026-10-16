---
title: "A Survey of Generative Search and Recommendation in the Era of Large Language Models"
date: 2024-04-01
year: 2024
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2404.16924
arxiv_id: "2404.16924"
---

## 一、简介

本文是首篇从统一视角全面综述生成式搜索与生成式推荐的论文。作者抽象出一个统一的生成式范式框架，将现有工作分解为查询/用户表述、文档/物品标识符、训练和推理四个阶段，并据此对现有方法进行分类和比较。论文首次系统总结了生成式搜索的发展，区分了生成式搜索与生成式推荐各自的独特挑战，识别了开放问题并展望了下一代信息获取范式。

## 二、论文方法

论文采用综述方法论，首先回顾机器学习和深度学习时代的搜索与推荐范式，然后界定生成式范式的范围，抽象出统一框架。基于该框架，分别对生成式搜索和生成式推荐的方法进行归类分析，涵盖查询/用户表述、标识符设计、训练策略和推理方式。最后进行深度讨论，比较两个领域的异同，识别开放问题并展望未来方向。

## 三、论文里的图与解释

### 图 1

![Comparison of the three paradigms for search and recommendation, \ie machine learning-based, deep learning-based, and generative search and recommendation. ``rec.'' denotes ``recommendation''.](/images/papers/2404.16924/figure_001_paradigms.png)

**原图说明：** Comparison of the three paradigms for search and recommendation, \ie machine learning-based, deep learning-based, and generative search and recommendation. ``rec.'' denotes ``recommendation''.

**图示解释：** 该图对应论文中的“Comparison of the three paradigms for search and recommendation, \ie machine learning-based, deep learning-based, and generative search and recommendation. ``rec.'' denotes ``recommendation''.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![{Major milestones in the development of generative search.}](/images/papers/2404.16924/figure_002_timeline_search_v2.png)

**原图说明：** {Major milestones in the development of generative search.}

**图示解释：** 该图对应论文中的“{Major milestones in the development of generative search.}”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![{Statistics of six representative datasets in search and recommendation. ``Int.'' denotes ``Interactions'' and ``Rec.'' denotes ``Recommendation''. The results are based on the LLaMA2 tokenizer . The user formulation for generative recommendation includes task descriptions and the user's historical interactions with item titles.}](/images/papers/2404.16924/figure_004_dataset_statistics.png)

**原图说明：** {Statistics of six representative datasets in search and recommendation. ``Int.'' denotes ``Interactions'' and ``Rec.'' denotes ``Recommendation''. The results are based on the LLaMA2 tokenizer . The user formulation for generative recommendation includes task descriptions and the user's historical interactions with item titles.}

**图示解释：** 该图对应论文中的“{Statistics of six representative datasets in search and recommendation. ``Int.'' denotes ``Interactions'' and ``Rec.'' denotes ``Recommendation''. The results are based on the LLaMA2 tokenizer . The user formulation for generative recommendation includes task descriptions and the user's historical interactions with item titles.}”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 首次从统一视角综述生成式搜索与生成式推荐，抽象出包含查询/用户表述、文档/物品标识符、训练、推理四阶段的统一框架，将现有工作映射到不同阶段以凸显优劣势。
2. 首次系统总结生成式搜索的发展，全面梳理了数值ID、标题、N-gram、码本、多视图标识符等文档标识符类型，并从语义性、区分性、可更新性、训练方式和适用场景等维度进行对比分析。
3. 深入对比生成式搜索与生成式推荐的异同，识别开放问题并展望下一代信息获取范式，强调两个领域相互启发、协同发展的关系。

## 五、实验数据集选择

- NQ10K
- NQ100K
- NQ320K
- TriviaQA
- MSMARCO
- KILT
- BEIR
- HotpotQA
- TOPIOCQA
- QRECC
- ORQUAC
- XOR QA 100k
- TREC DL
- NQ-inc
- MSMARCO-inc
- WebQuestions

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

- NQ10K
- NQ100K
- NQ320K
- TriviaQA
- MSMARCO
- KILT
- BEIR
- HotpotQA
- TOPIOCQA
- QRECC
- ORQUAC
- XOR QA 100k
- TREC DL
- NQ-inc
- MSMARCO-inc
- WebQuestions

## 八、总结

论文未提供可独立提取的总结章节。

## References

完整参考文献请见论文原文。

### 在线资源

- [论文：arXiv 2404.16924](https://arxiv.org/abs/2404.16924)
- [PDF源文件](/papers/2404.16924.pdf)
