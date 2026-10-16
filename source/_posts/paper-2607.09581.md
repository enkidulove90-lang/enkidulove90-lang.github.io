---
title: "Wan-Dancer：分钟级连贯音乐到舞蹈生成的分层框架"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.09581
arxiv_id: "2607.09581"
description: "论文提出Wan-Dancer，一个分层全局到局部的音乐到舞蹈视频生成框架，旨在突破现有扩散模型20秒的时长限制。"
---

> 论文：[arXiv 2607.09581](https://arxiv.org/abs/2607.09581) · PDF：[本地阅读](/papers/2607.09581.pdf)

论文提出Wan-Dancer，一个分层全局到局部的音乐到舞蹈视频生成框架，旨在突破现有扩散模型20秒的时长限制。该方法将生成过程解耦为全局关键帧规划和局部时间细化两个阶段，利用完整音乐上下文保证长程连贯性。核心创新包括：通过时间映射RoPE嵌入实现动态帧率适配以精确对齐任意时长音乐；引入光流损失增强运动连续性；采用运动速度控制在高动态场景下保持细节。实验表明，该框架可生成超过一分钟的720p/30fps稳定视频，在五种舞蹈风格上均达到最优性能。

## 研究问题

论文提出Wan-Dancer，一个分层全局到局部的音乐到舞蹈视频生成框架，旨在突破现有扩散模型20秒的时长限制。该方法将生成过程解耦为全局关键帧规划和局部时间细化两个阶段，利用完整音乐上下文保证长程连贯性。核心创新包括：通过时间映射RoPE嵌入实现动态帧率适配以精确对齐任意时长音乐；引入光流损失增强运动连续性；采用运动速度控制在高动态场景下保持细节。实验表明，该框架可生成超过一分钟的720p/30fps稳定视频，在五种舞蹈风格上均达到最优性能。

## 方法：核心思路与整体框架

基于Wan-I2V扩散Transformer架构，采用统一训练框架整合全局和局部学习目标。通过关键帧掩码拼接视频潜变量区分训练阶段：全局阶段仅首帧为1以模拟长程依赖建模；局部阶段随机选择关键帧位置为1以学习稀疏时间锚点下的运动合成。采用Rectified Flow公式建模生成过程，结合CLIP视觉条件、umT5文本嵌入和音乐编码器特征。推理时先全局生成38帧稀疏关键帧，再以149帧片段并行局部细化，最终拼接为完整视频。

![图 1：Inference Pipeline. Initially, the global stage synthesizes a sparse keyframe global video that captures the overall motion structure and rhythmic alignment. Subsequently, this global output serves as a structural guidance condition for the local stage, which interpolates and refines the sequence to generate the final high-frame-rate, dense video with enhanced temporal coherence and visual detail.](/images/papers/2607.09581/figure_001_pipeline_infer.png)

*图 1 · 原图说明：Inference Pipeline. Initially, the global stage synthesizes a sparse keyframe global video that captures the overall motion structure and rhythmic alignment. Subsequently, this global output serves as a structural guidance condition for the local stage, which interpolates and refines the sequence to generate the final high-frame-rate, dense video with enhanced temporal coherence and visual detail.*

**图示解释：** 基于Wan-I2V扩散Transformer架构，采用统一训练框架整合全局和局部学习目标。

## 创新点

1. 分层全局到局部生成架构：将音乐到舞蹈生成解耦为全局关键帧规划和局部时间细化两个阶段，利用完整音乐上下文进行长程节奏规划，有效消除时间漂移和重复性伪影。
2. 动态帧率适配机制：将绝对时间标识符集成到旋转位置嵌入（RoPE）中，使模型能够根据音乐总时长动态生成关键帧序列，实现精确的时间对齐，支持从15fps到3fps的灵活采样。
3. 基于光流损失的运动连续性增强：引入SEA-RAFT光流约束作为损失函数权重，显著提升快速运动场景下的空间一致性和边缘保真度，减少运动模糊和结构失真。
4. 基于LoRA的高效编舞定制：采用低秩适配（LoRA）微调策略，仅需16个参考视频即可快速复现特定舞蹈动作，无需大规模重训练或数据集。
5. 运动速度分层训练策略：将训练样本按运动速度分为慢、中、高三档（10%/80%/10%），优先学习自然的中速动态，实现推理时通过文本提示精确控制运动速度。

## 实验：数据、基线与结果

### 数据集与设置

任务为音乐到舞蹈视频生成。使用自建约200小时专有数据集，最低分辨率720p/30fps，涵盖五种舞蹈风格，时间分布近乎均匀。训练时将原始视频分割为5秒片段，50%重叠。使用Librosa提取音频特征，SEA-RAFT生成光流掩码。按运动速度分层：慢10%、中80%、高10%。未使用AIST和Finedance数据集。

### Benchmark 与结果

在舞蹈质量指标上，Wan-Dancer平均得分8.46，显著优于MusicInfuser（6.23）和X-Dancer（6.06）。具体而言：风格对齐8.33 vs 7.43/6.55，节拍对齐8.73 vs 7.26/6.78，身体表征9.01 vs 4.76/6.23，运动真实感9.23 vs 6.89/6.11，编舞复杂度6.98 vs 4.80/4.63。视频质量平均7.46 vs 5.22/6.23，其中成像质量6.84 vs 5.03/5.23，美学质量7.91 vs 4.74/6.05，整体一致性7.63 vs 5.88/7.48。提示对齐方面，Wan-Dancer在风格捕捉、创意诠释和用户满意度上均优于MusicInfuser。定性比较显示，相比X-Dancer，本方法在面部和手部细节上保持解剖完整性，支持五种舞蹈风格文本控制，且无时间不连续；相比MusicInfuser，本方法可生成分钟级视频且空间分辨率更高。

![图 2：Minute-scale Video Generation. Our framework enables the synthesis of dance videos exceeding one minute in duration across diverse genres. The first row features Chinese Classical dance with fluid movements, the second showcases the energetic rhythms of Latin dance, and the third reflects the unique elements of K-Pop dance.](/images/papers/2607.09581/figure_002_figure_long_video.png)

*图 2 · 原图说明：Minute-scale Video Generation. Our framework enables the synthesis of dance videos exceeding one minute in duration across diverse genres. The first row features Chinese Classical dance with fluid movements, the second showcases the energetic rhythms of Latin dance, and the third reflects the unique elements of K-Pop dance.*

**图示解释：** 在舞蹈质量指标上，Wan-Dancer平均得分8.46，显著优于MusicInfuser（6.23）和X-Dancer（6.06）。

![图 3：Comparison with X-Dancer . Our approach yields markedly sharper reconstructions of complex anatomical regions, particularly hands and facial features, which often suffer from blurring or distortion in X-Dancer.](/images/papers/2607.09581/figure_004_figure_compare_xdancer.png)

*图 3 · 原图说明：Comparison with X-Dancer . Our approach yields markedly sharper reconstructions of complex anatomical regions, particularly hands and facial features, which often suffer from blurring or distortion in X-Dancer.*

**图示解释：** 在舞蹈质量指标上，Wan-Dancer平均得分8.46，显著优于MusicInfuser（6.23）和X-Dancer（6.06）。

### 消融实验

主要对比方法为X-Dancer和MusicInfuser。消融实验设置包括：长程时间连贯性机制（全局到局部vs朴素片段拼接）、光流损失权重（有/无）、动态帧率注入（15fps/7.5fps/3fps）、运动速度分层（慢/中/高）。

## 总结

论文提出Wan-Dancer，一个分层全局到局部的音乐到舞蹈视频生成框架，旨在突破现有扩散模型20秒的时长限制。

## References

- Wan-Dancer: A Hierarchical Framework for Minute-scale Coherent Music-to-Dance Generation：[arXiv 2607.09581](https://arxiv.org/abs/2607.09581)

- [PDF源文件](/papers/2607.09581.pdf)
