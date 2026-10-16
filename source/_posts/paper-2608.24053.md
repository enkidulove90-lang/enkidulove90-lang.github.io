---
title: "微信多模态嵌入模型技术报告"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.24053
arxiv_id: "2608.24053"
description: "本文提出了WeMM-Embedding，一个覆盖2B、4B、9B三种参数规模的通用多模态嵌入模型家族，基于Qwen3.5原生多模态骨干网络构建。"
---

> 论文：[arXiv 2608.24053](https://arxiv.org/abs/2608.24053) · 代码：[GitHub](https://github.com/Tencent/WeMM-Embedding) · PDF：[本地阅读](/papers/2608.24053.pdf)

本文提出了WeMM-Embedding，一个覆盖2B、4B、9B三种参数规模的通用多模态嵌入模型家族，基于Qwen3.5原生多模态骨干网络构建。模型采用两阶段训练策略：第一阶段在数亿级异构多模态数据上进行大规模对齐，第二阶段在精选数据上通过细粒度相关性监督和跨规模知识蒸馏进行精调。WeMM-Embedding支持文本、图像、视频、视觉文档及任意交错多模态输入的统一编码，并支持Matryoshka灵活嵌入维度。在MMEB-v2/v3、12个跨模态检索基准及26任务内部基准上均取得领先性能，并已在微信多个推荐与搜索场景中大规模部署。

## 研究问题

本文提出了WeMM-Embedding，一个覆盖2B、4B、9B三种参数规模的通用多模态嵌入模型家族，基于Qwen3.5原生多模态骨干网络构建。模型采用两阶段训练策略：第一阶段在数亿级异构多模态数据上进行大规模对齐，第二阶段在精选数据上通过细粒度相关性监督和跨规模知识蒸馏进行精调。WeMM-Embedding支持文本、图像、视频、视觉文档及任意交错多模态输入的统一编码，并支持Matryoshka灵活嵌入维度。在MMEB-v2/v3、12个跨模态检索基准及26任务内部基准上均取得领先性能，并已在微信多个推荐与搜索场景中大规模部署。

## 方法：核心思路与整体框架

WeMM-Embedding基于Qwen3.5原生多模态骨干，采用last-token pooling方式，在输入序列末尾添加专用<embedding> token并取其最后一层隐状态经L2归一化作为表示。训练分两阶段：第一阶段在数亿级pair-based数据上使用InfoNCE对比学习和分级相关性CoSENT排序损失进行大规模多任务对齐；第二阶段在精选数据上引入重排序模型监督和跨规模嵌入蒸馏进行精调。所有目标均结合MRL在多个嵌入维度上独立计算。

![图 1：Figure 2 Overview of our multimodal training data. Major data families and representative coverage across diverse task settings and content domains.](/images/papers/2608.24053/2dcc6661f27b363db3819560518c94a168ceecf463e01f32942b6649d0776ccc.jpg)

*图 1 · 原图说明：Figure 2 Overview of our multimodal training data. Major data families and representative coverage across diverse task settings and content domains.*

**图示解释：** WeMM-Embedding基于Qwen3.5原生多模态骨干，采用last-token pooling方式，在输入序列末尾添加专用<embedding> token并取其最后一层隐状态经L2归一化作为表示。

## 创新点

1. 提出两阶段渐进式训练策略：第一阶段在数亿级异构多模态数据上建立广泛对齐，第二阶段在精选数据上通过语义平衡重采样、质量过滤和难负样本增强实现细粒度相关性学习，兼顾覆盖广度与匹配精度。
2. 设计基于Semantic-ID引导的数据重采样方法：利用RQ-KMeans对嵌入表示进行三级量化得到语义ID，根据码本分配密度调整采样率，缓解高频语义模式的重复曝光问题，提升数据语义平衡性。
3. 引入多源监督信号融合机制：结合对比学习、分级相关性排序（score-gap-weighted CoSENT）、重排序模型监督和跨规模嵌入蒸馏，在统一pair-based框架下灵活适配不同监督信号。
4. 支持灵活嵌入维度与多位置嵌入token：通过Matryoshka Representation Learning支持单次前向获取多种维度嵌入，并允许在序列不同位置插入多个<embedding> token以同时提取单模态和联合模态表示。

## 实验：数据、基线与结果

### 数据集与设置

评估覆盖图像-文本检索、视频-文本检索、视觉文档检索、文本检索、Agent检索和音频检索等任务。公开基准包括MMEB-v2（78任务）、MMEB-v3（190任务，含53文本任务、47 Agent任务、11音频任务和MCMR）、12个跨模态检索基准。内部基准包含26个任务，覆盖分类、搜索、跨域内容匹配、文章相关性和视频相关性五类。训练数据为数亿级异构pair，精选数据约为其十分之一。具体训练/验证/测试划分原文未披露。

### Benchmark 与结果

在MMEB-v3上，WeMM-Embedding-9B取得V3-All 59.5分，超越Qwen3-VL-Embedding-8B（53.5）和Tianmu-Emb-Uni-8B（53.3）。在MMEB-v2上，2B模型即超越此前领先的8B开源基线，9B模型达到80.6分排名第一。在12个跨模态检索基准上，2B/4B/9B分别取得79.8/80.8/81.7的平均分，超越Gemini Embedding 2（79.5）和Qwen3-VL-Embedding-8B（76.7）。在26任务内部基准上，2B模型平均72.0分，大幅超越Qwen3-VL-Embedding-2B的60.9分。已在14个在线A/B测试中取得一致提升。



### 消融实验

对比方法包括VLM2Vec-V2 (2B)、Omni-Embed-Nemotron (3B)、E5-Omni (3B/7B)、Qwen3-VL-Embedding (2B/8B)、WAVE (7B)、VLM2Vec (8B)、LCO-Embedding-Omni (7B)、GME (8B)、Tianmu-Emb-Uni (8B)，以及专有模型Gemini Embedding 2、Amazon Nova MME、Voyage Multimodal 3.5。消融设置包括不同模型规模（2B/4B/9B）的对比。

## 总结

本文提出了WeMM-Embedding，一个覆盖2B、4B、9B三种参数规模的通用多模态嵌入模型家族，基于Qwen3.5原生多模态骨干网络构建。

## References

- WeMM-Embedding: WeChat Multi-Modal Embedding Technical Report：[arXiv 2608.24053](https://arxiv.org/abs/2608.24053)

- [代码：GitHub](https://github.com/Tencent/WeMM-Embedding)
- [PDF源文件](/papers/2608.24053.pdf)
