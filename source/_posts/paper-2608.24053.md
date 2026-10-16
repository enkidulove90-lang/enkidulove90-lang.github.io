---
title: "WeMM-Embedding: WeChat Multi-Modal Embedding Technical Report"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.24053
arxiv_id: "2608.24053"
---

## 一、简介

Universal multimodal embeddings are becoming a core component of modern AI systems, enabling heterogeneous content to be represented in a shared space for applications such as retrieval, recommendation, classification, and agentic systems. In this report, we present WeMM-Embedding, a family of universal multimodal embedding models supporting text, images, videos, visual documents, and arbitrarily interleaved multimodal inputs with flexible output dimensions. The family comprises 2B, 4B, and 9B variants and is trained in two stages: a large-scale multimodal align ment stage, followed by a refinement stage using curated data, fine-grained relevance supervision, and cross-scale knowledge transfer. Across extensive evaluations, WeMM-Embedding achieves leading performance on multiple public benchmarks. Notably, the 2B variant already surpasses the previously leading 8B open-source baseline on MMEB-v2, while the 9B variant further achieves a new state-of-the-art overall score of 80.6. WeMM-Embedding also demonstrates strong practical performance across WeChat applications, with substantial gains on a 26-task in-house benchmark and consistent improvements across 14 online A/B tests. It has been deployed at scale across recommendation and search applications, including WeChat Channels, Oficial Accounts, Moments, and e-commerce services. We have released the model weights and code to facilitate future research.

G https://huggingface.co/collections/tencent/wemm-embedding https://github.com/Tencent/WeMM-Embedding

Date: August 26, 2026

![](images/e279c030f55ffc135f1e69c3f048612c576f8180e483fbc757dd42938d351e64.jpg)  
 % #&"  % #&"   % #&"   , &	% #&" , &	% #&"  %#&#% #&" %.'&'+ '-" \*\$)#%'\$	

![](images/6b20e2d0dc40d5da708006906c01235740c19fb3379bf0fbad6d4299735edcad.jpg)  
Figure 1 Performance and efficiency overview of WeMM-Embedding. Left: MMEB-v2 overall performance across diferent model sizes, compared with representative baselines. Right: Aggregate performance on the MMEB-v2 image and video subsets, a 12-dataset cross-modal retrieval suite, and the 26-task in-house benchmark.

## 二、论文方法

WeMM-Embedding基于Qwen3.5原生多模态骨干，采用last-token pooling方式，在输入序列末尾添加专用<embedding> token并取其最后一层隐状态经L2归一化作为表示。训练分两阶段：第一阶段在数亿级pair-based数据上使用InfoNCE对比学习和分级相关性CoSENT排序损失进行大规模多任务对齐；第二阶段在精选数据上引入重排序模型监督和跨规模嵌入蒸馏进行精调。所有目标均结合MRL在多个嵌入维度上独立计算。

## 三、论文里的图与解释

### 图 1

![Figure 2 Overview of our multimodal training data. Major data families and representative coverage across diverse task settings and content domains.](/images/papers/2608.24053/2dcc6661f27b363db3819560518c94a168ceecf463e01f32942b6649d0776ccc.jpg)

**原图说明：** Figure 2 Overview of our multimodal training data. Major data families and representative coverage across diverse task settings and content domains.

**图示解释：** 该图对应论文中的“Figure 2 Overview of our multimodal training data. Major data families and representative coverage across diverse task settings and content domains.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 提出两阶段渐进式训练策略：第一阶段在数亿级异构多模态数据上建立广泛对齐，第二阶段在精选数据上通过语义平衡重采样、质量过滤和难负样本增强实现细粒度相关性学习，兼顾覆盖广度与匹配精度。
2. 设计基于Semantic-ID引导的数据重采样方法：利用RQ-KMeans对嵌入表示进行三级量化得到语义ID，根据码本分配密度调整采样率，缓解高频语义模式的重复曝光问题，提升数据语义平衡性。
3. 引入多源监督信号融合机制：结合对比学习、分级相关性排序（score-gap-weighted CoSENT）、重排序模型监督和跨规模嵌入蒸馏，在统一pair-based框架下灵活适配不同监督信号。
4. 支持灵活嵌入维度与多位置嵌入token：通过Matryoshka Representation Learning支持单次前向获取多种维度嵌入，并允许在序列不同位置插入多个<embedding> token以同时提取单模态和联合模态表示。

## 五、实验数据集选择

- MMEB-v2
- MMEB-v3
- MSCOCO
- Flickr30k
- DOCCI
- TextCaps
- VATEX
- MSR-VTT
- YouCook2
- ViDoRe V2
- MCMR
- 26-task in-house benchmark (WeChat)

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

The MMEB series provides a comprehensive evaluation across diverse modalities, task formulations, and retrieval scenarios. Specifically, MMEB-v2 [28] evaluates general multimodal embedding capabilities across images, videos, and visual documents, while MMEB-v3 [15] further extends the evaluation to audio, complex text retrieval, and agent-centric scenarios. In this section, we follow the benchmark-defined evaluation metrics, using Hit@1 for image, video, audio, and agent tasks and NDCG@5 for text and visual-document tasks.

## 八、总结

In this report, we introduced WeMM-Embedding, a family of universal multimodal embedding models spanning multiple scales. The family is trained with a two-stage strategy that progresses from broad multimodal alignment to finer-grained representation learning through curated data, richer relevance supervision, and cross-scale knowledge transfer. Extensive evaluations across public benchmarks demonstrate that WeMM-Embedding achieves state-of-the-art performance and establishes a new performance–eficiency frontier. Moreover, it delivers consistent gains on the 26-task in-house benchmark and across 14 online A/B tests. WeMM-Embedding has also been deployed at scale across multiple recommendation and search systems within WeChat, further demonstrating its practical value. In the future, we will continue to extend WeMM-Embedding toward omni-modal inputs, scale the model family to larger sizes, and further improve data curation and fine-grained relevance supervision.

