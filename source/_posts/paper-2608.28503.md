---
title: "SG-UMP: Sequence-Guided Universal Multimodal Prioritization Calculation Framework"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.28503
arxiv_id: "2608.28503"
---

## 一、简介

Multimodal sequential recommendation (MSR) improves recommendation by incorporating heterogeneous information such as text, images, and user interactions. However, existing MSR meth ods often fail to capture user-level preference heterogeneity and dataset-level modality bias, limiting their adaptability across users and datasets. To address this issue, we propose Sequence-Guided Universal Multimodal Prioritization Calculation Framework (SG-UMP), a plug-and-play plugin for enhancing multimodal informa tion processing in MSR. SG-UMP includes a Module Combiner for flexible multimodal processing and a Module Router for dynamic module ordering, enabling adaptation to both user preferences and dataset characteristics. Experiments on four real-world datasets show that SG-UMP consistently improves recommendation performance across diferent backbones and multimodal settings. The code is available at https://github.com/esemsc-xz524/SG-UMP.

## 二、论文方法

Xinyi Zhang Imperial College London London, UK zxyzxy090588@163.com

Yutong Li University College London London, UK lyt3612671@163.com

Peijie Sun∗ Nanjing University of Posts and Telecommunications Nanjing, China sun.hfut@gmail.com

## 三、论文里的图与解释

### 图 1

![Figure 2: Illustration of SG-UMP and its components. (a) Overall framework of SG-UMP, where the Module Combiner integrates the Frequency Filter Layer, Hierarchical Attention Layer, and Multi-Scale Fusion Layer. (b) Module Router structure. (c) Frequency Filter Layer. (d) Hierarchical Attention Layer. (e) Multi-Scale Fusion Layer.](/images/papers/2608.28503/fccd40f3d44c3b8fc4af3a058854104d2f2aaeb41e49683dde42bd3fb3d2fc8f.jpg)

**原图说明：** Figure 2: Illustration of SG-UMP and its components. (a) Overall framework of SG-UMP, where the Module Combiner integrates the Frequency Filter Layer, Hierarchical Attention Layer, and Multi-Scale Fusion Layer. (b) Module Router structure. (c) Frequency Filter Layer. (d) Hierarchical Attention Layer. (e) Multi-Scale Fusion Layer.

**图示解释：** 该图对应论文中的“Figure 2: Illustration of SG-UMP and its components. (a) Overall framework of SG-UMP, where the Module Combiner integrates the Frequency Filter Layer, Hierarchical Attention Layer, and Multi-Scale Fusion Layer. (b) Module Router structure. (c) Frequency Filter Layer. (d) Hierarchical Attention Layer. (e) Multi-Scale Fusion Layer.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Figure 3: Visualization analysis. ${ ( \mathbf { a } ) , ( \mathbf { b } ) } .$ , and (c) correspond to STOSA with pre-trained embeddings, the approximated user perspective based on salient item features, and SG-UMP + STOSA, respectively. Red text highlights important attributes, and the intensity of the green background indi cates attention assigned by the model.](/images/papers/2608.28503/eeacc17bf8c64c866f69b8b9e229ef0cfff7cd5e15ab77667c09c23c3c6f3680.jpg)

**原图说明：** Figure 3: Visualization analysis. ${ ( \mathbf { a } ) , ( \mathbf { b } ) } .$ , and (c) correspond to STOSA with pre-trained embeddings, the approximated user perspective based on salient item features, and SG-UMP + STOSA, respectively. Red text highlights important attributes, and the intensity of the green background indi cates attention assigned by the model.

**图示解释：** 该图对应论文中的“Figure 3: Visualization analysis. ${ ( \mathbf { a } ) , ( \mathbf { b } ) } .$ , and (c) correspond to STOSA with pre-trained embeddings, the approximated user perspective based on salient item features, and SG-UMP + STOSA, respectively. Red text highlights important attributes, and the intensity of the green background indi cates attention assigned by the model.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 提出两条多模态序列推荐设计原则：一是利用用户历史交互序列引导个性化多模态表示处理以建模用户级偏好异质性；二是支持模块化、可重排序的处理流程以适应不同数据集的模态偏差。
2. 设计Module Combiner，集成频率滤波层（去噪并提取稳定低频模式）、层次注意力层（自适应融合模态信号）和多尺度融合层（基于MoE建模模态间交互），形成完整的多模态嵌入处理流水线。
3. 提出Module Router，通过模态感知路由机制动态确定三个功能模块的执行顺序，并引入条件互信息（CMI）正则化损失，鼓励输入感知和多样化的路由策略，防止退化为固定执行路径。
4. 将SG-UMP设计为即插即用插件，不替换序列推荐骨干本身，而是增强现有多模态序列推荐模型的多模态信息处理能力，在多种骨干和数据集上均取得一致提升。

