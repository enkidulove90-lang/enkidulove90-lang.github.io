---
title: "AGENTIC COMMERCE WORLD: AN AUDITABLE AND VERIFIABLE ENVIRONMENT FOR VIBE COMMERCE"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.02441
arxiv_id: "2608.02441"
---

## 一、简介

In vibe coding, people describe software in natural language and delegate implementation to AI agents. By analogy, vibe commerce allows people to express buying or selling goals in natural language and delegate the corresponding tasks to agents. Commerce, however, requires independently controlled Buyer and Merchant agents to interact in a shared market while preserving their private objectives and distinct authority. We introduce Agentic Commerce World (ACWORLD)1, an environment for evaluating such agents across ongoing transactions. Through its Vibe Commerce Protocol (VCP), ACWORLD validates agent actions before updating shared transaction state and records the resulting interactions, making agent behavior auditable and evaluation reproducible. The ACWORLD Benchmark contains a 200-task capability-coverage track and a 60-task large-catalog track that searches 785,022 transactable listings. Across ten models, mean scores range from 65.9% to 85.6% and from 56.1% to 91.4%, respectively. Our analysis shows that process-level evidence is necessary: final state alone can miss evaluated errors, incomplete trajectories still retain useful process signals, and large-catalog tasks expose bottlenecks across stages.

![](images/a693a4c02b04e2d76c8322515f3a521f9cdf88ca3c9f046afeddab5bdc27251c.jpg)  
Figure 1: A vibe-commerce negotiation. A Buyer with a private \$100 ceiling and a Merchant with a private \$90 floor settle on \$95 without revealing either limit.

## 二、论文方法

论文采用系统构建与基准评测相结合的方法。首先定义VCP协议，将智能体决策、平台验证与World状态提交分离；然后实现ACWORLD环境，通过确定性转移函数W_{j+1}=F(W_j,u_j)提交授权事件，并记录链接执行轨迹。评测采用冻结任务契约、固定对手策略和确定性评分器，基于加权谓词聚合得分，并通过状态重建、重打分、变异测试和HTTP一致性检查验证评测有效性。

## 三、论文里的图与解释

### 图 1

![Figure 11: Detection of 95 injected errors under four evidence views. Filled cells are detected, and gray cells are missed. This tests view coverage, not empirical error rates.](/images/papers/2608.02441/58982b403121325b43704daf890c405691ace94dc2002aba5608ccdc8d42f675.jpg)

**原图说明：** Figure 11: Detection of 95 injected errors under four evidence views. Filled cells are detected, and gray cells are missed. This tests view coverage, not empirical error rates.

**图示解释：** 该图对应论文中的“Figure 11: Detection of 95 injected errors under four evidence views. Filled cells are detected, and gray cells are missed. This tests view coverage, not empirical error rates.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 提出Vibe Commerce Protocol（VCP），将智能体决策与共享状态变更权限分离，每个动作绑定认证主体，消息不能直接修改World，提交必须引用已接受的验证结果，并支持从初始状态重放提交以复现最终状态与事件摘要。
2. 构建ACWORLD持久化多对多商业环境，支持独立控制的Buyer与Merchant策略在同一市场中交互，同时保留各自私有mandate、身份与权限，实现决策、验证与效果的可审计归因。
3. 设计双赛道ACWORLD Benchmark：能力覆盖赛道含200任务、10个商业家族、80项能力；大目录赛道含60任务、覆盖785,022个可交易商品，二者共用同一执行与评分路径但独立报告均值。
4. 提出基于链接记录L_t=(actor, decision, validation, evidence, ΔWorld)的执行轨迹与确定性重打分机制，无需再次调用模型即可重建状态并重新评分，同时暴露候选过程奖励信号。
5. 实验表明最终状态不足以评估智能体：在861个未满分运行中，99个运行虽达到与满分执行相同的最终状态，但仍存在被评估错误，说明过程级证据对归因和评估是必要的。

## 五、实验数据集选择

- ACWORLD Benchmark Capability-Coverage Track（200任务，10个商业家族，80项能力，116 Buyer/84 Merchant）
- ACWORLD Benchmark Large-Catalog Track（60任务，18项能力，45 Buyer/15 Merchant，785,022个可交易商品）
- 1,082个公开商品快照（能力覆盖赛道使用）
- 791,431条公开源记录构建的只读数据库（其中785,022条有正价格并进入可交易目录）

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

The ACWORLD Benchmark has two complementary tracks. The capability-coverage track tests broad commerce behavior in compact controlled worlds. The large-catalog track uses the same Agent, VCP, Commerce Intelligence Platform, World, and scoring path over a much larger catalog. Each task assigns one Buyer or Merchant to the evaluated model while every other agent follows a fixed policy. The tracks report independent means because they contain different task distributions.

## 八、总结

Each task evaluates one policy against deterministic counterparties. Neither the scores nor the fixed 5 × 5 study measure strategy in an open market. The catalogs have not received an independent audit and are not representative samples of deployed commerce. The large-catalog track does not reproduce live inventory or open-market behavior. Reconstruction establishes consistency under the declared transition and scorer, not their independent semantic correctness. Ten integrity cases are not a complete security proof. Because public tasks permit direct optimization, future versions will pair public development tasks with held-out test tasks that remain unpublished during evaluation.

