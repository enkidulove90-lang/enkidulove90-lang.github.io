---
title: "Efficient Cold-Start Recommendation via BPE Token-Level Embedding Initialization with LLM"
date: 2025-09-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2509.13179
arxiv_id: "2509.13179"
---

## 一、简介

提出一种利用字节对编码（BPE）和预训练大语言模型（LLM）进行子词级嵌入初始化的冷启动推荐方法。该方法通过将文本元数据分解为BPE子词令牌，并聚合其LLM嵌入作为冷启动实体（新用户/物品）的稠密语义先验，在无需任何交互历史的情况下即可实现有效的零样本推荐。实验证明，该方法在Recall@k和NDCG@k指标上显著优于基于句子级嵌入的基线方法，尤其在多语言和稀疏输入场景下表现突出，且计算效率高，易于集成到现有推荐系统中。

## 二、论文方法

采用BPE分词器将文本元数据（如标题、描述）分解为子词令牌序列，然后使用预训练且冻结的LLM（如DistilBERT）为每个令牌提取上下文嵌入，最后通过平均池化或注意力加权池化聚合所有令牌嵌入，得到用户或物品的最终表示向量。该向量直接用于与现有协同过滤模型中的实体嵌入进行点积计算推荐分数，并使用BPR损失进行优化。

## 三、论文里的图与解释

### 图 1

![Table 1: Performance Comparison Across Methods on Retrieval Metrics](/images/papers/2509.13179/p3_caption_1.png)

**原图说明：** Table 1: Performance Comparison Across Methods on Retrieval Metrics

**图示解释：** 该图对应论文中的“Table 1: Performance Comparison Across Methods on Retrieval Metrics”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Figure 1: Cold-Start Recommendations](/images/papers/2509.13179/p3_caption_2.png)

**原图说明：** Figure 1: Cold-Start Recommendations

**图示解释：** 该图对应论文中的“Figure 1: Cold-Start Recommendations”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Figure 2: t-SNE projection of Cold-start Items](/images/papers/2509.13179/p4_caption_3.png)

**原图说明：** Figure 2: t-SNE projection of Cold-start Items

**图示解释：** 该图对应论文中的“Figure 2: t-SNE projection of Cold-start Items”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出BPE令牌级嵌入初始化策略，利用子词分解捕获细粒度语义，克服了传统句子级嵌入丢失关键子词信息的缺陷。
2. 创新点2：设计了一种与模型架构无关的轻量级方法，通过冻结LLM编码器进行一次性嵌入计算，实现了低延迟、可扩展的冷启动推荐。
3. 创新点3：在多种稀疏度（10%、30%、50%）和跨领域（电影、书籍）的严格冷启动设定下，验证了该方法相比图嵌入、元学习等基线方法的鲁棒性和泛化能力。

## 五、实验数据集选择

In order to comprehensively test our strategy, we experiment on two benchmark datasets: MovieLens 1M and Amazon Books, that are commonly used in the research on recommender systems. To model the cold-start objective, we exclude the sets of users and items that have interacted before, and generate evaluation sets of users and items which have never been seen before[15].

Along with collaborative filtering and sentence-based embedding baselines, it is important to include more formal cold-start baselines. Comparative baselines should be provided, e.g., with models based on graph embedding (e.g., GraphSAGE, LightGCN) or meta-learning (e.g., MeLU, MAML-based cold-start recommenders) or using attribute expansion. Their addition would enable us to evaluate the robustness of BPE-LLM embeddings at various levels of sparsity and a heterogeneous metadata structure[16]. As an example, graph-based models utilize the topology of the useritem interaction, whereas meta-learning methods can rapidly learn to represent previously unseen users/items with few examples. Attribute-expansion techniques exploit additional attributes, e.g., demographics or item attributes, to circumvent sparsity [17].

The metadata includes title and genre of the movies when Textual metadata is used in MovieLens and in Amazon products it includes titles and category[18]. Any text is preprocessed (by lowercase normalization, removing punctuation marks, and Byte Pair Encoding (BPE) in a 30,000-token vocabulary). Pre-trained DistilBERT-base is performed on the extraction of embeddings, and unless specified, attentionweighted pooling over the embeddings is employed[19].

