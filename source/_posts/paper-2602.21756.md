---
title: "Offline Reasoning for Efficient Recommendation: LLM-Empowered Persona-Profiled Item Indexing"
date: 2026-02-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2602.21756
arxiv_id: "2602.21756"
---

## 一、简介

Recent advances in large language models (LLMs) ofer new op portunities for recommender systems by capturing the nuanced semantics of user interests and item characteristics through rich semantic understanding and contextual reasoning. In particular, LLMs have been employed as rerankers that reorder candidate items based on inferred user–item relevance. However, these approaches often require expensive online inference-time reasoning, leading to high latency that hampers real-world deployment.

In this work, we introduce Persona4Rec, a recommendation framework that performs ofline reasoning to construct interpretable persona representations of items, enabling lightweight and scalable real-time inference. In the ofline stage, Persona4Rec leverages LLMs to reason over item reviews, inferring diverse user motiva tions that explain why diferent types of users may engage with an item; these inferred motivations are materialized as persona representations, providing multiple, human-interpretable views of each item. Unlike conventional approaches that rely on a single item representation, Persona4Rec learns to align user profiles with the most plausible item-side persona through a dedicated encoder, efectively transforming user–item relevance into user–persona relevance. At the online stage, this persona-profiled item index al lows fast relevance computation without invoking expensive LLM reasoning. Extensive experiments show that Persona4Rec achieves performance comparable to recent LLM-based rerankers while sub stantially reducing inference time. Moreover, qualitative analysis confirms that persona representations not only drive eficient scor ing but also provide intuitive, review-grounded explanations. These results demonstrate that Persona4Rec ofers a practical and inter pretable solution for next-generation recommender systems.1

∗Both authors contributed equally to this research. †Corresponding author 1https://github.com/legenduck/PERSONA4REC

![](images/1a360a67f51867b4513ef099939e7827ed1d5018ba89fa0e8a3eb91a61a98fa1.jpg)  
Figure 1: Comparison between existing LLM-based item rerankers (Upper) and our Persona4Rec (Lower). Persona4Rec shifts LLM reasoning from online inference to ofline persona construction, enabling real-time recommendation via lightweight similarity scoring.

## 二、论文方法

The key idea of Persona4Rec is to shift the costly reasoning process from online (inference) stage to the ofline stage by precomputing review-grounded item personas. Specifically, during ofline stage, Persona4Rec derives multiple personas for each item, where each persona captures a distinct motivation or preference pattern associated with the item. These personas are organized into a personaprofiled item index and serve as the primary units for aligning with user profiles, which summarize user historical interactions, rather than relying on direct alignment with raw item information. During online stage, user profiles are eficiently matched against pre-indexed personas, enabling real-time recommendation without invoking expensive reasoning. Moreover, the selected persona naturally provides a human-interpretable explanation for the recommendation, grounded in evidence from actual user reviews. As illustrated in Figure 2, Persona4Rec consists of two stages:

• Ofline process: Persona4Rec analyzes item information and reviews to generate multiple personas representing diverse user motivations. These personas are then paired with user profiles to produce user–persona alignment signals, which are used to train a lightweight encoder that embeds both into a shared space and constructs a persona-profiled item index for eficient scoring.

• Online process: During inference, Persona4Rec constructs user profiles on-the-fly from recent interaction histories, leveraging the precomputed persona representations. For each candidate item, its personas are scored against the user profile via eficient similarity computation, and relevance score is determined by the best-matching persona, which is used for reranking.

## 三、论文里的图与解释

### 图 1

![Figure 2: Overview of our Persona4Rec framework. The ofline process (Left) constructs item personas and trains a userpersona alignment encoder. The online process (Right) reranks candidates via eficient similarity scoring](/images/papers/2602.21756/335ea814ab1566a9ee7213c6b4352ff4c6c580e7c90f45a2e5be95ebeb77ff63.jpg)

**原图说明：** Figure 2: Overview of our Persona4Rec framework. The ofline process (Left) constructs item personas and trains a userpersona alignment encoder. The online process (Right) reranks candidates via eficient similarity scoring

