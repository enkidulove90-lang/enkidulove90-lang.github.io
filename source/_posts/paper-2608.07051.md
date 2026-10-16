---
title: "YOLO-PEFT: Parameter-Efficient Fine-Tuning on YOLO Family"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.07051
arxiv_id: "2608.07051"
---

## 一、简介

Generic parameter-eficient fine-tuning (PEFT) methods transferred from language models can fail silently on real-time detectors, whose heterogeneous operators and detection-specific components impose placement constraints absent from regular Transformer stacks. We propose YOLO-PEFT, a structure-aware framework that formulates adapter placement as an auditable constraint-planning problem. Given a detector graph, a PEFT request, and a resource budget, YOLO-PEFT assigns operator and semantic roles, evaluates explicit operator-validity, detector-semantic, graph-interface, and deployment predicates, records a reason code for each excluded module, and either emits a budgeted target-module plan or returns Refuse before training. Under the oficial VOC07+12 trainval-to-VOC07 test protocol, planner-selected RS-LoRA reaches 0.7138 and 0.7307 mAP50-95 on YOLO11s and YOLO12s, respectively, compared with 0.6428 and 0.6662 for Full-SFT. On RT-DETR-L, all seven evaluated LoRA-family configurations cross the predefined catastrophic threshold, supporting a calibrated Refuse-to-Full-SFT decision within the evaluated coverage. A controlled YOLO11 audit further shows that LoRA reduces peak training memory by 43.9 percent, although training takes 1.72 times longer. Within the evaluated detector families, placement policies, and calibration coverage, YOLO-PEFT replaces manual target-module trial and error with explicit, inspectable planning while preserving verified train-save-merge-export paths; refusal on unseen detector architectures remains an open validation problem.

Project Page: github.com/Tencent/YOLO-Master

## 二、论文方法

The evaluated detector families contain heterogeneous operators and task-specific dense heads, so languagemodel PEFT rules cannot be transferred by matching module names alone. YOLO-PEFT instead treats adapter placement as a constrained decision problem: given a detector graph, a PEFT request, and a parameter budget, it returns a structurally valid, trainable, and deployable plan, or refuses the request when no admissible plan exists within the implemented rules and calibration coverage. The pipeline proceeds in four stages: parse the detector, resolve a constraint-valid placement, lower the plan into the YOLO runtime, and apply compatible training strategies. Complete pseudocode and implementation details are provided in the supplementary materials.

## 三、论文里的图与解释

### 图 1

![Fig. 3. Architecture-conditioned PEFT behavior. ∆mAP versus Full-SFT for 14 variants on five heterogeneous detectors. Red cells are catastrophic $( \Delta < - 0 . 0 5 )$ ; gray denotes not swept and colors clip below −0.30. The catastrophe rate rises with $\phi _ { \mathrm { a t t n } } ,$ and no common ranking survives across the five evaluated families.](/images/papers/2608.07051/9f8f7e1cff9b53a20ffa7ddd3bf25d3d4c5477019d61846a4e35ad01fc541770.jpg)

**原图说明：** Fig. 3. Architecture-conditioned PEFT behavior. ∆mAP versus Full-SFT for 14 variants on five heterogeneous detectors. Red cells are catastrophic $( \Delta < - 0 . 0 5 )$ ; gray denotes not swept and colors clip below −0.30. The catastrophe rate rises with $\phi _ { \mathrm { a t t n } } ,$ and no common ranking survives across the five evaluated families.

**图示解释：** 该图对应论文中的“Fig. 3. Architecture-conditioned PEFT behavior. ∆mAP versus Full-SFT for 14 variants on five heterogeneous detectors. Red cells are catastrophic $( \Delta < - 0 . 0 5 )$ ; gray denotes not swept and colors clip below −0.30. The catastrophe rate rises with $\phi _ { \mathrm { a t t n } } ,$ and no common ranking survives across the five evaluated families.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 将检测器PEFT重新定义为异构计算图上的多约束规划问题，联合考虑算子有效性、检测语义、图接口、部署兼容性和参数预算约束，而非仅按模块名称或类型选择目标。
2. 提出双角色图解析器与10维架构指纹，为每个模块分配算子角色和语义角色，识别DFL投影、MoE路由、文本融合等检测器特有组件，并基于校准覆盖范围进行训练前风险估计，支持Refuse作为一等规划结果。
3. 建立部署完整的运行时契约，支持训练、仅适配器持久化、重载、权重合并及ONNX/TensorRT导出，并证明分组卷积LoRA后端在合并后移除包装器可保持卷积输出在数值容差内等价。
4. 通过14种PEFT变体与5种检测器架构的系统性诊断，揭示PEFT可靠性强烈依赖架构而非存在通用排序，并给出架构条件化的放置策略与拒绝规则。

