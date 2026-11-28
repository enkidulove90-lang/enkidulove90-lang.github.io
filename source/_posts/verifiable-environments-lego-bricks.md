---
title: "可验证环境不是推荐任务：RACES 如何用递归组合扩展推理训练"
date: 2026-06-10
year: 2026
venue_type: arXiv预印本
venue_name: arXiv
categories: [AI, 大模型与智能体]
tags: [论文速读, 强化学习, 可验证环境, 推理泛化]
slug: verifiable-environments-lego-bricks
arxiv_id: "2606.12373"
description: "RACES 把可验证环境视作可组合构件，用四类算子递归生成更难的训练环境，并检验这种扩展能否提升推理模型的分布外泛化。"
---

> 论文：[RACES: Recursive Automated Composition for Environment Scaling](https://arxiv.org/abs/2606.12373)<br>
> 作者匿名代码与数据快照：[Submission of NeurIPS 2026](https://anonymous.4open.science/r/Submission_of_NIPS2026_34776-B7FD)

## 问题是什么

这篇论文研究的不是“序列推荐”，而是**可验证环境上的强化学习与推理泛化**。这类环境能够用确定性验证器判断答案对错，因此适合为推理模型提供可扩展的奖励信号。真正的瓶颈在于：人工设计环境代价高，逐个生成新环境通常只能线性扩展任务数量，而且容易停留在相似难度和相似推理模式上。

RACES 的核心问题是：已有环境能否像乐高积木一样递归组合，从有限的原子环境自动形成更多、更难、结构更丰富的训练任务？论文把一个可验证环境写成四元组：

$$
e=(G_e, f_e, D_e, V_e),
$$

其中 $G_e$ 生成问题，$f_e$ 定义问题到答案的映射，$D_e$ 与 $V_e$ 分别描述输入域和输出域。只要前一环境的输出域与后一环境的输入域兼容，两者就可以继续组合。

## RACES 如何工作

![RACES 从原子环境池递归组合出复合环境](/images/papers/2606.12373/races-framework.png)

**图解：** 这张方法总览图从左到右展示原子环境池、可执行性筛选、递归组合以及四种组合算子。重点看中间的“积木式”递归：新生成的复合环境还能重新进入候选池，继续与其他环境组合。图支持的有限结论是，RACES 扩展的是环境的**组合结构**，而不是简单复制或改写题目文本。

框架维护一个环境前沿集合，先检查类型是否兼容，再实际执行组合后的生成器与验证器，只有通过质量检查的环境才会进入下一轮。这样，系统不是让语言模型凭空描述一个新任务，而是保留可执行的生成逻辑和可验证的答案链。

论文定义了四种算子：

- **SEQUENTIAL**：前一个环境的答案成为后一个环境的输入，形成多步依赖。
- **PARALLEL**：多个环境独立求解，再把结果共同交给聚合环境。
- **SORT**：对多个子任务的结果执行排序，要求模型同时完成求解与比较。
- **SELECT**：根据条件从候选结果中选择目标，增加分支判断。

这些算子诱导不同推理结构。递归应用后，环境数量不再只随原子任务数量线性增长，但每个复合环境仍能通过组成它的确定性验证器进行检查。

## 训练设置

实验使用 DeepSeek-R1-Distill-Qwen-14B 和 Qwen3-14B，两者都采用 GRPO 训练。主要设置为 300 个训练步骤、12,800 个训练实例、batch size 128、学习率 $2\times10^{-6}$、每题 8 个 rollout，以及 32K 最大上下文长度。训练运行在 32 张 A100 80GB GPU 上。

论文比较三组模型：未经强化学习的 Base、在单个原子环境上训练的 $\mathrm{RL}_{\mathrm{individual}}$，以及在 RACES 复合环境上训练的 $\mathrm{RL}_{\mathrm{RACES}}$。

## 主要结果

| 模型 | Base | 单环境 RL | RACES RL | RACES 相对 Base | RACES 相对单环境 |
|---|---:|---:|---:|---:|---:|
| DeepSeek-R1-Distill-Qwen-14B | 48.2 | 48.8 | 51.3 | +3.1 | +2.5 |
| Qwen3-14B | 58.8 | 60.1 | 61.1 | +2.3 | +1.0 |

这里必须区分两个参照系：DeepSeek 系列的 51.3 相比**未经 RL 的 Base 48.2**提高 3.1 分；相比**单环境 RL 的 48.8**提高 2.5 分。旧版文章遗漏了前一个基线，导致“平均提升 3.1 分”和“提升 2.5 分”看起来互相冲突。

## 为什么训练奖励更低，泛化反而更好

![单环境与 RACES 训练奖励对比](/images/papers/2606.12373/training-reward.png)

**图解：** 图中单环境训练的奖励快速升高，而 RACES 的奖励持续更低。重点不是把低奖励解释成训练失败，而是识别任务难度差异：复合环境包含更长的依赖链和更多推理模式。该图只能说明 RACES 训练任务更难，不能单独证明泛化更强。

![不同训练方法的分布外评测表现](/images/papers/2606.12373/ood-performance.png)

**图解：** 这张图给出与上一张图对应的分布外评测曲线。尽管 RACES 的训练奖励较低，其下游平均分在约 200 步时达到 51.9，而单环境训练约为 50.4。两图合看才支持论文的核心解释：容易记住的训练环境不必然带来更好的跨任务泛化，更难且结构更多样的组合环境可能提供更有效的训练信号。

## 组合深度带来的收益与边界

![不同组合长度下的训练奖励与波动](/images/papers/2606.12373/composition-size.png)

**图解：** 图中比较组合长度从 2 增加到 6 时的奖励水平和波动。组合越深，平均奖励和方差整体下降，表明任务趋难；下游表现从长度 2 的 50.8 提升到长度 5 的 51.2，但长度 6 回落到 50.7。重点结论不是“越深越好”，而是存在难度甜点区：过浅缺少结构多样性，过深则可能造成奖励稀疏和优化困难。

论文还报告了一项环境效率结果：对 Qwen3-4B，RACES 只使用 50 个环境即可取得 50.8 的平均分，而单环境方法使用 300 个环境得到 50.4。这说明组合机制的价值不仅是提高最终分数，也在于复用已有环境结构。

## 局限与阅读判断

论文明确承认四类算子没有覆盖条件分支、有界循环等全部程序结构；复合任务依赖模型已经具备一定推理能力，较弱模型容易遭遇稀疏奖励；更深组合还会产生长轨迹，因此 32K 上下文窗口成为实际门槛。

此外，当前公开地址是匿名评审代码与数据快照，并非正式 GitHub 仓库；文章因此不把它误写成 GitHub 链接。主表给出了清晰的平均分，但没有为所有差异报告统计显著性检验。对“组合环境导致泛化提升”的因果解释，应结合训练曲线、环境效率和组合深度消融共同阅读，而不能只看单一最终分数。

## References

1. [RACES: Recursive Automated Composition for Environment Scaling](https://arxiv.org/abs/2606.12373). arXiv:2606.12373, 2026.
2. [RLVE: Scaling Reinforcement Learning from Verifiable Environments](https://arxiv.org/abs/2511.07317). arXiv:2511.07317, 2025.
3. [SCALER: Scaling Verifiable Environments for Reinforcement Learning](https://arxiv.org/abs/2601.04809). arXiv:2601.04809, 2026.
4. [ReSyn: Environment Synthesis for Reinforcement Learning](https://openreview.net/forum?id=YcrOuJRVGh). OpenReview, 2026.
5. [Composition-RL: Compositional Reinforcement Learning for Reasoning](https://arxiv.org/abs/2602.12036). arXiv:2602.12036, 2026.
6. [From f(x) and g(x) to f(g(x)): Learning Through Problem Composition](https://openreview.net/forum?id=jt7oCtYqHE). OpenReview, 2026.
