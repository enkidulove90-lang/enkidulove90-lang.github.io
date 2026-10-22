---

title: "OpticalRec：面向多模态推荐的统一光学视觉-语言表示"

date: "2026-10-22"

year: "2026"

venue_type: "arxiv预印本"

venue_name: "arXiv"

categories: ["推荐系统", "多模态推荐"]

tags: ["论文速读", "多模态协同过滤", "统一编码", "视觉-语言模型", "光学渲染", "晚期融合", "有效秩"]

slug: "paper-2610.05432"

---

[论文链接](https://arxiv.org/abs/2610.05432)

## 一、研究背景与问题

近年来，视觉-语言建模在编码、检索与推理方面取得显著进展，为推荐系统带来了新的机会：文本与视觉表示能够刻画用户兴趣与物品属性，且大规模视觉-语言预训练得到的表示可迁移到推荐任务。然而，将丰富的多模态特征注入推荐系统仍面临根本瓶颈——主流做法是对视觉与语言模态分别独立编码，再通过求和、拼接或图融合等刚性晚期融合进行整合。这种范式存在两点缺陷：其一，独立编码天然忽略了跨注意力等视觉-语言交互，各模态嵌入处于异构向量空间；其二，有损的晚期融合会扭曲跨模态语义。基于图的方法虽在相似度图上做多模态融合，但其初始图构建仍依赖晚期融合的分离编码，近期工作也多在改进下游图结构而忽视图文交互与破坏性的晚期融合。

据此，作者提出统一空间编码范式应满足两个条件：多模态内容应在统一输入空间中呈现以支持丰富的视觉-语言交互；统一输入应被一次性编码为同质嵌入空间，无需额外的破坏性晚期融合。受此启发，论文提出 OpticalRec——一个轻量、即插即用的统一编码框架。它通过一次高效的渲染操作将物品文本元数据转换为视觉字形，使图像与文本在视觉编码器内于统一像素空间发生丰富交互，这也契合“以用户所见方式观看”的原则：用户浏览商品时会在图片与文字之间来回切换注意力。随后表示再经语言解码器处理，形成双重注意力机制，并在无晚期融合的情况下输出同质嵌入。论文的主要贡献包括：(1) 提出首个面向多模态协同过滤的视觉空间统一编码框架，支持基于双重注意力的图文跨模态交互；(2) 在不使用有损晚期融合的前提下保留视觉-语言相关性，并通过互信息与矩阵有效秩给出理论分析；(3) 在多个 Amazon Review 基准与多种推荐骨干上验证了相对强多模态基线编码器的一致提升；(4) 框架轻量、即插即用，且对输入布局、文字颜色与字体等具有鲁棒性。

## 二、方法

论文首先形式化多模态协同过滤（MMCF）任务：用户集合与物品集合分别记为 U 与 I，物品 i 由图像 v_i 与文本描述 t_i 描述，物品嵌入 q_i = f(v_i, t_i)，用户表示 p_u 由聚合函数 A 对其交互物品嵌入聚合得到，推荐器 F 进一步结合用户-物品图 G 变换得到 (p_u', q_i')，最终以二者内积作为推荐得分。

在编码范式上，论文将独立编码加晚期融合与 OpticalRec 均表述为马尔可夫链。独立编码先用视觉与语言编码器 f_V、f_T 分别得到模态特定向量 (z_i^v, z_i^t)，再经融合算子 g 得到 q_i^LF；基于提示的编码虽在语言解码器层引入视觉-语言交互，但图像与文本仍分别编码，投影后的图像 token 与文本 token 拼接本身即是一种晚期融合。

OpticalRec 则先通过高效渲染操作 R(·) 将物品图像 v_i、文本描述 t_i 以及遵循商品页面视觉组织方式的图文布局结构 s_i^vt 统一映射到同质像素空间，得到渲染后的物品卡片 ṽ_i = R(v_i, t_i, s_i^vt)。渲染在离线阶段一次性完成，开销可忽略，具体步骤为：创建 m×m 像素的方形空白画布并设定图像高度 h（h<m）；按原始宽高比将物品图像缩放至高度 h 并调整宽度 w；按物品 id 检索 {标题、品牌、类别、价格} 文本元数据，渲染到剩余的 m×(m−h) 区域，布局与配色大致遵循亚马逊网站风格。随后统一输入 ṽ_i 由单一冻结的视觉-语言编码器 f_Φ 映射为最终嵌入 z_i^OR = q_i^OR。由此，OpticalRec 在视觉编码器（感知层）与语言解码器（语义层）两个阶段实现双重注意力的视觉-语言交互，其中感知层的图文区域匹配此前未在 MMCF 编码中被探索。

理论分析方面，论文引入互信息差：OpticalRec 嵌入与晚期融合嵌入关于原始图文输入的信息量之差，可分解为统一编码带来的跨模态信息增益与晚期融合造成的信息损失两项。前者为正，因为独立编码无法完整保留跨模态信息，而 OpticalRec 将两种模态暴露于统一视觉-语言编码器；后者为正，因为晚期融合 q_i^LF = g(z_i^LF) 构成马尔可夫链，由数据处理不等式可知融合后信息不增，且对有损融合严格减少。附录进一步给出跨模态交互预算的估算，说明该差距在实际规模下相当可观。此外，论文采用矩阵有效秩 erank(X) = exp(−Σ p_i log p_i)（p_i 为归一化奇异值分布）衡量表示的信息丰富度，值越低表示表示坍缩，越高表示信息分布越丰富。

![方法图 1](/images/b7842d2e931f548a95e4223eccad9071.png)

该图对比三种编码范式：(a) 传统独立编码加晚期融合，图像与文本分别编码后才做有损刚性融合，中间没有任何跨模态交互；(b) 基于提示的 VLM 编码，两模态仍分别编码，仅在语言解码器层通过 token 拼接获得语义层交互；(c) OpticalRec 将图像与渲染后的文本字形放入统一视觉空间联合编码，从而在视觉编码器获得块级/感知层交互、在语言解码器获得映射 token 级/语义层交互。图中左上角展示了渲染后的物品卡片示例，所有编码器与 VLM 均冻结、无需训练。

## 三、实验

实验在 Amazon 的三个常用 MMCF 基准上进行：Baby（108,897 用户、17,836 物品、330,771 交互，稀疏度 99.983%）、Pets（461,828 用户、61,060 物品、1,772,584 交互，99.993%）与 Clothing（398,796 用户、75,616 物品、2,109,975 交互，99.993%），预处理采用 5-core 过滤并剔除缺失特征的物品。对比基线包括 VBPR、LATTICE、FREEDOM、BM3 与 LGMRec，并额外构建强提示式 VLM 基线以隔离感知层交互的贡献。主实验使用 Qwen3-VL-8B，所有 VLM 在编码阶段冻结；推荐模型用 AdamW 训练并早停，评价指标为 NDCG@20、Recall@20 与 Hit Ratio@20。

主结果方面，OpticalRec 在所有骨干与数据集上一致优于最强基线：全部模型、指标与数据集上平均提升 2.12%，其中 Pets 提升最大（平均 3.21%，FREEDOM 上 NDCG@20 最高提升 5.82%），Baby 与 Clothing 分别稳定提升 1.65% 与 1.51%；NDCG@20 的提升（2.41%）大于 Recall@20（1.97%），说明不仅检索更强，排序质量也更好；图类骨干受益多于 VBPR，LATTICE、FREEDOM、LGMRec 平均提升分别为 2.29%、2.88%、2.29%，而 VBPR 为 1.09%，表明更丰富的多模态物品表示能进一步促进交互图上的语义传播。附录中以 InternVL3.5-8B 作为编码 VLM 的消融同样显示 OpticalRec 全面最优，相对次优基线平均提升 2.51%，体现即插即用特性。

行为分析方面，注意力可视化显示视觉编码器对商品图像与相关文本区域进行广泛关注，体现感知层的上下文化；语言解码器则呈现更局部的、语义匹配的图像-文本区域注意力，二者互补。PCA 可视化显示 OpticalRec 在图像与文本表示之间形成统一流形，而晚期融合偏向单一模态（VBPR 偏文本、LATTICE 偏图像）。有效秩分析中，OpticalRec 取得最高平均有效秩 155.6，比晚期融合高 22.81%，比最强的单模态基线（纯文本编码）高 11.54%；晚期融合平均有效秩为 126.7，比纯文本编码低 9.18%，出现维度坍缩。附录的 Spearman 相关性研究显示有效秩与 Recall@20 整体呈强正相关（ρ=0.85，p<0.001）。

消融与鲁棒性方面：渲染分辨率在 256×256、544×544、1024×1024 中，544×544 综合最佳，过低或过高均略有下降；对布局（50% 数据随机打乱标题、品牌、类别、价格位置）、字号（±25%）与文字颜色（黑白）的扰动，所有结果相对默认设置偏差均在 ±1% 以内；渲染更长文本（<500、<1000、<1500 字符）可带来约 0.7% 至 1.6% 的提升，且在 1000 字符阈值附近趋于饱和，说明默认仅用标题、品牌、类别、价格已提供较强推荐信号。效率方面，渲染为一次性离线过程：Baby 的 17,836 个物品耗时 13.5 分钟、占用 2.4 GB；Pets 的 61,060 个物品耗时 46.0 分钟、占用 8.1 GB；Clothing 的 75,616 个物品耗时 57.0 分钟、占用 10.1 GB（均为 8 个 worker、每秒 22 张卡片）。

![实验图 1](/images/d8b8b9839d91ac00a0b949924f6d1d24.png)

该图以一张圣诞猫衣服物品卡片为例，分别以“Cat”“Christmas”“Clothes”对应的图像块为查询，可视化 Qwen3-VL-8B 视觉编码器（上排，对应框架中的紫色部分）与语言解码器（下排，对应绿色部分）的注意力分布，颜色越亮表示注意力越高。可以看到视觉编码器的注意力较广泛地覆盖商品图像与相关文字区域，体现感知层的上下文化；语言解码器则更集中地聚焦于语义匹配的图文区域，体现语义层的对齐，二者互补印证了双重注意力机制。

![实验图 2](/images/97699852911cc482786d0e8dd36d29b6.png)

该图在图类骨干下对物品表示做 PCA 降维，并以 50% 置信椭圆展示分布。OpticalRec（橙色）在图像与文本表示之间形成统一的分布流形，说明视觉-语言对齐更强；而晚期融合（紫色）明显偏向单一模态，表明事后融合难以平衡异构的模态分布。

![实验图 3](/images/50714a45e32991bbdc88bfd4f74f95ef.png)

该图比较单模态编码、晚期融合与 OpticalRec 的矩阵有效秩。灰色区域突出显示晚期融合造成的有效秩下降，而 OpticalRec 在各设置下始终最高，说明其嵌入空间保留了更丰富的视觉-语言变化信息，晚期融合则出现维度坍缩。

![实验图 4](/images/67aa0e3d7013bcfb3b2cfbe472490721.png)

该图与上一张有效秩图并列呈现，进一步从不同数据集或骨干角度展示单模态编码、晚期融合与 OpticalRec 的有效秩对比，同样显示 OpticalRec 的表示信息量最高、晚期融合存在明显的信息损失。

![实验图 5](/images/87cb039df99eeade9b16619dd32a5395.png)

该图展示不同物品卡片渲染分辨率下的推荐性能。544×544 在多个数据集与模型上综合表现最佳，更低或更高分辨率都会带来轻微下降，说明中等分辨率已足以保留视觉-语言语义，可避免不必要的高分辨率 VLM 推理并降低分辨率调参成本。

![实验图 6](/images/daeb919041a5b5d227a6ce3dc23a172c.png)

该图与分辨率图并列，从另一组数据集或模型角度补充展示渲染分辨率对性能的影响，同样支持 544×544 为高效部署下的稳健选择这一结论。

## 四、总结

论文提出 OpticalRec，一种面向多模态协同过滤的统一光学视觉-语言编码框架。通过将物品文本与图像渲染到共享视觉空间，OpticalRec 在避免破坏性晚期融合的同时，实现了感知层与语义层互补的跨模态交互。大量实验表明其在多个数据集与推荐骨干上取得一致增益，并伴随更优的嵌入质量、对渲染变化的鲁棒性以及可接受的一次性预处理开销，说明统一光学编码是替代传统独立多模态编码表示的简单而有效的方案。作者也指出局限：本文在基于特征的多模态协同过滤这一大规模物品编码的主流设定下研究统一光学编码，虽已评估多种骨干、渲染设置、文本长度与 VLM 规模，但向视频推荐等更多推荐领域的扩展验证仍有待未来研究。

## References

- Shuai Bai, Yuxuan Cai, and 1 others. 2025. Qwen3-vl technical report. Preprint, arXiv:2511.21631.

- Jingyuan Chen, Hanwang Zhang, Xiangnan He, Liqiang Nie, Wei Liu, and Tat-Seng Chua. 2017. Attentive collaborative filtering: Multimedia recommendation with item-and component-level attention. In Proceedings of the 40th International ACM SIGIR conference on Research and Development in Information Retrieval, pages 335–344.

- Thomas M. Cover and Joy A. Thomas. 2006. Elements of Information Theory, 2nd edition. John Wiley & Sons, Hoboken, NJ.

- Zhiqiang Guo, Jianjun Li, Guohui Li, Chaoyang Wang, Si Shi, and Bin Ruan. 2024. Lgmrec: Local and global graph learning for multimodal recommendation. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 38, pages 8454–8462.

- Ruining He and Julian McAuley. 2016. Vbpr: visual bayesian personalized ranking from implicit feedback. In Proceedings of the AAAI conference on artificial intelligence, volume 30.

- Yicheng He, Zhou Kaiyu, Haoyue Bai, Fengbin Zhu, and Yonghui Yang. 2025. Understanding embedding scaling in collaborative filtering. arXiv preprint arXiv:2509.15709.

- Yupeng Hou, Jiacheng Li, Zhankui He, An Yan, Xiusi Chen, and Julian McAuley. 2024. Bridging language and items for retrieval and recommendation. Preprint, arXiv:2403.03952.

- Kibum Kim, Jiwan Kim, Kyle Min, Yueqi Wang, Jinyoung Moon, Julian McAuley, and Chanyoung Park. 2026. Sink-token-aware pruning for fine-grained video understanding in efficient video llms. arXiv preprint arXiv:2604.20937.

- Zijie Lei, Tao Feng, Zhigang Hua, Yan Xie, Guanyu Lin, Shuang Yang, Ge Liu, and Jiaxuan You. 2026. Unirec: Unified multimodal encoding for llm-based recommendations. arXiv preprint arXiv:2601.19423.

- Bo Li, Yuanhan Zhang, Dong Guo, Renrui Zhang, Feng Li, Hao Zhang, Kaichen Zhang, Peiyuan Zhang, Yanwei Li, Ziwei Liu, and 1 others. 2024a. Llava-onevision: Easy visual task transfer. arXiv preprint arXiv:2408.03326.

- Feng Li, Renrui Zhang, Hao Zhang, Yuanhan Zhang, Bo Li, Wei Li, Zejun Ma, and Chunyuan Li. 2024b. Llava-next-interleave: Tackling multi-image, video, and 3d in large multimodal models. arXiv preprint arXiv:2407.07895.

- Guohui Li, Li Zou, Zhiying Deng, and Qi Chen. 2024c. Neighborhood-enhanced multimodal collaborative filtering for item cold start recommendation. In ICASSP 2024-2024 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), pages 7815–7819. IEEE.