**图示解释：** 该图对应论文中的“Figure 2: Overview of our Persona4Rec framework. The ofline process (Left) constructs item personas and trains a userpersona alignment encoder. The online process (Right) reranks candidates via eficient similarity scoring”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出离线人物画像构建机制，利用LLM对物品元数据和用户评论进行推理，为每个物品生成多个可解释的人物画像，每个画像代表一种不同的用户动机或偏好模式。
2. 创新点2：设计用户-人物画像对齐框架，通过LLM-as-a-judge范式为每个交互对选择最相关的人物画像，生成监督信号训练轻量级编码器，将用户画像和物品人物画像映射到共享语义空间。
3. 创新点3：构建人物画像索引的物品表示，在线推理时仅需计算用户画像与预计算人物画像的相似度，避免昂贵的实时LLM调用，实现亚毫秒级推理延迟。

## 五、实验数据集选择

- Amazon-Books (Amazon Reviews 2023)
- Yelp (Philadelphia region restaurant and food)

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

We first examine whether Persona4Rec can efectively enhance top-?? recommendation accuracy when used to rerank candidates produced by CF models, to verify that shifting reasoning ofline does not compromise ranking quality.

4.2.1 Overall Performance. Table 4 shows Persona4Rec consistently outperforms CF generators and LLM-based rerankers across datasets. Notably, LLM-based rerankers struggle under real-world data conditions, with some falling behind CF generators due to dataset-specific limitations. In Amazon-Books, extreme rating skew toward 5-stars (Figure 3) undermines EXP3RT; when most items share similar ratings, rating-based reasoning loses discriminative power. On the other hand, ZS-LLM’s generic prompting and TALL Rec’s instruction-tuned approach fail to capture nuanced collaborative patterns. In Yelp, rating skew is less extreme than Amazon-Books but still exhibits significant imbalance (Figure 3). When this unbalanced distribution is combined with sparse metadata (e.g., “WiFi available,” “child-friendly”), it provides insuficient diferentiation for reasoning-based methods.

Table 5: Reranking performance across cold-start and warm-start scenarios on Amazon-Books dataset, with relative improvements (%) over CF baseline, denoted by “-”. (∗: p-value < 0.05)

<table><tr><td rowspan="2">Generator</td><td rowspan="2">Reranker</td><td colspan="2">Warm Users@10</td><td colspan="2">Cold Users@10</td><td colspan="2">Head Items@10</td><td colspan="2">Tail Items@10</td></tr><tr><td>HR</td><td>NDCG</td><td>HR</td><td>NDCG</td><td>HR</td><td>NDCG</td><td>HR</td><td>NDCG</td></tr><tr><td rowspan="6">BPR-MF</td><td>-</td><td>0.0469</td><td>0.0236</td><td>0.1380</td><td>0.0757</td><td>0.1662</td><td>0.0868</td><td>0.0310</td><td>0.0185</td></tr><tr><td>ZS-LLM</td><td>0.0490</td><td>0.0251</td><td>0.1409</td><td>0.0778</td><td>0.1696</td><td>0.0897</td><td>0.0323</td><td>0.0191</td></tr><tr><td>TALLRec</td><td>0.0451</td><td>0.0216</td><td>0.0749</td><td>0.0333</td><td>0.1120</td><td>0.0530</td><td>0.0160</td><td>0.0076</td></tr><tr><td>EXP3RT</td><td>0.0486</td><td>0.0236</td><td>0.1109</td><td>0.0528</td><td>0.1457</td><td>0.0683</td><td>0.0268</td><td>0.0160</td></tr><tr><td>PERSONA4Rec (ours)</td><td>0.0599*</td><td>0.0320*</td><td>0.1432</td><td>0.0789</td><td>0.1707</td><td>0.0904</td><td>0.0360*</td><td>0.0196</td></tr><tr><td>improv. over BPR-MF</td><td>+27.7%</td><td>+35.6%</td><td>+3.8%</td><td>+4.2%</td><td>+2.7%</td><td>+4.1%</td><td>+16.1%</td><td>+5.9%</td></tr><tr><td rowspan="6">LightGCN</td><td>-</td><td>0.0552</td><td>0.0267</td><td>0.1479</td><td>0.0782</td><td>0.1671</td><td>0.0858</td><td>0.0383</td><td>0.0225</td></tr><tr><td>ZS-LLM</td><td>0.0536</td><td>0.0273</td><td>0.1474</td><td>0.0803</td><td>0.1658</td><td>0.0858</td><td>0.0385</td><td>0.0235</td></tr><tr><td>TALLRec</td><td>0.0462</td><td>0.0213</td><td>0.0841</td><td>0.0363</td><td>0.1124</td><td>0.0519</td><td>0.0235</td><td>0.0106</td></tr><tr><td>EXP3RT</td><td>0.0445</td><td>0.0211</td><td>0.1049</td><td>0.0495</td><td>0.1295</td><td>0.0591</td><td>0.0330</td><td>0.0170</td></tr><tr><td>PERSONA4Rec (ours)</td><td>0.0621*</td><td>0.0328*</td><td>0.1545*</td><td>0.0850*</td><td>0.1697*</td><td>0.0905*</td><td>0.0455*</td><td>0.0233</td></tr><tr><td>improv. over LightGCN</td><td>+12.5%</td><td>+22.8%</td><td>+4.5%</td><td>+8.7%</td><td>+1.6%</td><td>+5.5%</td><td>+18.8%</td><td>+3.6%</td></tr></table>

