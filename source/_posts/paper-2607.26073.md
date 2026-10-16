---
title: "Guess Where You Go: Generative Next Point-of-Interest Recommendation in Amap"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.26073
arxiv_id: "2607.26073"
---

## 一、简介

Generative retrieval enables recommender systems to retrieve items by generating compact item identifiers, but scaling it to industrial scenarios remains challenging due to redundant or colliding token assignments and insuficient integration of heterogeneous item signals. These challenges are particularly critical for next Point of-Interest (POI) recommendation, where models must represent structured spatial entities, capture sequential mobility patterns, and produce predictions consistent with real user behavior. We propose Gwhere, an end-to-end industrial framework that integrates semantic identifier (SID) generation with LLM-based generative next POI recommendation. Gwhere first learns discriminative POI SIDs through a contrastive residual-quantization tokenizer that aligns textual, visual, spatial, and collaborative signals. Based on these SIDs, Gwhere adapts LLMs to mobility scenarios via contin ued pretraining on enriched spatio-temporal corpora, supervised fine-tuning, and Exposure-Aware Kahneman-Tversky Optimization (EAKTO), a reinforcement learning objective for behavioral prefer ence alignment. Experiments on public datasets and Amap’s large scale industrial dataset demonstrate the efectiveness of Gwhere.

∗Contributed equally to this research. †Corresponding Author.

The system has been deployed in Amap’s homepage service under high-concurrency and low-latency constraints. Long-term online A/B tests show improvements of 5.83% in P-CTR and 6.20% in U-CTR over the production baseline. The implementation is publicly available at https://github.com/alibaba/SimCIT.

## 二、论文方法

This section elaborates on the integrated framework (Gwhere) for next POI prediction, which unifies Semantic IDs (SIDs) generation and spatio-temporal LLM post-training. We first formalize the problem, then detail the motivation and design of each core component, and finally describe the inference optimization for industrial deployment.

## 三、论文里的图与解释

### 图 1

![Figure 1: Ofline Training and Online Serving Procedure of proposed framework Gwhere. Ofline Training:(1) POIs are tokenized as Semantic IDs (SIDs); (2) a base LLM is continually pretrained on the collected corpus. (3) The LLM is further fine-tuned and aligned the with inference prompt to finish this procedure. Online Serving: Gwhere is stored in a model engine and invoked through a data-service engine that converts real-time context—user profile, recent check-ins, current time, location and weather—into an instruction prompt. The model predicts the next POI in SID form, which is mapped back to a readable location and returned to the mobile client.](/images/papers/2607.26073/9763bee4fc97cac195f66407d8b739af7a16c4d51cfa29828a61c11f9d9f64d4.jpg)

**原图说明：** Figure 1: Ofline Training and Online Serving Procedure of proposed framework Gwhere. Ofline Training:(1) POIs are tokenized as Semantic IDs (SIDs); (2) a base LLM is continually pretrained on the collected corpus. (3) The LLM is further fine-tuned and aligned the with inference prompt to finish this procedure. Online Serving: Gwhere is stored in a model engine and invoked through a data-service engine that converts real-time context—user profile, recent check-ins, current time, location and weather—into an instruction prompt. The model predicts the next POI in SID form, which is mapped back to a readable location and returned to the mobile client.

