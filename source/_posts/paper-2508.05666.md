---
title: "混合语义检索增强生成框架"
date: 2025-08-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2508.05666
arxiv_id: "2508.05666"
description: "HySemRAG是一个集成了ETL流水线与多智能体RAG能力的框架，用于自动化文献综合与方法论差距分析。"
---

> 论文：[arXiv 2508.05666](https://arxiv.org/abs/2508.05666) · PDF：[本地阅读](/papers/2508.05666.pdf)

HySemRAG是一个集成了ETL流水线与多智能体RAG能力的框架，用于自动化文献综合与方法论差距分析。它通过混合检索策略（语义搜索、关键词过滤、知识图谱遍历）、智能体自校正框架和事后引用验证，解决了现有RAG系统中的检索噪声、幻觉和缺乏可验证引用等问题。在臭氧暴露与心血管疾病的地理空间流行病学文献中，该系统成功识别了方法论趋势和研究空白。

## 研究问题

HySemRAG是一个集成了ETL流水线与多智能体RAG能力的框架，用于自动化文献综合与方法论差距分析。它通过混合检索策略（语义搜索、关键词过滤、知识图谱遍历）、智能体自校正框架和事后引用验证，解决了现有RAG系统中的检索噪声、幻觉和缺乏可验证引用等问题。在臭氧暴露与心血管疾病的地理空间流行病学文献中，该系统成功识别了方法论趋势和研究空白。

## 方法：核心思路与整体框架

采用八阶段ETL流水线：多源元数据获取、异步PDF检索、自定义文档布局分析（修改Docling）、文献管理、LLM结构化字段提取、LDA主题建模、语义统一和知识图谱构建。随后通过混合检索与多智能体QA框架实现可验证的生成式问答。

![图 1：Figure 1: Graphical Abstract](/images/papers/2508.05666/a83b0cf30eeb22b1aa40c2d832e85b27134f9e8fc256ce3c7e10d7b437f480ad.jpg)

*图 1 · 原图说明：Figure 1: Graphical Abstract*

**图示解释：** 采用八阶段ETL流水线：多源元数据获取、异步PDF检索、自定义文档布局分析（修改Docling）、文献管理、LLM结构化字段提取、LDA主题建模、语义统一和知识图谱构建。

![图 2：Figure 8: Table Missclassification](/images/papers/2508.05666/34d9aec98286aed2e08b78d00c5c636d6150c3597006792484c6983475aac122.jpg)

*图 2 · 原图说明：Figure 8: Table Missclassification*

**图示解释：** 采用八阶段ETL流水线：多源元数据获取、异步PDF检索、自定义文档布局分析（修改Docling）、文献管理、LLM结构化字段提取、LDA主题建模、语义统一和知识图谱构建。

![图 3：Figure 9: Table Correction](/images/papers/2508.05666/672b928d8c3e0f47a3afde6977cfe35c4bc996c19d7159e1a0f6b194c4380570.jpg)

*图 3 · 原图说明：Figure 9: Table Correction*

**图示解释：** 采用八阶段ETL流水线：多源元数据获取、异步PDF检索、自定义文档布局分析（修改Docling）、文献管理、LLM结构化字段提取、LDA主题建模、语义统一和知识图谱构建。

![图 4：Figure 10: Query example](/images/papers/2508.05666/ed78fbae966e452d9df19cfdc5e77fe8f2bb4080d91145231f9d85d52295d1ad.jpg)

*图 4 · 原图说明：Figure 10: Query example*

**图示解释：** 采用八阶段ETL流水线：多源元数据获取、异步PDF检索、自定义文档布局分析（修改Docling）、文献管理、LLM结构化字段提取、LDA主题建模、语义统一和知识图谱构建。

## 创新点

1. 创新点1：提出混合检索策略，结合语义搜索（Qdrant）、关键词搜索和知识图谱遍历（Neo4j），并使用Reciprocal Rank Fusion（RRF）融合结果，克服了单一检索方法的局限性。
2. 创新点2：设计多智能体自校正QA框架，包含生成器LLM和QA审计LLM，通过迭代反馈循环提高生成答案的准确性和可验证性，并生成用于模型微调的首选数据集。
3. 创新点3：实现语义统一流水线，利用Sentence Transformer和余弦相似度进行阈值映射，解决学术文献中的术语歧义问题，确保知识图谱中概念的一致性。

## 实验：数据、基线与结果

### 数据集与设置

- PubMed
- OpenAlex
- Scopus
- Unpaywall API

### Benchmark 与结果

在643次观测（60次测试会话）中，结构化字段提取的语义相似度（0.655±0.178）比PDF文本分块（0.485±0.204）高35.1%（p<0.000001）。智能体自校正系统单次通过成功率为68.3%，平均迭代2.33次。验证后的响应中，引用准确率达99.0%±4.5%，语义相似度达1.000±0.000。在34篇实证研究中，识别出随机森林（58.8%）等主流方法。



### 消融实验

论文未报告独立的消融实验。

## 总结

HySemRAG是一个集成了ETL流水线与多智能体RAG能力的框架，用于自动化文献综合与方法论差距分析。

## References

- HySemRAG：[arXiv 2508.05666](https://arxiv.org/abs/2508.05666)

- [PDF源文件](/papers/2508.05666.pdf)