## 五、实验数据集选择

Datasets. We evaluate our model on four datasets: Amazon1 Home, Beauty, Ofice, and Yelp2. The Amazon datasets capture purchasing behavior and reviews across diverse domains, serving as widely used benchmarks for SR [7, 20]. The Yelp dataset, sourced from a business platform, contains restaurant reviews and is widely used in recommendation tasks [22, 46]. All datasets are pre-processed using a 5-core setting [7, 20, 22, 46], ensuring each user and item has at least five interactions. Detailed dataset statistics are provided in Table 1.

Table 1: Datasets Statistics

<table><tr><td>Dataset</td><td>#users</td><td>#items</td><td>#interactions</td><td>density</td><td>avg.length</td></tr><tr><td>Home</td><td>66,519</td><td>28,237</td><td>551,682</td><td>0.03%</td><td>8.3</td></tr><tr><td>Beauty</td><td>22,363</td><td>12,101</td><td>198,502</td><td>0.05%</td><td>8.3</td></tr><tr><td>Office</td><td>4,905</td><td>2,421</td><td>53,258</td><td>0.04%</td><td>10.8</td></tr><tr><td>Yelp</td><td>287,116</td><td>148,523</td><td>4,392,169</td><td>0.01%</td><td>15.3</td></tr></table>

Evaluation Settings. To ensure fair and rigorous evaluation, we adopt the standard leave-one-out strategy [7, 20], where the last item in each user sequence is used for testing, the second-to-last for validation, and the rest for training. We report performance using widely-used metrics [20, 21, 39, 48]: Recall@K (R@K) and NDCG@K (N@K), with $K = 1 0$ and 20. Higher R@K and N@K indicate better recommendation accuracy.

Baselines. We compare our proposed model with representative recommendation models, categorized into two groups: (1) Tradi tional Recommendation: SASRec [20], BERT4-Rec [35], Light GCN [13], STOSA [7], FMLP-Rec [48] and Oracle4Rec [41]. (2) Mul timodal Recommendation: VBPR [12], MMMLP [24], MML [29], MMSR [17], MMSBR [45] and MP4SR [43].

Implementation Details. For fair comparison, baselines are configured using reported hyperparameters or tuned via grid search on validation sets when unavailable. We adopt CLIP ViT-B/323 as the unified encoder for both text and image modalities. Key hyperparameters are selected via grid search, including the number of shared and task experts {1, 2, 3, 4, 5}, the mutual information loss weight $\alpha \in \{ 0 . 1 , 0 . 2 , 0 . 5 , 1 . 0 , 2 . 0 \}$ , and the number of Frequency Filter layers {1, 2, 3, 4, 5}. Results are averaged over 5 runs and are statistically significant $( p < 0 . 0 5 )$ . All experiments are conducted on an NVIDIA 4090 GPU.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

- Amazon Home
- Amazon Beauty
- Amazon Office
- Yelp

## 八、总结

This paper proposes SG-UMP, a plug-and-play plugin for enhancing multimodal information processing in MSR. To address user-level preference heterogeneity and dataset-level modality bias, SG-UMP introduces a Module Combiner for flexible multimodal processing and a Module Router for dynamic module ordering. Experiments on multiple real-world datasets demonstrate that SG-UMP con sistently improves recommendation performance across diferent backbones and multimodal settings. In future work, we will explore more eficient routing strategies and extend SG-UMP to additional modalities and recommendation scenarios.

## References

[1] Tadas Baltrušaitis, Chaitanya Ahuja, and Louis-Philippe Morency. 2018. Multi modal machine learning: A survey and taxonomy. IEEE transactions on pattern analysis and machine intelligence 41, 2 (2018), 423–443.

