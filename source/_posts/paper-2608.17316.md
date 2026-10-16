---
title: "Empowering Compact LLMs with Fusion of Layer-wise Exits for Recommendation"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.17316
arxiv_id: "2608.17316"
---

## 一、简介

论文提出FLEXRec，一种基于判别式LLM推荐范式的逐层出口融合框架，旨在解决紧凑LLM在序列推荐中表达能力不足的问题。FLEXRec在LLM每一层后插入预测头（出口），将各层用户偏好嵌入生成的评分分布进行融合，以补偿小模型参数容量的限制。同时设计自适应连续路由器（AC-Router），根据用户序列复杂度动态选择激活的出口数量与身份，并引入target-k hinge loss等联合优化目标控制路由稀疏性。在三个真实数据集上，使用Qwen 3 1.7B和Llama 3.2 3B紧凑骨干，FLEXRec在紧凑骨干方法中达到最优精度，且推理延迟仅比E4SRec增加不到1ms。

## 二、论文方法

In this section, we present the design details of our proposed framework FLEXRec.

## 三、论文里的图与解释

### 图 1

![Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.](/images/papers/2608.17316/figure_001_Toys-Qwen_boxplot.png)

**原图说明：** Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.

**图示解释：** 该图对应论文中的“Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.](/images/papers/2608.17316/figure_002_Toys-Llama_boxplot.png)

**原图说明：** Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.

**图示解释：** 该图对应论文中的“Performance distribution (NDCG@20) of all independent exits across datasets and backbones. The red dashed line, with its exact magnitude marked in bold red on the $x$-axis, denotes the performance of FLEXRec.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Overview of the FLEXRec framework and its three-stage training. Stage 1 trains the base components via $\mathcal{L}_{rec}$. Stage 2 warms up intermediate exits $\mathcal{H}_{inter}$ via $\mathcal{L}_{inter}$. Stage 3 optimizes the AC-Router using $\mathcal{L}_{rec}$ alongside router-specific loss terms ($\mathcal{L}_{LB}$, $\mathcal{L}_{Hinge}$, $\mathcal{L}_Z$). In the given sequence example, solid green arrows depict active routing weights assigned by the AC-Router, whereas dotted arrows indicate unselected exits that do not contribute to the final fused distribution $\mathbf{O}^{fused}$.](/images/papers/2608.17316/figure_017_framework_overview-crop.png)

**原图说明：** Overview of the FLEXRec framework and its three-stage training. Stage 1 trains the base components via $\mathcal{L}_{rec}$. Stage 2 warms up intermediate exits $\mathcal{H}_{inter}$ via $\mathcal{L}_{inter}$. Stage 3 optimizes the AC-Router using $\mathcal{L}_{rec}$ alongside router-specific loss terms ($\mathcal{L}_{LB}$, $\mathcal{L}_{Hinge}$, $\mathcal{L}_Z$). In the given sequence example, solid green arrows depict active routing weights assigned by the AC-Router, whereas dotted arrows indicate unselected exits that do not contribute to the final fused distribution $\mathbf{O}^{fused}$.

**图示解释：** 该图对应论文中的“Overview of the FLEXRec framework and its three-stage training. Stage 1 trains the base components via $\mathcal{L}_{rec}$. Stage 2 warms up intermediate exits $\mathcal{H}_{inter}$ via $\mathcal{L}_{inter}$. Stage 3 optimizes the AC-Router using $\mathcal{L}_{rec}$ alongside router-specific loss terms ($\mathcal{L}_{LB}$, $\mathcal{L}_{Hinge}$, $\mathcal{L}_Z$). In the given sequence example, solid green arrows depict active routing weights assigned by the AC-Router, whereas dotted arrows indicate unselected exits that do not contribute to the final fused distribution $\mathbf{O}^{fused}$.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 提出从静态单出口LLM推荐器向动态多层融合范式的转变，通过自适应集成不同LLM传播深度的预测评分分布，有效补偿紧凑LLM骨干有限的语义建模能力。
2. 设计自适应连续路由器（AC-Router），采用连续ReLU路由机制，根据每个用户序列的复杂度动态决定激活哪些出口以及激活多少个出口，实现输入自适应的计算深度分配。
3. 提出target-k hinge loss，通过连续Sigmoid代理和不对称双侧铰链损失，软性惩罚激活出口数量偏离目标范围[1, k]的情况，在无额外参数开销下实现路由稀疏性控制。
4. 设计三阶段训练流程：先训练LLM推荐骨干，再独立训练中间出口，最后冻结骨干仅训练AC-Router，使路由器梯度纯粹反映融合策略，支持灵活部署不同target-k的路由器共享同一冻结骨干。

