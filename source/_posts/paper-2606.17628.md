---

title: "OPD-Evolver：通过在线策略蒸馏培育整体性智能体进化器"

date: "2026-10-21"

year: "2026"

venue_type: "arxiv预印本"

venue_name: "arXiv"

categories: ["推荐系统", "论文速递"]

tags: ["论文速读", "agent evolver", "on-policy distillation", "memory hierarchy", "experience lifecycle", "self-evolving agents", "outcome-calibrated attribution"]

slug: "paper-2606.17628"

---

[论文链接](https://arxiv.org/pdf/2606.17628.pdf)

## 一、研究背景与问题

论文首先重新界定了“自进化智能体”这一概念。作者指出，记忆只是自进化的基底而非其定义：现有记忆增强智能体、技能库、反思机制与自改进流水线虽然能够存储轨迹、检索反思或积累技能，却往往缺乏一种整体能力——即从不断增长且含噪的经验库中挑选有用经验、以经验为依托执行多轮动作、把新轨迹与反馈写成可复用知识，并对记忆库进行长期维护。为此，作者提出以四项耦合能力刻画“合格的智能体进化器”：❶经验选择、❷经验依托的执行、❸经验书写、❹经验管理，并强调四者不可割裂——选择弱会放大检索噪声，执行弱会使智能体依赖提示期指导，书写弱会污染未来记忆，管理弱会导致长期退化。

围绕“如何训练智能体获得通过经验进化的整体能力”这一核心问题，作者提出 OPD-Evolver，一个慢-快协同进化框架：快循环让智能体在与环境和四级记忆（轨迹、提示、技能、工具）的在线交互中完成测试时进化；慢循环则通过在线策略自蒸馏，把交互中产生的行为蒸馏为可部署策略的内在能力。作者将贡献概括为三点：目标形式化（以四项耦合能力定义合格进化器）、实用方案（快慢双循环的在线策略自蒸馏框架，将任务结果与特权后见之明转化为对选择、执行、书写与记忆管理的监督）、以及实验验证（在四个自进化基准上，OPD-Evolver-4B/9B 超越当代记忆系统，并与 QWEN3.5-397B、STEP-3.5-196B 等巨型模型保持竞争力）。相关工作部分按经验生命周期梳理了自进化智能体研究，并指出在线策略蒸馏此前多用于强化执行能力，而本文将其扩展为同时培育进化器所需的四项能力。

## 二、方法

方法部分先给出问题形式化：智能体面对任务流而非孤立查询，在第 t 轮接收任务 x_t，与环境交互得到观测、动作与反馈，形成轨迹 τ_t 与回报 R_t；与常规评测丢弃轨迹不同，进化器维护不断演化的经验库 M_t，并实现从（任务, 记忆库）状态到任务行为与更新后记忆库的闭环转移——先由非参数检索器得到候选集 C_t，再由选择行为 Sel_θ 压缩为上下文 S_t，随后同一策略 π_θ 在 S_t 条件下执行并产出经验更新 Δ_t，记忆库按 M_{t+1}=M_t ⊕_θ Δ_t 更新。流式目标是在任务流上最大化 R_t 与更新后记忆库下游可用性 U(M_{t+1}) 的加权和。

快进化循环在测试时不改变参数 θ，负责把 M_t 变成小而可执行的上下文，并把新回合转回可复用经验。记忆被组织为四级：轨迹层保存情景证据，提示层保存局部警告与启发式，技能层抽象可复用流程，工具层保存可执行命令或代码模板。检索按嵌入余弦相似度在每层取 Top-K 形成高召回候选集，选择器再按层压缩为 S_t 并渲染为文本上下文 c_t；执行时动作以任务、交互历史与 c_t 为条件，回合结束后同一智能体自行决定更新哪些层、每层写入多少条记忆，并每隔 Q 个任务进入一次维护交互，使用 lookup、merge、delete 三类工具调用更新记忆库。循环同时记录候选、被选记忆、结果、新建记忆 id 与维护动作，作为慢循环的后见证据。

慢进化循环解决“如何把标量结果回传到选择、执行、书写与维护决策”的问题。结果校准归因只在记忆 m 实际被检索到的任务上估计其价值，以候选受控的方式比较被选入与未被选入任务组的期望回报差，并用可靠性权重 ρ_g(m) 降权不可靠选择；随后结合层级先验 α 与置信因子 γ(m)=1−1/√(1+N⁺(m)) 得到记忆分数 V(m)，把延迟反馈转成稠密后见标签。统一后见自蒸馏对 k∈{sel, act, write, maint} 四类生命周期决策分别构造学生可见的公开输入 z^k 与教师额外可见的特权后见视图 h^k：选择看到每个候选的记忆价值，执行通过让学生在没有记忆的条件下解题来内化有用记忆，书写看到所写记忆的后续价值，维护看到包含价值、置信度、使用统计与冗余分数的记忆库诊断。学生在部署条件下采样在线输出，教师在同一学生前缀上以停止梯度的参数给出分布，损失为全词表 token 级 KL 散度在学生访问前缀上的期望；蒸馏后仅将学生侧行为部署回快循环，使其在测试时无需特权反馈即可行使进化能力。

![方法图 1](/images/28bc09accf18b8cd902578773a73d821.png)

该图概括 OPD-Evolver 的整体框架。上半部分展示快循环：智能体在环境中执行任务，并与轨迹、提示、技能、工具四级记忆层级进行读取、使用、写入与维护的在线交互；下半部分展示慢循环：将经结果校准的后见信息转化为在线策略自蒸馏信号，用于训练同一个进化器策略，从而把测试时的经验使用行为内化为可部署能力。

## 三、实验

实验在异构智能体经验上训练 OPD-Evolver，数据来自 Agent World Model、nvidia/Nemotron-Terminal-Corpus 与 EnvScaler，与所有评测基准不相交；默认以 QWEN3-4B-INSTRUCT-2507 与 QWEN3.5-9B 为骨干，QWEN3-EMBEDDING-0.6B 做检索，检索 50 个候选，维护周期 Q=30，教师上下文最多保留 20 条记忆，监督过滤阈值为 0.01。评测覆盖 LifelongAgentBench（DB、OS）、MemoryArena（Math、Physics）、AMA-Bench（因果推断、状态更新、状态抽象）、InterCode（Bash、CTF、SQL）与 MiniHack（Room、Maze、KeyRoom）。基线包括 ExpeL、AWM、Cheatsheet、MemP、ReasoningBank、EvolveR、MemEvolve 等记忆增强智能体，以及 SFT、GRPO、Skill0、MemRL、Complementary RL 等训练式方法；所有基于记忆的方法均从空经验库开始，仅从评测流中积累记忆。

主结果显示，在 4B 与 9B 两个骨干下，OPD-Evolver 在同骨干的 10 个子集上均取得最佳，9B 相对最强记忆基线在 OS（65.00% 对 61.00%）、AMA-SA（52.92% 对 48.00%）与 InterCode-CTF（57.00% 对 53.00%）上有明显提升；OPD-Evolver-9B 在 9/10 子集上超过 STEP-3.5-FLASH（196B），在 6/10 子集上超过 QWEN3.5-397B-A17B。与训练式方法相比，OPD-Evolver 在 6 个子集中的 5 个取得最佳，相对 GRPO 在 Maze、KeyRoom、Bash、CTF、SQL 上均有提升，相对 Complementary RL 在最难的 MiniHack 子集上进一步改善。

消融在 InterCode 上以 4B 模型进行：去掉慢进化、以记忆频率校准替代结果校准归因、仅按相似度取 Top-5 选择、去掉书写蒸馏、禁用维护训练均导致性能下降，其中去掉记忆归因的降幅最大，说明校准归因、可学习选择、记忆书写与库维护需要联合训练。框架分析表明，选择蒸馏把被选记忆的中位分数从 0.66/0.69/0.66 提升到 0.79/0.76/0.76（SQL/CTF/Bash），下四分位数从 0.50 升至 0.62 以上；书写蒸馏把所写记忆的中位分数从 0.80/0.82/0.82 提升到 0.91/0.90/0.89，下四分位数升至 0.83 以上；经验内化实验显示每个骨干的箭头都指向更高成功率与更少步数，4B 提升约 3–4 点、9B 提升约 3–7 点，轨迹最多缩短 2.5 步。案例研究进一步显示，慢循环训练使选择更精准、书写更贴近失败根因。

![实验图 1](/images/afe61cc5b31cb376ae3939e6baf4c9a5.png)

该图对比原始 QWEN3.5-9B 与经过选择蒸馏后的 OPD-Evolver-9B 所选中记忆的校准分数分布。可以看到训练后的选择器把分布整体上移，中位数与下四分位数均提高，说明它减少了对低价值检索噪声的注入，而非仅抬高少数高分样本。

![实验图 2](/images/3ac3bc44423126187c9f4881013ccdfd.png)

该图比较原始 QWEN3.5-9B 与 OPD-Evolver-9B 所书写记忆的校准分数分布。书写蒸馏后分布更集中于高分区间、低分记忆明显减少，表明训练后的书写器更倾向于产出对未来任务真正有用的紧凑记忆，而不是泛泛而谈的建议。

![实验图 3](/images/c6b131b044858eb543ea8753d1d733bd.png)

该图展示经验内化效果：每个箭头从原始骨干模型指向对应的 OPD-Evolver 策略，横轴为任务成功率、纵轴（反向）为执行步数。所有箭头都指向更高成功率与更少步数，说明慢循环蒸馏把高价值记忆转化为更直接高效的执行行为，而不仅是推理时检索到更好的上下文。

![实验图 4](/images/12310d23af9ab59167c24af3df9765d7.png)

该案例图展示慢循环训练如何同时提升记忆选择与记忆书写。上半部分在 LifelongAgentBench-OS 任务上，OPD-Evolver 从检索到的记忆中只保留与创建文件、设置权限和生成排序文件列表直接相关的技能与提示；下半部分在 MiniHack-Room 失败轨迹上，它写出“仅探索相邻区域并不充分”这类更具因果性与可复用性的记忆，而非泛化建议。

![实验图 5](/images/064f5749fc0778b6a736cfb584d297fc.png)

该图给出 LifelongAgentBench 上记忆选择的补充结果（左为 DB、右为 OS），用于说明选择蒸馏在长程数据库与操作系统环境中同样使被选记忆的校准分数分布上移，减少宽泛或弱相关记忆的注入。

![实验图 6](/images/debc0e58226138c3076fd0a419b9d8a0.png)

该图是 LifelongAgentBench 上记忆选择的另一组补充结果（左 DB、右 OS），与前一图共同支撑“训练后的选择器更少注入噪声记忆、更贴合当前任务”的结论。

![实验图 7](/images/76f38e55bc50e89283ef5b8510e72d30.png)

该图展示 LifelongAgentBench 上记忆书写的补充结果（左 DB、右 OS）：相比原始书写器，OPD-Evolver 写出的记忆校准分数更高且更集中，低分记忆减少，说明它更善于把失败转化为捕捉因果错误模式与任务约束的紧凑记忆。

![实验图 8](/images/72cd269b5c8be24e64529c2e1243872b.png)

该图是 LifelongAgentBench 上记忆书写的另一组补充结果（左 DB、右 OS），与前一图一起表明书写蒸馏的效果可推广到主要基准之外的长程智能体环境。

![实验图 9](/images/16ec40a55b82f7221ee051b0639cdaf4.png)

该案例图聚焦执行器：左上为 InterCode-SQL，右上为 MiniHack-Room-5×5，下方为 LifelongAgentBench-OS。原始执行器可能违反任务约束、在未真正达成成功条件前停止或遗漏必要副作用，而 OPD-Evolver 学会分离 SQL 动作、持续导航直到踏上目标格，并补上缺失的目录创建与权限设置操作。

![实验图 10](/images/92c0bf91094e32020e8ee971848b63e1.png)

该案例图聚焦选择器：左上为 InterCode-SQL，右上为 LifelongAgentBench-OS，下方为 MiniHack-Trap。原始选择器常注入表面相关但无因果帮助的记忆，甚至在 JSON 解析失败后给出空注入；OPD-Evolver 更积极地过滤记忆，只保留直接支持当前问题的技能、提示、工具或轨迹。

## 四、总结

论文总结提出 OPD-Evolver，一个结合在线记忆条件交互、结果校准归因与特权在线策略自蒸馏的慢-快协同进化框架。跨多个评测基准的结果表明，该框架使紧凑开源模型稳定优于记忆增强与训练式基线，说明从异构经验流中学到的进化能力可以迁移到训练环境之外。作者据此主张，智能体研究应从“仅存储经验”转向“持续把经验转化为自身进化能力”，并指出该工作指向超越记忆增强智能体、迈向真正合格智能体进化器的方向。

## References

- Rishabh Agarwal, Nino Vieillard, Yongchao Zhou, et al. On-policy distillation of language models: Learning from self-generated mistakes. arXiv:2306.13649, 2024.

- Prateek Chhikara, Dev Khant, Saket Aryan, et al. Mem0: Building production-ready ai agents with scalable long-term memory. arXiv:2504.19413, 2025.

- Jinyuan Fang, Yanwen Peng, Xi Zhang, et al. A comprehensive survey of self-evolving ai agents. arXiv:2508.07407, 2025a.

- Runnan Fang, Yuan Liang, Xiaobin Wang, et al. Memp: Exploring agent procedural memory. arXiv:2508.06433, 2025b/2025c.

- Thomas Palmeira Ferraz, Romain Deffayet, Vassilina Nikoulina, et al. Retrieval-augmented llm agents: Learning to learn from experience. arXiv:2603.18272, 2026.

- Zexue He, Yu Wang, Churan Zhi, et al. Memoryarena: Benchmarking agent memory in interdependent multi-session agentic tasks. arXiv:2602.16313, 2026.

- Geoffrey Hinton, Oriol Vinyals, Jeff Dean. Distilling the knowledge in a neural network. arXiv:1503.02531, 2015.

- Yuyang Hu, Shichun Liu, Yanwei Yue, et al. Memory in the age of ai agents. arXiv:2512.13564, 2025.

- Chunyu Li, Jingyi Kang, Ding Chen, et al. Memreranker: Reasoning-aware reranking for agent memory retrieval. arXiv:2605.06132, 2026a.

- Yaxuan Li, Yuxin Zuo, Bingxiang He, et al. Rethinking on-policy distillation of large language models. arXiv:2604.13016, 2026b.

- Xuechen Liang, Meiling Tao, Yinghui Xia, et al. Self-evolving agents with reflective and memory-augmented abilities. arXiv:2409.00872, 2024.

- Weize Liu, Minghui Liu, Sy-Tuyen Ho, et al. Agentic critical training. arXiv:2603.08706, 2026.

- Zhengxi Lu, Zhiyuan Yao, Jinyang Wu, et al. Skill0: In-context agentic reinforcement learning for skill internalization. arXiv:2604.02268, 2026.

- MiniMax. MiniMax M2.7 - Model Self-Improvement. https://www.minimax.io/models/text/m27, 2026.

- Dilxat Muhtar, Jiashun Liu, Wei Gao, et al. Complementary reinforcement learning. arXiv:2603.17621, 2026.

- Jingwei Ni, Yihao Liu, Xinpeng Liu, et al. Trace2skill: Distill trajectory-local lessons into transferable agent skills. arXiv:2603.25158, 2026.

- Siru Ouyang, Jun Yan, I-Hung Hsu, et al. Reasoningbank: Scaling agent self-evolving with reasoning memory. arXiv:2509.25140, 2025.

- Linyue Pan, Lexiao Zou, Shuo Guo, et al. Natural-language agent harnesses. arXiv:2603.25723, 2026.

- Renjie Pi, Grace Lam, Mohammad Shoeybi, et al. On data engineering for scaling llm terminal capabilities. arXiv:2602.21193, 2026.

- Qwen. Qwen Studio. https://qwen.ai/blog?id=qwen3.5, 2026.

- Mikayel Samvelyan, Robert Kirk, Vitaly Kurin, et al. Minihack the planet: A sandbox for open-ended reinforcement learning research. 2021.

- Zhihong Shao, Peiyi Wang, Qihao Zhu, et al. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. arXiv:2402.03300, 2024.

- Junhao Shen, Teng Zhang, Xiaoyan Zhao, Hong Cheng. Dynamic skill lifecycle management for agentic reinforcement learning. arXiv:2605.10923, 2026.

- Yaorui Shi, Yuxin Chen, Zhengxi Lu, et al. Skill1: Unified evolution of skill-augmented agents via reinforcement learning. arXiv:2605.06130, 2026.

- Noah Shinn, Federico Cassano, Ashwin Gopinath, et al. Reflexion: Language agents with verbal reinforcement learning. NeurIPS, 36:8634–8652, 2023.

- Mingyang Song, Mao Zheng. A survey of on-policy distillation for large language models. arXiv:2604.00626, 2026.

- Xiaoshuai Song, Haofei Chang, Guanting Dong, et al. Envscaler: Scaling tool-interactive environments for llm agent via programmatic synthesis. arXiv:2601.05808, 2026.

- Mirac Suzgun, Mert Yuksekgonul, Federico Bianchi, et al. Dynamic cheatsheet: Test-time learning with adaptive memory. arXiv:2504.07952, 2025.

- Zhen Tan, Jun Yan, I-Hung Hsu, et al. In prospect and retrospect: Reflective memory management for long-term personalized dialogue agents. arXiv:2503.08026, 2025.

- Kimi Team, Yifan Bai, Yiping Bao, et al. Kimi k2: Open agentic intelligence. arXiv:2507.20534, 2025.

- Yash Vishe, Rohan Surana, Xunyi Jiang, et al. Skill-r1: Agent skill evolution via reinforcement learning. arXiv:2605.09359, 2026.

- Hao Wang, Guozhi Wang, Han Xiao, et al. Skill-sd: Skill-conditioned self-distillation for multi-turn llm agents. arXiv:2604.10674, 2026a.

- Yinjie Wang, Xuyang Chen, Xiaolong Jin, et al. Openclaw-rl: Train any agent simply by talking. arXiv:2603.10165, 2026b.

- Zhaoyang Wang, Canwen Xu, Boyi Liu, et al. Agent world model: Infinity synthetic environments for agentic reinforcement learning. arXiv:2602.10090, 2026c.

- Zhenting Wang, Huancheng Chen, Jiayun Wang, Wei Wei. Memex(rl): Scaling long-horizon llm agents via indexed experience memory. arXiv:2603.04257, 2026d.

- Zora Zhiruo Wang, Jiayuan Mao, Daniel Fried, Graham Neubig. Agent workflow memory. arXiv:2409.07429, 2024.

- Tianxin Wei, Noveen Sachdeva, Benjamin Coleman, et al. Evo-memory: Benchmarking llm agent test-time learning with self-evolving memory. arXiv:2511.20857, 2025.

- Cheng-Kuang Wu, Zhi Rui Tam, Chieh-Yen Lin, et al. Streambench: Towards benchmarking continuous improvement of language agents. arXiv:2406.08747, 2024.

- Rong Wu, Xiaoman Wang, Jianbiao Mei, et al. Evolver: Self-evolving llm agents through an experience-driven lifecycle. arXiv:2510.16079, 2025a/2025b.

- Yecheng Wu, Song Han, Hai Cai. Lightning opd: Efficient post-training for large reasoning models with offline on-policy distillation. arXiv:2604.13010, 2026.

- Zhiheng Xi, Jixuan Huang, Chenyang Liao, et al. Agentgym-rl: Training llm agents for long-horizon decision making through multi-turn reinforcement learning. arXiv:2509.08755, 2025.

- Peng Xia, Jianwen Chen, Hanyang Wang, et al. Skillrl: Evolving agents via recursive skill-augmented reinforcement learning. arXiv:2602.08234, 2026.

- Derong Xu, Yi Wen, Pengyue Jia, et al. From single to multi-granularity: Toward long-term memory association and selection of conversational agents. arXiv:2505.19549, 2025.

- An Yang, Anfeng Li, Baosong Yang, et al. Qwen3 technical report. arXiv:2505.09388, 2025.

- John Yang, Akshara Prabhakar, Karthik Narasimhan, Shunyu Yao. Intercode: Standardizing and benchmarking interactive coding with execution feedback. arXiv:2306.14898, 2023.

- Tianzhu Ye, Li Dong, Xun Wu, et al. On-policy context distillation for language models. arXiv:2602.12275, 2026.

- Yanwei Yue, Boci Peng, Xuanbo Fan, et al. Mem-t: Densifying rewards for long-horizon memory agents. arXiv:2601.23014, 2026.

- Guibin Zhang, Haotian Ren, Chong Zhan, et al. Memevolve: Meta-evolution of agent memory systems. arXiv:2512.18746, 2025a.

- Hanchen Zhang, Xiao Liu, Bowen Lv, et al. Agentrl: Scaling agentic reinforcement learning with a multi-turn, multi-task framework. arXiv:2510.04206, 2025b.

- Haozhen Zhang, Quanyu Long, Jianzhu Bao, et al. Memskill: Learning and evolving memory skills for self-evolving agents. arXiv:2602.02474, 2026a.

- Kai Zhang, Xiangchao Chen, Bo Liu, et al. Agent learning via early experience. arXiv:2510.08558, 2025c.

- Shengtao Zhang, Jiaqian Wang, Ruiwen Zhou, et al. Memrl: Self-evolving agents via runtime reinforcement learning on episodic memory. arXiv:2601.03192, 2026b/2026c.

- Andrew Zhao, Daniel Huang, Quentin Xu, et al. Expel: Llm agents are experiential learners. AAAI, 38:19632–19642, 2024.

- Shitian Zhao, Shaoheng Lin, Ming Li, et al. Pyvision-rl: Forging open agentic vision models via rl. arXiv:2602.20739, 2026a.

- Yujie Zhao, Boqin Yuan, Junbo Huang, et al. Ama-bench: Evaluating long-horizon memory for agentic applications. arXiv:2602.22769, 2026b.

- Boyuan Zheng, Michael Y. Fatemi, Xiaolong Jin, et al. Skillweaver: Web agents can self-improve by discovering and honing skills. arXiv:2504.07079, 2025a.

- Junhao Zheng, Xidi Cai, Qiuke Li, et al. Lifelongagentbench: Evaluating llm agents as lifelong learners. arXiv:2505.11942, 2025b.

- Qiyong Zhong, Mao Zheng, Mingyang Song, et al. Sod: Step-wise on-policy distillation for small language model agents. arXiv:2605.07725, 2026.

- Chenyu Zhou, Huacan Chai, Wenteng Chen, et al. Externalization in llm agents: A unified review of memory, skills, protocols and harness engineering. arXiv:2604.08224, 2026.
