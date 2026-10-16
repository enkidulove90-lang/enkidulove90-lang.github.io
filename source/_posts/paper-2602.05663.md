---
title: "Coarse-to-Fine Long-term Interest Modeling for Generative Recommendation"
date: 2026-02-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2602.05663
arxiv_id: "2602.05663"
---

## 一、简介

Leveraging long-term user behavioral patterns is a key trajectory for enhancing the accuracy of modern recommender systems. Due to the quadratic complexity of attention mechanisms, existing GR models are typically confined to short interaction sequences. While pioneer works have attempted to adapt Search-based Interest Models (SIM) to the generative context, they typically overlook the inherent hierarchical distinction of SIDs. GR is fundamentally a coarse-to-fine generation task, where the initial SIDs (prefix) deter mine the broad semantic category and the subsequent SIDs (sufix) pinpoint the specific item. Thus, our core insight is that the prefix and sufix of SIDs require distinct long-term signal injections. To bridge this gap, we propose GLASS, a Generative recommendation framework that integrates Long-term user interests into the gener ative process viA SIDTier and Semantic Search. For the generation of SID prefix, we introduce SID-Tier, a module that maps long-term interactions into a unified interest vector to enhance the prediction of the initial SID token. SID-Tier leverages the compact nature of the semantic codebook to incorporate cross features between the user’s long-term history and candidate semantic codes. Furthermore, for the generation of SID sufix , we present semantic hard search, which utilizes generated coarse-grained semantic ID as dynamic keys to extract relevant historical behaviors, which are then fused via an adaptive gated fusion module to recalibrate the trajectory of subsequent fine-grained tokens. Extensive experiments on two large-scale real-world datasets, TAOBAO-MM and KuaiRec, demonstrate that GLASS outperforms state-of-the-art baselines. A two-week online A/B test on a short-video platform demonstrate that GLASS achieves significant gains in recommendation quality. Our codes are publicly available at this anonymous link to facilitate further research in generative recommendation.

## 二、论文方法

As mentioned above, it is challenging to introduce long-term sequence into generative recommendation paradigm. To solve this problem, we propose GLASS, a generative long-sequence modeling framework via SID-Tier and Semantic Search. To retrieve related items from the long-term sequence, we perform hard search with the first codeword. Although the generation of follow-up codewords can be boosted by retrieved items, the generation of the first codeword lacks extra information. Thus, we propose SID-Tier to capture the cross feature between the first codeword and the long-term sequence, which can be calculated in advance. After that, we propose a gate module to better merge user’s short-term and long-term interest.

The overall architecture of our proposed GLASS is illustrated in Figure 1. It consists of three primary components: SID-Tier module to enhance the prediction of the initial token, a semantic hard search module for fine-grained trajectory recalibration, and a sparsityaware augmentation strategy to provide suficient information gain to guide the subsequent fine-grained generation.

## 三、论文里的图与解释

### 图 1

![Figure 1: Overview of the proposed GLASS framework. (a) GLASS adopts the encoder-decoder architecture. The encoder processes short-term item sequences and SID-Tier to capture user interests. The decoder integrates encoder output and Semantic Search via dual cross attention. (b) SID-Tier aggregates long-term history into a unified interest vector to enhance the first codeword $( s i d _ { 1 } )$ prediction. (c) Semantic Hard Search performs hard search based on the generated $s i d _ { 1 } ,$ followed by a gate to enhance the generation of fine-grained tokens $( s i d _ { 2 } , s i d _ { 3 } )$ . sparsity-aware augmentation ensures robust context by incorporating semanti neighbors or resizing the codebook](/images/papers/2602.05663/e5a32d2e4fd2de8aa1d8610dacc94fded27cfe77a11012eb29fb1037dd04d49f.jpg)

**原图说明：** Figure 1: Overview of the proposed GLASS framework. (a) GLASS adopts the encoder-decoder architecture. The encoder processes short-term item sequences and SID-Tier to capture user interests. The decoder integrates encoder output and Semantic Search via dual cross attention. (b) SID-Tier aggregates long-term history into a unified interest vector to enhance the first codeword $( s i d _ { 1 } )$ prediction. (c) Semantic Hard Search performs hard search based on the generated $s i d _ { 1 } ,$ followed by a gate to enhance the generation of fine-grained tokens $( s i d _ { 2 } , s i d _ { 3 } )$ . sparsity-aware augmentation ensures robust context by incorporating semanti neighbors or resizing the codebook

