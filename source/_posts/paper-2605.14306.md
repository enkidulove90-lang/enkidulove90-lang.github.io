---
title: "PaSaMaster: Self-Evolving Agentic Literature Retrieval"
date: 2026-05-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2605.14306
arxiv_id: "2605.14306"
---

## 一、简介

Scientific literature retrieval must understand complex search intents while preserving source authenticity. Traditional keyword and embedding-based systems return authentic sources but miss nuanced intents, whereas large language models capture richer intents but may fabricate citations. We introduce PaSaMaster, a Recursive Self-Evolving agentic literature retrieval system that iteratively analyzes intent, retrieves verified papers and ranks them with evidence-grounded relevance scores. PaSaMaster combines self-evolving retrieval that refines search intent from ranked evidence over time, hallucination-free ranking over verified papers rather than generated citations, and cost-efficient planning–retrieval separation that reserves frontier LLMs for intent understanding while delegating retrieval and scoring to lightweight models and customized corpora. Across 38 disciplines in PaSaMaster-Bench, PaSaMaster achieves a 16.5× higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost, while reducing source hallucination from 32.66% in generative LLMs to zero: https://github.com/sjtu-sai-agents/PaSaMaster

Keywords: Scientific Literature Discovery, Agentic AI, Large Language Models

![](images/b3d40710676739648d7d5154aec61a1e34ff00ac635fbd5560421f95feab0b92.jpg)  
Fig. 1 Overview of PaSaMaster and PaSaMaster-Bench. a, PaSaMaster converts a complex natural-language search intent into a verified, evidence-ranked paper list through three layers: a Navigator that refines intent and search strategy, a Librarian Swarm that retrieves, verifies and scores candidate papers, and verified corpora and tools that ground all outputs in real sources. b, PaSaMaster-Bench evaluates complex literature retrieval through expert-written search intents, multi-channel candidate retrieval and checklist-based expert annotation. The benchmark contains 244 tasks across 38 disciplines, enabling evaluation of intent understanding, source reliability and ranking quality.

Table 1 The Five Paradigms of Scientific Literature Discovery. Existing paradigms each improve one aspect of literature retrieval, but fail to jointly achieve adaptive intent understanding, hallucination-free evidence grounding, and cost-efficient scaling. PaSaMaster resolves these limitations through agentic Recursive Self-Evolving, evidence-grounded retrieval.

<table><tr><td>Paradigm Level</td><td>Representative Systems</td><td>Intent Adaptivity</td><td>Source Reliability</td><td>Cost Efficiency</td></tr><tr><td>Level 0: Lexical Retrieval</td><td>Google Scholar [1], PubMed [2]</td><td>Keyword-based; severe intent compression</td><td>Verified indexed papers</td><td>Efficient but semantically shallow</td></tr><tr><td>Level 1: Semantic Retrieval</td><td>OpenScholar [3], Bohrium Navigator [4]</td><td>Passive embedding matching; limited intent compression</td><td>Verified indexed papers</td><td>Efficient but semantically shallow</td></tr><tr><td>Level 2: Generative LLMs</td><td>GPT-5.2 [5], Gemini 3.1 Pro [6], DeepSeek [7]</td><td>Strong natural-language understanding</td><td>Prone to hallucinated papers</td><td>Expensive to deploy at scale</td></tr><tr><td>Level 3: Fixed-Pipeline Agentic Retrieval</td><td>Google Scholar Labs [8], PaSa [9]</td><td>User intent fixed at the outset; no cognition update during retrieval</td><td>Verified indexed papers</td><td>Cost-controlled, but constrained by fixed intent interpretation</td></tr><tr><td>Level 4: Recursive Self-Evolving Agentic Retrieval</td><td>PaSaMaster (Ours)</td><td>Iteratively refines intent using ranked evidence</td><td>Verified indexed papers</td><td>Cost-efficient planning-retrieval separation</td></tr></table>

