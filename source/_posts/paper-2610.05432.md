---

title: "OpticalRec：面向多模态推荐的统一光学视觉-语言表示"

date: "2026-10-22"

year: "2026"

venue_type: "arxiv预印本"

venue_name: "arXiv"

categories: ["推荐系统", "多模态推荐"]

tags: ["论文速读", "统一编码", "视觉空间渲染", "跨模态交互", "即插即用", "有效秩", "互信息"]

slug: "paper-2610.05432"

---

[论文链接](https://arxiv.org/abs/2610.05432)

## 一、研究背景与问题

多模态推荐（multimodal collaborative filtering, MMCF）的核心目标是为每个物品学习一个能够同时刻画视觉外观与文本语义的表示，再与用户交互图结合完成匹配。近年来视觉-语言模型（VLM）的进展为这一任务提供了强大的预训练表示，但论文指出，主流做法仍然沿用“先独立编码、再后融合”的范式：视觉编码器与文本编码器各自处理单一模态，随后通过求和、拼接或图融合等刚性操作合并。这种范式存在两个结构性缺陷：其一，独立编码天然缺失跨模态交互（如跨注意力），两种模态被投影到异质向量空间；其二，后融合是有损压缩，会进一步扭曲跨模态语义。

作者据此提出两条设计准则：多模态内容应置于统一的输入空间以支持丰富的视觉-语言交互；统一输入应被一次性编码为同质嵌入空间，不再引入破坏性的后融合。基于此，论文提出 OpticalRec——首个面向多模态协同过滤的视觉空间统一编码范式。其关键洞察是“所见即用户所见”：用户浏览商品页时会在商品图与文字之间来回切换注意力，因此把物品的文本元数据渲染为视觉字形（glyph），与商品图共同构成一张“物品卡片”，让图像与文字在同一个像素空间内被视觉编码器原生地联合处理，再经语言解码器完成语义级对齐，从而同时利用现代 VLM 的感知级与语义级双重注意力。论文的主要贡献包括：提出视觉空间统一编码框架；在无需有损后融合的前提下保留视觉-语言相关性，并用互信息与矩阵有效秩给出理论支撑；在多个 Amazon 基准与多种推荐骨干上取得一致提升；以及该模块轻量、即插即用、对渲染布局/字体/颜色鲁棒。

## 二、方法

任务定义。设用户集合 $\mathcal{U}=\{u_1,\dots,u_M\}$、物品集合 $\mathcal{I}=\{i_1,\dots,i_N\}$，物品 $i$ 由图像 $\mathbf{v}_i$ 与文本描述 $\mathbf{t}_i$ 描述。物品嵌入由编码器 $f$ 给出，用户表示由交互物品聚合得到：

$$

\mathbf{q}_i = f(\mathbf{v}_i, \mathbf{t}_i), \quad \mathbf{p}_u = \mathcal{A}(\{\mathbf{q}_i\}_{i\in\mathcal{N}_u})

$$

推荐器 $\mathcal{F}(\cdot)$ 进一步结合用户-物品图 $\mathcal{G}$ 得到 $(\mathbf{p}_u', \mathbf{q}_i')=\mathcal{F}(\mathbf{p}_u,\mathbf{q}_i,\mathcal{G})$，最终打分由内积 $y_{ui}=\langle \mathbf{p}_u', \mathbf{q}_i'\rangle$ 给出。

独立编码与后融合。传统范式先用视觉、语言编码器 $f_V,f_T$ 得到模态特定向量，再用融合算子 $g$ 合并：

$$

(\mathbf{v}_i,\mathbf{t}_i) \xrightarrow{f_V,f_T} \mathbf{z}_i^{\mathrm{LF}} \triangleq (\mathbf{z}_i^{v},\mathbf{z}_i^{t}) \xrightarrow{g} \mathbf{q}_i^{\mathrm{LF}}

$$

基于提示（prompt）的编码虽在语言解码器层引入了语义级交互，但图像 token 与文本 token 仍是分别编码后拼接，本质上仍属后融合。

统一像素空间编码。OpticalRec 首先用一次高效的渲染操作 $\mathcal{R}(\cdot)$ 把物品图像 $\mathbf{v}_i$、文本描述 $\mathbf{t}_i$ 以及图文版式结构 $\mathbf{s}_i^{vt}$ 统一映射到像素空间：

$$

\tilde{\mathbf{v}}_i = \mathcal{R}(\mathbf{v}_i, \mathbf{t}_i, \mathbf{s}_i^{vt})

$$

具体渲染步骤为：创建 $m\times m$ 的方形空白画布并设定图像高度 $h$（$h<m$）；按原始宽高比缩放物品图并置于画布上方；从物品 id 检索 {标题, 品牌, 类别, 价格} 文本元数据，渲染到剩余的 $m\times(m-h)$ 区域，版式与配色大致遵循电商页面风格。随后统一输入经单一（冻结的）视觉-语言编码器 $f_\Phi$ 一次性编码：

$$

(\mathbf{v}_i,\mathbf{t}_i,\mathbf{s}_i^{vt}) \xrightarrow{\mathcal{R}} \tilde{\mathbf{v}}_i \xrightarrow{f_\Phi} \mathbf{z}_i^{\mathrm{OR}} = \mathbf{q}_i^{\mathrm{OR}}

$$

由此，跨模态交互同时发生在视觉编码器的 patch 级（感知层，图像区域与渲染字形的区域匹配）与语言解码器的 token 级（语义层），且输出为同质嵌入，无需任何后融合。

互信息视角的理论分析。论文将两种范式的信息保留差异分解为跨模态增益与融合损失之和：

$$

I(\mathbf{q}_i^{\mathrm{OR}};(\mathbf{v}_i,\mathbf{t}_i)) - I(\mathbf{q}_i^{\mathrm{LF}};(\mathbf{v}_i,\mathbf{t}_i)) = \mathcal{I}_{\mathrm{cross}}^{\mathrm{OR}} + \mathcal{D}_{\mathrm{intra}}^{\mathrm{LF}}

$$

其中 $\mathcal{I}_{\mathrm{cross}}^{\mathrm{OR}} \triangleq I(\mathbf{q}_i^{\mathrm{OR}};\mathbf{x}_i) - I(\mathbf{z}_i^{\mathrm{LF}};\mathbf{x}_i)$ 为正，因为独立编码无法完整保留跨模态信息，而统一编码将两种模态暴露给同一编码器；$\mathcal{D}_{\mathrm{intra}}^{\mathrm{LF}} \triangleq I(\mathbf{z}_i^{\mathrm{LF}};\mathbf{x}_i) - I(\mathbf{q}_i^{\mathrm{LF}};\mathbf{x}_i)$ 为正，因为 $\mathbf{x}_i \to \mathbf{z}_i^{\mathrm{LF}} \to \mathbf{q}_i^{\mathrm{LF}}$ 构成马尔可夫链，由数据处理不等式可知有损融合必然造成严格的信息损失。附录进一步给出跨模态交互预算的规模估计，说明该差距在实际规模下相当可观。

矩阵有效秩分析。为刻画表示是否塌缩，论文采用有效秩 $\mathrm{erank}(\mathbf{X})=\exp\left(-\sum_{i=1}^{n} p_i \log p_i\right)$，其中 $p_i=\sigma_i/\sum_j \sigma_j$ 为归一化奇异值分布；取值越低表示表示塌缩，越高表示信息分布越丰富。

![方法图 1](/images/cb6d66ae554a6633322ba4ddb273c71e.png)

该图对比三种编码路径：传统独立编码加后融合、基于提示的 VLM 编码，以及 OpticalRec 的统一像素空间编码。前两者在融合前都缺少跨模态交互，而 OpticalRec 让图像与渲染文字在同一视觉编码器内完成 patch 级交互，再经语言解码器完成语义级对齐，全程无需后融合。

## 三、实验

数据集与设置。实验采用 Amazon 评论数据中三个常用 MMCF 基准：Baby（108,897 用户 / 17,836 物品 / 330,771 交互，稀疏度 99.983%）、Pets（461,828 / 61,060 / 1,772,584，99.993%）与 Clothing（398,796 / 75,616 / 2,109,975，99.993%），预处理采用 5-core 过滤并剔除缺失特征的物品。骨干模型包括 VBPR、LATTICE、FREEDOM、BM3 与 LGMRec，并额外构造基于提示的 VLM 基线以隔离感知级交互的贡献。主实验使用 Qwen3-VL-8B 且全程冻结，推荐模型用 AdamW 训练并早停，评价指标为 NDCG@20、Recall@20 与 Hit Ratio@20。

主结果。OpticalRec 在所有骨干与数据集上一致优于最强基线：全部模型、指标与数据集上的平均增益为 2.12%，其中 Pets 上平均提升 3.21%（FREEDOM 的 NDCG@20 最高提升 5.82%），Baby 与 Clothing 分别为 1.65% 与 1.51%。NDCG@20 的提升（2.41%）大于 Recall@20（1.97%），说明不仅召回更强，排序质量也更好。图结构骨干受益更多：LATTICE、FREEDOM、LGMRec 的平均增益分别为 2.29%、2.88%、2.29%，而 VBPR 为 1.09%，表明更丰富的多模态物品表示能进一步促进交互图上的语义传播。以 InternVL3.5-8B 作为编码 VLM 的补充实验同样显示 OpticalRec 全面最优，相对次优基线平均提升 2.51%，体现即插即用特性。

双重注意力行为。作者以一件“圣诞猫衣”物品卡片为例，用 Cat、Christmas、Clothes 对应的 patch 作为查询可视化注意力：视觉编码器的注意力广泛覆盖商品图与相关文本区域，体现感知级的上下文构建；语言解码器的注意力则更集中于语义匹配的图文区域，体现语义级的精细对齐。两者互补，印证了统一编码在两个阶段完成跨模态交互。

嵌入几何与有效秩。PCA 可视化显示 OpticalRec 在图像与文本表示之间形成统一流形，而后融合则偏向单一模态（VBPR 偏文本、LATTICE 偏图像），说明事后融合难以平衡异质模态分布。有效秩方面，OpticalRec 取得最高平均有效秩 155.6，比后融合高 22.81%，比最强的单模态基线（纯文本编码）高 11.54%；后融合平均有效秩仅 126.7，比纯文本编码低 9.18%，呈现维度塌缩。附录的 Spearman 分析显示有效秩与 Recall@20 整体呈强正相关（$\rho=0.85$，$p<0.001$）。

消融与鲁棒性。渲染分辨率方面，$544\times544$ 整体最优，更低或更高分辨率均略有下降，说明中等分辨率已足以保留视觉-语言语义并避免不必要的高分辨率推理开销。版式、字号与颜色扰动实验（50% 数据随机打乱 {标题, 品牌, 类别, 价格} 位置、字号缩放 ±25%、文字改为黑白）显示所有结果相对默认设置均在 ±1% 以内。更长文本实验表明加入物品详细描述可带来 +0.7% 至 +1.6% 的提升，且在 1000 字符阈值附近饱和（+1.14%），说明默认仅用标题、品牌、类别、价格已提供较强的推荐信号。效率方面，渲染为一次性离线过程：Baby 的 17,836 件物品用 8 个 worker 耗时 13.5 分钟、占用 2.4 GB；Pets 为 46.0 分钟、8.1 GB；Clothing 为 57.0 分钟、10.1 GB，开销在现代机器上可接受。

![实验图 1](/images/1ebfcd71f7be071bb1682b4efb1b65be.png)

该图以圣诞猫衣物品卡片为例，用 Cat、Christmas、Clothes 对应 patch 作为查询展示双重注意力：视觉编码器注意力较宽泛地覆盖商品图与相关文字区域，语言解码器注意力更集中于语义匹配的图文区域，说明感知层与语义层承担互补的跨模态对齐角色。

![实验图 2](/images/1374d62fafc2ce749d28b69e55827f4f.png)

该图用 PCA 与 50% 置信椭圆展示嵌入分布：OpticalRec 在图像与文本表示之间形成统一流形，而后融合明显偏向单一模态，说明事后融合难以平衡异质模态分布，统一编码的跨模态对齐更好。

![实验图 3](/images/a4a36a82ac2fc18fb49a791433c534fc.png)

该图比较单模态编码、后融合与 OpticalRec 的矩阵有效秩。灰色区域标出后融合造成的有效秩下降，而 OpticalRec 在各设置下均最高，说明其嵌入空间保留了更丰富的视觉-语言变化、塌缩更少。

![实验图 4](/images/faa790e1a8210455a5f23f2f49c4b6c6.png)

该图展示不同物品卡片渲染分辨率下的性能变化，$544\times544$ 在多个数据集与骨干上整体最优，过低或过高分辨率均略有下降，说明中等分辨率已足以承载视觉-语言语义并降低推理开销。

![实验图 5](/images/84396bad91776bc195efae52e5deed05.png)

该图作为分辨率鲁棒性分析的补充面板，进一步呈现不同渲染分辨率对推荐指标的影响趋势，与主图结论一致：中等分辨率即可稳定取得最佳或接近最佳的表现，便于实际部署时固定渲染配置。

## 四、总结

论文提出 OpticalRec，一种面向多模态协同过滤的统一光学视觉-语言编码框架。它通过将物品文本与图像渲染到共享视觉空间，使跨模态交互同时发生在视觉编码器的感知层与语言解码器的语义层，从而避免破坏性的后融合。跨数据集、跨推荐骨干的实验显示出一致增益，并伴随更高的嵌入有效秩、对渲染变化的鲁棒性以及可接受的一次性预处理成本。作者也指出局限：本文聚焦于基于特征的多模态协同过滤这一大规模物品编码的主流设定，尽管已评估多种骨干、渲染设置、文本长度与 VLM 规模，向视频推荐等更多推荐领域的推广验证仍值得未来研究。

## References

- Shuai Bai, Yuxuan Cai, and 1 others. 2025. Qwen3-vl technical report. Preprint, arXiv:2511.21631.

- Jingyuan Chen, Hanwang Zhang, Xiangnan He, Liqiang Nie, Wei Liu, and Tat-Seng Chua. 2017. Attentive collaborative filtering: Multimedia recommendation with item-and component-level attention. In Proceedings of the 40th International ACM SIGIR Conference on Research and Development in Information Retrieval, pages 335–344.

- Thomas M. Cover and Joy A. Thomas. 2006. Elements of Information Theory, 2nd edition. John Wiley & Sons, Hoboken, NJ.

- Zhiqiang Guo, Jianjun Li, Guohui Li, Chaoyang Wang, Si Shi, and Bin Ruan. 2024. Lgmrec: Local and global graph learning for multimodal recommendation. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 38, pages 8454–8462.

- Ruining He and Julian McAuley. 2016. Vbpr: visual bayesian personalized ranking from implicit feedback. In Proceedings of the AAAI conference on artificial intelligence, volume 30.

- Yicheng He, Zhou Kaiyu, Haoyue Bai, Fengbin Zhu, and Yonghui Yang. 2025. Understanding embedding scaling in collaborative filtering. arXiv preprint arXiv:2509.15709.

- Yupeng Hou, Jiacheng Li, Zhankui He, An Yan, Xiusi Chen, and Julian McAuley. 2024. Bridging language and items for retrieval and recommendation. Preprint, arXiv:2403.03952.

- Kibum Kim, Jiwan Kim, Kyle Min, Yueqi Wang, Jinyoung Moon, Julian McAuley, and Chanyoung Park. 2026. Sink-token-aware pruning for fine-grained video understanding in efficient video llms. arXiv preprint arXiv:2604.20937. [论文链接](https://arxiv.org/abs/2604.20937) · [代码链接](https://github.com/rlqja1107/SToP)

- Zijie Lei, Tao Feng, Zhigang Hua, Yan Xie, Guanyu Lin, Shuang Yang, Ge Liu, and Jiaxuan You. 2026. Unirec: Unified multimodal encoding for llm-based recommendations. arXiv preprint arXiv:2601.19423.

- Bo Li, Yuanhan Zhang, Dong Guo, Renrui Zhang, Feng Li, Hao Zhang, Kaichen Zhang, Peiyuan Zhang, Yanwei Li, Ziwei Liu, and 1 others. 2024a. Llava-onevision: Easy visual task transfer. arXiv preprint arXiv:2408.03326.

- Feng Li, Renrui Zhang, Hao Zhang, Yuanhan Zhang, Bo Li, Wei Li, Zejun Ma, and Chunyuan Li. 2024b. Llava-next-interleave: Tackling multi-image, video, and 3d in large multimodal models. arXiv preprint arXiv:2407.07895.

- Guohui Li, Li Zou, Zhiying Deng, and Qi Chen. 2024c. Neighborhood-enhanced multimodal collaborative filtering for item cold start recommendation. In ICASSP 2024-2024 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), pages 7815–7819. IEEE.

- Kang Liu, Feng Xue, Dan Guo, Le Wu, Shujie Li, and Richang Hong. 2023. Megcf: Multimodal entity graph collaborative filtering for personalized recommendation. ACM transactions on information systems, 41(2):1–27.

- Shiqin Liu, Chaozhuo Li, Minjun Zhao, Litian Zhang, and Jiajun Bu. 2025. Modalsync: Synchronizing user behavior with multimodal features for multimodal pre-training recommendation. In Companion Proceedings of the ACM on Web Conference 2025, pages 2278–2287.

- Daniele Malitesta, Giandomenico Cornacchia, Claudio Pomo, Felice Antonio Merra, Tommaso Di Noia, and Eugenio Di Sciascio. 2025. Formalizing multimedia recommendation through multimodal deep learning. ACM Transactions on Recommender Systems, 3(3):1–33.

- Daniele Malitesta, Emanuele Rossi, Claudio Pomo, Tommaso Di Noia, and Fragkiskos D Malliaros. 2024. Do we really need to drop items with missing modalities in multimodal recommendation? In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management, pages 3943–3948.

- Rongqing Kenneth Ong and Andy WH Khong. 2025. Spectrum-based modality representation fusion graph convolutional network for multimodal recommendation. In Proceedings of the Eighteenth ACM International Conference on Web Search and Data Mining, pages 773–781.

- OpenAI. 2026. OpenAI gpt-5 system card. Preprint, arXiv:2601.03267. [论文链接](https://arxiv.org/abs/2601.03267)

- OpenGV. 2025. Internvl3.5: Advancing open-source multimodal models in versatility, reasoning, and efficiency. Preprint, arXiv:2508.18265.

- Claudio Pomo, Matteo Attimonelli, Danilo Danese, Fedelucio Narducci, and Tommaso Di Noia. 2025. Do recommender systems really leverage multimodal content? a comprehensive analysis on multimodal representations for recommendation. In Proceedings of the 34th ACM International Conference on Information and Knowledge Management, pages 2377–2387.

- Shutong Qiao, Wei Yuan, Tong Chen, Xiangyu Zhao, Quoc Viet Hung Nguyen, and Hongzhi Yin. 2026. When text-as-vision meets semantic ids in generative recommendation: An empirical study. arXiv preprint arXiv:2601.14697.

- Olivier Roy and Martin Vetterli. 2007. The effective rank: A measure of effective dimensionality. In 2007 15th European Signal Processing Conference, pages 606–610. IEEE.

- Leheng Sheng, An Zhang, Yi Zhang, Yuxin Chen, Xiang Wang, and Tat-Seng Chua. 2024. Language representations can be what recommenders need: Findings and potentials. arXiv preprint arXiv:2407.05441.

- Jianlin Su. 2025. Effective rank construction and computation.

- Qifan Wang, Yinwei Wei, Jianhua Yin, Jianlong Wu, Xuemeng Song, and Liqiang Nie. 2021. Dualgnn: Dual graph neural network for multimedia recommendation. IEEE Transactions on Multimedia, 25:1074–1084.

- Yueqi Wang, Zhankui He, Zhenrui Yue, Julian McAuley, and Dong Wang. 2025a. Your causal self-attentive recommender hosts a lonely neighborhood. In Proceedings of the Eighteenth ACM International Conference on Web Search and Data Mining, pages 688–696.

- Yueqi Wang, Zhenrui Yue, Huimin Zeng, Dong Wang, and Julian McAuley. 2024. Train once, deploy anywhere: Matryoshka representation learning for multimodal recommendation. In Findings of the Association for Computational Linguistics: EMNLP 2024, pages 13461–13472.

- Yuxiang Wang, Xin Shi, and Xueqing Zhao. 2025b. Mllm4rec: multimodal information enhancing llm for sequential recommendation. Journal of Intelligent Information Systems, 63(3):745–761.

- Yinwei Wei, Xiang Wang, Liqiang Nie, Xiangnan He, and Tat-Seng Chua. 2020. Graph-refined convolutional network for multimedia recommendation with implicit feedback. In Proceedings of the 28th ACM international conference on multimedia, pages 3541–3549.

- Yinwei Wei, Xiang Wang, Liqiang Nie, Xiangnan He, Richang Hong, and Tat-Seng Chua. 2019. Mmgcn: Multi-modal graph convolution network for personalized recommendation of micro-video. In Proceedings of the 27th ACM international conference on multimedia, pages 1437–1445.

- Xin Xin, Xiangnan He, Yongfeng Zhang, Yongdong Zhang, and Joemon Jose. 2019. Relational collaborative filtering: Modeling multiple item relations for recommendation. In Proceedings of the 42nd international ACM SIGIR conference on research and development in information retrieval, pages 125–134.

- Shuo Xing, Peiran Li, Yuping Wang, Ruizheng Bai, Yueqi Wang, Chan-Wei Hu, Chengxuan Qian, Huaxiu Yao, and Zhengzhong Tu. 2025. Re-align: Aligning vision language models via retrieval-augmented direct preference optimization. In Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, pages 2379–2397.

- Jinfeng Xu, Zheyu Chen, Shuo Yang, Jinze Li, Wei Wang, Xiping Hu, Steven Hoi, and Edith Ngai. 2025. A survey on multimodal recommender systems: Recent advances and future directions. arXiv preprint arXiv:2502.15711.

- Yu Ye, Junchen Fu, Yu Song, Kaiwen Zheng, and Joemon M Jose. 2025. Are multimodal embeddings truly beneficial for recommendation? a deep dive into whole vs. individual modalities. arXiv preprint arXiv:2508.07399.

- Penghang Yu, Zhiyi Tan, Guanming Lu, and Bing-Kun Bao. 2023. Multi-view graph convolutional network for multimedia recommendation. In Proceedings of the 31st ACM international conference on multimedia, pages 6576–6585.

- Penghang Yu, Zhiyi Tan, Guanming Lu, and Bing-Kun Bao. 2025. Mind individual information! principal graph learning for multimedia recommendation. In Proceedings of the AAAI conference on artificial intelligence, volume 39, pages 13096–13105.

- Zhenrui Yue, Yueqi Wang, Zhankui He, Huimin Zeng, Julian McAuley, and Dong Wang. 2024. Linear recurrent units for sequential recommendation. In Proceedings of the 17th ACM international conference on web search and data mining, pages 930–938.

- Zhenrui Yue, Huimin Zeng, Yueqi Wang, Julian McAuley, and Dong Wang. 2025. Preference-optimized retrieval and ranking for efficient multimodal recommendation. In Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V. 2, pages 3692–3703.

- Jianyang Zhai, Zi-Feng Mai, Chang-Dong Wang, Feidiao Yang, Xiawu Zheng, Hui Li, and Yonghong Tian. 2025. Multimodal quantitative language for generative recommendation. In The Thirteenth International Conference on Learning Representations.

- Jinghao Zhang, Yanqiao Zhu, Qiang Liu, Shu Wu, Shuhui Wang, and Liang Wang. 2021. Mining latent structures for multimedia recommendation. In Proceedings of the 29th ACM international conference on multimedia, pages 3872–3880.

- Bowen Zheng, Junjie Zhang, Hongyu Lu, Yu Chen, Ming Chen, Wayne Xin Zhao, and Ji-Rong Wen. 2024. Enhancing graph contrastive learning with reliable and informative augmentation for recommendation. arXiv preprint arXiv:2409.05633.

- Hongyu Zhou, Yinan Zhang, Aixin Sun, and Zhiqi Shen. 2025a. Does multimodality improve recommender systems as expected? a critical analysis and future directions. Preprint, arXiv:2508.05377.

- Hongyu Zhou, Xin Zhou, Lingzi Zhang, and Zhiqi Shen. 2023a. Enhancing dyadic relations with homogeneous graphs for multimodal recommendation. arXiv preprint arXiv:2301.12097.

- Xin Zhou. 2023. Mmrec: Simplifying multimodal recommendation. In Proceedings of the 5th ACM International Conference on Multimedia in Asia Workshops, pages 1–2.

- Xin Zhou and Zhiqi Shen. 2023. A tale of two graphs: Freezing and denoising graph structures for multimodal recommendation. In Proceedings of the 31st ACM international conference on multimedia, pages 935–943.

- Xin Zhou, Xiaoxiong Zhang, Dusit Niyato, and Zhiqi Shen. 2025b. Learning item representations directly from multimodal features for effective recommendation. arXiv preprint arXiv:2505.04960.

- Xin Zhou, Hongyu Zhou, Yong Liu, Zhiwei Zeng, Chunyan Miao, Pengwei Wang, Yuan You, and Feijun Jiang. 2023b. Bootstrap latent representations for multi-modal recommendation. In Proceedings of the ACM web conference 2023, pages 845–854.
