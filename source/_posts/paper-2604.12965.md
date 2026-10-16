---
title: "大规模推荐的高效检索分层索引"
date: 2026-04-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2604.12965
arxiv_id: "2604.12965"
description: "本文提出HILL方法，为大规模基础检索模型（如Meta的MoNN）学习一个分层索引结构，通过交叉注意力和残差量化实现高效近似搜索，同时保持检索准确性。"
---

> 论文：[arXiv 2604.12965](https://arxiv.org/abs/2604.12965) · PDF：[本地阅读](/papers/2604.12965.pdf)

本文提出HILL方法，为大规模基础检索模型（如Meta的MoNN）学习一个分层索引结构，通过交叉注意力和残差量化实现高效近似搜索，同时保持检索准确性。该方法在Meta的广告推荐系统中部署，服务于数十亿用户。此外，论文发现索引中间节点可产生少量高质量数据，用于测试时训练（Test-Time Training）以进一步提升模型性能，并首次系统性地公开了Meta基础检索模型MoNN的架构细节。

## 研究问题

本文提出HILL方法，为大规模基础检索模型（如Meta的MoNN）学习一个分层索引结构，通过交叉注意力和残差量化实现高效近似搜索，同时保持检索准确性。该方法在Meta的广告推荐系统中部署，服务于数十亿用户。此外，论文发现索引中间节点可产生少量高质量数据，用于测试时训练（Test-Time Training）以进一步提升模型性能，并首次系统性地公开了Meta基础检索模型MoNN的架构细节。

## 方法：核心思路与整体框架

HILL方法首先利用交叉注意力机制学习单层映射，将物品嵌入软分配到索引节点；然后通过残差量化逐层堆叠，将低层残差传递到高层，形成层次结构。训练过程中采用温度调度、平衡正则化和预热策略优化。此外，还提供了基于EM算法和FAISS的近似版本，以降低计算资源需求。

![图 1：Overall Pipeline of MoNN Foundation Retrieval Model with HILL Index.](/images/papers/2604.12965/figure_001_framework.png)

*图 1 · 原图说明：Overall Pipeline of MoNN Foundation Retrieval Model with HILL Index.*

**图示解释：** HILL方法首先利用交叉注意力机制学习单层映射，将物品嵌入软分配到索引节点；然后通过残差量化逐层堆叠，将低层残差传递到高层，形成层次结构。

![图 2：A MoNN Block](/images/papers/2604.12965/figure_002_MoNN.png)

*图 2 · 原图说明：A MoNN Block*

**图示解释：** HILL方法首先利用交叉注意力机制学习单层映射，将物品嵌入软分配到索引节点；然后通过残差量化逐层堆叠，将低层残差传递到高层，形成层次结构。

![图 3：A Hierarchical Index Example Learnt by HILL.](/images/papers/2604.12965/figure_003_HILL.png)

*图 3 · 原图说明：A Hierarchical Index Example Learnt by HILL.*

**图示解释：** HILL方法首先利用交叉注意力机制学习单层映射，将物品嵌入软分配到索引节点；然后通过残差量化逐层堆叠，将低层残差传递到高层，形成层次结构。

## 创新点

1. 创新点1：提出HILL分层索引学习方法，利用交叉注意力机制和残差量化，在基础检索模型之上构建层次化索引树，实现从粗到细的近似搜索，大幅降低推理成本。
2. 创新点2：发现索引树的中间层节点可生成高质量的用户-索引节点数据对，用于测试时训练（Test-Time Training），在不依赖真实标签的情况下微调模型，进一步提升检索性能。
3. 创新点3：设计了软硬分配过渡的温度调度器、平衡索引分布的FLOPs正则化器以及预热策略等训练技巧，确保索引学习的稳定性和有效性。

## 实验：数据、基线与结果

### 数据集与设置

数据集：Gowalla、Yelp2018、Amazon-Book、Meta内部广告推荐数据集

### Benchmark 与结果

在内部数据集上，HILL使MoNN Large模型相比基线TTSN在NE指标上降低1.70%，Recall提升9.4%，但推理成本仅增加24.6倍（相比无索引的线性扫描大幅降低）。在公开数据集Gowalla上，HILL在Recall@20和NDCG@20上分别达到0.1924和0.1628，优于所有基线（如NESCL: 0.1908/0.1614）。消融实验显示，移除温度调度器导致NE上升0.10%，验证了各训练技巧的有效性。



### 消融实验

论文未报告独立的消融实验。

## 总结

本文提出HILL方法，为大规模基础检索模型（如Meta的MoNN）学习一个分层索引结构，通过交叉注意力和残差量化实现高效近似搜索，同时保持检索准确性。

## References

- Efficient Retrieval Scaling with Hierarchical Indexing for Large-Scale Recommendation：[arXiv 2604.12965](https://arxiv.org/abs/2604.12965)

- [PDF源文件](/papers/2604.12965.pdf)