Scientific literature retrieval is the axiomatic starting point of all scientific inquiry $[10]$ . Before formulating hypotheses, designing experiments, or building new theories, researchers must fundamentally navigate the vast and ever-expanding corpus of existing knowledge $[11]$ . However, the volume of scientific publications has grown exponentially over recent decades, decisively overwhelming the fixed cognitive bandwidth of individual researchers $[12–14]$ . This severe information overload has driven an inevitable reliance on artificial intelligence to automate and accelerate knowledge discovery $[15]$ . More importantly, modern literature search is rarely a simple keyword lookup $[16, 17]$ . Researchers often express complex academic intents involving technical constraints, application contexts, and implicit background knowledge $[10, 18, 19]$ . As large language models reshape scientific research workflows, literature retrieval therefore faces a new central challenge: how to deeply understand complex search intents while ensuring that every returned source is real and verifiable $[19, 20]$ .

Existing literature retrieval systems still struggle to jointly achieve complex intent understanding and source authenticity. Some methods preserve source authenticity at the cost of shallow intent understanding $[1, 3, 4]$ , whereas others improve semantic comprehension while sacrificing factual reliability $[5–7, 21–23]$ . This creates a persistent tradeoff between reliable but limited retrieval and more intelligent but less trustworthy literature discovery.

The tradeoff between intent understanding and source reliability is clearer when viewed through the evolution of literature retrieval paradigms (Table 1). Level 0 (Lexical Retrieval) [1, 2] guarantees source authenticity through indexed databases, but reduces complex research intents to rigid keywords, causing severe intent compression. Level 1 (Semantic Retrieval) [3, 4] improves over exact keyword matching by using embedding-based similarity and retrieval-augmented matching [24, 25], but still treats retrieval as passive query-document matching and lacks the ability to actively clarify, decompose, or refine complex intents. Level 2 (Generative LLMs) [5-7, 21-23] offers stronger intent comprehension, yet its probabilistic generation introduces fabricated papers [26, 27], undermining the factual trust required for scientific inquiry. Level 3 (Fixed-Pipeline Agentic Retrieval) [8, 9] mitigates source hallucination by grounding

LLM agents in verifiable retrieval tools $[28–33]$ . However, these systems typically follow a predefined retrieve-read-answer pipeline in which the interpretation of the user question is largely fixed at the beginning. For complex research intents, this initial interpretation can be incomplete or biased toward only part of the request, causing later retrieval steps to miss relevant subtopics or return papers that satisfy only some constraints. This limitation motivates retrieval systems that can update their understanding of the intent as evidence accumulates.

The unresolved need for adaptive, verifiable and efficient retrieval motivates Level 4 (Recursive Self-Evolving Agentic Retrieval), represented by PaSaMaster. PaSaMaster is a Recursive Self-Evolving agentic literature retrieval system that iteratively analyzes intent, retrieves verified papers and ranks them with evidence-grounded relevance scores. Rather than treating literature search as one-shot query-document matching problem, PaSaMaster formulates scientific literature discovery as a Recursive Self-Evolving intent-paper relevance ranking process. This design enables the system to align with complex research intents while ensuring that every returned source is real, verifiable, and grounded in customized corpora.

PaSaMaster is built on three key designs. First, Recursive Self-Evolving retrieval: it transforms literature retrieval from one-shot query–document matching into an adaptive search process that evolves over time $[34, 35]$ , where retrieved and ranked evidence is used to identify coverage gaps, refine the research intent, and guide subsequent retrieval rounds. Second, hallucination-free ranking: it treats literature discovery as intent–paper relevance ranking rather than generation, and trains a lightweight Ranker on multidisciplinary query–paper evidence so that Librarian agents can make expert-style relevance judgments across disciplines while ranking only verified papers grounded in original evidence. Third, cost-efficient planning–retrieval separation: it uses frontier LLMs only for intent understanding and refinement, while delegating large-scale retrieval and relevance scoring to customized scientific corpora and lightweight models. Together, these designs enable PaSaMaster to align with complex research intents while maintaining source verifiability and cost-efficient scalability.

