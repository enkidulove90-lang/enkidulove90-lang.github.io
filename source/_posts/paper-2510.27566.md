---
title: "Interact-RAG"
date: 2025-10-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2510.27566
arxiv_id: "2510.27566"
---

## 一、简介

Retrieval-Augmented Generation (RAG) has significantly enhanced LLMs by incorporating external information. However, prevailing agentic RAG approaches are constrained by a critical limitation: they treat the retrieval process as a blackbox querying operation. This confines agents’ actions to query issuing, hindering its ability to tackle complex information-seeking tasks. To address this, we introduce Interact-RAG, a new paradigm that elevates the LLM agent from a passive query issuer into an active manipulator of the retrieval process. We dismantle the black-box with a Corpus Interaction Engine, equipping the agent with a set of action primitives for fine-grained control over information retrieval. To further empower the agent on the entire RAG pipeline, we first develop a reasoningenhanced workflow, which enables both zero-shot execution and the synthesis of interaction trajectories. We then leverage this synthetic data to train a fully autonomous end-to-end agent via Supervised Fine-Tuning (SFT), followed by refinement with Reinforcement Learning (RL). Extensive experiments across six benchmarks demonstrate that Interact-RAG significantly outperforms other advanced methods, validating the efficacy of our reasoning-interaction strategy.

## 二、论文方法

In this section, we introduce Interact-RAG with three core components: (1) a corpus interaction engine that supports the fine-grained information control; (2) a reasoning-enhanced workflow that enables both zero-shot solution and data synthesis; and (3) a training pipeline using SFT and RL to produce an autonomous end-to-end agent.

## 三、论文里的图与解释

### 图 1

![A brief demonstration of Interact-RAG. It empowers the agent with fine-grained control over the information-seeking process, leveraging a set of interactive actions. In contrast, conventional RAG is confined to ineffective loops of query issuing.](/images/papers/2510.27566/figure_001_intro.png)

**原图说明：** A brief demonstration of Interact-RAG. It empowers the agent with fine-grained control over the information-seeking process, leveraging a set of interactive actions. In contrast, conventional RAG is confined to ineffective loops of query issuing.

**图示解释：** 该图对应论文中的“A brief demonstration of Interact-RAG. It empowers the agent with fine-grained control over the information-seeking process, leveraging a set of interactive actions. In contrast, conventional RAG is confined to ineffective loops of query issuing.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Comparison of the retrieval iterations and the accuracy.](/images/papers/2510.27566/figure_003_compare_iter.png)

**原图说明：** Comparison of the retrieval iterations and the accuracy.

**图示解释：** 该图对应论文中的“Comparison of the retrieval iterations and the accuracy.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Action invocation status in different training stages. Measured on the Musique dataset.](/images/papers/2510.27566/figure_005_training-stage.png)

**原图说明：** Action invocation status in different training stages. Measured on the Musique dataset.

**图示解释：** 该图对应论文中的“Action invocation status in different training stages. Measured on the Musique dataset.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出语料交互引擎（Corpus Interaction Engine），将检索过程透明化。该引擎提供多面检索（语义/精确搜索及加权融合）、锚定匹配（实体聚焦）和上下文塑造（包含/排除文档、调整规模）三类交互原语，使智能体能够超越简单的查询重写，对信息获取过程进行细粒度控制。
2. 创新点2：设计推理增强工作流（Reasoning-Enhanced Workflow），将复杂任务分解为全局规划、自适应推理和执行三个模块。该工作流不仅作为无需训练的零样本解决方案，还能合成高质量的智能体交互轨迹，为后续的端到端训练提供数据基础。
3. 创新点3：采用两阶段训练策略（SFT + RL）训练端到端智能体。首先通过监督微调（SFT）学习基本的交互和推理模式，然后利用基于GRPO的强化学习（RL）进一步优化策略，使智能体能够内化高级策略，实现完全自主的交互式RAG。

## 五、实验数据集选择

For the training phase, our data is sourced from the combined training splits of NQ, HotpotQA, and MuSiQue. This collection includes both single-hop (NQ) and multi-hop (HotpotQA, MuSiQue) question-answering data. Following the workflow described in Section 3.2, we synthesized 4.8K agent trajectories for Supervised Fine-Tuning (SFT). Subsequently, for the Reinforcement Learning (RL) phase, we started with 9K question-answer pairs and filtered out some overly simplistic questions (measured by the pass rate), resulting in a curated set of 7.4K pairs. For the evaluation phase, our test set was constructed by randomly sampling 500 question-answer pairs from each of six distinct datasets. An exception was made for the Bamboogle dataset, from which we used all 125 available test instances due to its limited size.

