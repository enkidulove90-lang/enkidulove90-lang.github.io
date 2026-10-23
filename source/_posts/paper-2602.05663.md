---

title: "面向生成式推荐的由粗到细长期兴趣建模"

date: 2026-02-05

year: 2026

venue_type: arXiv预印本

venue_name: arXiv

categories: ["推荐系统", "生成式推荐"]

tags: ["论文速读"]

slug: "paper-2602.05663"

---

[论文链接](https://arxiv.org/pdf/2602.05663.pdf)

## 一、研究背景与问题

生成式推荐（GR）将推荐重新表述为在层次化语义 ID（SID）上的自回归生成任务，能够借助 Transformer 的序列建模能力直接刻画复杂的用户—物品关联。然而注意力机制的二次复杂度使现有 GR 模型通常只能处理较短的交互序列，难以利用用户长期历史中蕴含的丰富信号。工业界常用 SIM 式的两阶段范式（先搜索相关子序列再做重注意力）来缓解长序列建模的噪声与开销，但已有将搜索式方法引入生成式推荐的工作忽略了 SID 的层次结构差异。

本文的核心观察是：GR 本质上是一个由粗到细的生成过程——前几个 SID（前缀）决定目标物品的粗粒度语义类别，后续 SID（后缀）则在该类别内定位具体物品。因此前缀与后缀的生成需要注入不同形态的长期信号：前缀生成时尚无已建立的路径，需要主动注入全局长期兴趣；后缀生成时首个 SID 已确定，可作为语义触发器约束搜索空间，从而以已生成前缀为键从历史中检索相关信息。

基于此，作者提出 GLASS 框架，通过 SID-Tier 与语义搜索将长期用户兴趣注入生成过程：针对首级 SID 引入 SID-Tier 模块，将长期交互映射为统一兴趣向量以增强初始 token 的预测；针对后续 SID 提出语义硬搜索，以生成的粗粒度语义 ID 作为动态键抽取相关历史行为，并通过自适应门控融合模块校准后续细粒度 token 的生成轨迹。作者还指出语义硬搜索存在信息稀缺瓶颈，并提出语义邻居增强与码本重缩放两种缓解策略。论文的主要贡献包括：提出将长期行为信号注入生成式推荐框架的 GLASS；提出用于精化首级 SID 生成的 SID-Tier 模块；提出以生成 SID 为键在长期历史中检索的语义硬搜索；并在两个真实数据集上验证了方法优于当前最优基线。

## 二、方法

GLASS 采用编码器—解码器架构，包含三个主要组件：增强首 token 预测的 SID-Tier 模块、用于细粒度轨迹校准的语义硬搜索模块，以及为后续细粒度生成提供充足信息增益的稀疏感知增强策略。

（1）SID-Tier。由于初始 token 的生成缺乏前序轨迹，SID-Tier 通过层级感知的量化机制将长期历史交互聚合为上下文向量，作为“冷启动”引导。首先进行原型对齐：为第一级码本 C0 中的每个码字 k 分配原型嵌入，该原型由属于该簇的所有物品嵌入均值池化得到，从而保证每个码字的表示在其对应物品簇内语义居中。其次构建兴趣直方图：计算原型与用户长期历史中每个物品的余弦相似度，将相似度区间 [-1,1] 离散为 N 个层级，对每个码字统计历史物品落入各相似度层级的频次，形成统一兴趣向量。最后进行全局注入：将所有第一级码字的兴趣向量拼接成用户兴趣热力图，经 MLP 展平投影为与 token 空间对齐的向量，并追加到用户短期序列嵌入之后送入编码器，使初始 token 的生成以全局长期偏好为条件。

（2）基于语义搜索的解码。利用 RQ-VAE 生成的层次化语义 ID，第一级码字表示粗粒度语义桶并天然具有聚类性质，第二、三级码字表示逐步逼近物品唯一标识的细粒度语义。在自回归解码中，模型生成首个码字后，以该已确定的粗粒度意图作为语义键在用户长期历史中执行硬搜索，构造仅包含与生成首级码字相同的历史物品的检索序列，相当于为解码器提供检索增强生成的上下文窗口；与基于稠密向量相似度的常规 RAG 不同，该方式依据粗粒度意图的显式语义对齐过滤历史，显著降低无关噪声干扰。随后解码器采用两个并行的交叉注意力模块分别构建短期视图与检索视图：短期视图捕捉近期交互的序列模式与即时意图，检索视图聚合与当前生成语义相关的长期偏好。为有效融合两种视图，引入门控作为自验证模块，通过投影拼接表示计算标量门控值，并以加权求和得到最终上下文向量：门控值较大时强调检索到的长期语义，较小时抑制检索并依赖短期行为。上下文向量经前馈网络、残差连接与层归一化处理后得到当前解码层的最终隐状态，堆叠多层后经线性头投影到码本空间并计算码字概率分布，训练目标为层次化码字序列上的负对数似然损失。

（3）稀疏感知增强。基于首级 SID 的语义硬搜索可能面临子序列稀疏问题：例如序列长度为 1000、第一级码本大小为 128 时，每个 SID 平均仅检索到约 7.8 个历史物品，上下文窗口有限且易受噪声影响。为此提出两种互补策略：其一是语义邻居增强，基于残差量化学到的码嵌入计算第一层所有码字的两两余弦相似度，为每个码字预计算 top-k 最近语义邻居构成静态字典；生成过程中若检索集合长度低于预设阈值，则触发邻居增强协议，将首级 SID 的最近邻居及其关联历史物品合并进检索集合，在保持语义一致性的同时提升序列长度与信息密度。其二是码本重缩放，在训练时约束第一级码本大小，迫使模型将更广范围的物品聚合到每个 SID 桶中，从而大幅提升每个桶的平均物品数，保证检索上下文具备足够的信息量；通过解耦层级职责——将密度分配给主层、将精度留给后续层——有效缓解稀疏瓶颈。

![方法图 1](/images/358490f771fd80c3206e998e718f83b8.png)

该图展示 GLASS 框架的整体架构。子图 (a) 为编码器—解码器结构：编码器处理短期物品序列与 SID-Tier 特征以刻画用户兴趣，解码器通过双交叉注意力整合编码器输出与语义搜索结果。子图 (b) 说明 SID-Tier 如何将长期历史聚合为统一兴趣向量，以增强首个码字（sid1）的预测。子图 (c) 展示语义硬搜索：以已生成的 sid1 为键执行硬搜索，再经门控增强细粒度 token（sid2、sid3）的生成；稀疏感知增强通过引入语义邻居或重缩放码本保证上下文信息充分。

## 三、实验

实验在 TAOBAO-MM 与 KuaiRec 两个真实数据集上进行。由于两数据集原本面向排序任务，作者将其改造为长序列检索设定，仅将正反馈交互作为输入序列：TAOBAO-MM 保留有点击的用户—物品交互，KuaiRec 选取观看比例（播放时长/视频时长）超过 100% 的样本。针对 TAOBAO-MM 的大物品词表，先均匀采样 10000 个物品，再仅保留在训练集中出现至少五次的物品；参照 MUSE 的配置，将每个用户最近 50 次交互作为短期序列，更早的交互归入长期历史。处理后 TAOBAO-MM 含 189423 名用户、10000 个物品、265301 条训练样本，平均历史序列长度 987；KuaiRec 含 3790 名用户、10728 个物品、30320 条训练样本，平均历史序列长度 884。

实现细节方面，SID 类与 ID 类模型共享配置包括：嵌入表维度 96、dropout 0.1、AdamW 优化器学习率 1e-4、短序列长度 50、早停耐心 50、8 个注意力头、键/值维度 32。任务特定配置：SID 类模型使用语义 token 输入，码本结构为 [64,128,128]，SID-tier MLP 维度 256，4 个编码器/解码器块；ID 类模型使用原子物品 ID，20 个负样本，2 个编码器/解码器块。评价指标为 Recall@K 与 NDCG@K。基线分为两组：ID 类检索基线包括 Caser、HGN、GRU4Rec、SASRec、Bert4Rec、S3-Rec、HSTU；SID 类检索基线包括 Tiger 与 DualGR。

整体性能对比（RQ1）显示，GLASS 在两个数据集的所有指标上均持续优于全部基线。与最强基线相比，在 Taobao-MM 上 H@1 与 N@3 的相对提升最高分别达 21.57% 与 29.91%。作者将优势归因于：相比传统序列推荐方法更充分地利用长期行为序列；相比同样引入长序列信息的 DualGR，SID-Tier 通过显式建模目标感知交互提供了比简单平均池化更丰富的信息，且每层采用更精细的融合策略而非单一交叉注意力，使瞬时意图与持久偏好得到更好整合。作者还观察到 Taobao-MM 上的增益比 KuaiRec 更明显，原因是前者使用监督对比学习得到的高质量多模态特征、语义对齐更优，而后者多模态信息来自简单文本编码、表示质量较低。

消融研究（RQ2）从训练准确率（教师强制下第 i 层的拟合程度）与推理精度（top-1 束搜索中前缀均正确时第 i 个码正确的条件概率）两个维度分析模块贡献：引入 SID-Tier 带来显著提升，例如 Recall@5 从 0.0702 提升到 0.0842，其根源在于语义 ID 范式的前缀依赖性——SID-Tier 使首级训练准确率从 0.2410 提升到 0.2485，并直接带动首级推理精度从 0.1470 提升到 0.1587；语义硬搜索模块提供互补增益，二者结合显著提升第二级的训练准确率与推理精度，使模型在整条序列上保持高保真，取得最高的 Recall@10 与 NDCG@10。稀疏感知增强的消融显示，码本重缩放显著增强排序能力，GLASS(mode=CR) 取得最高 Recall@10；语义邻居增强在未做码本重缩放的设定下有效，印证其可通过语义邻居扩充检索上下文缓解稀疏瓶颈，但在码本重缩放设定下相较不使用 SN 出现轻微性能下降，作者归因于语义邻居引入的噪声——当码本表示宽泛兴趣簇时，软化搜索空间可能模糊不同用户兴趣之间的边界。

门控机制分析（RQ3）表明，固定权重（如 0.5）在第一级码本较小时可带来提升，但随着码本粒度增大反而导致性能下降，主要原因是检索序列的高方差：推理时若检索序列过短，信噪比显著降低，固定权重下这些噪声信号会直接扭曲后续层束搜索的累积概率，最终损害排序性能。对门控值与检索序列长度的分析显示，两种码本配置（[128,128,128] 与 [64,128,128]）下均呈现一致上升趋势：检索序列越长，平均门控值越高，说明模型学会了在检索序列信息量更大时赋予其更高重要性，验证了门控机制在动态平衡短期与长期兴趣以优化 SID2、SID3 预测方面的有效性。

对语义硬搜索的理论分析（RQ4）采用条件排名进展（CRP）指标，衡量在前缀于前序步骤存活的前提下，正确第 d 级前缀在深度 d 处束内的期望排名。CRP 接近 1 表示高置信度，接近束大小则意味着易受后续检索失败影响。在束大小 20 下，基线 GR 模型在第二层使 CRP 增加 1.25，而语义硬搜索将其限制在 0.98（提升 22%）；在第三层，语义硬搜索将退化降低 31%（从 0.19 降至 0.13）。作者从束搜索的概率链角度解释：基线中上下文是静态的，无法在更细粒度上拉大真实路径与干扰项的概率差距；语义硬搜索动态扩展上下文，以预测的首级 SID 为查询从长期历史中检索相关物品，初始上下文提供宽泛行为信号，检索上下文提供细粒度个人偏好，从而校准转移概率、缓解排名退化。

工业级验证（RQ5）在某短视频推荐平台进行了为期两周的在线 A/B 测试，实验组与对照组各分配约 3%（约 1200 万）用户。结果显示在 95% 置信水平下，实验组总应用使用时长提升 0.056%、人均应用使用时长提升 0.052%，召回率相较基线提升 3 个百分点（绝对值），表明方法在工业推荐场景中具有实际价值。

![实验图 1](/images/1ac190b783f704f3cf06b6de631181bd.png)

该图对比 SID-Tier 与语义硬搜索（SHS）模块在训练准确率与推理精度上的表现，图例分别对应 Vanilla（蓝色）、+SID-Tier（浅蓝）、+SHS（红色）与 GLASS 完整模型（橙色）。可以看出 SID-Tier 主要提升首级码字的拟合与条件精度，SHS 则进一步改善后续层级的指标，二者结合使整条序列的保真度最高。

![实验图 2](/images/169db41ce20b6b28c0517b63d9f4dfce.png)

该图给出稀疏感知增强在不同模式（None、CR、SN、CR+SN）下的消融结果。码本重缩放（CR）显著提升排序能力并取得最高 Recall@10；语义邻居增强（SN）在未重缩放码本时有效，说明其能通过扩充检索上下文缓解语义硬搜索的稀疏瓶颈，但在已重缩放码本的设定下会因引入邻居噪声而略有下降。

![实验图 3](/images/e22f7fcc70270f4b94b175b70514c364.png)

该图展示推理阶段平均门控值与检索序列长度的关系，左右两条曲线分别对应码本配置 [128,128,128] 与 [64,128,128]。两种配置下均呈现随检索序列变长而门控值上升的一致趋势，说明模型学会了在检索上下文信息量更大时赋予长期检索信号更高权重，从而动态平衡短期与长期兴趣。

## 四、总结

本文提出 GLASS——一种旨在生成式推荐系统中有效利用用户长期交互序列的生成式推荐框架，针对现有 GR 系统在处理长行为历史时信息利用不足的核心挑战给出解决方案。作者引入 SID-Tier 模块，促进用户长期历史与语义码本之间的特征交互，通过捕捉全局语义偏好为关键初始 token 的预测提供稳健的全局上下文；进一步提出语义硬搜索，以生成的 SID 作为搜索键校准后续细粒度 token 的生成轨迹；为克服语义搜索中的信息稀缺瓶颈，设计了稀疏感知增强，确保细粒度生成获得信息充分的上下文。在 TAOBAO-MM 与 KuaiRec 数据集上的大量实验表明 GLASS 优于基线方法。未来工作将探索融合跨域长期行为以进一步丰富语义搜索过程。

## References

- Yue Cao, Xiaojiang Zhou, Jiaqi Feng, Peihao Huang, Yao Xiao, Dayao Chen, and Sheng Chen. 2022. Sampling is all you need on modeling long-term user behaviors for CTR prediction. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management. 2974–2983.

- Jianxin Chang, Chenbin Zhang, Zhiyi Fu, Xiaoxue Zang, Lin Guan, Jing Lu, Yiqun Hui, Dewei Leng, Yanan Niu, Yang Song, et al. 2023. TWIN: TWo-stage interest network for lifelong user behavior modeling in CTR prediction at kuaishou. In Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 3785–3794.

- Ben Chen, Xian Guo, Siyuan Wang, Zihan Liang, Yue Lv, Yufei Ma, Xinlong Xiao, Bowen Xue, Xuxin Zhang, Ying Yang, Huangyu Dai, Xing Xu, Tong Zhao, Mingcan Peng, Xiaoyang Zheng, Chao Wang, Qihang Zhao, Zhixin Zhai, Yang Zhao, Bochao Liu, Jingshan Lv, Xiao Liang, Yuqing Ding, Jing Chen, Chenyi Lei, Wenwu Ou, Han Li, and Kun Gai. 2025. OneSearch: A Preliminary Exploration of the Unified End-to-End Generative Framework for E-commerce Search. arXiv:2509.03236 [cs.IR] https://arxiv.org/abs/2509.03236

- Qiwei Chen, Changhua Pei, Shanshan Lv, Chao Li, Junfeng Ge, and Wenwu Ou. 2021. End-to-end user behavior retrieval in click-through rate prediction model. arXiv preprint arXiv:2108.04468 (2021).

- Jiaxin Deng, Shiyao Wang, Kuo Cai, Lejian Ren, Qigen Hu, Weifeng Ding, Qiang Luo, and Guorui Zhou. 2025. Onerec: Unifying retrieve and rank with generative recommender and iterative preference alignment. arXiv preprint arXiv:2502.18965 (2025).

- Kairui Fu, Tao Zhang, Shuwen Xiao, Ziyang Wang, Xinming Zhang, Chenchi Zhang, Yuliang Yan, Junjun Zheng, Yu Li, Zhihong Chen, Jian Wu, Xiangheng Kong, Shengyu Zhang, Kun Kuang, Yuning Jiang, and Bo Zheng. 2025. FORGE: Forming Semantic Identifiers for Generative Retrieval in Industrial Datasets. arXiv:2509.20904 [cs.IR] https://arxiv.org/abs/2509.20904

- Chongming Gao, Shijun Li, Wenqiang Lei, Jiawei Chen, Biao Li, Peng Jiang, Xiangnan He, Jiaxin Mao, and Tat-Seng Chua. 2022. KuaiRec: A Fully-observed Dataset and Insights for Evaluating Recommender Systems. In Proceedings of the 31st ACM International Conference on Information & Knowledge Management (CIKM '22). ACM, 540–550. doi:10.1145/3511808.3557220

- Chengcheng Guo, Kuo Cai, Yu Zhou, Qiang Luo, Ruiming Tang, Han Li, Kun Gai, and Guorui Zhou. 2026. PROMISE: Process Reward Models Unlock Test-Time Scaling Laws in Generative Recommendations. arXiv:2601.04674 [cs.IR] https://arxiv.org/abs/2601.04674

- Chengcheng Guo, Junda She, Kuo Cai, Shiyao Wang, Qigen Hu, Qiang Luo, Guorui Zhou, and Kun Gai. 2025. MISS: Multi-Modal Tree Indexing and Searching with Lifelong Sequential Behavior for Retrieval Recommendation. In Proceedings of the 34th ACM International Conference on Information and Knowledge Management. 5683–5690.

- Balázs Hidasi, Alexandros Karatzoglou, Linas Baltrunas, and Domonkos Tikk. 2016. Session-based Recommendations with Recurrent Neural Networks. arXiv:1511.06939 [cs.LG] https://arxiv.org/abs/1511.06939

- Yupeng Hou, Jianmo Ni, Zhankui He, Noveen Sachdeva, Wang-Cheng Kang, Ed H Chi, Julian McAuley, and Derek Zhiyuan Cheng. 2025. ActionPiece: Contextually Tokenizing Action Sequences for Generative Recommendation. arXiv preprint arXiv:2502.13581 (2025).

- Kalervo Järvelin and Jaana Kekäläinen. 2002. Cumulated gain-based evaluation of IR techniques. ACM Transactions on Information Systems (TOIS) 20, 4 (2002), 422–446.

- Wang-Cheng Kang and Julian McAuley. 2018. Self-Attentive Sequential Recommendation. arXiv:1808.09781 [cs.IR] https://arxiv.org/abs/1808.09781

- Xiaopeng Li, Bo Chen, Junda She, Shiteng Cao, You Wang, Qinlin Jia, Haiying He, Zheli Zhou, Zhao Liu, Ji Liu, et al. 2025. A Survey of Generative Recommendation from a Tri-Decoupled Perspective: Tokenization, Architecture, and Optimization. (2025).

- Zida Liang, Changfa Wu, Dunxian Huang, Weiqiang Sun, Ziyang Wang, Yuliang Yan, Jian Wu, Yuning Jiang, Bo Zheng, Ke Chen, Silu Zhou, and Yu Zhang. 2025. TBGRecall: A Generative Retrieval Model for E-commerce Recommendation Scenarios. arXiv:2508.11977 [cs.IR] https://arxiv.org/abs/2508.11977

- Qijiong Liu, Jieming Zhu, Yanting Yang, Quanyu Dai, Zhaocheng Du, Xiao-Ming Wu, Zhou Zhao, Rui Zhang, and Zhenhua Dong. 2024. Multimodal pretraining, adaptation, and generation for recommendation: A survey. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 6566–6576.

- Chen Ma, Peng Kang, and Xue Liu. 2019. Hierarchical Gating Networks for Sequential Recommendation. arXiv:1906.09217 [cs.IR] https://arxiv.org/abs/1906.09217

- Yue Meng, Cheng Guo, Xiaohui Hu, Honghu Deng, Yi Cao, Tong Liu, and Bo Zheng. 2025. User Long-Term Multi-Interest Retrieval Model for Recommendation. arXiv:2507.10097 [cs.IR] https://arxiv.org/abs/2507.10097

- Qi Pi, Guorui Zhou, Yujing Zhang, Zhe Wang, Lejian Ren, Ying Fan, Xiaoqiang Zhu, and Kun Gai. 2020. Search-based user interest modeling with lifelong sequential behavior data for click-through rate prediction. In Proceedings of the 29th ACM International Conference on Information & Knowledge Management. 2685–2692.

- Shashank Rajput, Nikhil Mehta, Anima Singh, Raghunandan Hulikal Keshavan, Trung Vu, Lukasz Heldt, Lichan Hong, Yi Tay, Vinh Tran, Jonah Samost, et al. 2023. Recommender systems with generative retrieval. Advances in Neural Information Processing Systems 36 (2023), 10299–10315.

- Qin Ren, Zheng Chai, Xijun Xiao, Yuchao Zheng, and Di Wu. 2025. LongRetriever: Towards Ultra-Long Sequence based Candidate Retrieval for Recommendation. arXiv:2508.15486 [cs.IR] https://arxiv.org/abs/2508.15486

- Zihua Si, Lin Guan, ZhongXiang Sun, Xiaoxue Zang, Jing Lu, Yiqun Hui, Xingchao Cao, Zeyu Yang, Yichen Zheng, Dewei Leng, et al. 2024. Twin v2: Scaling ultra-long user behavior sequence modeling for enhanced ctr prediction at kuaishou. In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management. 4890–4897.

- Fei Sun, Jun Liu, Jian Wu, Changhua Pei, Xiao Lin, Wenwu Ou, and Peng Jiang. 2019. BERT4Rec: Sequential Recommendation with Bidirectional Encoder Representations from Transformer. arXiv:1904.06690 [cs.IR] https://arxiv.org/abs/1904.06690

- Jiaxi Tang and Ke Wang. 2018. Personalized Top-N Sequential Recommendation via Convolutional Sequence Embedding. arXiv:1809.07426 [cs.IR] https://arxiv.org/abs/1809.07426

- Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia Polosukhin. 2017. Attention is all you need. Advances in neural information processing systems 30 (2017).

- Zhipeng Wei, Kuo Cai, Junda She, Jie Chen, Minghao Chen, Yang Zeng, Qiang Luo, Wencong Zeng, Ruiming Tang, Kun Gai, and Guorui Zhou. 2025. OneLoc: Geo-Aware Generative Recommender Systems for Local Life Service. arXiv:2508.14646 [cs.IR] https://arxiv.org/abs/2508.14646

- Bin Wu, Feifan Yang, Zhangming Chan, Yu-Ran Gu, Jiawei Feng, Chao Yi, Xiang Rong Sheng, Han Zhu, Jian Xu, Mang Ye, et al. 2025. MUSE: A Simple Yet Effective Multimodal Search-Based Framework for Lifelong User Interest Modeling. arXiv preprint arXiv:2512.07216 (2025).

- Zhongchao Yi, Kai Feng, Xiaojian Ma, Yalong Wang, Yongqi Liu, Han Li, Zhengyang Zhou, and Yang Wang. 2025. DualGR: Generative Retrieval with Long and Short-Term Interests Modeling. arXiv preprint arXiv:2511.12518 (2025).

- Jiaqi Zhai, Lucy Liao, Xing Liu, Yueming Wang, Rui Li, Xuan Cao, Leon Gao, Zhaojie Gong, Fangda Gu, Michael He, et al. 2024. Actions speak louder than words: Trillion-parameter sequential transducers for generative recommendations. arXiv preprint arXiv:2402.17152 (2024).

- Jun Zhang, Yi Li, Yue Liu, Changping Wang, Yuan Wang, Yuling Xiong, Xun Liu, Haiyang Wu, Qian Li, Enming Zhang, Jiawei Sun, Xin Xu, Zishuai Zhang, Ruoran Liu, Suyuan Huang, Zhaoxin Zhang, Zhengkai Guo, Shuojin Yang, Meng-Hao Guo, Huan Yu, Jie Jiang, and Shi-Min Hu. 2025. GPR: Towards a Generative Pre-trained One-Model Paradigm for Large-Scale Advertising Recommendation. arXiv:2511.10138 [cs.IR] https://arxiv.org/abs/2511.10138

- Zuowu Zheng, Ze Wang, Fan Yang, Jiangke Fan, Teng Zhang, Yongkang Wang, and Xingxing Wang. 2025. EGA-V2: An End-to-end Generative Framework for Industrial Advertising. arXiv:2505.17549 [cs.IR] https://arxiv.org/abs/2505.17549

- Guorui Zhou, Jiaxin Deng, Jinghao Zhang, Kuo Cai, Lejian Ren, Qiang Luo, Qianqian Wang, Qigen Hu, Rui Huang, Shiyao Wang, et al. 2025. OneRec Technical Report. arXiv preprint arXiv:2506.13695 (2025).

- Kun Zhou, Hui Wang, Wayne Xin Zhao, Yutao Zhu, Sirui Wang, Fuzheng Zhang, Zhongyuan Wang, and Ji-Rong Wen. 2020. S3-Rec: Self-Supervised Learning for Sequential Recommendation with Mutual Information Maximization. In Proceedings of the 29th ACM International Conference on Information & Knowledge Management (CIKM '20). ACM, 1893–1902. doi:10.1145/3340531.3411954
