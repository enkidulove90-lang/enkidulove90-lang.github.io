---
title: "CoSA: Accelerating Long-Context Inference via Proxy-Kernel Co-Designed Sparse Attention"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.25291
arxiv_id: "2607.25291"
---

## 一、简介

The quadratic cost of self-attention makes long-context inference prohibitively expensive, and proxy-based block-sparse attention has become a practical remedy. Existing methods typically rely on a proxy to predict a binary sparse mask and a kernel to consume this mask and perform sparse attention computation. Such an approach is efective under moderate budgets. However, as the budget tightens, the estimated proxy inevitably drops some salient blocks, while the kernel can only apply the sparse mask mechanically, leading to an evident drop in model accuracy. We propose CoSA, a two-stage training-free Sparse Attention under proxy-kernel CO-design, which couples a Kernel-Aware Proxy (KAP) with an Ordered-Skipping Kernel (OSK). In the first stage, the KAP selects blocks under a moderate budget and produces an ordered mask that prescribes the order in which KV pages are visited in the kernel inner loop. In the second stage, the OSK applies this mask and skips more blocks under a tightened budget given online-softmax statistics. Across mainstream LLM backbones and long-context benchmarks, CoSA attains higher accuracy at lower budgets. Impressively, CoSA achieves a 4.93× attention speedup and reduces end-to-end Time-to-First-Token by 2.53× under a context length of 128K with negligible performance degradation. Code is available at https://github.com/Tencent/AngelSlim.

## 二、论文方法

CoSA采用两阶段无训练块稀疏注意力框架。第一阶段，KAP通过步长下采样查询和键，经Softmax、MaxPool和MaxNorm计算块重要性分数和HRM标志，通过标志分组排序生成计算顺序掩码，在中等预算下选择块并规定访问顺序。第二阶段，OSK消费该掩码，通过KV页重映射物理跳过未选中页，并利用在线Softmax的精确logits进行内核内跳跃，进一步稀疏化。两阶段通过计算顺序掩码桥接，代理塑造内核执行顺序，内核消费代理掩码驱动稀疏。

## 三、论文里的图与解释

### 图 1

![Figure 4: Overview of CoSA. $\mathbf { M } _ { \mathrm { K A P } } .$ the KAP mask serves as a bridge between the co-designed proxy and kernel. Left: KAP estimates a per-block score together with the HRM flag. They are merged into the computation-order mask ${ \bf M } _ { \mathrm { K A P } }$ , which places HRM blocks first. Right: OSK consumes ${ \bf M } _ { \mathrm { K A P } }$ through KV page remapping, yielding three per-block patterns: ➀ mask-skipped, ➁ in-kernel skipped, and ➂ computed.](/images/papers/2607.25291/4e85b9243983bd21922df3e58da8f8c3082e6e64c009de6b5c222ab4bfdf2188.jpg)

**原图说明：** Figure 4: Overview of CoSA. $\mathbf { M } _ { \mathrm { K A P } } .$ the KAP mask serves as a bridge between the co-designed proxy and kernel. Left: KAP estimates a per-block score together with the HRM flag. They are merged into the computation-order mask ${ \bf M } _ { \mathrm { K A P } }$ , which places HRM blocks first. Right: OSK consumes ${ \bf M } _ { \mathrm { K A P } }$ through KV page remapping, yielding three per-block patterns: ➀ mask-skipped, ➁ in-kernel skipped, and ➂ computed.

**图示解释：** 该图对应论文中的“Figure 4: Overview of CoSA. $\mathbf { M } _ { \mathrm { K A P } } .$ the KAP mask serves as a bridge between the co-designed proxy and kernel. Left: KAP estimates a per-block score together with the HRM flag. They are merged into the computation-order mask ${ \bf M } _ { \mathrm { K A P } }$ , which places HRM blocks first. Right: OSK consumes ${ \bf M } _ { \mathrm { K A P } }$ through KV page remapping, yielding three per-block patterns: ➀ mask-skipped, ➁ in-kernel skipped, and ➂ computed.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Figure C: Full remapping sweeps across Stage-1 budgets and skip scales. Each column fixes ${ { B } _ { \mathrm { S t a g e - 1 } } }$ . The Top row reports PPL and the Bottom row reports the in-kernel skip ratio as $\Delta$ varies. Remapping achieves a higher skip ratio at a fixed $\Delta$ and a lower PPL at a matched skip ratio. Red annotations highlight the matched-ratio PPL gain.](/images/papers/2607.25291/793761a8283ef1a3937fb56e453152e738698fb3d8e4f7e8fb79af4029f6329c.jpg)

