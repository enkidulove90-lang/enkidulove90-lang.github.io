---
title: "RADAR: Recall Augmentation through Deferred Asynchronous Retrieval"
date: 2025-06-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2506.07261
arxiv_id: "2506.07261"
---

## 一、简介

Modern large-scale recommender systems employ multi-stage ranking funnel (Retrieval, Pre-ranking, Ranking) to balance engagement and computational constraints (latency, CPU). However, the initial retrieval stage, often relying on efficient but less precise methods like K-Nearest Neighbors (KNN), struggles to effectively surface the most engaging items from billion-scale catalogs, particularly distinguishing highly relevant and engaging candidates from merely relevant ones. We introduce Recall Augmentation through Deferred Asynchronous Retrieval (RADAR), a novel framework that leverages asynchronous, offline computation to pre-rank a significantly larger candidate set for users using the full complexity ranking model. These topranked items are stored and utilized as a high-quality retrieval source during online inference, bypassing online retrieval and preranking stages for these candidates. We demonstrate through offline experiments that RADAR significantly boosts recall (2X Recall@200 vs DNN retrieval baseline) by effectively combining a larger retrieved candidate set with a more powerful ranking model. Online A/B tests confirm a +0.8% lift in topline engagement metrics, validating RADAR as a practical and effective method to improve recommendation quality under strict online serving constraints.

## 二、论文方法

采用异步离线预计算与在线注入相结合的方法。离线阶段：对目标用户使用高效检索方法获取50倍候选集，再用全量排序模型评分，将Top-200结果存入键值存储。在线阶段：并行从标准检索源和RADAR存储获取候选，RADAR候选跳过预排序，与标准候选合并后由最终排序模型重排序。

## 三、论文里的图与解释

### 图 1

![Figure 1: Recall@K as a Function of Candidate Retrieved](/images/papers/2506.07261/p1_caption_1.png)

**原图说明：** Figure 1: Recall@K as a Function of Candidate Retrieved

**图示解释：** 该图对应论文中的“Figure 1: Recall@K as a Function of Candidate Retrieved”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Figure 2: RADAR End-to-End System Architecture](/images/papers/2506.07261/p2_caption_2.png)

**原图说明：** Figure 2: RADAR End-to-End System Architecture

**图示解释：** 该图对应论文中的“Figure 2: RADAR End-to-End System Architecture”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Table 1: Offline Recall@200 — RADAR vs. Baselines](/images/papers/2506.07261/p3_caption_3.png)

**原图说明：** Table 1: Offline Recall@200 — RADAR vs. Baselines

**图示解释：** 该图对应论文中的“Table 1: Offline Recall@200 — RADAR vs. Baselines”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出完全解耦的异步离线-在线混合架构，利用非高峰计算资源，使用全量生产级排序模型对50倍候选集进行离线预排序，突破了在线检索的延迟和计算瓶颈。
2. 创新点2：设计基于用户活跃度的自适应刷新调度策略，高频用户每日刷新、低频用户每周或双周刷新，在计算成本与候选新鲜度之间取得平衡。
3. 创新点3：通过在线检索源的重调（强调短期意图和新内容）与RADAR（专注长期稳定兴趣）形成互补，实现了约60%的独特候选覆盖率，最大化增量价值。

## 五、实验数据集选择

- Meta视频平台大规模用户交互数据集

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

RADAR substantially outperforms the traditional retrieval baselines in Recall@200. As shown in Table 1, RADAR achieves about 16.5% recall@200, compared to 8.1% for the DNN Two Tower source and 7.2% for the Item-KNN source. We also observed that many of the items surfaced by RADAR have niche appeal that simple similarity-based methods failed to catch.

Table 1: Offline Recall@200 — RADAR vs. Baselines

