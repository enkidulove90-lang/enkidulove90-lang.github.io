---
title: "AgentX: Towards Agent-Driven Self-Iteration of Industrial Recommender Systems"
date: 2026-06-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2606.26859
arxiv_id: "2606.26859"
---

## 一、简介

本文提出并部署了AgentX，一个面向工业推荐系统的多智能体自动化开发框架。AgentX构建了从想法生成、代码开发、在线A/B实验到知识积累的完整闭环，实现了推荐算法的自主迭代。在快手App三周部署中，3个AgentX worker将374个想法转化为10个可上线实验，吞吐量每周翻倍，带来0.561%用户时长提升和超1亿人民币年化收入。该系统不仅自动化了策略迭代，还扩展到模型研究，实现了论文复现、模块消融和跨论文架构组合。

## 二、论文方法

AgentX采用多智能体协同架构：Brainstorm Agent通过证据加权生成可执行提案；Developing Agent基于仓库感知生成生产级代码；Evaluation Agent进行安全在线部署和A/B判断；Harness Evolution层通过SGPO从执行轨迹中学习，持续优化智能体行为。系统形成闭环，每次实验的轨迹数据都用于改进后续迭代。

## 三、论文里的图与解释

### 图 1

![Brainstorm Agent workflow. Historical experiment memory and system knowledge are organized into Experiment KB and System KB. The Brainstorm Agent clarifies the task, produces candidate ideas, validates them with review and boundary checks, and materializes accepted ideas for downstream execution.](/images/papers/2606.26859/figure_001_agentx_brainstorm_overview.png)

**原图说明：** Brainstorm Agent workflow. Historical experiment memory and system knowledge are organized into Experiment KB and System KB. The Brainstorm Agent clarifies the task, produces candidate ideas, validates them with review and boundary checks, and materializes accepted ideas for downstream execution.

**图示解释：** 该图对应论文中的“Brainstorm Agent workflow. Historical experiment memory and system knowledge are organized into Experiment KB and System KB. The Brainstorm Agent clarifies the task, produces candidate ideas, validates them with review and boundary checks, and materializes accepted ideas for downstream execution.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Architecture of the Developing Agent for the online strategy track. The central pipeline transforms a strategy specification into a validated code submission through four sequential stages: abstracting requirements, orchestrating the implementation plan, executing atomic sub-requirements, and assembling with validation. The case toolbox (right) injects constraint checks and context retrieval into the pipeline, comprising schema-retrieval tools for user-, context-, and item-side feature structs, a ranking DSL checker, a C++ syntax checker, and a lightweight static linter that accumulates project-specific rules automatically.](/images/papers/2606.26859/figure_002_CODE.png)

**原图说明：** Architecture of the Developing Agent for the online strategy track. The central pipeline transforms a strategy specification into a validated code submission through four sequential stages: abstracting requirements, orchestrating the implementation plan, executing atomic sub-requirements, and assembling with validation. The case toolbox (right) injects constraint checks and context retrieval into the pipeline, comprising schema-retrieval tools for user-, context-, and item-side feature structs, a ranking DSL checker, a C++ syntax checker, and a lightweight static linter that accumulates project-specific rules automatically.

**图示解释：** 该图对应论文中的“Architecture of the Developing Agent for the online strategy track. The central pipeline transforms a strategy specification into a validated code submission through four sequential stages: abstracting requirements, orchestrating the implementation plan, executing atomic sub-requirements, and assembling with validation. The case toolbox (right) injects constraint checks and context retrieval into the pipeline, comprising schema-retrieval tools for user-, context-, and item-side feature structs, a ranking DSL checker, a C++ syntax checker, and a lightweight static linter that accumulates project-specific rules automatically.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Architecture of the Coding Agent for the offline model track. The central pipeline (bottom) turns a model-architecture proposal into a trustworthy training conclusion through four sequential stages: declaring a policy, implementing and verifying the code change, running training and evaluation, and reviewing the result with causal-chain attribution. The verification-and-experts harness (top) injects checks and evidence through an isolated expert panel voting for consensus, a change verifier that confirms the code matches the policy, a metric reader that extracts AUC from training logs, and an attribution check that adjudicates whether each causal-chain link holds.](/images/papers/2606.26859/figure_003_Model_Developing.png)

**原图说明：** Architecture of the Coding Agent for the offline model track. The central pipeline (bottom) turns a model-architecture proposal into a trustworthy training conclusion through four sequential stages: declaring a policy, implementing and verifying the code change, running training and evaluation, and reviewing the result with causal-chain attribution. The verification-and-experts harness (top) injects checks and evidence through an isolated expert panel voting for consensus, a change verifier that confirms the code matches the policy, a metric reader that extracts AUC from training logs, and an attribution check that adjudicates whether each causal-chain link holds.

**图示解释：** 该图对应论文中的“Architecture of the Coding Agent for the offline model track. The central pipeline (bottom) turns a model-architecture proposal into a trustworthy training conclusion through four sequential stages: declaring a policy, implementing and verifying the code change, running training and evaluation, and reviewing the result with causal-chain attribution. The verification-and-experts harness (top) injects checks and evidence through an isolated expert panel voting for consensus, a change verifier that confirms the code matches the policy, a metric reader that extracts AUC from training logs, and an attribution check that adjudicates whether each causal-chain link holds.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出完整的工业级闭环迭代框架，包含Brainstorm、Developing、Evaluation和Harness Evolution四个智能体，实现从模糊意图到在线收益的端到端自动化。
2. 创新点2：设计基于语义梯度的提示优化方法（SGPO），通过执行轨迹数据持续优化智能体自身，使系统具备自我进化能力。
3. 创新点3：构建证据加权提案生成机制，融合实验知识库、系统知识库、数据分析和模型研究四类证据源，确保提案的可行性和业务价值。

## 五、实验数据集选择

- 快手主Feed推荐场景
- 快手生活服务推荐场景

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

- 快手主Feed推荐场景
- 快手生活服务推荐场景

## 八、总结

论文未提供可独立提取的总结章节。

## References

完整参考文献请见论文原文。

### 在线资源

- [论文：arXiv 2606.26859](https://arxiv.org/abs/2606.26859)
- [PDF源文件](/papers/2606.26859.pdf)