## 五、实验数据集选择

- PASCAL VOC 2007+2012 trainval → VOC 2007 test
- YOLO11s
- YOLO12s
- RT-DETR-L
- YOLO-World
- YOLO-Master-EsMoE-S

## 六、消融实验

Efectiveness of Planner Constraints. We isolate the performance contributions of individual planner components on YOLO12s. As detailed in Supplementary Table 11, a naive baseline without constraints yields 0.6900 m $\mathrm { A P _ { 5 0 - 9 5 } }$ . Introducing operator validity filtering to exclude depthwise and normalization layers elevates the accuracy to 0.7094. Incorporating detection-head semantic exclusions provides the largest stability leap, driving the performance to 0.7307 mAP, which supports semantic guards as stability drivers rather than mere engineering safeguards.

Predicate-level diagnostics. Table 5 separates an applicable constraint from a constraint that is merely present in the rule set. On YOLO12s, opening the attention-stream rule admits 32 modules and raises the mean adapter-gradient norm by 1.581×; opening the typed-head rule admits 18 modules and raises it by 1.091×. Neither short run produces non-finite gradients, so the evidence supports changed optimization pressure rather than inevitable collapse. Conversely, the depthwise predicate admits no additional rank-4 target on either audited graph and therefore cannot be credited with a training efect here. The single DFL projection, 12 deformable-sampling/attention-weight layers, and 28 RT-DETR score/bbox output layers remain counterfactual candidates: their fixed-bin, sampling-geometry, or output-bias semantics make direct insertion a diferent intervention, not an ordinary leave-one-out switch.

![](images/9f8f7e1cff9b53a20ffa7ddd3bf25d3d4c5477019d61846a4e35ad01fc541770.jpg)  
Fig. 3. Architecture-conditioned PEFT behavior. ∆mAP versus Full-SFT for 14 variants on five heterogeneous detectors. Red cells are catastrophic $( \Delta < - 0 . 0 5 )$ ; gray denotes not swept and colors clip below −0.30. The catastrophe rate rises with $\phi _ { \mathrm { a t t n } } ,$ and no common ranking survives across the five evaluated families.

Downstream decoder drift under safe placement. We compare an RT-DETR-L VOC checkpoint with its safe adapter active against the same checkpoint with adapter parameters zeroed. Through the supported predictor path, 16 fixed VOC2007 images produce finite 300×6 outputs. Relative $\ell _ { 2 }$ drift is $0 . 5 5 3 { \pm } 0 . 0 9 9$ in decoder modules, 0.530±0.103 in MSDeformAttn, 0.613±0.100 in bbox heads, and 0.127±0.033 in score heads; final-output drift is $0 . 5 4 8 { \pm } 0 . 0 9 4$ (median 0.571, P90 0.611). Safe upstream adaptation therefore propagates into the frozen decoder, but these 16-image, 1%-training diagnostics do not validate unsafe decoder insertion

or replace the core protocol.

Rank Sensitivity Analysis. Supplementary Table 13 evaluates the accuracy-cost trade-ofs across diferent rank budgets where $r \in \{ 8 , 1 6 , 3 2 \}$ on YOLO12s. Increasing the rank from 8 to 16 improves the mAP from 0.7288 to 0.7307. Scaling further to r = 32 ofers diminishing returns yielding 0.7363 mAP at a substantially higher parameter and computational overhead, supporting r = 16 as a practical Pareto point for real-time detectors.

Necessity of Runtime Contract. We ablate the contract layer against a naive wrapper substitution. While both approaches reach an identical 0.7138 mAP with YOLO11s, Supplementary Table 10 demonstrates that the naive substitution breaks downstream deployment pipelines, including ONNX/TensorRT export and standard checkpoint saving. Our Contract layer satisfies the checkpoint, merge, and ONNX invariants; after merging, the adapter branch is removed, so the exported graph has base-model operator cost.

Interaction of Training Priors. We conduct a 2 × 2 factorial ablation on YOLO12s to examine the interplay between RS-LoRA scaling and DoRA’s magnitude decomposition. Supplementary Table 15 reveals that training priors interact non-additively, showing that enabling DoRA without RS-LoRA scaling triggers a collapse to 0.6112 mAP. This empirical finding underscores the need to report the joint training configuration rather than isolated prior settings. Results are therefore interpreted by protocol: the core matrix, diagnostic architecture sweep, and controlled VRAM/time audit are not pooled, and the planner treats disabled-expert MoE tests and RT-DETR-L refusal as separately scoped outcomes.

