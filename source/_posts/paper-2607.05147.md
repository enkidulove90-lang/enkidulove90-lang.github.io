---
title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.05147
arxiv_id: "2607.05147"
---

## 一、简介

Speculative decoding accelerates Large Language Model (LLM) inference by decoupling draft generation from target verification. While recent parallel drafters efficiently propose long token sequences in a single forward pass, they suffer from rapid acceptance decay due to a lack of inter-token dependencies. Furthermore, indiscriminately verifying these extended blocks wastes critical batch capacity on tokens with high rejection risks, severely degrading throughput in high-concurrency serving systems. We introduce DSpark, a speculative decoding framework that unifies high-throughput parallel generation with adaptive, load-aware verification. To maintain draft quality, DSpark utilizes a semi-autoregressive architecture—coupling a parallel backbone with a lightweight sequential module—to introduce intra-block dependency modeling and mitigate suffix decay. To optimize system efficiency, DSpark employs confidence-scheduled verification, dynamically tailoring the verification length for each request based on estimated prefix survival probabilities and engine-specific throughput profiles. On offline benchmarks across diverse domains, DSpark substantially improves the accepted length over state-of-the-art autoregressive and parallel drafters. When deployed within the DeepSeek-V4 serving system under live user traffic, DSpark successfully mitigates verification waste. Compared to the established production baseline (MTP-1), DSpark accelerates per-user generation speeds by 60%–85% at matched throughput levels. More importantly, by preventing severe throughput degradation under strict interactivity constraints, it enables performance tiers that were previously unattainable, shifting the Pareto frontier of our serving system. To facilitate community progress, we open-source the DSpark checkpoints alongside DeepSpec, an algorithm-driven training repository for speculative decoding.

## 二、论文方法

DSpark 将推测解码的每 token 延迟分解为草稿与验证时间除以接受长度。方法上采用两阶段草稿：并行骨干（基于 DFlash）一次前向生成所有草稿隐藏状态和基础 logits，轻量级串行头（Markov 低秩转移矩阵或 RNN 门控更新）自回归地注入块内依赖。验证阶段，置信度头估计每位置条件接受概率，经顺序温度缩放校准后，硬件感知调度器根据当前并发请求的累积存活概率和引擎吞吐曲线，贪心地选择使全局吞吐量最大的每请求验证前缀长度。

## 三、论文里的图与解释

### 图 1

![Figure 1 | The DSpark architecture and decoding cycle. Given prompt tokens ABC , the target model executes one step to generate the next token D , which serves as the anchor for the drafting phase. Using D as the input, DSpark employs a heavy parallel backbone and a lightweight sequential head to generate draft tokens EFGH along with their corresponding confidence scores � –� . The Hardware-Aware Prefix Scheduler then evaluates these scores to retain the prefix EFG and drop the low-confidence token H . Finally, the target model verifies the scheduled prefix in parallel. As illustrated, E and F are accepted while G is rejected, prompting the model to generate a corrected token G∗ to complete the current round.](/images/papers/2607.05147/5889079bacbf3c279318531b1aa8c47cf5a154150b4efd0d6a766f52f077ba3d.jpg)

**原图说明：** Figure 1 | The DSpark architecture and decoding cycle. Given prompt tokens ABC , the target model executes one step to generate the next token D , which serves as the anchor for the drafting phase. Using D as the input, DSpark employs a heavy parallel backbone and a lightweight sequential head to generate draft tokens EFGH along with their corresponding confidence scores � –� . The Hardware-Aware Prefix Scheduler then evaluates these scores to retain the prefix EFG and drop the low-confidence token H . Finally, the target model verifies the scheduled prefix in parallel. As illustrated, E and F are accepted while G is rejected, prompting the model to generate a corrected token G∗ to complete the current round.

**图示解释：** 该图对应论文中的“Figure 1 | The DSpark architecture and decoding cycle. Given prompt tokens ABC , the target model executes one step to generate the next token D , which serves as the anchor for the drafting phase. Using D as the input, DSpark employs a heavy parallel backbone and a lightweight sequential head to generate draft tokens EFGH along with their corresponding confidence scores � –� . The Hardware-Aware Prefix Scheduler then evaluates these scores to retain the prefix EFG and drop the low-confidence token H . Finally, the target model verifies the scheduled prefix in parallel. As illustrated, E and F are accepted while G is rejected, prompting the model to generate a corrected token G∗ to complete the current round.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 半自回归生成架构：保留并行草稿骨干以维持草稿延迟与块大小近似无关，仅附加轻量级串行头（Markov 头或 RNN 头）注入块内 token 依赖，显著缓解并行草稿的后缀接受率衰减。
2. 置信度调度验证机制：设计置信度头预测每个草稿位置的条件下接受概率，并通过顺序温度缩放（STS）进行后校准，使累积接受概率的绝对幅度可用于吞吐量估计。
3. 硬件感知前缀调度器：将验证长度选择建模为全局吞吐量最大化问题，利用实时引擎吞吐曲线和校准后的前缀存活概率，动态为每个请求分配验证预算，在高并发下剪枝低置信度后缀 token。
4. 生产级在线验证与开源：在 DeepSeek-V4-Flash/Pro 生产服务系统中部署，相比 MTP-1 基线在匹配吞吐量下提升单用户生成速度 60%–85%，并开源 DSpark 检查点和 DeepSpec 训练仓库。

