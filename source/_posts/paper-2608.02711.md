---
title: "Hunyuan3D-Buffalo 1.0"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.02711
arxiv_id: "2608.02711"
---

## 一、简介

Recent advances in image generation have demonstrated the potential of unified multimodal models that integrate understanding, generation, and editing. However, unified 3D modeling remains constrained by scarce multi modal data, particularly the lack of large-scale and geometrically consistent editing data. To address this limitation, we propose Hunyuan3D-Buffalo 1.0, a unified framework supporting 3D understanding, text-to-3D generation, instruction-guided 3D editing, and text-grounded part generation within a single architecture. To enable scalable training, we construct an 87M-scale 3D multimodal corpus, comprising 25M understanding samples, 50M text-to-3D pairs, and 12M editing pairs generated using Nano3D-v2. Architecturally, the framework combines Hunyuan3D-VLM for semantic, structural, and spatial understanding with Hunyuan3D DiT for highfidelity 3D synthesis. The VLM provides multimodal semantic conditions for generation, while editing and part generation additionally condition the diffusion process on the source object representation to preserve its overall structure and unedited regions. Extensive experiments show that Hunyuan3D-Buffalo 1.0 achieves state-of-the-art or leading performance on text-to-3D generation and 3D editing benchmarks, while exhibiting strong understanding and part-generation capabilities. Our analysis further shows that both generation and understanding improve editing, demonstrating the effectiveness of unified 3D multimodal training.

87M Training Samples

![](images/250d0ce0c379d9a3f72ea465cbd65a7d088ec670f2790272413c683a45dd5893.jpg)

Hunyuan3D-Buffalo 1.0

![](images/ebfa3e187012d83daa23a8cff47ce856de7e7050075219e996abce08a88e08ed.jpg)

![](images/f624f59b62c4a636b053cfb4e9dc98c73e345ccc13f751475a3ba2d4369a3fac.jpg)  
Fig. 1: Hunyuan3D-Buffalo 1.0 is a unified 3D multimodal framework that combines autoregressive modeling with diffusion-based generation, enabling 3D understanding, text-to-3D generation, 3D editing, and text-grounded part generation within a single architecture.

## 二、论文方法

论文采用统一多模态架构，将Hunyuan3D-VLM（基于预训练LLM的仅解码器Transformer）与3D-DiT（从Hunyuan3D-2.1初始化）通过轻量级MLP连接器连接。VLM编码结构（XYZ坐标和法线）和外观（RGB）线索，经VecSet编码器和Q-Former压缩为512个token，并扩展133个特殊token支持3D定位。3D-DiT以VLM隐藏状态为条件，编辑和部件生成时额外以源物体表示为条件，通过自注意力层拼接源3D表示与噪声隐变量。训练数据通过自动化流水线构建，包括分层提示分类、组合提示合成、图像到3D资产生成、多层级描述和几何质量评分。

## 三、论文里的图与解释

### 图 1

![Fig. 1: Hunyuan3D-Buffalo 1.0 is a unified 3D multimodal framework that combines autoregressive modeling with diffusion-based generation, enabling 3D understanding, text-to-3D generation, 3D editing, and text-grounded part generation within a single architecture.](/images/papers/2608.02711/f624f59b62c4a636b053cfb4e9dc98c73e345ccc13f751475a3ba2d4369a3fac.jpg)

**原图说明：** Fig. 1: Hunyuan3D-Buffalo 1.0 is a unified 3D multimodal framework that combines autoregressive modeling with diffusion-based generation, enabling 3D understanding, text-to-3D generation, 3D editing, and text-grounded part generation within a single architecture.

**图示解释：** 该图对应论文中的“Fig. 1: Hunyuan3D-Buffalo 1.0 is a unified 3D multimodal framework that combines autoregressive modeling with diffusion-based generation, enabling 3D understanding, text-to-3D generation, 3D editing, and text-grounded part generation within a single architecture.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Fig. 3: Pipeline of constructing 3D editing training corpus (Nano3D-v2).](/images/papers/2608.02711/585543982771788dec982dde72206a3bc3dfdf161c081b4ba997e138b7eb506d.jpg)

