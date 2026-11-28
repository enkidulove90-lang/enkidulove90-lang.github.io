---

title: "TSPORec：用偏好优化为LLM序列推荐挑选信息Token"

date: 2026-08-10

year: 2026

venue_type: arXiv预印本

venue_name: arXiv

categories: [推荐系统, 论文速递]

tags: [论文速读]

slug: paper-2608.09605

---

> 论文：[arXiv 2608.09605](https://arxiv.org/abs/2608.09605) · 代码：[GitHub](https://github.com/WNQzhu/TSPORec.git) · PDF：[本地阅读](https://app.notion.com/papers/2608.09605.pdf)

基于大语言模型的序列推荐把物品的标题、描述、标签等文本编码成物品嵌入，再交给用户侧模型聚合出用户表示。这条路线之所以有效，是因为LLM能同时利用丰富的语义信息和用户历史中的异构偏好；但代价也很直接：一次推理要处理“序列长度 × 每物品Token数”的输入，计算和显存开销都随文本长度线性增长。

为了压住成本，现有做法普遍只截取物品描述的前若干个Token。这个选择看似中性，实际上把“哪些文本值得读”这一信息筛选问题固化成了一个与内容无关的位置先验：描述开头往往是套话、模板或通用标签，真正有区分度的实体、属性、风格词可能出现在更靠后的位置。论文把这一矛盾摆到台面上：能否在全文范围内识别信息量最高的Token，既提升推荐效果，又缩短输入序列？

TSPORec 的答案不是设计一个新的打分函数直接排序，而是把Token选择本身当作一个可学习的策略，用推荐任务自身的反馈来训练它。它的真实地位在于把“输入压缩”从预处理技巧提升为与推荐目标联合优化的决策问题，并且给出了一个绕开子集指数级枚举的代理奖励构造。

这一方法有明确的前置条件：需要一个已经预训练好的LLM推荐底座（论文以HLLM式用户LLM/物品LLM结构为基座），需要物品全文可获取，并且接受一次性多出的训练开销。它面向的是部署期推理成本敏感、而训练可以离线完成的场景——这也解释了论文为何把效率论证放在“物品嵌入离线预计算”和“用户与物品LLM均在线”两种服务形态下分别给出。

## 一、方法：三阶段流水线与代理奖励驱动的Token选择

TSPORec 把问题写成：给定物品Token序列 T=\{t_1,\dots,t_n\}，传统方法取前 k 个Token得到 \mathbf{e}_i=\mathrm{LLM}(t_1,\dots,t_k)；TSPORec 则要学出一个信息性子集 T_k\subseteq T，用 \mathbf{e}_i'=\mathrm{LLM}(T_k) 替代前缀嵌入。选择在chunk级别进行：从序列中挑出 \lfloor k/c\rfloor 个连续Token块，c 为块大小，c=1 即退化为Token级选择。这个粒度参数是后文消融的核心变量。

![TSPORec 三阶段训练流水线](/images/8a50f5e3f2ee1a912f3fa8023b27253e.png)

读这张图可以按从左到右的三段来看。第一段是预训练：用户LLM与物品LLM用InfoNCE损失联合训练，物品嵌入取序列末尾特殊Token `[ITEM]` 的最后一层隐状态 \mathbf{h}_{k+1}，这一步为后续奖励计算提供“裁判”。第二段是策略学习：LLM主干被冻结，只挂一个可学习的策略头，它用query-key注意力给每个Token打重要性分，再按softmax概率采样出Token块；同一段历史被独立采样两次，得到两条子序列，分别经冻结的用户/物品LLM得到两个用户嵌入，与完整物品嵌入做交叉熵比较，胜者获得奖励，策略据此更新。第三段是选择与重训：用训练好的策略在全量数据上挑出高概率chunk，构造精炼数据集，重新训练推荐模型。三段之间的数据流是单向的——预训练产物只作为冻结裁判，策略只改“读哪些Token”，不改LLM权重。

策略头的打分是双向的。对Token t_i，重要性为 \mathrm{info}(t_i)=\langle W_Q\mathbf{h}_i, W_K\mathbf{h}_{k+1}\rangle/\sqrt{d}，其中 \mathbf{h}_{k+1} 是预训练得到的物品嵌入。这意味着分数同时来自标准注意力编码的语义信息，以及预训练物品嵌入携带的协同过滤信号。论文在分析top-k logit策略失效时明确把原因归到“单向注意力无法有效捕捉跨序列的协同信号”，这正是双向设计要解决的问题。

代理奖励是全文最关键的机制。穷举所有Token子集是指数级复杂度，TSPORec 改为对同一交互历史做两次独立采样，得到 \mathcal{I}_M' 与 \mathcal{I}_M''，分别构造用户嵌入 \mathbf{e}_u'、\mathbf{e}_u''，再各自与完整物品嵌入 \mathbf{e}_i 及 N 个负样本计算交叉熵 \mathcal{L}_{\mathrm{ce}}^1、\mathcal{L}_{\mathrm{ce}}^2。奖励定义为：若 \mathcal{L}_{\mathrm{ce}}^1\le\mathcal{L}_{\mathrm{ce}}^2 则 r=1，否则 r=-1。优化目标为 \mathcal{R}(\theta)=\mathbb{E}[r\cdot(\log P(\mathcal{I}_M'\mid\theta)-\log P(\mathcal{I}_M''\mid\theta))]。直观上，交叉熵更低意味着该子序列构造的用户嵌入更接近真实偏好分布，策略被推去提高“更好那一次采样”的似然。论文的Theorem 1给出三条性质：交叉熵越小对应KL散度意义下越紧的偏好分布近似；两次采样共有的chunk梯度相互抵消、不参与更新；该目标确实提升信息性chunk的概率、压低其余chunk。

第三阶段把策略用于全量数据：chunk c 的概率定义为其内部Token概率之积 P(c)=\prod_{i=1}^{|c|}p_i，按此挑出高概率块，重建数据集后重训。一个实现细节是，由于起始Token占据独立特征空间，TSPORec 在所有采样序列中保留前16个Token作为前缀，不参与筛选。

## 二、实验：两个数据集、六个基线与效率账本

实验任务是序列推荐，采用leave-one-out协议：最近一次交互作测试、倒数第二次作验证、其余作训练。主实验用Qwen3-Embedding-0.6B作主干、文本截断64 Token、chunk size为8；泛化实验换TinyLlama-1.1B主干，并把选出的Token用于LLMinit初始化。










主结果如下（Qwen3-Embedding-0.6B，64 Token）：

















最值得对照的不是SASRec，而是同架构的HLLM(first-k)：在Amazon Books上R@5从4.16升到4.37、N@5从2.80升到2.94，六个指标全部同向提升，说明增益来自“选哪些Token”而非换模型。Pixel上的绝对差距更小（R@5 2.80→2.88），但方向一致。论文报告的相对SASRec最高提升为29.29% Recall与31.25% NDCG，平均提升在Books为29.43%、Pixel为16.79%。

Token选择策略本身的对比给出了更强的信号：随机选择把HLLM相对SASRec的提升从24.40%压到2.14%，而top-k logits只有+5.36%，甚至不如first-k的+24.40%。这说明“按logit取高分Token”并不是有效的重要性度量，论文将其归因于单向注意力难以携带协同信号——这正是TSPORec双向打分要补的缺口。

![first-k 与 TSPORec 选出的Token分布对比](/images/c5468c0dbcf171982dbcdd4670936ace.png)

这张分布图回答的是“TSPORec到底选走了什么”。横轴是Token，纵轴是计数，两条分布分别对应first-k与TSPORec。阅读时重点看高频区的差异：TSPORec的曲线在高频Token处明显被压低，说明它系统性地过滤掉跨物品共享的“热Token”。这类Token语义特异性低，用户LLM难以靠它们区分物品；把它们换成内容词，物品嵌入才更有判别力。案例研究给出了同一结论的具体形态：在Pixel的样例中，TSPORec删去“released in the summer of In accordance”这类功能词片段，改选“cucumber、endless mode、Penny”等内容词；另一个样例中它删去泛化标签“tag: Cover Song”，改选词曲作者等具体元数据。

长度与效率实验构成第二组证据。在Amazon Books上，HLLM与TSPORec都随Token长度增加而提升；在Pixel上，HLLM在长度继续增加后性能反而下降，说明并非所有Token都有正贡献，噪声Token会伤害推荐。关键结论是：TSPORec仅用64个Token即可达到或超过HLLM用256个Token的性能。推理时间上，物品LLM主导开销且占比随长度上升：64/128/256 Token对应的总时间为326/536/843 ms，其中物品LLM分别为299/509/817 ms，用户LLM稳定在约27 ms。据此，在物品嵌入离线预计算的场景下推理开销降低63.4%，在物品与用户LLM均在线时降低61.3%。






泛化性方面，换用TinyLlama-1.1B主干后，TSPORec在Amazon Books上R@5 4.16、R@10 6.30、N@5 2.78、N@10 3.46，相对HLLM的3.99/6.07/2.66/3.33平均提升4.12%；把TSPORec选出的Token用于LLMinit初始化，R@5从3.29升到3.42、R@10从5.05升到5.23，提升3.76%。这说明选出的Token携带的不只是对某一主干的适配信息，而是可迁移的推荐信号。

粒度消融在Amazon Books、128 Token输入下进行，记训练chunk为 k_1、选择chunk为 k_2。四种配置T16S1、T16S8、T16S16、T16S32相对HLLM平均提升分别为3.54%、2.15%、2.54%、0.53%，全部为正，说明方法对参数不敏感；但随选择chunk增大整体呈下降趋势，更细的选择单元更有效。论文进一步用top-k logits选择验证了同一趋势，并据此论证top-k logits的失效源于单向性，而非打乱了句子结构。

代价方面，三阶段流水线使TSPORec比单阶段基线多约21.5小时训练时间（8×H100集群）。论文的立场是这是一次性成本，部署期推理效率才是长期约束。

## 三、总结

TSPORec 的机制可以概括为：把“读哪些Token”建模为chunk级采样策略，用冻结的预训练推荐模型作裁判，通过两次独立采样的交叉熵比较构造±1代理奖励，绕开子集枚举的指数复杂度，再用策略筛出的Token重训模型。双向打分让Token重要性同时吸收语义注意力与协同过滤信号，这是它相对top-k logits的关键差异。

证据层面，最硬的对照是同架构的HLLM(first-k)：Amazon Books上六个指标一致提升，R@5 4.16→4.37、N@5 2.80→2.94；策略对比显示随机选择几乎抹平LLM带来的增益（+24.40%→+2.14%），说明Token选择是这条路线不可回避的变量；效率上64 Token追平256 Token，推理开销降低63.4%或61.3%。

边界同样清楚。方法依赖一个已预训练的LLM推荐底座和可获取的物品全文，额外训练时间约21.5小时；主实验集中在两个数据集、两种主干，且chunk消融只在Amazon Books上完成；代理奖励是二值比较信号，其信息量受限于两次采样的区分度。

可迁移的设计启示是：当系统需要在离散的上下文片段上做取舍时，不必先构造一个精确的效用函数，可以用“同一输入两次采样、以下游任务损失定胜负”的相对信号来训练选择器——这种成对比较式的奖励构造，对Agent的工具选择、上下文压缩与记忆筛选模块同样适用。

## References

- Wenqiao Zhu, Chao Xu, Haipang Wu, Ji Liu. *TSPORec: Token Selection via Preference Optimization for LLM-Based Sequential Recommendation.* arXiv:2608.09605. [arXiv](https://arxiv.org/abs/2608.09605) · [代码](https://github.com/WNQzhu/TSPORec.git)

- Junyi Chen, Lu Chi, Bingyue Peng, Zehuan Yuan. *HLLM: Enhancing Sequential Recommendations via Hierarchical Large Language Models for Item and User Modeling.* arXiv:2409.12740.

- Jesse Harte et al. *Leveraging Large Language Models for Sequential Recommendation.* RecSys 2023.

- Yu Cheng et al. *An Image Dataset for Benchmarking Recommender Systems with Raw Pixels.* arXiv:2309.06789.