To evaluate retrieval capability on complex natural-language literature search problems, we introduce PaSaMaster-Bench, the first multidisciplinary literature retrieval benchmark designed for complex search intents. Unlike conventional retrieval benchmarks $[9, 19, 36–38]$ built around short keyword queries, PaSaMaster-Bench focuses on highly specific, multi-constrained natural language search intents that require systems to search, verify, and rank all papers satisfying explicit criteria. The benchmark contains 244 expert-curated tasks spanning 38 scientific disciplines, with queries, constraints, target paper lists, and evaluation checklists annotated and verified by human domain experts.

The PaSaMaster-Bench evaluation reveals the severe inaccuracy and incompleteness of traditional keyword retrieval, with PaSaMaster improving F1-score by $16.5\times$ . The evaluation also exposes the unreliability of generative LLMs, which exhibit hallucination rates up to 32.66%. Remarkably, PaSaMaster outperforms GPT-5.2 by 37.8% while using only 1% of its computational cost, and maintains zero source hallucination. These results demonstrate that Recursive Self-Evolving, evidence-grounded relevance ranking can improve complex intent understanding, eliminate source hallucination and enable low-cost scientific literature discovery at scale.

## 二、论文方法

采用三层智能体架构：导航器负责意图消歧、检查清单构建和搜索规划；馆员群执行多通道检索、证据验证和相关性评分；验证语料库层提供真实论文支撑。通过导航器与馆员之间的策略-反馈循环实现检索的自进化，并使用轻量级排序器对多学科查询-论文对进行训练。

## 三、论文里的图与解释

### 图 1

![Fig. 1 Overview of PaSaMaster and PaSaMaster-Bench. a, PaSaMaster converts a complex natural-language search intent into a verified, evidence-ranked paper list through three layers: a Navigator that refines intent and search strategy, a Librarian Swarm that retrieves, verifies and scores candidate papers, and verified corpora and tools that ground all outputs in real sources. b, PaSaMaster-Bench evaluates complex literature retrieval through expert-written search intents, multi-channel candidate retrieval and checklist-based expert annotation. The benchmark contains 244 tasks across 38 disciplines, enabling evaluation of intent understanding, source reliability and ranking quality.](/images/papers/2605.14306/b3d40710676739648d7d5154aec61a1e34ff00ac635fbd5560421f95feab0b92.jpg)

**原图说明：** Fig. 1 Overview of PaSaMaster and PaSaMaster-Bench. a, PaSaMaster converts a complex natural-language search intent into a verified, evidence-ranked paper list through three layers: a Navigator that refines intent and search strategy, a Librarian Swarm that retrieves, verifies and scores candidate papers, and verified corpora and tools that ground all outputs in real sources. b, PaSaMaster-Bench evaluates complex literature retrieval through expert-written search intents, multi-channel candidate retrieval and checklist-based expert annotation. The benchmark contains 244 tasks across 38 disciplines, enabling evaluation of intent understanding, source reliability and ranking quality.

**图示解释：** 该图对应论文中的“Fig. 1 Overview of PaSaMaster and PaSaMaster-Bench. a, PaSaMaster converts a complex natural-language search intent into a verified, evidence-ranked paper list through three layers: a Navigator that refines intent and search strategy, a Librarian Swarm that retrieves, verifies and scores candidate papers, and verified corpora and tools that ground all outputs in real sources. b, PaSaMaster-Bench evaluates complex literature retrieval through expert-written search intents, multi-channel candidate retrieval and checklist-based expert annotation. The benchmark contains 244 tasks across 38 disciplines, enabling evaluation of intent understanding, source reliability and ranking quality.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：递归自进化检索机制，将文献检索从一次性查询-文档匹配转变为迭代过程，利用已排序证据持续更新系统对用户意图的理解，从而发现初始查询遗漏的相关论文。
2. 创新点2：无幻觉的意图-论文相关性排序，将文献发现视为排序问题而非生成问题，所有候选论文必须从验证语料库中检索，且每个相关性判断都需有原始论文证据支撑，从根本上消除源幻觉。
3. 创新点3：成本高效的规划-检索分离架构，将前沿LLM仅用于意图理解和策略规划，而将大规模检索和轻量级相关性评分委托给定制语料库和小模型，实现高质量检索的同时大幅降低计算成本。