## 五、实验数据集选择

Target and draft models. We evaluate DSpark on four target models spanning different scales and model families: Qwen3-{4B, 8B, 14B} (Yang et al., 2025), and Gemma4-12B (Google DeepMind, 2026). For draft models, we compare DSpark with two representative drafters: DFlash (Chen et al., 2026), a state-of-the-art parallel drafter, and Eagle3 (Li et al., 2026b), an autoregressive drafter based on Training-Time Test (TTT). For strict and fair comparison, we retrain all drafters in the same training framework and on the same data3. We align Eagle3’s TTT horizon (7) with the block size (7) used by DFlash and DSpark, and we use the same target-model feature layers for all drafters. For the number of draft model layers, we set 1 for Eagle3 and 5 for DSpark and DFlash (Chen et al., 2026). Unless otherwise stated, DSpark denotes the Markov-head variant; we study the RNN-head variant in Section 4.3.2.

Training data. We use Open-PerfectBlend, an open-sourced version of PerfectBlend (Xu et al., 2024) consisting of 1.3 million samples. It is a general-purpose instruction dataset containing chat (17.6%), math (39.4%), code (38.9%), and instruction-following data (4.1%). We only use the prompts from Open-PerfectBlend; responses are regenerated by each target model with recommended sampling parameters. Each drafter is trained for 10 epochs to ensure full convergence. For data generation and evaluation, we adopt the non-thinking mode.

Evaluation protocol. We evaluate the performance of different algorithms on three domains:

1. Mathematical Reasoning, including GSM8K (Cobbe et al., 2021), MATH500 (Lightman et al., 2024) and AIME25 (Zhang and Math-AI, 2025).

2. Code Generation, including MBPP (Austin et al., 2021b), HumanEval (Chen et al., 2021) and Live-CodeBench (Jain et al., 2025).

3. Daily Chat, including MT-Bench (Zheng et al., 2023), Alpaca (Taori et al., 2023) and Arena-Hard (Li et al., 2024a, 2025b).

For all benchmarks, we use standard speculative decoding (Chen et al., 2023; Leviathan et al., 2023) with the sampling temperature set to 1.0. We report the accepted length (�) per decoding round4. For all drafters, we use chain-based drafting.

Table 1 | Main speculative decoding results. We report accepted length (�) per decoding round (higher is better) for different target models and domains. Bold marks the best results.