**原图说明：** Fig. 3: Pipeline of constructing 3D editing training corpus (Nano3D-v2).

**图示解释：** 该图对应论文中的“Fig. 3: Pipeline of constructing 3D editing training corpus (Nano3D-v2).”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Fig. 4: Examples of editing pairs in the training corpus created by Nano3D-v2.](/images/papers/2608.02711/489fe3f3141f5238554728016b7c2f21d8298c046085aa3792c0a3b1613dab8a.jpg)

**原图说明：** Fig. 4: Examples of editing pairs in the training corpus created by Nano3D-v2.

**图示解释：** 该图对应论文中的“Fig. 4: Examples of editing pairs in the training corpus created by Nano3D-v2.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 4

![Fig. 5: Examples of multi-round editing by Nano3D-v2.](/images/papers/2608.02711/89927cb11d5efb298e6cebbf22841d3c780183c4c91744ccff325bd72a8aff06.jpg)

**原图说明：** Fig. 5: Examples of multi-round editing by Nano3D-v2.

**图示解释：** 该图对应论文中的“Fig. 5: Examples of multi-round editing by Nano3D-v2.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 5

![Fig. 11: Qualitative part generation results.](/images/papers/2608.02711/d73ee56a0906b6d131c106b997fc93adfcd67eff4c01f8352a2b41fc5c21577b.jpg)

**原图说明：** Fig. 11: Qualitative part generation results.

**图示解释：** 该图对应论文中的“Fig. 11: Qualitative part generation results.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 6

![Fig. 12: Qualitative shape editing results.](/images/papers/2608.02711/22f283436e2a5e2abd0672976ded8f6650ae6632bb97615b723602b5f87b64f2.jpg)

**原图说明：** Fig. 12: Qualitative shape editing results.

**图示解释：** 该图对应论文中的“Fig. 12: Qualitative shape editing results.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 构建了8700万规模的大规模3D多模态训练语料库，覆盖2500万理解样本、5000万文本-3D对和1200万编辑对，有效缓解了3D多模态数据稀缺问题。
2. 提出Nano3D-v2智能体式3D编辑数据构建算法，通过锚点视图选择、学习式3D编辑区域定位、体素级编辑、精细几何纹理优化和VLM标注过滤，可规模化生成高质量、几何一致的编辑对。
3. 提出Hunyuan3D-VLM，一种具备细粒度语义、结构和空间理解能力的3D视觉语言模型，支持物体级描述、部件级问答、3D定位、编辑指令合成和编辑结果推理。
4. 开发了Hunyuan3D-Buffalo 1.0统一框架，将自回归建模与扩散生成相结合，通过MLP连接器将VLM隐藏状态注入3D-DiT条件空间，实现理解、生成、编辑和部件生成在单一架构内的统一。
5. 首次揭示并验证了3D多模态任务间的两个协同效应：更强的文本到3D生成能力可提升3D编辑质量，更强的3D理解能力可提升3D编辑的定位和指令遵循能力。

## 五、实验数据集选择

- 3D理解数据集（基于Part-X-MLLM和ShapeLLM-Omni构建，约2500万样本）
- 文本到3D生成数据集（约5000万文本-资产对）
- 3D编辑数据集（约1200万编辑对，含人类编辑约700万、物体编辑约300万、部件生成约200万）
- 文本引导部件生成数据集

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

Add a cannon mounted on the front deck

![](images/22f283436e2a5e2abd0672976ded8f6650ae6632bb97615b723602b5f87b64f2.jpg)  
Fig. 12: Qualitative shape editing results.

## 八、总结

In this work, we present a unified multimodal 3D model that jointly addresses 3D understanding, 3D generation, and 3D editing within a single framework. Our model achieves state-of-the-art performance across all three tasks, and notably surpasses prior methods by a significant margin on both 3D generation and 3D editing. We believe that unified 3D models represent a promising future direction, with the potential to address multiple 3D tasks within a single framework. However, several key challenges remain to be solved before this vision can be fully realized.

