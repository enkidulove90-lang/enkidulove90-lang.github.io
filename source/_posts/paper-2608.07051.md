---
title: "YOLO-PEFT：YOLO系列参数高效微调"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.07051
arxiv_id: "2608.07051"
description: "论文提出YOLO-PEFT，一个面向异构实时检测器的结构感知参数高效微调（PEFT）框架。"
---

> 论文：[arXiv 2608.07051](https://arxiv.org/abs/2608.07051) · 代码：[GitHub](https://github.com/huggingface/peft) · 代码：[GitHub](https://github.com/ultralytics/ult) · PDF：[本地阅读](/papers/2608.07051.pdf)

论文提出YOLO-PEFT，一个面向异构实时检测器的结构感知参数高效微调（PEFT）框架。它将适配器放置形式化为多约束规划问题，通过解析检测器图、分配算子与语义角色、过滤不安全目标、在预算下分配秩、校准失败风险，并在无可靠方案时返回Refuse。框架覆盖训练、仅适配器检查点保存、权重合并及ONNX/TensorRT导出的完整生命周期。在VOC协议下，规划器选择的LoRA在YOLO11s和YOLO12s上分别超过全量微调7.1和6.5 mAP50:95，同时降低43.9%峰值显存，但训练时间增加1.72倍。

## 研究问题

论文提出YOLO-PEFT，一个面向异构实时检测器的结构感知参数高效微调（PEFT）框架。它将适配器放置形式化为多约束规划问题，通过解析检测器图、分配算子与语义角色、过滤不安全目标、在预算下分配秩、校准失败风险，并在无可靠方案时返回Refuse。框架覆盖训练、仅适配器检查点保存、权重合并及ONNX/TensorRT导出的完整生命周期。在VOC协议下，规划器选择的LoRA在YOLO11s和YOLO12s上分别超过全量微调7.1和6.5 mAP50:95，同时降低43.9%峰值显存，但训练时间增加1.72倍。

## 方法：核心思路与整体框架

YOLO-PEFT将检测器表示为有向无环图，每个模块由算子元数据、语义角色、图接口元数据和部署元数据描述。规划器按固定顺序执行：算子过滤、语义过滤、架构策略应用、预算感知秩分配和可靠性校准。通过约束满足返回接受计划或Refuse，并将接受的计划降低到统一的训练-保存-合并-导出运行时。

![图 1：Fig. 3. Architecture-conditioned PEFT behavior. ∆mAP versus Full-SFT for 14 variants on five heterogeneous detectors. Red cells are catastrophic $( \Delta < - 0 . 0 5 )$ ; gray denotes not swept and colors clip below −0.30. The catastrophe rate rises with $\phi _ { \mathrm { a t t n } } ,$ and no common ranking survives across the five evaluated families.](/images/papers/2608.07051/9f8f7e1cff9b53a20ffa7ddd3bf25d3d4c5477019d61846a4e35ad01fc541770.jpg)

*图 1 · 原图说明：Fig. 3. Architecture-conditioned PEFT behavior. ∆mAP versus Full-SFT for 14 variants on five heterogeneous detectors. Red cells are catastrophic $( \Delta < - 0 . 0 5 )$ ; gray denotes not swept and colors clip below −0.30. The catastrophe rate rises with $\phi _ { \mathrm { a t t n } } ,$ and no common ranking survives across the five evaluated families.*

**图示解释：** YOLO-PEFT将检测器表示为有向无环图，每个模块由算子元数据、语义角色、图接口元数据和部署元数据描述。

## 创新点

1. 将检测器PEFT重新定义为异构计算图上的多约束规划问题，联合考虑算子有效性、检测语义、图接口、部署兼容性和参数预算约束，而非仅按模块名称或类型选择目标。
2. 提出双角色图解析器与10维架构指纹，为每个模块分配算子角色和语义角色，识别DFL投影、MoE路由、文本融合等检测器特有组件，并基于校准覆盖范围进行训练前风险估计，支持Refuse作为一等规划结果。
3. 建立部署完整的运行时契约，支持训练、仅适配器持久化、重载、权重合并及ONNX/TensorRT导出，并证明分组卷积LoRA后端在合并后移除包装器可保持卷积输出在数值容差内等价。
4. 通过14种PEFT变体与5种检测器架构的系统性诊断，揭示PEFT可靠性强烈依赖架构而非存在通用排序，并给出架构条件化的放置策略与拒绝规则。

## 实验：数据、基线与结果

### 数据集与设置

目标检测任务。训练集为VOC2007 trainval（5,011张）与VOC2012 trainval（11,540张）的并集，共16,551张图像；测试集为官方VOC2007 test，4,952张图像。核心s-scale运行使用600 epoch上限和640×640输入；14变体×5架构诊断扫描使用300 epoch和320×320输入。

### Benchmark 与结果

在VOC协议下，规划器选择的RS-LoRA在YOLO11s上达到0.7138 mAP50:95，超过Full-SFT的0.6428（+0.0710）；在YOLO12s上达到0.7307，超过Full-SFT的0.6662（+0.0645）。HRA在YOLO11s和YOLO12s上分别达到0.7276和0.7453。RT-DETR-L上所有7种LoRA族配置均低于灾难阈值Δ=-0.05，规划器返回Refuse。受控YOLO11审计显示LoRA降低峰值显存43.9%（28.57→16.03 GB），但训练时间增加1.72倍（118.2→203.8秒）。合并后YOLO11s延迟从27.719ms降至17.933ms，吞吐量从36.076提升至55.763 img/s。



### 消融实验

对比方法包括Full-SFT、标准LoRA、Planner-LoRA、最佳PEFT和朴素放置。评估的PEFT变体包括LoRA、DoRA、LoHa、LoKr、IA3、HRA、RS-LoRA等。消融设置包括无RS-LoRA缩放、DoRA转换、不同秩（8/16/32）等。

## 总结

论文提出YOLO-PEFT，一个面向异构实时检测器的结构感知参数高效微调（PEFT）框架。

## References

- YOLO-PEFT: Parameter-Efficient Fine-Tuning on YOLO Family：[arXiv 2608.07051](https://arxiv.org/abs/2608.07051)

- [代码：GitHub](https://github.com/huggingface/peft)
- [代码：GitHub](https://github.com/ultralytics/ult)
- [PDF源文件](/papers/2608.07051.pdf)
