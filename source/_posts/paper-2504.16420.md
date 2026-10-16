---
title: "A Survey of Foundation Model-Powered Recommender Systems: From Feature-Based, Generative to Agentic Paradigms"
date: 2025-04-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2504.16420
arxiv_id: "2504.16420"
---

## 一、简介

本文系统综述了基础模型（FM）在推荐系统（RS）中的应用，提出了一个涵盖特征增强、生成式和智能体三大范式的分类框架。文章详细梳理了从传统数据到多模态数据的演变，分析了FM在表示学习、自然语言理解和多模态推理方面的能力，并探讨了其在Top-N推荐、序列推荐、零样本/少样本推荐、对话推荐和内容生成等任务中的应用。最后，本文总结了关键机遇（如泛化能力提升、可解释性增强）和挑战（如跨域泛化、公平性、多模态融合），并指出了未来研究方向，包括多模态推荐智能体、检索增强框架和终身学习等。

## 二、论文方法

本文采用系统性文献综述方法，收集并分析了超过150篇来自顶级会议和期刊（如ICLR、NeurIPS、KDD等）的相关论文。通过构建一个从数据特征、集成范式到下游任务和开放挑战的分类体系，对现有研究进行了归纳、比较和批判性分析，并识别了关键趋势和未来方向。

## 三、论文里的图与解释

### 图 1

![Three Paradigms of FM-Powered Recommender Systems](/images/papers/2504.16420/figure_001_framework.png)

**原图说明：** Three Paradigms of FM-Powered Recommender Systems

**图示解释：** 该图对应论文中的“Three Paradigms of FM-Powered Recommender Systems”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![The taxonomy of FM4RecSys from data characteristics to open problems and opportunities. In contrast to previous surveys, our methodology introduces a unique viewpoint for examining the intersection of FM4RecSys from data characteristics to open problems and opportunities, which are detailed in Section .](/images/papers/2504.16420/figure_002_survey_overview_fig.png)

**原图说明：** The taxonomy of FM4RecSys from data characteristics to open problems and opportunities. In contrast to previous surveys, our methodology introduces a unique viewpoint for examining the intersection of FM4RecSys from data characteristics to open problems and opportunities, which are detailed in Section .

**图示解释：** 该图对应论文中的“The taxonomy of FM4RecSys from data characteristics to open problems and opportunities. In contrast to previous surveys, our methodology introduces a unique viewpoint for examining the intersection of FM4RecSys from data characteristics to open problems and opportunities, which are detailed in Section .”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![The taxonomy of FM4RecSys from data characteristics to open problems and opportunities. In contrast to previous surveys, our methodology introduces a unique viewpoint for examining the intersection of FM4RecSys from data characteristics to open problems and opportunities, which are detailed in Section .](/images/papers/2504.16420/figure_003_main_fig.png)

**原图说明：** The taxonomy of FM4RecSys from data characteristics to open problems and opportunities. In contrast to previous surveys, our methodology introduces a unique viewpoint for examining the intersection of FM4RecSys from data characteristics to open problems and opportunities, which are detailed in Section .

**图示解释：** 该图对应论文中的“The taxonomy of FM4RecSys from data characteristics to open problems and opportunities. In contrast to previous surveys, our methodology introduces a unique viewpoint for examining the intersection of FM4RecSys from data characteristics to open problems and opportunities, which are detailed in Section .”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出了一个涵盖特征增强、生成式和智能体三大范式的统一分类框架，系统性地组织并分析了FM在RS中的不同集成角色，从被动特征提供者到主动决策者。
2. 创新点2：不仅关注LLM，还涵盖了视觉和多模态基础模型，提供了比以往仅聚焦LLM的综述更广泛的视角，并深入探讨了多模态数据融合技术。
3. 创新点3：对三大范式进行了批判性分析，指出了各自的权衡（trade-offs），并特别强调了智能体范式在动态适应、多模态情境化和伦理对齐方面的变革潜力。

## 五、实验数据集选择

- Amazon Reviews
- MovieLens
- Yelp
- Steam
- Goodreads
- Last.fm

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

- Amazon Reviews
- MovieLens
- Yelp
- Steam
- Goodreads
- Last.fm

## 八、总结

论文未提供可独立提取的总结章节。

## References

完整参考文献请见论文原文。

### 在线资源

- [论文：arXiv 2504.16420](https://arxiv.org/abs/2504.16420)
- [代码：GitHub](https://github.com/huggingface/smolagents)
- [代码：GitHub](https://github.com/microsoft/autogen)
- [PDF源文件](/papers/2504.16420.pdf)
