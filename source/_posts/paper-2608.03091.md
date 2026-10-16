---
title: "Position Bias Undermines Preference Consistency in Listwise LLM-Based Reranking"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.03091
arxiv_id: "2608.03091"
---

## 一、简介

Large language models (LLMs) have emerged as promising list wise rerankers for recommender systems, but their reliability under equivalent candidate permutations remains unclear. Since recommendation candidates form an unordered set, a reranker should not depend on the arbitrary order used to serialize them. However, decoder-only LLM rerankers can allow input order to afect model scores, pairwise preferences, and rankings. We study how position bias afects the ranking process induced by LLM-based rerankers. Instead of measuring only changes in final ranked lists, we treat rankings produced under equivalent candidate permutations as observations of an induced preference system. We introduce an evaluation framework measuring pairwise preference instability, global preference inconsistency, and listwise output consistency. This framework characterizes candidate-order sensitivity at the pairwise, global, and output levels. Experiments across multiple LLMs, datasets, and list lengths show that these consistency measures are closely aligned, but can diverge from recommendation efectiveness and marginal position-exposure bias. Improving rel evance or flattening exposure across positions does not necessarily restore stable pairwise preferences, globally coherent prefer ence structures, or consistent ranked outputs. These results show that reducing marginal exposure skew is insuficient to establish ranking-function validity in LLM-based reranking. Code is available at https://github.com/ejbito/InvariRank.

## 二、论文方法

论文将用户上下文和候选集下的列表式重排序建模为排序函数，采样M个候选排列并提取排序，构建诱导偏好系统Q。定义PPI为分桶条件下成对偏好概率的最大最小差，GPI为加权Kemeny秩聚合目标下的近似最优排序分歧，LOC用Kendall's τ衡量采样排序间平均成对一致性，并额外测量top-k曝光随输入位置的变化。

## 三、论文里的图与解释

### 图 1

![PPI and GPI across candidate-list lengths for Llama-3.2-3B-Instruct on MovieLens-32M. Lower values indicate greater preference consistency.](/images/papers/2608.03091/figure_001_figure2_instability_decomposition.png)

**原图说明：** PPI and GPI across candidate-list lengths for Llama-3.2-3B-Instruct on MovieLens-32M. Lower values indicate greater preference consistency.

**图示解释：** 该图对应论文中的“PPI and GPI across candidate-list lengths for Llama-3.2-3B-Instruct on MovieLens-32M. Lower values indicate greater preference consistency.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Top-5 exposure by input position on MovieLens-32M using Llama-3.2-3B-Instruct for list lengths $K \in \{15,25,50\}$.](/images/papers/2608.03091/figure_002_figure1_exposure.png)

**原图说明：** Top-5 exposure by input position on MovieLens-32M using Llama-3.2-3B-Instruct for list lengths $K \in \{15,25,50\}$.

**图示解释：** 该图对应论文中的“Top-5 exposure by input position on MovieLens-32M using Llama-3.2-3B-Instruct for list lengths $K \in \{15,25,50\}$.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 提出将等价候选排列下的排序视为诱导偏好系统观测的新视角，从排序函数有效性角度而非仅最终列表变化角度研究位置偏差。
2. 设计了多层级一致性评估框架，包括成对偏好不稳定性PPI、全局偏好不一致性GPI和列表级输出一致性LOC，分别刻画局部、全局和输出层面的候选顺序敏感性。
3. 揭示了推荐效果、边际位置曝光偏差与排列一致性之间的背离现象：STELLA_LW获得最高HR@5且曝光曲线更平坦，但PPI、GPI最差、LOC最低。
4. 通过分桶条件化偏好概率和加权Kemeny秩聚合近似求解，使成对与全局一致性度量在有限采样排列下可计算。

## 五、实验数据集选择

Datasets. We evaluate on MovieLens-32M and Amazon Books. User interactions are ordered chronologically and split temporally into training and evaluation sets. For each evaluation query, the user history is constructed from past interactions, and held-out interactions are used as relevant items. Each evaluated candidate set contains at least one held-out relevant item.

