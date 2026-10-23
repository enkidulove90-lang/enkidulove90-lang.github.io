---

title: "AstaBench：用可控文献环境与成本感知排行榜严格评测科研智能体"

date: 2025-10-24

year: 2025

venue_type: arXiv预印本

venue_name: arXiv

categories: [推荐系统, 论文速递]

tags: [论文速读]

slug: paper-2510.21652

---

> 论文：[arXiv 2510.21652](https://arxiv.org/abs/2510.21652) · 代码：[GitHub](https://github.com/UKGovernmentBEIS/inspect) · 代码：[GitHub](https://github.com/laude-institute/terminal-bench) · 代码：[GitHub](https://github.com/mlfoundations/evalchemy) · 代码：[GitHub](https://github.com/princeton-pli/hal-harness) · 代码：[GitHub](https://github.com/soheeyang/unified-prompt-selection) · PDF：[本地阅读](https://app.notion.com/papers/2510.21652.pdf)

AI 智能体被寄望于自动完成文献综述、复现实验、分析数据乃至提出新研究方向，但“哪个智能体真正更强”却难以回答。现有基准往往缺少可复现的工具环境，不控制推理成本与工具访问等混淆变量，任务接口也不统一，导致排行榜上的领先可能来自更贵模型或更全工具，而非核心智能体能力。

AstaBench 的定位正是回应这些缺陷：它不是一个新智能体，而是一套评测方法论、环境、工具链与排行榜的组合。论文首先形式化严格评测智能体的原则，再据此构建覆盖文献理解、编码与执行、数据分析、端到端发现四大类别的 11 个基准，共 2400 多个问题，其中不少来自已部署 Asta 智能体的真实用户请求。

核心矛盾在于：科研任务既需要通用推理，又依赖领域工具与信息检索。若不同智能体访问的文献语料不同，比较就失去意义；若不计成本，重复采样或多数投票就能刷高分数。AstaBench 用生产级文献检索环境固定语料与工具集，用 Inspect 记录模型用量并折算为冻结价格快照下的美元成本，从而把“能力”与“资源”分开。

部署条件方面，AstaBench 提供标准化任务接口，新智能体可较快接入；排行榜同时标注智能体开放程度（开源开放权重、开源闭源权重、闭源 API、仅界面）与工具使用方式（标准、自定义接口、完全自定义），使读者能判断分数背后的控制程度。

## 一、方法：原则、环境与成本感知评测

AstaBench 的方法由三层构成。第一层是评测原则：任务需覆盖完整科研流程、环境需可控可复现、评分需控制成本与工具等混淆变量、接口需对通用智能体友好、基线需足够全面。第二层是 Asta Environment，它提供生产级文献检索工具，让所有智能体在相同语料上检索，从而隔离“信息访问差异”与“规划、工具调用”等核心能力。第三层是 agent-eval 工具包与排行榜：基于 Inspect 记录模型用量，用 litellm 成本表的冻结快照计算归一化美元成本，并支持缓存折扣但不计延迟相关折扣，保证跨时间比较公平。

在任务组织上，11 个基准被归入四个类别。文献理解包括 PaperFindingBench、LitQA2-FullText-Search、ScholarQA-CS2、ArxivDIGESTables-Clean 等；编码与执行包括 SUPER-Expert、CORE-Bench-Hard、DS-1000；数据分析以 DiscoveryBench 为代表；端到端发现包括 E2E-Bench 与 E2E-Bench-Hard。智能体套件包含九类 Asta 专用智能体与多种通用基线，最终实验覆盖 22 个智能体类别、57 个具体智能体。

![文献理解问答基准的分数—成本分析](/images/20fe201b9df2ae8e2eb1f3bf47356ea1.png)

这张图应沿横轴从低成本向高成本阅读，纵轴是基准得分，误差棒为 95% 置信区间，虚线连接帕累托前沿上的点。它支撑的核心主张是：在文献理解问答上，专用智能体与通用 ReAct 的差距并非单纯由成本决定；Asta Scholar QA 在 ScholarQA-CS2 上以约 0.126 美元的成本取得 87.7 分，而 ReAct 搭配 gpt-5 以约 0.373 美元取得 79.8 分，说明任务优化能带来成本与质量的双重优势，但这一优势在 LitQA2-FullText 上并不一致。

## 二、实验：57 个智能体的成绩与代价

实验覆盖数月，报告准确率、成本与标准差。下表汇总数据集、模型、划分、基线与指标等设置信息。












主结果如下表所示，数值取自论文表 4 与表 11。











最强相关基线是 ReAct 搭配 gpt-5，综合 44.0 分；类别层面呈现明显不一致：编码与执行上 ReAct 搭配 gpt-5 的 55.0 分高于 Asta v0 的 47.6 分；端到端发现上 Asta v0 的 68.8 分远高于 ReAct 搭配 gpt-5 的 36.1 分。这说明专用优化并非全面领先，而是以更高工程与推理成本换取特定类别优势。

![端到端发现基准的分数—成本分析](/images/46f045f0988886db031814416c3cd02b.png)

这张图聚焦端到端发现，横轴为对数成本，纵轴为得分，虚线标出帕累托前沿。阅读时应关注高成本区间的 Asta Panda 与 Asta v0：Asta Panda 搭配 claude-sonnet-4 在 E2E-Bench 上得 70.5 分、成本约 10.643 美元，在 E2E-Bench-Hard 上得 68.2 分、成本约 14.487 美元；而 Smolagents Coder 搭配 gpt-5 仅用约 0.205 美元就在 E2E-Bench 上得 62.8 分，但在 E2E-Bench-Hard 上跌至 30.3 分。这支撑了“端到端发现的高分伴随极高成本，且难度提升后性能骤降”的判断。

分基准看，文献理解问答中 Asta Scholar QA 搭配 gemini-2.5-flash 在 ScholarQA-CS2 上得 87.7 分、成本约 0.126 美元，Elicit 得 85.5 分，SciSpace Deep Review 得 84.6 分；但 LitQA2-FullText 上 ReAct 搭配 gpt-5 得 82.7 分，Asta v0 仅 70.7 分。编码任务中 SUPER-Expert 最高为 ReAct 搭配 gpt-5 的 41.1 分，CORE-Bench-Hard 最高为 ReAct 搭配 o3 的 56.8 分，DS-1000 最高为 ReAct 搭配 gpt-5 的 78.0 分。数据分析 DiscoveryBench 最高为 ReAct 搭配 o3 的 33.7 分。端到端发现的平均步骤完成率可达约 70%，但完整实验成功率最高仅 5%，论文以 0.7^10≈3% 说明多步串联的衰减。

论文未报告独立的消融实验，因此这里不设消融表；其替代性证据是同一智能体类别下更换底层模型的对比，例如 ReAct 搭配 gpt-5 相比 o3 在多数基准提升 0%–5%，但在 ScholarQA-CS2 提升 13.4 个百分点、SUPER-Expert 提升 24.8 个百分点、LitQA2-FullText-Search 提升 25.3 个百分点、E2E-Bench-Hard 提升 21.1 个百分点。另一个值得注意的例外是 gpt-5 反而降低了部分专用智能体的表现，论文推测 gpt-5 可能更适配常见的 ReAct 式工作流。

## 三、总结

AstaBench 的机制贡献在于把“可控环境、标准化接口、成本核算、开放性与工具标注”整合为可复用的评测基础设施，并用 57 个智能体、22 个类别的实验给出当前科研智能体的全景快照。证据表明：文献理解相对成熟，最佳专用智能体在 ScholarQA-CS2 上接近 88 分；但编码、数据分析与端到端发现仍是瓶颈，SUPER-Expert 最高 41.1 分，DiscoveryBench 最高 33.7 分，完整实验成功率最高 5%。

限制与边界同样明显：成本依赖冻结价格快照与社区维护的成本表，未计延迟折扣；类别聚合假设任务独立，可能略微低估不确定性；部分商业智能体无法在全部基准上评测；端到端发现的成功率对步骤数敏感。设计启示是，任何智能体排行榜都应同时报告成本、工具访问与开放程度，并用帕累托前沿而非单一分数来呈现性能—成本权衡，否则“领先”可能只是资源堆叠的结果。

## References

- AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite. [arXiv 2510.21652](https://arxiv.org/abs/2510.21652)

- Inspect 评测框架：[GitHub](https://github.com/UKGovernmentBEIS/inspect)

- Terminal-Bench：[GitHub](https://github.com/laude-institute/terminal-bench)

- HAL 评测工具：[GitHub](https://github.com/princeton-pli/hal-harness)

- Evalchemy：[GitHub](https://github.com/mlfoundations/evalchemy)
