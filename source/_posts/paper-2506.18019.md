---
title: "Graphs Meet AI Agents: Taxonomy, Progress, and Future Opportunities"
date: 2025-06-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2506.18019
arxiv_id: "2506.18019"
---

## 一、简介

本文是首篇系统综述图技术与AI智能体交叉领域的论文。论文提出了一种新颖的分类体系，围绕图学习如何赋能智能体的核心功能——规划、执行、记忆和多智能体协调——展开深入探讨，同时反向分析了AI智能体范式如何增强图学习过程（如图标注、合成与理解）。论文还总结了代表性应用场景、关键挑战和未来研究方向，为下一代AI智能体的发展提供了结构化知识支撑的新思路。

## 二、论文方法

本文采用系统性文献综述方法，首先界定AI智能体（RL智能体与LLM智能体）、强化学习、图与图学习等核心概念，然后提出分类体系，按智能体核心功能模块（规划、执行、记忆、多智能体协调）组织图技术的应用综述，并反向讨论智能体对图学习的增强，最后总结应用场景与未来机遇。

## 三、论文里的图与解释

### 图 1

![Fig. 1: An overall illustration of graphs meet AI agents. (1) Graph Methodology: graph data organization and knowledge extraction with graphs. (2) AI Agent Methodology: LLM-based foundation models and RL-based learning paradigms, forming core AI Agent pipelines. (3) AI Agents for Graphs: the powerful capabilities of agents in graph modeling and learning, such as graph annotation, synthesis, and understanding. (4) Graphs for AI Agents: the role and potential of graphs and graph learning in empowering the core functionalities of agents, including agent planning, execution, memory, and multi-agent coordination. (5) Representative Applications. (6) Challenges and Future Opportunities.](/images/papers/2506.18019/279dc08dbddfe0f373d97b0afabee3a5dd63872a1b6522646ef2408b19771d8c.jpg)

**原图说明：** Fig. 1: An overall illustration of graphs meet AI agents. (1) Graph Methodology: graph data organization and knowledge extraction with graphs. (2) AI Agent Methodology: LLM-based foundation models and RL-based learning paradigms, forming core AI Agent pipelines. (3) AI Agents for Graphs: the powerful capabilities of agents in graph modeling and learning, such as graph annotation, synthesis, and understanding. (4) Graphs for AI Agents: the role and potential of graphs and graph learning in empowering the core functionalities of agents, including agent planning, execution, memory, and multi-agent coordination. (5) Representative Applications. (6) Challenges and Future Opportunities.

**图示解释：** 该图对应论文中的“Fig. 1: An overall illustration of graphs meet AI agents. (1) Graph Methodology: graph data organization and knowledge extraction with graphs. (2) AI Agent Methodology: LLM-based foundation models and RL-based learning paradigms, forming core AI Agent pipelines. (3) AI Agents for Graphs: the powerful capabilities of agents in graph modeling and learning, such as graph annotation, synthesis, and understanding. (4) Graphs for AI Agents: the role and potential of graphs and graph learning in empowering the core functionalities of agents, including agent planning, execution, memory, and multi-agent coordination. (5) Representative Applications. (6) Challenges and Future Opportunities.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Fig. 2: A taxonomy overview of this survey with representative methods on graph-empowered functionalities of AI agents and agent-facilitated graph learning.](/images/papers/2506.18019/a849806c6d14cfcb70db0d5a1801a236bbddc89964fa4a438d827dbe5d548285.jpg)

**原图说明：** Fig. 2: A taxonomy overview of this survey with representative methods on graph-empowered functionalities of AI agents and agent-facilitated graph learning.

**图示解释：** 该图对应论文中的“Fig. 2: A taxonomy overview of this survey with representative methods on graph-empowered functionalities of AI agents and agent-facilitated graph learning.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Fig. 3: An illustration of graphs for agent planning.](/images/papers/2506.18019/45f687f3adee6aa94a77f8e29871987f6b9999c1cc1f325e20e64fc5d3facc51.jpg)

