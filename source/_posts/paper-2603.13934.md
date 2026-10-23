---

title: "面向大语言模型生成式推荐的从个体兴趣到群体兴趣的迭代语义推理"

date: 2026-03-14

year: 2026

venue_type: 会议

venue_name: WWW 2026

categories: ["推荐系统", "生成式推荐"]

tags: ["论文速读", "语义推理", "用户兴趣建模", "图神经网络", "LightGCN", "对比学习", "迭代优化", "链式思维"]

slug: "paper-2603.13934"

---

[论文链接](https://arxiv.org/pdf/2603.13934.pdf) · [代码链接](https://github.com/htired/ISRF)

## 一、研究背景与问题

推荐系统的目标是从用户历史行为中学习兴趣并推荐相关物品。早期方法仅依赖点击物品的 ID 序列建模用户兴趣，忽略了物品语义信息，限制了对用户兴趣的准确理解。随后一类研究引入品牌、价格等侧信息，在小规模模型内设计专门组件融合语义特征（如 MoRec、LSMRec、CaFe、ESIF），但受限于模型参数与知识容量，语义表示能力有限。另一类研究引入具备强表示能力的大语言模型（LLM），用其编码用户与物品语义并结合 ID 特征表示用户兴趣（如 LLMEmb、SLMRec、POD、ELMRec），取得了不错效果。

然而，根据用户行为理论，仅靠语义表示往往不足以揭示用户真实兴趣，挖掘深层偏好通常需要基于语义理解进行逐步推理。论文以篮球鞋为例说明：用户点击具有气垫中底、耐磨防滑外底等特征的篮球鞋，其显式兴趣可推断为在硬地球场需要高缓震性能；但这尚不能揭示更深层兴趣——在行为相似的用户群体中，许多人更看重长时间比赛或训练中的透气性与轻量设计以保持舒适和耐力。识别这种群体层面的隐式兴趣，才能更精准地推荐更合适的物品。这种从物品属性推断显式兴趣、再通过相似用户群体发现隐式需求的逐步推理过程，能带来对用户兴趣更全面的理解，但如何有效模拟这一推理过程仍是重要挑战。

为此，论文提出迭代语义推理框架 ISRF（Iterative Semantic Reasoning Framework）用于生成式推荐，通过三个协同模块用 LLM 连接显式个体兴趣与隐式群体兴趣：（1）个体兴趣推理模块，对物品属性进行多步双向推理以推断语义物品特征，并构建捕捉用户显式兴趣的语义交互图；（2）群体兴趣推理模块，基于语义物品特征生成语义用户特征，并构建基于相似度的用户图以推断相似用户群体的隐式兴趣；（3）迭代精炼模块，采用迭代批量优化策略，让个体显式兴趣直接指导群体隐式兴趣的精炼，而精炼后的群体兴趣反过来增强个体偏好建模。该三阶段过程保证了从显式到隐式兴趣的一致、渐进式语义推理。论文主要贡献包括：提出从显式个体兴趣与隐式群体兴趣进行推理的新语义推理视角；实现从显式个体兴趣到隐式群体兴趣的语义推理并通过迭代精炼模块逐步优化推理过程；在多个数据集上的大量实验表明模型持续优于现有 SOTA 方法。

![背景图 1](/images/4c0b2626d3318f2d37ffa20a23384363.png)

该图对比了“语义整合”思路与本文提出的 ISRF“语义推理”思路。左侧展示仅依赖语义表示难以揭示深层偏好；右侧以篮球鞋为例，说明从物品属性（气垫中底、耐磨防滑外底）推断显式兴趣（硬地球场高缓震需求），再借助相似用户群体推断隐式兴趣（长时间比赛中的透气与轻量需求），从而推荐更合适的物品。

## 二、方法

ISRF 的整体架构包含三个关键组件：个体兴趣推理（IIR）、群体兴趣推理（GIR）与迭代精炼（IR）。

问题定义方面，ISRF 同时处理两类核心推荐任务：序列推荐（给定用户历史交互序列，预测下一个可能交互的物品）与直接推荐（由随机采样的一个正样本物品和若干负样本物品构成候选集，要求 LLM 根据用户偏好识别正样本）。为统一处理两类任务，定义输入与输出 token 序列，每个输入 token 关联索引形成索引序列；将可学习提示嵌入与输入嵌入拼接，最终输入为 X̃ = X_p + β·X_ω(Z)，其中 β 控制整词嵌入 X_ω(Z) 的贡献，X_ω 在序列推荐与直接推荐任务下分别采用物品整词嵌入序列与用户/物品整词嵌入序列，ω_0 为非 ID token（如提示）的共享嵌入。

（a）个体兴趣推理（IIR）：以往方法对物品属性的语义推理利用不足。ISRF 采用链式思维（CoT）机制引导 LLM 对物品进行多步推理：先基于物品结构化属性进行前向推理，生成正描述 I_se^pos（如“哪些类型的用户可能喜欢该物品”）；再以 I_se^pos 为条件进行后向推理，生成负描述 I_se^neg（如“哪些类型的用户可能不喜欢该物品”）；最后融合两者形成更多样、可解释的语义描述 I_se。为避免直接用增强后的物品语义特征 S_v 作为初始物品嵌入破坏原有语义结构，先用 PCA 将其降维为 S̃_v 并在训练中冻结，再通过适配器映射到推荐空间得到最终物品嵌入 E_v = W_2(W_1·S̃_v + b_1) + b_2。在此基础上，在用户-物品交互图 G 上应用 LightGCN 建模用户显式兴趣，逐层传播为 E^{l+1} = D^{-1/2} A D^{-1/2} E^l，最终嵌入取各层平均 Ẽ = (1/(L+1))ΣE^l，其中包含用户显式兴趣与物品上下文语义。为将增强嵌入整合进 LLM，用 ẽ_v、ẽ_u 替换提示构造中的整词嵌入。

（b）群体兴趣推理（GIR）：仅依赖个体交互历史中的物品语义特征不足以捕捉潜在用户兴趣，因为行为相似的用户常共享偏好。该模块先从每个用户交互历史中随机采样部分物品，引导 LLM 生成正向兴趣描述 P_se^pos，再以其为上下文提示推断互补的负向兴趣描述 P_se^neg，最终用户兴趣描述 P_se 融合两种视角。随后基于 LLM 增强的语义嵌入 S_u 构建用户关系图，生成语义关系矩阵 R：若 u_j 属于与 u_i 最相似的前 k 个用户则 R_{i,j}=1，否则为 0，相似度采用余弦相似度，Top-k 选择可降低计算复杂度。再在 R 上使用 LightGCN 聚合邻域信息精炼用户表示，H^{(l)} = D_R^{-1/2} R D_R^{-1/2} H^{(l-1)}，最终表示 H 为各层平均，包含群体隐式兴趣。

（c）迭代精炼（IR）：独立建模 IIR 与 GIR 可能导致表示不一致并限制互补性。在直接到序列表示对齐阶段，以个体显式兴趣表示 ẽ_u 作为监督信号指导群体隐式兴趣表示 h_u 的优化，采用对比蒸馏损失 L_{D→S}，其中使用温度缩放的余弦相似度 f_c 并对教师信号做 stop-gradient；在序列表示对齐阶段，通过最大化 h_u 与用户偏好 e_u^p 之间的互信息增强 e_u^p 的表达能力，采用对比损失 L_S，其中 e_u 由交互序列中物品整词嵌入平均得到。

优化与推理：采用联合损失，直接推荐任务为 L_gen + L_{D→S}，序列推荐任务为 L_gen + L_S，其中 L_gen 为文本生成损失（逐 token 负对数似然）。推理阶段沿用 ELMRec 的做法，采用束搜索从词表中选择似然最高的词生成结果。

![方法图 1](/images/ffc33f4c09ba6e733b6136bb63e75385.png)

ISRF 整体架构图，包含三个部分：(a) 个体兴趣推理，通过 LLM 多步双向推理生成物品语义并经 PCA 与适配器映射，再用 LightGCN 在交互图上建模显式兴趣；(b) 群体兴趣推理，基于语义用户嵌入构建相似用户关系图并用 LightGCN 聚合邻域信息；(c) 迭代精炼，通过对比蒸馏与对比损失在显式与隐式兴趣之间交替对齐优化。

![方法图 2](/images/dcd348fbbeb02017d6f183be1dfce290.png)

Sports 数据集上的物品语义推理提示示例，展示如何用链式思维引导 LLM 先做前向推理生成正向描述、再做后向推理生成负向描述，并融合为物品语义特征。

![方法图 3](/images/843c4eb9b0a30a7e2d966e8925507f0b.png)

Sports 数据集上的用户语义推理提示示例，展示如何从用户交互历史中采样物品，引导 LLM 生成正向与负向兴趣描述并融合为最终用户兴趣语义。

## 三、实验

实验在 Sports & Outdoors、Beauty、Toys & Games 三个广泛使用的基准数据集上进行，采用与已有工作相同的数据预处理与划分协议（每个用户最后一次交互用于测试、倒数第二次用于验证、其余用于训练）。对比 14 个主流基线，分为四类：传统推荐方法（SimpleX、Caser、GRU4Rec、HGN）、基于注意力的方法（SASRec、BERT4Rec、FDSA）、基于 GNN 的方法（LightGCN、NCL、XSimGCL）以及基于 LLM 的方法（P5、RSL、POD、ELMRec）。实现上采用 DeepSeek-R1-14B 作为骨干 LLM 执行多步语义推理，采用 EasyRec 作为语义嵌入提取模块；直接推荐中训练与评估的负样本数设为 99，批大小为 64，早停耐心为 5 个 epoch；P5、POD、ELMRec 与 ISRF 均采用 T5-small 作为骨干语言模型；评价指标为 Top-k 命中率 H@k 与 NDCG@k（k∈{5,10}），实验在单张 24GB 显存的 NVIDIA GeForce RTX 4090 上完成。

RQ1 整体性能：序列推荐任务中，ISRF 在所有数据集上持续超越所有基线，相对 ELMRec 提升 3.71% 至 10.37%，增益归因于建模隐式用户兴趣的群体兴趣推理模块以及跨粒度优化用户表示的迭代精炼机制；直接推荐任务中，ISRF 相对最强基线 ELMRec 取得 7.52% 至 24.57% 的提升，主要得益于个体兴趣推理模块对物品语义与细粒度显式兴趣的捕捉，且直接推荐任务上表现更强，可能因为该任务更依赖对未见物品的理解，凸显语义建模的重要性。

RQ2 消融研究：序列推荐中移除 L_{D→S} 导致明显性能下降，说明显式兴趣对指导群体隐式兴趣学习的重要性；移除 L_S 同样使性能下降，因为 LLM 仅依赖用户与物品 ID 而缺乏语义增强。直接推荐中引入物品语义 I_se 可改善物品理解，而移除可训练适配器显著削弱性能，凸显其在对齐语义空间与推荐空间中的作用。

RQ3 语义变体：设计 ISRF-uPos、ISRF-uNeg、ISRF-vPos、ISRF-vNeg 等变体，完整模型在两类任务上均持续优于所有语义变体，验证了整合正负两种视角的多角度语义推理的重要性；同时负向语义变体与正向变体性能相近，说明正负语义视角对用户兴趣建模贡献相当，可作为有效的语义互补。

RQ4 超参数敏感性：随着 LightGCN 层数 L' 增加，两类任务性能先提升，超过一定程度后趋于平稳或略有下降，说明适度的传播深度有助于捕捉隐式用户兴趣，但过多层可能导致过平滑或噪声累积。附录中进一步分析 Top-k 相似用户数 k：性能随 k 增大先升后降，序列推荐在三个数据集上 k=100 时最佳；直接推荐在 Beauty 与 Toys 上最优 k 为 100，在 Sports 上为 50，说明引入更多相似用户有益于偏好建模，但过大的 k 可能引入噪声并降低准确率。

RQ5 计算复杂度：ISRF 的复杂度主要来自 Transformer 的 O(m^2) 与 LightGCN 的 O(n^2)，由于 m≪n，整体复杂度由 O(n^2) 主导，与 ELMRec 相同。实际运行时间分析显示，ISRF 消耗的计算资源与 ELMRec 相当（训练时间略长、显存占用略高，推理时间相近），但取得更好性能。

RQ6 案例研究：以用户 u_10 为例，ELMRec 主要推荐配件类物品（如 Match Container Kit、Ball Pump Kit），而 ISRF 识别出用户对 Cycling、Lights、Headlights 等类别的兴趣；借助与语义相似用户（如 u_10043 与 u_30259，曾交互 Taillights、Cycling、Headlights 类物品）的行为，ISRF 推断出用户对 Headlights 的隐式兴趣，从而推荐 Bicycle Light、Bicycle Headlight Torch 等更相关物品，展示了其在建模群体级语义偏好方面的优势。

![实验图 1](/images/6a05fe494a877df30044e39757708c4e.png)

直接推荐任务下 ISRF 与各语义变体（仅用正向/负向用户语义、仅用正向/负向物品语义）的性能对比，完整模型表现最佳，说明正负两种语义视角的融合具有互补价值。

![实验图 2](/images/bc63351e9beb718f345382b042f39b07.png)

序列推荐任务下 ISRF 与各语义变体的性能对比，同样显示完整模型优于仅使用单一正向或负向语义的变体，验证多视角语义推理的必要性。

![实验图 3](/images/f0c2a31e1ad4f66aedb4a3b76118cc62.png)

直接推荐任务中关于群体兴趣推理所用 LightGCN 层数 L' 的超参数敏感性曲线之一，展示不同层数下的性能变化趋势。

![实验图 4](/images/bd1f883b4e4a04fc7ae1653c04ab486e.png)

直接推荐任务中 LightGCN 层数 L' 超参数研究的另一组结果曲线，用于观察传播深度对性能的影响。

![实验图 5](/images/9a35c7df07093313b29e99c0028fb50a.png)

直接推荐任务中不同 L' 取值下的性能对比图，配合其他子图共同说明层数增加先提升后趋稳或下降的现象。

![实验图 6](/images/d8d4151a440bdeb7323c68120577517c.png)

直接推荐任务中 L' 超参数研究的补充曲线，展示不同数据集上性能随层数的变化。

![实验图 7](/images/a8a949046d4ef9d1f0ff1144a2d707c6.png)

直接推荐任务中 L' 超参数研究的又一组结果，整体表明适度传播深度有助于捕捉隐式兴趣，过深则可能过平滑。

![实验图 8](/images/66a01883955d709387426ff1ac8dde3c.png)

序列推荐任务中 LightGCN 层数 L' 的超参数敏感性结果，性能随层数先升后平稳或略降，说明层数选择需要权衡。

![实验图 9](/images/1e6f73316fa8f28b1055ef5ad3599c0b.png)

用户 u_10 的案例研究：ELMRec 主要推荐配件类物品，而 ISRF 借助语义相似用户（如 u_10043、u_30259）在 Taillights、Cycling、Headlights 等类别的行为，推断出用户对车灯的隐式兴趣，从而推荐 Bicycle Light、Bicycle Headlight Torch 等更相关物品。

![实验图 10](/images/234967e0cd9f59113f3695382b45622a.png)

附录中 Top-k 相似用户数 k 的超参数敏感性结果之一，展示性能随 k 增大先升后降的趋势。

![实验图 11](/images/852a6d6ef57b3720b11548f225fc04dc.png)

Top-k 超参数研究的补充曲线，用于说明不同数据集上最优 k 取值的差异。

![实验图 12](/images/e24de3aadc7f741a3223b06f53994593.png)

Top-k 超参数研究的又一组结果，整体表明较大的相似用户集合有益于偏好建模，但过大会引入噪声。

![实验图 13](/images/531a8556ed4d7ce21e87a5c45bbdd5fd.png)

Top-k 超参数敏感性结果之一，配合其他子图说明 k 的取值对推荐性能的影响。

![实验图 14](/images/cbc7f16ad08d91c3345335cf6e8a164d.png)

直接推荐任务下 Top-k 相似用户数 k 的超参数研究结果，显示 Beauty 与 Toys 上最优 k 为 100、Sports 上为 50。

![实验图 15](/images/671cd3b0a4da0495c5bb872418b1b0e1.png)

序列推荐任务下 Top-k 相似用户数 k 的超参数研究结果，三个数据集上均在 k=100 时取得最佳性能。

## 四、总结

论文提出了用于推荐的迭代兴趣推理框架 ISRF，利用 LLM 通过三个协同模块执行从个体显式兴趣到群体隐式兴趣的语义推理：个体兴趣推理模块推断语义物品特征并构建语义交互图以学习个体显式兴趣；群体兴趣推理模块构建基于相似度的用户图以捕捉相似用户群体的隐式兴趣；迭代精炼模块交替优化两类兴趣以保证一致且渐进的推理。在三个真实数据集上的大量实验表明，ISRF 持续优于现有最先进基线。未来工作将进一步引入多样化推理策略以增强 LLM 的推理能力。

## References

- Keqin Bao, Jizhi Zhang, Xinyu Lin, Yang Zhang, Wenjie Wang, and Fuli Feng. 2024. Large language models for recommendation: Past, present, and future. In SIGIR. 2993–2996.

- Zheng Chu, Jingchang Chen, Qianglong Chen, Weijiang Yu, Tao He, Haotian Wang, Weihua Peng, Ming Liu, Bing Qin, and Ting Liu. 2023. Navigate through enigmatic labyrinth a survey of chain of thought reasoning: Advances, frontiers and future. arXiv preprint arXiv:2309.15402.

- Zhixuan Chu, Hongyan Hao, Xin Ouyang, Simeng Wang, Yan Wang, Yue Shen, Jinjie Gu, Qing Cui, Longfei Li, Siqiao Xue, et al. 2023. Leveraging large language models for pre-trained recommender systems. arXiv preprint arXiv:2308.10837.

- Shijie Geng, Shuchang Liu, Zuohui Fu, Yingqiang Ge, and Yongfeng Zhang. 2022. Recommendation as language processing (rlp): A unified pretrain, personalized prompt & predict paradigm (p5). In RecSys. 299–315.

- Jonathan Gutman. 1982. A means-end chain model based on consumer categorization processes. Journal of Marketing, 60–72.

- Xiangnan He, Kuan Deng, Xiang Wang, Yan Li, Yongdong Zhang, and Meng Wang. 2020. Lightgcn: Simplifying and powering graph convolution network for recommendation. In SIGIR. 639–648.

- Balázs Hidasi, Alexandros Karatzoglou, Linas Baltrunas, and Domonkos Tikk. 2015. Session-based recommendations with recurrent neural networks. arXiv preprint arXiv:1511.06939.

- Wang-Cheng Kang and Julian McAuley. 2018. Self-attentive sequential recommendation. In ICDM. 197–206.

- Jiacheng Li, Tong Zhao, Jin Li, Jim Chan, Christos Faloutsos, George Karypis, Soo-Min Pantel, and Julian McAuley. 2022. Coarse-to-fine sparse sequential recommendation. In SIGIR. 2082–2086.

- Lei Li, Yongfeng Zhang, and Li Chen. 2023. Prompt distillation for efficient llm-based recommendation. In CIKM. 1348–1357.

- Jianghao Lin, Xinyi Dai, Yunjia Xi, Weiwen Liu, Bo Chen, Hao Zhang, Yong Liu, Chuhan Wu, Xiangyang Li, Chenxu Zhu, et al. 2025. How can recommender systems benefit from large language models: A survey. ACM Transactions on Information Systems, 1–47.

- Zihan Lin, Changxin Tian, Yupeng Hou, and Wayne Xin Zhao. 2022. Improving graph collaborative filtering with neighborhood-enriched contrastive learning. In WWW. 2320–2329.

- Qidong Liu, Xian Wu, Wanyu Wang, Yejing Wang, Yuanshao Zhu, Xiangyu Zhao, Feng Tian, and Yefeng Zheng. 2025. LLMEmb: Large Language Model Can Be a Good Embedding Generator for Sequential Recommendation. In AAAI. 12183–12191.

- Qidong Liu, Xian Wu, Yejing Wang, Zijian Zhang, Feng Tian, Yefeng Zheng, and Xiangyu Zhao. 2024. LLM-ESR: Large Language Models Enhancement for Long-tailed Sequential Recommendation. In NIPS.

- Chen Ma, Peng Kang, and Xue Liu. 2019. Hierarchical gating networks for sequential recommendation. In SIGKDD. 825–833.

- Qiyao Ma, Xubin Ren, and Chao Huang. 2024. XRec: Large Language Models for Explainable Recommendation. In EMNLP. 391–402.

- Kelong Mao, Jieming Zhu, Jinpeng Wang, Quanyu Dai, Zhenhua Dong, Xi Xiao, and Xiuqiang He. 2021. SimpleX: A simple and strong baseline for collaborative filtering. In CIKM. 1243–1252.

- Karl Pearson. 1901. LIII. On lines and planes of closest fit to systems of points in space. The London, Edinburgh, and Dublin Philosophical Magazine and Journal of Science, 559–572.

- Yingtao Peng, Chen Gao, Yu Zhang, Tangpeng Dan, Xiaoyi Du, Hengliang Luo, Yong Li, and Xiaofeng Meng. 2025. Denoising alignment with large language model for recommendation. ACM Transactions on Information Systems 43, 1–35.

- J Paul Peter and Jerry C Olson. 2010. Consumer behavior & marketing strategy. McGraw-Hill.

- Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J Liu. 2020. Exploring the limits of transfer learning with a unified text-to-text transformer. Journal of Machine Learning Research, 1–67.

- Xubin Ren and Chao Huang. 2024. EasyRec: Simple yet effective language models for recommendation. arXiv preprint arXiv:2408.08821.

- Xubin Ren, Wei Wei, Lianghao Xia, Lixin Su, Suqi Cheng, Junfeng Wang, Dawei Yin, and Chao Huang. 2024. Representation learning with large language models for recommendation. In WWW. 3464–3475.

- Steffen Rendle, Christoph Freudenthaler, and Lars Schmidt-Thieme. 2010. Factorizing personalized markov chains for next-basket recommendation. In WWW. 811–820.

- Thomas J Reynolds and Jonathan Gutman. 2001. Laddering theory, method, analysis, and interpretation. In Understanding Consumer Decision Making. Psychology Press, 40–79.

- Zheng-Ang Su, Juan Zhang, Zhijun Fang, and Yongbin Gao. 2025. Enhanced side information fusion framework for sequential recommendation. International Journal of Machine Learning and Cybernetics, 1157–1173.

- Fei Sun, Jun Liu, Jian Wu, Changhua Pei, Xiao Lin, Wenwu Ou, and Peng Jiang. 2019. BERT4Rec: Sequential recommendation with bidirectional encoder representations from transformer. In CIKM. 1441–1450.

- Fei Tang, Yongliang Shen, Hang Zhang, Zeqi Tan, Wenqi Zhang, Zhibiao Huang, Kaitao Song, Weiming Lu, and Yueting Zhuang. 2024. GaVaMoE: Gaussian-Variational Gated Mixture of Experts for Explainable Recommendation. arXiv preprint arXiv:2410.11841.

- Jiaxi Tang and Ke Wang. 2018. Personalized top-n sequential recommendation via convolutional sequence embedding. In WSDM. 565–573.

- Hadise Vaghari, Mehdi Hosseinzadeh Aghdam, and Hojjat Emami. 2025. Group attention for collaborative filtering with sequential feedback and context aware attributes. Scientific Reports, 10050.

- Qi Wang, Jindong Li, Shiqi Wang, Qianli Xing, Runliang Niu, He Kong, Rui Li, Guodong Long, Yi Chang, and Chengqi Zhang. 2024. Towards next generation llm-based recommender systems: A survey and beyond. arXiv preprint arXiv:2410.19744.

- Xinfeng Wang, Jin Cui, Fumiyo Fukumoto, and Yoshimi Suzuki. 2024. Enhancing High-order Interaction Awareness in LLM-based Recommender Model. In EMNLP.

- Xinfeng Wang, Jin Cui, Yoshimi Suzuki, and Fumiyo Fukumoto. 2024. RDRec: Rationale Distillation for LLM-based Recommendation. In ACL (Volume 2: Short Papers). 65–74.

- Xiang Wang, Xiangnan He, Meng Wang, Fuli Feng, and Tat-Seng Chua. 2019. Neural graph collaborative filtering. In SIGIR. 165–174.

- Lianghao Xia, Chao Huang, Chunzhen Huang, Kangyi Lin, Tao Yu, and Ben Kao. 2023. Automated self-supervised learning for recommendation. In WWW. 992–1002.

- Wujiang Xu, Qitian Wu, Zujie Liang, Jiaojiao Han, Xuying Ning, Yunxiao Shi, Wenfang Lin, and Yongfeng Zhang. 2025. SLMRec: Distilling Large Language Models into Small for Sequential Recommendation. In ICLR.

- Xihong Yang, Heming Jing, Zixing Zhang, Jindong Wang, Huakang Niu, Shuaiqiang Wang, Yu Lu, Junfeng Wang, Dawei Yin, Xinwang Liu, et al. 2024. Darec: A disentangled alignment framework for large language model and recommender system. arXiv preprint arXiv:2408.08231.

- Junliang Yu, Xin Xia, Tong Chen, Lizhen Cui, Nguyen Quoc Viet Hung, and Hongzhi Yin. 2023. XSimGCL: Towards extremely simple graph contrastive learning for recommendation. IEEE Transactions on Knowledge and Data Engineering, 913–926.

- Zheng Yuan, Fajie Yuan, Yu Song, Youhua Li, Junchen Fu, Fei Yang, Yunzhu Pan, and Yongxin Ni. 2023. Where to go next for recommender systems? id-vs. modality-based recommender models revisited. In SIGIR. 2639–2649.

- Haoyu Zhang and Wenfang Li. 2024. LSMRec: Leveraging Hash-Enhanced Semantic Mapping for Superior Sequential Recommendations. In ICTAI. 166–173.

- Tingting Zhang, Pengpeng Zhao, Yanchi Liu, Victor S Sheng, Jiajie Xu, Deqing Wang, Guanfeng Liu, Xiaofang Zhou, et al. 2019. Feature-level deeper self attention network for sequential recommendation. In IJCAI. 4320–4326.

- Xin Zhou. 2023. Mmrec: Simplifying multimodal recommendation. In MMAsia. 1–2.