## 五、实验数据集选择

We compare PaSaMaster with four groups of baselines. Lexical retrieval systems, represented by Google Scholar $[1]$ , search verified indexed records but mainly rely on keyword matching. Semantic retrieval systems, including OpenScholar $[3]$ and Bohrium Science Navigator $[4]$ , use semantic matching or retrieval-augmented scientific search. Generative LLM baselines include DeepSeek, Kimi, MiniMax, GLM, Gemini and GPT $[5–7, 21–23]$ . These LLMs are evaluated as tool-assisted search agents rather than closed-book models: each is equipped with Search and Visit tools and prompted to search, inspect evidence and verify sources before returning papers, following tool-use agent evaluation protocols $[31–33]$ . For fixed-pipeline agentic retrieval, we use Google Scholar Labs $[8]$ as a representative predefined agentic search workflow.

Retrieval quality is measured at K = 20 using standard information retrieval metrics $[39, 40]$ . Recall@20 measures how many ground-truth target papers are recovered in the top 20 results; Precision@20 measures how many returned top-20 papers are genuine target papers; F1-score@20 summarizes the balance between recall and precision; and NDCG@20 measures whether relevant papers are ranked closer to the top. We also report per-query cost and source hallucination rate. Cost captures the computational expense of interpreting complex constraints and carrying out retrieval, while hallucination rate measures the proportion of returned papers that cannot be matched to a real scholarly record or contain provably wrong source metadata. Together, these metrics assess intent comprehension, source authenticity and cost-effective retrieval.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

- PaSaMaster-Bench

## 八、总结

论文未提供可独立提取的总结章节。

## References

[1] Google: Google Scholar. https://scholar.google.com/ (2026)

[2] National Center for Biotechnology Information: PubMed. https://pubmed.ncbi.nlm.nih.gov/ Accessed 2026-05-08

[3] Asai, A., He, J., Shao, R., Shi, W., Singh, A., Chang, J.C., Lo, K., Soldaini, L., Feldman, S., D'arcy, M., Wadden, D., Latzke, M., Tian, M., Ji, P., Liu, S., Tong, H., Wu, B., Xiong, Y., Zettlemoyer, L., Neubig, G., Weld, D., Downey, D., Yih, W.-t., Koh, P.W., Hajishirzi, H.: OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs (2024). http://arxiv.org/abs/2411.14199

[4] Zhang, L., Chen, S., Cai, Y., Chai, J., Chang, J., Chen, K., Chen, Z.X., Ding, Z., Du, Y., Gao, Y., Gao, Y., Gao, J., Gao, Z., Gu, Q., Hong, Y., Huang, Y., Fang, X., Ji, X., Ke, G., Lei, Z., Li, X., Li, Y., Liao, R., Lin, H., Lin, X., Liu, Y., Liu, X., Liu, Z., Lu, J., Miao, T., Que, H., Sun, W., Wang, Y., Wu, B., Xue, T., Ye, R., Zeng, J., Zhang, D., Zhang, J., Zhang, L., Zhang, T., Zhang, W., Zhang, Y., Zhang, Z., Zheng, H., Zhou, H., Zhu, T., Zhu, X., Zhou, Q., E, W.: Bohrium + SciMaster: Building the Infrastructure and Ecosystem for Agentic Science at Scale (2025). https://arxiv.org/abs/2512.20469

[5] OpenAI: Introducing GPT-5.4 (2026). https://openai.com/zh-Hans-CN/index/introducing-gpt-5-4/

[6] Google DeepMind: Gemini 3.1 Pro: A smarter model for your most complex tasks (2026). https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-pro/