**图示解释：** 该图对应论文中的“Figure 1: Ofline Training and Online Serving Procedure of proposed framework Gwhere. Ofline Training:(1) POIs are tokenized as Semantic IDs (SIDs); (2) a base LLM is continually pretrained on the collected corpus. (3) The LLM is further fine-tuned and aligned the with inference prompt to finish this procedure. Online Serving: Gwhere is stored in a model engine and invoked through a data-service engine that converts real-time context—user profile, recent check-ins, current time, location and weather—into an instruction prompt. The model predicts the next POI in SID form, which is mapped back to a readable location and returned to the mobile client.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 提出完全对比式的语义分词框架，结合可学习残差量化与层次化标识符学习，融合文本、视觉、空间和协同等多模态POI信号，通过对比损失（NT-Xent）替代重构损失，增强令牌判别性并缓解长尾POI的表示坍塌问题。
2. 设计端到端LLM生成式下一POI预测框架Gwhere，通过持续预训练（掩码SID预测和SID-属性对齐）、监督微调（SFT）和曝光感知Kahneman-Tversky优化（EAKTO）三阶段训练，使LLM适配移动领域并实现认知对齐的推荐。
3. 提出EAKTO强化学习目标，利用曝光但未点击的POI作为E-Neg信号，在标签不平衡下有效利用曝光数据，平衡用户参与度与负面反馈抑制，实验证明其优于DPO和GRPO。
4. 在工业级部署中采用预填充-解码解耦和多令牌预测等工程优化，满足高并发低延迟要求，并通过大规模在线A/B测试验证了长期效果。

## 五、实验数据集选择

- Foursquare-NYC
- Foursquare-TKY
- Gowalla-CA
- AMAP（高德工业数据集）

## 六、消融实验

4.3.1 Ablation study. To evaluate the impact of individual modules, we developed various versions of Gwhere. Initially, certain essential modules were removed: "w/o SID" replaces the proposed SID gener ation method with random id. "w/o ST" eliminates spatio-temporal descriptions from the prompt. "w/o SLD" exclude the SID-Location-Description corpus in the continued pretraining stage. "w/o CPT" exclude the Continued Pretraining stage in the post-training stage, only applying SFT and RL. "w/o SFT" and "w/o RL" denote skipping SFT and RL training in the alignment stage, respectively. As illustrated in Table 5 Left, removing any module leads to noticeable Acc@1 degradation. In particular, removing SID tokenization or RL-based preference alignment leads to the largest performance drops, demonstrating their essential roles in recommendation effectiveness.

4.3.2 Impact Analysis on Multi-modal Synergy. We systematically evaluate modality-specific contributions using the AMAP dataset containing four distinct modalities: (1). textual descriptions (denoted as TX), (2). image content (denoted as IM), (3). Spatial information (denoted as SP) and (4). collaborative filtering signals (denoted as CF). As shown in Fig. 2, progressive modality integration yields monotonically improving performance in generative recommendation tasks. Crucially, spatial features provide the largest individual gain. The full quad-modal configuration achieves stateof-the-art results, validating our framework’s capacity to synthesize cross-modal synergies and preserve modality specificity.

4.3.3 Impact Analysis on Preference Alignment. To isolate the effect of the preference alignment strategy, we fix the SID tokenizer and model architecture and compare three variants: "SFT-only" is trained with continued pretraining plus SFT, but without any explicit preference optimization loss. "SFT + DPO" denotes the baseline that adds a DPO-style loss over paired preferences derived from logged comparisons. "SFT + GRPO" represents the baseline that utilizes GRPO strategy. "SFT + EAKTO": our exposure-aware KTO setup using clicked POIs as desirable examples and exposedbut-unclicked POIs as E-Neg signals.

Table 5 Right reports the comparison. EAKTO consistently outperforms DPO and GRPO, confirming its efectiveness in leveraging abundant exposure data under label imbalance.

![](images/4a46b515bc81e2cbbc28cbbc5b5acd8525215879425e44f5c5e70ca7fa5b3a2d.jpg)  
Figure 2: Acc@1 results of AMAP under individual or composition of input modals. text is denoted as TX, IM is image, SP is spatial information and CF is collaborative signals. TX-IM (SP-CF) means composition of text-image (spatial collaborative).

Table 5: Left: Ofline ablation study using Gwhere-3B on Amap dataset. Right: Preference alignment comparison on Amap.

