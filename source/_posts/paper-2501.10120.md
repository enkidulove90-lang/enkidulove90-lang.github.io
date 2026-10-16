---
title: "PaSa: An LLM Agent for Comprehensive Academic Paper Search"
date: 2025-01-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2501.10120
arxiv_id: "2501.10120"
---

## 一、简介

We introduce PaSa, an advanced Paper Search agent powered by large language models. PaSa can autonomously make a series of decisions, including invoking search tools, reading papers, and selecting relevant references, to ultimately obtain comprehensive and accurate results for complex scholar queries. We optimize PaSa using reinforcement learning with a synthetic dataset, AutoScholarQuery, which includes 35k fine-grained academic queries and corresponding papers sourced from top-tier AI conference publications. Additionally, we develop RealScholarQuery, a benchmark collecting real-world academic queries to assess PaSa performance in more realistic scenarios. Despite being trained on synthetic data, PaSa significantly outperforms existing baselines on RealScholarQuery, including Google, Google Scholar, Google with GPT-4o for paraphrased queries, ChatGPT (search-enabled GPT-4o), GPT-o1, and PaSa-GPT-4o (PaSa implemented by prompting GPT-4o). Notably, PaSa-7B surpasses the best Google-based baseline, Google with GPT-4o, by 37.78% in recall@20 and 39.90% in recall@50, and exceeds PaSa-GPT-4o by 30.36% in recall and 4.25% in precision. Model, datasets, and code are available at https://github.com/bytedance/pasa.

## 二、论文方法

PaSa采用双智能体架构：Crawler执行马尔可夫决策过程，通过[Search]、[Expand]和[Stop]三个动作自主搜索和扩展论文队列；Selector则基于论文标题和摘要输出决策令牌和推理依据。Crawler的训练分两阶段：先通过模仿学习初始化策略，再使用会话级PPO进行强化学习优化，其中Selector作为辅助奖励模型缓解稀疏奖励问题。

## 三、论文里的图与解释

### 图 1

![Table 16: The prompt used with GPT-4o to automatically synthesize AutoScholarQuery.](/images/papers/2501.10120/27973c6c03b5e82525acf0e039c19c69d707f94a49d77a1d23cb3a5750c721ef.jpg)

**原图说明：** Table 16: The prompt used with GPT-4o to automatically synthesize AutoScholarQuery.

**图示解释：** 该图对应论文中的“Table 16: The prompt used with GPT-4o to automatically synthesize AutoScholarQuery.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出双智能体协作架构（Crawler与Selector），Crawler负责最大化召回率，通过搜索和引用扩展自主收集论文；Selector负责精确筛选，判断论文是否满足查询要求，模拟了人类研究者的搜索行为。
2. 创新点2：设计了会话级PPO（Proximal Policy Optimization）强化学习训练方法，通过将长轨迹分割为以[Stop]动作结束的会话，并引入跨会话折扣因子和Selector作为辅助奖励模型，有效解决了学术搜索任务中的稀疏奖励和长轨迹挑战。
3. 创新点3：构建了高质量合成数据集AutoScholarQuery和真实世界基准RealScholarQuery。AutoScholarQuery从顶级AI会议论文的Related Work部分自动生成细粒度查询-论文对，RealScholarQuery则包含50个真实研究查询及其人工标注的相关论文，为学术搜索研究提供了标准化评估平台。

## 五、实验数据集选择

We select 200 queries from the AutoScholarQuery development set. For each query, we perform a Google search and randomly choose one paper from the union of the search results and the relevant paper set in AutoScholarQuery. This yields a set of <user query, paper> pairs. Annotators then evaluate whether each paper aligns with the requirements of the user query. The final test dataset consists of 98 positive samples and 102 negative samples.

```txt
The prompt for paper selection
You are an elite researcher in the field of AI, conducting research on {user_query}. Evaluate whether the following paper fully satisfies the detailed requirements of the user query and provide your reasoning. Ensure that your decision and reasoning are consistent.
Searched Paper:
Title: {title}
Abstract: {abstract}
User Query: {user_query}
Output format: Decision: True/False
Reason:...
Decision:
```

Table 13: Prompt used by PaSa Selector or GPT-4o to evaluate paper relevance.