The following are the models that we compare:

1.Random Initialization- normal matrix factorization lacking metadata.

2.Sentence Embedding - metadata encoded through distilbertsentence-vector mean-pooling.

3.BPE + LLM (Ours) -aggregation of token level embeddings at a fine-grained level.

All models are written in PyTorch and Adam is used as the optimization with BPR loss during 50 epochs. Our training and evaluation are done using 90/10 and we use cold start on the test data.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

To give a more complete analysis, the findings are generalized to cover other cold-start baselines, i.e., graph-embedding methods, meta-learning systems, and attribute-expansion algorithms[20]. Our BPE-LLM approach is compared with theirs in Table 1 on the standard metrics Recall@10, NDCG@10, and Hit Rate@10. The findings indicated that though graph-embedding and attribute-based solutions have focused on intermediate levels of sparsity negatively in terms of performance, they decline sharply when beyond sparsity levels of 30-40 percent. In sharp comparison, the proposed BPE-LLM initialization shows a stable performance under various regimes of sparsity (10%, 30%, 50% observed interactions), thus its robustness in extreme cold-starts. This tiered analysis furnishes the empirical results that subwordlevel initialization presents better generalization performance than structure-aware and an attribute-based baseline[21].

Table 1: Performance Comparison Across Methods on Retrieval Metrics

<table><tr><td>Method</td><td>Recall@10</td><td>NDCG@10</td><td>Hit Rate@10</td></tr><tr><td>Random Init</td><td>0.41</td><td>0.32</td><td>0.45</td></tr><tr><td>Sentence Embedding</td><td>0.56</td><td>0.48</td><td>0.59</td></tr><tr><td>BPE + LLM (Ours)</td><td>0.68</td><td>0.62</td><td>0.71</td></tr></table>

As it is indicated in the table, we greatly outperform all the baselines, especially in terms of Recall and NDCG. This proves the usefulness of subword level embeddings in relation to acquisition of semantically subtle characteristics that facilitates generalization when conditions transcend to zeroshot environments[22].

## 八、总结

The proposed study presented an effective and innovative approach to cold-start recommendation based on the initialization of Byte-Pair Encoding (BPE) token-level embedding with the help of large language models (LLMs). The approach is particularly effective in filling the gap that the traditional user-item collaborative filtering approach has in sparse user-item interaction data since it introduces substantial contextualization through the transformer-based approach to subword tokens and their combinations. The approach showed impressive results when tested in a coldstart environment on heterogeneous tasks like books, movies, and games. Empirical evidence proved the higher performance of BPE-LLM in the top-N recommendation task as Recall@10 and NDCG@10 in comparison with sentencelevel and randomly initialized baselines. In addition to that, t-SNE visualization demonstrated semantic clustering, confirming the fidelity and generalizability of the learned embedding space. Importantly, the model is efficient to scale, with embedding inference taking only forward passes of a frozen LLM encoder, which makes it suitable to deploy at scale in modern recommender systems.

## References

[1] Lin X, Cheng Z, Yun L, et al. Enhanced Recommendation Combining Collaborative Filtering and Large Language Models[J]. arXiv preprint arXiv:2412.18713, 2024.

[2] Niu, Tianyue, et al. "Decoding student cognitive abilities: a comparative study of explainable AI algorithms in educational data mining." Scientific Reports 15.1 (2025): 26862.

[3] Zheng Z, Liu K, Zhu X. Machine Learning-Based Prediction of Metal-Organic Framework Materials: A Comparative Analysis of Multiple Models[J]. arXiv preprint arXiv:2507.04493, 2025.

[4] Leong H, Gao Y, Ji S, et al. Efficient fine-tuning of large language models for automated medical documentation[C]//2024 4th International Conference on Digital Society and Intelligent Systems (DSInS). IEEE, 2024: 204-209.

