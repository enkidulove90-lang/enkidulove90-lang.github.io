---
title: "Wan-Dancer: A Hierarchical Framework for Minute-scale Coherent Music-to-Dance Generation"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.09581
arxiv_id: "2607.09581"
---

## 一、简介

论文提出Wan-Dancer，一个分层全局到局部的音乐到舞蹈视频生成框架，旨在突破现有扩散模型20秒的时长限制。该方法将生成过程解耦为全局关键帧规划和局部时间细化两个阶段，利用完整音乐上下文保证长程连贯性。核心创新包括：通过时间映射RoPE嵌入实现动态帧率适配以精确对齐任意时长音乐；引入光流损失增强运动连续性；采用运动速度控制在高动态场景下保持细节。实验表明，该框架可生成超过一分钟的720p/30fps稳定视频，在五种舞蹈风格上均达到最优性能。

## 二、论文方法

Mingyang Huang, Peng Zhang, Li Hu, Guangyuan Wang, Ruoshi Zhang, Yi Lu, Gang Cheng, Bang Zhang

Tongyi Lab, Alibaba Group {hongcan.hmy, futian.zp, hooks.hl, yixuan.wgy, ruoshi.zrs, ly449033, chenggang.cg, zhangbang.zb}@alibaba-inc.com

Project | GitHub | MS Space | MS Model | HF | Paper

Abstract. Generating long-duration, high-definition, and rhythmically synchronized dance videos directly from music remains a significant challenge, primarily due to the temporal constraints of current difusion models, which typically fail beyond 20 seconds. Existing approaches, whether they rely on intermediate 3D skeletons or on end-to-end video synthesis, sufer from temporal drift, identity inconsistency, and repetitive motion patterns when extended to longer horizons. To address these limitations, we propose a novel hierarchical framework for minute-scale coherent music-to-dance generation. Our method decouples the process into global keyframe planning and local temporal refinement, leveraging full-track musical context to ensure long-range coherence. Key innovations include dynamic frame rate adaptation via time-mapped RoPE embeddings for precise alignment, an optical-flow-based loss function to enhance motion continuity, and motion-speed control to preserve high-fidelity details during rapid movements. Extensive experiments demonstrate that our framework surpasses the conventional duration barrier, generating stable, 720p/30fps videos exceeding one minute with superior temporal stability. Furthermore, the model exhibits robust versatility across five distinct dance genres, conditioned on both audio and textual prompts, establishing a new state-of-the-art in coherent, long-form dance video synthesis.

Keywords: Video Generation · Music-to-Dance · Global-to-Local · Minutescale

## 三、论文里的图与解释

### 图 1

![Inference Pipeline. Initially, the global stage synthesizes a sparse keyframe global video that captures the overall motion structure and rhythmic alignment. Subsequently, this global output serves as a structural guidance condition for the local stage, which interpolates and refines the sequence to generate the final high-frame-rate, dense video with enhanced temporal coherence and visual detail.](/images/papers/2607.09581/figure_001_pipeline_infer.png)

**原图说明：** Inference Pipeline. Initially, the global stage synthesizes a sparse keyframe global video that captures the overall motion structure and rhythmic alignment. Subsequently, this global output serves as a structural guidance condition for the local stage, which interpolates and refines the sequence to generate the final high-frame-rate, dense video with enhanced temporal coherence and visual detail.

**图示解释：** 该图对应论文中的“Inference Pipeline. Initially, the global stage synthesizes a sparse keyframe global video that captures the overall motion structure and rhythmic alignment. Subsequently, this global output serves as a structural guidance condition for the local stage, which interpolates and refines the sequence to generate the final high-frame-rate, dense video with enhanced temporal coherence and visual detail.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Minute-scale Video Generation. Our framework enables the synthesis of dance videos exceeding one minute in duration across diverse genres. The first row features Chinese Classical dance with fluid movements, the second showcases the energetic rhythms of Latin dance, and the third reflects the unique elements of K-Pop dance.](/images/papers/2607.09581/figure_002_figure_long_video.png)

