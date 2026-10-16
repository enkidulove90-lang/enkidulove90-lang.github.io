---
title: "压缩 KV Cache 为什么在推荐上失效：EARN 的 register token"
date: 2025-07-01
categories: [推荐系统, 生成式推荐]
tags: [论文速读, 生成式推荐, 大模型微调]
slug: earn-register-token-inference-accel
description: "在推荐任务上，主流 KV Cache 压缩方法的指标会掉到近乎失效（StreamingLLM R@10 只有 0.0005，AnLLM 直接 0.0000）。EARN 换了个思路：先训练模型把长 prompt 摘要进 register token，再在第 k 层之后丢掉原文——3.79× 加速的同时精度反而高于不压缩基线。"
---

> 论文：[arXiv 2507.00715](https://arxiv.org/abs/2507.00715) · 代码：[GitHub](https://github.com/transcend-0/EARN)

LLM 生成式推荐（LLM-Rec）有个绕不开的成本问题：**提示词特别长**。用户历史交互、物品描述、任务指令全都要塞进 prompt，动辄几百到上千 token。推理时这些 token 的 KV Cache 要占显存，attention 计算量也随长度增长。而生成式推荐的输出往往只是几个 item token——**为了产出十几个 token，付出上千 token 的代价**。

已有的加速思路基本是"压缩 KV Cache"：丢注意力分数低的 token、按窗口截断、把历史压成固定长度。但这些方法在推荐任务上**精度崩得很厉害**——下面会看到，它们能把速度提上去，但推荐指标掉到近乎随机。

EARN 的差别在于：**它不是想办法"丢"，而是先训练模型学会"把长 prompt 摘要成短表示"**。

---

## 一、方法：register tokens + 在第 k 层丢掉原文

![EARN 整体结构：训练时 prefix/suffix register 可训练，推理时在第 k 层之后移除 prompt tokens](images/earn-framework.jpg)

### 1. 两个 register

EARN 在输入序列两端各插一组**可学习的虚拟 token**：

```text
X = [ R_prefix ; Prompt ; R_suffix ]
```

- **Prefix Register**：放在开头，学"任务特定信息"（这个任务要做什么、输出格式是什么）。
- **Suffix Register**：放在末尾，学"**总结历史交互**"——把用户行为序列压缩成少量 token。

关键在于这两个 register 是**训练出来的**，不是人为规则。模型在训练过程中被迫学会"把 prompt 里的信息写进 register"，因为它知道后面会看不到 prompt 原文。

### 2. 分层处理：前 k 层看全文，之后只看 register

这是整个方法的核心机制：

| 层 | 参与 attention 计算的 token |
|---|---|
| `l ≤ k` | **全部** token（指令 + 历史交互 + 两个 register） |
| `l > k` | **只有 register 与已生成 token** |

也就是说，前 k 层完成"读透 prompt"，之后 prompt token 就从计算中被移除，模型靠 register 的表示继续推理和生成。

图示的注意力分布对比也印证了这个设计的必要性：

![不同任务上的注意力分布：NLP 阅读理解任务与 LLMRec 任务（Beauty 数据集）的差异](images/earn-attention.jpg)

推荐任务和自然语言任务的注意力模式并不相同，这也解释了为什么直接照搬 NLP 的 KV 压缩方法在推荐上会失效——**它们按语言任务的注意力分布做剪枝，剪掉的恰好是推荐任务真正依赖的部分**。

### 3. 收益的量化

论文给出 KV Cache 的压缩比：

```text
压缩后 / 原大小 = ( kL + (N − k) r ) / ( N L )
```

其中 `N` 是层数、`L` 是 prompt 长度、`k` 是保留全文的层数、`r` 是 register 数量。

在典型配置（`N=32`、`L=512`、`k=8`、`r=2`）下，压缩效果显著——因为后 `N−k` 层不再为 `L` 个 prompt token 保存 KV，只存 `r` 个 register 的。

---

## 二、实验：加速的同时精度反而更高

### 主结果：所有压缩方法里只有 EARN 涨点

Beauty 数据集 + Llama 主干：

| 方法 | 时间效率 ω | 空间效率 τ | R@10 | R@20 |
|---|---|---|---|---|
| Finetune（基线） | 1.00 | 505.2 | 0.0145 | 0.0225 |
| SkipLayers | 1.79 | 895.4 | 0.0013 | 0.0013 |
| POD | 1.15 | 585.0 | 0.0045 | 0.0074 |
| 500xCompressor | 2.31 | 1168.6 | 0.0005 | 0.0006 |
| StreamingLLM | 1.22 | 611.2 | 0.0005 | 0.0005 |
| SnapKV | 1.20 | 600.7 | 0.0054 | 0.0061 |
| Gist | 1.18 | 597.6 | 0.0048 | 0.0077 |
| AnLLM | 1.24 | 625.1 | 0.0000 | 0.0000 |
| **EARN** | **3.79** | **1844.8** | **0.0167** | **0.0265** |

这张表值得逐行看：

- **所有基线压缩方法都掉到近乎失效**：StreamingLLM、SnapKV 的 R@10 只有 0.0005–0.0054（基线 0.0145），AnLLM 直接是 **0.0000**（完全生成不出有效结果）。500xCompressor 拿到 2.31× 加速，代价是精度掉到 0.0005。
- **只有 EARN 同时做到最快和最好**：3.79× 的时间效率，R@10 0.0167 **高于不压缩的 Finetune（0.0145）**。

"加速还能涨点"听起来反常，但机制上说得通：register token 相当于**给模型一个显式的"历史摘要槽位"**，模型被训练去主动维护这个摘要，这比把长 prompt 直接丢给模型、让它自己从上千 token 里找重点更有效。也就是说，EARN 压缩掉的是**冗余的信息通道**，而不是信息本身。

### 消融：suffix register 是关键，prefix register 可有可无

| 配置（Llama, k=7） | R@10 | R@20 |
|---|---|---|
| EARN | 0.0174 | 0.0273 |
| 去掉 Prefix Register（w/o PR） | 0.0172 | 0.0252 |
| 去掉 Suffix Register（w/o SR） | **0.0041** | **0.0075** |

再看另一组（去掉 register 本身）：

| 配置 | R@10 | R@20 |
|---|---|---|
| EARN (k=7) | 0.0174 | 0.0273 |
| w/o RT（无 register tokens） | **0.0048** | **0.0060** |

结论很清楚：

- **Suffix Register 是命门**：没有它，R@10 从 0.0174 崩到 0.0041（−76%）。因为它承担"总结用户历史交互"这个最吃信息的活。
- **Prefix Register 影响很小**：去掉后 R@20 从 0.0273 到 0.0252，几乎无损。任务指令本身较短，压缩它收益不大。
- **没有 register 的版本同样崩塌**（0.0048）：说明"丢 prompt"这个动作本身没问题，**问题在于丢之前有没有一个能承载信息的容器**。

### 更苛刻的设定下依然成立

![不同 batch size 下的效率曲线：注册机制带来的加速在不同批量下保持稳定](images/earn-efficiency.jpg)

| 数据集 / 主干 | 方法 | ω | R@10 |
|---|---|---|---|
| Beauty / Llama | Finetune | 1.00 | 0.0108 |
| Beauty / Llama | EARN | 3.44 | **0.0115** |
| Beauty / 其他主干 | Finetune | 1.00 | 0.0446 |
| Beauty / 其他主干 | EARN | 2.01 | **0.0520** |
| Games / 同上 | Finetune | 1.00 | 0.0557 |
| Games / 同上 | EARN | 1.97 | **0.0586** |

换了主干、换了数据集，"加速 + 涨点"的结论都稳定成立（加速比 1.97×–3.44×，指标全部高于基线）。

---

## 三、总结

EARN 给"LLM 推荐太慢"这个问题提供了一个与其他压缩路线不同的答案：

1. **区别在于"先学容器再丢内容"**：主流的 KV 压缩是"按重要性丢 token"，本质上是在信息不完备的条件下做赌注；EARN 是**先训练出一个能承载信息的 register 表示，再把原文丢掉**。表 1 里基线与 EARN 的差距（0.005 vs 0.0167）本质上就是这两条路线的差距。
2. **层深 k 是一个直观的"读—写"分界**：前 k 层负责读透 prompt（全注意力），之后只靠 register 工作。这让"信息压缩发生在前几层"这件事变得显式可控。
3. **消融给出了实现优先级**：只做 Suffix Register 就能拿到主要收益（去掉它掉 76%），Prefix Register 属于锦上添花。工程上如果要简化实现，值得先保 suffix。

一个边界：register 是**训练时学出来的**，所以它不能直接套到已经训好的模型上——需要重新微调，这是它相比"推理期剪枝"方法的额外成本。

## References

- EARN: Efficient Inference Acceleration for LLM-based Generative Recommendation by Register Tokens — [arXiv:2507.00715](https://arxiv.org/abs/2507.00715) · 代码：[GitHub](https://github.com/transcend-0/EARN)
- 对比的 KV Cache 压缩方法：StreamingLLM、SnapKV、POD、500xCompressor、Gist、AnLLM、SkipLayers
- 相关背景：LLM 生成式推荐（LC-Rec 等）