<table><tr><td>Ablations</td><td>Acc@1</td></tr><tr><td>w/o SID</td><td>0.2455 (↓ 16.01%)</td></tr><tr><td>w/o ST</td><td>0.2785 (↓ 4.72%)</td></tr><tr><td>w/o SLD</td><td>0.2822 (↓ 3.46%)</td></tr><tr><td>w/o CPT</td><td>0.2632 (↓ 9.96%)</td></tr><tr><td>w/o SFT</td><td>0.2725 (↓ 6.77%)</td></tr><tr><td>w/o RL</td><td>0.2580 (↓ 11.73%)</td></tr><tr><td>Gwhere</td><td>0.2923</td></tr></table>

<table><tr><td>Variants</td><td>Acc@1</td></tr><tr><td>SFT-only</td><td>0.2492</td></tr><tr><td>SFT + DPO</td><td>0.2634</td></tr><tr><td>SFT + GRPO</td><td>0.2759</td></tr><tr><td>SFT + EAKTO</td><td>0.2820</td></tr></table>

4.3.4 Impact Analysis on Training Corpus. In this section, we analyze the impact on the performance of sequence length (input tokens) and number of utilized tokens in continued pretraining stage. Figure 3 presents the results. Our investigation into the im pact of input sequence length shows that while longer context is beneficial, its utility eventually saturates. The model’s performance gains are most pronounced up to a context window of 2048 tokens (∼30 user historical check-ins) and largely stabilize beyond 4096 tokens (∼50 check-ins). This suggests that a moderately-sized his tory is suficient to encapsulate the user’s core preferences. Further extending the context window provides limited new signal, as this long-term information is already implicitly encoded in the user’s learned representation.

The volume of tokens involved in pretraining phase also proved to be a key determinant of performance. We observed a nearly linear improvement in model efectiveness as the training corpus size increased. Constrained by our training budget, the final model was trained to convergence on a dataset of 10B tokens. The consistent, non-saturating growth suggests that performance is largely data bound, with significant potential for improvement as more data becomes available.

![](images/bab3b58e4618b76cb3b96d9a59891b6dfb5750595a2b703f302fc83c98616797.jpg)

![](images/49d4e385c772d04cee1f159d046352c2536b08b3adc5c544a4722605040c9b52.jpg)  
Figure 3: Impact on the performance of sequence length (input tokens) and number of tokens involved in continued pretraining stage.

## 七、Benchmark 结果与解释

Our method substantially outperforms all baseline methods across all ofthe evaluated datasets. Table 4 illustrate the comparison results on NYC, TKY, and CA datasets. Specifically, compared to the stateof-the-art GNPR-SID which utilizes LLaMA-7B as its base model, we observe a substantial improvement on all of the versions of Gwhere. Notably, Gwhere-7B demonstrated the most significant improvements, achieving gains of 11.3%, 8.1%, and 13.2% over the SOTA, respectively.

Table 3 details the performance comparison between our proposed model and the cascade ranking system on the Amap dataset. Consistent with our findings on public datasets, all Gwhere variants significantly outperform the traditional cascade ranking system on Acc@1, with Gwhere-7B achieving 14.8% relative improvement.

![](images/9763bee4fc97cac195f66407d8b739af7a16c4d51cfa29828a61c11f9d9f64d4.jpg)  
Figure 1: Ofline Training and Online Serving Procedure of proposed framework Gwhere. Ofline Training:(1) POIs are tokenized as Semantic IDs (SIDs); (2) a base LLM is continually pretrained on the collected corpus. (3) The LLM is further fine-tuned and aligned the with inference prompt to finish this procedure. Online Serving: Gwhere is stored in a model engine and invoked through a data-service engine that converts real-time context—user profile, recent check-ins, current time, location and weather—into an instruction prompt. The model predicts the next POI in SID form, which is mapped back to a readable location and returned to the mobile client.

The scaling trend from 0.5B to 7B confirms that larger model capac ity benefits next POI prediction when combined with our SID-based generative paradigm.

Table 4: Comparison of diferent models on three datasets: NYC, TKY, and CA. We present the model inputs including the POI and User representation approach and whether visit timestamps are utilized. RID, SID, UID and UP represent Random one-hot ID, Semantic ID, User one-hot ID and User Profiles, respectively. The results for the baseline methods are borrowed from [13, 26].

