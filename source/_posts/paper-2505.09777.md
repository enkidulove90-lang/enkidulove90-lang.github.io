---
title: "A Survey on Large Language Models in Multimodal Recommender Systems"
date: 2025-05-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2505.09777
arxiv_id: "2505.09777"
---

## 一、简介

本文是一篇关于大语言模型（LLM）在多模态推荐系统（MRS）中应用的综述。主要贡献包括：提出了一个以LLM为中心的新分类法，将LLM的集成方式分为提示、训练和数据适配三大类；系统性地回顾了提示策略、微调方法和数据适配技术；识别并引入了来自相邻推荐领域（如序列推荐、知识感知推荐）的可迁移技术；提供了更全面的评估指标和数据集资源；指出了当前研究空白和未来方向。

## 二、论文方法

本文采用综述研究方法，通过系统性地检索、筛选和分类近年来的相关论文，构建了以LLM功能（提示、训练、数据适配）为核心的分类框架。对每类方法进行了详细的技术分析、优缺点比较和适用场景讨论，并总结了当前趋势和未来方向。

## 三、论文里的图与解释

### 图 1

![Classification of modality adaptation strategies for integrating structured and multimodal inputs into LLMs.](/images/papers/2505.09777/figure_001_adaptation.png)

**原图说明：** Classification of modality adaptation strategies for integrating structured and multimodal inputs into LLMs.

**图示解释：** 该图对应论文中的“Classification of modality adaptation strategies for integrating structured and multimodal inputs into LLMs.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出了以LLM为中心的新分类法，区别于传统以编码器为中心的MRS综述，将LLM集成策略分为提示、训练和数据适配三大类，并细分为硬提示、软提示、混合提示、控制逻辑提示等子类。
2. 创新点2：系统性地引入了来自相邻推荐领域（如序列推荐、文本推荐、知识感知推荐）的LLM技术，并分析了这些技术向多模态推荐场景迁移的可能性，扩展了MRS的设计空间。
3. 创新点3：提供了比以往综述更全面的评估指标和数据集资源，包括NLP衍生指标（如BLEURT）和LLM评估器，以及涵盖更多领域和模态的公开数据集列表。

## 五、实验数据集选择

- Amazon Reviews (多类别)
- Yelp
- MovieLens
- Steam
- KuaiRand
- MicroLens
- BabyMind
- GNSS (全球导航卫星系统) 数据集

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

- Amazon Reviews (多类别)
- Yelp
- MovieLens
- Steam
- KuaiRand
- MicroLens
- BabyMind
- GNSS (全球导航卫星系统) 数据集

## 八、总结

论文未提供可独立提取的总结章节。

## References

完整参考文献请见论文原文。

### 在线资源

- [论文：arXiv 2505.09777](https://arxiv.org/abs/2505.09777)
- [PDF源文件](/papers/2505.09777.pdf)
