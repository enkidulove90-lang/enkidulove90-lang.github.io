---
title: "EdgeBench：揭示真实环境学习的缩放定律"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.05155
arxiv_id: "2607.05155"
description: "论文提出EdgeBench，一个包含134个真实世界任务、覆盖六大能力族、支持至少12小时连续交互的超长时程基准，用于研究智能体部署后从环境中学习的能力。"
---

> 论文：[arXiv 2607.05155](https://arxiv.org/abs/2607.05155) · PDF：[本地阅读](/papers/2607.05155.pdf)

论文提出EdgeBench，一个包含134个真实世界任务、覆盖六大能力族、支持至少12小时连续交互的超长时程基准，用于研究智能体部署后从环境中学习的能力。通过分析约38,000小时的智能体-环境交互数据，论文首次发现环境学习性能随交互时间遵循精确的log-sigmoid缩放定律，平均R²达0.998。论文还提出基于潜在任务图上前沿扩展过程的理论推导，发现前沿智能体的学习速度约每三个月翻倍，并揭示持续经验、长上下文和有效反馈对长时程性能的关键作用。

## 研究问题

论文提出EdgeBench，一个包含134个真实世界任务、覆盖六大能力族、支持至少12小时连续交互的超长时程基准，用于研究智能体部署后从环境中学习的能力。通过分析约38,000小时的智能体-环境交互数据，论文首次发现环境学习性能随交互时间遵循精确的log-sigmoid缩放定律，平均R²达0.998。论文还提出基于潜在任务图上前沿扩展过程的理论推导，发现前沿智能体的学习速度约每三个月翻倍，并揭示持续经验、长上下文和有效反馈对长时程性能的关键作用。

## 方法：核心思路与整体框架

论文构建EdgeBench基准，包含134个真实世界任务，覆盖科学问题与ML、系统与软件工程、组合优化、专业知识工作、形式数学与定理证明、交互式游戏六大能力族。每个任务在可执行工作空间中运行，采用工作-评判双容器隔离架构和双环反馈机制。评估五个前沿模型（Claude Opus 4.8、GPT-5.5、GPT-5.4、GLM-5.1、DeepSeek-V4-Pro），每个任务-模型对运行三次12小时试验，记录完整提交轨迹，并用log-sigmoid等S曲线拟合性能随交互时间的变化。

![图 1：Figure 2 EdgeBench task taxonomy. 134 real world tasks across six capability families, with feedback channels designed to support within-run improvement. Recorded human expert efort estimates: mean 57.2 h.](/images/papers/2607.05155/ccf902412bc706f24f7ad9602f45bf4a1bbd0cf861539999b9f0f72f1e189dac.jpg)

*图 1 · 原图说明：Figure 2 EdgeBench task taxonomy. 134 real world tasks across six capability families, with feedback channels designed to support within-run improvement. Recorded human expert efort estimates: mean 57.2 h.*

**图示解释：** 论文构建EdgeBench基准，包含134个真实世界任务，覆盖科学问题与ML、系统与软件工程、组合优化、专业知识工作、形式数学与定理证明、交互式游戏六大能力族。

![图 2：Figure 4 Learning curves over 12 hours for 18 representative tasks across six capability families. The remaining task curves are provided in Figures 15–35.](/images/papers/2607.05155/685438f115491a7989375db77922aa4a2f9a7d46ad7b211f1e7e74374e450a8e.jpg)

*图 2 · 原图说明：Figure 4 Learning curves over 12 hours for 18 representative tasks across six capability families. The remaining task curves are provided in Figures 15–35.*

**图示解释：** 论文构建EdgeBench基准，包含134个真实世界任务，覆盖科学问题与ML、系统与软件工程、组合优化、专业知识工作、形式数学与定理证明、交互式游戏六大能力族。

![图 3：Figure 5 Task-family-level log-sigmoid fits across the six EdgeBench task families. Despite large diferences in task type and scoring function, the same log-time sigmoidal form fits the average trajectory in each task family well.1](/images/papers/2607.05155/2bee0c8b5d0722839ccc8c89ced3d1dd8bb71a77db017f5aea0ff93cf60b71cd.jpg)

*图 3 · 原图说明：Figure 5 Task-family-level log-sigmoid fits across the six EdgeBench task families. Despite large diferences in task type and scoring function, the same log-time sigmoidal form fits the average trajectory in each task family well.1*

**图示解释：** 论文构建EdgeBench基准，包含134个真实世界任务，覆盖科学问题与ML、系统与软件工程、组合优化、专业知识工作、形式数学与定理证明、交互式游戏六大能力族。

![图 4：Figure 27 Per-task learning curves: Combinatorial Optimization & Planning (13/21).](/images/papers/2607.05155/7932dce4f21485740e95513225f406f699ae088beb3312b3a327300ca748bc50.jpg)

*图 4 · 原图说明：Figure 27 Per-task learning curves: Combinatorial Optimization & Planning (13/21).*

**图示解释：** 论文构建EdgeBench基准，包含134个真实世界任务，覆盖科学问题与ML、系统与软件工程、组合优化、专业知识工作、形式数学与定理证明、交互式游戏六大能力族。

## 创新点

1. 首次发现环境学习遵循log-sigmoid缩放定律：在134个真实任务、约38,000小时交互数据上，平均性能随交互时间呈log-sigmoid增长，R²=0.998，且该形式在任务族、更长时程和早期轨迹预测中均成立。
2. 提出环境学习的理论推导：将学习建模为潜在任务图上的前沿扩展过程，用解锁-锁定分数质量乘积解释y(1-y)速率律，并从任务图自相似搜索几何导出log时间坐标。
3. 揭示智能体学习速度每三个月翻倍的快速缩放趋势：从2025年9月GPT-5-Codex到2026年4月GPT-5.5，学习速度约提升8倍，且该提升源于更有效的每次交互学习而非更频繁的提交。
4. 设计双环反馈与工作-评判隔离的评估框架SForge：内环为智能体本地探索，外环为提交门控的隐藏评判反馈，支持日尺度运行、异步评分、自动评估和防作弊机制。
5. 系统研究长时程学习动态：持续有状态经验优于独立重启，1M上下文比200k上下文在12小时内稳定高出4.4-5.8分，有效提交率与最终性能相关但提交数量本身不保证更好结果。

## 实验：数据、基线与结果

### 数据集与设置

134个真实世界任务，覆盖六大能力族：科学问题与ML（39）、系统与软件工程（36）、组合优化（19）、专业知识工作（19）、形式数学与定理证明（13）、交互式游戏与模拟器（8）。每个任务-模型对运行三次独立12小时试验，记录完整提交轨迹。人类专家平均耗时57.2小时，最高320小时。18任务切片用于学习速度测量，42任务子集用于上下文消融。

### Benchmark 与结果

在134个任务上，平均性能随交互时间呈log-sigmoid增长，R²=0.998。12小时聚合排行榜：Claude Opus 4.8以51.3分领先，GPT-5.5为48.4分，GPT-5.4为39.3分，GLM-5.1为37.4分，DS-V4-Pro为31.0分。类别得分上，Opus 4.8在Code族达67.4分，Math族55.0分。学习速度从GPT-5-Codex（2025年9月）到GPT-5.5（2026年4月）提升约8倍，约每三个月翻倍。1M上下文Opus 4.8比200k版本在2小时高5.8分，12小时高4.4分。持续有状态运行优于等预算独立重启。



### 消融实验

对比五个前沿模型：Claude Opus 4.8、GPT-5.5、GPT-5.4、GLM-5.1、DeepSeek-V4-Pro（preview）。消融设置包括：200k vs 1M上下文Opus 4.8对比、持续有状态运行 vs 独立重启、不同S曲线拟合对比（log-sigmoid、log-Gompertz、log-probit、Weibull CDF、log-linear）。

## 总结

论文提出EdgeBench，一个包含134个真实世界任务、覆盖六大能力族、支持至少12小时连续交互的超长时程基准，用于研究智能体部署后从环境中学习的能力。

## References

- EdgeBench: Unveiling Scaling Laws of Learning from Real-World Environments：[arXiv 2607.05155](https://arxiv.org/abs/2607.05155)

- [PDF源文件](/papers/2607.05155.pdf)
