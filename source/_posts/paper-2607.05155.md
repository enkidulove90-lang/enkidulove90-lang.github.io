---
title: "EdgeBench: Unveiling Scaling Laws of Learning from Real-World Environments"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.05155
arxiv_id: "2607.05155"
---

## 一、简介

Pretraining scaling laws reveal that model capability improves predictably with data and compute. But learning from real world environments after deployment remains far less understood. Analyzing roughly 38,000 hours of agent interaction with the environment across 134 real world tasks, we find, to the best of our knowledge, the first evidence that overall performance during environment learning follows a log-sigmoid scaling law with remarkably high precision, reaching $R ^ { 2 } = 0 . 9 9 8$ . Across model generations, we also find that agent learning speed roughly doubles every three months. This discovery stems from EdgeBench, a suite of 134 real world tasks with ultra-long horizons, spanning scientific discovery, software engineering, combinatorial optimization, professional knowledge work, formal mathematics, and interactive games. Each task sustains at least 12 hours of continuous agent operation under rich, multilevel feedback, and is built through substantial expert efort. We publicly release 51 tasks and our full evaluation framework to accelerate the study of how agents learn from real world experience.

Date: July 7, 2026 Correspondence: Shu Zhong at zhongshu@bytedance.com Project Page: https://edge-bench.org

![](images/ccf902412bc706f24f7ad9602f45bf4a1bbd0cf861539999b9f0f72f1e189dac.jpg)  
Figure 2 EdgeBench task taxonomy. 134 real world tasks across six capability families, with feedback channels designed to support within-run improvement. Recorded human expert efort estimates: mean 57.2 h.

## 二、论文方法

论文构建EdgeBench基准，包含134个真实世界任务，覆盖科学问题与ML、系统与软件工程、组合优化、专业知识工作、形式数学与定理证明、交互式游戏六大能力族。每个任务在可执行工作空间中运行，采用工作-评判双容器隔离架构和双环反馈机制。评估五个前沿模型（Claude Opus 4.8、GPT-5.5、GPT-5.4、GLM-5.1、DeepSeek-V4-Pro），每个任务-模型对运行三次12小时试验，记录完整提交轨迹，并用log-sigmoid等S曲线拟合性能随交互时间的变化。

## 三、论文里的图与解释

### 图 1

![Figure 2 EdgeBench task taxonomy. 134 real world tasks across six capability families, with feedback channels designed to support within-run improvement. Recorded human expert efort estimates: mean 57.2 h.](/images/papers/2607.05155/ccf902412bc706f24f7ad9602f45bf4a1bbd0cf861539999b9f0f72f1e189dac.jpg)

**原图说明：** Figure 2 EdgeBench task taxonomy. 134 real world tasks across six capability families, with feedback channels designed to support within-run improvement. Recorded human expert efort estimates: mean 57.2 h.

**图示解释：** 该图对应论文中的“Figure 2 EdgeBench task taxonomy. 134 real world tasks across six capability families, with feedback channels designed to support within-run improvement. Recorded human expert efort estimates: mean 57.2 h.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Figure 4 Learning curves over 12 hours for 18 representative tasks across six capability families. The remaining task curves are provided in Figures 15–35.](/images/papers/2607.05155/685438f115491a7989375db77922aa4a2f9a7d46ad7b211f1e7e74374e450a8e.jpg)

**原图说明：** Figure 4 Learning curves over 12 hours for 18 representative tasks across six capability families. The remaining task curves are provided in Figures 15–35.

**图示解释：** 该图对应论文中的“Figure 4 Learning curves over 12 hours for 18 representative tasks across six capability families. The remaining task curves are provided in Figures 15–35.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Figure 5 Task-family-level log-sigmoid fits across the six EdgeBench task families. Despite large diferences in task type and scoring function, the same log-time sigmoidal form fits the average trajectory in each task family well.1](/images/papers/2607.05155/2bee0c8b5d0722839ccc8c89ced3d1dd8bb71a77db017f5aea0ff93cf60b71cd.jpg)

