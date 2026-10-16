---
title: "交互式检索增强生成"
date: 2025-10-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2510.27566
arxiv_id: "2510.27566"
description: "本文提出Interact-RAG，一种将LLM智能体从被动的查询发出者转变为检索过程的主动操纵者的新范式。"
---

> 论文：[arXiv 2510.27566](https://arxiv.org/abs/2510.27566) · PDF：[本地阅读](/papers/2510.27566.pdf)

本文提出Interact-RAG，一种将LLM智能体从被动的查询发出者转变为检索过程的主动操纵者的新范式。核心贡献包括：(1) 提出语料交互引擎，赋予智能体多面检索、锚定匹配和上下文塑造等细粒度交互原语，打破了传统RAG的黑盒检索限制；(2) 设计推理增强工作流，通过全局规划器、自适应推理器和执行器实现零样本RAG并合成高质量轨迹；(3) 采用SFT和RL两阶段训练，最终得到一个统一的端到端交互式RAG智能体。在六个基准上，Interact-RAG平均EM得分相对提升22.5%，显著优于现有方法。

## 研究问题

本文提出Interact-RAG，一种将LLM智能体从被动的查询发出者转变为检索过程的主动操纵者的新范式。核心贡献包括：(1) 提出语料交互引擎，赋予智能体多面检索、锚定匹配和上下文塑造等细粒度交互原语，打破了传统RAG的黑盒检索限制；(2) 设计推理增强工作流，通过全局规划器、自适应推理器和执行器实现零样本RAG并合成高质量轨迹；(3) 采用SFT和RL两阶段训练，最终得到一个统一的端到端交互式RAG智能体。在六个基准上，Interact-RAG平均EM得分相对提升22.5%，显著优于现有方法。

## 方法：核心思路与整体框架

本文方法分为三步：1) 构建语料交互引擎，定义三类交互原语（多面检索、锚定匹配、上下文塑造）；2) 设计推理增强工作流（全局规划器、自适应推理器、执行器），用于零样本推理和数据合成；3) 两阶段训练：先使用合成的高质量轨迹进行SFT，再使用GRPO算法进行RL优化，最终得到端到端智能体。

![图 1：A brief demonstration of Interact-RAG. It empowers the agent with fine-grained control over the information-seeking process, leveraging a set of interactive actions. In contrast, conventional RAG is confined to ineffective loops of query issuing.](/images/papers/2510.27566/figure_001_intro.png)

*图 1 · 原图说明：A brief demonstration of Interact-RAG. It empowers the agent with fine-grained control over the information-seeking process, leveraging a set of interactive actions. In contrast, conventional RAG is confined to ineffective loops of query issuing.*

**图示解释：** 本文方法分为三步：1) 构建语料交互引擎，定义三类交互原语（多面检索、锚定匹配、上下文塑造）；2) 设计推理增强工作流（全局规划器、自适应推理器、执行器），用于零样本推理和数据合成；3) 两阶段训练：先使用合成的高质量轨迹进行SFT，再使用GRPO算法进行RL优化，最终得到端到端智能体。

## 创新点

1. 创新点1：提出语料交互引擎（Corpus Interaction Engine），将检索过程透明化。该引擎提供多面检索（语义/精确搜索及加权融合）、锚定匹配（实体聚焦）和上下文塑造（包含/排除文档、调整规模）三类交互原语，使智能体能够超越简单的查询重写，对信息获取过程进行细粒度控制。
2. 创新点2：设计推理增强工作流（Reasoning-Enhanced Workflow），将复杂任务分解为全局规划、自适应推理和执行三个模块。该工作流不仅作为无需训练的零样本解决方案，还能合成高质量的智能体交互轨迹，为后续的端到端训练提供数据基础。
3. 创新点3：采用两阶段训练策略（SFT + RL）训练端到端智能体。首先通过监督微调（SFT）学习基本的交互和推理模式，然后利用基于GRPO的强化学习（RL）进一步优化策略，使智能体能够内化高级策略，实现完全自主的交互式RAG。

## 实验：数据、基线与结果

### 数据集与设置

- Natural Questions (NQ)
- PopQA
- HotpotQA
- 2WikiMultiHopQA (2Wiki)
- MuSiQue
- Bamboogle
- MultiHop-RAG

### Benchmark 与结果

在六个基准上，Interact-RAG（Qwen3-8B）平均EM得分为52.8，F1为62.2，相对第二名Search-R1（EM 43.1）提升22.5%。在多跳QA任务上提升尤为显著，如MuSiQue上EM相对提升36.4%（从25.5到34.8）。在单跳任务NQ和PopQA上，EM分别相对提升11.0%和12.3%。消融实验表明，移除交互范式导致性能下降8.9%-10.9%，移除SFT或RL也分别导致6.8%-21.9%和6.3%-18.6%的性能下降。

![图 2：Comparison of the retrieval iterations and the accuracy.](/images/papers/2510.27566/figure_003_compare_iter.png)

*图 2 · 原图说明：Comparison of the retrieval iterations and the accuracy.*

**图示解释：** 在六个基准上，Interact-RAG（Qwen3-8B）平均EM得分为52.8，F1为62.2，相对第二名Search-R1（EM 43.1）提升22.5%。

![图 3：Action invocation status in different training stages. Measured on the Musique dataset.](/images/papers/2510.27566/figure_005_training-stage.png)

*图 3 · 原图说明：Action invocation status in different training stages. Measured on the Musique dataset.*

**图示解释：** 在六个基准上，Interact-RAG（Qwen3-8B）平均EM得分为52.8，F1为62.2，相对第二名Search-R1（EM 43.1）提升22.5%。

### 消融实验

论文未报告独立的消融实验。

## 总结

本文提出Interact-RAG，一种将LLM智能体从被动的查询发出者转变为检索过程的主动操纵者的新范式。

## References

- Interact-RAG：[arXiv 2510.27566](https://arxiv.org/abs/2510.27566)

- [PDF源文件](/papers/2510.27566.pdf)
