---
title: "选择性LLM引导正则化"
date: 2025-12-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2512.21526
arxiv_id: "2512.21526"
description: "提出一种模型无关、计算高效的框架S-LLMR，通过可训练的门控机制，仅在LLM预测可靠时（基于用户历史长度、物品流行度、模型不确定性）激活LLM成对排序监督，避免全局蒸馏的弊端。"
---

> 论文：[arXiv 2512.21526](https://arxiv.org/abs/2512.21526) · PDF：[本地阅读](/papers/2512.21526.pdf)

提出一种模型无关、计算高效的框架S-LLMR，通过可训练的门控机制，仅在LLM预测可靠时（基于用户历史长度、物品流行度、模型不确定性）激活LLM成对排序监督，避免全局蒸馏的弊端。实验证明该方法在冷启动和长尾场景下显著优于全局蒸馏基线，且不增加推理成本。

## 研究问题

提出一种模型无关、计算高效的框架S-LLMR，通过可训练的门控机制，仅在LLM预测可靠时（基于用户历史长度、物品流行度、模型不确定性）激活LLM成对排序监督，避免全局蒸馏的弊端。实验证明该方法在冷启动和长尾场景下显著优于全局蒸馏基线，且不增加推理成本。

## 方法：核心思路与整体框架

采用模型无关的训练框架，离线使用GPT-4o-mini生成软相关性分数，在线训练时通过可学习门控网络（输入为冷启动、长尾、不确定性指标）控制成对排序正则化损失的权重，与基础推荐模型联合优化。

![图 1：Illustration of our selective LLM-guided regularization framework. Left: In the offline phase, the LLM is prompted to produce soft relevance scores Right: In the training phase, a base recommender produces prediction scores, and the LLM signals are incorporated through a pairwise ranking regularizer whose contribution is controlled by a gating function.](/images/papers/2512.21526/figure_001_recom2.png)

*图 1 · 原图说明：Illustration of our selective LLM-guided regularization framework. Left: In the offline phase, the LLM is prompted to produce soft relevance scores Right: In the training phase, a base recommender produces prediction scores, and the LLM signals are incorporated through a pairwise ranking regularizer whose contribution is controlled by a gating function.*

**图示解释：** 采用模型无关的训练框架，离线使用GPT-4o-mini生成软相关性分数，在线训练时通过可学习门控网络（输入为冷启动、长尾、不确定性指标）控制成对排序正则化损失的权重，与基础推荐模型联合优化。

## 创新点

1. 创新点1：提出选择性门控机制，利用用户历史长度、物品流行度和模型不确定性三个信号，通过可学习的单层网络动态决定是否激活LLM监督，实现可靠性感知的知识迁移。
2. 创新点2：设计LLM引导的成对排序正则化损失，鼓励推荐模型在LLM可靠时对齐其排序，同时通过门控权重自动抑制不可靠LLM预测的影响。
3. 创新点3：构建离线LLM评分流水线，为冷启动用户和长尾物品生成合成候选集，扩展监督覆盖范围，且不增加在线推理开销。

## 实验：数据、基线与结果

### 数据集与设置

数据集：Amazon Sports & Outdoors、Amazon Beauty、Amazon Toys & Games

### Benchmark 与结果

在DeepFM、xDeepFM、AutoInt、DCNv1、DCNv2、DIN六种骨干上，S-LLMR在三个Amazon域均取得最佳AUC。例如在Sports域，DeepFM上AUC从0.7990提升至0.8176（+1.86%），AutoInt上从0.8003提升至0.8161（+1.58%）。冷启动和长尾场景提升更显著，AUC提升可达+0.02至+0.04。消融实验显示全局LLM损失会损害长尾性能（如Beauty域从0.7702降至0.7330），而门控成对正则化持续提升。

![图 2：AUC improvements in cold-start and long-tail regimes across backbones. \textsc{S-LLMR} delivers the strongest boosts for cold-start users and long-tail items—often exceeding generalrelative improvement.](/images/papers/2512.21526/figure_002_gain_plot.png)

*图 2 · 原图说明：AUC improvements in cold-start and long-tail regimes across backbones. \textsc{S-LLMR} delivers the strongest boosts for cold-start users and long-tail items—often exceeding generalrelative improvement.*

**图示解释：** 在DeepFM、xDeepFM、AutoInt、DCNv1、DCNv2、DIN六种骨干上，S-LLMR在三个Amazon域均取得最佳AUC。

### 消融实验

论文未报告独立的消融实验。

## 总结

提出一种模型无关、计算高效的框架S-LLMR，通过可训练的门控机制，仅在LLM预测可靠时（基于用户历史长度、物品流行度、模型不确定性）激活LLM成对排序监督，避免全局蒸馏的弊端。

## References

- Selective LLM-Guided Regularization for Enhancing Recommendation Models：[arXiv 2512.21526](https://arxiv.org/abs/2512.21526)

- [PDF源文件](/papers/2512.21526.pdf)