**原图说明：** Figure C: Full remapping sweeps across Stage-1 budgets and skip scales. Each column fixes ${ { B } _ { \mathrm { S t a g e - 1 } } }$ . The Top row reports PPL and the Bottom row reports the in-kernel skip ratio as $\Delta$ varies. Remapping achieves a higher skip ratio at a fixed $\Delta$ and a lower PPL at a matched skip ratio. Red annotations highlight the matched-ratio PPL gain.

**图示解释：** 该图对应论文中的“Figure C: Full remapping sweeps across Stage-1 budgets and skip scales. Each column fixes ${ { B } _ { \mathrm { S t a g e - 1 } } }$ . The Top row reports PPL and the Bottom row reports the in-kernel skip ratio as $\Delta$ varies. Remapping achieves a higher skip ratio at a fixed $\Delta$ and a lower PPL at a matched skip ratio. Red annotations highlight the matched-ratio PPL gain.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 提出代理-内核协同设计原则，通过单一计算顺序掩码替代传统二值掩码，使代理不仅决定哪些块被保留，还规定内核中块的访问顺序，实现代理与内核的相互塑造。
2. 设计内核感知代理（KAP），利用顺序不变性输出计算顺序掩码，优先访问包含行最大值的块（HRM块），通过标志分组排序缓解内核内跳跃的保守性问题，在中等预算下实现第一阶段稀疏选择。
3. 设计有序跳跃内核（OSK），支持任意顺序页访问、物理页跳转和基于精确在线Softmax统计的内核内跳跃，实现第二阶段稀疏计算，将稀疏预算进一步压低，同时保持输出正确性。
4. 揭示现有块稀疏注意力的两个关键性质（预算依赖的代理保真度、在线Softmax的顺序不变性）和内核内跳跃的两个局限（密集QK乘法作为代理、跳跃保守性），为协同设计提供理论依据。

## 五、实验数据集选择

- RULER
- LongBench-v2

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

Beyond algorithm-level optimization, a parallel line of works optimizes the attention kernel itself. The FlashAttention series (Dao et al. 2022; Dao 2024; Shah et al. 2024; Zadouri et al. 2026) tile the computation and fuse the online-softmax (OSM) to cut trafic to GPU global memory, delivering large speedups without altering the result. Building on this, Block-Sparse-Attention kernel (Guo et al. 2024) supports streaming and arbitrary block masks for eficient prefilling, and Flash-Infer (Ye et al. 2025) provides a customizable engine with block-sparse and paged KV-cache formats. BLASST (Yuan et al. 2025b) instead exploits the Softmax statistics to skip negligible blocks inside the kernel with near-zero decision overhead on modern GPUs. PagedAttention (Kwon et al. 2023) stores the KV cache in non-contiguous pages to eliminate fragmentation during serving. Eficient as they are, these backends realize block sparsity by merely consuming a binary mask or depending on a conservative online-condition branch, which in turn constrains the algorithm design.

![](images/a4d55bdcda7a632fc0f1d5aa36d3eb79a3fa150c5b9b1bf2b7ad15a5c1e776c1.jpg)  
Figure 2: IoU of proxy masks against the oracle for Qwen3- 8B under a context length of 128K.

## 八、总结

We presented CoSA, a two-stage training-free block-sparse attention for eficient long-context inference built on proxykernel co-design. Instead of treating the importance proxy and the sparse kernel as isolated designs, CoSA bridges them through a single computation-order mask. CoSA features $\mathrm { K A P }$ and OSK. The KAP selects blocks under a moderate budget and further prescribes the order in which they are visited. The OSK consumes this order through lightweight page remapping and skips additional blocks in-kernel from exact online-softmax statistics. The joint design lowers the budget while still retaining the truly salient blocks that an isolated proxy tends to discard. Across mainstream backbones and long-context benchmarks, CoSA attains higher accuracy at lower budgets than existing sparse methods. For example, it reduces TTFT by 2.53× at 128K context with negligible accuracy loss. As future work, we will extend CoSA beyond prefilling to decoding, which requires dedicated proxy and kernel designs due to its distinct query shapes and computational patterns.

## References

Dao, T. 2024. FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning. In International Conference on Learning Representations (ICLR).

Dao, T.; Fu, D. Y.; Ermon, S.; Rudra, A.; and Ré, C. 2022. FlashAttention: Fast and Memory-Eficient Exact Attention with IO-Awareness. In Advances in Neural Information Processing Systems (NeurIPS).

Du, M.; Xu, B.; Zhu, C.; Wang, S.; Wang, P.; Wang, X.; and Mao, Z. 2026. A-RAG: Scaling Agentic Retrieval-Augmented Generation via Hierarchical Retrieval Interfaces. arXiv preprint arXiv:2602.03442.

Fan, Q.; Huang, H.; Wu, Z.; Wang, J.; Wang, B.; and He, R. 2026. Flashprefill: Instantaneous pattern discovery and thresholding for ultra-fast long-context prefilling. arXiv preprint arXiv:2603.06199.