## 六、消融实验

As shown in Table 2, we conduct an ablation study on Interact-RAG.

Efficacy of the Interaction Paradigm. The “w/o Interaction” variant means the black-box retrieval is deployed, mirroring the paradigm of typical agentic RAG systems. In this configuration, the agent is restricted to issuing queries to a semantic retriever, without any other interaction. The corresponding results clearly show a marked performance drop. This finding underscores the critical value of our interactive paradigm, confirming that equipping the agent with fine-grained control over the information-seeking process is essential and effective.

<table><tr><td>Method</td><td>2Wiki</td><td>Musique</td><td>PopQA</td></tr><tr><td>Interact-RAG</td><td>69.6</td><td>34.8</td><td>56.0</td></tr><tr><td>w/o All-Interaction</td><td>63.4</td><td>30.1</td><td>50.2</td></tr><tr><td>w/o Multi-faceted Retrieval</td><td>66.0</td><td>34.6</td><td>55.1</td></tr><tr><td>w/o Anchored Matching</td><td>66.3</td><td>34.4</td><td>53.4</td></tr><tr><td>w/o Context Shaping</td><td>68.8</td><td>33.6</td><td>55.2</td></tr></table>

Table 3: Fine-grained ablation study on interaction primitives, reported in Exact Match (EM) scores.

<table><tr><td>Training-free Method</td><td>2Wiki.</td><td>Musique</td><td>PopQA</td></tr><tr><td>MA-RAG</td><td>45.5</td><td>18.0</td><td>40.2</td></tr><tr><td>Interact-RAG-Workflow</td><td>60.1</td><td>24.1</td><td>43.6</td></tr><tr><td>w/o Interaction</td><td>56.3</td><td>18.8</td><td>38.7</td></tr><tr><td>w/o Workflow</td><td>52.0</td><td>21.8</td><td>40.0</td></tr></table>

Table 4: Ablation performance of our training-free workflow, with MA-RAG (Nguyen et al., 2025) as a baseline reference. Results are reported in Exact Match (EM) scores.

Impact of the Training Strategy. For our two-phase training, removing SFT leads to severe performance drops, especially on challenging datasets like Musique (-21.9%). This highlights its role in building fundamental mechanics of planning, reasoning, and iterative interaction. Similarly, omitting RL also causes marked declines, as RL is essential to develop more strategic policies. These results demonstrate that while SFT establishes the core patterns of reasoning and interaction, RL further optimizes the agent’s policy to achieve better performance. (More discussion in Section 4.5).

Ablation on Interaction Primitives. To isolate the specific contributions of each component, we conduct a fine-grained ablation study on the interaction primitives (Table 4.3). The results reveal a strong synergistic effect: while removing the single module degrades performance, the complete absence of interaction leads to the most significant drop. This confirms that these primitives function collectively to surpass black-box retrieval. Furthermore, the contributions of different components vary across data patterns, showing the comprehensiveness of our design. For example, Multi-Faceted Retrieval and Anchored Matching are vital for 2Wiki, which may demand explicit facts. And Context Shaping proves more impactful on Musique, where the prevalence of distractors requires robust context scaling.

## 七、Benchmark 结果与解释

We evaluate Interact-RAG on six benchmarks, with the main results in Table ??. Our findings highlight three key advantages of our approach. First, Interact-RAG consistently achieves best performance across all datasets. On average, it improves the EM-score by 9.7 points (22.5% relative gain) over the second-best method, Search-R1. And our 7B version also achieves a relative improvement of 10.1%. Notably, our Interact-RAG was trained on 12K QA data, a small fraction of the 170K QA pairs used for Search-R1. This data disparity also explains Search-R1’s higher results on the NQ dataset using the 7B model. Second, the performance gains are more pronounced on complex multi-hop QA tasks. For instance, on Musique, Interact-RAG delivers a 36.4% relative improvement. Concurrently, it maintains strong performance on single-hop benchmarks like

