---
title: "CoRAL: Collaborative Retrieval-Augmented Large Language Models Improve Long-tail Recommendation"
date: 2024-03-01
year: 2024
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2403.06447
arxiv_id: "2403.06447"
---

## 一、简介

论文针对长尾推荐中数据稀疏和协同信息缺失导致LLM推理与任务不对齐的问题，提出CoRAL框架。该框架通过协同提示将用户-物品交互证据注入LLM提示中，并利用强化学习训练检索策略，以在有限提示容量下找到最小充分的协同信息。同时，利用热门物品数据预训练协同过滤模型为检索策略提供热启动，提升数据效率。实验表明，CoRAL在四个Amazon数据集上显著优于传统协同过滤、去偏方法及LLM基线，平均AUC和F1分别提升21.1%和25.1%。

## 二、论文方法

论文将长尾推荐建模为LLM的自然语言推理任务，通过协同提示将检索到的用户-物品交互证据（包括支持用户和物品及其偏好模式）注入提示中。检索过程被形式化为MDP，使用DDPG算法训练连续动作空间下的检索策略，以边际信息增益为奖励。LLM作为环境的一部分保持冻结，仅训练轻量级检索策略。

## 三、论文里的图与解释

### 图 1

![Conventional item-based LLM reasoning process.](/images/papers/2403.06447/figure_001_fig1_1.png)

**原图说明：** Conventional item-based LLM reasoning process.

**图示解释：** 该图对应论文中的“Conventional item-based LLM reasoning process.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Conventional item-based LLM reasoning process.](/images/papers/2403.06447/figure_002_fig1_2.png)

**原图说明：** Conventional item-based LLM reasoning process.

**图示解释：** 该图对应论文中的“Conventional item-based LLM reasoning process.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Appliances (AUC)](/images/papers/2403.06447/figure_003_figure_5.3_Appliances_AUC.png)

**原图说明：** Appliances (AUC)

**图示解释：** 该图对应论文中的“Appliances (AUC)”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 识别了LLM推理与长尾推荐任务之间的不对齐问题，该问题源于缺乏协同信息，并首次提出通过协同提示注入用户-物品交互证据来对齐LLM推理。
2. 将协同信息检索形式化为序列决策过程，并基于DDPG强化学习框架训练检索策略，以在有限提示容量下寻找最小充分的协同信息，平衡探索与利用。
3. 提出利用热门物品数据预训练协同过滤模型来初始化检索策略，实现热启动，缓解强化学习中的奖励稀疏问题并提升数据效率。

## 五、实验数据集选择

- Amazon Appliances
- Amazon Gift Cards
- Amazon Prime Pantry
- Amazon Software

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

- Amazon Appliances
- Amazon Gift Cards
- Amazon Prime Pantry
- Amazon Software

## 八、总结

论文未提供可独立提取的总结章节。

## References

完整参考文献请见论文原文。

### 在线资源

- [论文：arXiv 2403.06447](https://arxiv.org/abs/2403.06447)
- [PDF源文件](/papers/2403.06447.pdf)