**原图说明：** Fig. 3: An illustration of graphs for agent planning.

**图示解释：** 该图对应论文中的“Fig. 3: An illustration of graphs for agent planning.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 4

![Fig. 5: An illustration of graphs for agent memory.](/images/papers/2506.18019/399a889c4ee6a2c235cd2fee1f466551f6044efa080d14934f8a8364470d97a6.jpg)

**原图说明：** Fig. 5: An illustration of graphs for agent memory.

**图示解释：** 该图对应论文中的“Fig. 5: An illustration of graphs for agent memory.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 首次系统综述图技术与AI智能体的交叉领域：论文填补了现有综述仅关注图在强化学习或LLM中应用的空白，首次全面梳理了图技术如何赋能智能体的规划、执行、记忆和多智能体协调等核心功能。
2. 提出双向增强的新颖分类体系：不仅讨论图如何赋能智能体，还反向探讨智能体范式如何增强图学习（如图标注、合成、理解），强调图与智能体的协同演化与深度融合。
3. 系统梳理图赋能智能体各功能的具体机制：针对规划（任务推理、任务分解、决策搜索）、执行（工具使用、环境交互）、记忆（图结构记忆组织与检索）和多智能体协调分别总结了代表性方法和图结构设计范式。

## 五、实验数据集选择

- 论文为综述性文章，未使用特定数据集进行实验，而是系统梳理了现有基准和工具包，包括LLM-based agent benchmarks和graph-related agent benchmarks

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

As illustrated in Table I, there are currently numerous representative benchmarks and open-source toolkits that have been proposed for evaluations in different agent tasks, especially

LLM-based agents. Graph-related agent benchmarks have also begun to gain attention in recent years. For the challenge aspects, existing benchmarks still differ in task definitions or evaluation data, making unified evaluation challenging. Furthermore, as LLM foundation models and RL technologies integrate deeply, future benchmarks could incorporate both and include graph-based models as a part. Also, for emerging complex scenarios in which graph learning shows great potential, like multi-agent reasoning, memory, and collaboration in large-scale dynamic environments, there is currently a lack of graph-centric agent benchmarks.

## 八、总结

In this paper, we provide a comprehensive and systematic review of the intersection of graph techniques and AI agents, with graph-empowered agent functionalities, including planning, execution, memory, and multi-agent coordination. In addition, we also investigate how AI agent paradigms can enhance graph learning, such as graph annotation, synthesis, and understanding. Based on the detailed review, we then summarize meaningful applications, open questions, and future opportunities for this rapidly developing intersection field, offering new potential approaches for next-generation agents facing increasingly complex and messy task information. Related resources are organized and updated in Github link for the research and industrial communities.

## References

[1] T. T. Nguyen, N. D. Nguyen, and S. Nahavandi, “Deep reinforcement learning for multiagent systems: A review of challenges, solutions, and applications,” IEEE transactions on cybernetics, vol. 50, no. 9, pp. 3826–3839, 2020.

[2] C. Florensa, D. Held, X. Geng, and P. Abbeel, “Automatic goal generation for reinforcement learning agents,” in International conference on machine learning. PMLR, 2018, pp. 1515–1528.

[3] L. Wang, C. Ma, X. Feng, Z. Zhang, H. Yang, J. Zhang, Z. Chen, J. Tang, X. Chen, Y. Lin et al., “A survey on large language model based autonomous agents,” Frontiers of Computer Science, vol. 18, no. 6, p. 186345, 2024.

[4] A. Zhao, D. Huang, Q. Xu, M. Lin, Y.-J. Liu, and G. Huang, “Expel: Llm agents are experiential learners,” in Proceedings of the AAAI Conference on Artificial Intelligence, vol. 38, no. 17, 2024, pp. 19 632– 19 642.