**原图说明：** Figure 5 Task-family-level log-sigmoid fits across the six EdgeBench task families. Despite large diferences in task type and scoring function, the same log-time sigmoidal form fits the average trajectory in each task family well.1

**图示解释：** 该图对应论文中的“Figure 5 Task-family-level log-sigmoid fits across the six EdgeBench task families. Despite large diferences in task type and scoring function, the same log-time sigmoidal form fits the average trajectory in each task family well.1”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 4

![Figure 27 Per-task learning curves: Combinatorial Optimization & Planning (13/21).](/images/papers/2607.05155/7932dce4f21485740e95513225f406f699ae088beb3312b3a327300ca748bc50.jpg)

**原图说明：** Figure 27 Per-task learning curves: Combinatorial Optimization & Planning (13/21).

**图示解释：** 该图对应论文中的“Figure 27 Per-task learning curves: Combinatorial Optimization & Planning (13/21).”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

<table><tr><td>Core Contributors</td><td>Peng Tang</td></tr><tr><td>Deyao Zhu*</td><td>Chengyao Tang</td></tr><tr><td>Xin Zhou*</td><td>Shanyu Wu</td></tr><tr><td>Shengling Qin*</td><td>Huanyu Zheng</td></tr><tr><td>Xuekai Zhu*</td><td>Yu Liu</td></tr><tr><td>Hangliang Ding*</td><td>Liya Zhu</td></tr><tr><td>Shu Zhong*†</td><td>He Wang</td></tr><tr><td></td><td>Ming Ding</td></tr><tr><td colspan="2">Theory</td></tr><tr><td>Zixin Wen</td><td>Data Infrastructure</td></tr><tr><td>Data Collection and Curation</td><td>Ziyu Wan</td></tr><tr><td>Zhonglin Xie</td><td>Hao Liu</td></tr><tr><td>Chenhui Gou</td><td>Sibo Wang</td></tr><tr><td>Linxuan Ren</td><td>Haotian Zhu</td></tr><tr><td>Yueyang Wang</td><td>Xintian Zhang</td></tr><tr><td>Junfeng Zhong</td><td>Nan Chai</td></tr><tr><td>Rui Liu</td><td>Yipeng Liu</td></tr><tr><td>Tian Gao</td><td>Panhao Lai</td></tr><tr><td>Yangguang Lin</td><td>Referrals</td></tr><tr><td>Jingyuan Zhang</td><td>Sihang Yuan</td></tr><tr><td>Maojia Song</td><td>Zixin Su</td></tr><tr><td>Xuan Qi‡</td><td>Ge Zhang</td></tr><tr><td>Jinhong Wu‡</td><td>Wangchunshu Zhou</td></tr><tr><td>Chenyang Zhang‡</td><td>Yantao Du</td></tr><tr><td>Yinzhu Piao</td><td></td></tr><tr><td>Ziru Niu</td><td>Advisors</td></tr><tr><td>Hongbin Lin</td><td>Wenhao Huang</td></tr><tr><td>Lingxiang Meng</td><td>Guang Shi</td></tr></table>

\*Equal contribution †Project Lead ‡External contributor

## 五、实验数据集选择

- EdgeBench（134个真实世界任务，公开释放51个任务）
- 18任务切片（用于解耦先验知识与环境学习）
- 42任务子集（用于200k vs 1M上下文消融）

## 六、消融实验

Long-running agent evaluation depends not only on model capability, but also on how the harness keeps the run alive and carries useful state across many hours. In a 12-hour task, an agent may stop its running unexpectedly due to idleness and need to resume. These continuation mechanisms are therefore part of the practical measurement setup: a weak scafold can make a capable model stop working on the task, while a stronger scafold may help the same model keep active and improving. As a supplementary harness-level ablation, we evaluate two such mechanisms, /goal mode and the Ralph loop, under a fixed 12-hour budget with GPT-5.5 and GPT-5.4.

Base uses the standard harness: one continuing agent session, a stop hook to prevent voluntary early exit, and auto-resume for abnormal exits. In /goal mode [53], the harness prompts the agent to create a task-level goal at the beginning, keep it active during the run, and mark it complete only when the task is validated. The Ralph loop follows the file-backed fresh-context pattern [32]: each loop starts a new agent invocation on the same workspace, asks it to read and update progress.md, then appends judge feedback to that file before the next loop. It uses up to 100 loops, a 7200-second per-loop cap, and the same 12-hour overall budget. Each cell schedules three runs and reports the mean score over valid runs.

