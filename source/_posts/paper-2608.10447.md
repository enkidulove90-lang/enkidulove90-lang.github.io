---
title: "Towards Efficient Reasoning in LLM-Based Recommender Systems via Model Merging"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.10447
arxiv_id: "2608.10447"
---

## 一、简介

Large language model-based recommender systems are increas- ingly adopting slow-thinking models that generate step-by-step reasoning before making predictions, often achieving higher ac curacy than fast-thinking models that predict directly. However, their reasoning traces are often unnecessarily verbose, increasing inference costs without commensurate accuracy gains. Existing training-based approaches to reasoning compression often incur substantial adaptation costs, while inference-time methods are brit tle and dificult to scale. These limitations motivate model merging as a promising training-free direction for transferring specialised behaviours between models in a shared parameter space. In particu lar, merging a slow-thinking model with a fast-thinking counterpart provides a natural mechanism for balancing recommendation ac- curacy and reasoning conciseness. To this end, we propose, to our knowledge, the first model merging framework for reasoning com- pression in recommender systems. Unlike conventional merging methods that apply uniform merge coeficients across model com- ponents, our method performs fine-grained merging at the level of individual attention heads, capturing heterogeneous patterns in recommendation reasoning. Each attention head is assigned a distinct merge coeficient according to its contribution to critical reasoning evidence and its sensitivity to parameter change, enabling selec tive injection of the concise behaviour of the fast-thinking model into the slow-thinking model and reducing reasoning verbosity without compromising recommendation quality. Experiments on three benchmark datasets show that our method reduces reason ing length by up to 24.3% while outperforming competitive model merging baselines in maintaining recommendation accuracy. The code is available at https://github.com/linhledieu/REAM.

## 二、论文方法

To transfer concise generation behaviour from a fast-thinking recommender to a slow-thinking one while preserving the reasoning that supports its predictions, we develop our method by investigat ing three questions (Figure 2 summarises the resulting pipeline): (1) which attention heads are most important to the reasoning underly ing the final prediction (§4.1)? (2) How sensitive is each head to the fast-thinking update (§4.2)? (3) How should the update be allocated to improve conciseness while limiting degradation in reasoning and recommendation quality (§4.3)?

## 三、论文里的图与解释

### 图 1

![Figure 2: Overview of the proposed framework.](/images/papers/2608.10447/7832e3b02bc301f6487e52a39d48b82c29aa0bd89f882dd3222717def8d24fb5.jpg)

**原图说明：** Figure 2: Overview of the proposed framework.

**图示解释：** 该图对应论文中的“Figure 2: Overview of the proposed framework.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 首次将模型融合用于推荐系统推理压缩：不同于已有工作将模型融合用于多域/跨域/联邦推荐的知识整合，本文首次探索通过融合快思考与慢思考推荐模型来平衡推荐准确率与推理简洁性。
2. 注意力头粒度的选择性融合：现有通用融合方法在模型组件上使用统一融合系数，REAM则在单个注意力头级别进行细粒度融合，捕捉推荐推理中的异质模式，实现选择性注入快思考行为。
3. 基于推理重要性与参数敏感度的系数分配：每个注意力头根据其对关键推理证据的贡献度（推理重要性）和对参数变化的敏感度联合确定融合系数，从而在缩短推理的同时保护对预测至关重要的推理行为。
4. 揭示通用模型融合在推荐推理压缩中的局限：系统实验表明通用融合方法虽能缩短推理长度，但无法可靠保持慢思考模型的预测行为，甚至改变其评分行为（如RMSE改善但MAE恶化）。

## 五、实验数据集选择

