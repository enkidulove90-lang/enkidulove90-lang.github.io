---
title: "面向生成式推荐的粗到细长期兴趣建模"
date: 2026-02-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2602.05663
arxiv_id: "2602.05663"
description: "论文提出GLASS框架，将长期用户行为序列有效注入生成式推荐（GR）的自回归解码过程。"
---

> 论文：[arXiv 2602.05663](https://arxiv.org/abs/2602.05663) · PDF：[本地阅读](/papers/2602.05663.pdf)

论文提出GLASS框架，将长期用户行为序列有效注入生成式推荐（GR）的自回归解码过程。核心洞察是SID前缀（sid1）决定粗粒度语义类别、后缀（sid2/3）定位具体物品，二者需要不同的长期信号注入方式。针对前缀生成，提出SID-Tier模块，利用语义码本紧凑性构建用户长期兴趣直方图并注入编码器；针对后缀生成，提出语义硬搜索（Semantic Hard Search），以已生成的sid1为键从长期历史中检索相关物品，并通过自适应门控融合短期与长期信号。此外提出稀疏感知增强策略缓解检索信息稀缺问题。在Taobao-MM和KuaiRec上全面超越SOTA，并在短视频平台两周在线A/B测试中取得显著收益。

## 研究问题

论文提出GLASS框架，将长期用户行为序列有效注入生成式推荐（GR）的自回归解码过程。核心洞察是SID前缀（sid1）决定粗粒度语义类别、后缀（sid2/3）定位具体物品，二者需要不同的长期信号注入方式。针对前缀生成，提出SID-Tier模块，利用语义码本紧凑性构建用户长期兴趣直方图并注入编码器；针对后缀生成，提出语义硬搜索（Semantic Hard Search），以已生成的sid1为键从长期历史中检索相关物品，并通过自适应门控融合短期与长期信号。此外提出稀疏感知增强策略缓解检索信息稀缺问题。在Taobao-MM和KuaiRec上全面超越SOTA，并在短视频平台两周在线A/B测试中取得显著收益。

## 方法：核心思路与整体框架

GLASS采用编码器-解码器架构。编码器处理短期序列与SID-Tier生成的长期兴趣向量；解码器在自回归生成每个SID token时，先由SID-Tier增强sid1预测，再以生成的sid1为键执行语义硬搜索检索长期历史，通过双交叉注意力与自适应门控融合短期和长期信号，最终以负对数似然损失端到端训练。

![图 1：Figure 1: Overview of the proposed GLASS framework. (a) GLASS adopts the encoder-decoder architecture. The encoder processes short-term item sequences and SID-Tier to capture user interests. The decoder integrates encoder output and Semantic Search via dual cross attention. (b) SID-Tier aggregates long-term history into a unified interest vector to enhance the first codeword $( s i d _ { 1 } )$ prediction. (c) Semantic Hard Search performs hard search based on the generated $s i d _ { 1 } ,$ followed by a gate to enhance the generation of fine-grained tokens $( s i d _ { 2 } , s i d _ { 3 } )$ . sparsity-aware augmentation ensures robust context by incorporating semanti neighbors or resizing the codebook](/images/papers/2602.05663/e5a32d2e4fd2de8aa1d8610dacc94fded27cfe77a11012eb29fb1037dd04d49f.jpg)

*图 1 · 原图说明：Figure 1: Overview of the proposed GLASS framework. (a) GLASS adopts the encoder-decoder architecture. The encoder processes short-term item sequences and SID-Tier to capture user interests. The decoder integrates encoder output and Semantic Search via dual cross attention. (b) SID-Tier aggregates long-term history into a unified interest vector to enhance the first codeword $( s i d _ { 1 } )$ prediction. (c) Semantic Hard Search performs hard search based on the generated $s i d _ { 1 } ,$ followed by a gate to enhance the generation of fine-grained tokens $( s i d _ { 2 } , s i d _ { 3 } )$ . sparsity-aware augmentation ensures robust context by incorporating semanti neighbors or resizing the codebook*

**图示解释：** GLASS采用编码器-解码器架构。

## 创新点

1. SID-Tier模块：针对首个SID token缺乏前置轨迹的问题，利用第一层码本的紧凑性，将长期交互映射为跨语义簇的兴趣直方图（interest histogram），通过原型对齐和分桶统计构建统一兴趣向量，作为编码器的全局先验注入，增强sid1的预测。
2. 语义硬搜索（Semantic Hard Search）：以自回归生成的粗粒度sid1作为动态语义键，从用户长期历史中硬检索具有相同第一层码字的物品子序列，构建RAG式上下文窗口，为后续细粒度token生成提供语义一致的历史信号，避免无关噪声干扰。
3. 自适应门控融合机制：在解码器中并行使用两个交叉注意力模块分别建模短期序列视图和检索长期视图，通过可学习的标量门控g动态平衡二者贡献，实现短期意图与长期偏好的自适应融合，替代DualGR的硬选择策略。
4. 稀疏感知增强策略：针对语义硬搜索中检索子序列过短（如平均仅7.8个物品）导致信息增益不足的问题，提出两种策略——放宽匹配机制动态纳入语义邻居，或调整码本结构增加桶密度，以保证检索上下文的充分信息量。

## 实验：数据、基线与结果

### 数据集与设置

任务为长序列检索式推荐（next item prediction）。TAOBAO-MM保留点击交互，采样10000个物品并过滤出现少于5次的物品，189423用户、265301训练样本、31205验证、31206测试，平均历史序列长度987；KuaiRec选取观看比>100%的样本，3790用户、10728物品、30320训练、3790验证、3790测试，平均序列长度884。参照MUSE配置，最近50个交互为短期序列，更早的为长期历史。

### Benchmark 与结果

在Taobao-MM上，GLASS相比最强基线DualGR在R@1上提升21.57%（0.0372 vs 0.0306），N@3提升29.91%（0.0582 vs 0.0448），R@5提升19.59%，R@10提升14.03%，R@20提升15.02%，N@5提升15.74%，N@10提升19.75%，N@20提升21.00%。在KuaiRec上，R@1提升4.94%（0.0467 vs 0.0445），N@3提升4.27%（0.0659 vs 0.0632），各指标提升幅度在3.81%-4.94%之间。Taobao-MM提升更显著，归因于其高质量多模态特征带来的更优语义对齐。两周在线A/B测试（3%用户约1200万）显示：总使用时长+0.056%，人均使用时长+0.052%，召回率绝对提升3个百分点（95%置信水平）。



### 消融实验

ID-based基线：Caser、HGN、GRU4Rec、SASRec、Bert4Rec、S3-Rec、HSTU；SID-based基线：Tiger、DualGR。消融实验针对SID-Tier、语义硬搜索、门控融合等核心组件（RQ2-RQ4）。

## 总结

论文提出GLASS框架，将长期用户行为序列有效注入生成式推荐（GR）的自回归解码过程。

## References

- Coarse-to-Fine Long-term Interest Modeling for Generative Recommendation：[arXiv 2602.05663](https://arxiv.org/abs/2602.05663)

- [PDF源文件](/papers/2602.05663.pdf)