As shown in Table 6, the goal mode and the Ralph loop often outperform the base setting, suggesting that long-horizon agents benefit from harness support that preserves and updates task state across extended runs. In the displayed-task average, GPT-5.5 improves from 42.6 in Base to 43.1 with Goal and 43.4 with Ralph, while GPT-5.4 improves from 26.1 in Base to 31.8 with Goal and 27.6 with Ralph. The gains are not uniform across all tasks and models, so we treat this as an appendix-level harness diagnostic rather than a main result.

Most cells use all three scheduled runs. A few GPT-5.4 cells have fewer valid runs because of intermittent API or network instability: one-run cells are w/ Goal for storyboard\_ad\_copywriting and flt\_regular\_ formalization, plus w/ Ralph for symbolic\_integration\_engine; two-run cells are battery\_soh\_rul\_ anomaly (w/ Goal and w/ Ralph), capecod\_plume\_reconstruction (w/ Goal), combinatorial\_games\_ formalization (w/ Ralph), ffmpeg\_swscale\_reimplementation (w/ Goal), flt\_regular\_formalization (w/ Ralph), git\_rewrite\_in\_zig (w/ Goal), and symbolic\_integration\_engine (w/ Goal). All reported GPT-5.5 cells use the full three runs.

## 七、Benchmark 结果与解释

Motivation. Section 5.2 shows that accumulated experience can improve performance. A remaining question is how this experience should be retained during a long run. Using long context is a natural way to do so. However, frontier-agent harnesses can also maintain state outside the model context through workspace files, compaction, progress notes, and memory-like artifacts. It is therefore unclear whether extending the context window still provides additional benefits once these external state channels are available, and if so, by how much.

Setup. We compare 200k-context Opus 4.8 with 1M-context Opus 4.8 on the 42-task subset under the same long-horizon evaluation protocol.

Result. A longer context yields a consistent multi-point gain throughout the 12-hour window (Figure 12b). The 1M-context Opus 4.8 stays above the 200k variant at every checkpoint, and the two trajectories run roughly parallel: the gap is +5.8 at 2h and only edges down to +4.4 by 12h, with both curves well described by the same log-sigmoid form. Thus, even with identical external workspace and harness state, a longer context window gives a stable advantage over the horizon, with at most a slight tendency to narrow.

## 八、总结

This paper introduced EdgeBench, a benchmark for studying how agents learn from real-world environments over day-long horizons. Across 134 diverse executable tasks and roughly 38,000 hours of environment interaction, we find that aggregate learning trajectories follow a precise log-sigmoid relationship with interaction time. The same form appears across task families, remains stable over longer horizons, and supports forecasting later performance from early trajectories. We also find that agent learning speed has improved rapidly across recent frontier model generations.

These results suggest that learning from environments is not merely a collection of idiosyncratic task outcomes, but a measurable scaling object. Unlike many aggregate capability curves, environment-learning trajectories expose the intermediate attempts, feedback, and revisions through which progress occurs. This makes EdgeBench useful not only for ranking agents, but for studying how agents acquire and reuse experience. More broadly, the regularity we observe suggests that post-deployment learning from rich environments may deserve the same systematic scaling attention that pretraining has received.

## References

[1] B. P. Abbott et al. Observation of gravitational waves from a binary black hole merger. Physical Review Letters, 116(6):061102, 2016. doi: 10.1103/PhysRevLett.116.061102.

[2] Anthropic. The Claude Model Family. https://www-cdn.anthropic.com/ de8ba9b01c9ab7cbabf5c33b80b7bbc618857627/Model\_Card\_Claude\_3.5\_Addendum.pdf, 2024.

[3] Anthropic. Claude Opus 4.8 System Card. https://www-cdn.anthropic.com/ 0b4915911bb0d19eca5b5ee635c80fef830a37ea.pdf, May 2026. System card. Released May 28, 2026; updated June 3, 2026.