Models and datasets. We evaluate on Amazon Book, Amazon Music, and Yelp using the Reason4Rec rating-prediction splits [7]. Each instance provides a user’s historical ratings and reviews and a target item, with a 1–5 rating as the label. The slow-thinking model $\theta _ { S }$ is RecZero [22], fine-tuned from Qwen2.5-3B-Instruct for structured reasoning. The fast-thinking model $\theta _ { F }$ is an adapted TALLRec model [4], fine-tuned from the base Qwen2.5-3B-noninstruct to obtain a behaviourally distinct direct-prediction model, as an instruct-initialised model may retain substantial reasoning and instruction-following behaviour even when fine-tuned for di- rect rating prediction. (Appendix A.1). We use Qwen2.5-3B-Instruct as the shared base $\theta _ { B }$ for both task vectors.

Baselines. We compare REAM with the two source models and eight representative training-free baselines spanning arithmeticbased, pruning-based, and data-driven methods (Appendices A.5 and A.6). Among the data-driven baselines, AIM and ACM derive one coeficient per layer from activation statistics, whereas RAIN-Merging operates at head granularity but bases its coeficients on instruction relevance rather than recommendation reasoning—the distinction REAM’s allocation is built around. All baselines merge the same $\theta _ { S }$ and $\theta _ { F }$ using their recommended configurations.

Metrics. We report MAE and RMSE for rating accuracy and mean generated tokens per response (Tok) as a proxy for reasoning verbosity; lower is better for all metrics. Metrics are computed on parseable outputs (Appendix A.3); parse rates are near 100% for all methods except DARE+TIES, as noted in Table 1.

Implementation details. REAM and all baselines share a common configuration (calibration, hyperparameters, hardware; Ap- pendix A.3), with baseline-specific settings in Appendix A.6 and REAM’s computational overhead reported in Appendix A.4.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

- Book
- Music
- Yelp

## 八、总结

This work shows that reasoning compression in slow-thinking recommender systems depends not only on how much of the fast thinking update is merged, but also on which components receive it. To our knowledge, REAM is the first merging framework de signed for this setting, assigning each head a merge coeficient according to its retrieval criticality, decision faithfulness, and sen sitivity to parameter change. The two reasoning signals identify causally important yet largely disjoint head sets, supporting their complementary rather than redundant contributions. Across three recommendation datasets, REAM shortens reasoning while main taining accuracy, achieving a more favourable accuracy–eficiency trade-of than the evaluated training-free merging baselines. The re- maining accuracy gap at larger model scale highlights an important direction for extending selective merging to larger recommenders.

## References

[1] Pranjal Aggarwal and Sean Welleck. 2025. L1: Controlling How Long A Reasoning Model Thinks With Reinforcement Learning. arXiv:2503.04697 [cs.CL] https: //arxiv.org/abs/2503.04697

[2] Simon A. Aytes, Jinheon Baek, and Sung Ju Hwang. 2025. Sketch-of-Thought: Eficient LLM Reasoning with Adaptive Cognitive-Inspired Sketching. arXiv:2503.05179 [cs.CL] https://arxiv.org/abs/2503.05179

[3] Keqin Bao, Jizhi Zhang, Wenjie Wang, Yang Zhang, Zhengyi Yang, Yancheng Luo, Chong Chen, Fuli Feng, and Qi Tian. 2023. A Bi-Step Grounding Paradigm for Large Language Models in Recommendation Systems. arXiv:2308.08434 [cs.IR] https://arxiv.org/abs/2308.08434

[4] Keqin Bao, Jizhi Zhang, Yang Zhang, Wenjie Wang, Fuli Feng, and Xiangnan He. 2023. TALLRec: An Efective and Eficient Tuning Framework to Align Large Language Model with Recommendation. In Proceedings of the 17th ACM Conference on Recommender Systems (RecSys ’23). ACM, 1007–1014. doi:10.1145/ 3604915.3608857

[5] Steven Bird, Ewan Klein, and Edward Loper. 2009. Natural Language Processing with Python: Analyzing Text with the Natural Language Toolkit. O’Reilly Media, Inc.