## 七、Benchmark 结果与解释

- PASCAL VOC 2007+2012 trainval → VOC 2007 test
- YOLO11s
- YOLO12s
- RT-DETR-L
- YOLO-World
- YOLO-Master-EsMoE-S

## 八、总结

We presented YOLO-PEFT, which parses detector graphs from the supported, evaluated families, resolves adapter placements under operator, semantic, and budget constraints, and lowers accepted plans into a mergeable and export-compatible runtime. Under the oficial VOC07+12 trainval→VOC07 test protocol, accepted YOLO11s and YOLO12s plans match or exceed Full-SFT. Our controlled YOLO11 audit measures 43.9% lower LoRA peak VRAM but 1.72× longer training. Externally sourced storage and distribution estimates are intentionally excluded from the core claims. RT-DETR-L’s Refuse→Full-SFT fallback is excluded from these PEFT aggregates. Stability remains architecture-conditioned, and held-out-architecture validation of refusal remains future work.

The supplied seed-0 YOLO-Master-EsMoE-S export adds a scoped MoE stress test: with planner, router, expert, attention, and head targeting disabled, HRA reaches 0.7454 mAP versus the logged Full-SFT value 0.6891, whereas BOFT and OFT terminate without metrics. This supports compatibility with a conv-only MoE host subset, not an expert-aware planner claim. More broadly, the current evidence is limited to VOC and the evaluated families; COCO/domain-shift evaluation, region-only fine-tuning baselines, and held-out-family false-refusal/false-acceptance estimates remain necessary.

For practice, the result is a decision rule within the implemented constraints and calibration coverage, rather than a universal adapter recommendation. A planner-selected adapter should be used only after operator and semantic checks pass; refusal before training is supported only for evaluated or calibrated architecture–method regimes. Future work will extend this rule to VLM detectors with cross-modal attention and vocabulary heads, and to mixture-of-transformers (MoT/MoE) detectors with shared blocks, expert-local adapters, router load balancing, and dispatch-aware budgets. We will test these extensions on held-out architectures and cross-domain benchmarks, including merged and unmerged export checks.

![](images/cdcaf76535e8e06cc31a6cd4747687922c5e63456f04ca527f773f0c9575cd66.jpg)  
Fig. 4. Paper-measured controlled YOLO11 systems audit. Relative to Full-SFT, LoRA lowers peak VRAM from 28.57 to 16.03 GB (43.9%) but increases training time from 118.2 to 203.8 s (1.72×); all displayed PEFT variants are slower than Full-SFT.

Tab. 6. MPS deployment audit on controlled YOLO11s and YOLO12s checkpoints.

<table><tr><td>Backbone</td><td>Mode</td><td>Params</td><td>Adapter Params</td><td>GFLOPs</td><td>Latency (ms)</td><td>Throughput (img/s)</td><td>MPS Δ (MB)</td></tr><tr><td>YOLO11s</td><td>unmerged</td><td>10.491M</td><td>1.033M</td><td>25.891</td><td>27.719</td><td>36.076</td><td>1024</td></tr><tr><td>YOLO11s</td><td>merged</td><td>9.459M</td><td>0</td><td>21.718</td><td>17.933</td><td>55.763</td><td>1024</td></tr><tr><td>YOLO12s</td><td>unmerged</td><td>10.380M</td><td>1.094M</td><td>26.199</td><td>35.095</td><td>28.494</td><td>8</td></tr><tr><td>YOLO12s</td><td>merged</td><td>9.286M</td><td>0</td><td>21.692</td><td>24.881</td><td>40.191</td><td>8</td></tr></table>

## References

[1] Hao Chen, Ran Tao, Han Zhang, Yidong Wang, Xiang Li, Wei Ye, Jindong Wang, Guosheng Hu, and Marios Savvides. Conv-Adapter: Exploring parameter eficient transfer learning for ConvNets. In CVPR Workshops, pages 1551–1561, 2024. doi: 10.1109/CVPRW63382.2024.00162. URL https://arxiv.org/abs/2208.07463.

[2] Shoufa Chen, Chongjian Ge, Zhan Tong, Jiangliu Wang, Yibing Song, Jue Wang, and Ping Luo. AdaptFormer: Adapting vision transformers for scalable visual recognition. In NeurIPS, 2022.