<table><tr><td rowspan="2">Target</td><td rowspan="2">Drafter</td><td colspan="3">Math</td><td colspan="3">Code</td><td colspan="3">Chat</td></tr><tr><td>GSM8K</td><td>MATH</td><td>AIME25</td><td>MBPP</td><td>HumanEval</td><td>LCB</td><td>MT-Bench</td><td>Alpaca</td><td>Arena-Hard</td></tr><tr><td rowspan="3">Qwen3-4B</td><td>Eagle3</td><td>5.14</td><td>4.62</td><td>3.92</td><td>3.69</td><td>4.16</td><td>3.77</td><td>2.39</td><td>2.26</td><td>2.55</td></tr><tr><td>DFlash</td><td>5.40</td><td>4.85</td><td>4.15</td><td>4.40</td><td>4.74</td><td>4.18</td><td>3.07</td><td>2.96</td><td>2.83</td></tr><tr><td>DSpark</td><td>6.11</td><td>5.70</td><td>4.89</td><td>5.13</td><td>5.38</td><td>4.86</td><td>3.64</td><td>3.54</td><td>3.29</td></tr><tr><td rowspan="3">Qwen3-8B</td><td>Eagle3</td><td>5.30</td><td>4.77</td><td>3.91</td><td>3.96</td><td>4.33</td><td>4.17</td><td>2.66</td><td>2.54</td><td>2.54</td></tr><tr><td>DFlash</td><td>5.33</td><td>4.91</td><td>4.07</td><td>4.36</td><td>4.64</td><td>4.39</td><td>3.11</td><td>2.98</td><td>2.81</td></tr><tr><td>DSpark</td><td>6.17</td><td>5.78</td><td>5.01</td><td>5.16</td><td>5.52</td><td>5.17</td><td>3.72</td><td>3.58</td><td>3.21</td></tr><tr><td rowspan="3">Qwen3-14B</td><td>Eagle3</td><td>5.24</td><td>4.60</td><td>3.71</td><td>3.81</td><td>4.14</td><td>4.01</td><td>2.62</td><td>2.47</td><td>2.48</td></tr><tr><td>DFlash</td><td>5.41</td><td>4.84</td><td>3.98</td><td>4.44</td><td>4.59</td><td>4.33</td><td>3.10</td><td>2.94</td><td>2.72</td></tr><tr><td>DSpark</td><td>6.21</td><td>5.74</td><td>4.94</td><td>5.26</td><td>5.43</td><td>5.02</td><td>3.70</td><td>3.58</td><td>3.13</td></tr><tr><td rowspan="3">Gemma4-12B</td><td>Eagle3</td><td>5.87</td><td>5.46</td><td>4.83</td><td>4.72</td><td>5.37</td><td>4.16</td><td>3.19</td><td>3.06</td><td>2.72</td></tr><tr><td>DFlash</td><td>5.45</td><td>5.04</td><td>4.22</td><td>4.39</td><td>4.95</td><td>3.70</td><td>2.98</td><td>2.84</td><td>2.59</td></tr><tr><td>DSpark</td><td>6.05</td><td>5.78</td><td>5.12</td><td>5.11</td><td>5.64</td><td>4.51</td><td>3.49</td><td>3.35</td><td>2.92</td></tr></table>

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

To isolate the raw draft quality from system-level scheduling policies, our offline evaluation disables the confidence scheduler, forcing all drafters to propose a fixed block of tokens. The main results, measured by the average accepted length (�) per round, are reported in Table 1.

DSpark consistently outperforms both the autoregressive baseline (Eagle3) and the parallel baseline (DFlash) across all evaluated target models and benchmark domains. Specifically, across the Qwen3-4B, 8B, and 14B models, DSpark improves the macro-average accepted length over Eagle3 by 30.9%, 26.7%, and 30.0%, respectively. Similarly, compared to DFlash, DSpark yields relative improvements of 16.3%, 18.4%, and 18.3% across the three scales. Crucially, this advantage generalizes across model families, as demonstrated by the consistent performance gains on the Gemma4-12B target.

Beyond the average improvements, Table 1 reveals a strong domain effect: the accepted length is naturally higher on structured tasks (e.g., 5.57 on math and 5.12 on code for Qwen3-4B) than on open-ended chat (3.49). This inherent variance in data predictability means a static verification length often wastes compute on trailing tokens that are highly likely to be rejected. This directly motivates our confidence-scheduled verification, which dynamically prunes the draft block based on expected acceptance.

## 八、总结

In this paper, we present DSpark, a speculative decoding framework designed to overcome the structural and system-level bottlenecks of large language model inference in high-concurrency production environments. Algorithmically, DSpark introduces a semi-autoregressive generation paradigm—coupling a computationally heavy parallel backbone with a lightweight sequential head—to mitigate the rapid suffix decay of independent parallel drafters. At the system level, we formulate verification length selection as a global throughput maximization problem, employing a hardware-aware prefix scheduler that dynamically tailors the target model’s verification budget based on calibrated survival probabilities and real-time engine load. Extensive offline evaluations demonstrate that DSpark substantially outperforms state-of-the-art autoregressive and parallel baselines across diverse domains. Furthermore, its real-world deployment within the DeepSeek-V4 validates its practical value in production serving: by intelligently managing verification overhead, DSpark sustains robust concurrency under heavy load, consistently accelerates per-user generation speeds, and shifts the Pareto frontier of LLM serving outward.

## References

T. Abramovich, M. Ashkenazi, I. Putterman, B. Chislett, T. Mitra, B. D. Rouhani, R. Zilberstein, and Y. Geifman. Speed-bench: A unified and diverse benchmark for speculative decoding. arXiv preprint arXiv:2604.09557, 2026.

Z. An, H. Bai, Z. Liu, D. Li, and E. Barsoum. PARD: Accelerating LLM inference with low-cost PARallel draft model adaptation. In The Fourteenth International Conference on Learning Representations, 2026a. URL https://openreview.net/forum?id=XbOyv7iVGL.

Z. An, T. Liu, Z. Liu, D. Li, R. Liu, and E. Barsoum. Pard-2: Target-aligned parallel draft model for dual-mode speculative decoding. arXiv preprint arXiv:2605.08632, 2026b.