Table 6: Simulating items without reviews on Amazon-Books. Results at @10 with relative improvement over CF baseline.

<table><tr><td>Generator</td><td>Reranker</td><td>HR</td><td>NDCG</td></tr><tr><td rowspan="3">BPR-MF</td><td>-</td><td>0.1000</td><td>0.0531</td></tr><tr><td>Summary Only</td><td> $\underline{0.1043 (+4.3\%)}$ </td><td> $\underline{0.0560 (+5.5\%)}$ </td></tr><tr><td>Full (Ours)</td><td> $\underline{0.1081 (+8.1\%)}$ </td><td> $\underline{0.0585 (+10.2\%)}$ </td></tr><tr><td rowspan="3">LightGCN</td><td>-</td><td>0.1071</td><td>0.0561</td></tr><tr><td>Summary Only</td><td> $\underline{0.1112 (+3.8\%)}$ </td><td> $\underline{0.0591 (+5.3\%)}$ </td></tr><tr><td>Full (Ours)</td><td> $\underline{0.1151 (+7.5\%)}$ </td><td> $\underline{0.0622 (+10.9\%)}$ </td></tr></table>

Persona4Rec overcomes these limitations by extracting personas primarily from review contents rather than focus on metadata or ratings. While LLM rerankers are afected by noisy raw metadata for reasoning, we refine this noisy metadata into structured summaries. This refinement process provides more objective and dense information for constructing personas, even when metadata is sparse. Besides, even though ratings are skewed, personas can capture diverse aspects from review semantics. This allows our model to avoid the loss of discriminative power that hinders rating based reasoning approaches. Beyond this textual refinement, our framework learns to align user interaction histories with these per sonas through contrastive learning, enabling the model to capture implicit behavioral preferences. This alignment process allows the encoder to recognize subtle preference patterns embedded in users’ actual engagement histories. This synergy between semantic understanding and behavioral alignment ensures robust and reliable performance even under challenging data conditions. Even without fine-tuning, the vanilla variant with pre-trained BGE-M3 outperforms LLM baselines, validating the efectiveness of our personabased textual refinement. Fine-tuning adds further gains by learning from interaction patterns through user-persona alignment training.

4.2.2 Cold-/Warm-start Scenario Analysis. We partition test interactions by review count into user/item segments to test robustness under sparsity (warm/head: top 20%, cold/tail: bottom 20%). As shown in Table 5, Persona4Rec exhibits gains across all regimes. Tail items deliver the suitable gains. These items remain sparsely connected within the dataset, causing CF generators to produce unreliable rankings from weak collaborative patterns. In contrast, Persona4Rec infers structured personas from the available reviews—even when reviews are few, they provide richer semantic signals than interaction counts alone. This review-grounded evidence enables robust reranking where CF struggles most.

Warm users show strong relative improvements. Despite start- ing from low baseline performance, warm users achieve substantial relative gains. This suggests that persona-based matching provides significant value when users have extensive histories, as richer context enables alignment with more specialized personas that capture preference nuances invisible to collaborative filtering.

