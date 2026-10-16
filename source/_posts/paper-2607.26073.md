---
title: "高德生成式下一兴趣点推荐"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.26073
arxiv_id: "2607.26073"
description: "论文提出Gwhere，一个端到端的生成式下一兴趣点（POI）推荐框架，旨在解决生成式检索在工业场景中面临的令牌分配冗余/冲突及异构信号融合不足的问题。"
---

> 论文：[arXiv 2607.26073](https://arxiv.org/abs/2607.26073) · 代码：[GitHub](https://github.com/alibaba/SimCIT) · PDF：[本地阅读](/papers/2607.26073.pdf)

论文提出Gwhere，一个端到端的生成式下一兴趣点（POI）推荐框架，旨在解决生成式检索在工业场景中面临的令牌分配冗余/冲突及异构信号融合不足的问题。Gwhere首先通过对比残差量化分词器学习具有判别性的多模态语义ID（SID），融合文本、视觉、空间和协同信号；然后基于SID，通过持续预训练、监督微调（SFT）和曝光感知Kahneman-Tversky优化（EAKTO）将LLM适配到移动领域。在公开数据集和高德大规模工业数据集上的实验表明，Gwhere显著优于基线，并已部署于高德首页服务，长期A/B测试中P-CTR提升5.83%，U-CTR提升6.20%。

## 研究问题

论文提出Gwhere，一个端到端的生成式下一兴趣点（POI）推荐框架，旨在解决生成式检索在工业场景中面临的令牌分配冗余/冲突及异构信号融合不足的问题。Gwhere首先通过对比残差量化分词器学习具有判别性的多模态语义ID（SID），融合文本、视觉、空间和协同信号；然后基于SID，通过持续预训练、监督微调（SFT）和曝光感知Kahneman-Tversky优化（EAKTO）将LLM适配到移动领域。在公开数据集和高德大规模工业数据集上的实验表明，Gwhere显著优于基线，并已部署于高德首页服务，长期A/B测试中P-CTR提升5.83%，U-CTR提升6.20%。

## 方法：核心思路与整体框架

Gwhere将下一POI预测转化为自回归生成SID序列的问题。首先，通过对比残差量化分词器将多模态POI特征（文本、图像、空间、协同）融合并量化为紧凑的SID元组；然后，基于SID序列，使用Qwen2.5作为基础LLM，通过持续预训练（掩码SID预测和SID-属性对齐）注入时空知识，再通过SFT学习推荐逻辑，最后通过EAKTO进行偏好对齐。推理时，模型生成目标SID并通过查找表映射回POI。

![图 1：Figure 1: Ofline Training and Online Serving Procedure of proposed framework Gwhere. Ofline Training:(1) POIs are tokenized as Semantic IDs (SIDs); (2) a base LLM is continually pretrained on the collected corpus. (3) The LLM is further fine-tuned and aligned the with inference prompt to finish this procedure. Online Serving: Gwhere is stored in a model engine and invoked through a data-service engine that converts real-time context—user profile, recent check-ins, current time, location and weather—into an instruction prompt. The model predicts the next POI in SID form, which is mapped back to a readable location and returned to the mobile client.](/images/papers/2607.26073/9763bee4fc97cac195f66407d8b739af7a16c4d51cfa29828a61c11f9d9f64d4.jpg)

*图 1 · 原图说明：Figure 1: Ofline Training and Online Serving Procedure of proposed framework Gwhere. Ofline Training:(1) POIs are tokenized as Semantic IDs (SIDs); (2) a base LLM is continually pretrained on the collected corpus. (3) The LLM is further fine-tuned and aligned the with inference prompt to finish this procedure. Online Serving: Gwhere is stored in a model engine and invoked through a data-service engine that converts real-time context—user profile, recent check-ins, current time, location and weather—into an instruction prompt. The model predicts the next POI in SID form, which is mapped back to a readable location and returned to the mobile client.*

**图示解释：** Gwhere将下一POI预测转化为自回归生成SID序列的问题。

## 创新点

1. 提出完全对比式的语义分词框架，结合可学习残差量化与层次化标识符学习，融合文本、视觉、空间和协同等多模态POI信号，通过对比损失（NT-Xent）替代重构损失，增强令牌判别性并缓解长尾POI的表示坍塌问题。
2. 设计端到端LLM生成式下一POI预测框架Gwhere，通过持续预训练（掩码SID预测和SID-属性对齐）、监督微调（SFT）和曝光感知Kahneman-Tversky优化（EAKTO）三阶段训练，使LLM适配移动领域并实现认知对齐的推荐。
3. 提出EAKTO强化学习目标，利用曝光但未点击的POI作为E-Neg信号，在标签不平衡下有效利用曝光数据，平衡用户参与度与负面反馈抑制，实验证明其优于DPO和GRPO。
4. 在工业级部署中采用预填充-解码解耦和多令牌预测等工程优化，满足高并发低延迟要求，并通过大规模在线A/B测试验证了长期效果。

## 实验：数据、基线与结果

### 数据集与设置

任务为下一POI预测。数据集包括三个公开数据集（Foursquare-NYC、Foursquare-TKY、Gowalla-CA）和一个高德工业数据集（AMAP）。预处理：移除交互少于10次的POI和签到少于10次的用户，按时间排序，按80%/10%/10%划分训练/验证/测试集。测试集中移除训练集中未出现的用户和POI。每个用户最后一次访问作为真值，之前访问作为输入序列。AMAP数据集包含1000万用户、8310万POI、3.8亿交互，平均序列长度38。

### Benchmark 与结果

离线实验中，Gwhere在所有数据集上显著优于基线。在NYC、TKY、CA数据集上，Gwhere-7B相比SOTA GNPR-SID分别提升11.3%、8.1%、13.2%（Acc@1）。在AMAP数据集上，Gwhere-7B相比级联排序基线Acc@1相对提升14.8%。消融实验显示，移除SID、RL、CPT分别导致Acc@1下降16.01%、11.73%、9.96%。偏好对齐中，EAKTO（0.2820）优于GRPO（0.2759）和DPO（0.2634）。在线A/B测试中，Gwhere相比生产基线P-CTR提升5.83%，U-CTR提升6.20%，AC-Rate提升9.67%，NF-Rate降低11.11%。



### 消融实验

对比方法包括：传统方法PRME、PLSPL；Transformer方法STAN、GETNext；GCN方法STHGCN；时间感知方法TPG、ROTAN；LLM方法LLM4POI、GNPR-SID。消融实验包括：w/o SID（随机ID）、w/o ST（无时空描述）、w/o SLD（无SID-位置-描述语料）、w/o CPT（无持续预训练）、w/o SFT、w/o RL。偏好对齐对比：SFT-only、SFT+DPO、SFT+GRPO、SFT+EAKTO。

## 总结

论文提出Gwhere，一个端到端的生成式下一兴趣点（POI）推荐框架，旨在解决生成式检索在工业场景中面临的令牌分配冗余/冲突及异构信号融合不足的问题。

## References

- Guess Where You Go: Generative Next Point-of-Interest Recommendation in Amap：[arXiv 2607.26073](https://arxiv.org/abs/2607.26073)

- [代码：GitHub](https://github.com/alibaba/SimCIT)
- [PDF源文件](/papers/2607.26073.pdf)