Within these limits, VCP links agent decisions to Commerce Intelligence Platform validation and World effects. ACWORLD provides a persistent environment whose traces support state reconstruction and candidate process rewards. Its benchmark tests capability breadth and full-catalog search, while the restricted-view analysis identifies information lost from recorded trajectories. We will preserve both tracks as fixed references and document substantive changes so results remain comparable. The ten-model results characterize these tracks, not a general ranking.

## References

Amine Allouah, Omar Besbes, Josue D. Figueroa, Yash Kanoria, and Akshit Kumar. What is your´ AI agent buying? evaluation, biases, model dependence, & emerging implications of agentic e-commerce. In Proceedings of the ACM Web Conference 2026, pp. 8697–8700, New York, NY, USA, 2026. Association for Computing Machinery. doi: 10.1145/3774904.3792943. URL https://doi.org/10.1145/3774904.3792943.

Anthropic. Introducing Claude Sonnet 5. Anthropic News, 2026. URL https://www. anthropic.com/news/claude-sonnet-5. Published June 30, 2026; accessed July 22, 2026.

Gagan Bansal, Wenyue Hua, Zezhou Huang, Adam Fourney, Amanda Swearngin, Will Epperson, Tyler Payne, Jake M Hofman, Brendan Lucier, Chinmay Singh, et al. Magentic marketplace: An open-source environment for studying agentic markets. arXiv preprint arXiv:2510.25779, 2025.

Victor Barres, Honghua Dong, Soham Ray, Xujie Si, and Karthik Narasimhan. τ2-bench: Evaluating conversational agents in a dual-control environment. In Proceedings of the 43rd International Conference on Machine Learning, volume 306 of Proceedings of Machine Learning Research, Seoul, South Korea, 2026. PMLR. URL https://openreview.net/forum? id=OC2z7iSQKa.

Adrian de Valois-Franklin and Alex Bogdan. Rails: Verification-native clearing for agentic commerce. arXiv preprint arXiv:2606.08790, 2026.

Edoardo Debenedetti, Jie Zhang, Mislav Balunovic, Luca Beurer-Kellner, Marc Fischer, and´ Florian Tramer. AgentDojo: A dynamic environment to evaluate prompt injection attacks\` and defenses for LLM agents. In Advances in Neural Information Processing Systems, volume 37, Red Hook, NY, USA, 2024. Curran Associates, Inc. doi: 10.52202/079017-2636. URL https://proceedings.neurips.cc/paper\_files/paper/2024/ hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets\_and\_ Benchmarks\_Track.html.

DeepSeek. DeepSeek-V4 preview release. DeepSeek API Documentation, 2026. URL https: //api-docs.deepseek.com/news/news260424/. Published April 24, 2026; accessed July 22, 2026.

Xiang Deng, Yu Gu, Boyuan Zheng, Shijie Chen, Samuel Stevens, Boshi Wang, Huan Sun, and Yu Su. Mind2Web: Towards a generalist agent for the web. In Advances in Neural Information Processing Systems, volume 36, Red Hook, NY, USA, 2023. Curran Associates, Inc. URL https://proceedings.neurips.cc/paper\_files/paper/2023/ hash/5950bf290a1570ea401bf98882128160-Abstract-Datasets\_and\_ Benchmarks.html.

Zeyao Du, Tong Li, and Haibo Zhang. Ecomagentbench: Benchmarking shopping agents on longhorizon tasks with distributed hidden intent. arXiv preprint arXiv:2606.17698, 2026.

Shicheng Fan, Haochang Hao, Dehai Min, Weihao Liu, Philip S. Yu, and Lu Cheng. Verifiable rewards beyond math and code: Lightweight corpus-grounded process supervision for factual question answering. arXiv preprint arXiv:2605.29648, 2026a.

Shuxian Fan, Seonwoo Min, Youna Hu, Botao Xia, Jayakrishnan Unnikrishnan, Rowan Musselmann, Yifan Gao, Qingyu Yin, Priyanka Nigam, and Bing Yin. Shopping reasoning bench: An expert-authored benchmark for multi-turn conversational shopping assistants. arXiv preprint arXiv:2606.12608, 2026b.

Google. Agent payments protocol. Official protocol specification and reference implementation, 2026a. URL https://github.com/google-agentic-commerce/AP2. Accessed July 23, 2026.

Google. Gemini 3.5 Flash. Google AI for Developers, 2026b. URL https://ai.google. dev/gemini-api/docs/models/gemini-3.5-flash. Last updated July 21, 2026; accessed July 22, 2026.

Google. Gemini 3.6 Flash. Google AI for Developers, 2026c. URL https://ai.google.dev/ gemini-api/docs/models/gemini-3.6-flash. Last updated July 21, 2026; accessed July 26, 2026.

Google. Universal commerce protocol. Google for Developers, 2026d. URL https:// developers.google.com/merchant/ucp. Accessed July 22, 2026.

Shijun Lei, Quang Nguyen, Swapneel S Mehta, Zeping Li, Huichuan Fu, Xiaolong Zheng, Siki Chen, Yunji Liang, Philip Torr, and Zhenfei Yin. Strategic exploitation in llm agent markets: A simulation framework fo

### 在线资源

- [论文：arXiv 2608.02441](https://arxiv.org/abs/2608.02441)
- [代码：GitHub](https://github.com/google-agentic-commerce/AP2)
- [PDF源文件](/papers/2608.02441.pdf)