Retrieval. Candidate sets are constructed using LightGCN as a first-stage retriever [12]. We follow a standard two-stage recommen dation pipeline [8, 27], in which a first-stage recommender produces a candidate set and an LLM reranks it. For each query, we take the top-� candidate items for LLM reranking, with � ∈ {15, 25, 50}.

Models and ranking extraction. We evaluate three instructiontuned decoder-only LLMs: Llama-3.2-3B-Instruct, Mistral-7B-Instructv0.3, and Qwen2.5-7B-Instruct. All models use the same prompt tem plate. Evaluation rankings are extracted from token log-probabilities over candidate marker identifiers instead of sampled text generation [3, 28]. This makes ranking deterministic for a fixed serialized input and avoids failures from parsing generated ranked lists. Con sequently, variation across evaluation rankings is induced by candi date permutation rather than decoding randomness or formatting errors. For each query and method, we evaluate � = 20 candidate permutations.

Baselines. We compare zero-shot listwise reranking with three position-bias mitigation baselines. Bootstrapping aggregates rankings from independently shufled candidate orders using Borda count [13]. SGS iteratively selects the highest-ranked candidate, removes it, and reshufles the remaining candidates [2]. STELLALW adapts STELLA [17] to listwise ranking. Its generation-based calibration stage uses up to 150 probing candidate sets, places each relevant candidate at every input position, and repeats each placement five times with shufled non-target candidates to estimate a smoothed position-transition matrix. At inference, STELLALW maintains a candidate-level Bayesian posterior and updates it using the input position of the model’s top-ranked candidate over the original and shufled candidate orders. It performs up to ten updates with early stopping, returns the ranking induced by the minimum-entropy posterior, and falls back to the raw ranking when the posterior information gain is negligible. Remaining settings are provided in the repository.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

Efectiveness. Table 1 reports efectiveness and consistency at � = 25. STELLA obtains the highest HR@5 for all three models on both datasets. The best nDCG@5 varies across methods: SGS performs best for Llama-3B on MovieLens-32M, STELLALW for Mistral-7B on both datasets, and bootstrapping in the remaining three settings. Thus, even standard efectiveness metrics do not consistently favour the same mitigation method.

Preference consistency. PPI and GPI exhibit the same method ordering across both datasets and all three models. Relative to zeroshot reranking, bootstrapping reduces both pairwise instability and global inconsistency, while SGS produces the lowest PPI and GPI throughout. In contrast, STELLA produces the highest PPI and GPI in every setting, despite obtaining the highest HR@5. Figure 2 shows that this ordering also persists across $K \in \{ 1 5 , 2 5 , 5 0 \}$ for Llama-3B on MovieLens-32M. Improving top-ranked relevance therefore does not necessarily yield stable pairwise preferences or a globally coherent induced preference system.

Output consistency. LOC follows the same method ordering as PPI and GPI across all six model–dataset combinations. Bootstrapping improves agreement over zero-shot reranking, SGS produces the most consistent ranked outputs, and STELLA produces the lowest LOC, with all values below 0.13. The agreement among PPI, GPI, and LOC shows that candidate-order sensitivity is reflected consistently at the pairwise, global, and ranked-output levels. Their divergence from HR@5 demonstrates that recommendation efectiveness alone does not establish permutation consistency.

Marginal position exposure. Figure 1 shows top-5 exposure across input positions on MovieLens-32M using Llama-3B for $K \in$ {15, 25, 50}. Zero-shot reranking exhibits substantial positional skew, with early input positions receiving lower exposure than later positions. Bootstrapping reduces this skew but does not eliminate it, while STELLALW and SGS produce flatter exposure curves.

These results distinguish marginal exposure correction from permutation consistency. STELLALW flattens exposure across input positions, yet produces the highest PPI and GPI and the lowest

Figure 1: Top-5 exposure by input position on MovieLens-32M using Llama-3.2-3B-Instruct for list lengths � ∈ {15, 25, 50}.  
![](images/deae01ab86a7d8eedd8a814fb867b2a27fe48e12985847f09007261a7e16fc82.jpg)  
(a) K= 15