## 五、实验数据集选择

- Amazon Toys and Games (Toys)
- Amazon Beauty
- Yelp

## 六、消融实验

We conduct ablation studies on the three AC-Router-related loss terms in Section III-D to demonstrate their importance in training an optimal router for layer-wise exit fusion. Table III presents the performance of the default framework alongside variants where individual loss components are disabled. The empirical results confirm that the default setting consistently achieves the highest accuracy across all datasets and both LLM backbones. Disabling any of the introduced loss terms leads to a sub-optimally trained router and inevitably impedes overall recommendation performance.

Additionally, we investigate the impact of the proposed target-k hinge loss $( \mathcal { L } _ { H i n g e } )$ in controlling the number of exits utilized for fusion. Figure 3 plots the exit usage statistics to compare the default setting against the variant lacking $\mathcal { L } _ { H i n g e } .$ Removing this hinge loss clearly causes severe routing instability. For instance, the maximum number of active exits surges to 16 on the Beauty dataset under the Qwen backbone. In contrast, the default configuration substantially reduces extreme exit activation and keeps the average utilization near the target capacity.

## 七、Benchmark 结果与解释

We present the overall performance results of our work and baseline methods in Table II. First, we observe that the Skyline setting consistently outperforms the standard E4SRec baseline, confirming that the parameter scale of the LLM backbone is crucial to the performance of general LLM-RS architectures. However, FLEXRec effectively subverts this reliance on sheer parameter size. Despite using a backbone approximately half the size of the Skyline setting, FLEXRec consistently achieves the best performance among the comparable compact-backbone methods on the $N = 1 0$ metrics. It additionally surpasses the larger-backbone Skyline in several settings, including Beauty under both backbones and Yelp under Qwen. To verify the effectiveness of layer-wise exit fusion instead of simply selecting the best exits after the Stage 1 and 2 training, we also present the distribution plots of all independent exits in Figure 2. Notably, FLEXRec’s adaptive fusion consistently outperforms the best-performing individual exit across all evaluated settings.

When comparing our framework against MoE variants (i.e., SparseToken, DynamicMoE, and LD-MoLE), we observe that while the variants generally improve upon the original E4SRec on Toys and Beauty, they falter on the sparser Yelp dataset, especially for SparseToken and DynamicMoE variants. As for other LLM methods, their performance varies greatly and generally falls short of discriminative models like E4SRec and FLEXRec. Some methods, such as SPRec, even underperform traditional models. One possible explanation is their greater sensitivity to item textual representations, which may affect sample selection during DPO training.

Regarding model inference efficiency, traditional methods naturally incur the lowest latency due to their architectural simplicity. Among LLM-based approaches, the discriminative E4SRec remains the fastest. This showcases the major merit of discriminative models compared to generative ones (e.g., SETRec), which rely on time-consuming autoregressive text decoding. Our method inherits this efficiency paradigm. By processing the sequence in a single forward pass and utilizing lightweight routing, FLEXRec introduces minimal additional latency (less than 1ms overhead compared to E4SRec) while delivering impressive accuracy gains.

## 八、总结

In this paper, we propose FLEXRec, a layer-wise exit fusion framework that enhances compact LLMs for scalable sequential recommendation. FLEXRec adopts a discriminative retrieval paradigm to enable efficient full-corpus ranking and employs an adaptive continuous router (AC-Router) to dynamically select and fuse layer-wise score distributions for each user sequence. A novel target-k hinge loss further regulates the number of activated exits to maintain routing sparsity. Extensive experiments on three real-world datasets demonstrate that FLEXRec effectively compensates for the limited capacity of compact LLM backbones, achieving stateof-the-art accuracy among compact-backbone methods while maintaining efficient inference.

## References

[1] K. Bao, J. Zhang, Y. Zhang, W. Wang, F. Feng, and X. He, “Tallrec: An effective and efficient tuning framework to align large language model with recommendation,” in RecSys, 2023, pp. 1007–1014.

[2] Y. Zhang, F. Feng, J. Zhang, K. Bao, Q. Wang, and X. He, “Collm: Integrating collaborative embeddings into large language models for recommendation,” TKDE, 2025.

[3] C. Yu et al., “Cosmo: A large-scale e-commerce common sense knowledge generation and serving system at amazon,” in Companion of SIGMOD, 2024, pp. 148–160.

[4] X. Liang, V. Nguyen, V. Le, P. Albert, and J. Monteil, “In-context learning for addressing user cold-start in sequential movie recommenders,” in RecSys, 2025, pp. 979–982.

