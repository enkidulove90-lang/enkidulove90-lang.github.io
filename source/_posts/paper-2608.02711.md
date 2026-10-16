---
title: "混元3D-Buffalo 1.0：统一多模态3D生成、理解与编辑框架"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.02711
arxiv_id: "2608.02711"
description: "该论文提出了Hunyuan3D-Buffalo 1.0，一个统一的多模态3D框架，在单一架构内支持3D理解、文本到3D生成、指令引导的3D编辑以及文本引导的部件生成。"
---

> 论文：[arXiv 2608.02711](https://arxiv.org/abs/2608.02711) · 代码：[GitHub](https://github.com/Tencent-Hunyuan/Hunyuan3D-Buffalo1.0) · PDF：[本地阅读](/papers/2608.02711.pdf)

该论文提出了Hunyuan3D-Buffalo 1.0，一个统一的多模态3D框架，在单一架构内支持3D理解、文本到3D生成、指令引导的3D编辑以及文本引导的部件生成。为解决3D多模态数据稀缺问题，作者构建了包含8700万样本的大规模3D多模态语料库，其中包含2500万理解样本、5000万文本-3D对和1200万编辑对。编辑数据通过提出的Nano3D-v2智能体式数据构建算法生成，该算法结合锚点视图选择、学习式3D编辑区域定位、体素级编辑和精细几何纹理优化。架构上，框架结合了Hunyuan3D-VLM（用于语义、结构和空间理解）与Hunyuan3D DiT（用于高保真3D合成），通过轻量级MLP连接器对齐VLM隐藏状态与DiT条件空间。实验表明，该模型在文本到3D生成和3D编辑基准上达到最先进或领先性能，并揭示了生成提升编辑、理解提升编辑的跨任务协同效应。

## 研究问题

该论文提出了Hunyuan3D-Buffalo 1.0，一个统一的多模态3D框架，在单一架构内支持3D理解、文本到3D生成、指令引导的3D编辑以及文本引导的部件生成。为解决3D多模态数据稀缺问题，作者构建了包含8700万样本的大规模3D多模态语料库，其中包含2500万理解样本、5000万文本-3D对和1200万编辑对。编辑数据通过提出的Nano3D-v2智能体式数据构建算法生成，该算法结合锚点视图选择、学习式3D编辑区域定位、体素级编辑和精细几何纹理优化。架构上，框架结合了Hunyuan3D-VLM（用于语义、结构和空间理解）与Hunyuan3D DiT（用于高保真3D合成），通过轻量级MLP连接器对齐VLM隐藏状态与DiT条件空间。实验表明，该模型在文本到3D生成和3D编辑基准上达到最先进或领先性能，并揭示了生成提升编辑、理解提升编辑的跨任务协同效应。

## 方法：核心思路与整体框架

论文采用统一多模态架构，将Hunyuan3D-VLM（基于预训练LLM的仅解码器Transformer）与3D-DiT（从Hunyuan3D-2.1初始化）通过轻量级MLP连接器连接。VLM编码结构（XYZ坐标和法线）和外观（RGB）线索，经VecSet编码器和Q-Former压缩为512个token，并扩展133个特殊token支持3D定位。3D-DiT以VLM隐藏状态为条件，编辑和部件生成时额外以源物体表示为条件，通过自注意力层拼接源3D表示与噪声隐变量。训练数据通过自动化流水线构建，包括分层提示分类、组合提示合成、图像到3D资产生成、多层级描述和几何质量评分。

![图 1：Fig. 1: Hunyuan3D-Buffalo 1.0 is a unified 3D multimodal framework that combines autoregressive modeling with diffusion-based generation, enabling 3D understanding, text-to-3D generation, 3D editing, and text-grounded part generation within a single architecture.](/images/papers/2608.02711/f624f59b62c4a636b053cfb4e9dc98c73e345ccc13f751475a3ba2d4369a3fac.jpg)

*图 1 · 原图说明：Fig. 1: Hunyuan3D-Buffalo 1.0 is a unified 3D multimodal framework that combines autoregressive modeling with diffusion-based generation, enabling 3D understanding, text-to-3D generation, 3D editing, and text-grounded part generation within a single architecture.*

**图示解释：** 论文采用统一多模态架构，将Hunyuan3D-VLM（基于预训练LLM的仅解码器Transformer）与3D-DiT（从Hunyuan3D-2.1初始化）通过轻量级MLP连接器连接。

![图 2：Fig. 3: Pipeline of constructing 3D editing training corpus (Nano3D-v2).](/images/papers/2608.02711/585543982771788dec982dde72206a3bc3dfdf161c081b4ba997e138b7eb506d.jpg)

*图 2 · 原图说明：Fig. 3: Pipeline of constructing 3D editing training corpus (Nano3D-v2).*

**图示解释：** 论文采用统一多模态架构，将Hunyuan3D-VLM（基于预训练LLM的仅解码器Transformer）与3D-DiT（从Hunyuan3D-2.1初始化）通过轻量级MLP连接器连接。

![图 3：Fig. 4: Examples of editing pairs in the training corpus created by Nano3D-v2.](/images/papers/2608.02711/489fe3f3141f5238554728016b7c2f21d8298c046085aa3792c0a3b1613dab8a.jpg)

*图 3 · 原图说明：Fig. 4: Examples of editing pairs in the training corpus created by Nano3D-v2.*

**图示解释：** 论文采用统一多模态架构，将Hunyuan3D-VLM（基于预训练LLM的仅解码器Transformer）与3D-DiT（从Hunyuan3D-2.1初始化）通过轻量级MLP连接器连接。

![图 4：Fig. 5: Examples of multi-round editing by Nano3D-v2.](/images/papers/2608.02711/89927cb11d5efb298e6cebbf22841d3c780183c4c91744ccff325bd72a8aff06.jpg)

*图 4 · 原图说明：Fig. 5: Examples of multi-round editing by Nano3D-v2.*

**图示解释：** 论文采用统一多模态架构，将Hunyuan3D-VLM（基于预训练LLM的仅解码器Transformer）与3D-DiT（从Hunyuan3D-2.1初始化）通过轻量级MLP连接器连接。

## 创新点

1. 构建了8700万规模的大规模3D多模态训练语料库，覆盖2500万理解样本、5000万文本-3D对和1200万编辑对，有效缓解了3D多模态数据稀缺问题。
2. 提出Nano3D-v2智能体式3D编辑数据构建算法，通过锚点视图选择、学习式3D编辑区域定位、体素级编辑、精细几何纹理优化和VLM标注过滤，可规模化生成高质量、几何一致的编辑对。
3. 提出Hunyuan3D-VLM，一种具备细粒度语义、结构和空间理解能力的3D视觉语言模型，支持物体级描述、部件级问答、3D定位、编辑指令合成和编辑结果推理。
4. 开发了Hunyuan3D-Buffalo 1.0统一框架，将自回归建模与扩散生成相结合，通过MLP连接器将VLM隐藏状态注入3D-DiT条件空间，实现理解、生成、编辑和部件生成在单一架构内的统一。
5. 首次揭示并验证了3D多模态任务间的两个协同效应：更强的文本到3D生成能力可提升3D编辑质量，更强的3D理解能力可提升3D编辑的定位和指令遵循能力。

## 实验：数据、基线与结果

### 数据集与设置

实验涵盖四个任务：3D理解（描述、问答、定位）、文本到3D生成、指令引导3D编辑和文本引导部件生成。训练语料库总计约8700万样本，其中理解数据约2500万（含纯文本约700万、图文约300万、3D点云-文本约1500万），文本到3D约5000万对，编辑约1200万对。文本到3D数据通过五阶段自动化流水线构建，编辑数据通过Nano3D-v2五阶段流水线构建。具体训练/验证/测试划分比例原文未披露。

### Benchmark 与结果

Hunyuan3D-Buffalo 1.0在文本到3D生成和3D编辑基准上达到最先进或领先性能，在3D生成和3D编辑任务上显著超越先前方法。模型同时展现出强大的3D理解和部件生成能力。实验揭示了两个明确的跨任务协同效应：更强的文本到3D生成能力提升3D编辑质量，因为更好的生成先验产生更完整自然的编辑几何；更强的3D理解能力提升3D编辑，因为细粒度语义和空间推理帮助模型定位编辑区域、解释指令并保留未编辑区域。具体性能提升百分比或数值原文未完整披露。

![图 5：Fig. 11: Qualitative part generation results.](/images/papers/2608.02711/d73ee56a0906b6d131c106b997fc93adfcd67eff4c01f8352a2b41fc5c21577b.jpg)

*图 5 · 原图说明：Fig. 11: Qualitative part generation results.*

**图示解释：** Hunyuan3D-Buffalo 1.0在文本到3D生成和3D编辑基准上达到最先进或领先性能，在3D生成和3D编辑任务上显著超越先前方法。

![图 6：Fig. 12: Qualitative shape editing results.](/images/papers/2608.02711/22f283436e2a5e2abd0672976ded8f6650ae6632bb97615b723602b5f87b64f2.jpg)

*图 6 · 原图说明：Fig. 12: Qualitative shape editing results.*

**图示解释：** Hunyuan3D-Buffalo 1.0在文本到3D生成和3D编辑基准上达到最先进或领先性能，在3D生成和3D编辑任务上显著超越先前方法。

### 消融实验

文本到3D生成和3D编辑基准上对比了现有方法，包括TRELLIS、Nano3D、VoxHammer、ShapeLLM-Omni等。3D理解任务对比了Part-X-MLLM和ShapeLLM-Omni。消融实验验证了生成提升编辑和理解提升编辑的协同效应。具体完整基线列表原文未完整披露。

## 总结

该论文提出了Hunyuan3D-Buffalo 1.0，一个统一的多模态3D框架，在单一架构内支持3D理解、文本到3D生成、指令引导的3D编辑以及文本引导的部件生成。

## References

- Hunyuan3D-Buffalo 1.0：[arXiv 2608.02711](https://arxiv.org/abs/2608.02711)

- [代码：GitHub](https://github.com/Tencent-Hunyuan/Hunyuan3D-Buffalo1.0)
- [PDF源文件](/papers/2608.02711.pdf)