[2] Nils Bertschinger, Johannes Rauh, Eckehard Olbrich, Jürgen Jost, and Nihat Ay. 2014. Quantifying unique information. Entropy 16, 4 (2014), 2161–2183.

[3] Xu Chen, Hanxiong Chen, Hongteng Xu, Yongfeng Zhang, Yixin Cao, Zheng Qin, and Hongyuan Zha. 2019. Personalized Fashion Recommendation with Visual Explanations based on Multimodal Attention Network: Towards Visually Explainable Recommendation. In Proceedings of the 42nd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR’19). Association for Computing Machinery, New York, NY, USA, 765–774.

[4] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. In Proceedings ofthe 2019Conference ofthe North American Chapter ofthe Association for Computational Linguistics: Human Language Technologies, NAACL-HLT 2019, Minneapolis, MN, USA, June 2–7, 2019, Volume 1 (Long and Short Papers). Associa tion for Computational Linguistics, Minneapolis, Minnesota, USA, 4171–4186.

[5] Pierre Duhamel and Martin Vetterli. 1990. Fast Fourier transforms: a tutorial review and a state of the art. Signal processing 19, 4 (1990), 259–299.

[6] Qile Fan, Penghang Yu, Zhiyi Tan, Bing-Kun Bao, and Guanming Lu. 2025. BeFA: a general behavior-driven feature adapter for multimedia recommendation. In Proceedings ofthe Thirty-Ninth AAAI Conference on Artificial Intelligence (AAAI’25). AAAI Press, Washington, USA, Article 1293, 11 pages.

[7] Ziwei Fan, Zhiwei Liu, Yu Wang, Alice Wang, Zahra Nazari, Lei Zheng, Hao Peng, and Philip S. Yu. 2022. Sequential Recommendation via Stochastic Self-Attention. In Proceedings of the ACM Web Conference 2022 (WWW ’22). Association for Computing Machinery, New York, NY, USA, 2036–2047.

[8] Hui Fang, Danning Zhang, Yiheng Shu, and Guibing Guo. 2020. Deep Learning for Sequential Recommendation: Algorithms, Influential Factors, and Evaluations. ACM Trans. Inf. Syst. 39, 1 (2020), 42 pages.

[9] Guibing Guo, Jie Zhang, and Neil Yorke-Smith. 2015. TrustSVD: collaborative filtering with both the explicit and implicit influence of user trust and of item rat ings. In Proceedings of the Twenty-Ninth AAAI Conference on Artificial Intelligence (AAAI’15). AAAI Press, New York, NY, USA, 123–129.

[10] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. 2016. Deep residual learning for image recognition. In Proceedings of the IEEE conference on computer vision and pattern recognition. 770–778.

[11] Ruining He and Julian McAuley. 2016. Fusing similarity models with Markov chains for sparse sequential recommendation. In 2016 IEEE 16th International Conference on Data Mining (ICDM). IEEE Computer Society, Barcelona, Spain, 191–200.

[12] Ruining He and Julian McAuley. 2016. VBPR: visual Bayesian Personalized Ranking from implicit feedback. In Proceedings ofthe Thirtieth AAAI Conference on Artificial Intelligence (AAAI’16). AAAI Press, Phoenix, Arizona, 144–150.

[13] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, YongDong Zhang, and Meng Wang. 2020. LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation. In Proceedings ofthe 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR ’20). Association for Computing Machinery, New York, NY, USA, 639–648.

[14] Balázs Hidasi, Alexandros Karatzoglou, Linas Baltrunas, and Domonkos Tikk. 2016. Session-based Recommendations with Recurrent Neural Networks. In 4th International Conference on Learning Representations, ICLR 2016, San Juan, Puerto Rico, May 2-4, 2016, Conference Track Proceedings, Yoshua Bengio and Yann LeCun (Eds.). ICLR, San Juan, Puerto Rico.

[15] Sepp Hochreiter and Jürgen Schmidhuber. 1997. Long short-term memory

### 在线资源

- [论文：arXiv 2608.28503](https://arxiv.org/abs/2608.28503)
- [代码：GitHub](https://github.com/esemsc-xz524/SG-UMP)
- [PDF源文件](/papers/2608.28503.pdf)
