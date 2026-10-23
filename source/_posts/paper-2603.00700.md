---

title: "面向生成式推荐的分布级对比监督"

date: "2026-10-23"

year: "2026"

venue_type: "会议"

venue_name: "RecSys '26"

categories: ["推荐系统", "生成式推荐"]

tags: ["论文速读", "生成式推荐", "分布级监督", "对比监督", "贝叶斯个性化排序", "RQ-VAE", "码本分布"]

slug: "paper-2603.00700"

---

[论文链接](https://arxiv.org/abs/2603.00700) · [代码链接](https://github.com/freyasa/SODA)

## 一、研究背景与问题

生成式推荐通过在紧凑的令牌空间中运作，已成为传统“检索—排序”流水线的一种可扩展替代方案。它通常由两个核心组件构成：一是分词器（tokenizer），将每个物品映射为从多层预定义码本中取出的离散码序列；二是生成式推荐器，基于令牌化的用户交互历史自回归地预测下一个物品。由于在紧凑的令牌空间中运作，生成式推荐器避免了穷举式候选比较，从而能够在大规模物品语料上实现可扩展且高效的推荐。

早期方法采用解耦的训练流程：先优化分词器以生成物品码，随后在推荐器训练时将其冻结。这种做法虽然直接，但限制了分词器与推荐器的联合演化。为缓解这一问题，近期工作提出了交替优化框架，使分词器与推荐器迭代训练。从分词器的角度看，这类方法能更好地将码生成与推荐目标对齐，增强码的适应性。然而，即便在更强的耦合下，推荐器仍主要受硬离散令牌标签监督，分词器所保留的更丰富的分布分配信息并未被显式传递给推荐器，这可能导致信息损失与次优性能。

为充分利用分词器编码的丰富语义信息，本文超越码级监督，引入分布级监督：不再将离散码作为唯一的监督信号，而是利用多层码本上的概率分布作为柔性且信息丰富的表示。将这些分布作为辅助监督，可使推荐器捕捉细粒度语义差异并提升表示保真度，从而促进联合优化、增强两个组件之间的协同。

基于这一思路，本文提出一种面向推荐器的新型对比监督策略，其建立在贝叶斯个性化排序（BPR）损失之上，鼓励模型对正项赋予比负项更高的分数。为将该原则扩展到分布级监督，推荐器提取用户历史表示，再由分词器将其映射为码本分布。一对分布之间的匹配分数定义为负 KL 散度。本文将这一即插即用的方法称为语义导向分布对齐（Semantic-Oriented Distributional Alignment, SODA），它促使推荐器对齐语义丰富的分布，同时实现与分词器的有效联合训练。在多个真实数据集上的实验表明，将 SODA 融入现有生成式推荐主干可稳定带来性能提升。

本文的主要贡献如下：（1）提出面向生成式推荐的分布级对比监督，使推荐器能够捕捉分词器编码的细粒度语义信息，超越传统的码级信号；（2）提出 SODA，一个即插即用的分布级对比监督框架，利用分词器诱导的码本分布作为辅助监督目标，实现推荐器侧的语义对齐；（3）在多个真实数据集上开展大量实验，验证 SODA 在多种生成式推荐主干上的有效性。

## 二、方法

本节先形式化生成式推荐任务，再介绍所提方法。

**任务形式化。** 本文将生成式推荐建模为序列到序列任务：给定用户交互历史 $x$，目标是预测目标物品 $y$。框架由两个耦合组件构成：分词器 $\mathcal{T}$ 与生成式推荐器 $\mathcal{R}$。

**物品令牌化。** 采用 RQ-VAE 作为分词器 $\mathcal{T}$，将嵌入为 $\bm{z}_i$ 的物品 $i$ 映射为离散令牌序列。编码器 $\mathcal{E}_{\mathcal{T}}$ 将 $\bm{z}_i$ 投影为潜在向量，并用 $L$ 个码本 $\mathcal{C} = \{\mathcal{C}_l\}_{l=1}^L$ 递归量化得到令牌序列 $(c_1, \dots, c_L)$，再经解码器 $\mathcal{D}_{\mathcal{T}}$ 重建得到 $\tilde{\bm{z}}_i$：

$$

c_l = \arg\min_k \lVert \bm{v}_l - \bm{e}_l^k \rVert^2, \quad \bm{v}_l = \bm{v}_{l-1} - \bm{e}_{l-1}^{c_{l-1}}, \quad \bm{v}_1 = \mathcal{E}_{\mathcal{T}}(\bm{z}_i),

$$

$$

\tilde{\bm{z}}_i = \mathcal{D}_{\mathcal{T}}\left(\sum_{l=1}^L \bm{e}_l^{c_l}\right),

$$

其中 $\bm{e}_l^k$ 表示码本 $\mathcal{C}_l$ 中的第 $k$ 个码字。分词器通过最小化重建与量化损失进行训练：

$$

\mathcal{L}_\text{token} = \lVert \tilde{\bm{z}}_i - \bm{z}_i \rVert^2 + \sum_{l=1}^{L} \Big( \lVert \text{sg}(\bm{v}_l) - \bm{e}_l^{c_l} \rVert^2 + \alpha \lVert \bm{v}_l - \text{sg}(\bm{e}_l^{c_l}) \rVert^2 \Big),

$$

其中 $\text{sg}(\cdot)$ 表示停止梯度算子，$\alpha$ 为权重。

**生成式推荐。** 给定分词器得到的令牌化用户历史 $X$ 与目标物品序列 $Y$，推荐器 $\mathcal{R}$ 是一个 Transformer 编码器—解码器模型，通过将 $X$ 编码为上下文表示并生成解码器状态，自回归地从 $X$ 预测 $Y$，其训练损失为：

$$

\mathcal{L}_{\text{rec}} = -\sum_{l=1}^{L} \log P(Y_l \mid X, Y_{<l}).

$$

**SODA 框架。** SODA 是一个即插即用的分布级对比监督框架，在离散令牌匹配之外引入额外监督。

**监督策略。** 推荐本质上是一个相对匹配问题：当前用户历史应比不匹配的物品或历史更接近目标物品。本文为推荐器引入基于 BPR 损失的额外优化目标，鼓励模型对正表示赋予比负表示更高的匹配分数：

$$

\mathcal{L}_{\text{SODA}} = - \log \sigma \left( \beta \cdot (s(h^+, h^y) - s(h^-, h^y)) \right),

$$

其中 $h^y$ 表示目标物品的分布表示，$h^+$ 与 $h^-$ 分别表示正历史与负历史的分布表示；$h^+$ 来自当前用户，$h^-$ 则按批内负采样惯例由小批量中的其他用户构造。分布匹配函数 $s(\cdot,\cdot)$ 基于负对称 KL 散度定义：

$$

s(h^a, h^b) = - \Big(\mathrm{KL}(h^a \,\|\, h^b) + \mathrm{KL}(h^b \,\|\, h^a)\Big) / 2.

$$

**分布表示。** 对于目标表示 $h^y$，编码其语义嵌入 $\bm{z}_y$，度量所得潜在表示在每一层与所有码字的亲和度，并将亲和度归一化为概率分布：

$$

p_{l,k} = \frac{\exp(-\|\bm{v}_l - \bm{e}_l^k\|^2 / \tau)}{\sum_{j=1}^K \exp(-\|\bm{v}_l - \bm{e}_l^j\|^2 / \tau)},

$$

其中 $\tau$ 为温度参数。该形式是硬分配的一种软松弛，得到分布表示 $h^y = \{ p_{l,k}(y) \}_{l=1:L,\; k=1:K}$。

对于 $h^+/h^-$，二者在共享的分词器语义空间中由用户交互历史导出。给定用户交互序列 $x$，用推荐器编码其令牌化历史 $X$，并将所得表示投影到分词器码本空间：

$$

\bm{r}_x = \text{MLP}(\text{AvgPool}( \mathcal{E}_{\mathcal{R}}(X) )),

$$

其中 $\mathcal{E}_{\mathcal{R}}$ 为推荐器编码器。对 $\bm{r}_x$ 施加同样的软量化得到 $h^+=\{p_{l,k}^+\}_{l,k}$，而 $h^-=\{p_{l,k}^-\}_{l,k}$ 为批内其他用户分布的逐层平均，从而提供稳定的非目标参照，较少受语义相关假阴性影响。

**训练流程。** 遵循先前的交替优化策略，先以 $\mathcal{L}_{\text{token}}$ 预训练分词器 $\mathcal{T}$ 以建立稳定的离散潜在空间，随后交替优化推荐器 $\mathcal{R}$ 与分词器 $\mathcal{T}$。SODA 目标 $\mathcal{L}_{\text{SODA}}$ 在交替训练过程中被纳入推荐器 $\mathcal{R}$ 的优化。推荐器的总体训练目标为：

$$

\mathcal{L} = \mathcal{L}_{\text{rec}} + \lambda \, \mathcal{L}_{\text{SODA}},

$$

其中 $\lambda$ 为控制 SODA 监督贡献的超参数。将 SODA 应用于特定生成式推荐主干（如 ETEGRec）时，总体目标还可包含其他辅助损失。SODA 不引入推理开销，训练时间增加不到 5%。

![方法图 1](/images/a917d3b279d4a52b9c983995aa11ed65.png)

图中上路由分词器把目标物品映射为多层码本概率分布，下路由推荐器把用户历史映射为正、负分布；三者通过对称 KL 散度构造 SODA 对比损失，体现了分布级监督如何连接分词器与推荐器。

## 三、实验

本节通过实验回答两个研究问题。RQ1：SODA 应用于现有生成式推荐方法时表现如何？RQ2：各组成部分对 SODA 整体有效性的贡献如何？

**实验设置。** 实验在三个真实数据集上进行：两个公开的 Amazon Review 基准（Beauty 与 Pet）以及来自在线自由职业平台的专有数据集 Upwork。在 Upwork 中，每次交互是一次带时间戳的雇佣事件，雇主为用户、自由职业者为物品。数据集统计如下：Beauty 含 22362 用户、12083 物品、198313 次交互，稀疏度 99.93%，平均序列长度 8.87；Pet 含 19855 用户、8498 物品、157747 次交互，稀疏度 99.91%，平均序列长度 7.95；Upwork 含 15542 用户、33508 物品、139217 次交互，稀疏度 99.97%，平均序列长度 8.96。遵循先前研究，采用 5-core 过滤，仅保留交互数不少于 5 的用户与物品；每个用户序列按最近交互截断或填充至长度 20；评估采用留一法划分。

基线分为两类：（1）传统推荐方法：Caser、GRU4Rec、SASRec、BERT4Rec、HGN；（2）生成式推荐方法：TIGER、LETTER、ETEGRec。由于 SODA 是即插即用框架，将其分别应用于各生成式主干，得到 SODA-T、SODA-L 与 SODA-E 进行对比。评估采用 top-$K$ 推荐的两个常用指标 Recall@$K$ 与 NDCG@$K$，$K \in \{10, 20\}$。为保证评估无偏，在整个物品集上执行全排序而非负采样；所有生成式方法在推理时使用束大小为 30 的受限束搜索。

实现细节方面，采用 RQ-VAE 作为分词器、T5 作为推荐器。Beauty 与 Pet 数据集的初始物品语义嵌入由 \texttt{sentence-t5-base} 从物品标题与描述中提取（768 维）。超参数 $\lambda$ 在 $\{1e\!-\!2, \dots, 1e\!-\!6\}$ 中按数量级调优，温度 $\tau$ 在 $\{1, \dots, 1e\!-\!5\}$ 中调优，缩放因子 $\beta$ 在 $\{1, \dots, 1000\}$ 中调优。传统基线使用开源库 RecBole 的实现，其余生成式推荐模型配置与训练设置遵循先前工作。

**主要结果（RQ1）。** 在三个数据集上的整体性能对比显示：将 SODA 应用于多种生成式推荐主干可稳定提升其性能，这归因于分布级监督缓解了基于码的方法中刚性离散化造成的信息损失，利用概率分布作为软表示可捕捉细粒度语义差异；同时，生成式方法总体优于传统基于 ID 的基线方法，说明生成式方法在利用分词器提供的丰富语义信息（而非随机 ID）的同时能够捕捉复杂协同信号，验证了生成式推荐范式的有效性。

**消融研究（RQ2）。** 通过逐步移除各关键组件进行消融，报告 Beauty 数据集上 SODA-T 与 SODA-L 的结果，其他数据集与主干呈现一致趋势。对比的变体包括：w/o neg，移除负项、将 BPR 对比目标替换为仅建模正历史—目标关系的逐点损失；w/o loss，完全移除 $\mathcal{L}_{\text{SODA}}$，仅依赖离散码级监督；w/o alter，采用标准 TIGER/LETTER 的解耦优化而非交替训练。结果显示：w/o neg 与 w/o loss 均持续导致性能下降，表明分布级监督提供了超越码级监督的细粒度语义信号，而对比负样本进一步提升了表示判别力以及用户历史与目标物品之间的语义对齐；w/o alter 变体表现较差，因为移除交替优化会固定物品码、使其无法适应推荐上下文，说明动态更新、推荐感知的令牌表示具有收益。

![实验图 1](/images/35d42d8a7eda487f1b897e5dd166e2e1.png)

主结果表比较 Beauty、Pet 与 Upwork 上的传统模型和三种生成式主干。加粗列显示 SODA-T、SODA-L、SODA-E 相对各自主干在 Recall 与 NDCG 指标上的变化，用于检验框架跨数据集与跨主干的稳定性。

![实验图 2](/images/91170c1b1f644eb7c9caf3c1d0ed0bbb.png)

消融表在 Beauty 数据集上分别移除负项、分布级损失与交替优化。各变体的 Recall 和 NDCG 均可与完整 SODA-T、SODA-L 直接对照，从而区分对比负样本、软分布监督和交替训练的贡献。

## 四、总结

本文提出了 SODA，一个即插即用的分布级监督框架，通过基于负对称 KL 散度的 BPR 目标，将推荐器表示与分词器诱导的码本分布对齐。通过利用离散码之外的细粒度语义，SODA 在不引入推理开销的情况下稳定提升了多种生成式推荐主干。未来工作方面，计划在大规模工业推荐数据集上评估该方法的可扩展性，以进一步考察其在超大规模物品语料上的鲁棒性与效率。

## References

- Rajput et al. [Recommender Systems with Generative Retrieval (TIGER)](https://scholar.google.com/scholar?q=Recommender+Systems+with+Generative+Retrieval+%28TIGER%29).

- Wang et al. [RQ-VAE: Residual Quantized Variational Autoencoder](https://scholar.google.com/scholar?q=RQ-VAE%3A+Residual+Quantized+Variational+Autoencoder).

- Rendle et al. [BPR: Bayesian Personalized Ranking from Implicit Feedback](https://scholar.google.com/scholar?q=BPR%3A+Bayesian+Personalized+Ranking+from+Implicit+Feedback).

- Wang et al. [LETTER: Learnable Item Tokenization for Generative Recommendation](https://scholar.google.com/scholar?q=LETTER%3A+Learnable+Item+Tokenization+for+Generative+Recommendation).

- Zhou et al. [ETEGRec: Alternating Optimization for Generative Recommendation](https://scholar.google.com/scholar?q=ETEGRec%3A+Alternating+Optimization+for+Generative+Recommendation).

- Raffel et al. [T5: Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer](https://scholar.google.com/scholar?q=T5%3A+Exploring+the+Limits+of+Transfer+Learning+with+a+Unified+Text-to-Text+Transformer).

- Kang and McAuley. [Self-Attentive Sequential Recommendation (SASRec)](https://scholar.google.com/scholar?q=Self-Attentive+Sequential+Recommendation+%28SASRec%29).

- Sun et al. [BERT4Rec: Sequential Recommendation with Bidirectional Encoder Representations](https://scholar.google.com/scholar?q=BERT4Rec%3A+Sequential+Recommendation+with+Bidirectional+Encoder+Representations).

- Hidasi et al. [GRU4Rec: Session-based Recommendations with Recurrent Neural Networks](https://scholar.google.com/scholar?q=GRU4Rec%3A+Session-based+Recommendations+with+Recurrent+Neural+Networks).

- Tang and Wang. [Caser: Personalized Top-N Sequential Recommendation via Convolutional Sequence Embedding](https://scholar.google.com/scholar?q=Caser%3A+Personalized+Top-N+Sequential+Recommendation+via+Convolutional+Sequence+Embedding).

- Ma et al. [HGN: Hierarchical Gating Networks for Sequential Recommendation](https://scholar.google.com/scholar?q=HGN%3A+Hierarchical+Gating+Networks+for+Sequential+Recommendation).

- Zhao et al. [RecBole: A Unified, Comprehensive and Efficient Recommendation Library](https://scholar.google.com/scholar?q=RecBole%3A+A+Unified%2C+Comprehensive+and+Efficient+Recommendation+Library).

- Ni et al. [Sentence-T5: Scalable Sentence Encoders from Pre-trained Text-to-Text Models](https://doi.org/10.18653/v1/2022.findings-acl.146).
