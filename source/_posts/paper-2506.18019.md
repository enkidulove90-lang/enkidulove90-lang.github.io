---
title: "图与AI智能体：分类、进展与未来机遇"
date: 2025-06-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2506.18019
arxiv_id: "2506.18019"
description: "本文是首篇系统综述图技术与AI智能体交叉领域的论文。"
---

> 论文：[arXiv 2506.18019](https://arxiv.org/abs/2506.18019) · PDF：[本地阅读](/papers/2506.18019.pdf)

本文是首篇系统综述图技术与AI智能体交叉领域的论文。论文提出了一种新颖的分类体系，围绕图学习如何赋能智能体的核心功能——规划、执行、记忆和多智能体协调——展开深入探讨，同时反向分析了AI智能体范式如何增强图学习过程（如图标注、合成与理解）。论文还总结了代表性应用场景、关键挑战和未来研究方向，为下一代AI智能体的发展提供了结构化知识支撑的新思路。

## 研究问题

本文是首篇系统综述图技术与AI智能体交叉领域的论文。论文提出了一种新颖的分类体系，围绕图学习如何赋能智能体的核心功能——规划、执行、记忆和多智能体协调——展开深入探讨，同时反向分析了AI智能体范式如何增强图学习过程（如图标注、合成与理解）。论文还总结了代表性应用场景、关键挑战和未来研究方向，为下一代AI智能体的发展提供了结构化知识支撑的新思路。

## 方法：核心思路与整体框架

本文采用系统性文献综述方法，首先界定AI智能体（RL智能体与LLM智能体）、强化学习、图与图学习等核心概念，然后提出分类体系，按智能体核心功能模块（规划、执行、记忆、多智能体协调）组织图技术的应用综述，并反向讨论智能体对图学习的增强，最后总结应用场景与未来机遇。

![图 1：Fig. 1: An overall illustration of graphs meet AI agents. (1) Graph Methodology: graph data organization and knowledge extraction with graphs. (2) AI Agent Methodology: LLM-based foundation models and RL-based learning paradigms, forming core AI Agent pipelines. (3) AI Agents for Graphs: the powerful capabilities of agents in graph modeling and learning, such as graph annotation, synthesis, and understanding. (4) Graphs for AI Agents: the role and potential of graphs and graph learning in empowering the core functionalities of agents, including agent planning, execution, memory, and multi-agent coordination. (5) Representative Applications. (6) Challenges and Future Opportunities.](/images/papers/2506.18019/279dc08dbddfe0f373d97b0afabee3a5dd63872a1b6522646ef2408b19771d8c.jpg)

*图 1 · 原图说明：Fig. 1: An overall illustration of graphs meet AI agents. (1) Graph Methodology: graph data organization and knowledge extraction with graphs. (2) AI Agent Methodology: LLM-based foundation models and RL-based learning paradigms, forming core AI Agent pipelines. (3) AI Agents for Graphs: the powerful capabilities of agents in graph modeling and learning, such as graph annotation, synthesis, and understanding. (4) Graphs for AI Agents: the role and potential of graphs and graph learning in empowering the core functionalities of agents, including agent planning, execution, memory, and multi-agent coordination. (5) Representative Applications. (6) Challenges and Future Opportunities.*

**图示解释：** 本文采用系统性文献综述方法，首先界定AI智能体（RL智能体与LLM智能体）、强化学习、图与图学习等核心概念，然后提出分类体系，按智能体核心功能模块（规划、执行、记忆、多智能体协调）组织图技术的应用综述，并反向讨论智能体对图学习的增强，最后总结应用场景与未来机遇。

![图 2：Fig. 2: A taxonomy overview of this survey with representative methods on graph-empowered functionalities of AI agents and agent-facilitated graph learning.](/images/papers/2506.18019/a849806c6d14cfcb70db0d5a1801a236bbddc89964fa4a438d827dbe5d548285.jpg)

*图 2 · 原图说明：Fig. 2: A taxonomy overview of this survey with representative methods on graph-empowered functionalities of AI agents and agent-facilitated graph learning.*

**图示解释：** 本文采用系统性文献综述方法，首先界定AI智能体（RL智能体与LLM智能体）、强化学习、图与图学习等核心概念，然后提出分类体系，按智能体核心功能模块（规划、执行、记忆、多智能体协调）组织图技术的应用综述，并反向讨论智能体对图学习的增强，最后总结应用场景与未来机遇。

![图 3：Fig. 3: An illustration of graphs for agent planning.](/images/papers/2506.18019/45f687f3adee6aa94a77f8e29871987f6b9999c1cc1f325e20e64fc5d3facc51.jpg)

*图 3 · 原图说明：Fig. 3: An illustration of graphs for agent planning.*

**图示解释：** 本文采用系统性文献综述方法，首先界定AI智能体（RL智能体与LLM智能体）、强化学习、图与图学习等核心概念，然后提出分类体系，按智能体核心功能模块（规划、执行、记忆、多智能体协调）组织图技术的应用综述，并反向讨论智能体对图学习的增强，最后总结应用场景与未来机遇。

![图 4：Fig. 5: An illustration of graphs for agent memory.](/images/papers/2506.18019/399a889c4ee6a2c235cd2fee1f466551f6044efa080d14934f8a8364470d97a6.jpg)

*图 4 · 原图说明：Fig. 5: An illustration of graphs for agent memory.*

**图示解释：** 本文采用系统性文献综述方法，首先界定AI智能体（RL智能体与LLM智能体）、强化学习、图与图学习等核心概念，然后提出分类体系，按智能体核心功能模块（规划、执行、记忆、多智能体协调）组织图技术的应用综述，并反向讨论智能体对图学习的增强，最后总结应用场景与未来机遇。

## 创新点

1. 首次系统综述图技术与AI智能体的交叉领域：论文填补了现有综述仅关注图在强化学习或LLM中应用的空白，首次全面梳理了图技术如何赋能智能体的规划、执行、记忆和多智能体协调等核心功能。
2. 提出双向增强的新颖分类体系：不仅讨论图如何赋能智能体，还反向探讨智能体范式如何增强图学习（如图标注、合成、理解），强调图与智能体的协同演化与深度融合。
3. 系统梳理图赋能智能体各功能的具体机制：针对规划（任务推理、任务分解、决策搜索）、执行（工具使用、环境交互）、记忆（图结构记忆组织与检索）和多智能体协调分别总结了代表性方法和图结构设计范式。

## 实验：数据、基线与结果

### 数据集与设置

本文为综述论文，不涉及具体实验任务与数据划分。论文在Benchmarking Evaluation部分讨论了现有基准在任务定义和评估数据上的差异，指出统一评估的困难，并呼吁未来基准应融合LLM与RL技术并纳入图模型。原文未披露具体实验数据划分。

### Benchmark 与结果

本文为综述论文，未开展定量实验，因此无具体性能提升数值。论文的核心贡献在于分类体系的构建和文献的系统梳理，而非实验验证。论文指出当前图相关智能体基准仍存在任务定义和评估数据不一致的问题，缺乏图-centric的智能体基准，尤其是在多智能体推理、记忆和大规模动态环境协作等新兴复杂场景中。



### 消融实验

论文未报告独立的消融实验。

## 总结

本文是首篇系统综述图技术与AI智能体交叉领域的论文。

## References

- Graphs Meet AI Agents: Taxonomy, Progress, and Future Opportunities：[arXiv 2506.18019](https://arxiv.org/abs/2506.18019)

- [PDF源文件](/papers/2506.18019.pdf)