[4] Parth Asawa, Christopher M. Glaze, Gabriel Orlanski, Ramya Ramakrishnan, Benji Xu, et al. Continual learning bench: Evaluating frontier AI systems in real-world stateful environments. arXiv preprint arXiv:2606.05661, 2026.

[5] Per Bak, Chao Tang, and Kurt Wiesenfeld. Self-organized criticality: An explanation of 1/f noise. Physical Review Letters, 59(4):381–384, 1987.

[6] Joseph Berkson. Application of the logistic function to bio-assay. Journal of the American Statistical Association, 39(227):357–365, 1944. doi: 10.1080/01621459.1944.10500699.

[7] Akshita Bhagia, Jiacheng Liu, Alexander Wettig, David Heineman, Oyvind Tafjord, Ananya Harsh Jha, Luca Soldaini, Noah A. Smith, Dirk Groeneveld, Pang Wei Koh, Jesse Dodge, and Hannaneh Hajishirzi. Establishing task scaling laws via compute-eficient model ladders. arXiv preprint arXiv:2412.04403, 2024.

[8] Chester I. Bliss. The method of probits. Science, 79(2037):38–39, 1934.

[9] Bradley Brown, Jordan Juravsky, Ryan Ehrlich, Ronald Clark, Quoc V. Le, Christopher Ré, and Azalia Mirhoseini. Large language monkeys: Scaling inference compute with repeated sampling. arXiv preprint arXiv:2407.21787, 2024.

[10] Jun Shern Chan, Neil Chowdhury, Oliver Jafe, James Aung, Dane Sherburn, Evan Mays, Giulio Starace, Kevin Liu, Leon Maksin, Tejal Patwardhan, Lilian Weng, and Aleksander Mądry. MLE-bench: Evaluating machine learning agents on machine learning engineering. In The Thirteenth International Conference on Learning Representations, 2025.

[11] Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, et al. Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374, 2021.

[12] Ziru Chen, Shijie Chen, Yuting Ning, Qianheng Zhang, Boshi Wang, Botao Yu, Yifei Li, Zeyi Liao, Chen Wei, Zitong Lu, et al. ScienceAgentBench: Toward rigorous assessment of language agents for data-driven scientific discovery. In International Conference on Learning Representations, 2025.

[13] Ching-An Cheng, Andrey Kolobov, Dipendra Misra, Allen Nie, and Adith Swaminathan. LLF-bench: Benchmark for interactive learning from language feedback. arXiv preprint arXiv:2312.06853, 2023.

[14] Yizhe Chi, Deyao Hong, Dapeng Jiang, Tianwei Luo, Kaisen Yang, Boshi Zhang, et al. Frontier-Eng: Benchmarking self-evolving agents on real-world engineering tasks with generative optimization. arXiv preprint arXiv:2604.12290, 2026.

[15] Evan Chu, Rajan Agarwal, Abishek Thangamuthu, Brendan Graham, and Justus Mattern. FrontierSWE: Benchmarking coding agents at the limits of human abilities. https://www.frontierswe.com/blog, 2026.

[16] DeepSeek-AI. DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning. arXiv preprint arXiv:2501.12948, 2025.

[17] DeepSeek-AI. DeepSeek-V4: Towards highly eficient million-token context intelligence. https://huggingface. co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek\_V4.pdf, April 2026. Technical report.

[18] Jingzhe Ding, Shengda Long, Changxin Pu, et al. NL2Repo-Bench: Towards long-horizon repository generation evaluation of coding agents. arXiv preprint arXiv:2512.12730, 2025.

[19] Shihan Dou, Ming Zhang, Chenhao Huang, Jiayi Chen, Feng Chen, Shichun Liu, Yan Liu, Chenxiao Liu, Cheng Zhong, Zongzhang Zhang, et al. EvaLearn: Quantifying the learning capability and eficiency of LLMs via sequential problem solving. arXiv pr

### 在线资源

- [论文：arXiv 2607.05155](https://arxiv.org/abs/2607.05155)
- [PDF源文件](/papers/2607.05155.pdf)