<table><tr><td rowspan="3">Method</td><td colspan="8">Multi-Hop QA</td><td colspan="4">Single-Hop QA</td><td rowspan="2" colspan="2">AVG</td></tr><tr><td colspan="2">HotpotQA</td><td colspan="2">2Wiki.</td><td colspan="2">Musique</td><td colspan="2">Bamboogle</td><td colspan="2">NQ</td><td colspan="2">PopQA</td></tr><tr><td>EM</td><td>F1</td><td>EM</td><td>F1</td><td>EM</td><td>F1</td><td>EM</td><td>F1</td><td>EM</td><td>F1</td><td>EM</td><td>F1</td><td>EM</td><td>F1</td></tr><tr><td colspan="15">Results on Qwen2.5-7B Backbone</td></tr><tr><td>Direct</td><td>17.8</td><td>26.2</td><td>22.6</td><td>27.7</td><td>4.3</td><td>9.8</td><td>19.6</td><td>30.2</td><td>16.1</td><td>23.5</td><td>18.6</td><td>21.2</td><td>16.5</td><td>23.1</td></tr><tr><td>Std-RAG</td><td>29.8</td><td>41.5</td><td>28.0</td><td>34.1</td><td>9.5</td><td>14.4</td><td>18.4</td><td>26.8</td><td>35.1</td><td>44.9</td><td>34.6</td><td>41.2</td><td>25.9</td><td>33.8</td></tr><tr><td>IR-CoT</td><td>19.3</td><td>36.6</td><td>20.0</td><td>37.5</td><td>5.2</td><td>14.4</td><td>18.2</td><td>30.0</td><td>16.5</td><td>27.5</td><td>24.6</td><td>34.8</td><td>17.3</td><td>30.1</td></tr><tr><td>MA-RAG</td><td>35.0</td><td>44.7</td><td>39.6</td><td>46.9</td><td>13.1</td><td>19.0</td><td>40.8</td><td>50.9</td><td>29.5</td><td>39.9</td><td>33.3</td><td>39.0</td><td>31.9</td><td>40.1</td></tr><tr><td>Search-o1</td><td>33.6</td><td>46.3</td><td>39.9</td><td>49.6</td><td>14.7</td><td>21.7</td><td>32.0</td><td>45.3</td><td>33.7</td><td>43.8</td><td>36.3</td><td>43.1</td><td>31.7</td><td>41.6</td></tr><tr><td>Search-R1</td><td>45.2</td><td>60.1</td><td>50.9</td><td>58.2</td><td>25.5</td><td>34.1</td><td>42.2</td><td>55.6</td><td>45.3</td><td>54.7</td><td>49.3</td><td>53.6</td><td>43.1</td><td>52.7</td></tr><tr><td>R-Search</td><td>38.2</td><td>51.0</td><td>58.8</td><td>64.4</td><td>19.4</td><td>28.0</td><td>36.0</td><td>52.1</td><td>36.8</td><td>46.5</td><td>42.8</td><td>46.2</td><td>38.7</td><td>48.0</td></tr><tr><td>S-DeepSearch</td><td>40.2</td><td>53.6</td><td>54.0</td><td>61.8</td><td>18.6</td><td>25.8</td><td>46.2</td><td>57.4</td><td>37.0</td><td>46.6</td><td>40.6</td><td>46.1</td><td>39.4</td><td>48.5</td></tr><tr><td>Interact-RAG-7B</td><td>47.8</td><td>61.6</td><td>63.6</td><td>71.0</td><td>30.9</td><td>39.5</td><td>47.6</td><td>61.1</td><td>43.7</td><td>52.9</td><td>51.6</td><td>54.4</td><td>47.5</td><td>56.8</td></tr><tr><td colspan="15">Results on Qwen3-8B Backbone</td></tr><tr><td>Direct</td><td>23.6</td><td>33.0</td><td>26.4</td><td>32.5</td><td>5.9</td><td>13.3</td><td>33.2</td><td>49.1</td><td>19.8</td><td>30.4</td><td>20.5</td><td>25.0</td><td>21.6</td><td>30.6</td></tr><tr><td>Std-RAG</td><td>37.6</td><td>50.6</td><td>35.9</td><td>41.2</td><td>13.7</td><td>21.0</td><td>26.8</td><td>35.0</td><td>37.1</td><td>47.8</td><td>37.3</td><td>44.6</td><td>31.4</td><td>40.0</td></tr><tr><td>IR-CoT</td><td>30.8</td><td>43.3</td><td>33.6</td><td>42.6</td><td>12.9</td><td>20.3</td><td>22.8</td><td>32.6</td><td>33.0</td><td>43.9</td><td>31.7</td><td>38.1</td><td>27.5</td><td>36.8</td></tr><tr><td>MA-RAG</td><td>39.3</td><td>51.7</td><td>45.5</td><td>53.1</td><td>18.0</td><td>25.1</td><td>35.6</td><td>49.3</td><td>34.6</td><td>46.2</td><td>40.2</td><td>45.8</td><td>35.5</td><td>45.2</td></tr><tr><td>Search-o1</td><td>23.1</td><td>30.2</td><td>28.0</td><td>34.6</td><td>10.1</td><td>13.8</td><td>31.2</td><td>39.7</td><td>33.1</td><td>41.9</td><td>33.1</td><td>38.4</td><td>26.4</td><td>33.1</td></tr><tr><td> $Search-R1^†$ </td><td>45.2</td><td>60.1</td><td>50.9</td><td>58.2</td><td>25.5</td><td>34.1</td><td>42.2</td><td>55.6</td><td>45.3</td><td>54.7</td><td>49.3</td><td>53.6</td><td>43.1</td><td>52.7</td></tr><tr><td> $R-Search^†$ </td><td>38.2</td><td>51.0</td><td>58.8</td><td>64.4</td><td>19.4</td><td>28.0</td><td>36.0</td><td>52.1</td><td>36.8</td><td>46.5</td><td>42.8</td><td>46.2</td><td>38.7</td><td>48.0</td></tr><tr><td> $S-DeepSearch^†$ </td><td>40.2</td><td>53.6</td><td>54.0</td><td>61.8</td><td>18.6</td><td>25.8</td><td>46.2</td><td>57.4</td><td>37.0</td><td>46.6</td><td>40.6</td><td>46.1</td><td>39.4</td><td>48.5</td></tr><tr><td>Interact-RAG</td><td>51.6</td><td>66.7</td><td>69.6</td><td>76.4</td><td>34.8</td><td>43.9</td><td>54.0</td><td>65.5</td><td>50.9</td><td>60.7</td><td>56.0</td><td>60.2</td><td>52.8</td><td>62.2</td></tr></table>

