---
title: "AstaBench：AI智能体科学基准"
date: 2025-10-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2510.21652
arxiv_id: "2510.21652"
description: "本文提出了AstaBench，一个用于严格评估AI智能体在科学研究任务上表现的基准套件。"
---

> 论文：[arXiv 2510.21652](https://arxiv.org/abs/2510.21652) · 代码：[GitHub](https://github.com/UKGovernmentBEIS/inspect) · 代码：[GitHub](https://github.com/laude-institute/terminal-bench) · 代码：[GitHub](https://github.com/mlfoundations/evalchemy) · 代码：[GitHub](https://github.com/princeton-pli/hal-harness) · 代码：[GitHub](https://github.com/soheeyang/unified-prompt-selection) · PDF：[本地阅读](/papers/2510.21652.pdf)

本文提出了AstaBench，一个用于严格评估AI智能体在科学研究任务上表现的基准套件。它包含超过2400个问题，覆盖文献理解、编码、数据分析、端到端发现等全科研流程。AstaBench提供了标准化的任务接口、可控的文献检索环境（Asta Environment），并引入成本感知的评估方法，首次在排行榜中控制工具使用和推理成本等混淆变量。论文还发布了包含22类、57个智能体的最全面基线套件，揭示了当前科研智能体在编码和端到端发现等任务上远未解决的现状。

## 研究问题

本文提出了AstaBench，一个用于严格评估AI智能体在科学研究任务上表现的基准套件。它包含超过2400个问题，覆盖文献理解、编码、数据分析、端到端发现等全科研流程。AstaBench提供了标准化的任务接口、可控的文献检索环境（Asta Environment），并引入成本感知的评估方法，首次在排行榜中控制工具使用和推理成本等混淆变量。论文还发布了包含22类、57个智能体的最全面基线套件，揭示了当前科研智能体在编码和端到端发现等任务上远未解决的现状。

## 方法：核心思路与整体框架

论文采用基准测试方法论。首先定义严格原则，然后构建包含11个基准、覆盖4大科研类别（文献理解、编码与执行、数据分析、端到端发现）的AstaBench套件。通过标准化任务接口和Asta Environment实现可控评估。使用Inspect框架记录模型使用量以计算成本，并基于此构建成本感知的排行榜。最后，对22类、57个智能体进行大规模实验，分析性能与成本。

![图 1：Figure 4: Score vs. cost analysis for Literature Understanding QA benchmarks (Table 13). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (ScholarQA-CS2, LitQA2-FullText). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.](/images/papers/2510.21652/d56e7480c924a302120c09584c6cbcc8c29c7ac9838e8ceb69979c8f7eddeffe.jpg)

*图 1 · 原图说明：Figure 4: Score vs. cost analysis for Literature Understanding QA benchmarks (Table 13). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (ScholarQA-CS2, LitQA2-FullText). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.*

**图示解释：** 最佳开源智能体Asta v0综合得分53.0%，远超其他通用智能体（如ReAct with gpt-5为44.0%）。

## 创新点

1. 创新点1：提出严格的智能体基准测试原则，并基于此构建AstaBench，解决了现有基准缺乏标准化环境、未控制混淆变量（如工具、成本）、任务接口不通用等问题。
2. 创新点2：构建了首个生产级、可控的科学文献检索环境（Asta Environment），允许在相同文献语料库上公平比较不同智能体的核心能力（如规划、工具调用），隔离信息访问差异。
3. 创新点3：引入成本感知的评估与排行榜（AstaBench Leaderboard），通过Pareto前沿展示准确率与推理成本之间的权衡，并首次在排行榜中控制工具使用和开放性等混淆变量。

## 实验：数据、基线与结果

### 数据集与设置

- PaperFindingBench
- LitQA2-FullText-Search
- ScholarQA-CS2
- ArxivDIGESTables-Clean
- SUPER-Expert
- CORE-Bench-Hard
- DS-1000
- DiscoveryBench
- E2E-Bench
- E2E-Bench-Hard

### Benchmark 与结果

最佳开源智能体Asta v0综合得分53.0%，远超其他通用智能体（如ReAct with gpt-5为44.0%）。在文献理解任务上，Asta Scholar QA等专用智能体得分约85-88%，表现较好。但在编码任务（SUPER-Expert）上，最佳ReAct with gpt-5仅得41.1%；数据分析（DiscoveryBench）最高仅33.7%；端到端发现任务（E2E-Bench-Hard）平均步骤完成率约70%，但完整实验成功率仅约3-5%。成本方面，ReAct with gpt-5-mini以$0.04/问题成本获得32%综合得分，性价比最优。

![图 2：Figure 8: Score vs. cost analysis for End-to-End Discovery benchmarks (Table 17). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (E2E-Bench, E2E-Bench-Hard). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.](/images/papers/2510.21652/f58ba4301a10798320cf700d000c1356314d661dd11c9e3d959f875fa449509d.jpg)

*图 2 · 原图说明：Figure 8: Score vs. cost analysis for End-to-End Discovery benchmarks (Table 17). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (E2E-Bench, E2E-Bench-Hard). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.*

**图示解释：** 最佳开源智能体Asta v0综合得分53.0%，远超其他通用智能体（如ReAct with gpt-5为44.0%）。

### 消融实验

论文未报告独立的消融实验。

## 总结

本文提出了AstaBench，一个用于严格评估AI智能体在科学研究任务上表现的基准套件。

## References

- AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite：[arXiv 2510.21652](https://arxiv.org/abs/2510.21652)

- [代码：GitHub](https://github.com/UKGovernmentBEIS/inspect)
- [代码：GitHub](https://github.com/laude-institute/terminal-bench)
- [代码：GitHub](https://github.com/mlfoundations/evalchemy)
- [代码：GitHub](https://github.com/princeton-pli/hal-harness)
- [代码：GitHub](https://github.com/soheeyang/unified-prompt-selection)
- [PDF源文件](/papers/2510.21652.pdf)
