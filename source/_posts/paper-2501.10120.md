---

title: "PaSa：用双智能体与会话级PPO重塑学术搜索"

date: 2026-10-19

year: 2026

venue_type: arXiv预印本

venue_name: ""

categories: [推荐系统, 论文速递]

tags: [论文速读]

slug: paper-2501.10120

---

> 论文：[arXiv 2501.10120](https://arxiv.org/abs/2501.10120) · 代码：[GitHub](https://github.com/bytedance/pasa) · PDF：[本地阅读](https://app.notion.com/papers/2501.10120.pdf)

学术论文搜索是科研工作的核心环节，却也是信息检索中最具挑战性的任务之一。研究者常常需要针对细粒度、长尾的专业问题，从海量文献中找出全面且准确的答案。传统搜索引擎如Google Scholar对一般查询有效，但面对“哪些研究关注基于价值函数、特别是UCB算法的非平稳强化学习”这类复杂查询时，往往力不从心。大语言模型（LLM）的兴起为查询改写和检索增强提供了新思路，但学术搜索远不止一次检索——人类研究者会反复搜索、阅读论文、追溯引用，进行系统性的文献调研。

PaSa正是为了模拟这一完整过程而提出的LLM智能体。它由两个协同工作的智能体构成：Crawler负责最大化召回，通过自主调用搜索工具和扩展引用网络来收集候选论文；Selector负责精确筛选，判断每篇论文是否满足查询要求。两者分工明确，共同完成从查询理解到结果筛选的端到端学术搜索。

然而，训练这样的智能体面临两大矛盾：其一，高质量学术搜索数据稀缺，人工标注成本极高；其二，搜索轨迹可能长达数百篇论文，奖励稀疏且难以直接输入LLM上下文。为此，作者构建了合成数据集AutoScholarQuery（从顶级AI会议论文的Related Work部分自动生成查询-论文对）和真实世界基准RealScholarQuery（50个真实查询，人工标注相关论文），并设计了会话级PPO训练方法，将长轨迹分割为以[Stop]动作结束的会话，引入跨会话折扣因子和Selector作为辅助奖励模型，有效缓解了稀疏奖励和长轨迹问题。

PaSa的部署条件并不苛刻：基于7B参数的Qwen2.5模型，在8张NVIDIA H100 GPU上即可完成训练。搜索工具通过Google API并限定site:[arxiv.org](http://arxiv.org/)和发布时间，论文全文通过ar5iv获取并解析。这些工程选择使得PaSa在有限资源下仍能实现强大的搜索能力。

## 一、方法：双智能体协作与会话级PPO

PaSa的核心是一个双智能体架构，如图1所示。Crawler和Selector各司其职，Crawler负责广泛收集，Selector负责精准判断。

![PaSa架构图](/images/783f0bdcf81a8d30d3e0576d684b0481.png)

图中左侧是Crawler，它接收用户查询，并可以访问论文队列中的论文。Crawler能够自主调用搜索工具、扩展引用或停止处理当前论文，所有收集到的论文被追加到论文队列。右侧是Selector，它阅读队列中的每篇论文，判断其是否满足用户查询的条件。阅读顺序上，先看Crawler的动作循环，再看Selector的筛选环节，就能理解整个数据流：查询进入Crawler，经过多轮搜索和引用扩展形成候选池，再由Selector逐一过滤，最终输出相关论文。这张图支撑了PaSa“先召回后精选”的核心设计主张。

### Crawler：基于MDP的召回引擎

Crawler被建模为token级的马尔可夫决策过程（MDP）。动作空间是LLM的词表，每个token是一个动作。当生成的token匹配预注册的函数名时，对应函数被执行，从而改变智能体状态。Crawler有三个核心动作：[Search]生成搜索查询并调用搜索工具，将结果论文加入队列；[Expand]从当前论文中提取子章节名，将该子章节引用的所有论文加入队列；[Stop]重置上下文到用户查询和队列中的下一篇论文。

图2展示了一个具体的工作流示例。用户查询是“有没有工作分析多模态模型（如视频-文本、图像-文本模型）的缩放定律”。Crawler首先执行多次[Search]，使用多样且互补的查询。随后，它评估动作的长期价值，决定是否深入引用网络。值得注意的是，即使路径上的中间论文与查询不完全匹配，Crawler也能通过深入探索发现许多相关论文。这张图直观地说明了Crawler如何通过搜索和引用扩展的交替进行，逐步扩大召回范围。

![PaSa工作流示例](/images/5566fceef43abc68d85bf60a01f190f1.png)

Crawler的训练分两阶段：先通过模仿学习初始化策略，再使用会话级PPO进行强化学习。奖励设计如公式(1)所示：每发现一篇匹配查询且未在队列中的论文获得奖励α，同时每个动作有成本c(a_t)。由于AutoScholarQuery中的论文只是真实相关论文的子集（引用往往只强调少数关键文献），仅依赖匹配会导致奖励稀疏。因此，作者引入Selector作为辅助奖励模型：只要Selector判断论文相关，或论文在标注集中，都给予奖励。

### 会话级PPO：解决长轨迹与稀疏奖励

直接对完整轨迹做PPO不可行，因为一条轨迹可能包含数百篇论文，上下文过长。作者将轨迹分割为以[Stop]动作结束的会话（session），每个会话的初始状态要么是仅含查询的S_q，要么是含查询和一篇论文的S_{q+p}。在PPO训练时，对每个会话内的动作进行蒙特卡洛采样估计回报，并引入跨会话折扣因子γ1，将后续会话的回报纳入当前估计。同时，加入KL惩罚项防止策略偏离初始策略。

这种设计使得训练可以在会话级别高效采样，同时通过跨会话折扣保持长期回报的连贯性。Selector作为辅助奖励模型，不仅缓解了稀疏奖励，还加速了训练收敛。

### Selector：精准筛选与可解释性

Selector接收查询和论文（标题与摘要），输出一个决策token（True/False）和一段推理依据。决策token放在推理之前，使得Selector可以作为单token奖励模型用于Crawler训练，同时决策token的概率可用于排序搜索结果。Selector通过模仿学习训练，数据由GPT-4o生成并经过筛选。

## 二、实验：合成与真实基准上的全面评估

实验在AutoScholarQuery测试集和RealScholarQuery上进行，基线包括Google、Google Scholar、Google with GPT-4o（用GPT-4o改写查询）、ChatGPT（搜索增强的GPT-4o）、GPT-o1以及PaSa-GPT-4o（用提示实现PaSa）。评估指标包括Recall@20/50/100（针对排序基线）和精确率、召回率（针对非排序基线），以及Crawler召回率（目标论文被Crawler收集的比例）。

### 数据集与实现条件





实现上，Selector和Crawler均基于Qwen2.5-7B，在8张NVIDIA H100 GPU上训练。Selector进行1个epoch的监督微调，学习率1e-5，batch size 4。Crawler先进行1个epoch的模仿学习（12,989条数据），再进行PPO训练（16,000个查询）。搜索工具使用Google API，限定site:[arxiv.org](http://arxiv.org/)和查询日期之前。

### 主结果：7B模型超越GPT-4o智能体

表4和表5分别展示了在AutoScholarQuery测试集和RealScholarQuery上的结果。

**AutoScholarQuery测试集**











*ChatGPT基线在100个随机采样子集上评估。

在AutoScholarQuery上，PaSa-7b相比最强基线PaSa-GPT-4o，召回率提升9.64%（0.4834 vs 0.3873），精确率相当（0.1448 vs 0.1457）。Crawler召回率也高出3.66%（0.7931 vs 0.7565）。与最佳Google基线Google with GPT-4o相比，PaSa-7b在Recall@20、Recall@50、Recall@100上分别提升33.80%、38.83%和42.64%。集成版本PaSa-7b-ensemble进一步将Crawler召回提升3.34%，最终召回提升1.51%，精确率无显著变化。

**RealScholarQuery**











在更真实的RealScholarQuery上，PaSa-7b的优势更加明显。相比PaSa-GPT-4o，召回率提升30.36%（0.6111 vs 0.3075），精确率提升4.25%（0.5146 vs 0.4721）。与Google with GPT-4o相比，Recall@20、Recall@50、Recall@100分别提升37.78%、39.90%和39.83%。集成版本将Crawler召回提升4.32%，最终召回提升3.52%。

### 消融实验：引用扩展与RL训练的关键作用

表7展示了消融实验结果。







移除[Expand]动作导致召回率大幅下降：AutoScholarQuery上降低22.98%，RealScholarQuery上降低32.21%。这表明引用网络探索是召回的关键。移除RL训练后，召回率分别下降6.24%和19.96%，说明强化学习显著提升了策略性能。移除Selector作为辅助奖励模型，召回率分别下降3.76%和9.63%，验证了辅助奖励对缓解稀疏奖励的有效性。

### 超参数与成本分析

表8展示了奖励系数α的影响。随着α从0.5增加到2.0，Crawler召回率从0.7227升至0.8063，Crawler动作数从175.9增至785.5，但精确率从0.1458略降至0.1409，最终召回率从0.4602升至0.4869。这说明提高奖励可以鼓励更积极的探索，但需在召回与效率间权衡。

表15展示了动作成本c(a_t)的影响。当成本为0时，Crawler召回率0.8239，动作数高达1296.3；成本0.1时，召回率0.7931，动作数382.4；成本0.2时，召回率0.7478，动作数230.1。成本增加会抑制动作数量，降低召回但略微提升精确率（0.1388→0.1489）。这为实际部署中控制计算开销提供了调节手段。

### Selector性能

表6展示了Selector在200个查询-论文对上的评估结果。PaSa-7b-Selector的F1为0.85，精确率0.95，召回率0.78，超过GPT-4o（F1 0.80）和Qwen-2.5-7b（F1 0.55）。将推理放在决策之前（Reason First）性能略降至F1 0.84，说明决策token前置的设计在保持性能的同时提升了训练效率。

## 三、总结

PaSa通过双智能体架构和会话级PPO训练，将学术搜索分解为召回与精选两个阶段，在合成数据和真实基准上均显著超越Google、ChatGPT等强基线。其核心机制在于：Crawler利用[Search]和[Expand]动作自主导航引用网络，最大化召回；Selector作为精确筛选器和辅助奖励模型，缓解稀疏奖励；会话级PPO则解决了长轨迹训练难题。实验证据表明，7B参数的PaSa在RealScholarQuery上召回率比PaSa-GPT-4o提升30.36%，验证了强化学习训练的有效性。

然而，PaSa的局限同样明确：数据集和实验主要集中于机器学习领域，未验证其他学科；模型规模限于7B，更大模型的效果有待探索。此外，搜索依赖Google API和ar5iv解析，工程稳定性可能影响实际部署。

对推荐系统Agent开发的启示在于：双智能体“召回+精排”的架构可直接迁移至推荐系统的候选生成与重排序；会话级PPO为长序列决策提供训练范式；从Related Work自动生成训练数据的方法，可启发从用户行为日志中构建推荐样本。PaSa展示了如何用强化学习将LLM智能体的搜索行为优化为高效、可解释的流程，这一思路值得在更广泛的检索与推荐场景中借鉴。

## References

- He, Y., Huang, G., Feng, P., Lin, Y., Zhang, Y., Li, H., & E, W. (2025). PaSa: An LLM Agent for Comprehensive Academic Paper Search. arXiv:2501.10120. [https://arxiv.org/abs/2501.10120](https://arxiv.org/abs/2501.10120) 代码：[https://github.com/bytedance/pasa](https://github.com/bytedance/pasa)

- Feng, P., et al. (2024). AGILE: A Reinforcement Learning Framework for LLM Agents. （PaSa所基于的RL框架）

- Schulman, J., et al. (2017). Proximal Policy Optimization Algorithms. arXiv:1707.06347.

- Yang, A., et al. (2024). Qwen2.5 Technical Report. arXiv:2412.15115.