**图示解释：** 该图对应论文中的“Figure 1: Overview of the proposed GLASS framework. (a) GLASS adopts the encoder-decoder architecture. The encoder processes short-term item sequences and SID-Tier to capture user interests. The decoder integrates encoder output and Semantic Search via dual cross attention. (b) SID-Tier aggregates long-term history into a unified interest vector to enhance the first codeword $( s i d _ { 1 } )$ prediction. (c) Semantic Hard Search performs hard search based on the generated $s i d _ { 1 } ,$ followed by a gate to enhance the generation of fine-grained tokens $( s i d _ { 2 } , s i d _ { 3 } )$ . sparsity-aware augmentation ensures robust context by incorporating semanti neighbors or resizing the codebook”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. SID-Tier模块：针对首个SID token缺乏前置轨迹的问题，利用第一层码本的紧凑性，将长期交互映射为跨语义簇的兴趣直方图（interest histogram），通过原型对齐和分桶统计构建统一兴趣向量，作为编码器的全局先验注入，增强sid1的预测。
2. 语义硬搜索（Semantic Hard Search）：以自回归生成的粗粒度sid1作为动态语义键，从用户长期历史中硬检索具有相同第一层码字的物品子序列，构建RAG式上下文窗口，为后续细粒度token生成提供语义一致的历史信号，避免无关噪声干扰。
3. 自适应门控融合机制：在解码器中并行使用两个交叉注意力模块分别建模短期序列视图和检索长期视图，通过可学习的标量门控g动态平衡二者贡献，实现短期意图与长期偏好的自适应融合，替代DualGR的硬选择策略。
4. 稀疏感知增强策略：针对语义硬搜索中检索子序列过短（如平均仅7.8个物品）导致信息增益不足的问题，提出两种策略——放宽匹配机制动态纳入语义邻居，或调整码本结构增加桶密度，以保证检索上下文的充分信息量。

## 五、实验数据集选择

To validate the practical value ofour method in an industrial setting, we conducted an online A/B test on a short-video recommendation platform for two weeks. We allocated 3%(approximately 12 million) of total users to the experimental group and another 3% to the control group. Results show that GLASS significantly improves user engagement. At the 95% confidence level, the experimental group achieved a +0.056% increase in total app usage time and a +0.052% increase in app usage time per user. Moreover, recall improved by 3 percentage points (absolute) compared to the baseline. These results strongly demonstrate the practical value of our method in industrial recommendation scenarios.

## 六、消融实验

5.3.1 Synergy ofSID-Tier and SHS. To investigate the specific loca tions and stages where diferent modules contribute to performance improvements , we analyze the model across two dimensions: Train ing Accuracy(����), measured under teacher-forcing to represent the model’s fit at the �-th hierarchical level, and Inference Preci sion (��), which measures the conditional probability that the �-th code is correct given that all preceding prefixes were accurately predicted during top-1 beam search. As illustrated in Figure 2, the integration of the SID-Tier module yields substantial performance gains over the vanilla model. For instance, Recall@5 increases from

0.0702 to 0.0842. This improvement is fundamentally rooted in the prefix-dependent nature of the Semantic ID paradigm. By employing SID-Tier, ���1 rises from 0.2410 to 0.2485, which directly translates to an increase in $P _ { 1 }$ from 0.1470 to 0.1587. The Semantic Hard Search (SHS) module provides a complementary boost. As shown in the training accuracy metrics in Figure 2, GLASS, which integrates both SID-Tier and SHS, promotes ���2 and $P _ { 2 }$ significantly. The synergy between SID-Tier and SHS allows the model to maintain high fidelity across the entire sequence, resulting in the highest observed values for Recall@10 and NDCG@10.