Head items show modest gains. Two factors may contribute to this ceiling. First, abundant interactions enable CF to learn robust patterns, reducing the marginal value of semantic augmentation. Second, popular items often exhibit broader preference diversity than what our current persona generation framework can capture. Although Persona4Rec limits each item to a maximum of seven personas for computational eficiency, highly reviewed items might benefit from a more fine-grained representation.

Cold users show moderate improvements. Cold users exhibit smaller relative improvements as sparse histories limit coherent preference profiling—especially when consuming popular items with generic taste signals. In contrast, warm users’ extensive histories reveal consistent patterns (e.g., recurring themes, quality criteria) enabling precise alignment with specialized personas. This confirms that persona semantics provide value across sparsity levels, but optimal matching requires suficient interaction data.

Table 7: Comparison of inference eficiency between LLM based rerankers and Persona4Rec. Latency for ZS-LLM is measured as end-to-end API latency.

<table><tr><td>Method</td><td>Inference Latency (ms)</td><td>Memory Footprint (GB)</td></tr><tr><td>ZS-LLM</td><td> $5,537 \pm 3,094.13$ </td><td>-</td></tr><tr><td>TALLRec</td><td> $979.17 \pm 13.29$ </td><td>12.57</td></tr><tr><td>EXP3RT</td><td> $77,974.08 \pm 1,229.99$ </td><td>14.96</td></tr><tr><td rowspan="2">PERSONA4Rec</td><td> $0.52 \pm 0.01$  (CPU)</td><td>-</td></tr><tr><td> $0.75 \pm 0.02$  (GPU)</td><td>0.1</td></tr></table>

![](images/5be07f05bbed8f13e75342cd79b445f180fb7e0db3da0ab59e93f048d046abff.jpg)

![](images/67afea5372933cc039f5d7463b6b00c18daa4385fc7f10494d70fc8883491fa5.jpg)  
Figure 4: Comparison of inference scalability with respect to the number of user samples and candidate items.

4.2.3 Robustness to Missing Reviews. A common limitation of reviewbased methods is their inability to handle items lacking reviews, which frequently occurs for newly listed items in real-world plat forms. To evaluate robustness when items have metadata but no reviews yet, we simulate this by using the same trained encoder but indexing items with their summary $e _ { i } = E _ { \theta } { \bigl ( } s _ { i } { \bigr ) }$ instead of personas (Summary Only). As shown in Table 6, this variant still outper forms the CF baseline across all settings, demonstrating that our framework can efectively serve cold-start items before reviews accumulate, as the encoder has already learned summary seman tics through user profiles during training. When reviews become available, the Full model yields additional gains, confirming the complementary value of review-grounded persona reasoning.

Overall, Persona4Rec demonstrates robust improvements across all data —including complete cold-start scenarios where no reviews are available—confirming our method efectively complements CFbased candidate generation under diverse conditions.

## 八、总结

This work introduced Persona4Rec, a novel recommendation framework that shifts online LLM reasoning to the ofline by constructing diverse review-grounded item personas. By reframing recommen dation as a user-persona alignment task trained on LLM-derived supervision, it enables real-time inference with lightweight encoder scoring while naturally providing interpretable explanations. Exten sive experiments show that Persona4Rec consistently outperforms state-of-the-art LLM-based rerankers, achieving robust gains for cold users and tail items while reducing inference latency by orders of magnitude. Overall, Persona4Rec ofers a practical and scal able solution bridging eficiency, accuracy, and interpretability, and paves the way for extending persona-based alignment to richer user feedback and hybrid reasoning framework that combines ofline knowledge construction with adaptive online refinement.

## References

[1] Mofetoluwa Adeyemi, Akintunde Oladipo, Ronak Pradeep, and Jimmy Lin. 2024. Zero-Shot Cross-Lingual Reranking with Large Language Models for Low Resource Languages. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers). 650–656.

[2] Keqin Bao, Jizhi Zhang, Yang Zhang, Wenjie Wang, Fuli Feng, and Xiangnan He. 2023. Tallrec: An efective and eficient tuning framework to align large language model with recommendation. In Proceedings of the 17th ACM conference on recommender systems. 1007–1014.