![](images/b6f149b9b34076310dae4e7406e4c11e9850ef2bf39d6b7fed958297d30d9722.jpg)  
(b) K = 25

![](images/2d74cc4f99ea975bb5fcdda40d43b062a058fc56d3490679e66401b2409e087d.jpg)  
(c) K= 50

Table 1: Reranking efectiveness and consistency on MovieLens-32M and Amazon Books with � = 25. Higher is better for HR@5, nDCG@5, and LOC (Kendall’s �); lower is better for PPI and GPI.

<table><tr><td rowspan="2">Model</td><td rowspan="2">Method</td><td colspan="5">MovieLens-32M</td><td colspan="4">Amazon Books</td></tr><tr><td>HR@5 ↑</td><td>nDCG@5 ↑</td><td>PPI ↓</td><td>GPI ↓</td><td>LOC ↑</td><td>HR@5 ↑</td><td>nDCG@5 ↑</td><td>PPI ↓</td><td>GPI ↓</td></tr><tr><td rowspan="4">Llama-3B</td><td>Zero-shot</td><td>0.5560</td><td>0.2301</td><td>0.4775</td><td>0.1149</td><td>0.6358</td><td>0.2145</td><td>0.1477</td><td>0.3853</td><td>0.0983</td></tr><tr><td>Bootstrapping</td><td>0.5480</td><td>0.2256</td><td>0.2992</td><td>0.0827</td><td>0.7475</td><td>0.2302</td><td>0.1590</td><td>0.2387</td><td>0.0668</td></tr><tr><td> $\text{STELLA}_{\text{LW}}$ </td><td>0.5922</td><td>0.2318</td><td>0.8331</td><td>0.3648</td><td>0.1181</td><td>0.2345</td><td>0.1583</td><td>0.8337</td><td>0.3644</td></tr><tr><td>SGS</td><td>0.5634</td><td>0.2324</td><td>0.1972</td><td>0.0586</td><td>0.8268</td><td>0.2117</td><td>0.1466</td><td>0.1876</td><td>0.0571</td></tr><tr><td rowspan="4">Mistral-7B</td><td>Zero-shot</td><td>0.4794</td><td>0.1778</td><td>0.4726</td><td>0.1195</td><td>0.6290</td><td>0.2325</td><td>0.1604</td><td>0.4329</td><td>0.1147</td></tr><tr><td>Bootstrapping</td><td>0.4790</td><td>0.1771</td><td>0.2970</td><td>0.0831</td><td>0.7481</td><td>0.2320</td><td>0.1613</td><td>0.2787</td><td>0.0796</td></tr><tr><td> $\text{STELLA}_{\text{LW}}$ </td><td>0.5490</td><td>0.1917</td><td>0.8902</td><td>0.3861</td><td>0.0616</td><td>0.2435</td><td>0.1643</td><td>0.8452</td><td>0.3410</td></tr><tr><td>SGS</td><td>0.4840</td><td>0.1753</td><td>0.2150</td><td>0.0643</td><td>0.8107</td><td>0.2335</td><td>0.1554</td><td>0.1956</td><td>0.0591</td></tr><tr><td rowspan="4">Qwen-7B</td><td>Zero-shot</td><td>0.5344</td><td>0.2136</td><td>0.5408</td><td>0.1372</td><td>0.5799</td><td>0.2530</td><td>0.1627</td><td>0.4496</td><td>0.1219</td></tr><tr><td>Bootstrapping</td><td>0.5450</td><td>0.2166</td><td>0.3288</td><td>0.0938</td><td>0.7198</td><td>0.2535</td><td>0.1759</td><td>0.2844</td><td>0.0831</td></tr><tr><td> $\text{STELLA}_{\text{LW}}$ </td><td>0.5528</td><td>0.2086</td><td>0.8328</td><td>0.3615</td><td>0.1230</td><td>0.2594</td><td>0.1652</td><td>0.8291</td><td>0.3342</td></tr><tr><td>SGS</td><td>0.5366</td><td>0.2152</td><td>0.2654</td><td>0.0804</td><td>0.7641</td><td>0.2460</td><td>0.1641</td><td>0.2202</td><td>0.0661</td></tr></table>