<table><tr><td>Method</td><td>Crawler Recall</td><td>Precision</td><td>Recall</td><td>Recall@100</td><td>Recall@50</td><td>Recall@20</td></tr><tr><td>Google</td><td>-</td><td>-</td><td>-</td><td>0.2101</td><td>0.2010</td><td>0.1788</td></tr><tr><td>Google Scholar</td><td>-</td><td>-</td><td>-</td><td>0.0801</td><td>0.0739</td><td>0.0612</td></tr><tr><td>Google with GPT-4o</td><td>-</td><td>-</td><td>-</td><td>0.2101</td><td>0.2010</td><td>0.1788</td></tr><tr><td>ChatGPT</td><td>-</td><td>0.0507</td><td>0.3046</td><td>-</td><td>-</td><td>-</td></tr><tr><td>GPT-o1</td><td>-</td><td>0.0374</td><td>0.2006</td><td>-</td><td>-</td><td>-</td></tr><tr><td>PaSa-GPT-4o</td><td>0.7595</td><td>0.1817</td><td>0.4488</td><td>-</td><td>-</td><td>-</td></tr><tr><td>PaSa-7b</td><td>0.7752</td><td>0.1881</td><td>0.5328</td><td>0.6932</td><td>0.6543</td><td>0.5494</td></tr><tr><td>PaSa-7b-ensemble</td><td>0.8244</td><td>0.1822</td><td>0.5568</td><td>0.7041</td><td>0.6795</td><td>0.5535</td></tr></table>

Table 14: Results on 100-sample subset of AutoScholarQuery test.

<table><tr><td> $c(a_t)$ </td><td>Crawler Recall</td><td>Crawler Actions</td><td>Precision</td><td>Recall</td></tr><tr><td>0</td><td>0.8239</td><td>1296.3</td><td>0.1388</td><td>0.4852</td></tr><tr><td>0.1</td><td>0.7931</td><td>382.4</td><td>0.1448</td><td>0.4834</td></tr><tr><td>0.2</td><td>0.7478</td><td>230.1</td><td>0.1489</td><td>0.4764</td></tr></table>

Table 15: Performance of the Crawler trained on different action cost $c ( a _ { t } )$ on AutoScholarQuery test set.

## 六、消融实验

We perform ablation studies in Table 7 to evaluate the individual contributions of exploring citation networks, RL training, and using the Selector as the reward model. The results indicate that removing the [Expand] action from the Crawler leads to a significant drop in the recall: a decrease of 22.98% on AutoScholarQuery and 32.21% on RealScholar-Query. Furthermore, RL training enhances recall by 6.24% on AutoScholarQuery and 19.96% on RealScholarQuery. The RL training curves are depicted in Figure 3 in Appendix D.2, where the training curves show a steady increase in return with the training steps, eventually converging after 200 steps. Finally, removing the Selector as an auxiliary reward model results in a 3.76% recall drop on AutoScholarQuery and a 9.63% drop on RealScholarQuery.

We investigate how to control agent behavior by adjusting the rewards in RL training. Experiments are conducted with varying reward coefficients α in Equation 1, and results are presented in Table 8. We report two metrics: crawler recall and crawler action. The crawler action refers to the total number of [Search] and [Expand] actions throughout the Crawler’s entire trajectory. As the reward increases, both crawler recall and crawler action increase, suggesting that adjusting rewards in RL training can effectively influence PaSa’s behavior.

<table><tr><td>α</td><td>Crawler Recall</td><td>Crawler Actions</td><td>Precision</td><td>Recall</td></tr><tr><td>0.5</td><td>0.7227</td><td>175.9</td><td>0.1458</td><td>0.4602</td></tr><tr><td>1.0</td><td>0.7708</td><td>319.8</td><td>0.1451</td><td>0.4792</td></tr><tr><td>1.5</td><td>0.7931</td><td>382.4</td><td>0.1448</td><td>0.4834</td></tr><tr><td>2.0</td><td>0.8063</td><td>785.5</td><td>0.1409</td><td>0.4869</td></tr></table>

Table 8: Performance of the Crawler trained on different reward coefficient α on AutoScholarQuery test set.

## 七、Benchmark 结果与解释

As shown in Table 4, PaSa-7b outperforms all baselines on AutoScholarQuery test set. Specifically, compared to the strongest baseline, PaSa-GPT-4o,

PaSa-7b demonstrates a 9.64% improvement in recall with comparable precision. Moreover, the recall of the Crawler in PaSa-7b is 3.66% higher than that in PaSa-GPT-4o. When compared to the best Google-based baseline, Google with GPT-4o, PaSa-7b achieves an improvement of 33.80%, 38.83% and 42.64% in Recall@20, Recall@50 and Recall@100, respectively.