**原图说明：** Minute-scale Video Generation. Our framework enables the synthesis of dance videos exceeding one minute in duration across diverse genres. The first row features Chinese Classical dance with fluid movements, the second showcases the energetic rhythms of Latin dance, and the third reflects the unique elements of K-Pop dance.

**图示解释：** 该图对应论文中的“Minute-scale Video Generation. Our framework enables the synthesis of dance videos exceeding one minute in duration across diverse genres. The first row features Chinese Classical dance with fluid movements, the second showcases the energetic rhythms of Latin dance, and the third reflects the unique elements of K-Pop dance.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Comparison with X-Dancer . Our approach yields markedly sharper reconstructions of complex anatomical regions, particularly hands and facial features, which often suffer from blurring or distortion in X-Dancer.](/images/papers/2607.09581/figure_004_figure_compare_xdancer.png)

**原图说明：** Comparison with X-Dancer . Our approach yields markedly sharper reconstructions of complex anatomical regions, particularly hands and facial features, which often suffer from blurring or distortion in X-Dancer.

**图示解释：** 该图对应论文中的“Comparison with X-Dancer . Our approach yields markedly sharper reconstructions of complex anatomical regions, particularly hands and facial features, which often suffer from blurring or distortion in X-Dancer.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 分层全局到局部生成架构：将音乐到舞蹈生成解耦为全局关键帧规划和局部时间细化两个阶段，利用完整音乐上下文进行长程节奏规划，有效消除时间漂移和重复性伪影。
2. 动态帧率适配机制：将绝对时间标识符集成到旋转位置嵌入（RoPE）中，使模型能够根据音乐总时长动态生成关键帧序列，实现精确的时间对齐，支持从15fps到3fps的灵活采样。
3. 基于光流损失的运动连续性增强：引入SEA-RAFT光流约束作为损失函数权重，显著提升快速运动场景下的空间一致性和边缘保真度，减少运动模糊和结构失真。
4. 基于LoRA的高效编舞定制：采用低秩适配（LoRA）微调策略，仅需16个参考视频即可快速复现特定舞蹈动作，无需大规模重训练或数据集。
5. 运动速度分层训练策略：将训练样本按运动速度分为慢、中、高三档（10%/80%/10%），优先学习自然的中速动态，实现推理时通过文本提示精确控制运动速度。

## 五、实验数据集选择

- 自建专有数据集（约200小时高质量视频，最低720p/30fps，涵盖中国古典舞、K-Pop、拉丁舞、踢踏舞、街舞五种风格）
- 对比基准：X-Dancer、MusicInfuser
- 评估协议参考：MusicInfuser评估协议

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

Minute-scale Music-to-Dance Generation. Our framework leverages a globalto-local architecture to synthesize minute-scale dance videos based on input music. As shown in Fig. 3, it maintains high fidelity and spatial resolution for sequences up to 160 seconds while preserving identity across durations; generated subjects closely match the reference images in fine details like clothing textures.

Additionally, the model adheres precisely to semantic prompts for dance genres. The visual results demonstrate accurate representation of choreographic styles, which highlights the model’s ability to align high-level textual instructions with specific motion patterns.

![](images/4c95e2c389d4a23e9fadcb4fd001af8b8a2338fe341e71abdb43aa38a2da313f.jpg)  
Fig. 3: Minute-scale Video Generation. Our framework enables the synthesis of dance videos exceeding one minute in duration across diverse genres. The first row features Chinese Classical dance with fluid movements, the second showcases the energetic rhythms of Latin dance, and the third reflects the unique elements of K-Pop dance.

By leveraging a hierarchical global-to-local architecture, we achieve highdefinition output while efectively mitigating the error accumulation and temporal drift, and maintaining the dance style.

Customized Dance Generation. Our framework not only synthesizes dance videos based on input music but also generates specific choreographic motions using Low-Rank Adaptation (LoRA) [10]. As shown in Fig. 4, this method aligns generated sequences with human-curated motion templates. For instance, it successfully reproduces the unique kinematic characteristics of the "Spaghetti" dance, demonstrating LoRA’s efectiveness in fine-tuning motion control.