<table><tr><td>Retrieval Source</td><td>Recall@200</td></tr><tr><td>DNN</td><td>8.1%</td></tr><tr><td>Item-KNN</td><td>7.2%</td></tr><tr><td>Content-KNN</td><td>5.1%</td></tr><tr><td>RADAR</td><td>16.5%</td></tr></table>

## 八、总结

论文未提供可独立提取的总结章节。

## References

[1] Covington, Paul, Jay Adams, and Emre Sargin. 2016. Deep Neural Networks for YouTube Recommendations. In Proceedings of the 10th ACM Conference on Recommender Systems (RecSys ’16). ACM, New York, NY, USA, 191– 198. https://doi.org/10.1145/2959100.2959190.

[2] He, Xiangnan, Lizi Liao, Hanwang Zhang, Liqiang Nie, Xia Hu, and Tat-Seng Chua. 2017. Neural Collaborative Filtering. In Proceedings of the 26th International Conference on World Wide Web (WWW ’17). IW3C2, Geneva, Switzerland, 173–182. https://doi.org/10.1145/3038912.3052569

[3]. Andrzej Pacuk, Piotr Sankowski, Karol Wegrzycki, Adam Witkowski, and Piotr Wygocki. 2016. RecSys Challenge 2016: job recommendations based on preselection of offers and gradient boosting. In Proceedings of the Recommender Systems Challenge 2016 (RecSys Challenge ’16). Association for Computing Machinery, New York, NY, USA, Article 10, 1–4 pages. https://doi.org/10.1145/2987538.2987544

[4] B. Sarwar, G. Karypis, J. Konstan, and J. Riedl. Item-based collaborative filtering recommendation algorithms. In WWW, pages 285–295, 2001.

[5] X. Yi, S.-C. Wang, R. He, H. Chandrasekaran, C. Wu, L. Heldt, L. Hong, M. Chen, and E. H. Chi. 2023. Online Matching: A Real-time Bandit System for Large-scale Recommendations. In Proceedings of the 17th ACM Conference on Recommender Systems (RecSys ’23), Singapore, 403–414. ACM. DOI: 10.1145/3604915.3608792

[6] Vanessa Cai, Pradeep Prabakar, Manuel Serrano Rebuelta, Lucas Rosen, Federico Monti, Katarzyna Janocha, Tomo Lazovich, Jeetu Raj, Yedendra Shrinivasan, Hao Li, and Thomas Markovich. 2023. TwERC: High-Performance Ensembled Candidate Generation for Ads Recommendation at Twitter. In Proceedings of the Workshop on Data Mining for Online Advertising (AdKDD ’23), co-located with the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD ’23) (Long Beach, CA, USA, 7 August 2023). CEUR-WS.org, Vol. 3556, Article 8, 10 pages. DOI: https://doi.org/10.48550/arXiv.2302.13915.

[7] Jiaqi Zhai, Zhaojie Gong, Yueming Wang, Xiao Sun, Zheng Yan, Fu Li, and Xing Liu. 2023. Revisiting Neural Retrieval on Accelerators. In Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD ’23), August 6–10, 2023, Long Beach, CA, USA. Association for Computing Machinery, New York, NY, USA, 5520–5531. https://doi.org/10.1145/3580305.3599897

[8] Weiwen Liu, Yunjia Xi, Jiarui Qin, Fei Sun, Bo Chen, Weinan Zhang, Rui Zhang, and Ruiming Tang. Neural re-ranking in multi-stage recommender systems: A review. arXiv preprint arXiv:2202.06602, 2022.

[9] Xiangyang Li, Bo Chen, HuiFeng Guo, Jingjie Li, Chenxu Zhu, Xiang Long, Sujian Li, Yichao Wang, Wei Guo, Longxia Mao, et al. Inttower: the next generation of two-tower model for pre-ranking system. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management, pages 3292–3301, 2022.

### 在线资源

- [论文：arXiv 2506.07261](https://arxiv.org/abs/2506.07261)
- [PDF源文件](/papers/2506.07261.pdf)
