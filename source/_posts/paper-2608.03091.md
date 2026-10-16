---
title: "位置偏差破坏列表式LLM重排序的偏好一致性"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.03091
arxiv_id: "2608.03091"
description: "论文系统研究了列表式LLM重排序器在候选集等价排列下的可靠性问题。"
---

> 论文：[arXiv 2608.03091](https://arxiv.org/abs/2608.03091) · 代码：[GitHub](https://github.com/ejbito/InvariRank) · PDF：[本地阅读](/papers/2608.03091.pdf)

论文系统研究了列表式LLM重排序器在候选集等价排列下的可靠性问题。作者将不同排列下产生的排序视为一个诱导偏好系统的观测，提出了一个多层级评估框架，分别从局部成对偏好、全局偏好结构和列表级输出三个层面刻画候选顺序敏感性。实验覆盖三个LLM、两个数据集和多种列表长度，发现PPI、GPI、LOC三种一致性度量高度一致，但与推荐效果和边际位置曝光偏差可能背离。核心结论是：提升相关性或拉平位置曝光并不足以恢复稳定的成对偏好、全局一致的偏好结构或一致的排序输出，边际曝光校正不足以确立排序函数的有效性。

## 研究问题

论文系统研究了列表式LLM重排序器在候选集等价排列下的可靠性问题。作者将不同排列下产生的排序视为一个诱导偏好系统的观测，提出了一个多层级评估框架，分别从局部成对偏好、全局偏好结构和列表级输出三个层面刻画候选顺序敏感性。实验覆盖三个LLM、两个数据集和多种列表长度，发现PPI、GPI、LOC三种一致性度量高度一致，但与推荐效果和边际位置曝光偏差可能背离。核心结论是：提升相关性或拉平位置曝光并不足以恢复稳定的成对偏好、全局一致的偏好结构或一致的排序输出，边际曝光校正不足以确立排序函数的有效性。

## 方法：核心思路与整体框架

论文将用户上下文和候选集下的列表式重排序建模为排序函数，采样M个候选排列并提取排序，构建诱导偏好系统Q。定义PPI为分桶条件下成对偏好概率的最大最小差，GPI为加权Kemeny秩聚合目标下的近似最优排序分歧，LOC用Kendall's τ衡量采样排序间平均成对一致性，并额外测量top-k曝光随输入位置的变化。

![图 1：PPI and GPI across candidate-list lengths for Llama-3.2-3B-Instruct on MovieLens-32M. Lower values indicate greater preference consistency.](/images/papers/2608.03091/figure_001_figure2_instability_decomposition.png)

*图 1 · 原图说明：PPI and GPI across candidate-list lengths for Llama-3.2-3B-Instruct on MovieLens-32M. Lower values indicate greater preference consistency.*

**图示解释：** 论文将用户上下文和候选集下的列表式重排序建模为排序函数，采样M个候选排列并提取排序，构建诱导偏好系统Q。

![图 2：Top-5 exposure by input position on MovieLens-32M using Llama-3.2-3B-Instruct for list lengths $K \in \{15,25,50\}$.](/images/papers/2608.03091/figure_002_figure1_exposure.png)

*图 2 · 原图说明：Top-5 exposure by input position on MovieLens-32M using Llama-3.2-3B-Instruct for list lengths $K \in \{15,25,50\}$.*

**图示解释：** 论文将用户上下文和候选集下的列表式重排序建模为排序函数，采样M个候选排列并提取排序，构建诱导偏好系统Q。

## 创新点

1. 提出将等价候选排列下的排序视为诱导偏好系统观测的新视角，从排序函数有效性角度而非仅最终列表变化角度研究位置偏差。
2. 设计了多层级一致性评估框架，包括成对偏好不稳定性PPI、全局偏好不一致性GPI和列表级输出一致性LOC，分别刻画局部、全局和输出层面的候选顺序敏感性。
3. 揭示了推荐效果、边际位置曝光偏差与排列一致性之间的背离现象：STELLA_LW获得最高HR@5且曝光曲线更平坦，但PPI、GPI最差、LOC最低。
4. 通过分桶条件化偏好概率和加权Kemeny秩聚合近似求解，使成对与全局一致性度量在有限采样排列下可计算。

## 实验：数据、基线与结果

### 数据集与设置

两阶段推荐流水线中的列表式重排序任务。使用MovieLens-32M和Amazon Books，用户交互按时间排序并时序划分训练集与评估集；每个评估查询用历史交互构建用户历史，留出交互作为相关物品，候选集至少包含一个留出相关物品。第一阶段用LightGCN检索top-K候选，K∈{15,25,50}。

### Benchmark 与结果

在K=25时，STELLA_LW在三个模型和两个数据集上均取得最高HR@5，例如Llama-3B在MovieLens-32M上HR@5为0.5922，但PPI高达0.8331、GPI为0.3648、LOC仅0.1181，一致性最差。SGS取得最低PPI和GPI，如Llama-3B在MovieLens-32M上PPI为0.1972、GPI为0.0586，LOC为0.8268，一致性最好。Bootstrapping相对零样本降低PPI和GPI并提升LOC，例如Llama-3B在MovieLens-32M上PPI从0.4775降至0.2992，LOC从0.6358升至0.7475。PPI、GPI、LOC方法排序在所有模型-数据集组合中高度一致，但与HR@5和边际曝光偏差出现背离。



### 消融实验

论文未报告独立的消融实验。

## 总结

论文系统研究了列表式LLM重排序器在候选集等价排列下的可靠性问题。

## References

- Position Bias Undermines Preference Consistency in Listwise LLM-Based Reranking：[arXiv 2608.03091](https://arxiv.org/abs/2608.03091)

- [代码：GitHub](https://github.com/ejbito/InvariRank)
- [PDF源文件](/papers/2608.03091.pdf)