## 八、总结

In conclusion, we have tackled the challenge of generating long-duration, highdefinition, rhythmically synchronized dance videos by overcoming limitations in current difusion models. Our novel hierarchical framework decouples global keyframe planning from local temporal refinement, eliminating issues like temporal drift and identity degradation that impact existing 3D-based and end-toend approaches. Key innovations, such as dynamic frame rate adaptation, an optical flow-based loss function, and precise motion-speed control, ensure longrange coherence and detail preservation during rapid movements. Our experiments demonstrate a breakthrough beyond the 20-second limit, producing stable $7 2 0 \mathrm { p / 3 0 f p s }$ videos exceeding one minute while showcasing versatility across five dance genres conditioned on audio and text. This work sets a new state-of-the-art in coherent, long-form music-to-dance synthesis.

![](images/ae0c8455a6209faa8fa57a80f8fd94beefc83f2babe5728cb8c9c266d449dca9.jpg)  
FPS=3  
(a) Dynamic Frame Rate Adaptation: The rows show generation results at 15, 7.5, and 3 fps. As the frame rate decreases, temporal sampling becomes sparser, leading to greater kinematic disparities between frames.

![](images/7f2fd3bc6a06910c94e0fee4414bb264a361e6e0c02931fc900988e9436d7e1f.jpg)  
(b) The rows illustrate generation results at slow, medium, and high motion speeds. The slow setting misaligns with the musical tempo, while the high-speed setting creates visual artifacts due to complexity. The medium speed strikes an optimal balance.  
Fig. 7: Comparisons for dynamic frame rate adaptation and motion speed.

Limitations and Future Work: Three key areas need further exploration:

– Identity Consistency: We plan to integrate face-embedding constraints to maintain facial consistency across long sequences.

– Semantic Alignment: Future eforts will employ multimodal semantic encoders to enhance contextual expressiveness in the generated dances.

Multi-Dancer Scenarios: We aim to extend our architecture to model interdancer interactions for synchronized group choreography.

Ethics Statement: Our research focuses on advancing human image animation techniques and disavows malicious uses, like deceptive deepfakes. All synthesized outputs will be clearly labeled as artificially generated.

![](images/02a67e3704cc9e4c11de9224bb431fe0a48729953700de25ebfdb42708cf7bd3.jpg)

![](images/0eb8e31c0a8d790e0028ff29035d0ffe3d2e0b61fd284a0cff92edddad23ae4d.jpg)

![](images/8f1c26143bec091a9a5ad67a93c09c53291dd3d927d404001b6625af0e0a91dd.jpg)  
(a) The same reference image (b) The same music with dif- (c) The same music and refer with diferent music. The top ferent reference images. The top ence image are used, but diferand bottom videos use diferent and bottom videos use diferent ent seeds generate videos in the pieces of music. images. top and bottom rows.

Fig. 8: We assess the generative diversity of our method through controlled experiments by varying the reference image, music input, and random seed..

## References

1. Bai, S., Chen, K., Liu, X., Wang, J., Ge, W., Song, S., Dang, K., Wang, P., Wang, S., Tang, J., Zhong, H., Zhu, Y., Yang, M., Li, Z., Wan, J., Wang, P., Ding, W., Fu, Z., Xu, Y., Ye, J., Zhang, X., Xie, T., Cheng, Z., Zhang, H., Yang, Z., Xu, H., Lin, J.: Qwen2.5-vl technical report (2025), https://arxiv.org/abs/2502.13923

2. Chefer, H., Singer, U., Zohar, A., Kirstain, Y., Polyak, A., Taigman, Y., Wolf, L., Sheynin, S.: Videojam: Joint appearance-motion representations for enhanced motion generation in video models. arXiv preprint arXiv:2502.02492 (2025)