[3] Maciej Besta, Nils Blach, Ales Kubicek, Robert Gerstenberger, Michal Podstawski, Lukas Gianinazzi, Joanna Gajda, Tomasz Lehmann, Hubert Niewiadomski, Piotr Nyczyk, et al. 2024. Graph of thoughts: Solving elaborate problems with large language models. In Proceedings of the AAAI conference on artificial intelligence, Vol. 38. 17682–17690.

[4] Hongru Cai, Yongqi Li, Wenjie Wang, Fengbin Zhu, Xiaoyu Shen, Wenjie Li, and Tat-Seng Chua. 2025. Large language models empowered personalized web agents. In Proceedings of the ACM on Web Conference 2025. 198–215.

[5] Jianlv Chen, Shitao Xiao, Peitian Zhang, Kun Luo, Defu Lian, and Zheng Liu. 2024. BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation. arXiv:2402.03216 [cs.CL] https://arxiv.org/abs/2402.03216

[6] Ting Chen, Wei-Li Han, Hai-Dong Wang, Yi-Xun Zhou, Bin Xu, and Bin-Yu Zang. 2007. Content recommendation system based on private dynamic user profile. In 2007 International conference on machine learning and cybernetics, Vol. 4. IEEE, 2112–2118.

[7] Jingtong Gao, Bo Chen, Xiangyu Zhao, Weiwen Liu, Xiangyang Li, Yichao Wang, Wanyu Wang, Huifeng Guo, and Ruiming Tang. 2025. Llm4rerank: Llm-based auto-reranking framework for recommendations. In Proceedings of the ACM on Web Conference 2025. 228–239.

[8] Shijie Geng, Shuchang Liu, Zuohui Fu, Yingqiang Ge, and Yongfeng Zhang. 2022. Recommendation as language processing (rlp): A unified pretrain, personalized prompt & predict paradigm (p5). In Proceedings of the 16th ACM conference on recommender systems. 299–315.

[9] Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. Lightgcn: Simplifying and powering graph convolution network for recommendation. In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval. 639–648.

[10] Xiangnan He, Lizi Liao, Hanwang Zhang, Liqiang Nie, Xia Hu, and Tat-Seng Chua. 2017. Neural collaborative filtering. In Proceedings of the 26th international conference on world wide web. 173–182.

[11] Ryang Heo, Yongsik Seo, Junseong Lee, and Dongha Lee. 2025. Can Large Language Models be Efective Online Opinion Miners? arXiv preprint arXiv:2505.15695 (2025).

[12] Yupeng Hou, Jiacheng Li, Zhankui He, An Yan, Xiusi Chen, and Julian McAuley. 2024. Bridging language and items for retrieval and recommendation. arXiv preprint arXiv:2403.03952 (2024).

[13] Yupeng Hou, Junjie Zhang, Zihan Lin, Hongyu Lu, Ruobing Xie, Julian McAuley, and Wayne Xin Zhao. 2024. Large language models are zero-shot rankers for recommender systems. In European Conference on Information Retrieval. Springer, 364–381.

[14] Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen, et al. 2022. Lora: Low-rank adaptation of large language models. ICLR 1, 2 (2022), 3.

[15] Mathias Jackermeier, Jiaoyan Chen, and Ian Horrocks. 2024. Dual box embeddings for the description logic EL++. In Proceedings of the ACM Web Conference 2024.

2250–2258.

[16] Jieyong Kim, Hyunseo Kim, Hyunjin Cho, SeongKu Kang, Buru Chang, Jinyoung Yeo, and Dongha Lee. 2025. driven Personalized Preference Reasoning with Large Language Models for Recommendation. In Proceedings of the 48th International ACM SIGIR Conference on Research and Development in Information Retrieval. 1697–1706.

[17] Minjin Kim, Minju Kim, Hana K

### 在线资源

- [论文：arXiv 2602.21756](https://arxiv.org/abs/2602.21756)
- [代码：GitHub](https://github.com/legenduck/PERSONA4REC)
- [PDF源文件](/papers/2602.21756.pdf)
