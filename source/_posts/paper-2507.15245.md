---
title: "SPAR: Scholar Paper Retrieval with LLM-based Agents for Enhanced Academic Search"
date: 2025-07-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2507.15245
arxiv_id: "2507.15245"
---

## 一、简介

Recent advances in large language models (LLMs) have opened new opportunities for academic literature retrieval. However, existing systems often rely on rigid pipelines and exhibit limited reasoning capabilities. We introduce SPAR, a multi-agent framework that incorporates RefChain-based query decomposition and query evolution to enable more flexible and effective search. To facilitate systematic evaluation, we also construct SPAR-Bench, a challenging benchmark with expertannotated relevance labels. Experimental results demonstrate that SPAR substantially outperforms strong baselines, achieving up to +56% F1 on AutoScholar and +23% F1 on SPARBench over the best-performing baseline. Together, SPAR and SPARBench provide a scalable, interpretable, and high-performing foundation for advancing research in scholarly retrieval. Code and data will be available at: https://github.com/xiaofengShi/SPAR

## 二、论文方法

We introduce SPAR (Scholar PAper Retrieval), an agent-based framework for academic literature search. Given a user query, SPAR first analyzes the input to identify search intent and perform query refinement (§ 3.1). It then conducts iterative retrieval via multi-source search, reference chain expansion, and query evolution (§ 3.2). Finally, it re-ranks the retrieved documents based on timeliness and authority (§ 3.3). An overview of the framework is shown in Figure 2, with each component detailed in the following subsections.

## 三、论文里的图与解释

### 图 1

![The architecture of RefChain.](/images/papers/2507.15245/figure_001_refchain.png)

**原图说明：** The architecture of RefChain.

**图示解释：** 该图对应论文中的“The architecture of RefChain.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![The overview of SPAR.](/images/papers/2507.15245/figure_002_overview.png)

**原图说明：** The overview of SPAR.

**图示解释：** 该图对应论文中的“The overview of SPAR.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Document volume at each filtering stage of the benchmark construction pipeline, showing the reduction from raw retrieval results to the final final set.](/images/papers/2507.15245/figure_005_sparbench_data_flow.png)

**原图说明：** Document volume at each filtering stage of the benchmark construction pipeline, showing the reduction from raw retrieval results to the final final set.

**图示解释：** 该图对应论文中的“Document volume at each filtering stage of the benchmark construction pipeline, showing the reduction from raw retrieval results to the final final set.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出基于RefChain的迭代检索与查询演化机制，模拟研究者递归追踪引用的行为，通过单层引用链扩展和基于检索历史的查询生成，在提升召回率的同时控制噪声。
2. 创新点2：设计模块化多智能体架构，包含查询理解、检索、查询演化、判断和重排序五个专用智能体，各司其职，无需训练即可灵活组合，支持多源数据接口。
3. 创新点3：构建SPARBench基准，采用多阶段标注流程（LLM粗筛+专家精标），包含50个真实复杂查询和560篇专家验证的相关文档，覆盖计算机科学和生物医学，填补了端到端学术检索评估的空白。

## 五、实验数据集选择

Table 7 shows the comparison of different models for relevance judgment on three open-source benchmarks. Qwen3-32B with brief instruction achieves the best average performance among all benchmarks.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

• Realistic Queries: Simulate authentic academic search behavior through multi-intent, semantically rich queries with incomplete grammar and minor spelling errors.

• Cross-Domain Coverage: Supports evaluation across computer science and biomedicine, enabling assessment of domain-general and domain-specific retrieval capabilities.

• Multi-Source Corpus: Integrates documents from arXiv, PubMed, OpenAlex, and Semantic Scholar to reduce source-specific bias and improve retrieval realism.

![](images/72de114794ad795ad02a7e0224ccd6fcc0507829c5f2cbaf7be741128f21e582.jpg)  
Figure 3: SPARBench construction pipeline. The process includes expert-curated seed queries, GPT-4o-based query expansion, multi-source document retrieval, and a three-stage relevance filtering procedure combining language models and expert annotation.

• High-Quality Annotations: A multi-stage labeling pipeline combines LLM-based filtering with expert validation, ensuring high-quality annotations and domain consistency.

## 八、总结

We present SPAR, a modular multi-agent framework for academic paper retrieval, designed to tackle the challenges of underspecified queries, fragmented sources, and evolving information needs. SPAR consists of four key stages: (1) a Query Understanding agent that interprets user intent through intent classification, domain detection, and temporal constraint parsing, followed by intent-aware query refinement; (2) an Iterative Retrieval phase that integrates source-adaptive querying and RefChain-based citation expansion for recall-oriented exploration; (3) a Query Evolver agent that diversifies search trajectories by generating follow-up queries based on previously retrieved papers; and (4) a Reranker that ranks results using relevance, timeliness, and publication authority.