We observe that using multiple ensembles of Crawler during inference can improve performance. Specifically, we use sampling decoding to run Crawler twice in the PaSa-7b-ensemble setting, which boosts Crawler recall by 3.34% on AutoScholarQuery and increases the final recall by 1.51%, with no significant change in precision.

To evaluate PaSa in a more realistic setting, we assess its effectiveness on RealScholarQuery. As illustrated in Table 5, PaSa-7b exhibits a greater advantage in real-world academic search scenarios. Compared to PaSa-GPT-4o, PaSa-7b achieves improvements of 30.36% in recall and 4.25% in precision. Against the best Google-based baseline on RealScholarQuery, Google with GPT-4o, PaSa-7b outperforms Google by 37.78%, 39.90%, and 39.83% in recall@20, recall@50 and recall@100, respectively. Additionally, the PaSa-7b-ensemble further enhances crawler recall by 4.32%, contributing to an overall 3.52% improvement in the recall of the entire agent system.

<table><tr><td rowspan="2">Method</td><td colspan="3">AutoScholarQuery</td><td colspan="3">RealScholarQuery</td></tr><tr><td>Crawler Recall</td><td>Precision</td><td>Recall</td><td>Crawler Recall</td><td>Precision</td><td>Recall</td></tr><tr><td>w/o [Expand]</td><td>0.3355</td><td>0.1445</td><td>0.2536</td><td>0.3359</td><td>0.6738</td><td>0.2890</td></tr><tr><td>w/o RL training</td><td>0.6556</td><td>0.1476</td><td>0.4210</td><td>0.4847</td><td>0.5155</td><td>0.4115</td></tr><tr><td>w/o Selector as RM</td><td>0.7041</td><td>0.1535</td><td>0.4458</td><td>0.5994</td><td>0.5489</td><td>0.5148</td></tr><tr><td>PaSa-7b</td><td>0.7931</td><td>0.1448</td><td>0.4834</td><td>0.7071</td><td>0.5146</td><td>0.6111</td></tr></table>

Table 7: Ablation study results on AutoScholarQuery test set and RealScholarQuery.

As both the final decision-maker and auxiliary reward model in RL training for the Crawler, the performance of the Selector is crucial. To evaluate its effectiveness, we collected a dataset of 200 query-paper pairs, annotating whether each paper meets the query’s requirements. This dataset serves as the benchmark for evaluating the Selector (see Appendix F for details). We then compared our Selector against GPT-4o (Hurst et al., 2024) and Qwen-2.5-7b (Yang et al., 2024), as shown in Table 6. The results show that our Selector achieves an F1 score of 85%, outperforming GPT-4o by 5% and Qwen-2.5-7b by 30%. Additionally, when compared to a setting where reasoning precedes decision token generation, the performance is comparable. Lastly, the Selector’s precision reaches 95%, confirming its effectiveness as an auxiliary reward model for the Crawler RL training.

## 八、总结

In this paper, we introduce PaSa, a novel paper search agent designed to provide comprehensive and accurate results for complex academic queries. PaSa is implemented within the AGILE, a reinforcement learning framework for LLM agents. To train PaSa, we developed AutoScholarQuery, a dataset of fine-grained academic queries and corresponding papers drawn from top-tier AI conference publications. To evaluate PaSa in real-world scenarios, we also constructed RealScholarQuery, a dataset of actual academic queries paired with annotated papers. Our experimental results demonstrate that PaSa outperforms all baselines, including Google, Google Scholar, and Google with GPT-4o, ChatGPT, GPT-o1, and PaSa-GPT-4o. In particular, PaSa-7B surpasses Google with GPT-4o by 37.78% in recall@20 and 39.90% in recall@50, while also exceeding PaSa-GPT-4o by 30.36% in recall and 4.25% in precision. These findings underscore that PaSa significantly improves the efficiency and accuracy of academic search.

## References

Shubham Agarwal, Issam H Laradji, Laurent Charlin, and Christopher Pal. 2024. Litllm: A toolkit for scientific literature review. arXiv preprint arXiv:2402.01788.

Marwah Alaofi, Luke Gallagher, Mark Sanderson, Falk Scholer, and Paul Thomas. 2023. Can generative llms create query variants for test collections? an exploratory study. In Proceedings of the 46th international ACM SIGIR conference on research and development in information retrieval, pages 1869– 1873.

