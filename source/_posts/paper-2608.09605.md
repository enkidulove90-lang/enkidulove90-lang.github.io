---
title: "TSPORec: Token Selection via Preference Optimization for LLM-Based Sequential Recommendation"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.09605
arxiv_id: "2608.09605"
---

## 一、简介

Large Language Models (LLMs) have emerged as powerful tools for improving recommendation systems. The effectiveness of LLMs arises from their ability to harness rich textual information and their capacity to model heterogeneous user preferences based on users’ interaction history. However, due to the large-scale and deep architectures, LLM-based sequential recommendation approaches generally incur high inference costs, resulting in a low return on investment. To mitigate this cost, many ex isting approaches resort to using only the first few tokens of item descriptions, which inadvertently discards valuable information contained in the full text, thereby leading to suboptimal recommendation performance. To address this limitation, we propose a novel Token Selec tion approach for Preference Optimization in LLM-based sequential Recommendation, i.e., TSPORec, which accurately pinpoints informative tokens throughout the entire textual content to improve recommendation performance. Specifically, we design a three-stage pipeline to select informative tokens and introduce a novel proxy reward to facilitate the implementation. TSPORec not only enhances recommendation performance but also improves computational efficiency. Extensive experiments across two models and datasets demonstrate the su perb performance (up to 31.25%) and efficiency (up to 63.4%) of our approach compared with six baseline approaches. Code is avaliable at https://github.com/WNQzhu/TSPORec.git.

## 二、论文方法

In this section, we first formulate the problem to address in this paper. Then, we detail our approach, i.e., TSPORec, including the new token selection pipeline and the novel proxy reward method.

## 三、论文里的图与解释

### 图 1

![Figure 1: Overview of TSPORec’s Three-Stage Training Pipeline: (1) LLM Pretraining, (2) Token Selection Policy Learning, (3) Token Selection and Retraining.](/images/papers/2608.09605/3c3c933526d8dd15434702eed8fc316d19daf924b0aa22ddf5fac45b602d5e74.jpg)

**原图说明：** Figure 1: Overview of TSPORec’s Three-Stage Training Pipeline: (1) LLM Pretraining, (2) Token Selection Policy Learning, (3) Token Selection and Retraining.

**图示解释：** 该图对应论文中的“Figure 1: Overview of TSPORec’s Three-Stage Training Pipeline: (1) LLM Pretraining, (2) Token Selection Policy Learning, (3) Token Selection and Retraining.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Figure 6: Comparison of token distributions selected by first-k and TSPORec.](/images/papers/2608.09605/42b9f36735a4a51ab181f7289bcf226e58d66c88e6c379b79c7379a6a2346b85.jpg)

**原图说明：** Figure 6: Comparison of token distributions selected by first-k and TSPORec.

**图示解释：** 该图对应论文中的“Figure 6: Comparison of token distributions selected by first-k and TSPORec.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 提出三阶段Token选择流水线：预训练LLM推荐模型、基于代理奖励学习Token选择策略、利用选定Token重训练模型，实现了从全文描述中自动识别信息性Token的目标，且在不同LLM和数据集上展现强泛化能力。
2. 设计了一种新颖的代理奖励函数，通过对比两次独立采样的Token子序列所构建的用户嵌入与完整物品嵌入之间的交叉熵损失，引导策略学习区分信息性Token与非信息性Token，解决了Token子集评估的指数级复杂度问题。
3. 采用双向评分机制计算Token重要性：同时利用标准注意力机制编码语义信息和预训练物品嵌入提供协同过滤信号，使Token选择能够联合捕获丰富语义与序列协同模式，优于单向的top-k logit选择策略。
4. 引入chunk级别的Token选择粒度控制，通过可调节的chunk大小在Token级和粗粒度选择之间灵活权衡，实验发现更细粒度的选择单元能带来更有效的Token选择效果。

## 五、实验数据集选择

We conduct a comprehensive evaluation of TSPORec against four state-of-the-art baselines: (1) traditional ID-based sequential recommendation models, such as SASRec (Kang and McAuley, 2018) and HSTU (Zhai et al., 2024); (2) semantic initialization methods that leverage large language model (LLM)-derived embeddings to initialize item ID representations, exemplified by LLMinit (Harte et al., 2023); and (3) hierarchical LLM-based frameworks, specifically HLLM (Chen et al., 2024). In addition, to study the impact of token selection, we adapt these baselines with different token selection policies, resulting in six baseline variants for comparison. We evaluate our approach on two publicly available datasets: the Amazon Book Reviews dataset (McAuley et al., 2015) and the Pixel dataset (Cheng et al., 2023). For backbone LLMs, we employ Qwen3-Embedding-0.6B (Zhang et al., 2025b) and TinyLlama-1.1B (Zhang et al., 2024b). Performance is evaluated using Recall@K (R@K) and NDCG@K (N@K). Additional details on the experimental setup are given in Appendix A.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

