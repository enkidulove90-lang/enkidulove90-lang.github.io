---
title: "序列引导的通用多模态优先级计算框架"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.28503
arxiv_id: "2608.28503"
description: "论文提出SG-UMP，一个即插即用的多模态序列推荐增强框架，旨在解决现有方法中用户级偏好异质性和数据集级模态偏差两大问题。"
---

> 论文：[arXiv 2608.28503](https://arxiv.org/abs/2608.28503) · 代码：[GitHub](https://github.com/esemsc-xz524/SG-UMP) · PDF：[本地阅读](/papers/2608.28503.pdf)

论文提出SG-UMP，一个即插即用的多模态序列推荐增强框架，旨在解决现有方法中用户级偏好异质性和数据集级模态偏差两大问题。SG-UMP包含模块组合器（Module Combiner）和模块路由器（Module Router）：前者集成频率滤波层、层次注意力层和多尺度融合层三种功能模块，后者根据数据集级模态特征动态决定模块执行顺序。在四个真实数据集上的实验表明，SG-UMP可无缝集成到SASRec、STOSA、Oracle4Rec等不同序列推荐骨干中，平均提升18.91%-24.93%，验证了其有效性、通用性和可扩展性。

## 研究问题

论文提出SG-UMP，一个即插即用的多模态序列推荐增强框架，旨在解决现有方法中用户级偏好异质性和数据集级模态偏差两大问题。SG-UMP包含模块组合器（Module Combiner）和模块路由器（Module Router）：前者集成频率滤波层、层次注意力层和多尺度融合层三种功能模块，后者根据数据集级模态特征动态决定模块执行顺序。在四个真实数据集上的实验表明，SG-UMP可无缝集成到SASRec、STOSA、Oracle4Rec等不同序列推荐骨干中，平均提升18.91%-24.93%，验证了其有效性、通用性和可扩展性。

## 方法：核心思路与整体框架

SG-UMP将多模态序列推荐中的多模态嵌入处理分解为三个可重排序的功能模块：频率滤波层通过FFT/IFFT提取低频稳定模式并抑制高频噪声；层次注意力层通过MLP+Sigmoid计算模态重要性并利用自注意力细化表示；多尺度融合层采用MoE框架，结合模态独有专家和模态共享专家进行自适应融合。Module Router根据输入的多模态组成计算各模块的调度分数并排序，确定执行顺序，同时通过条件互信息损失正则化路由行为。模型以BPR损失和CMI正则化联合训练。

![图 1：Figure 2: Illustration of SG-UMP and its components. (a) Overall framework of SG-UMP, where the Module Combiner integrates the Frequency Filter Layer, Hierarchical Attention Layer, and Multi-Scale Fusion Layer. (b) Module Router structure. (c) Frequency Filter Layer. (d) Hierarchical Attention Layer. (e) Multi-Scale Fusion Layer.](/images/papers/2608.28503/fccd40f3d44c3b8fc4af3a058854104d2f2aaeb41e49683dde42bd3fb3d2fc8f.jpg)

*图 1 · 原图说明：Figure 2: Illustration of SG-UMP and its components. (a) Overall framework of SG-UMP, where the Module Combiner integrates the Frequency Filter Layer, Hierarchical Attention Layer, and Multi-Scale Fusion Layer. (b) Module Router structure. (c) Frequency Filter Layer. (d) Hierarchical Attention Layer. (e) Multi-Scale Fusion Layer.*

**图示解释：** SG-UMP在四个数据集上一致优于所有基线。

## 创新点

1. 提出两条多模态序列推荐设计原则：一是利用用户历史交互序列引导个性化多模态表示处理以建模用户级偏好异质性；二是支持模块化、可重排序的处理流程以适应不同数据集的模态偏差。
2. 设计Module Combiner，集成频率滤波层（去噪并提取稳定低频模式）、层次注意力层（自适应融合模态信号）和多尺度融合层（基于MoE建模模态间交互），形成完整的多模态嵌入处理流水线。
3. 提出Module Router，通过模态感知路由机制动态确定三个功能模块的执行顺序，并引入条件互信息（CMI）正则化损失，鼓励输入感知和多样化的路由策略，防止退化为固定执行路径。
4. 将SG-UMP设计为即插即用插件，不替换序列推荐骨干本身，而是增强现有多模态序列推荐模型的多模态信息处理能力，在多种骨干和数据集上均取得一致提升。

## 实验：数据、基线与结果

### 数据集与设置

任务为多模态序列推荐（MSR），预测用户下一个交互物品。使用四个数据集：Amazon Home（66,519用户，28,237物品，551,682交互，密度0.03%，平均长度8.3）、Amazon Beauty（22,363用户，12,101物品，198,502交互，密度0.05%，平均长度8.3）、Amazon Office（4,905用户，2,421物品，53,258交互，密度0.04%，平均长度10.8）、Yelp（287,116用户，148,523物品，4,392,169交互，密度0.01%，平均长度15.3）。所有数据集采用5-core预处理，确保每个用户和物品至少有5次交互。采用leave-one-out划分策略：每个用户序列最后一个物品用于测试，倒数第二个用于验证，其余用于训练。

### Benchmark 与结果

SG-UMP在四个数据集上一致优于所有基线。集成到SASRec平均提升21.96%，集成到STOSA平均提升24.93%，集成到Oracle4Rec平均提升18.91%。消融实验表明，移除任一模块均导致性能下降，其中移除层次注意力层在Beauty和Office上退化最大，说明细粒度用户偏好建模的重要性。模块顺序实验显示最优执行顺序因数据集而异（Home为c-b-a，Beauty为b-a-c，Office为a-c-b，Yelp为a-b-c），证实了自适应路由的必要性。训练时间方面，SG-UMP带来的额外开销可控，如SASRec在Home上从20.35s增至29.23s，在Yelp上从735.32s增至772.53s。

![图 2：Figure 3: Visualization analysis. ${ ( \mathbf { a } ) , ( \mathbf { b } ) } .$ , and (c) correspond to STOSA with pre-trained embeddings, the approximated user perspective based on salient item features, and SG-UMP + STOSA, respectively. Red text highlights important attributes, and the intensity of the green background indi cates attention assigned by the model.](/images/papers/2608.28503/eeacc17bf8c64c866f69b8b9e229ef0cfff7cd5e15ab77667c09c23c3c6f3680.jpg)

*图 2 · 原图说明：Figure 3: Visualization analysis. ${ ( \mathbf { a } ) , ( \mathbf { b } ) } .$ , and (c) correspond to STOSA with pre-trained embeddings, the approximated user perspective based on salient item features, and SG-UMP + STOSA, respectively. Red text highlights important attributes, and the intensity of the green background indi cates attention assigned by the model.*

**图示解释：** SG-UMP在四个数据集上一致优于所有基线。

### 消融实验

对比方法分为两类：（1）传统推荐：SASRec、BERT4-Rec、LightGCN、STOSA、FMLP-Rec、Oracle4Rec；（2）多模态推荐：VBPR、MMMLP、MML、MMSR、MMSBR、MP4SR。消融实验在STOSA上分别移除频率滤波层（w/o Filter）、层次注意力层（w/o Attention）和多尺度融合层（w/o MOE）。模块顺序实验评估三个核心模块的全部六种排列组合。

## 总结

论文提出SG-UMP，一个即插即用的多模态序列推荐增强框架，旨在解决现有方法中用户级偏好异质性和数据集级模态偏差两大问题。

## References

- SG-UMP: Sequence-Guided Universal Multimodal Prioritization Calculation Framework：[arXiv 2608.28503](https://arxiv.org/abs/2608.28503)

- [代码：GitHub](https://github.com/esemsc-xz524/SG-UMP)
- [PDF源文件](/papers/2608.28503.pdf)
