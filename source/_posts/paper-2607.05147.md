---
title: "DSpark：置信度调度的半自回归推测解码"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.05147
arxiv_id: "2607.05147"
description: "论文提出 DSpark，一个面向高并发 LLM 服务的推测解码框架，旨在同时解决并行草稿模型缺乏 token 间依赖导致的接受率衰减，以及固定长度验证在高负载下浪费目标模型批处理容量的问题。"
---

> 论文：[arXiv 2607.05147](https://arxiv.org/abs/2607.05147) · 代码：[GitHub](https://github.com/Zacks917/AutoMTP) · PDF：[本地阅读](/papers/2607.05147.pdf)

论文提出 DSpark，一个面向高并发 LLM 服务的推测解码框架，旨在同时解决并行草稿模型缺乏 token 间依赖导致的接受率衰减，以及固定长度验证在高负载下浪费目标模型批处理容量的问题。DSpark 采用半自回归生成架构，将计算密集的并行骨干与轻量级串行头结合，在保持草稿速度的同时注入块内依赖；同时引入置信度调度验证机制，通过置信度头估计前缀存活概率，并结合硬件感知调度器动态分配每个请求的验证长度。离线基准和 DeepSeek-V4 在线部署均验证了其有效性。

## 研究问题

论文提出 DSpark，一个面向高并发 LLM 服务的推测解码框架，旨在同时解决并行草稿模型缺乏 token 间依赖导致的接受率衰减，以及固定长度验证在高负载下浪费目标模型批处理容量的问题。DSpark 采用半自回归生成架构，将计算密集的并行骨干与轻量级串行头结合，在保持草稿速度的同时注入块内依赖；同时引入置信度调度验证机制，通过置信度头估计前缀存活概率，并结合硬件感知调度器动态分配每个请求的验证长度。离线基准和 DeepSeek-V4 在线部署均验证了其有效性。

## 方法：核心思路与整体框架

DSpark 将推测解码的每 token 延迟分解为草稿与验证时间除以接受长度。方法上采用两阶段草稿：并行骨干（基于 DFlash）一次前向生成所有草稿隐藏状态和基础 logits，轻量级串行头（Markov 低秩转移矩阵或 RNN 门控更新）自回归地注入块内依赖。验证阶段，置信度头估计每位置条件接受概率，经顺序温度缩放校准后，硬件感知调度器根据当前并发请求的累积存活概率和引擎吞吐曲线，贪心地选择使全局吞吐量最大的每请求验证前缀长度。

![图 1：Figure 1 | The DSpark architecture and decoding cycle. Given prompt tokens ABC , the target model executes one step to generate the next token D , which serves as the anchor for the drafting phase. Using D as the input, DSpark employs a heavy parallel backbone and a lightweight sequential head to generate draft tokens EFGH along with their corresponding confidence scores � –� . The Hardware-Aware Prefix Scheduler then evaluates these scores to retain the prefix EFG and drop the low-confidence token H . Finally, the target model verifies the scheduled prefix in parallel. As illustrated, E and F are accepted while G is rejected, prompting the model to generate a corrected token G∗ to complete the current round.](/images/papers/2607.05147/5889079bacbf3c279318531b1aa8c47cf5a154150b4efd0d6a766f52f077ba3d.jpg)

*图 1 · 原图说明：Figure 1 | The DSpark architecture and decoding cycle. Given prompt tokens ABC , the target model executes one step to generate the next token D , which serves as the anchor for the drafting phase. Using D as the input, DSpark employs a heavy parallel backbone and a lightweight sequential head to generate draft tokens EFGH along with their corresponding confidence scores � –� . The Hardware-Aware Prefix Scheduler then evaluates these scores to retain the prefix EFG and drop the low-confidence token H . Finally, the target model verifies the scheduled prefix in parallel. As illustrated, E and F are accepted while G is rejected, prompting the model to generate a corrected token G∗ to complete the current round.*

**图示解释：** DSpark 将推测解码的每 token 延迟分解为草稿与验证时间除以接受长度。

## 创新点

1. 半自回归生成架构：保留并行草稿骨干以维持草稿延迟与块大小近似无关，仅附加轻量级串行头（Markov 头或 RNN 头）注入块内 token 依赖，显著缓解并行草稿的后缀接受率衰减。
2. 置信度调度验证机制：设计置信度头预测每个草稿位置的条件下接受概率，并通过顺序温度缩放（STS）进行后校准，使累积接受概率的绝对幅度可用于吞吐量估计。
3. 硬件感知前缀调度器：将验证长度选择建模为全局吞吐量最大化问题，利用实时引擎吞吐曲线和校准后的前缀存活概率，动态为每个请求分配验证预算，在高并发下剪枝低置信度后缀 token。
4. 生产级在线验证与开源：在 DeepSeek-V4-Flash/Pro 生产服务系统中部署，相比 MTP-1 基线在匹配吞吐量下提升单用户生成速度 60%–85%，并开源 DSpark 检查点和 DeepSpec 训练仓库。

## 实验：数据、基线与结果

### 数据集与设置

离线评估覆盖数学推理（GSM8K、MATH500、AIME25）、代码生成（MBPP、HumanEval、LiveCodeBench）和日常聊天（MT-Bench、Alpaca、Arena-Hard）三个领域。训练数据使用 Open-PerfectBlend，包含 130 万样本，涵盖聊天 17.6%、数学 39.4%、代码 38.9%、指令跟随 4.1%；仅使用提示，响应由各目标模型以推荐采样参数重新生成。每个草稿模型训练 10 个 epoch。在线评估在 DeepSeek-V4-Flash 和 DeepSeek-V4-Pro 生产服务引擎中进行，使用真实用户流量遥测数据。

### Benchmark 与结果

离线基准上，DSpark 在所有目标模型和领域均优于 Eagle3 和 DFlash。在 Qwen3-4B、8B、14B 上，DSpark 相比 Eagle3 的宏平均接受长度分别提升 30.9%、26.7%、30.0%；相比 DFlash 分别提升 16.3%、18.4%、18.3%。在 Gemma4-12B 上也一致提升。例如 Qwen3-4B 上 DSpark 在 GSM8K 达到 6.11，而 Eagle3 为 5.14，DFlash 为 5.40。在线部署中，相比 MTP-1，在匹配聚合吞吐量下 DSpark 将单用户生成速度提升 60%–85%（V4-Flash）和 57%–78%（V4-Pro）；在严格 SLA 下（120 TPS Flash、50 TPS Pro），基线容量严重退化，DSpark 仍能维持稳健吞吐，扩展了可交互性前沿。



### 消融实验

对比方法包括：Eagle3（基于 Training-Time Test 的自回归草稿器，TTT 视野为 7，草稿层数 1）和 DFlash（最先进的并行草稿器，草稿层数 5）。所有草稿器在相同训练框架和相同数据上重新训练，使用相同的目标模型特征层。在线基线为 MTP-1（DeepSeek-AI 2024 的生产单 token 草稿配置）。消融分析包括 DSpark 的 Markov 头与 RNN 头变体。

## 总结

论文提出 DSpark，一个面向高并发 LLM 服务的推测解码框架，旨在同时解决并行草稿模型缺乏 token 间依赖导致的接受率衰减，以及固定长度验证在高负载下浪费目标模型批处理容量的问题。

## References

- DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation：[arXiv 2607.05147](https://arxiv.org/abs/2607.05147)

- [代码：GitHub](https://github.com/Zacks917/AutoMTP)
- [PDF源文件](/papers/2607.05147.pdf)