AngelSlim Team. D-Cut: Adaptive verification depth pruning for speculative decoding, 2026. URL https://angelslim.readthedocs.io/zh-cn/latest/dcut.html.

Z. Ankner, R. Parthasarathy, A. Nrusimha, C. Rinard, J. Ragan-Kelley, and W. Brandon. Hydra: Sequentially-dependent draft heads for medusa decoding. In First Conference on Language Modeling, 2024. URL https://openreview.net/forum?id=FbhjirzvJG.

M. Arriola, S. S. Sahoo, A. Gokaslan, Z. Yang, Z. Qi, J. Han, J. T. Chiu, and V. Kuleshov. Block diffusion: Interpolating between autoregressive and diffusion language models. In The Thirteenth International Conference on Learning Representations, 2025. URL https: //openreview.net/forum?id=tyEyYT267x.

J. Austin, D. D. Johnson, J. Ho, D. Tarlow, and R. van den Berg. Structured denoising diffusion models in discrete state-spaces. In A. Beygelzimer, Y. Dauphin, P. Liang, and J. W. Vaughan, editors, Advances in Neural Information Processing Systems, 2021a. URL https://openre view.net/forum?id=h7-XixPCAL.

J. Austin, A. Odena, M. Nye, M. Bosma, H. Michalewski, D. Dohan, E. Jiang, C. Cai, M. Terry, Q. Le, et al. Program synthesis with large language models. arXiv preprint arXiv:2108.07732, 2021b.

T. Cai, Y. Li, Z. Geng, H. Peng, J. D. Lee, D. Chen, and T. Dao. Medusa: Simple LLM inference acceleration framework with multiple decoding heads. In R. Salakhutdinov, Z. Kolter, K. Heller, A. Weller, N. Oliver, J. Scarlett, and F. Berkenkamp, editors, Proceedings of the 41st International Conference on Machine Learning, volume 235 of Proceedings of Machine Learning Research, pages 5209–5235. PMLR, 21–27 Jul 2024. URL https://proceedings. mlr.press/v235/cai24b.html.

Y. Cai, X. Liang, X. Wang, J. Ma, H. Liang, J. Luo, X. Zuo, L. Duan, Y. Yin, and X. Chen. Fastmtp: Accelerating llm inference with enhanced multi-token prediction, 2025. URL https: //arxiv.org/abs/2509.18362.

C. Chen, S. Borgeaud, G. Irving, J.-B. Lespiau, L. Sifre, and J. Jumper. Accelerating large language model decoding with speculative sampling. arXiv preprint arXiv:2302.01318, 2023.

J. Chen, Y. Liang, and Z. Liu. Dflash: Block diffusion for flash speculative decoding. arXiv preprint arXiv:2602.06036, 2026.

M. Chen, J. Tworek, H. Jun, Q. Yuan, H. P. de Oliveira Pinto, J. Kaplan, H. Edwards, Y. Burda, N. Joseph, G. Brockman, A. Ray, R. Puri, G. Krueger, M. Petrov, H. Khlaaf, G. Sastry, P. Mishkin, B. Chan, S. Gray, N. Ryder, M. Pavlov, A. Power, L. Kaiser, M. Bavarian, C. Winter, P. Tillet, F. P. Such, D. Cummings, M. Plappert, F. Chantzis, E. Barnes, A. Herbert-Voss, W. H. Guss, A. Nichol, A. Paino, N. Tezak, J. Tang, I. Babuschkin, S. Balaji, S. Jain, W. Saunders, C. Hesse, A. N. Carr, J. Leike, J. Achiam, V. Misra, E. Morikawa, A. Radford, M. Knight, M. Brundage, M. Murati, K. Mayer, P. Welinder, B. McGrew, D. Amodei, S. McCandlish, I. Sutskever, and W. Zaremba. Evaluating large language models trained on code, 2021.

Y. Cheng, A. Zhang, X. Zhang, C. Wang, and Y. Wang. Recurrent drafter for fast speculative decoding in large language models, 2024. URL https://arxiv.org/abs/2403.09919.

K. Cobbe, V. Kosaraju, M. Bavarian, M. Chen, H. Jun, L. Kaiser, M. Plappert, J. Tworek, J. Hilton, R. Nakano, C. Hesse, and J. Schulman. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021.

D. Dai, C. Deng, C. Zhao, R. 

### 在线资源

- [论文：arXiv 2607.05147](https://arxiv.org/abs/2607.05147)
- [代码：GitHub](https://github.com/Zacks917/AutoMTP)
- [PDF源文件](/papers/2607.05147.pdf)