3. Chen, Z., Xu, H., Song, G., Xie, Y., Zhang, C., Chen, X., Wang, C., Chang, D., Luo, L.: X-dancer: Expressive music to human dance video generation. In: Proceedings of the IEEE/CVF International Conference on Computer Vision. pp. 10602–10611 (2025)

4. Chung, H.W., Constant, N., Garcia, X., Roberts, A., Tay, Y., Narang, S., Firat, O.: Unimax: Fairer and more efective language sampling for large-scale multilingual pretraining. arXiv preprint arXiv:2304.09151 (2023)

5. Esser, P., Kulal, S., Blattmann, A., Entezari, R., Müller, J., Saini, H., Levi, Y., Lorenz, D., Sauer, A., Boesel, F., et al.: Scaling rectified flow transformers for high-resolution image synthesis. In: Forty-first international conference on machine learning (2024)

6. Fang, J., Zhao, S.: Usp: A unified sequence parallelism approach for long context generative ai. arXiv preprint arXiv:2405.07719 (2024)

7. Gao, X., Hu, L., Hu, S., Huang, M., Ji, C., Meng, D., Qi, J., Qiao, P., Shen, Z., Song, Y., et al.: Wan-s2v: Audio-driven cinematic video generation. arXiv preprint arXiv:2508.18621 (2025)

8. Heo, B., Park, S., Han, D., Yun, S.: Rotary position embedding for vision transformer. In: European Conference on Computer Vision. pp. 289–305. Springer (2024)

9. Hong, S., Kemelmacher-Shlizerman, I., Curless, B., Seitz, S.M.: Musicinfuser: Making video difusion listen and dance. arXiv preprint arXiv:2503.14505 (2025)

10. Hu, E.J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., Chen, W., et al.: Lora: Low-rank adaptation of large language models. Iclr 1(2), 3 (2022)

11. Huang, Z., Xu, X., Xu, C., Zhang, H., Zheng, C., Qin, J., He, S.: Beat-it: Beatsynchronized multi-condition 3d dance generation. In: European conference on computer vision. pp. 273–290. Springer (2024)

12. Hyung, J., Kim, K., Hong, S., Kim, M.J., Choo, J.: Spatiotemporal skip guidance for enhanced video difusion sampling. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 11006–11015 (2025)

13. Jiang, J., Zeng, W., Zheng, Z., Yang, J., Liang, C., Liao, W., Liang, H., Zhang, Y., Gao, M.: Omnihuman-1.5: Instilling an active mind in avatars via cognitive simulation. arXiv preprint arXiv:2508.19209 (2025)

14. Le, N., Pham, T., Do, T., Tjiputra, E., Tran, Q.D., Nguyen, A.: Music-driven group choreography. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 8673–8682 (2023)

15. Li, R., Zhang, H., Zhang, Y., Zhang, Y., Zhang, Y., Guo, J., Zhang, Y., Li, X., Liu, Y.: Lodge++: High-quality and long dance generation with vivid choreography patterns. arXiv preprint arXiv:2410.20389 (2024)

16. Li, R., Zhang, Y., Zhang, Y., Zhang, H., Guo, J., Zhang, Y., Liu, Y., Li, X.: Lodge: A coarse to fine difusion network for long dance generation guided by the characteristic dance primitives. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 1524–1534 (2024)

17. Li, R., Zhao, J., Zhang, Y., Su, M., Ren, Z., Zhang, H., Tang, Y., Li, X.: Finedance: A fine-grained choreography dataset for 3d full body dance generation. In: Proceedings of the IEEE/CVF International Conference on Computer Vision. pp. 10234– 10243 (2023)

18. Liu, H., Xu, Z., Hong, F.T., Huang, H.P., Zhou, Y., Zhou, Y.: Video motion graphs. In: Proceedings of the IEEE/CVF International Conference on Computer Vision. pp. 13730–13740 (2025)

19. Luo, Z., Ren, M., Hu

### 在线资源

- [论文：arXiv 2607.09581](https://arxiv.org/abs/2607.09581)
- [PDF源文件](/papers/2607.09581.pdf)