5.3.2 Sparsity-Aware Augmentation Method. The impact of Codebook Resizing (CR) and Semantic Neighbor Augmentation (SN) is summarized in Figure 3. We observe that CR significantly enhances the model’s ranking capability, with the GLASS(mode=CR) configuration achieving the peak Recall@10. Regarding the SN strategy, the results in Figure 3 exhibit divergent behavior. SN demonstrates its eficacy in the setting without codebook resizing, which confirms that SN can alleviate the sparsity bottleneck of SHS by augmenting the retrieval context with semantic neighbors. Conversely, in settings with codebook resizing, SN shows a marginal degradation in performance compared to the mode without SN. This is attributed to the noise introduced by semantic neighbors; when codebooks represent broad interest clusters, softening the search space likely blurs the boundaries between distinct user interests.

![](images/86e12dd0aec3a5761344d9bb493626f7da287e1b82879c2978cb5bb2435317df.jpg)

Training Accuracy & Inference Precision  
![](images/acd20e9ee837faefb19b3094ccbe0526f41c18756fcce278a55a672b1393cf24.jpg)  
Figure 2: Performance comparison of SID-Tier and SHS mod ules. The legends represent: Vanilla (Blue), +SID-Tier (Light Blue), +SHS (Red), and GLASS Full (Orange).

![](images/331a30dbf84107148711946b3cc811c8074d8a82ce763739113a5574b920ec33.jpg)  
Figure 3: Ablation study on Sparsity Augmentation across diferent modes (None, CR, SN, and CR+SN).

## 七、Benchmark 结果与解释

Table 2 reports the overall performance of our proposed method and the baselines on the Taobao-MM and KuaiRec datasets. We observe that GLASS consistently outperforms all baseline models across all evaluation metrics on both datasets. Specifically, compared with the strongest baseline, our model achieves a significant relative improvement of up to 21.57% and 29.91% in terms of H@1 and N@3 on the Taobao-MM dataset.

We attribute the superiority ofGLASS to several key factors. First, compared to traditional sequential recommendation methods, Ours efectively leverages long-term user behavior sequences to capture more comprehensive user interests. Although the recent generative model DualGR also incorporates long-sequence information, it exhibits two major limitations that GLASS successfully addresses: (1) Instead of relying on simple average pooling to generate user representations, which fails to capture fine-grained interaction features between the user and the candidate items, our SID-Tier mechanism provides richer information by explicitly modeling target-aware interactions. (2) In the generation process of hierarchical SIDs, traditional method employs only a single cross attention module per layer, which limits its ability to organically fuse short-term and long-term behavioral signals. Our method adopts a more sophisticated fusion strategy, ensuring that both transient intents and persistent preferences are well-integrated.

Table 2: Overall performance comparison on Taobao-MM and KuaiRec datasets. The best results are highlighted in bold, and the second-best are underlined. The background color indicates our proposed model.