## References

[1] Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, et al. Gpt-4 technical report. arXiv preprint arXiv:2303.08774, 2023.

[2] Yingshan Chang, Mridu Narang, Hisami Suzuki, Guihong Cao, Jianfeng Gao, and Yonatan Bisk. Webqa: Multihop and multimodal qa. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 16495–16504, 2022.

[3] Ben Chen, Xian Guo, Siyuan Wang, Zihan Liang, Yue Lv, Yufei Ma, Xinlong Xiao, Bowen Xue, Xuxin Zhang, Ying Yang, et al. Onesearch: A preliminary exploration of the unified end-to-end generative framework for e-commerce search. arXiv preprint arXiv:2509.03236, 2025.

[4] Haonan Chen, Liang Wang, Nan Yang, Yutao Zhu, Ziliang Zhao, Furu Wei, and Zhicheng Dou. mme5: Improving multimodal multilingual embeddings via high-quality synthetic data. arXiv preprint arXiv:2502.08468, 2025.

[5] Haonan Chen, Sicheng Gao, Radu Timofte, Tetsuya Sakai, and Zhicheng Dou. e5-omni: Explicit cross-modal alignment for omni-modal embeddings. In Findings of the Association for Computational Linguistics: ACL 2026, pages 19430–19443, 2026.

[6] Haonan Chen, Chu Li, Zhicheng Wang, Yuanwei Liu, Yuanjiang Wang, Shaohua Jiang, and Zhicheng Dou. Douyin multimodal embedding model technical report, 2026. URL https://arxiv.org/abs/2608.02148.

[7] Xinlei Chen, Hao Fang, Tsung-Yi Lin, Ramakrishna Vedantam, Saurabh Gupta, Piotr Dollár, and C Lawrence Zitnick. Microsoft coco captions: Data collection and evaluation server. arXiv preprint arXiv:1504.00325, 2015.

[8] Zhe Chen, Weiyun Wang, Hao Tian, Shenglong Ye, Zhangwei Gao, Erfei Cui, Wenwen Tong, Kongzhi Hu, Jiapeng Luo, Zheng Ma, et al. How far are we to gpt-4v? closing the gap to commercial multimodal models with open-source suites. arXiv preprint arXiv:2404.16821, 2024.

[9] Prateek Chhikara, Dev Khant, Saket Aryan, Taranjeet Singh, and Deshraj Yadav. Mem0: Building productionready ai agents with scalable long-term memory. arXiv preprint arXiv:2504.19413, 2025.

[10] Wei Chow, Yuan Gao, Linfeng Li, Xian Wang, Qi Xu, Hang Song, Lingdong Kong, Ran Zhou, Yi Zeng, Yidong Cai, et al. Merit: Multilingual semantic retrieval with interleaved multi-condition query. Advances in Neural Information Processing Systems, 38:74806–74867, 2025.

[11] Xuanming Cui, Jianpeng Cheng, Hong-you Chen, Satya Narayan Shukla, Abhijeet Awasthi, Xichen Pan, Chaitanya Ahuja, Shlok Mishra, Taipeng Tian, Qi Guo, et al. Think then embed: Generative context improves multimodal embedding. In International Conference on Learning Representations, volume 2026, pages 2690–2709, 2026.

[12] Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. Imagenet: A large-scale hierarchical image database. In 2009 IEEE conference on computer vision and pattern recognition, pages 248–255. Ieee, 2009.

[13] Jiaxin Deng, Shiyao Wang, Kuo Cai, Lejian Ren, Qigen Hu, Weifeng Ding, Qiang Luo, and Guorui Zhou. Onerec: Unifying retrieve and rank with generative recommender and iterative preference alignment. CoRR, abs/2502.18965, 2025. doi: 10.48550/ARXIV.2502.18965. URL https://doi.org/10.48550/arXiv.2502.18965.

[14] Wenbo Hu, Jia-Chen Gu, Zi-Yi Dou, Mohsen Fayyaz, Pan Lu, Kai-Wei Chang, and Nanyun Peng. Mrag-bench: Vision-centric evaluation for retrieval-augmented multimodal models. arXiv preprint arXiv:2410.08182, 2024.

[15] Haohang Huang, Xuan Lu, Mingyi Su, Xuan Zhang, Ziyan Jiang, Ping Nie, Kai Zou, Tomas Pfister, Wenhu Chen, Wei Zhang, et al. Mmeb-v3: Measuring the performance gaps of omni-modality embedding models. arXiv preprint arXiv:2604.23321, 2026.

[16] Xiang Huang, Hao Peng, Dongcheng Zou, Zhiwei Liu, Jianxin Li, Kay Liu, Jia Wu, Jianlin Su, and Philip S. Yu. Cosent: Consistent sentence embedding via similarity ranking. IEEE ACM Trans. Audio Speech Lang. Process., 32:2800–2813, 2024. doi: 10.1109/TASLP.2024.3402087. URL https://doi.org/10.1109/TASLP.2024.3402087.


### 在线资源

- [论文：arXiv 2608.24053](https://arxiv.org/abs/2608.24053)
- [代码：GitHub](https://github.com/Tencent/WeMM-Embedding)
- [PDF源文件](/papers/2608.24053.pdf)