<table><tr><td rowspan="2">Model</td><td colspan="3">Inputs</td><td colspan="3">Acc@1</td></tr><tr><td>POI</td><td>User</td><td>Time</td><td>NYC</td><td>TKY</td><td>CA</td></tr><tr><td>PRME</td><td>RID</td><td>UID</td><td>×</td><td>0.1159</td><td>0.1052</td><td>0.0521</td></tr><tr><td>PLSPL</td><td>RID</td><td>UID</td><td>×</td><td>0.1917</td><td>0.1889</td><td>0.1072</td></tr><tr><td>STAN</td><td>RID</td><td>UID</td><td>×</td><td>0.2231</td><td>0.1963</td><td>0.1104</td></tr><tr><td>GETNext</td><td>RID</td><td>UID</td><td>×</td><td>0.2435</td><td>0.1829</td><td>0.1357</td></tr><tr><td>STHGCN</td><td>RID</td><td>UID</td><td>×</td><td>0.2734</td><td>0.2950</td><td>0.1730</td></tr><tr><td>TPG</td><td>RID</td><td>UID</td><td>√</td><td>0.2555</td><td>0.1420</td><td>0.1749</td></tr><tr><td>ROTAN</td><td>RID</td><td>UID</td><td>√</td><td>0.3106</td><td>0.2458</td><td>0.2199</td></tr><tr><td>LLM4POI</td><td>RID</td><td>UID</td><td>√</td><td>0.3372</td><td>0.3035</td><td>0.2065</td></tr><tr><td>GNPR-SID</td><td>SID</td><td>UID</td><td>√</td><td>0.3618</td><td>0.3062</td><td>0.2403</td></tr><tr><td>Gwhere-0.5B</td><td>SID</td><td>UP</td><td>√</td><td>0.3705</td><td>0.3125</td><td>0.2555</td></tr><tr><td>Gwhere-1.5B</td><td>SID</td><td>UP</td><td>√</td><td>0.3727</td><td>0.3170</td><td>0.2585</td></tr><tr><td>Gwhere-3B</td><td>SID</td><td>UP</td><td>√</td><td>0.3872</td><td>0.3202</td><td>0.2611</td></tr><tr><td>Gwhere-7B</td><td>SID</td><td>UP</td><td>√</td><td>0.4027</td><td>0.3310</td><td>0.2721</td></tr></table>

## 八、总结

In this work, we propose a novel framework for next point-ofinterest (POI) recommendation to address key limitations of traditional retrieve-rank systems, starting with semantic IDs (SIDs) generation via a contrastive learning-based tokenization mechanism that fuses multi-modal item information (textual descriptions, spatial features, visual content, and collaborative signals), moving beyond traditional reconstruction-based quantization to enhance token discriminability and alleviate code collision. We then adapt large language models (LLMs) to the mobility domain through continued pretraining on enriched spatio-temporal corpora, equipping them with domain-specific knowledge of geographical entities and sequential mobility patterns, followed by a multi-stage fine-tuning pipeline integrating Supervised Fine-Tuning (SFT) and reinforcement learning to implement a novel alignment strategy with real user behavior preferences. For industrial deployment, we adopt engineering optimizations including prefill-decoding decoupling and multi-token prediction, enabling the framework to meet highconcurrency and low-latency requirements in real-world locationbased service (LBS) platforms. Extensive evaluations demonstrate that our framework outperforms traditional cascade ranking systems, and future work will focus on integrating more dynamic contextual signals, optimizing cold-start scenarios for new users and POIs, and exploring deeper alignment between semantic tokens and natural language to enhance recommendation interpretability for broader LBS applications.

## References

[1] Ting Chen, Simon Kornblith, Mohammad Norouzi, and Geofrey Hinton. 2020. A simple framework for contrastive learning of visual representations. In International Conference on Machine Learning.