<table><tr><td rowspan="2">Dataset</td><td rowspan="2">Type</td><td rowspan="2">Model</td><td colspan="5">Recall (R@K)</td><td colspan="4">NDCG (N@K)</td></tr><tr><td>R@1</td><td>R@3</td><td>R@5</td><td>R@10</td><td>R@20</td><td>N@3</td><td>N@5</td><td>N@10</td><td>N@20</td></tr><tr><td rowspan="11">Taobao-MM</td><td rowspan="7">ID</td><td>Caser</td><td>0.0191</td><td>0.0253</td><td>0.0293</td><td>0.0394</td><td>0.0611</td><td>0.0228</td><td>0.0243</td><td>0.0275</td><td>0.0330</td></tr><tr><td>HGN</td><td>0.0179</td><td>0.0287</td><td>0.0340</td><td>0.0444</td><td>0.0575</td><td>0.0242</td><td>0.0264</td><td>0.0298</td><td>0.0329</td></tr><tr><td>GRU4Rec</td><td>0.0196</td><td>0.0304</td><td>0.0397</td><td>0.0489</td><td>0.0587</td><td>0.0242</td><td>0.0296</td><td>0.0326</td><td>0.0350</td></tr><tr><td>SASRec</td><td>0.0221</td><td>0.0386</td><td>0.0387</td><td>0.0524</td><td>0.0624</td><td>0.0321</td><td>0.0322</td><td>0.0365</td><td>0.0454</td></tr><tr><td>Bert4Rec</td><td>0.0267</td><td>0.0376</td><td>0.0475</td><td>0.0542</td><td>0.0731</td><td>0.0337</td><td>0.0374</td><td>0.0395</td><td>0.0443</td></tr><tr><td> $S^3$ -Rec</td><td>0.0289</td><td>0.0347</td><td>0.0375</td><td>0.0552</td><td>0.0762</td><td>0.0321</td><td>0.0333</td><td>0.0453</td><td>0.0590</td></tr><tr><td>HSTU</td><td>0.0274</td><td>0.0452</td><td>0.0512</td><td>0.0784</td><td>0.1023</td><td>0.0384</td><td>0.0412</td><td>0.0495</td><td>0.0592</td></tr><tr><td rowspan="3">SID</td><td>Tiger</td><td>0.0280</td><td>0.0571</td><td>0.0756</td><td>0.1076</td><td> $\underline{0.1498}$ </td><td> $\underline{0.0448}$ </td><td>0.0523</td><td>0.0627</td><td>0.0733</td></tr><tr><td>DualGR</td><td> $\underline{0.0306}$ </td><td> $\underline{0.0592}$ </td><td> $\underline{0.0781}$ </td><td> $\underline{0.1126}$ </td><td> $\underline{0.1487}$ </td><td> $\underline{0.0438}$ </td><td> $\underline{0.0578}$ </td><td> $\underline{0.0653}$ </td><td> $\underline{0.0738}$ </td></tr><tr><td>GLASS</td><td> $\underline{0.0372}$ </td><td> $\underline{0.0720}$ </td><td> $\underline{0.0934}$ </td><td> $\underline{0.1284}$ </td><td> $\underline{0.1723}$ </td><td> $\underline{0.0582}$ </td><td> $\underline{0.0669}$ </td><td> $\underline{0.0782}$ </td><td> $\underline{0.0893}$ </td></tr><tr><td></td><td>Impr.</td><td>21.57%</td><td>21.62%</td><td>19.59%</td><td>14.03%</td><td>15.02%</td><td>29.91%</td><td>15.74%</td><td>19.75%</td><td>21.00%</td></tr><tr><td rowspan="11">KuaiRec</td><td rowspan="7">ID</td><td>Caser</td><td>0.0185</td><td>0.0556</td><td>0.0603</td><td>0.0918</td><td>0.1254</td><td>0.0373</td><td>0.0392</td><td>0.0493</td><td>0.0578</td></tr><tr><td>HGN</td><td>0.0262</td><td>0.0570</td><td>0.0791</td><td>0.1110</td><td>0.1582</td><td>0.0436</td><td>0.0525</td><td>0.0629</td><td>0.0747</td></tr><tr><td>GRU4Rec</td><td>0.0348</td><td>0.0469</td><td>0.0582</td><td>0.0887</td><td>0.1263</td><td>0.0428</td><td>0.0475</td><td>0.0572</td><td>0.0666</td></tr><tr><td>SASRec</td><td>0.0352</td><td>0.0638</td><td>0.0857</td><td>0.1180</td><td>0.1040</td><td>0.0498</td><td>0.0587</td><td>0.0703</td><td>0.0826</td></tr><tr><td>Bert4Rec</td><td>0.0404</td><td>0.0588</td><td>0.0698</td><td>0.0902</td><td>0.1244</td><td>0.0507</td><td>0.0553</td><td>0.0617</td><td>0.0704</td></tr><tr><td> $S^3$ -Rec</td><td>0.0385</td><td>0.0625</td><td>0.0780</td><td>0.1125</td><td> $\underline{0.1450}$ </td><td>0.0535</td><td>0.0605</td><td>0.0710</td><td>0.0795</td></tr><tr><td>HSTU</td><td>0.0334</td><td>0.0645</td><td>0.0845</td><td>0.1183</td><td> $\underline{0.1689}$ </td><td>0.0513</td><td>0.0595</td><td>0.0704</td><td>0.0830</td></tr><tr><td rowspan="3">SID</td><td>Tiger</td><td>0.0406</td><td>0.0700</td><td>0.0859</td><td>0.1202</td><td>0.1530</td><td>0.0574</td><td>0.0641</td><td>0.0751</td><td>0.0834</td></tr><tr><td>DualGR</td><td>0.0445</td><td> $\underline{0.0745}$ </td><td> $\underline{0.0932}$ </td><td>0.1292</td><td>0.1678</td><td> $\underline{0.0632}$ </td><td> $\underline{0.0718}$ </td><td> $\underline{0.0821}$ </td><td> $\underline{0.0908}$ </td></tr><tr><td>GLASS</td><td> $\underline{0.0467}$ </td><td> $\underline{0.0778}$ </td><td> $\underline{0.0971}$ </td><td> $\underline{0.1345}$ </td><td> $\underline{0.1742}$ </td><td> $\underline{0.0659}$ </td><td> $\underline{0.0749}$ </td><td> $\underline{0.0855}$ </td><td> $\underline{0.0946}$ </td></tr><tr><td></td><td>Impr.</td><td>4.94%</td><td>4.43%</td><td>4.18%</td><td>4.10%</td><td>3.81%</td><td>4.27%</td><td>4.32%</td><td>4.14%</td><td>4.19%</td></tr></table>