1. Single-stage high-quality geometry representation. The representation for 3D generation has not yet converged. To achieve high-quality geometry generation, current approaches often resort to multi-stage DiT pipelines—for example, TREL-LIS [92] employs a multi-stage architecture. This multi-stage design poses significant challenges for unified models: if we wish to perform editing, we must also carry out multi-stage editing to obtain high-quality results, which is inherently difficult to scale up. Whether the 3D domain can achieve single-stage high-quality geometry generation—analogous to what has been accomplished in the image domain—remains an open and fundamental question.

2. Text-to-3D & 3D editing dataset captioning quality. For text-to-3D generation, we currently rely on multimodal large language models such as Gemini for 3D asset captioning. However, these models still produce considerable ambiguity in their descriptions, leading to noisy training pairs in the text-to-3D dataset. We believe this issue will be progressively alleviated as multimodal large language models continue to advance.

3. End-to-end texture editing. Our current model primarily focuses on geometry editing. Texture editing remains largely unexplored due to the lack of suitable training data. This also raises a broader question: whether geometry and texture representa tions can be jointly modeled, and whether a unified single-stage representation for both high-quality geometry and texture can be achieved.

4. Robust editing data construction pipeline. Our current editing data construction pipeline, based on Nano3D-v2, maintains consistency by replacing tokens outside a box mask in the editing region. While this effectively preserves consistency in the unmasked exterior, the interior of the mask often contains non-edited regions whose consistency is difficult to guarantee. Such inconsistencies propagate into the end-to-end model during training, degrading editing quality. Developing a more robust and precise editing data construction pipeline remains an important open problem.

5. New architecture exploration. Our current framework adopts a cascaded AR + DiT architecture. In the image and video generation domains, Transfusion-style architectures have demonstrated remarkable effectiveness by deeply fusing information across multiple modalities. Exploring such architectures for 3D generation is a natural and promising next step.

6. Data scaling. We observe that both the quantity and quality of 3D data have not yet reached an ideal scale. Continuing to scale up the data—in both volume and quality—remains a critical direction for further improvement.

Acknowledgement We thank the authors of Omni123 for providing the results. We thank Zehuan Huang for his contribution during his internship in Hunyuan. We thank Yifei Feng and Xin Yang for sharing the texture generation codebase.

## References

[1] S. Bai, K. Chen, X. Liu, J. Wang, W. Ge, S. Song, K. Dang, P. Wang, S. Wang, J. Tang, et al. Qwen2. 5-vl technical report. arXiv preprint arXiv:2502.13923, 2025.

[2] R. Bar-On, D. Cohen-Bar, and D. Cohen-Or. Editp23: 3d editing via propagation of image prompts to multi-view, 2025. URL https://arxiv.org/abs/2506.20652.

[3] A. Barda, M. Gadelha, V. G. Kim, N. Aigerman, A. H. Bermano, and T. Groueix. Instant3dit: Multiview inpainting for fast editing of 3d objects, 2024. URL https: //arxiv.org/abs/2412.00518.

[4] K. Bhat, N. Khanna, K. Channa, T. Zhou, Y. Zhu, X. Sun, C. Shang, A. Sudarshan, M. Chu, D. Li, et al. Cube: A roblox view of 3d intelligence. arXiv preprint arXiv:2503.15475, 2025.

[5] W. Cai, S. Fang, W. Ye, X. Dong, Y. Yang, X. Zhang, W. Cheng, Y. Cao, G. Yu, and T. Chen. Native 3d editing with full attention. arXiv preprint arXiv:2511.17501, 2025.

[6] C. Cao, C. Yu, F. Wang, X. Xue, and Y. Fu. Mvinpainter: Learning multi-view consistent inpainting to bridge 2d and 3d editing, 2024. URL https://arxiv.org/abs/2408. 08000.