[2] Eunjoon Cho, Seth A. Myers, and Jure Leskovec. 2011. Friendship and mobility: user movement in location-based social networks. In Proceedings ofthe 17th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (San Diego, California, USA) (KDD ’11). Association for Computing Machinery, New York, NY, USA, 1082–1090. doi:10.1145/2020408.2020579

[3] Yashar Deldjoo, Zhankui He, Julian McAuley, Anton Korikov, Scott Sanner, Arnau Ramisa, René Vidal, Maheswaran Sathiamoorthy, Atoosa Kasirzadeh, and Silvia Milano. 2024. A review ofmodern recommender systems using generative models (gen-recsys). In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 6448–6458.

[4] Jiaxin Deng, Shiyao Wang, Kuo Cai, Lejian Ren, Qigen Hu, Weifeng Ding, Qiang Luo, and Guorui Zhou. 2025. OneRec: Unifying Retrieve and Rank with Generative Recommender and Iterative Preference Alignment. arXiv:2502.18965 [cs.IR] https://arxiv.org/abs/2502.18965

[5] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. Bert: Pre-training of deep bidirectional transformers for language understanding. In Proceedings ofthe 2019 Conference ofthe North American chapter ofthe Association for Computational Linguistics: Human Language Technologies. 4171–4186.

[6] Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, and Neil Houlsby. 2021. An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. arXiv:2010.11929 [cs.CV] https://arxiv.org/abs/2010.11929

[7] Kawin Ethayarajh, Winnie Xu, Niklas Muennighof, Dan Jurafsky, and Douwe Kiela. 2024. Model alignment as prospect theoretic optimization. In Proceedings of the 41st International Conference on Machine Learning (Vienna, Austria) (ICML’24). JMLR.org, Article 504, 18 pages.

[8] Chao Feng, Wuchao Li, Defu Lian, Zheng Liu, and Enhong Chen. 2022. Recom mender forest for eficient retrieval. In Advances in Neural Information Processing Systems.

[9] Shanshan Feng, Xutao Li, Yifeng Zeng, Gao Cong, Yeow Meng Chee, and Quan Yuan. 2015. Personalized ranking metric embedding for next new POI recommen dation. In Proceedings ofthe 24th International Conference on Artificial Intelligence (Buenos Aires, Argentina) (IJCAI’15). AAAI Press, 2069–2075.

[10] Shanshan Feng, Feiyu Meng, Lisi Chen, Shuo Shang, and Yew Soon Ong. 2024. ROTAN: A Rotation-based Temporal Attention Network for Time-Specific Next POI Recommendation. In Proceedings ofthe 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (Barcelona, Spain) (KDD ’24). Association for Computing Machinery, New York, NY, USA, 759–770. doi:10.1145/3637528. 3671809

[11] Shijie Geng, Shuchang Liu, Zuohui Fu, Yingqiang Ge, and Yongfeng Zhang. 2022. Recommendation as Language Processing (RLP): A Unified Pretrain, Personalized Prompt & Predict Paradigm (P5). In Proceedings of the 16th ACM Conference on Recommender Systems (Seattle, WA, USA) (RecSys ’22). Association for Computing Machinery, New York, NY, USA, 299–315. doi:10.1145/3523227.3546767

[12] William L. Hamilton, Rex Ying, and Jure Leskovec. 2017. Inductive representation learning on large graphs. In Advances in Neural Information Processing Systems. 1025–1035.

[13] Peibo Li, Maarten de Rijke, Hao Xue, Shuang Ao, Yang Song, and Flora D. Salim. 2024. Large Language Models for Next Point-of-Interest Recommen dation. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval (Washington DC, USA) (SIGIR ’24). Association for Computing Machinery, New York, NY, USA, 1463–1472. doi:10.1145/3626772.3657840

[14] Yan Luo, Haoyi Duan, Ye Liu, and Fu-Lai Chung. 20

### 在线资源

- [论文：arXiv 2607.26073](https://arxiv.org/abs/2607.26073)
- [代码：GitHub](https://github.com/alibaba/SimCIT)
- [PDF源文件](/papers/2607.26073.pdf)
