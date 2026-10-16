---
title: "融合逐层出口赋能紧凑LLM推荐"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.17316
arxiv_id: "2608.17316"
description: "论文提出FLEXRec，一种基于判别式LLM推荐范式的逐层出口融合框架，旨在解决紧凑LLM在序列推荐中表达能力不足的问题。"
---

> 论文：[arXiv 2608.17316](https://arxiv.org/abs/2608.17316) · 代码：[GitHub](https://github.com/xurong-liang/FLEXRec) · PDF：[本地阅读](/papers/2608.17316.pdf)

论文提出FLEXRec，一种基于判别式LLM推荐范式的逐层出口融合框架，旨在解决紧凑LLM在序列推荐中表达能力不足的问题。FLEXRec在LLM每一层后插入预测头（出口），将各层用户偏好嵌入生成的评分分布进行融合，以补偿小模型参数容量的限制。同时设计自适应连续路由器（AC-Router），根据用户序列复杂度动态选择激活的出口数量与身份，并引入target-k hinge loss等联合优化目标控制路由稀疏性。在三个真实数据集上，使用Qwen 3 1.7B和Llama 3.2 3B紧凑骨干，FLEXRec在紧凑骨干方法中达到最优精度，且推理延迟仅比E4SRec增加不到1ms。

## 研究问题

论文提出FLEXRec，一种基于判别式LLM推荐范式的逐层出口融合框架，旨在解决紧凑LLM在序列推荐中表达能力不足的问题。FLEXRec在LLM每一层后插入预测头（出口），将各层用户偏好嵌入生成的评分分布进行融合，以补偿小模型参数容量的限制。同时设计自适应连续路由器（AC-Router），根据用户序列复杂度动态选择激活的出口数量与身份，并引入target-k hinge loss等联合优化目标控制路由稀疏性。在三个真实数据集上，使用Qwen 3 1.7B和Llama 3.2 3B紧凑骨干，FLEXRec在紧凑骨干方法中达到最优精度，且推理延迟仅比E4SRec增加不到1ms。

## 方法：核心思路与整体框架

FLEXRec采用判别式LLM推荐范式，以E4SRec为基座，在LLM每层后插入预测头形成多层出口。AC-Router基于第一层响应token嵌入计算路由logits，经条件偏移约束和ReLU激活生成稀疏门控权重，归一化后融合激活出口的评分分布。训练分三阶段：Stage 1用交叉熵损失微调LoRA和最终出口；Stage 2冻结骨干训练中间出口；Stage 3冻结全部骨干和出口，仅训练路由器投影矩阵，联合优化推荐损失、负载均衡损失、target-k hinge损失和Z-loss。

![图 3：Overview of the FLEXRec framework and its three-stage training. Stage 1 trains the base components via $\mathcal{L}_{rec}$. Stage 2 warms up intermediate exits $\mathcal{H}_{inter}$ via $\mathcal{L}_{inter}$. Stage 3 optimizes the AC-Router using $\mathcal{L}_{rec}$ alongside router-specific loss terms ($\mathcal{L}_{LB}$, $\mathcal{L}_{Hinge}$, $\mathcal{L}_Z$). In the given sequence example, solid green arrows depict active routing weights assigned by the AC-Router, whereas dotted arrows indicate unselected exits that do not contribute to the final fused distribution $\mathbf{O}^{fused}$.](/images/papers/2608.17316/figure_017_framework_overview-crop.png)

*图 3 · 原图说明：Overview of the FLEXRec framework and its three-stage training. Stage 1 trains the base components via $\mathcal{L}_{rec}$. Stage 2 warms up intermediate exits $\mathcal{H}_{inter}$ via $\mathcal{L}_{inter}$. Stage 3 optimizes the AC-Router using $\mathcal{L}_{rec}$ alongside router-specific loss terms ($\mathcal{L}_{LB}$, $\mathcal{L}_{Hinge}$, $\mathcal{L}_Z$). In the given sequence example, solid green arrows depict active routing weights assigned by the AC-Router, whereas dotted arrows indicate unselected exits that do not contribute to the final fused distribution $\mathbf{O}^{fused}$.*

**图示解释：** FLEXRec采用判别式LLM推荐范式，以E4SRec为基座，在LLM每层后插入预测头形成多层出口。

## 创新点

1. 提出从静态单出口LLM推荐器向动态多层融合范式的转变，通过自适应集成不同LLM传播深度的预测评分分布，有效补偿紧凑LLM骨干有限的语义建模能力。
2. 设计自适应连续路由器（AC-Router），采用连续ReLU路由机制，根据每个用户序列的复杂度动态决定激活哪些出口以及激活多少个出口，实现输入自适应的计算深度分配。
3. 提出target-k hinge loss，通过连续Sigmoid代理和不对称双侧铰链损失，软性惩罚激活出口数量偏离目标范围[1, k]的情况，在无额外参数开销下实现路由稀疏性控制。
4. 设计三阶段训练流程：先训练LLM推荐骨干，再独立训练中间出口，最后冻结骨干仅训练AC-Router，使路由器梯度纯粹反映融合策略，支持灵活部署不同target-k的路由器共享同一冻结骨干。

## 实验：数据、基线与结果

### 数据集与设置

序列推荐任务，目标是给定用户历史交互序列预测下一物品并生成Top-N排序。使用Toys（19,412用户，11,924物品，167,597交互，稀疏度99.93%）、Beauty（22,363用户，12,101物品，198,502交互，99.93%）、Yelp（30,431用户，20,033物品，316,354交互，99.95%）三个数据集。采用5-core物品过滤，leave-one-out划分：最后一项为测试，倒数第二项为验证，其余为训练。

### Benchmark 与结果

FLEXRec在紧凑骨干方法中一致取得最佳性能，在N=10指标上超越所有对比方法。尽管骨干规模约为Skyline的一半，FLEXRec在Beauty（两种骨干）和Yelp（Qwen骨干）等设置上甚至超越更大骨干的Skyline。FLEXRec的自适应融合在所有评估设置中均优于最佳单出口。与MoE变体相比，SparseToken和DynamicMoE在更稀疏的Yelp数据集上表现不佳。推理效率方面，FLEXRec仅比E4SRec增加不到1ms延迟，远低于生成式方法（如SETRec）。消融实验表明，禁用任一损失项均导致性能下降，验证了三个损失项的必要性。

![图 1：Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.](/images/papers/2608.17316/figure_001_Toys-Qwen_boxplot.png)

*图 1 · 原图说明：Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.*

**图示解释：** FLEXRec在紧凑骨干方法中一致取得最佳性能，在N=10指标上超越所有对比方法。

![图 2：Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.](/images/papers/2608.17316/figure_002_Toys-Llama_boxplot.png)

*图 2 · 原图说明：Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.*

**图示解释：** FLEXRec在紧凑骨干方法中一致取得最佳性能，在N=10指标上超越所有对比方法。

### 消融实验

传统序列模型：SASRec、BERT4Rec。LLM-based推荐器：E4SRec（静态单出口对照）、SPRec、SETRec、LLM-SRec、HUM。MoE路由替代方案：SparseToken（离散Top-k路由）、DynamicMoE（阈值动态路由）、LD-MoLE（单纯形投影连续路由）。Skyline：E4SRec使用更大骨干（Qwen 3 4B、Llama 3.1 8B）。消融实验：分别禁用L_Hinge、L_LB、L_Z三个损失项。

## 总结

论文提出FLEXRec，一种基于判别式LLM推荐范式的逐层出口融合框架，旨在解决紧凑LLM在序列推荐中表达能力不足的问题。

## References

- Empowering Compact LLMs with Fusion of Layer-wise Exits for Recommendation：[arXiv 2608.17316](https://arxiv.org/abs/2608.17316)

- [代码：GitHub](https://github.com/xurong-liang/FLEXRec)
- [PDF源文件](/papers/2608.17316.pdf)
