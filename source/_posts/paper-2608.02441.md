---
title: "智能体商业世界：可审计可验证的Vibe Commerce环境"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.02441
arxiv_id: "2608.02441"
description: "论文提出ACWORLD，一个面向vibe commerce的可审计、可验证的多对多智能体商业环境。"
---

> 论文：[arXiv 2608.02441](https://arxiv.org/abs/2608.02441) · 代码：[GitHub](https://github.com/google-agentic-commerce/AP2) · PDF：[本地阅读](/papers/2608.02441.pdf)

论文提出ACWORLD，一个面向vibe commerce的可审计、可验证的多对多智能体商业环境。其核心是Vibe Commerce Protocol（VCP），将每个智能体决策绑定到具体Buyer或Merchant，经Commerce Intelligence Platform验证后才由World提交共享交易状态变更，从而支持状态重建与重打分。论文同时发布ACWORLD Benchmark，包含200任务/80能力的能力覆盖赛道和60任务/785,022商品的大目录赛道，并在10个模型上验证了过程级证据的必要性。

## 研究问题

论文提出ACWORLD，一个面向vibe commerce的可审计、可验证的多对多智能体商业环境。其核心是Vibe Commerce Protocol（VCP），将每个智能体决策绑定到具体Buyer或Merchant，经Commerce Intelligence Platform验证后才由World提交共享交易状态变更，从而支持状态重建与重打分。论文同时发布ACWORLD Benchmark，包含200任务/80能力的能力覆盖赛道和60任务/785,022商品的大目录赛道，并在10个模型上验证了过程级证据的必要性。

## 方法：核心思路与整体框架

论文采用系统构建与基准评测相结合的方法。首先定义VCP协议，将智能体决策、平台验证与World状态提交分离；然后实现ACWORLD环境，通过确定性转移函数W_{j+1}=F(W_j,u_j)提交授权事件，并记录链接执行轨迹。评测采用冻结任务契约、固定对手策略和确定性评分器，基于加权谓词聚合得分，并通过状态重建、重打分、变异测试和HTTP一致性检查验证评测有效性。

![图 1：Figure 11: Detection of 95 injected errors under four evidence views. Filled cells are detected, and gray cells are missed. This tests view coverage, not empirical error rates.](/images/papers/2608.02441/58982b403121325b43704daf890c405691ace94dc2002aba5608ccdc8d42f675.jpg)

*图 1 · 原图说明：Figure 11: Detection of 95 injected errors under four evidence views. Filled cells are detected, and gray cells are missed. This tests view coverage, not empirical error rates.*

**图示解释：** 论文采用系统构建与基准评测相结合的方法。

## 创新点

1. 提出Vibe Commerce Protocol（VCP），将智能体决策与共享状态变更权限分离，每个动作绑定认证主体，消息不能直接修改World，提交必须引用已接受的验证结果，并支持从初始状态重放提交以复现最终状态与事件摘要。
2. 构建ACWORLD持久化多对多商业环境，支持独立控制的Buyer与Merchant策略在同一市场中交互，同时保留各自私有mandate、身份与权限，实现决策、验证与效果的可审计归因。
3. 设计双赛道ACWORLD Benchmark：能力覆盖赛道含200任务、10个商业家族、80项能力；大目录赛道含60任务、覆盖785,022个可交易商品，二者共用同一执行与评分路径但独立报告均值。
4. 提出基于链接记录L_t=(actor, decision, validation, evidence, ΔWorld)的执行轨迹与确定性重打分机制，无需再次调用模型即可重建状态并重新评分，同时暴露候选过程奖励信号。
5. 实验表明最终状态不足以评估智能体：在861个未满分运行中，99个运行虽达到与满分执行相同的最终状态，但仍存在被评估错误，说明过程级证据对归因和评估是必要的。

## 实验：数据、基线与结果

### 数据集与设置

能力覆盖赛道含200个任务，覆盖10个商业家族和80项能力，角色划分为116个Buyer任务和84个Merchant任务，使用1,082个公开商品快照，缺失字段按固定规则填充。大目录赛道含60个任务，覆盖Discovery、Grounding、Preference、Multi-item四类共18项能力，角色划分为45个Buyer和15个Merchant，查询由791,431条公开源记录构建的只读数据库，其中785,022条有正价格并进入可交易目录。每个任务从相同初始World开始，面对相同固定对手，智能体仅看到角色可见信息。训练/验证/测试划分原文未披露。

### Benchmark 与结果

能力覆盖赛道2,000次运行中，模型均值范围为65.9%至85.6%，GPT-5.6 Sol总体最高，Gemini 3.6 Flash的Merchant均值最高。运行分布为1,139次满分、757次部分分、104次零分。家族层面，Inventory和Lifecycle最强，平均分别为93.3%和90.3%；Timing和Discovery最弱，分别为40.3%和65.9%。大目录赛道600次运行中，模型均值范围为56.10%至91.36%，Gemini 3.5 Flash和Gemini 3.6 Flash总体接近，分别为91.36%和91.35%，GPT-5.6 Sol为89.11%。运行分布为365次满分、206次部分分、29次零分。阶段分数显示Validation达94.17%、Evidence达86.75%，而Search为76.11%、Decision为73.67%。失败分析中，861个未满分运行有803个可归因到唯一主导组，其中Evidence 314、Choice 159、Execution 208、Authority 122；99个未满分运行达到与满分执行相同的最终状态。5×5市场研究中，确定性清算完成5笔交易，分配匹配参考，达到全局最优的97.8%，并重建到相同World状态。



### 消融实验

对比模型包括Claude Sonnet 5、DeepSeek-V4-Pro、Gemini 3.5 Flash、Gemini 3.6 Flash、GPT-5.6 Luna、GPT-5.6 Sol、GPT-5.6 Terra、Kimi K3、Mistral Medium 3.5、Qwen3.5 Plus，共10个模型。每个模型完成200个能力覆盖任务和60个大目录任务，分别产生2,000和600次运行。消融与验证设置包括：95个针对性决策变异覆盖全部80项能力、18个HTTP一致性episode、60个满分参考、374个针对性变异运行、60个确定性重打分和60个过程分数一致性检查；另有5×5多智能体市场研究、持久化案例、扩展接口案例和10个完整性案例。

## 总结

论文提出ACWORLD，一个面向vibe commerce的可审计、可验证的多对多智能体商业环境。

## References

- AGENTIC COMMERCE WORLD: AN AUDITABLE AND VERIFIABLE ENVIRONMENT FOR VIBE COMMERCE：[arXiv 2608.02441](https://arxiv.org/abs/2608.02441)

- [代码：GitHub](https://github.com/google-agentic-commerce/AP2)
- [PDF源文件](/papers/2608.02441.pdf)