Table 1: Overall performance in Exact Match (EM) and F1 scores across various benchmarks. Bold and underline denote the best and second-best performance. For the Qwen3-8B results, methods marked with a dagger (†) use their official 7B models, due to the lack of 8B versions. Notably, our Interact-RAG was trained on 12K QA data, a small fraction of the 170K QA pairs used for Search-R1. This data disparity also explains Search-R1’s higher results on the NQ dataset when using the 7B model.

<table><tr><td>Method</td><td>2Wiki.</td><td>Musique</td><td>PopQA</td></tr><tr><td>Interact-RAG</td><td>69.6</td><td>34.8</td><td>56.0</td></tr><tr><td>w/o Interaction</td><td>63.4 (-8.9%)</td><td>30.1 (-10.9%)</td><td>50.2 (-10.4%)</td></tr><tr><td>w/o SFT</td><td>59.0 (-15.2%)</td><td>26.4 (-21.9%)</td><td>52.2 (-6.8%)</td></tr><tr><td>w/o RL</td><td>65.2 (-6.3%)</td><td>28.1 (-16.9%)</td><td>45.6 (-18.6%)</td></tr></table>

Table 2: Ablation study on Interact-RAG, reported in Exact Match (EM) scores. The 2Wiki and Musique are multi-hop-QA datasets, while PopQA is single-hop.

NQ and PopQA, with relative improvements of 11.0% and 12.3% on EM scores. This validates the effectiveness of our interaction-reasoning paradigm in tackling complex challenges. Third, our trained agent demonstrates great generalization. Trained with train-splits of HotpotQA, Musique, and NQ, it achieves consistent improvements on both in-distribution and out-of-distribution benchmarks. This indicates that the learned capability are not task-specific, underscoring the robustness and generalizability of our approach.

## 八、总结

In this paper, we identify the limitation of simple black-box retrieval, and introduce Interact-RAG, a new paradigm empowering LLM agents with fine-grained control over the information-seeking process. Our approach features an underlying Interaction Engine, a reasoning-enhanced workflow and a two-stage training pipeline, finally yielding a unified, end-to-end interactive RAG agent. Extensive experiments show Interact-RAG significantly outperforms advanced baselines, validating the effectiveness of reasoning-interaction paradigm. This work offers a promising direction for creating more powerful, transparent, and interactive RAG systems.

## References

Satish Tanaji Bhosale, Tejaswini Patil, and Pooja Patil. Sqlite: Light database system. Int. J. Comput. Sci. Mob. Comput, 44(4):882–885, 2015.