To evaluate SPAR, we construct SPARBench, a benchmark of semantically complex academic queries with expert-labeled relevance. Experiments on SPARBench and AutoScholar demonstrate that SPAR consistently outperforms strong baselines. It achieves an F1 score of 0.3843 on AutoScholar, a +56% improvement over PaSa, and 0.3015 on SPARBench, the only method delivering balanced performance across all metrics.

Our results validate the synergy of symbolic planning (RefChain), LLM-powered query evolution, and agent-based modular design in addressing the complexity of scholarly retrieval tasks. SPAR and SPARBench offer a reproducible and extensible foundation for advancing intelligent academic search systems.

## References

Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, and 1 others. 2023. Gpt-4 technical report. arXiv preprint arXiv:2303.08774.

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal, Danqi Chen, and Tianyu Gao. 2024. Litsearch: A retrieval benchmark for scientific literature search. arXiv preprint arXiv:2407.18940.

Allen Institute for AI. 2025. Ai2 paper finder: LLMpowered academic search assistant. https:// paperfinder.allen.ai/chat. Accessed: 2025-07- 09.

Abhijit Anand, Vinay Setty, Avishek Anand, and 1 others. 2023. Context aware query rewriting for text rankers using llm. arXiv preprint arXiv:2308.16753.

Nicholas J Belkin. 1980. Anomalous states of knowl edge as a basis for information retrieval. Canadian journal of information science, 5(1):133–143.

Kathi Canese and Sarah Weis. 2013. Pubmed: the bibli ographic database. The NCBI handbook, 2(1):2013.

Claudio Carpineto and Giovanni Romano. 2012. A survey of automatic query expansion in information retrieval. Acm Computing Surveys (CSUR), 44(1):1– 50.

A Cohan, S Feldman, I Beltagy, D Downey, and DS Weld. 2004. Specter: document-level representation learning using citation-informed transformers. 2020. arXiv preprint arXiv:2004.07180.

W Bruce Croft, Donald Metzler, and Trevor Strohman. 2010. Search engines: Information retrieval in practice, volume 520. Addison-Wesley Reading.

Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Alex Vaughan, and 1 others. 2024. The llama 3 herd of models. arXiv preprint arXiv:2407.21783.

Michael Gusenbauer and Neal R Haddaway. 2020. Which academic search systems are suitable for systematic reviews or meta-analyses? evaluating retrieval qualities of google scholar, pubmed, and 26 other resources. Research synthesis methods, 11(2):181–217.

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin, Yuchen Zhang, Hang Li, and 1 others. 2025. Pasa: An llm agent for comprehensive academic paper search. arXiv preprint arXiv:2501.10120.

Aaron Hurst, Adam Lerer, Adam P Goucher, Adam Perelman, Aditya Ramesh, Aidan Clark, AJ Ostrow, Akila Welihinda, Alan Hayes, Alec Radford, and 1 others. 2024. Gpt-4o system card. arXiv preprint arXiv:2410.21276.

Rodney Kinney, Chloe Anastasiades, Russell Authur, Iz Beltagy, Jonathan Bragg, Alexandra Buraczynski, Isabel Cachola, Stefan Candra, Yoganand Chandrasekhar, Arman Cohan, and 1 others. 2023. The semantic scholar open data platform. arXiv preprint arXiv:2301.10140.

Aixin Liu, Bei Feng, Bing Xue, Bingxuan Wang, Bochao Wu, Chengda Lu, Chenggang Zhao, Chengqi Deng, Chenyu Zhang, Chong Ruan, and 1 others. 2024. Deepseek-v3 technical report. arXiv preprint arXiv:2412.19437.

Jie Liu and Barzan Mozafari. 2024. Query rewriting via large language models. arXiv preprint arXiv:2403.09060.

Xinbei Ma, Yeyun Gong, Pengcheng He, Hai Zhao, and Nan Duan. 2023. Query rewriting in retrievalaugmented large language models. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, pages 5303–5315.

Jason Priem, Heather Piwowar, and Richard Orr. 2022. Openalex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv preprint arXiv:2205.01833.

Gemini Team, Rohan Anil, Sebastian Borgeaud, Jean-Baptiste Alayrac, Jiahui Yu, Radu Soricut, Johan Schalkwyk, Andrew M Dai, Anja Hauth, Katie Millican, and 1 others. 2023. Gemini: a family of highly capable multimodal models. arXiv preprint arXiv:2312.11805.

Jaime Teevan, Susan T Dumais, and Eric Horvitz. 2005. Personalizing search via automated analysis of interests and activities. In Proceedings of the 28th annual international ACM SIGIR conference on Research and development in information retrieval, pages 449– 456.

Rita Vine. 2006. Google scholar. Journal of the Medical Library Association, 94(1):97.

Ellen Voorhees,

### 在线资源

- [论文：arXiv 2507.15245](https://arxiv.org/abs/2507.15245)
- [代码：GitHub](https://github.com/xiaofengShi/SPAR)
- [PDF源文件](/papers/2507.15245.pdf)