LOC. Reducing average position-dependent exposure is therefore insuficient to recover stable pairwise preferences, a coherent global preference structure, or consistent ranked outputs. SGS improves both marginal exposure and all three consistency measures in the examined setting, showing that these properties can improve together but are not equivalent.

Eficiency. The methods difer substantially in inference cost. Zero-shot reranking requires one forward pass per candidate set, while bootstrapping aggregates three shufled passes. With selection size one, SGS requires � sequential passes, corresponding to 25 when $K = 2 5 . \mathrm { S T E L A _ { L W } }$ performs up to ten inference-time ranking queries with early stopping and additionally requires a one-of calibration stage. We use up to 150 probing candidate sets in this stage, placing each relevant candidate at every input position and repeating each placement five times.

Summary. Across both datasets, PPI, GPI, and LOC provide closely aligned assessments of candidate-order sensitivity, but can diverge from recommendation efectiveness and marginal position exposure bias. $\mathrm { S T E L L A _ { L W } }$ obtains the highest HR@5 while per forming worst on all three consistency measures, and produces flatter exposure in the examined MovieLens-32M setting. SGS gives the strongest consistency and comparatively flat exposure, but requires sequential inference. These trade-ofs motivate evaluating LLM-based rerankers using efectiveness, permutation consistency, marginal exposure, and inference cost together.

Figure 2: PPI and GPI across candidate-list lengths for Llama-3.2-3B-Instruct on MovieLens-32M. Lower values indicate greater preference consistency.  
![](images/a8a063ddc948dd7b10d319605158a536f3e49c66f8d5255f3d2a6492983849a2.jpg)  
(a) PPI

![](images/23b446d5438ea30e32c7bbf66cf8d0d91f3e3455b5f7fdf2ca84d5c2ea30035e.jpg)  
(b) GPI

## 八、总结

We study the reliability of listwise LLM-based rerankers under equivalent candidate permutations. By treating the resulting rankings as observations of an induced preference system, we characterize candidate-order sensitivity at the pairwise, global, and ranked-output levels. Across models and datasets, PPI, GPI, and LOC provide closely aligned assessments of permutation consistency, but can diverge from recommendation efectiveness and marginal position-exposure bias. In particular, improving top-ranked relevance or flattening exposure across positions does not necessarily restore stable preferences or consistent rankings. These findings show that marginal exposure correction alone is insuficient to establish ranking-function validity and motivate evaluating LLM-based rerankers using efectiveness and consistency together.

## References

[1] Keqin Bao, Jizhi Zhang, Yang Zhang, Wenjie Wang, Fuli Feng, and Xiangnan He. 2023. TALLRec: An Efective and Eficient Tuning Framework to Align Large Language Model with Recommendation. In Proceedings ofthe 17th ACM Conference on Recommender Systems (RecSys ’23). ACM, 1007–1014. doi:10.1145/ 3604915.3608857

[2] Ethan Bito, Yongli Ren, and Estrid He. 2025. Evaluating Position Bias in Large Language Model Recommendations. arXiv:2508.02020 [cs.IR] https://arxiv.org/ abs/2508.02020

[3] Ethan Bito, Yongli Ren, and Estrid He. 2026. One Pass, Any Order: Position-Invariant Listwise Reranking for LLM-Based Recommendation. In Proceedings of the 49th International ACM SIGIR Conference on Research and Development in Information Retrieval (Australia) (SIGIR ’26). Association for Computing Machinery, New York, NY, USA, 3625–3629. doi:10.1145/3805712.3809952

[4] Wen-Shuo Chao, Zhi Zheng, Hengshu Zhu, and Hao Liu. 2024. Make Large Language Model a Better Ranker. In Findings ofthe Association for Computational Linguistics: EMNLP 2024, Yaser Al-Onaizan, Mohit Bansal, and Yun-Nung Chen (Eds.). Association for Computational Linguistics, Miami, Florida, USA, 918–929. doi:10.18653/v1/2024.findings-emnlp.51

