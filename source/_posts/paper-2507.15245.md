---
title: "基于LLM智能体的学术论文检索"
date: 2025-07-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2507.15245
arxiv_id: "2507.15245"
description: "提出SPAR，一个无需训练、模块化、可扩展的多智能体学术检索框架，通过查询理解、多源检索、引用链探索和重排序等五个智能体协同工作，显著提升了复杂学术查询的检索效果。"
---

> 论文：[arXiv 2507.15245](https://arxiv.org/abs/2507.15245) · 代码：[GitHub](https://github.com/xiaofengShi/SPAR) · PDF：[本地阅读](/papers/2507.15245.pdf)

提出SPAR，一个无需训练、模块化、可扩展的多智能体学术检索框架，通过查询理解、多源检索、引用链探索和重排序等五个智能体协同工作，显著提升了复杂学术查询的检索效果。同时构建了SPARBench，一个包含计算机科学和生物医学领域、经专家标注的高质量学术检索基准。实验表明，SPAR在AutoScholar和SPARBench上分别比最强基线PaSa提升F1达56.92%和23.15%，并实现了精度与召回率的良好平衡。

## 研究问题

提出SPAR，一个无需训练、模块化、可扩展的多智能体学术检索框架，通过查询理解、多源检索、引用链探索和重排序等五个智能体协同工作，显著提升了复杂学术查询的检索效果。同时构建了SPARBench，一个包含计算机科学和生物医学领域、经专家标注的高质量学术检索基准。实验表明，SPAR在AutoScholar和SPARBench上分别比最强基线PaSa提升F1达56.92%和23.15%，并实现了精度与召回率的良好平衡。

## 方法：核心思路与整体框架

SPAR采用多智能体协作流程：首先，查询理解智能体进行意图分类、领域识别和时间约束解析，并生成多个细化查询；然后，检索智能体在多源（Google、arXiv、OpenAlex、Semantic Scholar、PubMed）中执行源自适应查询，并通过RefChain扩展引用；判断智能体评估论文相关性；查询演化智能体基于已检索论文生成新查询以探索新方向；最后，重排序智能体综合相关性、权威性和时效性对结果排序。

![图 1：The architecture of RefChain.](/images/papers/2507.15245/figure_001_refchain.png)

*图 1 · 原图说明：The architecture of RefChain.*

**图示解释：** SPAR采用多智能体协作流程：首先，查询理解智能体进行意图分类、领域识别和时间约束解析，并生成多个细化查询；然后，检索智能体在多源（Google、arXiv、OpenAlex、Semantic Scholar、PubMed）中执行源自适应查询，并通过RefChain扩展引用；判断智能体评估论文相关性；查询演化智能体基于已检索论文生成新查询以探索新方向；最后，重排序智能体综合相关性、权威性和时效性对结果排序。

![图 2：The overview of SPAR.](/images/papers/2507.15245/figure_002_overview.png)

*图 2 · 原图说明：The overview of SPAR.*

**图示解释：** SPAR采用多智能体协作流程：首先，查询理解智能体进行意图分类、领域识别和时间约束解析，并生成多个细化查询；然后，检索智能体在多源（Google、arXiv、OpenAlex、Semantic Scholar、PubMed）中执行源自适应查询，并通过RefChain扩展引用；判断智能体评估论文相关性；查询演化智能体基于已检索论文生成新查询以探索新方向；最后，重排序智能体综合相关性、权威性和时效性对结果排序。

## 创新点

1. 创新点1：提出基于RefChain的迭代检索与查询演化机制，模拟研究者递归追踪引用的行为，通过单层引用链扩展和基于检索历史的查询生成，在提升召回率的同时控制噪声。
2. 创新点2：设计模块化多智能体架构，包含查询理解、检索、查询演化、判断和重排序五个专用智能体，各司其职，无需训练即可灵活组合，支持多源数据接口。
3. 创新点3：构建SPARBench基准，采用多阶段标注流程（LLM粗筛+专家精标），包含50个真实复杂查询和560篇专家验证的相关文档，覆盖计算机科学和生物医学，填补了端到端学术检索评估的空白。

## 实验：数据、基线与结果

### 数据集与设置

- AutoScholar
- SPARBench

### Benchmark 与结果

在AutoScholar上，SPAR的F1达0.3843，比PaSa（0.2449）提升56.92%，召回率0.4105，精度0.3612，而PaSa召回率0.7931但精度仅0.1448。在SPARBench上，SPAR是唯一在所有指标上表现均衡的方法，F1为0.3015，召回率0.3103，精度0.2932，而最强基线GA+LLM的F1仅0.1923。消融实验显示，查询解释使SPARBench精度从0.21提升至0.34；RefChain使召回率提升但精度下降；查询演化使F1提升约0.02；重排序使AutoScholar的Recall@5提升27.6%。

![图 3：Document volume at each filtering stage of the benchmark construction pipeline, showing the reduction from raw retrieval results to the final final set.](/images/papers/2507.15245/figure_005_sparbench_data_flow.png)

*图 3 · 原图说明：Document volume at each filtering stage of the benchmark construction pipeline, showing the reduction from raw retrieval results to the final final set.*

**图示解释：** 在AutoScholar上，SPAR的F1达0.3843，比PaSa（0.2449）提升56.92%，召回率0.4105，精度0.3612，而PaSa召回率0.7931但精度仅0.1448。

### 消融实验

论文未报告独立的消融实验。

## 总结

提出SPAR，一个无需训练、模块化、可扩展的多智能体学术检索框架，通过查询理解、多源检索、引用链探索和重排序等五个智能体协同工作，显著提升了复杂学术查询的检索效果。

## References

- SPAR: Scholar Paper Retrieval with LLM-based Agents for Enhanced Academic Search：[arXiv 2507.15245](https://arxiv.org/abs/2507.15245)

- [代码：GitHub](https://github.com/xiaofengShi/SPAR)
- [PDF源文件](/papers/2507.15245.pdf)