Overall Performance As shown in Table 1, TSPORec significantly outperforms all baseline approaches by a substantial margin. In this setting, input sequences are truncated to 64 tokens, and the Qwen3-Embedding-0.6B model serves as the frozen LLM backbone. For TSPORec, the chunk size is set to 8. On the Amazon Books dataset, TSPORec improves upon SASRec by up to 29.29% in Recall@K and 31.25% in NDCG@K, yielding an average gain of 29.43% across metrics. On the Pixel dataset, it achieves improvements of up to 19.63% in Recall@K and 18.24% in NDCG@K, with an average increase of 16.79%.

The Importance of Tokens in LLM-based Recommendation Given the significant advances achieved by LLM-based sequential recommendation methods, we investigate the impact of different types of input tokens. Specifically, we compare random tokens, top-k logit tokens, the first k tokens, and TSPORec. For random tokens, we randomly select k tokens from the item text. For top-k logit tokens, we select the k tokens with the highest logits. The first k tokens is the default strategy employed by many existing methods. In contrast, TSPORec selects k tokens using a learned policy.

As shown in Table 1, TSPORec achieves the most significant performance gain by leveraging the learned token selection policy, substantially outperforming existing token selection strategies. On the Amazon Books dataset, randomly selecting tokens reduces the performance improvement of HLLM from 24.40% to just 2.14%, highlighting the critical role of input token selection in LLMbased recommendation.

These results demonstrate that the choice of input tokens has a profound impact on model effectiveness—a factor largely overlooked by prior approaches. Surprisingly, the top-k logit tokens do not outperform the simple first-k tokens baseline, suggesting that more principled token selection mechanisms are needed. This limitation may stem from the unidirectional nature of standard LLM attention, which prevents hidden states from effectively capturing meaningful collaborative signals across the sequence. In contrast, as illustrated in Eq. (5), TSPORec leverages a bidirectional scoring mechanism. The importance score of each token is learned from both (i) the standard attention mechanism, which encodes semantic meaning, and (ii) the pretrained item embedding $\mathbf { h } _ { k + 1 }$ , which provides a collaborative filtering signal. This dual-source design enables TSPORec to jointly capture rich semantic information and sequential collaborative patterns, thereby facilitating the identification of the most informative tokens and ultimately improving model performance.

The Impact of Token Sequence Length in LLMbased Recommendation In this section, we further investigate how the length of input tokens impacts recommendation performance. To this end, we conduct extensive experiments with varying input token lengths, as shown in Figure 2. We denote each configuration as Method k, where k represents the number of input tokens used. For instance, HLLM-128 indicates the use of the first 128 tokens from the input sequence, while TSPORec-64 denotes the selection of 64 tokens according to the learned token selection policy.

As illustrated in Figure 2, on the Amazon Books dataset, increasing the token length leads to performance improvements for both HLLM and TSPORec, suggesting that longer input sequences may contain additional informative tokens that ben-

<table><tr><td> $Token_S$ </td><td> $I_t$  (ms)</td><td> $U_t$  (ms)</td><td>Total (ms)</td></tr><tr><td>64</td><td>299</td><td>27</td><td>326</td></tr><tr><td>128</td><td>509</td><td>27</td><td>536</td></tr><tr><td>256</td><td>817</td><td>26</td><td>843</td></tr></table>

$$
I _ {t}
$$

$$
U _ {t}
$$

efit recommendation quality. In contrast, on the Pixel dataset, while moderate increases in token length initially enhance HLLM’s performance, further lengthening the input sequence eventually degrades performance. This indicates that not all tokens contribute positively to recommendations, and including irrelevant or noisy tokens can be detrimental. This phenomenon further underscores the necessity of effective token selection to improve recommendation performance. Moreover, on both the Amazon Books and Pixel datasets, TSPORec with only 64 selected tokens achieves performance on par with or superior to the corresponding HLLM variants using 256 tokens. These results demonstrate that TSPORec not only enhances recommendation accuracy but also improves computational efficiency by enabling effective performance with significantly fewer tokens.

The Efficiency of TSPORec To evaluate the impact on inference efficiency of TSPORec, we analyze the computational cost across varying input sequence lengths. By selecting informative tokens, TSPORec effectively reduces the required input length without sacrificing performance, thereby lowering overall computational overhead.