Furthermore, we observe that the performance gain is more pronounced on the Taobao-MM dataset than on KuaiRec. This discrepancy stems from the diference in multimodal data qual ity. In the Taobao-MM dataset, we utilize high-quality multimodal features learned via supervised contrastive learning, which ofers superior semantic alignment. In contrast, the multimodal informa tion in KuaiRec is derived from simple text-based encoding, leading to relatively lower representational quality and thus more limited performance improvements.

## 八、总结

In this paper, we present GLASS, a novel generative recommendation framework designed to efectively harness long-term user interaction sequences within the generative recommender system. Our approach addresses the fundamental challenge of information under-utilization in existing GR systems when dealing with ex tensive behavioral histories. We introduce SID-Tier, a module that facilitates feature interaction between a user’s long history and the semantic codebook. By capturing global semantic preferences, SID-Tier provides a robust global context that enhances the prediction of the critical initial token. Furthermore, we propose semantic hard search. By utilizing the generated SID as a search key, the model recalibrates the generation trajectory of subsequent fine-grained to kens. To overcome the information scarcity bottleneck in semantic search, we implement sparsity-aware augmentation, ensuring an informative context for fine-grained generation.Extensive experi ments on the TAOBAO-MM and KuaiRec datasets demonstrate that GLASS outperforms baselines. In future work, we aim to explore the potential of integrating cross domain long-term behaviors to further enrich the semantic search process.

## References

[1] Yue Cao, Xiaojiang Zhou, Jiaqi Feng, Peihao Huang, Yao Xiao, Dayao Chen, and Sheng Chen. 2022. Sampling is all you need on modeling long-term user behaviors for CTR prediction. In Proceedings ofthe 31st ACM International Conference on Information & Knowledge Management. 2974–2983.

[2] Jianxin Chang, Chenbin Zhang, Zhiyi Fu, Xiaoxue Zang, Lin Guan, Jing Lu, Yiqun Hui, Dewei Leng, Yanan Niu, Yang Song, et al. 2023. TWIN: TWo-stage interest network for lifelong user behavior modeling in CTR prediction at kuaishou. In Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 3785–3794.

[3] Ben Chen, Xian Guo, Siyuan Wang, Zihan Liang, Yue Lv, Yufei Ma, Xinlong Xiao, Bowen Xue, Xuxin Zhang, Ying Yang, Huangyu Dai, Xing Xu, Tong Zhao, Mingcan Peng, Xiaoyang Zheng, Chao Wang, Qihang Zhao, Zhixin Zhai, Yang Zhao, Bochao Liu, Jingshan Lv, Xiao Liang, Yuqing Ding, Jing Chen, Chenyi Lei, Wenwu Ou, Han Li, and Kun Gai. 2025. OneSearch: A Preliminary Explo ration of the Unified End-to-End Generative Framework for E-commerce Search. arXiv:2509.03236 [cs.IR] https://arxiv.org/abs/2509.03236