[5] Sunhao Dai, Ninglu Shao, Haiyuan Zhao, Weijie Yu, Zihua Si, Chen Xu, Zhongx iang Sun, Xiao Zhang, and Jun Xu. 2023. Uncovering ChatGPT’s Capabilities in Recommender Systems. In Proceedings of the 17th ACM Conference on Recommender Systems (RecSys ’23). ACM, 1126–1132. doi:10.1145/3604915.3610646

[6] Cynthia Dwork, Ravi Kumar, Moni Naor, and D. Sivakumar. 2001. Rank aggrega tion methods for the Web. In Proceedings ofthe 10th International Conference on World Wide Web (Hong Kong, Hong Kong) (WWW’01). Association for Comput ing Machinery, New York, NY, USA, 613–622. doi:10.1145/371920.372165

[7] Luke Friedman, Sameer Ahuja, David Allen, Zhenning Tan, Hakim Sidahmed, Changbo Long, Jun Xie, Gabriel Schubiner, Ajay Patel, Harsh Lara, Brian Chu, Zexi Chen, and Manoj Tiwari. 2023. Leveraging Large Language Models in Conversational Recommender Systems. arXiv:2305.07961 [cs.IR] https://arxiv. org/abs/2305.07961

[8] Jingtong Gao, Bo Chen, Weiwen Liu, Xiangyang Li, Yichao Wang, Wanyu Wang, Huifeng Guo, Ruiming Tang, and Xiangyu Zhao. 2025. LLM4Rerank: LLM-based Auto-Reranking Framework for Recommendations. arXiv:2406.12433 [cs.IR] https://arxiv.org/abs/2406.12433

[9] Shijie Geng, Shuchang Liu, Zuohui Fu, Yingqiang Ge, and Yongfeng Zhang. 2022. Recommendation as language processing (rlp): A unified pretrain, personalized prompt & predict paradigm (p5). In Proceedings ofthe 16th ACM conference on recommender systems. 299–315.

[10] Jiayuan He, Jianzhong Qi, and Kotagiri Ramamohanarao. 2019. A joint context aware embedding for trip recommendations. In 2019 IEEE 35th international conference on data engineering (ICDE). IEEE, 292–303.

[11] Jiayuan He, Jianzhong Qi, and Kotagiri Ramamohanarao. 2020. Timesan: A time modulated self-attentive network for next point-of-interest recommendation. In 2020 International joint conference on neural networks (IJCNN). IEEE, 1–8.

[12] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. LightGCN: Simplifying and Powering Graph Convolution Network for Recommendation. arXiv:2002.02126 [cs.IR] https://arxiv.org/abs/2002.02126

[13] Yupeng Hou, Junjie Zhang, Zihan Lin, Hongyu Lu, Ruobing Xie, Julian McAuley, and Wayne Xin Zhao. 2024. Large Language Models are Zero-Shot Rankers for Recommender Systems. arXiv:2305.08845 [cs.IR] https://arxiv.org/abs/2305.08845

[14] Cheng-Yu Hsieh, Yung-Sung Chuang, Chun-Liang Li, Zifeng Wang, Long T. Le, Abhishek Kumar, James Glass, Alexander Ratner, Chen-Yu Lee, Ranjay Krishna, and Tomas Pfister. 2024. Found in the Middle: Calibrating Positional Attention Bias Improves Long Context Utilization. arXiv:2406.16008 [cs.CL] https://arxiv. org/abs/2406.16008

[15] Junling Liu, Chao Liu, Peilin Zhou, Renjie Lv, Kang Zhou, and Yan Zhang. 2023. Is ChatGPT a Good 

### 在线资源

- [论文：arXiv 2608.03091](https://arxiv.org/abs/2608.03091)
- [代码：GitHub](https://github.com/ejbito/InvariRank)
- [PDF源文件](/papers/2608.03091.pdf)