[5] F. Peiyuan, Y. He, G. Huang, Y. Lin, H. Zhang, Y. Zhang, and H. Li, “Agile: A novel reinforcement learning framework of llm agents,” in Advances in Neural Information Processing Systems, vol. 37, 2024, pp. 5244–5284.

[6] T. Masterman, S. Besen, M. Sawtell, and A. Chao, “The landscape of emerging ai agent architectures for reasoning, planning, and tool calling: A survey,” arXiv preprint arXiv:2404.11584, 2024.

[7] N. Krishnan, “Ai agents: Evolution, architecture, and real-world applications,” arXiv preprint arXiv:2503.12687, 2025.

[8] X. Huang, W. Liu, X. Chen, X. Wang, H. Wang, D. Lian, Y. Wang, R. Tang, and E. Chen, “Understanding the planning of llm agents: A survey,” arXiv preprint arXiv:2402.02716, 2024.

[9] T. Guo, X. Chen, Y. Wang, R. Chang, S. Pei, N. V. Chawla, O. Wiest, and X. Zhang, “Large language model based multi-agents: a survey of progress and challenges,” in Proceedings of the Thirty-Third International Joint Conference on Artificial Intelligence, 2024, pp. 8048– 8057.

[10] Q. Guo, F. Zhuang, C. Qin, H. Zhu, X. Xie, H. Xiong, and Q. He, “A survey on knowledge graph-based recommender systems,” IEEE Transactions on Knowledge and Data Engineering, vol. 34, no. 8, pp. 3549–3568, 2020.

[11] Y. Ektefaie, G. Dasoulas, A. Noori, M. Farhat, and M. Zitnik, “Multimodal learning with graphs,” Nature Machine Intelligence, vol. 5, no. 4, pp. 340–350, 2023.

[12] C. Chen, Y. Wu, Q. Dai, H.-Y. Zhou, M. Xu, S. Yang, X. Han, and Y. Yu, “A survey on graph neural networks and graph transformers in computer vision: A task-oriented perspective,” IEEE Transactions on Pattern Analysis and Machine Intelligence, 2024.

[13] Z. Wu, S. Pan, F. Chen, G. Long, C. Zhang, and P. S. Yu, “A comprehensive survey on graph neural networks,” IEEE transactions on neural networks and learning systems, vol. 32, no. 1, pp. 4–24, 2020.

[14] L. Wu, Y. Chen, K. Shen, X. Guo, H. Gao, S. Li, J. Pei, B. Long et al., “Graph neural networks for natural language processing: A survey,” Foundations and Trends® in Machine Learning, vol. 16, no. 2, pp. 119–328, 2023.

[15] M. Gallici, M. Martin, and I. Masmitja, “Transfqmix: Transformers for leveraging the graph structure of multi-agent reinforcement learning problems,” in Proceedings of the 2023 International Conference on Autonomous Agents and Multiagent Systems, 2023, pp. 1679–1687.

[16] M. Zhuge, W. Wang, L. Kirsch, F. Faccio, D. Khizbullin, and J. Schmidhuber, “Gptswarm: Language agents as optimizable graphs,” in Forty-first International Conference on Machine Learning, 2024.

[17] X. Liu, Z. Peng, X. Yi, X. Xie, L. Xiang, Y. Liu, and D. Xu, “Toolnet: Connecting large language models with massive tools via tool graph,” arXiv preprint arXiv:2403.00839, 2024.

[18] M. Yasunaga, H. Ren, A. Bosselut, P. Liang, and J. Leskovec, “Qa-gnn: Reasoning with language models and knowledge graphs for question answering,” in Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, 2021, pp. 535–546.

[19] R. Zhao, F. Zhao, L. Wang, X. Wang, and G. Xu, “Kg-cot: Chain-ofthought prom

### 在线资源

- [论文：arXiv 2506.18019](https://arxiv.org/abs/2506.18019)
- [PDF源文件](/papers/2506.18019.pdf)
