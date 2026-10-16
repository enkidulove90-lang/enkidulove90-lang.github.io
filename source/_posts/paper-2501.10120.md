---
title: "PaSa：学术论文搜索智能体"
date: 2025-01-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2501.10120
arxiv_id: "2501.10120"
description: "本文提出了PaSa，一个由大语言模型驱动的学术论文搜索智能体。"
---

> 论文：[arXiv 2501.10120](https://arxiv.org/abs/2501.10120) · 代码：[GitHub](https://github.com/bytedance/pasa) · PDF：[本地阅读](/papers/2501.10120.pdf)

本文提出了PaSa，一个由大语言模型驱动的学术论文搜索智能体。PaSa通过两个智能体（Crawler和Selector）协同工作，能够自主调用搜索工具、阅读论文、导航引用网络，以全面准确地检索复杂学术查询的相关论文。为了训练PaSa，作者构建了高质量合成数据集AutoScholarQuery（包含35k+查询-论文对）和真实世界基准RealScholarQuery。实验表明，基于7B模型的PaSa在召回率和精确率上显著超越了包括GPT-4o智能体、Google搜索和ChatGPT在内的所有基线方法，展示了强化学习训练在学术搜索任务中的巨大潜力。

## 研究问题

本文提出了PaSa，一个由大语言模型驱动的学术论文搜索智能体。PaSa通过两个智能体（Crawler和Selector）协同工作，能够自主调用搜索工具、阅读论文、导航引用网络，以全面准确地检索复杂学术查询的相关论文。为了训练PaSa，作者构建了高质量合成数据集AutoScholarQuery（包含35k+查询-论文对）和真实世界基准RealScholarQuery。实验表明，基于7B模型的PaSa在召回率和精确率上显著超越了包括GPT-4o智能体、Google搜索和ChatGPT在内的所有基线方法，展示了强化学习训练在学术搜索任务中的巨大潜力。

## 方法：核心思路与整体框架

PaSa采用双智能体架构：Crawler执行马尔可夫决策过程，通过[Search]、[Expand]和[Stop]三个动作自主搜索和扩展论文队列；Selector则基于论文标题和摘要输出决策令牌和推理依据。Crawler的训练分两阶段：先通过模仿学习初始化策略，再使用会话级PPO进行强化学习优化，其中Selector作为辅助奖励模型缓解稀疏奖励问题。

![图 1：Table 16: The prompt used with GPT-4o to automatically synthesize AutoScholarQuery.](/images/papers/2501.10120/27973c6c03b5e82525acf0e039c19c69d707f94a49d77a1d23cb3a5750c721ef.jpg)

*图 1 · 原图说明：Table 16: The prompt used with GPT-4o to automatically synthesize AutoScholarQuery.*

**图示解释：** PaSa采用双智能体架构：Crawler执行马尔可夫决策过程，通过[Search]、[Expand]和[Stop]三个动作自主搜索和扩展论文队列；Selector则基于论文标题和摘要输出决策令牌和推理依据。

## 创新点

1. 创新点1：提出双智能体协作架构（Crawler与Selector），Crawler负责最大化召回率，通过搜索和引用扩展自主收集论文；Selector负责精确筛选，判断论文是否满足查询要求，模拟了人类研究者的搜索行为。
2. 创新点2：设计了会话级PPO（Proximal Policy Optimization）强化学习训练方法，通过将长轨迹分割为以[Stop]动作结束的会话，并引入跨会话折扣因子和Selector作为辅助奖励模型，有效解决了学术搜索任务中的稀疏奖励和长轨迹挑战。
3. 创新点3：构建了高质量合成数据集AutoScholarQuery和真实世界基准RealScholarQuery。AutoScholarQuery从顶级AI会议论文的Related Work部分自动生成细粒度查询-论文对，RealScholarQuery则包含50个真实研究查询及其人工标注的相关论文，为学术搜索研究提供了标准化评估平台。

## 实验：数据、基线与结果

### 数据集与设置

- AutoScholarQuery
- RealScholarQuery

### Benchmark 与结果

在AutoScholarQuery测试集上，PaSa-7b相比最强基线Google with GPT-4o，Recall@20提升34.05%，Recall@50提升39.36%；相比PaSa-GPT-4o，召回率提升11.12%，精确率相当。在RealScholarQuery上，PaSa-7b超越Google with GPT-4o，Recall@20提升37.78%，Recall@50提升39.90%；超越PaSa-GPT-4o，召回率提升30.36%，精确率提升4.25%。Selector的F1分数达85%，超过GPT-4o的80%和Qwen-2.5-7b的55%。



### 消融实验

论文未报告独立的消融实验。

## 总结

本文提出了PaSa，一个由大语言模型驱动的学术论文搜索智能体。

## References

- PaSa: An LLM Agent for Comprehensive Academic Paper Search：[arXiv 2501.10120](https://arxiv.org/abs/2501.10120)

- [代码：GitHub](https://github.com/bytedance/pasa)
- [PDF源文件](/papers/2501.10120.pdf)
