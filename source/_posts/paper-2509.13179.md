---
title: "基于BPE令牌级嵌入的冷启动推荐"
date: 2025-09-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2509.13179
arxiv_id: "2509.13179"
description: "提出一种利用字节对编码（BPE）和预训练大语言模型（LLM）进行子词级嵌入初始化的冷启动推荐方法。"
---

> 论文：[arXiv 2509.13179](https://arxiv.org/abs/2509.13179) · PDF：[本地阅读](/papers/2509.13179.pdf)

提出一种利用字节对编码（BPE）和预训练大语言模型（LLM）进行子词级嵌入初始化的冷启动推荐方法。该方法通过将文本元数据分解为BPE子词令牌，并聚合其LLM嵌入作为冷启动实体（新用户/物品）的稠密语义先验，在无需任何交互历史的情况下即可实现有效的零样本推荐。实验证明，该方法在Recall@k和NDCG@k指标上显著优于基于句子级嵌入的基线方法，尤其在多语言和稀疏输入场景下表现突出，且计算效率高，易于集成到现有推荐系统中。

## 研究问题

提出一种利用字节对编码（BPE）和预训练大语言模型（LLM）进行子词级嵌入初始化的冷启动推荐方法。该方法通过将文本元数据分解为BPE子词令牌，并聚合其LLM嵌入作为冷启动实体（新用户/物品）的稠密语义先验，在无需任何交互历史的情况下即可实现有效的零样本推荐。实验证明，该方法在Recall@k和NDCG@k指标上显著优于基于句子级嵌入的基线方法，尤其在多语言和稀疏输入场景下表现突出，且计算效率高，易于集成到现有推荐系统中。

## 方法：核心思路与整体框架

采用BPE分词器将文本元数据（如标题、描述）分解为子词令牌序列，然后使用预训练且冻结的LLM（如DistilBERT）为每个令牌提取上下文嵌入，最后通过平均池化或注意力加权池化聚合所有令牌嵌入，得到用户或物品的最终表示向量。该向量直接用于与现有协同过滤模型中的实体嵌入进行点积计算推荐分数，并使用BPR损失进行优化。

![图 2：Figure 1: Cold-Start Recommendations](/images/papers/2509.13179/p3_caption_2.png)

*图 2 · 原图说明：Figure 1: Cold-Start Recommendations*

**图示解释：** 采用BPE分词器将文本元数据（如标题、描述）分解为子词令牌序列，然后使用预训练且冻结的LLM（如DistilBERT）为每个令牌提取上下文嵌入，最后通过平均池化或注意力加权池化聚合所有令牌嵌入，得到用户或物品的最终表示向量。

![图 3：Figure 2: t-SNE projection of Cold-start Items](/images/papers/2509.13179/p4_caption_3.png)

*图 3 · 原图说明：Figure 2: t-SNE projection of Cold-start Items*

**图示解释：** 采用BPE分词器将文本元数据（如标题、描述）分解为子词令牌序列，然后使用预训练且冻结的LLM（如DistilBERT）为每个令牌提取上下文嵌入，最后通过平均池化或注意力加权池化聚合所有令牌嵌入，得到用户或物品的最终表示向量。

## 创新点

1. 创新点1：提出BPE令牌级嵌入初始化策略，利用子词分解捕获细粒度语义，克服了传统句子级嵌入丢失关键子词信息的缺陷。
2. 创新点2：设计了一种与模型架构无关的轻量级方法，通过冻结LLM编码器进行一次性嵌入计算，实现了低延迟、可扩展的冷启动推荐。
3. 创新点3：在多种稀疏度（10%、30%、50%）和跨领域（电影、书籍）的严格冷启动设定下，验证了该方法相比图嵌入、元学习等基线方法的鲁棒性和泛化能力。

## 实验：数据、基线与结果

### 数据集与设置

数据集：MovieLens 1M、Amazon Books；划分：90/10

### Benchmark 与结果

在MovieLens和Amazon Books数据集上，BPE+LLM方法在Recall@10、NDCG@10和Hit Rate@10指标上均大幅领先。例如，在MovieLens上，Recall@10达到0.68，比句子嵌入基线（0.56）提升约21.4%，比随机初始化（0.41）提升65.9%；NDCG@10达到0.62，比句子嵌入（0.48）提升29.2%。在稀疏度高达50%的极端冷启动场景下，该方法仍能保持稳定性能，而图嵌入和属性扩展基线性能则急剧下降。

![图 1：Table 1: Performance Comparison Across Methods on Retrieval Metrics](/images/papers/2509.13179/p3_caption_1.png)

*图 1 · 原图说明：Table 1: Performance Comparison Across Methods on Retrieval Metrics*

**图示解释：** 在MovieLens和Amazon Books数据集上，BPE+LLM方法在Recall@10、NDCG@10和Hit Rate@10指标上均大幅领先。

### 消融实验

论文未报告独立的消融实验。

## 总结

提出一种利用字节对编码（BPE）和预训练大语言模型（LLM）进行子词级嵌入初始化的冷启动推荐方法。

## References

- Efficient Cold-Start Recommendation via BPE Token-Level Embedding Initialization with LLM：[arXiv 2509.13179](https://arxiv.org/abs/2509.13179)

- [PDF源文件](/papers/2509.13179.pdf)