[5] Yuan T, Zhang X, Chen X. Machine Learning based Enterprise Financial Audit Framework and High Risk Identification[J]. arXiv preprint arXiv:2507.06266, 2025.

[6] Li, K., Liu, L., Chen, J., Yu, D., Zhou, X., Li, M., ... & Li, Z. (2024, November). Research on reinforcement learning based warehouse robot navigation algorithm in complex warehouse layout. In 2024 6th International Conference on Artificial Intelligence and Computer Applications (ICAICA) (pp. 296-301). IEEE.

[7] Yu, D., Liu, L., Wu, S., Li, K., Wang, C., Xie, J., ... & Ji, R. (2025, March). Machine learning optimizes the efficiency of picking and packing in automated warehouse robot systems. In 2025 IEEE International Conference on Electronics, Energy Systems and Power Engineering (EESPE) (pp. 1325-1332). IEEE.

[8] Li J, Zhou Y. Bideeplab: An improved lightweight multi-scale feature fusion deeplab algorithm for facial recognition on mobile devices[J]. Computer Simulation in Application, 2025, 3(1): 57-65.

[9] Yang, Zhongheng, et al. "RLHF Fine-Tuning of LLMs for Alignment with Implicit User Feedback in Conversational Recommenders." arXiv preprint arXiv:2508.05289 (2025).

[10] Zhu R, Wang Y, Jiang T, et al. Self-Improving Model Steering[J]. arXiv preprint arXiv:2507.08967, 2025.

[11] Lyu, Haotian, et al. "Self-Supervised User Embedding Alignment for Cross-Domain Recommendations via Multi-LLM Co-Training." Authorea Preprints (2025).

[12] Zhao Y, Lyu H, Peng Y, et al. Research on Low-Latency Inference and Training Efficiency Optimization for Graph Neural Network and Large Language Model-Based Recommendation Systems[J]. arXiv preprint arXiv:2507.01035, 2025.

[13] Chen, Y., Du, H., & Zhou, Y. (2025). Lightweight Network-Based Semantic Segmentation for UAVs and Its RISC-V Implementation. Preprints.https://doi.org/10.20944/preprints202508.1108.v1

[14] Xiang, A., Qi, Z., Wang, H., Yang, Q., & Ma, D. (2024, August). A multimodal fusion network for student emotion recognition based on transformer and tensor product. In 2024 IEEE 2nd International Conference on Sensors, Electronics and Computer Engineering (ICSECE) (pp. 1-4). IEEE.

[15] Ding Y, Wu Y, Ding Z. An automatic patent literature retrieval system based on LLM-RAG[J]. arXiv preprint arXiv:2508.14064, 2025.

[16] Ning Z, Zeng H, Tian Z. Research on data-driven energy efficiency optimisation algorithm for air compressors[C]//Third International Conference on Advanced Materials and Equipment Manufacturing (AMEM 2024). SPIE, 2025, 13691: 1068-1075.

[17] Jiang T, Wang Z, Liang J, et al. Robustkv: Defending large language models against jailbreak attacks via kv eviction[J]. arXiv preprint arXiv:2410.19937, 2024.

[18] Ou, Y. "Dynamic Allocation Mechanism of Cloud Computing Resources Driven by Neural Network." Frontiers in Computing and Intelligent Systems (2023).

[19] Wang J, Zhang Z, He Y, et al. Enhancing Code LLMs with Reinforcement Learning in Code Generation[J]. arXiv preprint arXiv:2412.20367, 2024.

[20] Wang, Jingru, Wen Ding, and Xiaotong Zhu. "Financial analysis: Intelligent financial data analysis system based on llm-rag." arXiv preprint arXiv:2504.06279 (2025).

[21] Li Y, Yao Y, Lin J, et al. A Deep Learning Algorithm Based on CNN-LSTM Framework for Predic

### 在线资源

- [论文：arXiv 2509.13179](https://arxiv.org/abs/2509.13179)
- [PDF源文件](/papers/2509.13179.pdf)
