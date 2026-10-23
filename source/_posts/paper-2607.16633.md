---

title: "超越固定深度与宽度：优化基于大语言模型的生成式推荐中的文本解码前缀树"

date: "2026-10-23"

year: "2026"

venue_type: "会议"

venue_name: "ACM RecSys 2026"

categories: ["生成式推荐", "大语言模型推荐", "序列推荐"]

tags: ["论文速读", "term ID", "解码前缀树", "约束束搜索", "最小集合覆盖", "GRPO", "变长标识符"]

slug: "paper-2607.16633"

---

[论文链接](https://arxiv.org/abs/2607.16633) · [代码链接](https://github.com/Liu-Jingzhe/BONSAI)

## 一、研究背景与问题

生成式推荐（GR）把推荐建模为序列生成任务：模型自回归地生成下一个物品的标识序列。基于语义 ID 的方法将物品表示离散化为低基数编码，而基于词项（文本）ID 的方法则直接复用自然语言词元（如标题、元数据、关键词），从而更好地保留物品语义并复用大语言模型的开放世界知识。

与开放式文本生成不同，生成式推荐必须“落地”到固定候选集，因此推理阶段依赖在解码前缀树（trie）上执行约束束搜索，以保证输出对应合法物品。然而现有研究主要关注如何生成语义更丰富的词项 ID，却几乎忽略了这些词项所诱导的前缀树结构本身。语义上合理的 ID 仍可能构造出对束搜索极不友好的树，例如根节点附近分支过多，从而直接损害推荐性能。

作者通过实证与理论分析，提出高性能解码树应具备两个性质：（1）自适应、可变长的 ID 长度，使语义丰富的物品获得更长的表示，避免统一长度带来的信息损失；（2）受约束的分支因子，尤其是浅层分支因子，因为早期决策一旦偏离正确路径，正确物品就会被排除在所有束之外。基于此，作者提出 BONSAI（Branching-Optimized Node Structure for Adaptive Identifiers），将词项 ID 与其解码树的构建联合设计，把节点分裂形式化为递归最小集合覆盖问题。实验表明 BONSAI 相对最强基线最高取得 21.6% 的相对提升，并验证了上述结构性质可迁移用于改进已有词项 ID 方法。

## 二、方法

BONSAI 包含四个阶段：特征过滤、前缀树构建、监督学习与强化学习。

特征过滤阶段，作者用大语言模型从物品原始元数据中抽取对推荐有信息量的关键词，并丢弃泛化填充词。与通过标注器扩展语义的已有方法不同，这里只做抽取、不引入新词，从而把性能增益主要归因于解码树结构而非语义增强。过滤后每个物品被表示为一个变长的特征集合。

前缀树构建阶段，内部节点对应共享特征，叶节点对应物品，物品的 ID 即根到叶路径上的关键词序列。对每个物品子集，作者求解一个最小集合覆盖，选出最小的特征集合把当前子集划分为若干子节点，从而在每一层把分支因子压到尽可能低；同时，特征更丰富的物品需要更多次分裂才能被唯一区分，自然被推到更深的层次，形成自适应深度。精确求解可用 CP-SAT 等求解器，但数据规模下代价过高，因此实践中采用贪心近似：每轮选择能覆盖最多未覆盖物品的共享特征，直至全部覆盖。由于同一物品可能与不同物品组共享不同的合法特征组合，该构造天然允许同一物品拥有多条合法根到叶路径。

理论部分给出了三个结论。设物品集为 $I$，目标物品为 $Y$，束宽为 $B$，单步束存活因子为 $\phi_B(\cdot)$，则树 $T$ 的束搜索正确率为

$$

R(T) := \sum_{i \in I} p_i \prod_{t=1}^{d(i)} \phi_B\bigl(k_t(i)\bigr),

$$

其中 $d(i)$ 为叶深度，$k_t(i)$ 为物品 $i$ 在深度 $t$ 的分支因子。定理 1 证明在已知先验时，通过 Bellman 动态规划在每个子集上选择最大化 $\operatorname{Val}(U, \mathcal{P})$ 的分裂即可得到全局最优树。定理 2 证明在真实先验未知时，贪心集合覆盖分裂满足

$$

\operatorname{Val}(U, \mathcal{P}^{g}(U)) \geq \frac{1}{\rho \alpha_U} \operatorname{Val}(U, \mathcal{P}^{*}(U)),

$$

即具有可证明的局部近似保证。定理 3 证明变深树不劣于、且在非平凡扩展条件下严格优于等深树，从而为自适应 ID 长度提供理论支撑。

训练阶段先用监督微调让大语言模型适配序列推荐任务，由于一个物品可能对应多条合法路径，SFT 采用最长可用表示作为监督目标，目标为 $\mathcal{L}_{\mathrm{SFT}} = -\sum_{k=1}^{m} \log P_{\theta}(y_k \mid x, y_{<k})$。随后用 GRPO 在真实解码约束下继续优化，奖励按生成路径是否命中目标物品给出：

$$

R\bigl(y^{(g)}, Y^{*}\bigr) = \begin{cases} 1, & y^{(g)} \in Y^{*}, \\ 0, & \text{otherwise}, \end{cases}

$$

并以组内归一化优势 $\hat{A}^{(g)} = \frac{R^{(g)} - \mu}{\sigma + \epsilon}$ 构造带裁剪的 GRPO 目标。该阶段使模型能够对齐同一物品的多种合法 ID 变体，让约束束搜索保留更多正确解码路径。

![方法图 1](/images/3838716434754c961b2bce666c025ab9.png)

该图给出 BONSAI 的整体框架，包含四个相互衔接的阶段：先从物品元数据中抽取推荐相关关键词完成特征过滤；再以最小集合覆盖策略递归构建词项解码树；随后通过监督微调让大语言模型获得序列推荐能力；最后在真实解码约束下用强化学习进一步优化，使模型对齐同一物品的多种合法 ID 表示。四个阶段共同把“词项 ID 设计”与“解码树结构”耦合为一个整体。

## 三、实验

实验在 Amazon Review 数据集的 Beauty、Sports and Outdoors、Toys and Games 三个子集上进行，指标为 Recall@5、Recall@10、NDCG@5、NDCG@10，并额外使用 Amazon-M2 做数据规模实验。基线覆盖传统原子 ID 方法（SASRec、GRU4Rec）、从零训练的生成式推荐（TIGER、HSTU）、基于语义 ID 的大模型方法（MiniOneRec、OneRec-Think）以及基于文本表示的大模型方法（IDGenRec、GRLM）。实现上使用 Qwen3-32B 做特征过滤，统一以 Qwen3-1.7B 作为骨干模型，SFT 初始学习率 $1 \times 10^{-4}$ 并采用余弦衰减，RL 阶段初始学习率 $1 \times 10^{-6}$、rollout 束大小为 10，全部模型在八张 A100 80GB 上训练。

RQ1 的整体结果显示，BONSAI 在所有数据集与指标上均显著优于全部基线。相对最强基线 GRLM，Beauty 上提升 18.5%–19.5%，Sports 上提升 16.0%–16.8%，Toys 上提升 20.1%–21.6%。结果同时表明：传统原子 ID 方法整体最弱；从零训练的生成式方法优于传统方法但仍不及大模型方法；基于文本表示的大模型方法普遍优于基于语义 ID 的方法。

RQ2 考察两阶段训练的贡献。RL 相对 SFT 在各数据集上带来约 6%–10% 的相对提升，且增益主要来自长表示物品与拥有多种合法表示的物品，这两类子集高度重叠，与设计动机一致。

RQ3 通过受控消融验证两个结构性质。固定深度为 4、用固定大小覆盖集替换最小覆盖以改变分支因子时，三个数据集上性能随分支因子增大而持续下降，说明浅层早期决策尤为关键。将原始树截断为更浅的等深结构时，性能总体随深度增加而提升，但原始变深树始终优于所有截断变体，说明统一深度会过度压缩语义丰富的物品或对简单物品施加多余约束。

RQ4 验证可迁移性：保留 GRLM 生成 ID 中的原始关键词，仅用最小覆盖策略重排顺序，即可把第一层分支因子从千级大幅降低到数百级，并在三个数据集上分别带来 8.9%、7.7%、9.1% 的性能提升，说明解码树本身是主要性能瓶颈之一。

附录进一步报告了冷启动设置（每数据集随机抽取 500 个物品从训练序列中移除）与规模实验，BONSAI 在冷启动 Recall@10 上优于 OneRec-Think 与 GRLM，并随骨干模型规模与数据量呈现良好扩展性。

![实验图 1](/images/960917687e0d9bc23ed8e5ba71c214eb.png)

该图对应主实验的整体性能对比，覆盖 Beauty、Sports、Toys 三个数据集与 Recall@5、Recall@10、NDCG@5、NDCG@10 四项指标。可以看到 BONSAI 在所有数据集与指标上均取得最优结果，相对最强基线 GRLM 在 Beauty 上提升约 18.5%–19.5%，Sports 上约 16.0%–16.8%，Toys 上约 20.1%–21.6%，且基于文本表示的生成式方法整体优于基于语义 ID 的方法。

![实验图 2](/images/5634ecad41bde1ac3cc652f70bd7beab.png)

该图展示分支因子消融实验：固定树深度为 4，用固定大小覆盖集替换最小覆盖以人为改变中间层分支因子。三个数据集上性能随分支因子增大而持续下降，说明约束束搜索的成败高度依赖浅层决策节点保持较小的扇出，早期分支过多会让正确物品在后续步骤中被排除出束。

![实验图 3](/images/361f623858659737dd4e4925287485cc.png)

该图展示树深度消融实验：将原始变深树截断为更浅、更统一的等深结构。性能总体随深度增加而提升，但原始变深树始终优于所有截断变体，说明对所有物品强制统一深度是次优的——它会过度压缩语义丰富的物品，又对简单物品施加多余结构约束，而自适应深度能在表示保真度与解码难度之间取得更好折中。

## 四、总结

本文提出从解码前缀树优化的新视角来设计生成式推荐中的物品 ID，指出物品表示质量与解码结构不应被当作两个独立问题，而应联合优化。作者识别出两个有利的结构性质——自适应变长 ID 与受约束的分支因子，并给出理论保证与实证分析，进而提出 BONSAI：从物品元数据中抽取推荐相关词项，用递归最小集合覆盖构建满足上述性质的解码树，再结合监督微调与基于 GRPO 的强化学习完成训练。实验显示 BONSAI 相对最强基线最高取得 21.6% 的相对提升，且其结构原则可迁移用于改进已有词项 ID 方法。未来方向包括改进特征抽取方法、在树深度与宽度之间取得更好折中，以及把这些原则扩展到多模态物品表示。

## References

- Keqin Bao, Jizhi Zhang, Yang Zhang, Xinyue Huo, Chong Chen, and Fuli Feng. [2024. Decoding matters: Addressing amplification bias and homogeneity issue for llm-based recommendation. arXiv preprint arXiv:2406.14900](https://scholar.google.com/scholar?q=2024.+Decoding+matters%3A+Addressing+amplification+bias+and+homogeneity+issue+for+llm-based+recommendation.+arXiv+preprint+arXiv%3A2406.14900).

- Keqin Bao, Jizhi Zhang, Yang Zhang, Wenjie Wang, Fuli Feng, and Xiangnan He. [2023. TALLRec: An Effective and Efficient Tuning Framework to Align Large Language Model with Recommendation. In RecSys](https://scholar.google.com/scholar?q=2023.+TALLRec%3A+An+Effective+and+Efficient+Tuning+Framework+to+Align+Large+Language+Model+with+Recommendation.+In+RecSys).

- Dimitri Bertsekas. [2012. Dynamic programming and optimal control: Volume I. Vol. 4. Athena scientific](https://scholar.google.com/scholar?q=2012.+Dynamic+programming+and+optimal+control%3A+Volume+I.+Vol.+4.+Athena+scientific).

- Runjin Chen, Mingxuan Ju, Ngoc Bui, Dimosthenis Antypas, Stanley Cai, Xiaopeng Wu, Leonardo Neves, Zhangyang Wang, Neil Shah, and Tong Zhao. [2024. Enhancing item tokenization for generative recommendation through self-improvement. arXiv preprint arXiv:2412.17171](https://scholar.google.com/scholar?q=2024.+Enhancing+item+tokenization+for+generative+recommendation+through+self-improvement.+arXiv+preprint+arXiv%3A2412.17171).

- Weixin Chen, Yuhan Zhao, Jingyuan Huang, Zihe Ye, Clark Mingxuan Ju, Tong Zhao, Neil Shah, Li Chen, and Yongfeng Zhang. [2026. MemRec: Collaborative Memory-Augmented Agentic Recommender System. arXiv preprint arXiv:2601.08816](https://scholar.google.com/scholar?q=2026.+MemRec%3A+Collaborative+Memory-Augmented+Agentic+Recommender+System.+arXiv+preprint+arXiv%3A2601.08816).

- Paul Covington, Jay Adams, and Emre Sargin. [2016. Deep neural networks for youtube recommendations. In RecSys, 191–198](https://scholar.google.com/scholar?q=2016.+Deep+neural+networks+for+youtube+recommendations.+In+RecSys%2C+191%E2%80%93198).

- Jiaxin Deng, Shiyao Wang, Kuo Cai, Lejian Ren, Qigen Hu, Weifeng Ding, Qiang Luo, and Guorui Zhou. [2025. Onerec: Unifying retrieve and rank with generative recommender and iterative preference alignment. arXiv preprint arXiv:2502.18965](https://scholar.google.com/scholar?q=2025.+Onerec%3A+Unifying+retrieve+and+rank+with+generative+recommender+and+iterative+preference+alignment.+arXiv+preprint+arXiv%3A2502.18965).

- Qin Ding, Kevin Course, Linjian Ma, Jianhui Sun, Rouchen Liu, Zhao Zhu, Chunxing Yin, Wei Li, Dai Li, Yu Shi, et al. [2026. Bending the Scaling Law Curve in Large-Scale Recommendation Systems. arXiv preprint arXiv:2602.16986](https://scholar.google.com/scholar?q=2026.+Bending+the+Scaling+Law+Curve+in+Large-Scale+Recommendation+Systems.+arXiv+preprint+arXiv%3A2602.16986).

- Shijie Geng, Shuchang Liu, Zuohui Fu, Yingqiang Ge, and Yongfeng Zhang. [2022. Recommendation as Language Processing (RLP): A Unified Pretrain, Personalized Prompt & Predict Paradigm (P5). In RecSys](https://scholar.google.com/scholar?q=2022.+Recommendation+as+Language+Processing+%28RLP%29%3A+A+Unified+Pretrain%2C+Personalized+Prompt+%26+Predict+Paradigm+%28P5%29.+In+RecSys).

- Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Peiyi Wang, Qihao Zhu, Runxin Xu, Ruoyu Zhang, Shirong Ma, Xiao Bi, et al. [2025. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2501.12948](https://scholar.google.com/scholar?q=2025.+Deepseek-r1%3A+Incentivizing+reasoning+capability+in+llms+via+reinforcement+learning.+arXiv+preprint+arXiv%3A2501.12948).

- Ruining He, Lukasz Heldt, Lichan Hong, Raghunandan Keshavan, Shifan Mao, Nikhil Mehta, Zhengyang Su, Alicia Tsai, Yueqi Wang, Shao-Chuan Wang, et al. [2025. Plum: Adapting pre-trained language models for industrial-scale generative recommendations. arXiv preprint arXiv:2510.07784](https://scholar.google.com/scholar?q=2025.+Plum%3A+Adapting+pre-trained+language+models+for+industrial-scale+generative+recommendations.+arXiv+preprint+arXiv%3A2510.07784).

- Minjie Hong, Zetong Zhou, Zirun Guo, Ziang Zhang, Ruofan Hu, Weinan Gan, Jieming Zhu, and Zhou Zhao. [2025. Generative Reasoning Recommendation via LLMs. arXiv preprint arXiv:2510.20815](https://scholar.google.com/scholar?q=2025.+Generative+Reasoning+Recommendation+via+LLMs.+arXiv+preprint+arXiv%3A2510.20815).

- Yupeng Hou, Jianmo Ni, Zhankui He, Noveen Sachdeva, Wang-Cheng Kang, Ed H Chi, Julian McAuley, and Derek Zhiyuan Cheng. [2025. ActionPiece: Contextually Tokenizing Action Sequences for Generative Recommendation. arXiv preprint arXiv:2502.13581](https://scholar.google.com/scholar?q=2025.+ActionPiece%3A+Contextually+Tokenizing+Action+Sequences+for+Generative+Recommendation.+arXiv+preprint+arXiv%3A2502.13581).

- Peiyu Hu, Wayne Lu, and Jia Wang. [2026. From ids to semantics: A generative framework for cross-domain recommendation with adaptive semantic tokenization. In AAAI, Vol. 40. 14874–14882](https://scholar.google.com/scholar?q=2026.+From+ids+to+semantics%3A+A+generative+framework+for+cross-domain+recommendation+with+adaptive+semantic+tokenization.+In+AAAI%2C+Vol.+40.+14874%E2%80%9314882).

- Wenyue Hua, Shuyuan Xu, Yingqiang Ge, and Yongfeng Zhang. [2023. How to Index Item IDs for Recommendation Foundation Models. In SIGIR-AP](https://scholar.google.com/scholar?q=2023.+How+to+Index+Item+IDs+for+Recommendation+Foundation+Models.+In+SIGIR-AP).

- Jui-Ting Huang, Ashish Sharma, Shuying Sun, Li Xia, David Zhang, Philip Pronin, Janani Padmanabhan, Giuseppe Ottaviano, and Linjun Yang. [2020. Embedding based retrieval in facebook search. In KDD, 2553–2561](https://scholar.google.com/scholar?q=2020.+Embedding+based+retrieval+in+facebook+search.+In+KDD%2C+2553%E2%80%932561).

- Dietmar Jannach and Malte Ludewig. [2017. When Recurrent Neural Networks meet the Neighborhood for Session-Based Recommendation. In RecSys](https://scholar.google.com/scholar?q=2017.+When+Recurrent+Neural+Networks+meet+the+Neighborhood+for+Session-Based+Recommendation.+In+RecSys).

- Jianchao Ji, Zelong Li, Shuyuan Xu, Wenyue Hua, Yingqiang Ge, Juntao Tan, and Yongfeng Zhang. [2024. Genrec: Large language model for generative recommendation. In ECIR, 494–502](https://scholar.google.com/scholar?q=2024.+Genrec%3A+Large+language+model+for+generative+recommendation.+In+ECIR%2C+494%E2%80%93502).

- Wei Jin, Haitao Mao, Zheng Li, Haoming Jiang, Chen Luo, Hongzhi Wen, Haoyu Han, Hanqing Lu, Zhengyang Wang, Ruirui Li, et al. [2023. Amazon-m2: A multilingual multi-locale shopping session dataset for recommendation and text generation. NeurIPS 36 (2023), 8006–8026](https://scholar.google.com/scholar?q=2023.+Amazon-m2%3A+A+multilingual+multi-locale+shopping+session+dataset+for+recommendation+and+text+generation.+NeurIPS+36+%282023%29%2C+8006%E2%80%938026).

- Clark Mingxuan Ju, Liam Collins, Leonardo Neves, Bhuvesh Kumar, Louis Yufeng Wang, Tong Zhao, and Neil Shah. [2025. Generative Recommendation with Semantic IDs: A Practitioner's Handbook. arXiv preprint arXiv:2507.22224](https://scholar.google.com/scholar?q=2025.+Generative+Recommendation+with+Semantic+IDs%3A+A+Practitioner%27s+Handbook.+arXiv+preprint+arXiv%3A2507.22224).

- Clark Mingxuan Ju, Leonardo Neves, Bhuvesh Kumar, Liam Collins, Tong Zhao, Yuwei Qiu, Qing Dou, Sohail Nizam, Sen Yang, and Neil Shah. [2025. Revisiting Self-attention for Cross-domain Sequential Recommendation. In KDD V.2, 1094–1105](https://scholar.google.com/scholar?q=2025.+Revisiting+Self-attention+for+Cross-domain+Sequential+Recommendation.+In+KDD+V.2%2C+1094%E2%80%931105).

- Clark Mingxuan Ju, Leonardo Neves, Bhuvesh Kumar, Liam Collins, Tong Zhao, Yuwei Qiu, Qing Dou, Yang Zhou, Sohail Nizam, Rengim Ozturk, et al. [2025. Learning Universal User Representations Leveraging Cross-domain User Intent at Snapchat. arXiv preprint arXiv:2504.21838](https://scholar.google.com/scholar?q=2025.+Learning+Universal+User+Representations+Leveraging+Cross-domain+User+Intent+at+Snapchat.+arXiv+preprint+arXiv%3A2504.21838).

- Clark Mingxuan Ju, Tong Zhao, Leonardo Neves, Liam Collins, Bhuvesh Kumar, Jiwen Ren, Lili Zhang, Wenfeng Zhuo, Vincent Zhang, Xiao Bai, et al. [2026. Semantic IDs for Recommender Systems at Snapchat: Use Cases, Technical Challenges, and Design Choices. arXiv preprint arXiv:2604.03949](https://scholar.google.com/scholar?q=2026.+Semantic+IDs+for+Recommender+Systems+at+Snapchat%3A+Use+Cases%2C+Technical+Challenges%2C+and+Design+Choices.+arXiv+preprint+arXiv%3A2604.03949).

- Mingxuan Ju, William Shiao, Zhichun Guo, Yanfang Ye, Yozen Liu, Neil Shah, and Tong Zhao. [2024. How does message passing improve collaborative filtering? NeurIPS 37 (2024), 8760–8784](https://scholar.google.com/scholar?q=2024.+How+does+message+passing+improve+collaborative+filtering%3F+NeurIPS+37+%282024%29%2C+8760%E2%80%938784).

- Wang-Cheng Kang and Julian J. [McAuley. 2018. Self-Attentive Sequential Recommendation. In ICDM](https://scholar.google.com/scholar?q=McAuley.+2018.+Self-Attentive+Sequential+Recommendation.+In+ICDM).

- Xiaoyu Kong, Leheng Sheng, Junfei Tan, Yuxin Chen, Jiancan Wu, An Zhang, Xiang Wang, and Xiangnan He. [2025. Minionerec: An open-source framework for scaling generative recommendation. arXiv preprint arXiv:2510.24431](https://scholar.google.com/scholar?q=2025.+Minionerec%3A+An+open-source+framework+for+scaling+generative+recommendation.+arXiv+preprint+arXiv%3A2510.24431).

- Doyup Lee, Chiheon Kim, Saehoon Kim, Minsu Cho, and Wook-Shin Han. [2022. Autoregressive image generation using residual quantization. In CVPR, 11523–11532](https://scholar.google.com/scholar?q=2022.+Autoregressive+image+generation+using+residual+quantization.+In+CVPR%2C+11523%E2%80%9311532).

- Lei Li, Yongfeng Zhang, Dugang Liu, and Li Chen. [2023. Large Language Models for Generative Recommendation: A Survey and Visionary Discussions. CoRR abs/2309.01157](https://scholar.google.com/scholar?q=2023.+Large+Language+Models+for+Generative+Recommendation%3A+A+Survey+and+Visionary+Discussions.+CoRR+abs%2F2309.01157).

- Jiayi Liao, Sihang Li, Zhengyi Yang, Jiancan Wu, Yancheng Yuan, Xiang Wang, and Xiangnan He. [2024. LLaRA: Large Language-Recommendation Assistant. In SIGIR](https://scholar.google.com/scholar?q=2024.+LLaRA%3A+Large+Language-Recommendation+Assistant.+In+SIGIR).

- Jingzhe Liu, Liam Collins, Jiliang Tang, Tong Zhao, Neil Shah, and Clark Mingxuan Ju. [2025. Understanding generative recommendation with semantic ids from a model-scaling view. arXiv preprint arXiv:2509.25522](https://scholar.google.com/scholar?q=2025.+Understanding+generative+recommendation+with+semantic+ids+from+a+model-scaling+view.+arXiv+preprint+arXiv%3A2509.25522).

- Qidong Liu, Xiangyu Zhao, Yejing Wang, Zijian Zhang, Howard Zhong, Chong Chen, Xiang Li, Wei Huang, and Feng Tian. [2025. Bridge the domains: Large language models enhanced cross-domain sequential recommendation. In SIGIR, 1582–1592](https://scholar.google.com/scholar?q=2025.+Bridge+the+domains%3A+Large+language+models+enhanced+cross-domain+sequential+recommendation.+In+SIGIR%2C+1582%E2%80%931592).

- Zhanyu Liu, Shiyao Wang, Xingmei Wang, Rongzhou Zhang, Jiaxin Deng, Honghui Bao, Jinghao Zhang, Wuchao Li, Pengfei Zheng, Xiangyu Wu, et al. [2025. Onerec-think: In-text reasoning for generative recommendation. arXiv preprint arXiv:2510.11639](https://scholar.google.com/scholar?q=2025.+Onerec-think%3A+In-text+reasoning+for+generative+recommendation.+arXiv+preprint+arXiv%3A2510.11639).

- OpenAI. [2023. GPT-4 Technical Report. CoRR](https://scholar.google.com/scholar?q=2023.+GPT-4+Technical+Report.+CoRR).

- Laurent Perron, Frédéric Didier, and Steven Gay. [2023. The CP-SAT-LP solver (invited talk). In CP 2023. Schloss Dagstuhl–Leibniz-Zentrum für Informatik, 3–1](https://scholar.google.com/scholar?q=2023.+The+CP-SAT-LP+solver+%28invited+talk%29.+In+CP+2023.+Schloss+Dagstuhl%E2%80%93Leibniz-Zentrum+f%C3%BCr+Informatik%2C+3%E2%80%931).

- Shashank Rajput, Nikhil Mehta, Anima Singh, Raghunandan Hulikal Keshavan, Trung Vu, Lukasz Heldt, Lichan Hong, Yi Tay, Vinh Q. [Tran, Jonah Samost, Maciej Kula, Ed H. Chi, and Mahesh Sathiamoorthy. 2023. Recommender Systems with Generative Retrieval. In NeurIPS](https://scholar.google.com/scholar?q=Tran%2C+Jonah+Samost%2C+Maciej+Kula%2C+Ed+H.+Chi%2C+and+Mahesh+Sathiamoorthy.+2023.+Recommender+Systems+with+Generative+Retrieval.+In+NeurIPS).

- Steffen Rendle, Christoph Freudenthaler, Zeno Gantner, and Lars Schmidt-Thieme. [2012. BPR: Bayesian Personalized Ranking from Implicit Feedback. CoRR abs/1205.2618](https://scholar.google.com/scholar?q=2012.+BPR%3A+Bayesian+Personalized+Ranking+from+Implicit+Feedback.+CoRR+abs%2F1205.2618).

- Zhihong Shao, Peiyi Wang, Qihao Zhu, Runxin Xu, Junxiao Song, Xiao Bi, Haowei Zhang, Mingchuan Zhang, YK Li, Yang Wu, et al. [2024. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. arXiv preprint arXiv:2402.03300](https://scholar.google.com/scholar?q=2024.+Deepseekmath%3A+Pushing+the+limits+of+mathematical+reasoning+in+open+language+models.+arXiv+preprint+arXiv%3A2402.03300).

- Zhengyang Su, Isay Katsman, Yueqi Wang, Ruining He, Lukasz Heldt, Raghunandan Keshavan, Shao-Chuan Wang, Xinyang Yi, Mingyan Gao, Onkar Dalal, et al. [2026. Vectorizing the Trie: Efficient Constrained Decoding for LLM-based Generative Retrieval on Accelerators. arXiv preprint arXiv:2602.22647](https://scholar.google.com/scholar?q=2026.+Vectorizing+the+Trie%3A+Efficient+Constrained+Decoding+for+LLM-based+Generative+Retrieval+on+Accelerators.+arXiv+preprint+arXiv%3A2602.22647).

- Junfei Tan, Yuxin Chen, An Zhang, Junguang Jiang, Bin Liu, Ziru Xu, Han Zhu, Jian Xu, Bo Zheng, and Xiang Wang. [2025. Reinforced preference optimization for recommendation. arXiv preprint arXiv:2510.12211](https://scholar.google.com/scholar?q=2025.+Reinforced+preference+optimization+for+recommendation.+arXiv+preprint+arXiv%3A2510.12211).

- Juntao Tan, Shuyuan Xu, Wenyue Hua, Yingqiang Ge, Zelong Li, and Yongfeng Zhang. [2024. Idgenrec: Llm-recsys alignment with textual id learning. In SIGIR, 355–364](https://scholar.google.com/scholar?q=2024.+Idgenrec%3A+Llm-recsys+alignment+with+textual+id+learning.+In+SIGIR%2C+355%E2%80%93364).

- Zhouhang Xie, Bo Peng, Zhankui He, Ziqi Chen, Alice Han, Isabella Ye, Benjamin Coleman, Noveen Sachdeva, Fernando Pereira, Julian McAuley, et al. [2026. AgenticTagger: Structured Item Representation for Recommendation with LLM Agents. arXiv preprint arXiv:2602.05945](https://scholar.google.com/scholar?q=2026.+AgenticTagger%3A+Structured+Item+Representation+for+Recommendation+with+LLM+Agents.+arXiv+preprint+arXiv%3A2602.05945).

- Wujiang Xu, Yunxiao Shi, Zujie Liang, Xuying Ning, Kai Mei, Kun Wang, Xi Zhu, Min Xu, and Yongfeng Zhang. [2025. iagent: Llm agent as a shield between user and recommender systems. In Findings of ACL 2025, 18056–18084](https://scholar.google.com/scholar?q=2025.+iagent%3A+Llm+agent+as+a+shield+between+user+and+recommender+systems.+In+Findings+of+ACL+2025%2C+18056%E2%80%9318084).

- An Yang, Anfeng Li, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen Yu, Chang Gao, Chengen Huang, Chenxu Lv, et al. [2025. Qwen3 technical report. arXiv preprint arXiv:2505.09388](https://scholar.google.com/scholar?q=2025.+Qwen3+technical+report.+arXiv+preprint+arXiv%3A2505.09388).

- Ji Yang, Xinyang Yi, Derek Zhiyuan Cheng, Lichan Hong, Yang Li, Simon Xiaoming Wang, Taibai Xu, and Ed H Chi. [2020. Mixed negative sampling for learning two-tower neural networks in recommendations. In Companion proceedings of the web conference 2020, 441–447](https://scholar.google.com/scholar?q=2020.+Mixed+negative+sampling+for+learning+two-tower+neural+networks+in+recommendations.+In+Companion+proceedings+of+the+web+conference+2020%2C+441%E2%80%93447).

- Xinyang Yi, Ji Yang, Lichan Hong, Derek Zhiyuan Cheng, Lukasz Heldt, Aditee Kumthekar, Zhe Zhao, Li Wei, and Ed Chi. [2019. Sampling-bias-corrected neural modeling for large corpus item recommendations. In RecSys, 269–277](https://scholar.google.com/scholar?q=2019.+Sampling-bias-corrected+neural+modeling+for+large+corpus+item+recommendations.+In+RecSys%2C+269%E2%80%93277).

- Zhenrui Yue, Sara Rabhi, Gabriel de Souza Pereira Moreira, Dong Wang, and Even Oldridge. [2023. Llamarec: Two-stage recommendation using large language models for ranking. arXiv preprint arXiv:2311.02089](https://scholar.google.com/scholar?q=2023.+Llamarec%3A+Two-stage+recommendation+using+large+language+models+for+ranking.+arXiv+preprint+arXiv%3A2311.02089).

- Jiaqi Zhai, Lucy Liao, Xing Liu, Yueming Wang, Rui Li, Xuan Cao, Leon Gao, Zhaojie Gong, Fangda Gu, Michael He, et al. [2024. Actions speak louder than words: Trillion-parameter sequential transducers for generative recommendations. arXiv preprint arXiv:2402.17152](https://scholar.google.com/scholar?q=2024.+Actions+speak+louder+than+words%3A+Trillion-parameter+sequential+transducers+for+generative+recommendations.+arXiv+preprint+arXiv%3A2402.17152).

- An Zhang, Leheng Sheng, Yuxin Chen, Hao Li, Yang Deng, Xiang Wang, and Tat-Seng Chua. [2023. On Generative Agents in Recommendation. CoRR abs/2310.10108](https://scholar.google.com/scholar?q=2023.+On+Generative+Agents+in+Recommendation.+CoRR+abs%2F2310.10108).

- Junjie Zhang, Yupeng Hou, Ruobing Xie, Wenqi Sun, Julian J. [McAuley, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. 2023. AgentCF: Collaborative Learning with Autonomous Language Agents for Recommender Systems. CoRR abs/2310.09233](https://scholar.google.com/scholar?q=McAuley%2C+Wayne+Xin+Zhao%2C+Leyu+Lin%2C+and+Ji-Rong+Wen.+2023.+AgentCF%3A+Collaborative+Learning+with+Autonomous+Language+Agents+for+Recommender+Systems.+CoRR+abs%2F2310.09233).

- Junjie Zhang, Ruobing Xie, Yupeng Hou, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen. [2023. Recommendation as Instruction Following: A Large Language Model Empowered Recommendation Approach. CoRR abs/2305.07001](https://scholar.google.com/scholar?q=2023.+Recommendation+as+Instruction+Following%3A+A+Large+Language+Model+Empowered+Recommendation+Approach.+CoRR+abs%2F2305.07001).

- Luankang Zhang, Yonghao Huang, Hang Lv, Mingjia Yin, Liangyue Li, Zulong Chen, Hao Wang, and Enhong Chen. [2026. Why Thinking Hurts? Diagnosing and Rectifying the Reasoning Shift in Foundation Recommender Models. arXiv preprint arXiv:2602.16587](https://scholar.google.com/scholar?q=2026.+Why+Thinking+Hurts%3F+Diagnosing+and+Rectifying+the+Reasoning+Shift+in+Foundation+Recommender+Models.+arXiv+preprint+arXiv%3A2602.16587).

- Taiyan Zhang, Hongtao Wang, Yunqian Fan, Kunda Yang, Jichuan Zeng, and Renchi Yang. [A Survey of Item Identifiers in Generative Recommendation: Construction, Alignment, and Generation](https://scholar.google.com/scholar?q=A+Survey+of+Item+Identifiers+in+Generative+Recommendation%3A+Construction%2C+Alignment%2C+and+Generation).

- Zhiyang Zhang, Junda She, Kuo Cai, Bo Chen, Shiyao Wang, Xinchen Luo, Qiang Luo, Ruiming Tang, Han Li, Kun Gai, et al. [2026. Unleashing the Native Recommendation Potential: LLM-Based Generative Recommendation via Structured Term Identifiers. arXiv preprint arXiv:2601.06798](https://scholar.google.com/scholar?q=2026.+Unleashing+the+Native+Recommendation+Potential%3A+LLM-Based+Generative+Recommendation+via+Structured+Term+Identifiers.+arXiv+preprint+arXiv%3A2601.06798).

- Bowen Zheng, Yupeng Hou, Hongyu Lu, Yu Chen, Wayne Xin Zhao, Ming Chen, and Ji-Rong Wen. [2023. Adapting Large Language Models by Integrating Collaborative Semantics for Recommendation. CoRR abs/2311.09049](https://scholar.google.com/scholar?q=2023.+Adapting+Large+Language+Models+by+Integrating+Collaborative+Semantics+for+Recommendation.+CoRR+abs%2F2311.09049).

- Guorui Zhou, Honghui Bao, Jiaming Huang, Jiaxin Deng, Jinghao Zhang, Junda She, Kuo Cai, Lejian Ren, Lu Ren, Qiang Luo, et al. [2025. OpenOneRec Technical Report. arXiv preprint arXiv:2512.24762](https://scholar.google.com/scholar?q=2025.+OpenOneRec+Technical+Report.+arXiv+preprint+arXiv%3A2512.24762).

- Guorui Zhou, Hengrui Hu, Hongtao Cheng, Huanjie Wang, Jiaxin Deng, Jinghao Zhang, Kuo Cai, Lejian Ren, Lu Ren, Liao Yu, et al. [2025. Onerec-v2 technical report. arXiv preprint arXiv:2508.20900](https://scholar.google.com/scholar?q=2025.+Onerec-v2+technical+report.+arXiv+preprint+arXiv%3A2508.20900).