[4] Qiwei Chen, Changhua Pei, Shanshan Lv, Chao Li, Junfeng Ge, and Wenwu Ou. 2021. End-to-end user behavior retrieval in click-through rateprediction model. arXiv preprint arXiv:2108.04468 (2021).

[5] Jiaxin Deng, Shiyao Wang, Kuo Cai, Lejian Ren, Qigen Hu, Weifeng Ding, Qiang Luo, and Guorui Zhou. 2025. Onerec: Unifying retrieve and rank with generative recommender and iterative preference alignment. arXiv preprint arXiv:2502.18965 (2025).

[6] Kairui Fu, Tao Zhang, Shuwen Xiao, Ziyang Wang, Xinming Zhang, Chenchi Zhang, Yuliang Yan, Junjun Zheng, Yu Li, Zhihong Chen, Jian Wu, Xiangheng Kong, Shengyu Zhang, Kun Kuang, Yuning Jiang, and Bo Zheng. 2025. FORGE: Forming Semantic Identifiers for Generative Retrieval in Industrial Datasets. arXiv:2509.20904 [cs.IR] https://arxiv.org/abs/2509.20904

[7] Chongming Gao, Shijun Li, Wenqiang Lei, Jiawei Chen, Biao Li, Peng Jiang, Xiangnan He, Jiaxin Mao, and Tat-Seng Chua. 2022. KuaiRec: A Fully-observed Dataset and Insights for Evaluating Recommender Systems. In Proceedings ofthe 31st ACM International Conference on Information &amp; Knowledge Management (CIKM ’22). ACM, 540–550. doi:10.1145/3511808.3557220

[8] Chengcheng Guo, Kuo Cai, Yu Zhou, Qiang Luo, Ruiming Tang, Han Li, Kun Gai, and Guorui Zhou. 2026. PROMISE: Process Reward Models Unlock Test-Time Scaling Laws in Generative Recommendations. arXiv:2601.04674 [cs.IR] https://arxiv.org/abs/2601.04674

[9] Chengcheng Guo,Junda She, Kuo Cai, Shiyao Wang, Qigen Hu, Qiang Luo, Guorui Zhou, and Kun Gai. 2025. MISS: Multi-Modal Tree Indexing and Searching with Lifelong Sequential Behavior for Retrieval Recommendation. In Proceedings ofthe 34th ACM International Conference on Information and Knowledge Management. 5683–5690.

[10] Balázs Hidasi, Alexandros Karatzoglou, Linas Baltrunas, and Domonkos Tikk. 2016. Session-based Recommendations with Recurrent Neural Networks. arXiv:1511.06939 [cs.LG] https://arxiv.org/abs/1511.06939

[11] Yupeng Hou, Jianmo Ni, Zhankui He, Noveen Sachdeva, Wang-Cheng Kang, Ed H Chi, Julian McAuley, and Derek Zhiyuan Cheng. 2025. ActionPiece: Contextually Tokenizing Action Sequences for Generative Recommendation. arXiv preprint arXiv:2502.13581 (2025).

[12] Kalervo Järvelin and Jaana Kekäläinen. 2002. Cumulated gain-based evaluation of IR techniques. ACM Transactions on Information Systems (TOIS) 20, 4 (2002), 422–446.

[13] Wang-Cheng Kang and Julian McAuley. 2018. Self-Attentive Sequential Recommendation. arXiv:1808.09781 [cs.IR] https://arxiv.org/abs/1808.09781

[14] Xiaopeng Li, Bo Chen, Junda She, Shiteng Cao, You Wang, Qinlin Jia, Haiying He, Zheli Zhou, Zhao Liu, Ji Liu, et al. 2025. A Survey of Generative Recommendation from a Tri-Decoupled Perspective: Tokenization, Architecture, and Optimization. (2025).

[15] Zida Liang, Changfa Wu, Dunxian Huang, Weiqiang Sun, Ziyang Wang, Yuliang Yan, Jia

### 在线资源

- [论文：arXiv 2602.05663](https://arxiv.org/abs/2602.05663)
- [PDF源文件](/papers/2602.05663.pdf)