[7] DeepSeek-AI, Liu, A., Mei, A., Lin, B., Xue, B., Wang, B., Xu, B., Wu, B., Zhang, B., Lin, C., Dong, C., Lu, C., Zhao, C., Deng, C., Xu, C., Ruan, C., Dai, D., Guo, D., Yang, D., Chen, D., Li, E., Zhou, F., Lin, F., Dai, F., Hao, G., Chen, G., Li, G., Zhang, H., Xu, H., Li, H., Liang, H., Wei, H., Zhang, H., Luo, H., Ji, H., Ding, H., Tang, H., Cao, H., Gao, H., Qu, H., Zeng, H., Huang, J., Li, J., Xu, J., Hu, J., Chen, J., Xiang, J., Yuan, J., Cheng, J., Zhu, J., Ran, J., Jiang, J., Qiu, J., Li, J., Song, J., Dong, K., Gao, K., Guan, K., Huang, K., Zhou, K., Huang, K., Yu, K., Wang, L., Zhang, L., Wang, L., Zhao, L., Yin, L., Guo, L., Luo, L., Ma, L., Wang, L., Zhang, L., Zhang, M., Zhang, M., Tang, M., Zhou, M., Huang, P., Cong, P., Wang, P., Wang, Q., Zhu, Q., Li, Q., Chen, Q., Du, Q., Xu, R.,

Ge, R., Zhang, R., Pan, R., Wang, R., Yin, R., Xu, R., Shen, R., Zhang, R., Lu, S., Zhou, S., Chen, S., Cai, S., Chen, S., Hu, S., Liu, S., Hu, S., Ma, S., Wang, S., Yu, S., Zhou, S., Pan, S., Zhou, S., Ni, T., Yun, T., Pei, T., Ye, T., Yue, T., Zeng, W., Liu, W., Liang, W., Gao, W., Zhang, W., Bi, X., Liu, X., Wang, X., Chen, X., Zhang, X., Nie, X., Cheng, X., Liu, X., Xie, X., Liu, X., Yu, X., Yang, X., Li, X., Su, X., Lin, X., Zhang, Y., Xu, Y., Li, Y., Zhao, Y., Sun, Y., Wang, Y., Yu, Y., Zhang, Y., Shi, Y., Xiong, Y., He, Y., Piao, Y., Wang, Y., Tan, Y., Ma, Y., Liu, Y., Guo, Y., Wu, Y., Ou, Y., Wang, Y., Gong, Y., Zou, Y., Xiong, Y., Luo, Y., You, Y., Liu, Y., Zhou, Y., Ren, Z., Sha, Z., Fu, Z., Xu, Z., Xie, Z., Zhang, Z., Hao, Z., Gou, Z., Ma, Z., Yan, Z., Shao, Z., Wu, Z., Li, Z., Gu, Z., Zhu, Z., Li, Z., Xie, Z., Gao, Z., Pan, Z.: DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models (2025). https://arxiv.org/abs/2512.02556

[8] Google: Scholar Labs: An AI Powered Scholar Search. Google Scholar Blog (2025). https://scholar.googleblog.com/2025/11/scholar-labs-ai-powered-scholar-search.html

[9] He, Y., Huang, G., Feng, P., Lin, Y., Zhang, Y., Li, H., E, W.: PaSa: An LLM Agent for Comprehensive Academic Paper Search (2025). https://arxiv.org/abs/2501.10120

[10] Gusenbauer, M., Haddaway, N.R.: What every researcher should know about searching—clarified concepts, search advice, and an agenda to improve finding in academia. Research Synthesis Methods 12(2), 136–147 (2021) https://doi.org/10.1002/jrsm.1457

[11] Fortunato, S., Bergstrom, C.T., Börner, K., Evans, J.A., Helbing, D., Milojević, S., Petersen, A.M., Radicchi, F., Sinatra, R., Uzzi, B., Vespignani, A., Waltman, L.,

### 在线资源

- [论文：arXiv 2605.14306](https://arxiv.org/abs/2605.14306)
- [代码：GitHub](https://github.com/sjtu-sai-agents/PaSaMaster)
- [PDF源文件](/papers/2605.14306.pdf)