We measure the inference time of LLM on an NVIDIA H100 GPU using the Amazon Books dataset, with a batch size of 32 and an item sequence length of 10. The results are summarized in Table 2. We observe that the item LLM dominates the inference time, and its computational share grows significantly as the input token sequence length increases. Since TSPORec matches the performance of HLLM using only 64 tokens with HLLM using 256 tokens, it reduces inference cost by 63.4% in scenarios where item embeddings are precomputed offline, and by 61.3% when both the item and user LLMs are served online.

The Generalization capability of TSPORec To evaluate the generalization ability of TSPORec, we conduct experiments using a different LLM backbone—TinyLlama-1.1B, as well as a different downstream SR model, LLMinit (Harte et al.,

![](images/598364d9e6706348d2bb39460c6e110247b9cedc0a9951f2a9e8d80bad649a7d.jpg)  
(a) Amazon Book, Recall@5

![](images/d6836a3bcf276e1f5d6f7d7373af289ec6194630d1df0856f11aa520d238d542.jpg)  
(b) Amazon Book, NDCG@5

![](images/fcca742d105ffb6065808186ed1c5981ebc39047eb426d7176a437bd1f9944a0.jpg)

![](images/5c1da27f09a20aefcfa63ea8b37c43dd00b0c759c404973533f219ceeb44e54d.jpg)  
(c) Pixel, Recall@5  
(d) Pixel, NDCG@5

![](images/72c3fb3fe39e91ed8b71012a6691de233f407375d16da163f45982b91fd0bd55.jpg)

![](images/578a2984d46a63cea22b5078665184b7b17fe62bc6d52221871e6ac90798bd28.jpg)  
(e) Amazon Book, Recall@10 (f) Amazon Book, NDCG@10

![](images/0f3f34dd825e8226c05b3be3a1cacf0e1c5bb4c0396a18bb013d9bcbd39091c5.jpg)  
(g) Pixel, Recall@10

![](images/c9da2aecd92d286fd2c87f80d2a3a591d798bba0fc99e30df9b14c7bd0ac0799.jpg)  
(h) Pixel, NDCG@10

Figure 2: Performance of HLLM and TSPORec on Amazon Books and Pixel with different token sequence lengths, using Qwen3-Embedding-0.6B as the backbone model.

<table><tr><td>Method</td><td>R@5</td><td>R@10</td><td>N@5</td><td>N@10</td><td>Impr.</td></tr><tr><td>HLLM</td><td>3.99</td><td>6.07</td><td>2.66</td><td>3.33</td><td>+0.0%</td></tr><tr><td>TSPORec</td><td>4.16</td><td>6.30</td><td>2.78</td><td>3.46</td><td>+4.12%</td></tr></table>

Table 3: Performance comparison of HLLM and TSPORec on the Amazon Books dataset, using TinyLlama-1.1B as the backbone model, with text sequences truncated to 64 tokens.

2023). We compare TSPORec against the HLLM variant with the same LLM backbone, and the results are presented in Table 3. TSPORec consistently outperforms HLLM across all Recall and NDCG metrics, achieving an average improvement of 4.12%. Furthermore, as shown in Table 4, when TSPORec-selected tokens are used to initialize LLMinit, the model performance improves by 3.76%, demonstrating that the selected tokens carry informative signals for recommendation. These results confirm that TSPORec not only enhances downstream performance but also exhibits strong generalization across different LLM architectures and recommendation models.

## 八、总结

In this paper, we propose a novel Token Selection approach tailored for LLM-driven Sequential Recommendation systems, i.e., TSPORec. We develop a three-stage workflow. First, we pre-train the foundational LLM-based sequential recommendation model to establish a robust baseline. Second, we train a dedicated policy to identify informative tokens; additionally, a proxy reward function is designed to facilitate chunk-oriented token selection, addressing the challenges of granularity in token identification. Finally, leveraging the identified tokens, we retrain the pre-trained baseline model to optimize its recommendation performance. Comprehensive experimental results demonstrate the effectiveness (up to 31.25%) and efficiency (up to 63.4%) of the proposed method.

## References

Baichuan. 2023. Baichuan 2: Open large-scale language models. arXiv preprint arXiv: 2309.10305.

Junyi Chen, Lu Chi, Bingyue Peng, and Zehuan Yuan. 2024. Hllm: Enhancing sequential recommendations via hierarchical large language models for item and user modeling. arXiv preprint arXiv:2409.12740.