Chi-Min Chan, Chunpu Xu, Ruibin Yuan, Hongyin Luo, Wei Xue, Yike Guo, and Jie Fu. Rq-rag: Learning to refine queries for retrieval augmented generation. arXiv preprint arXiv:2404.00610, 2024.

Xinran Chen, Yuchen Li, Hengyi Cai, Zhuoran Ma, Xuanang Chen, Haoyi Xiong, Shuaiqiang Wang, Ben He, Le Sun, and Dawei Yin. Multi-agent proactive information seeking with adaptive llm orchestration for non-factoid question answering. In Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V. 2, pp. 4341–4352, 2025.

Chroma core team. Chroma: Open-source search and retrieval database for ai applications. https: //github.com/chroma-core/chroma, 2025.

Gordon V Cormack, Charles LA Clarke, and Stefan Buettcher. Reciprocal rank fusion outperforms condorcet and individual rank learning methods. In Proceedings of the 32nd international ACM SIGIR conference on Research and development in information retrieval, pp. 758–759, 2009.

Guanting Dong, Hangyu Mao, Kai Ma, Licheng Bao, Yifei Chen, Zhongyuan Wang, Zhongxia Chen, Jiazhen Du, Huiyang Wang, Fuzheng Zhang, et al. Agentic reinforced policy optimization. arXiv preprint arXiv:2507.19849, 2025.

Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Dasha Metropolitansky, Robert Osazuwa Ness, and Jonathan Larson. From local to global: A graph rag approach to query-focused summarization. arXiv preprint arXiv:2404.16130, 2024.

Mohamed Amine Ferrag, Norbert Tihanyi, and Merouane Debbah. From llm reasoning to autonomous ai agents: A comprehensive review. arXiv preprint arXiv:2504.19678, 2025.

Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, Yuxi Bi, Yixin Dai, Jiawei Sun, Haofen Wang, and Haofen Wang. Retrieval-augmented generation for large language models: A survey. arXiv preprint arXiv:2312.10997, 2(1), 2023.

Yunfan Gao, Yun Xiong, Yijie Zhong, Yuxi Bi, Ming Xue, and Haofen Wang. Synergizing rag and reasoning: A systematic review. arXiv preprint arXiv:2504.15909, 2025.

Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang, Runxin Xu, Qihao Zhu, Shirong Ma, Peiyi Wang, Xiao Bi, et al. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2501.12948, 2025.

Xanh Ho, Anh-Khoa Duong Nguyen, Saku Sugawara, and Akiko Aizawa. Constructing a multi-hop qa dataset for comprehensive evaluation of reasoning steps. In Proceedings of the 28th International Conference on Computational Linguistics, pp. 6609–6625, 2020.

Yunhai Hu, Yilun Zhao, Chen Zhao, and Arman Cohan. Mcts-rag: Enhancing retrieval-augmented generation with monte carlo tree search. arXiv preprint arXiv:2503.20757, 2025.

Lei Huang, Weijiang Yu, Weitao Ma, Weihong Zhong, Zhangyin Feng, Haotian Wang, Qianglong Chen, Weihua Peng, Xiaocheng Feng, Bing Qin, et al. A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions. ACM Transactions on Information Systems, 43(2):1–55, 2025.

Yulong Hui, Yao Lu, and Huanchen Zhang. Uda: a benchmark suite for retrieval augmented generation in real-world document analysis. In Proceedings of the 38th International Conference on Neural Information Processing Systems, pp. 67200–67217, 2024.

Yulong Hui, Yihao Liu, Yao Lu, and Huanchen Zhang. Okralong: A flexible retrieval-augmented framework for long-text query processing. arXiv preprint arXiv:2503.02603, 2025.

Aaron Jaech, Adam Kalai, Adam Lerer, Adam Richardson, Ahmed El-Kishky, Aiden Low, Alec Helyar, Aleksander Madry, Alex Beutel, Alex Carney, et al. Openai o1 system card. arXiv preprint arXiv:2412.16720, 2024.

Zhengbao Jiang, Frank F Xu, Luyu Gao, Zhiqing Sun, Qian Liu, Jane Dwivedi-Yu, Yiming Yang, Jamie Callan, and Graham Neubig. Active retrieval augmented generation. In Proceedings of the 2023 Conference on Empirical Methods in 

### 在线资源

- [论文：arXiv 2510.27566](https://arxiv.org/abs/2510.27566)
- [PDF源文件](/papers/2510.27566.pdf)