A Anthropic. 2024. The claude 3 model family: Opus, sonnet, haiku; 2024. URL https://wwwcdn.anthropic.com/de8ba9b01c9ab7cbabf5c33b80b7 bbc618857627/Model\_Card\_Claude\_3.pdf.

Jinheon Baek, Sujay Kumar Jauhar, Silviu Cucerzan, and Sung Ju Hwang. 2024. Researchagent: Iterative research idea generation over scientific literature with large language models. arXiv preprint arXiv:2404.07738.

Andres M Bran, Sam Cox, Oliver Schilter, Carlo Baldassari, Andrew D White, and Philippe Schwaller. 2023. Chemcrow: Augmenting large-language models with chemistry tools. arXiv preprint arXiv:2304.05376.

Guangyao Chen, Siwei Dong, Yu Shu, Ge Zhang, Jaward Sesay, Börje F Karlsson, Jie Fu, and Yemin Shi. 2023. Autoagents: A framework for automatic agent generation. arXiv preprint arXiv:2309.17288.

Xiang Deng, Yu Gu, Boyuan Zheng, Shijie Chen, Sam Stevens, Boshi Wang, Huan Sun, and Yu Su. 2024. Mind2web: Towards a generalist agent for the web. Advances in Neural Information Processing Systems, 36.

Peiyuan Feng, Yichen He, Guanhua Huang, Yuan Lin, Hanchong Zhang, Yuchen Zhang, and Hang Li. 2024. Agile: A novel reinforcement learning framework of llm agents. Advances in Neural Information Processing Systems, 37:5244–5284.

Team Gemini. 2023. Gemini: a family of highly capable multimodal models. arXiv preprint arXiv:2312.11805.

Karan Girotra, Lennart Meincke, Christian Terwiesch, and Karl T Ulrich. 2023. Ideas are dimes a dozen: Large language models for idea generation in innovation. Available at SSRN 4526071.

Atharva Gundawar, Mudit Verma, Lin Guan, Karthik Valmeekam, Siddhant Bhambri, and Subbarao Kambhampati. 2024. Robust planning with llm-modulo framework: Case study in travel planning. arXiv preprint arXiv:2405.20625.

Michael Gusenbauer and Neal R Haddaway. 2020. Which academic search systems are suitable for systematic reviews or meta-analyses? evaluating retrieval qualities of google scholar, pubmed, and 26 other resources. Research synthesis methods, 11(2):181–217.

Michael Gusenbauer and Neal R Haddaway. 2021. What every researcher should know about searching– clarified concepts, search advice, and an agenda to improve finding in academia. Research synthesis methods, 12(2):136–147.

Aaron Hurst, Adam Lerer, Adam P Goucher, Adam Perelman, Aditya Ramesh, Aidan Clark, AJ Ostrow, Akila Welihinda, Alan Hayes, Alec Radford, et al. 2024. Gpt-4o system card. arXiv preprint arXiv:2410.21276.

Karl Kingsley, Gillian M Galbraith, Matthew Herring, Eva Stowers, Tanis Stewart, and Karla V Kingsley. 2011. Why not just google it? an assessment of information literacy skills in a biomedical science curriculum. BMC medical education, 11:1–8.

Minghan Li, Honglei Zhuang, Kai Hui, Zhen Qin, Jimmy Lin, Rolf Jagerman, Xuanhui Wang, and Michael Bendersky. 2023. Generate, filter, and fuse: Query expansion via multi-step keyword generation for zero-shot neural rankers. arXiv preprint arXiv:2311.09175.

Zhehui Liao, Maria Antoniak, Inyoung Cheong, Evie Yu-Yen Cheng, Ai-Heng Lee, Kyle Lo, Joseph Chee Chang, and Amy X Zhang. 2024. Llms as research tools: A large scale survey of researchers’ usage and perceptions. arXiv preprint arXiv:2411.05025.

Zhihan Liu, Hao Hu, Shenao Zhang, Hongyi Guo, Shuqi Ke, Boyi Liu, and Zhaoran Wang. 2023. Reason for future, act for now: A principled framework for autonomous llm agents with provable sample efficiency. arXiv preprint arXiv:2309.17382.

Chris Lu, Cong Lu, Robert Tjarko Lange, Jakob Foerster, Jeff Clune, and David Ha. 2024. The ai scientist: Towards fully aut

### 在线资源

- [论文：arXiv 2501.10120](https://arxiv.org/abs/2501.10120)
- [代码：GitHub](https://github.com/bytedance/pasa)
- [PDF源文件](/papers/2501.10120.pdf)