Gao, Y.; Wei, J.; Zhang, Q.; Cheng, Y.; Chen, S.; Tang, Z.; Jiang, Z.; Song, Y.; Zhang, H.; Zhao, L.; et al. 2026. HySparse: A Hybrid Sparse Attention Architecture with Oracle Token Selection and KV Cache Sharing. arXiv preprint arXiv:2602.03560.

Gao, Y.; Zeng, Z.; Du, D.; Cao, S.; Zhou, P.; Qi, J.; Lai, J.; So, H. K.-H.; Cao, T.; Yang, F.; et al. 2024. Seerattention: Learning intrinsic sparse attention in your llms. arXiv preprint arXiv:2410.13276.

Grattafiori, A.; Dubey, A.; Jauhri, A.; Pandey, A.; Kadian, A.; Al-Dahle, A.; Letman, A.; Mathur, A.; Schelten, A.; Vaughan, A.; et al. 2024. The llama 3 herd of models. arXiv preprint arXiv:2407.21783.

Guo, J.; Tang, H.; Yang, S.; Zhang, Z.; Liu, Z.; and Han, S. 2024. Block Sparse Attention. https://github.com/mit-hanlab/Block-Sparse-Attention.

Hsieh, C.-P.; Sun, S.; Kriman, S.; Acharya, S.; Rekesh, D.; Jia, F.; Zhang, Y.; and Ginsburg, B. 2024. RULER: What’s the Real Context Size of Your Long-Context Language Models? arXiv preprint arXiv:2404.06654.

Jiang, H.; Li, Y.; Zhang, C.; Wu, Q.; Luo, X.; Ahn, S.; Han, Z.; Abdi, A. H.; Li, D.; Lin, C.-Y.; et al. 2024. Minference 1.0: Accelerating pre-filling for long-context llms via dynamic sparse attention. Advances in Neural Information Processing Systems, 37: 52481–52515.

Kwon, W.; Li, Z.; Zhuang, S.; Sheng, Y.; Zheng, L.; Yu, C. H.; Gonzalez, J.; Zhang, H.; and Stoica, I. 2023. Eficient memory management for large language model serving with pagedattention. In Proceedings of the 29th symposium on operating systems principles, 611–626.

Lai, X.; Lu, J.; Luo, Y.; Ma, Y.; and Zhou, X. 2025. Flexprefill: A context-aware sparse attention mechanism for eficient long-sequence inference. arXiv preprint arXiv:2502.20766.

Liu, A.; Yang, R.; Jiang, H.; Lin, B.; Sun, M.; Li, Y.; Zhang, C.; and Xie, T. 2026a. VecAttention: Vector-wise Sparse Attention for Accelerating Long Context Inference. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 41299–41310.

Liu, H.; Zaharia, M.; and Abbeel, P. 2023. Ring Attention with Blockwise Transformers for Near-Infinite Context. CoRR abs/2310.01889 (2023).

Liu, S.; Cao, Z.; and He, Y. 2025. A Unified Sparse Attention via Multi-Granularity Compression. arXiv preprint arXiv:2512.14082.

Liu, S.; Wang, G.; Wang, S.; Zeng, J.; Xie, H.; Lou, S.; Yang, J.; Yu, D.; Wang, H.; and Yang, C. 2026b. RRAttention: Dynamic Block Sparse Attention via Per-Head Round-Robin Shifts for Long-Context Inference. arXiv preprint arXiv:2602.05853.

Lu, E.; Jiang, Z.; Liu, J.; Du, Y.; Jiang, T.; Hong, C.; Liu, S.; He, W.; Yuan, E.; Wang, Y.; et al. 2026. Moba: Mixture of block attention for long-context llms. Advances in Neural Information Processing Systems, 38: 17790–17815.

Luo, S.; Guan, Y.; Li, P.; Wang, H.; and Chen, T. 2025. AsyncSpade: Eficient Test-Time Scaling with Asynchronous Sparse Decoding. arXiv preprint arXiv:2510.07486.

Milakov, M.; and Gimelshein, N. 2018. Online normalizer calculation for softmax. arXiv preprint arXiv:1805.02867.

Niu, L.; Luo, X.; Xie, L.; Sun, Y.; Yu, G.; Zhu, J.; and Zhou, S. K. 2026. Stem: Rethinking Causal Information Flow in Sparse Attention. arXiv preprint arXiv:2603.06274.

NVIDIA. 2023. TensorRT-LLM. 

### 在线资源

- [论文：arXiv 2607.25291](https://arxiv.org/abs/2607.25291)
- [代码：GitHub](https://github.com/Tencent/AngelSlim)
- [代码：GitHub](https://github.com/mit-hanlab/Block-Sparse-Attention)
- [PDF源文件](/papers/2607.25291.pdf)
