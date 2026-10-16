---
title: "CoRAL：协同检索增强大语言模型提升长尾推荐"
date: 2024-03-01
year: 2024
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2403.06447
arxiv_id: "2403.06447"
description: "论文针对长尾推荐中数据稀疏和协同信息缺失导致LLM推理与任务不对齐的问题，提出CoRAL框架。"
---

> 论文：[arXiv 2403.06447](https://arxiv.org/abs/2403.06447) · PDF：[本地阅读](/papers/2403.06447.pdf)

论文针对长尾推荐中数据稀疏和协同信息缺失导致LLM推理与任务不对齐的问题，提出CoRAL框架。该框架通过协同提示将用户-物品交互证据注入LLM提示中，并利用强化学习训练检索策略，以在有限提示容量下找到最小充分的协同信息。同时，利用热门物品数据预训练协同过滤模型为检索策略提供热启动，提升数据效率。实验表明，CoRAL在四个Amazon数据集上显著优于传统协同过滤、去偏方法及LLM基线，平均AUC和F1分别提升21.1%和25.1%。

## 研究问题

论文针对长尾推荐中数据稀疏和协同信息缺失导致LLM推理与任务不对齐的问题，提出CoRAL框架。该框架通过协同提示将用户-物品交互证据注入LLM提示中，并利用强化学习训练检索策略，以在有限提示容量下找到最小充分的协同信息。同时，利用热门物品数据预训练协同过滤模型为检索策略提供热启动，提升数据效率。实验表明，CoRAL在四个Amazon数据集上显著优于传统协同过滤、去偏方法及LLM基线，平均AUC和F1分别提升21.1%和25.1%。

## 方法：核心思路与整体框架

论文将长尾推荐建模为LLM的自然语言推理任务，通过协同提示将检索到的用户-物品交互证据（包括支持用户和物品及其偏好模式）注入提示中。检索过程被形式化为MDP，使用DDPG算法训练连续动作空间下的检索策略，以边际信息增益为奖励。LLM作为环境的一部分保持冻结，仅训练轻量级检索策略。

![图 1：Conventional item-based LLM reasoning process.](/images/papers/2403.06447/figure_001_fig1_1.png)

*图 1 · 原图说明：Conventional item-based LLM reasoning process.*

**图示解释：** 论文将长尾推荐建模为LLM的自然语言推理任务，通过协同提示将检索到的用户-物品交互证据（包括支持用户和物品及其偏好模式）注入提示中。

![图 2：Conventional item-based LLM reasoning process.](/images/papers/2403.06447/figure_002_fig1_2.png)

*图 2 · 原图说明：Conventional item-based LLM reasoning process.*

**图示解释：** 论文将长尾推荐建模为LLM的自然语言推理任务，通过协同提示将检索到的用户-物品交互证据（包括支持用户和物品及其偏好模式）注入提示中。

## 创新点

1. 识别了LLM推理与长尾推荐任务之间的不对齐问题，该问题源于缺乏协同信息，并首次提出通过协同提示注入用户-物品交互证据来对齐LLM推理。
2. 将协同信息检索形式化为序列决策过程，并基于DDPG强化学习框架训练检索策略，以在有限提示容量下寻找最小充分的协同信息，平衡探索与利用。
3. 提出利用热门物品数据预训练协同过滤模型来初始化检索策略，实现热启动，缓解强化学习中的奖励稀疏问题并提升数据效率。

## 实验：数据、基线与结果

### 数据集与设置

在四个Amazon产品数据集上进行长尾推荐任务，预测用户对长尾物品的偏好（二分类）。数据集包含Appliances（602,777条评论）、Gift Cards（147,194条）、Prime Pantry（471,614条）、Software（459,436条）。按80/20规则定义长尾物品（后80%），过滤交互少于5次的用户和物品。使用70%长尾数据加全部非长尾数据作为训练集，剩余30%长尾数据均分为验证集和测试集。原始5分制评分以3为阈值转为二分类标签。

### Benchmark 与结果

CoRAL在四个数据集上平均AUC和F1分别达到93.99和82.42（CoRAL-DFM），相比最佳基线CausE（AUC 74.71，F1 67.02）分别提升约25.8%和23.0%。具体地，CoRAL-AFM在Gift Cards上AUC达98.99，CoRAL-WDL在Software上F1达91.18。即使随机检索的CoRAL-random在AUC上仍优于LLM-Language，表明协同信息的重要性。在线强化学习使CoRAL相比LLM-Language平均AUC和F1分别提升21.1%和25.1%。

![图 3：Appliances (AUC)](/images/papers/2403.06447/figure_003_figure_5.3_Appliances_AUC.png)

*图 3 · 原图说明：Appliances (AUC)*

**图示解释：** CoRAL在四个数据集上平均AUC和F1分别达到93.99和82.42（CoRAL-DFM），相比最佳基线CausE（AUC 74.71，F1 67.02）分别提升约25.8%和23.0%。

### 消融实验

论文未报告独立的消融实验。

## 总结

论文针对长尾推荐中数据稀疏和协同信息缺失导致LLM推理与任务不对齐的问题，提出CoRAL框架。

## References

- CoRAL: Collaborative Retrieval-Augmented Large Language Models Improve Long-tail Recommendation：[arXiv 2403.06447](https://arxiv.org/abs/2403.06447)

- [PDF源文件](/papers/2403.06447.pdf)