- Kang Liu, Feng Xue, Dan Guo, Le Wu, Shujie Li, and Richang Hong. 2023. Megcf: Multimodal entity graph collaborative filtering for personalized recommendation. ACM transactions on information systems, 41(2):1–27.

- Shiqin Liu, Chaozhuo Li, Minjun Zhao, Litian Zhang, and Jiajun Bu. 2025. Modalsync: Synchronizing user behavior with multimodal features for multimodal pre-training recommendation. In Companion Proceedings of the ACM on Web Conference 2025, pages 2278–2287.

- Daniele Malitesta, Giandomenico Cornacchia, Claudio Pomo, Felice Antonio Merra, Tommaso Di Noia, and Eugenio Di Sciascio. 2025. Formalizing multimedia recommendation through multimodal deep learning. ACM Transactions on Recommender Systems, 3(3):1–33.

- Daniele Malitesta, Emanuele Rossi, Claudio Pomo, Tommaso Di Noia, and Fragkiskos D Malliaros. 2024. Do we really need to drop items with missing modalities in multimodal recommendation? In Proceedings of the 33rd ACM International Conference on Information and Knowledge Management, pages 3943–3948.

- Rongqing Kenneth Ong and Andy WH Khong. 2025. Spectrum-based modality representation fusion graph convolutional network for multimodal recommendation. In Proceedings of the Eighteenth ACM International Conference on Web Search and Data Mining, pages 773–781.

- OpenAI. 2026. Openai gpt-5 system card. Preprint, arXiv:2601.03267.

- OpenGV. 2025. Internvl3.5: Advancing open-source multimodal models in versatility, reasoning, and efficiency. Preprint, arXiv:2508.18265.

- Claudio Pomo, Matteo Attimonelli, Danilo Danese, Fedelucio Narducci, and Tommaso Di Noia. 2025. Do recommender systems really leverage multimodal content? a comprehensive analysis on multimodal representations for recommendation. In Proceedings of the 34th ACM International Conference on Information and Knowledge Management, pages 2377–2387.

- Shutong Qiao, Wei Yuan, Tong Chen, Xiangyu Zhao, Quoc Viet Hung Nguyen, and Hongzhi Yin. 2026. When text-as-vision meets semantic ids in generative recommendation: An empirical study. arXiv preprint arXiv:2601.14697.

- Olivier Roy and Martin Vetterli. 2007. The effective rank: A measure of effective dimensionality. In 2007 15th European signal processing conference, pages 606–610. IEEE.

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
