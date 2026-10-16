---
title: "SkillJack：自进化智能体中的持久技能后门"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.03509
arxiv_id: "2608.03509"
description: "论文首次揭示并形式化了自进化智能体中“经验到技能”管线的投毒攻击面，提出SkillJack攻击。"
---

> 论文：[arXiv 2608.03509](https://arxiv.org/abs/2608.03509) · 代码：[GitHub](https://github.com/Tencent/AI-Infra-Guard) · PDF：[本地阅读](/papers/2608.03509.pdf)

论文首次揭示并形式化了自进化智能体中“经验到技能”管线的投毒攻击面，提出SkillJack攻击。攻击者仅需向经验层注入一条经过功能化包装的恶意轨迹，智能体自身的技能提取管线便会将其编译为可复用、可路由的持久技能，从而绕过原始记录层面的安全检测。论文刻画了三个关键安全属性：净化洗白（提取后LLM检测率从98.5%降至11.4%）、跨层提升（经验层输入被提升为技能层持久能力）和持久隔离（删除源记录后80%攻击仍存活）。在SkillX和Anything2Skill两个独立系统上验证了该风险的范式级普遍性。

## 研究问题

论文首次揭示并形式化了自进化智能体中“经验到技能”管线的投毒攻击面，提出SkillJack攻击。攻击者仅需向经验层注入一条经过功能化包装的恶意轨迹，智能体自身的技能提取管线便会将其编译为可复用、可路由的持久技能，从而绕过原始记录层面的安全检测。论文刻画了三个关键安全属性：净化洗白（提取后LLM检测率从98.5%降至11.4%）、跨层提升（经验层输入被提升为技能层持久能力）和持久隔离（删除源记录后80%攻击仍存活）。在SkillX和Anything2Skill两个独立系统上验证了该风险的范式级普遍性。

## 方法：核心思路与整体框架

论文采用形式化建模与跨系统实证相结合的方法。首先将经验到技能管线形式化为加载、变换、持久化、路由四阶段，定义攻击者目标函数及三个安全属性的数学形式。然后设计配对实验：65条功能化包装的恶意轨迹与65条直接恶意措辞基线轨迹配对，外加20条干净轨迹，输入两个代表性系统（SkillX和Anything2Skill）的提取管线。通过模式匹配和LLM裁判两个代理检测器，在原始轨迹、派生技能、路由技能三个边界测量检测率、触发率和持久性，并进行元数据消融和防御评估。

![图 1：Sanitization whitewashing across systems. For each configuration, the LLM judge flags the raw trajectory far more often than the skill later extracted from it: SkillX $98.5%$ vs.\ $11.4%$, A2S DOC mode $100.0%$ vs.\ $44.4%$, and A2S SDK mode $100.0%$ vs.\ $28.6%$. Extraction reduces detectability in every case; the reduction is largest for SkillX, which produces the most abstracted skills.](/images/papers/2608.03509/figure_001_fig_whitewashing.png)

*图 1 · 原图说明：Sanitization whitewashing across systems. For each configuration, the LLM judge flags the raw trajectory far more often than the skill later extracted from it: SkillX $98.5%$ vs.\ $11.4%$, A2S DOC mode $100.0%$ vs.\ $44.4%$, and A2S SDK mode $100.0%$ vs.\ $28.6%$. Extraction reduces detectability in every case; the reduction is largest for SkillX, which produces the most abstracted skills.*

**图示解释：** 论文采用形式化建模与跨系统实证相结合的方法。

![图 2：Trigger rates in the matched 25-task evaluation, per risk category and overall (25 tasks). Direct-context injection triggers most often, but the skill pathway is durable: 80.0% of skill-based triggers survive deletion of the source trajectories (post-deletion versus skill-based, overall $32.0/40.0$). Values are percentages.](/images/papers/2608.03509/figure_002_fig_persistence.png)

*图 2 · 原图说明：Trigger rates in the matched 25-task evaluation, per risk category and overall (25 tasks). Direct-context injection triggers most often, but the skill pathway is durable: 80.0% of skill-based triggers survive deletion of the source trajectories (post-deletion versus skill-based, overall $32.0/40.0$). Values are percentages.*

**图示解释：** 论文采用形式化建模与跨系统实证相结合的方法。

![图 3：Routing-level outcomes on SkillX over a 356-skill library (305 poisoned, 51 clean), across 32 attack-oriented and 15 clean tasks. Trigger rate is the share of tasks routed to a skill that satisfies the policy-violation proxy; expected-category match is the share routed to a skill of the intended category (undefined for clean tasks). The clean-task trigger rate of 20.0% reflects collateral selection. Values are percentages.](/images/papers/2608.03509/figure_003_fig_routing.png)

*图 3 · 原图说明：Routing-level outcomes on SkillX over a 356-skill library (305 poisoned, 51 clean), across 32 attack-oriented and 15 clean tasks. Trigger rate is the share of tasks routed to a skill that satisfies the policy-violation proxy; expected-category match is the share routed to a skill of the intended category (undefined for clean tasks). The clean-task trigger rate of 20.0% reflects collateral selection. Values are percentages.*

**图示解释：** 论文采用形式化建模与跨系统实证相结合的方法。

## 创新点

1. 首次识别并形式化“经验到技能投毒”这一新型攻击面：不同于传统记忆投毒仅在检索时影响智能体，该攻击利用智能体自身的学习管线将恶意经验编译为持久技能，使攻击从瞬态上下文升级为持久行为资产。
2. 提出变换鲁棒载荷（transformation-resilient payloads）设计方法：通过功能化包装（如用“备份”“归档”等合法叙事掩盖数据外传等恶意动作），使恶意动作在提取管线的压缩与抽象过程中得以保留，同时生成表面无害的技能产物。
3. 揭示并量化三个组合涌现的安全属性：净化洗白（提取后检测率大幅下降）、跨层提升（经验层输入被提升为技能层可路由能力）和持久隔离（源记录删除后技能仍存活），并证明这些属性是两个独立实现系统的范式级共性而非单一实现缺陷。
4. 发现防御协调假设：分层防御（提取时审查+运行时监控）可能相互干扰，上游过滤改变技能库组成后导致下游监控的固定签名失效，组合防御效果反而弱于单一运行时监控。

## 实验：数据、基线与结果

### 数据集与设置

数据集包含150条轨迹记录：65条功能化包装的投毒轨迹（20条数据外泄、15条权限提升、15条未授权转账、15条持久后门），65条与包装集配对的直接恶意措辞基线，20条干净AppWorld格式轨迹。相同轨迹文件输入两个提取器。SkillX产生264条包装技能和241条直接基线技能；A2S文档模式对27条包装轨迹产生可复用输出（30条技能），对0条直接恶意基线产生输出。干净SkillX路由库含51条干净技能；路由评估使用356技能库（305条投毒+51条干净）。评估任务包括32个攻击导向任务和15个干净任务（SkillX路由评估），以及65个攻击导向查询（A2S评估）。

### Benchmark 与结果

SkillX上，LLM裁判对原始包装轨迹检测率为98.5%，对提取技能降至11.4%（模式检测从44.6%降至11.0%），规避率88.6%；直接恶意基线提取技能检测率为27.0%。A2S DOC模式原始轨迹检测率100.0%，提取技能降至44.4%，提取率41.5%，直接恶意基线提取率为0%。下游触发方面，SkillX原生路由对32个攻击任务触发率56.2%，对15个干净任务触发率20.0%；A2S DOC技能在65个攻击查询上触发率89.2%，干净任务检索率95.0%。持久性方面，源轨迹删除后80.0%的技能触发存活（删除后32.0% vs 技能基线40.0%）。元数据消融显示，仅展示代码时LLM检测率36.7%，附加良性名称和描述后降至10.0%。防御方面，SkillX运行时监控在15任务样本中阻断全部触发（0.0%），但组合防御反而重新引入2个触发（13.3%）；A2S扩展签名后触发率从85.0%降至20.0%，组合防御达5.0%。补充代码生成验证中，4个投毒任务危险API模式匹配率75.0%，2个干净任务0.0%。



### 消融实验

主要对比方法包括：(1) 直接恶意措辞基线（与包装轨迹配对）；(2) 仅记忆基线（将投毒轨迹放入上下文而非技能库）；(3) 干净任务假阳性率。消融设置包括：元数据消融（完整技能、仅内容、仅名称+描述、仅名称四种呈现条件）；防御消融（D1提取时LLM安全审查、D2运行时监控、D3组合防御）。

## 总结

论文首次揭示并形式化了自进化智能体中“经验到技能”管线的投毒攻击面，提出SkillJack攻击。

## References

- SkillJack: Persistent Skill Backdoors in Self-Evolving Agents：[arXiv 2608.03509](https://arxiv.org/abs/2608.03509)

- [代码：GitHub](https://github.com/Tencent/AI-Infra-Guard)
- [PDF源文件](/papers/2608.03509.pdf)