Junyi Chen, Lu Chi, Siliang Xu, Shiwei Ran, Bingyue Peng, and Zehuan Yuan. 2025. Hllm-creator: Hierarchical llm-based personalized creative generation. arXiv preprint arXiv:2508.18118.

Chen Cheng, Haiqin Yang, Michael R. Lyu, and Irwin King. 2013. Where you like to go next: Successive point-of-interest recommendation. In IJCAI, pages 2605–2611.

Yu Cheng, Yunzhu Pan, Jiaqi Zhang, Yongxin Ni, Aixin Sun, and Fajie Yuan. 2023. An image dataset for benchmarking recommender systems with raw pixels. arXiv preprint arXiv:2309.06789.

Mingkai Deng, Jianyu Wang, Cheng-Ping Hsieh, Yihan Wang, Han Guo, Tianmin Shu, Meng Song, Eric P Xing, and Zhiting Hu. 2022. Rlprompt: Optimizing discrete text prompts with reinforcement learning. arXiv preprint arXiv:2205.12548.

Kawin Ethayarajh, Winnie Xu, Niklas Muennighoff, Dan Jurafsky, and Douwe Kiela. 2024. Kto: Model alignment as prospect theoretic optimization. arXiv preprint arXiv:2402.01306.

Mohammad Gheshlaghi Azar, Zhaohan Daniel Guo, Bilal Piot, Remi Munos, Mark Rowland, Michal Valko, and Daniele Calandriello. 2024. A general theoretical paradigm to understand learning from human preferences. In AISTATS.

Chi Han, Qifan Wang, Hao Peng, Wenhan Xiong, Yu Chen, Heng Ji, and Sinong Wang. 2024. Lminfinite: Zero-shot extreme length generalization for large language models. In Proceedings ofthe 2024 Conference of the North American Chapter of the Associationfor Computational Linguistics: Human

Language Technologies (Volume 1: Long Papers), pages 3991–4008.

Jesse Harte, Wouter Zorgdrager, Panos Louridas, Asterios Katsifodimos, D. Jannach, and Marios Fragkoulis. 2023. Leveraging large language models for sequential recommendation. Proceedings ofthe 17th ACM Conference on Recommender Systems.

Balazs Hidasi, Alexandros Karatzoglou, Linas Baltrunas, and Domonkos Tikk. 2015. Session-based recommendations with recurrent neural networks. arXiv preprint arXiv:1511.06939.

Jiwoo Hong, Noah Lee, and James Thorne. 2024. ORPO: Monolithic preference optimization without reference model. In EMNLP.

Guoqing Hu, An Zhang, Shuo Liu, Zhibo Cai, Xun Yang, and Xiang Wang. 2025. Alphafuse: Learn id embeddings for sequential recommendation in null space of language embeddings. arXiv preprint arXiv:2504.19218.

Wang-Cheng Kang and Julian J. McAuley. 2018. Selfattentive sequential recommendation. In ICDM, pages 197–206.

Sein Kim, Hongseok Kang, Seungyoon Choi, Donghyun Kim, Minchul Yang, and Chanyoung Park. 2024. Large language models meet collaborative filtering: An efficient all-round llm-based recommender system. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining, KDD ’24, page 1395–1406, New York, NY, USA. Association for Computing Machinery.

Brian Lester, Rami Al-Rfou, and Noah Constant. 2021. The power of scale for parameter-efficient prompt tuning. arXiv preprint arXiv:2104.08691.

Jiacheng Li, Yujie Wang, and Julian McAuley. 2020. Time interval aware self-attention for sequential recommendation. In WSDM, pages 322–330.

Xiang Lisa Li and Percy Liang. 2021. Prefix-tuning: Optimizing continuous prompts for generation. arXiv preprint arXiv:2101.00190.

Jiayi Liao, Sihang Li, Zhengyi Yang, Jiancan Wu, Yancheng Yuan, Xiang Wang, and Xiangnan He. 2024. Llara: Large language-recommendation assistant. In Proceedings ofthe 47th International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR ’24, page 1785–1795, New York, NY, USA. Association for Computing Machinery.

Qidong Liu, Xian Wu, Wanyu Wang, Yejing Wang, Yuanshao Zhu, Xiangyu Zhao, Feng Tian, and Yefeng Zheng. 2024a. Large language model empowered embedding generator for sequential recommendation. 

### 在线资源

- [论文：arXiv 2608.09605](https://arxiv.org/abs/2608.09605)
- [代码：GitHub](https://github.com/WNQzhu/TSPORec.git)
- [PDF源文件](/papers/2608.09605.pdf)