[6] Jundong Chen, Honglei Zhang, Chunxu Zhang, Fangyuan Luo, and Yidong Li. 2025. Breaking the Aggregation Bottleneck in Federated Recommendation: A Personalized Model Merging Approach. arXiv:2508.12386 [cs.DC] https: //arxiv.or /abs/2508.12386

[7] Yi Fang, Wenjie Wang, Yang Zhang, Fengbin Zhu, Qifan Wang, Fuli Feng, and Xiangnan He. 2025. Reason4Rec: Large Language Models for Recommendation with Deliberative User Preference Alignment. arXiv:2502.02061 [cs.IR] https: //arxiv.org/abs/2502.02061

[8] Jingtong Gao, Zeyu Song, Chi Lu, Xiaopeng Li, Derong Xu, Maolin Wang, Peng Jiang, Kun Gai, Qingpeng Cai, and Xiangyu Zhao. 2026. Rein forced Preference Optimization for Reasoning-Augmented Recommendations. arXiv:2605.21967 [cs.IR] https://arxiv.org/abs/2605.21967

[9] Shijie Geng, Shuchang Liu, Zuohui Fu, Yingqiang Ge, and Yongfeng Zhang. 2023. Recommendation as Lan ua e Processin (RLP): A Unified Pretrain, Personalized Prompt & Predict Paradigm (P5). arXiv:2203.13366 [cs.IR] https://arxiv.org/abs 2203.13366

[10] Mor Geva, Roei Schuster, Jonathan Berant, and Omer Levy. 2021. Transformer Feed-Forward Layers Are Key-Value Memories. arXiv:2012.14913 [cs.CL] https: //arxiv.org/abs/2012.14913

[11] Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Peiyi Wang, et al. 2025. DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning. Nature 645 8081 (2025) 633–638. doi:10.1038/s41586-025-09422-z

[12] Tingxu Han, Zhenting Wang, Chunrong Fang, Shiyu Zhao, Shiqing Ma, and Zhenyu Chen. 2025. Token-Budget-Aware LLM Reasoning. arXiv:2412.18547 [cs.CL] https://arxiv.org/abs/2412.18547

[13] Bairu Hou, Yang Zhang, Jiabao Ji, Yujian Liu, Kaizhi Qian, Jacob Andreas, and Shiyu Chang. 2025. ThinkPrune: Pruning Long Chain-of-Thought of LLMs via Reinforcement Learning. arXiv:2504.01296 [cs.CL] https://arxiv.org/abs/2504. 01296

[14] Min Hou, Xin Liu, Le Wu, Chenyi He, Hao Liu, Zhi Li, Xin Li, and Si Wei. 2025. WeaveRec: An LLM-Based Cross-Domain Sequential Recommendation

Framework with Model Merging. arXiv:2510.26546 [cs.IR] https://arxiv.org/abs/ 2510.26546

[15] Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and Weizhu Chen. 2021. LoRA: Low-Rank Adaptation of Large Language Models. arXiv:2106.09685 [cs.CL] https://arxiv.org/abs/2106.09685

[16] Zhehao Huang, Yuhang Liu, Baijiong Lin, Yixin Lou, Zhengbao He, Hanling Tian, Tao Li, and Xiaolin Huang. 2026. RAIN-Merging: A Gradient-Free Method to Enhance Instruction Following in Large Reasoning Models with Preserved Thinking Format. arXiv:2602.22538 [cs.LG] https://arxiv.org/abs/2602.22538

[17] Gabriel Ilharco, Marco Tulio Ribeiro, Mitchell Wortsman, Suchin Gururangan, Ludwig Schmidt, Hannaneh Hajishirzi, and Ali Farhadi. 2023. Editing Models with Task Arithmetic. arXiv:2212.04089 [cs.LG] https://arxiv.org/abs/2212.04089

[18] Ji

### 在线资源

- [论文：arXiv 2608.10447](https://arxiv.org/abs/2608.10447)
- [代码：GitHub](https://github.com/linhledieu/REAM)
- [PDF源文件](/papers/2608.10447.pdf)