[5] J. Liao, S. Li, Z. Yang, J. Wu, Y. Yuan, X. Wang, and X. He, “Llara: Large language-recommendation assistant,” in SIGIR, 2024.

[6] J. Kaplan, S. McCandlish, T. Henighan, T. B. Brown, B. Chess, R. Child, S. Gray, A. Radford, J. Wu, and D. Amodei, “Scaling laws for neural language models,” arXiv preprint arXiv:2001.08361, 2020.

[7] A. Yang et al., “Qwen3 technical report,” 2025.

[8] W. Yue, Y. Yin, X. Zhang, B. Shi, T. Liang, and J. Wan, “Cot4rec: Revealing user preferences through chain of thought for recommender systems,” in AAAI, vol. 39, no. 12, 2025, pp. 13 142–13 151.

![](images/9a78d7cc2d6b4a5e01a6addf278e87dd4b188393b57a679a4393e3bd69983e55.jpg)

![](images/6a68157d4fc57a277976f38392cddcbd383cac77ebf810b82fb650f34f0a0d5d.jpg)

![](images/eac33435efe9a66117cee46574d7c77787ccf50b94dfff5ea33ad1b8755ccca3.jpg)

![](images/1669e9b3eaf47a76f2e4d10c6c1095112df6411c6566c6cd582a397cc8c58d82.jpg)

![](images/aa2ff8282f83dbd8e22e9bd31183e749ec008f4039ee9362b9a7f4bb6dd859a0.jpg)

![](images/b1a8957de0ca83ef9b2763e25fe4bc0ceb938382e59e062b75819c95d85fef20.jpg)  
Fig. 5: Adaptive routing behavior of FLEXRec across varying user sequence lengths. The x-axis categorizes users into interaction history bins, while the y-axis indicates the average number of exits assigned. Error bars denote the standard deviation of the router’s decisions.

[9] X. Kong, J. Jiang, B. Liu, Z. Xu, H. Zhu, J. Xu, B. Zheng, J. Wu, and X. Wang, “Think before recommendation: Autonomous reasoningenhanced recommender,” NIPS, vol. 38, pp. 141 209–141 232, 2025.

[10] Y. Cui, F. Liu, P. Wang, B. Wang, H. Tang, Y. Wan, J. Wang, and J. Chen, “Distillation matters: empowering sequential recommenders to match the performance of large language models,” in RecSys, 2024.

[11] S. Kim, H. Kang, K. Kim, J. Kim, D. Kim, M. Yang, K. Oh, J. McAuley, and C. Park, “Lost in sequence: Do large language models understand sequential recommendation?” in KDD, 2025, pp. 1160–1171.

[12] L. Wu et al., “A survey on large language models for recommendation,” WWW, 2024.

[13] W. Wang, H. Bao, X. Lin, J. Zhang, Y. Li, F. Feng, S.-K. Ng, and T.-S. Chua, “Learnable item tokenization for generative recommendation,” in CIKM, 2024, pp. 2400–2409.

[14] N. De Cao, G. Izacard, S. Riedel, and F. Petroni, “Autoregressive entity retrieval,” in ICLR, 2020.

[15] X. Li, C. Chen, X. Zhao, Y. Zhang, and C. Xing, “E4srec: An elegant effective efficient extensible solution of large language models for sequential recommendation,” arXiv preprint arXiv:2312.02443, 2023.

[16] H. Bao, W. Wang, X. Lin, F. Zhu, T. Sun, F. Feng, and T.-S. Chua, “Heterogeneous user modeling for llm-based recommendation,” in RecSys, 2025, pp. 145–154.

[17] Z. Hong et al., “Scale matters: Large language models with billions (rather than millions) of parameters better match neural representations of natural language,” 2024.

[18] O. Skean, M. R. Arefin, D. Zhao, N. N. Patel, J. Naghiyev, Y. Lecun, and R. Shwartz-Ziv, “Layer by layer: Uncovering hidden representations in language models,” in ICML. PMLR, 2025, pp. 55 854–55 875.

[19] A. Gromov, K. Tirumala, H. Shapourian, P. Glorioso, and D. Roberts, “The unreasonable ineffectiveness of the deeper layers,” in ICLR, 2025.

[20] W.-C. Kang and J. McAuley, “Self-attentive sequential recommen

### 在线资源

- [论文：arXiv 2608.17316](https://arxiv.org/abs/2608.17316)
- [代码：GitHub](https://github.com/xurong-liang/FLEXRec)
- [PDF源文件](/papers/2608.17316.pdf)