[7] S. Cao, H. Chen, P. Chen, Y. Cheng, Y. Cui, X. Deng, Y. Dong, K. Gong, T. Gu, X. Gu, et al. Hunyuanimage 3.0 technical report. arXiv preprint arXiv:2509.23951, 2025.

[8] H. Chen, R. Shi, Y. Liu, B. Shen, J. Gu, G. Wetzstein, H. Su, and L. Guibas. Generic 3d diffusion adapter using controlled multi-view editing, 2024. URL https://arxiv. org/abs/2403.12032.

[9] J. Chen, Z. Xu, X. Pan, Y. Hu, C. Qin, T. Goldstein, L. Huang, T. Zhou, S. Xie, S. Savarese, et al. Blip3-o: A family of fully open unified multimodal models-architecture, training and dataset. arXiv preprint arXiv:2505.09568, 2025.

[10] J. Chen, L. Xue, Z. Xu, X. Pan, S. Yang, C. Qin, A. Yan, H. Zhou, Z. Chen, L. Huang, et al. Blip3o-next: Next frontier of native image generation. arXiv preprint arXiv:2510.15857, 2025.

[11] L. Chen, P. Wang, G. Zhang, Z. Ma, and L. Zhang. Omni-3dedit: Generalized versatile 3d editing in one-pass. In Proceedings ofthe IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 12640–12650, 2026.

[12] M. Chen, J. Xie, I. Laina, and A. Vedaldi. Shap-editor: Instruction-guided latent 3d editing in seconds, 2023. URL https://arxiv.org/abs/2312.09246.

[13] R. Chen, Y. Chen, N. Jiao, and K. Jia. Fantasia3d: Disentangling geometry and appearance for high-quality text-to-3d content creation. In Proceedings ofthe IEEE/CVF International Conference on Computer Vision, pages 22246–22256, 2023.

[14] X. Chen, Z. Wu, X. Liu, Z. Pan, W. Liu, Z. Xie, X. Yu, and C. Ruan. Janus-pro: Unified multimodal understanding and generation with data and model scaling. arXiv preprint arXiv:2501.17811, 2025.

[15] Y. Chen, T. He, D. Huang, W. Ye, S. Chen, J. Tang, X. Chen, Z. Cai, L. Yang, G. Yu, et al. Meshanything: Artist-created mesh generation with autoregressive transformers. arXiv preprint arXiv:2406.10163, 2024.

[16] Y. Chen, Z. Li, Y. Wang, H. Zhang, Q. Li, C. Zhang, and G. Lin. Ultra3d: Efficient and high-fidelity 3d generation with part attention. arXiv preprint arXiv:2507.17745, 2025.

[17] Y. Chen, Y. Wang, Y. Luo, Z. Wang, Z. Chen, J. Zhu, C. Zhang, and G. Lin. Meshanything v2: Artist-created mesh generation with adjacent mesh tokenization. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 13922– 13931, 2025.

[18] Y. Chi, X. Li, Z. Huang, and J. M. Rehg. Vinedresser3d: Towards agentic text-guided 3d editing. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 12673–12683, 2026.

[19] Y. Cui, H. Chen, H. Deng, X. Huang, X. Li, J. Liu, Y. Liu, Z. Luo, J. Wang, W. Wang, Y. Wang, C. Wang, F. Zhang, Y. Zhao, T. Pan, X. Li, Z. Hao, W. Ma, Z. Chen, Y. Ao, T. Huang, Z. Wang, and X. Wang. Emu3.5: Native multimodal models are world learners, 2025. URL https://arxiv.org/abs/2510.26583.

[20] C. Deng, D. Zhu, K. Li, C. Gou, F. Li, Z. Wang, S. Zhong, W. Yu, X. Nie, Z. Song, G. Shi, and H. Fan. Emerging properties in unified multimodal pretra

### 在线资源

- [论文：arXiv 2608.02711](https://arxiv.org/abs/2608.02711)
- [代码：GitHub](https://github.com/Tencent-Hunyuan/Hunyuan3D-Buffalo1.0)
- [PDF源文件](/papers/2608.02711.pdf)
