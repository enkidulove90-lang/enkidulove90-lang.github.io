---
title: "VISTA：虚拟序列目标注意力"
date: 2025-10-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2510.22049
arxiv_id: "2510.22049"
description: "提出VISTA两阶段注意力框架，将用户长历史序列压缩为少量摘要嵌入并缓存，使下游模型训练和推理的计算成本固定，从而支持百万级用户历史序列的工业级推荐系统。"
---

> 论文：[arXiv 2510.22049](https://arxiv.org/abs/2510.22049) · PDF：[本地阅读](/papers/2510.22049.pdf)

提出VISTA两阶段注意力框架，将用户长历史序列压缩为少量摘要嵌入并缓存，使下游模型训练和推理的计算成本固定，从而支持百万级用户历史序列的工业级推荐系统。在Meta生产环境中部署，实现了0.5%的在线核心任务提升和94%的推理GPU资源节省。

## 研究问题

提出VISTA两阶段注意力框架，将用户长历史序列压缩为少量摘要嵌入并缓存，使下游模型训练和推理的计算成本固定，从而支持百万级用户历史序列的工业级推荐系统。在Meta生产环境中部署，实现了0.5%的在线核心任务提升和94%的推理GPU资源节省。

## 方法：核心思路与整体框架

采用两阶段框架：第一阶段使用准线性自注意力将超长用户历史序列压缩为128个种子嵌入；第二阶段使用标准Transformer注意力计算候选与摘要嵌入的交互。摘要嵌入每2小时更新并缓存到KV存储中，下游模型直接读取使用。

![图 1：An overview of VISTA architecture.](/images/papers/2510.22049/figure_002_VISTA-overview-1.png)

*图 1 · 原图说明：An overview of VISTA architecture.*

**图示解释：** 采用两阶段框架：第一阶段使用准线性自注意力将超长用户历史序列压缩为128个种子嵌入；第二阶段使用标准Transformer注意力计算候选与摘要嵌入的交互。

![图 2：The QLU module.](/images/papers/2510.22049/figure_003_Reconstruction.png)

*图 2 · 原图说明：The QLU module.*

**图示解释：** 采用两阶段框架：第一阶段使用准线性自注意力将超长用户历史序列压缩为128个种子嵌入；第二阶段使用标准Transformer注意力计算候选与摘要嵌入的交互。

![图 3：An overview of VISTA sequence summarization embedding delivery system.](/images/papers/2510.22049/figure_004_system.png)

*图 3 · 原图说明：An overview of VISTA sequence summarization embedding delivery system.*

**图示解释：** 采用两阶段框架：第一阶段使用准线性自注意力将超长用户历史序列压缩为128个种子嵌入；第二阶段使用标准Transformer注意力计算候选与摘要嵌入的交互。

## 创新点

1. 创新点1：提出两阶段注意力分解框架，将传统目标注意力解耦为用户历史摘要和候选注意力，使下游模型仅需处理压缩后的摘要嵌入。
2. 创新点2：设计准线性注意力(QLA)机制，实现O(N)复杂度的自注意力计算，避免候选间注意力导致的标签泄露问题，同时保持模型表达能力。
3. 创新点3：引入生成式序列重建损失，通过因果解码器强制摘要嵌入保留用户历史序列的完整信息，增强模型记忆能力。

## 实验：数据、基线与结果

### 数据集与设置

数据集：Amazon-Electronics、KuaiRand-1K、Simplified Prod (Minimal Production)、Industrial-Scale Data (Meta生产数据)

### Benchmark 与结果

在Amazon数据集上AUC达0.886，NE降至0.621，优于HSTU等基线。在工业级数据上，VISTA相比HSTU在C-Task上NE降低0.40%，E1-Task降低1.19%。在线A/B测试中，C-Task提升0.5%，O1-Task提升0.2%，O2-Task提升0.04%，推理GPU资源使用降低94%。



### 消融实验

论文未报告独立的消融实验。

## 总结

提出VISTA两阶段注意力框架，将用户长历史序列压缩为少量摘要嵌入并缓存，使下游模型训练和推理的计算成本固定，从而支持百万级用户历史序列的工业级推荐系统。

## References

- VISTA: Virtual Sequential Target Attention for Massive Memorization in Sequential Transducer Generative Recommenders：[arXiv 2510.22049](https://arxiv.org/abs/2510.22049)

- [PDF源文件](/papers/2510.22049.pdf)
