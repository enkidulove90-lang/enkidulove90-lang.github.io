---
title: "新颖性感知的智能体检索"
date: 2026-06-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2606.22151
arxiv_id: "2606.22151"
description: "论文提出了新颖性感知研究智能体，一种原型智能体检索系统，通过六组件流水线（查询分析、ReAct检索循环、相关性排序、模式引导提取、三遍比较智能体、答案生成）在RAG基础上进行结构化多步推理。"
---

> 论文：[arXiv 2606.22151](https://arxiv.org/abs/2606.22151) · PDF：[本地阅读](/papers/2606.22151.pdf)

论文提出了新颖性感知研究智能体，一种原型智能体检索系统，通过六组件流水线（查询分析、ReAct检索循环、相关性排序、模式引导提取、三遍比较智能体、答案生成）在RAG基础上进行结构化多步推理。核心贡献在于比较智能体，它操作结构化贡献记录而非原始文本，生成论文级重叠、差异化以及确定性的问题×方法空白矩阵，从而支持标准RAG无法实现的五种结构化比较能力。在100篇论文的语料库上，系统展示了查询敏感性（平均Jaccard相似度0.115）和结构化比较能力，为科研文献搜索提供了超越排名列表的、可审计的结构化视图。

## 研究问题

论文提出了新颖性感知研究智能体，一种原型智能体检索系统，通过六组件流水线（查询分析、ReAct检索循环、相关性排序、模式引导提取、三遍比较智能体、答案生成）在RAG基础上进行结构化多步推理。核心贡献在于比较智能体，它操作结构化贡献记录而非原始文本，生成论文级重叠、差异化以及确定性的问题×方法空白矩阵，从而支持标准RAG无法实现的五种结构化比较能力。在100篇论文的语料库上，系统展示了查询敏感性（平均Jaccard相似度0.115）和结构化比较能力，为科研文献搜索提供了超越排名列表的、可审计的结构化视图。

## 方法：核心思路与整体框架

论文采用智能体检索方法论，构建了一个六阶段顺序流水线：查询分析器将用户查询分解为2-4个检索意图；ReAct检索循环使用FAISS和Sentence-Transformers进行嵌入搜索，并在检索不足时进行迭代优化；排序器以低温度对候选论文进行相关性评分；贡献提取器通过模式引导解码提取结构化四字段记录；比较智能体执行三遍比较（重叠、差异化、空白）；答案生成器合成最终报告。

![图 1：Figure 1: End-to-end agentic retrieval pipeline. A user query is decomposed and reformulated, candidate papers are retrieved and ranked, structured contribution records are extracted under a schema, three comparison passes produce overlaps / diferentiation / a gap matrix, and a final citation-grounded report is generated.](/images/papers/2606.22151/4bf4dfdf915f70ed14a1afb471a156f7f7acf5cc5f1c631f05dc56b1289e65fd.jpg)

*图 1 · 原图说明：Figure 1: End-to-end agentic retrieval pipeline. A user query is decomposed and reformulated, candidate papers are retrieved and ranked, structured contribution records are extracted under a schema, three comparison passes produce overlaps / diferentiation / a gap matrix, and a final citation-grounded report is generated.*

**图示解释：** 在三个主要查询上，系统达到平均Precision@5为1.000，nDCG@5为0.752，Recall@5为0.527，MRR为1.000，优于BM25（P@5 0.733）、稠密检索（0.667）和混合检索（0.667）。

## 创新点

1. 创新点1：提出六组件智能体检索流水线，包含类型化的组件间契约，将ReAct检索循环、相关性排序、模式引导提取和多遍比较阶段有机结合，形成端到端的结构化比较系统。
2. 创新点2：设计三遍比较智能体，在结构化贡献记录而非原始文本上运行，通过重叠识别、差异化分析和确定性空白矩阵构建，实现论文间的跨论文比较和语料级空白分析。
3. 创新点3：引入确定性的问题×方法空白矩阵构建方法，基于固定分类法程序化填充矩阵，避免了LLM直接生成空白时的不稳定性和跨应用噪声，使空白集可复现且可审计。

## 实验：数据、基线与结果

### 数据集与设置

- 100-paper agentic AI and retrieval corpus

### Benchmark 与结果

在三个主要查询上，系统达到平均Precision@5为1.000，nDCG@5为0.752，Recall@5为0.527，MRR为1.000，优于BM25（P@5 0.733）、稠密检索（0.667）和混合检索（0.667）。在扩展的十个查询上，平均Precision@5为0.980，nDCG@5为0.739，Recall@5为0.489。模式合规性在三个主要查询上为86.7%，在十个查询上为84.0%。空白矩阵验证显示空白精度为0.600。与基线RAG系统相比，全系统支持5/5结构化比较能力，而基线支持0/5。



### 消融实验

论文未报告独立的消融实验。

## 总结

论文提出了新颖性感知研究智能体，一种原型智能体检索系统，通过六组件流水线（查询分析、ReAct检索循环、相关性排序、模式引导提取、三遍比较智能体、答案生成）在RAG基础上进行结构化多步推理。

## References

- Novelty-Aware Agentic Retrieval：[arXiv 2606.22151](https://arxiv.org/abs/2606.22151)

- [PDF源文件](/papers/2606.22151.pdf)