[3] Zheng Chen, Yu Zeng, Zehui Chen, Hongzhi Gao, Lin Chen, Jiaming Liu, and Feng Zhao. VFM-Adapter: Adapting visual foundation models for dense prediction with dynamic hybrid operation mapping. In AAAI, volume 39, pages 2385–2393, 2025. doi: 10.1609/aaai.v39i3.32239. URL https://ojs.aaai.org/index.php/AAAI/article/ view/32239.

[4] Tianheng Cheng, Lin Song, Yixiao Ge, Wenyu Liu, Xinggang Wang, and Ying Shan. YOLO-World: Real-time open-vocabulary object detection. In CVPR, 2024.

[5] Mark Everingham, S. M. Ali Eslami, Luc Van Gool, Christopher K. I. Williams, John Winn, and Andrew Zisserman. The PASCAL visual object classes challenge: A retrospective. International Journal of Computer Vision, 111:98–136, 2015.

[6] Bilal Faye, Hanane Azzag, and Mustapha Lebbah. Lightweight modular parameter-eficient tuning for openvocabulary object detection, 2024. URL https://arxiv.org/abs/2408.10787.

[7] Weifu Fu, Jinyang Li, Bin-Bin Gao, Jialin Li, Yuhuan Lin, Hanqiu Deng, Wenbing Tao, Yong Liu, and Chengjie Wang. Pet-dino: Unifying visual cues into grounding dino with prompt-enriched training. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 13039–13048, June 2026.

[8] Kanoko Goto, Takumi Karasawa, Takumi Hirose, Rei Kawakami, and Nakamasa Inoue. Multi-point positional insertion tuning for small object detection. In ICASSP, pages 1–5, 2025. doi: 10.1109/ICASSP49660.2025.10888925. URL https://arxiv.org/abs/2412.18090

[9] Zeyu Han, Chao Gao, Jinyang Liu, Jef Zhang, and Sai Qian Zhang. Parameter-eficient fine-tuning for large models: A comprehensive survey, 2024.

[10] Haoyu He, Jianfei Cai, Jing Zhang, Dacheng Tao, and Bohan Zhuang. Sensitivity-aware visual parametereficient fine-tuning. In ICCV, pages 11791–11801, 2023. doi: 10.1109/ICCV51070.2023.01086. URL https: //arxiv.org/abs/2303.08566.

[11] Junxian He, Chunting Zhou, Xuezhe Ma, Taylor Berg-Kirkpatrick, and Graham Neubig. Towards a unified view of parameter-eficient transfer learning. In ICLR, 2022.

[12] Xuehai He, Chunyuan Li, Pengchuan Zhang, Jianwei Yang, and Xin Eric Wang. Parameter-eficient model adaptation for vision transformers. In AAAI, volume 37, pages 817–825, 2023. doi: 10.1609/aaai.v37i1.25160. URL https://ojs.aaai.org/index.php/AAAI/article/view/25160.

[13] Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and Weizhu Chen. LoRA: Low-rank adaptation of large language models. In ICLR, 2022.

[14] Menglin Jia, Luming Tang, Bor-Chun Chen, Claire Cardie, Serge Belongie, Bharath Hariharan, and Ser-Nam Lim. Visual prompt tuning. In ECCV, 2022.

[15] Shibo Jie, Zhi-Hong Deng, Shixuan Chen, and Zhijuan Jin. Convolutional bypasses are better vision transformer adapters. In ECAI, pages 202–209, 2024. doi: 10.3233/FAIA240489. URL https://arxiv.org/abs/2207.07039.

[16] Glenn Jocher, Ayush Chaurasia, and Jing Qiu. YOLOv8 by Ultralytics. https://github.com/ultralytics/ult ralytics, 2023. GitHub repository, Accessed: 2026-05-10.

[17] Glenn Jocher, Ayush Chaurasia, and Jing Qiu. YOLO11 by Ultralytics. https://github.com/ultralytics/ult ralytics, 2024. GitHub repository and documentation, Accessed: 2026-05-10.

[18] Haochen Li, Rui Zhang, Hantao Yao, Xin Zhang, Yifan Hao, Xinkai Song, Xiaqing Li, Yongwei Zhao, Ling Li, and Yunji Chen. DA-Ada: Learning domain-aware adapter for domain adaptive object detection. In NeurIPS, volume 37, pages 103574–103598, 2024. doi: 10.52202/079017-3289. URL https://arxiv.or

### 在线资源

- [论文：arXiv 2608.07051](https://arxiv.org/abs/2608.07051)
- [代码：GitHub](https://github.com/huggingface/peft)
- [代码：GitHub](https://github.com/ultralytics/ult)
- [PDF源文件](/papers/2608.07051.pdf)
