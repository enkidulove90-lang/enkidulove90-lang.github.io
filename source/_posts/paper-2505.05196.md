---
title: "Stealthy LLM-Driven Data Poisoning Attacks Against Embedding-Based Retrieval-Augmented Recommender Systems"
date: 2025-05-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2505.05196
arxiv_id: "2505.05196"
---

## 一、简介

We present a systematic study of provider-side data poisoning in retrieval-augmented recommender systems (RAG-based). By modi fying only a small fraction of tokens within item descriptions—for instance, adding emotional keywords or borrowing phrases from semantically related items—an attacker can significantly promote or demote targeted items. We formalize these attacks under token-edit and semantic-similarity constraints, and we examine their efective ness in both promotion (long-tail items) and demotion (short-head items) scenarios. Our experiments on MovieLens, using two large language model (LLM) retrieval modules, show that even subtle attacks shift final rankings and item exposures while eluding naive detection. The results underscore the vulnerability of RAG-based pipelines to small-scale metadata rewrites, and emphasize the need for robust textual consistency checks and provenance tracking to thwart stealthy provider-side poisoning.

## 二、论文方法

本文采用提供方数据投毒攻击方法。攻击者选择长尾（提升）或热门（打压）项目，使用LLM在10%令牌编辑预算和SBERT语义相似度≥0.80约束下重写项目描述。设计了三种攻击：情感编辑、邻居借用和链式攻击。在RAG推荐管道中，先由Sentence Transformer检索候选，再由OpenAI LLM重排序，评估攻击对项目排名和系统级指标（Recall@K, nDCG@K）的影响。

## 三、论文里的图与解释

### 图 1

![High-level RAG architecture in a recommender setting. A retriever selects candidate items (step 1). An LLM uses these retrieved texts and user queries to re-rank or generate final recommendations (step 2). In our poisoning scenario (red arrow), an attacker subtly modifies item descriptions to alter how retrieval and generation perceive items.](/images/papers/2505.05196/figure_001_RAG_Attack_ver3.png)

**原图说明：** High-level RAG architecture in a recommender setting. A retriever selects candidate items (step 1). An LLM uses these retrieved texts and user queries to re-rank or generate final recommendations (step 2). In our poisoning scenario (red arrow), an attacker subtly modifies item descriptions to alter how retrieval and generation perceive items.

**图示解释：** 该图对应论文中的“High-level RAG architecture in a recommender setting. A retriever selects candidate items (step 1). An LLM uses these retrieved texts and user queries to re-rank or generate final recommendations (step 2). In our poisoning scenario (red arrow), an attacker subtly modifies item descriptions to alter how retrieval and generation perceive items.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：形式化了面向RAG推荐系统的提供方文本重写攻击，定义了提升和打压两种对抗目标，并引入令牌编辑预算和语义相似性约束来量化攻击的隐蔽性。
2. 创新点2：设计了三种基于LLM的文本攻击变体：情感编辑（注入情感词）、邻居借用（从语义相似项目借用短语）和链式攻击（两者结合），均可在低编辑预算下实现有效攻击。
3. 创新点3：通过实验对比OpenAI和Sentence Transformer两种检索模块，发现基于LLM的管道对文本修改更敏感，揭示了生成式重排序会放大对抗性文本信号。

## 五、实验数据集选择

We conduct our experiments on top of a retrieval-augmented recommendation (RAG) pipeline that integrates a Large Language Model (LLM) from OpenAI and a Sentence Transformer (ST) encoder for embedding-based retrieval. Specifically, the pipeline first employs the Sentence Transformer to select candidate items based on the semantic closeness of item descriptions, and then an OpenAI-based LLM re-ranks these candidates or generates final textual recommendations.

Although we report results primarily on the widely used Movie Lens “ml-latest-small” dataset in this paper, we have also evaluated the proposed methods on additional benchmark datasets; due to space limitations, we present here only the detailed findings for the MovieLens dataset.

Within the MovieLens corpus, we categorize items into long-tail (unpopular) vs. short-head (popular) segments, inject adversarial textual edits, and assess the resulting changes in item ranks and system-level metrics (e.g., Recall@??, nDCG@??). Our system rein dexes or retrains on these modified descriptions, thereby simulating real-world scenarios where metadata updates could inadvertently (or maliciously) be incorporated into a live recommender. We build the user profile for the retrieval stage in two ways: (1) Manual construction using a structured template; and (2) LLM-based summarization that generates a user’s preferences automatically. In Table 1 (Tab 2 and 3), we diferentiate these two methods when evaluating final recommendations. All remaining steps in our pipeline (retrieval and re-ranking) remain unchanged.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

We now present our key experimental findings, structured around these three main research questions (RQs).

RQ1: Are LLM-based textual attacks efective at pushing a target item ranking up or down (both at retrieval top-?? and recommendation stage top-??)?

RQ2: Does attack eficacy vary across LLMs model e.g., OpenAI vs. Sentence Transformer retrieval?

RQ3: How do these modifications afect overall recall or nDCG? Can poisoning degrade system-wide performance?

## 八、总结

Our work demonstrates that carefully designed textual perturbations (modifications) in item metadata can strategically alter recommendations in Retrieval-Augmented Generation (RAG) systems, emphasizing the need for robust textual provenance checks. Through a systematic exploration of diferent attack strategies—including emotional rewording, neighbor-based borrowing, and hybrid chain-ing—our experiments reveal that even small-scale semantic ma- nipulations can efectively boost the visibility of long-tail items or suppress popular ones, often while remaining stealthy and dificult to detect. These findings underscore the potential provider-side vulnerabilities in RAG-based pipelines and the necessity of defensive measures to safeguard recommendation integrity.

## References

[1] Arijit Ghosh Chowdhury, Md Mofijul Islam, Vaibhav Kumar, Faysal Hossain Shezan, Vinija Jain, and Aman Chadha. 2024. Breaking down the defenses: A comparative survey of attacks on large language models. arXiv preprint arXiv:2403.04786 (2024).

[2] Yashar Deldjoo, Zhankui He, Julian McAuley, Anton Korikov, Scott Sanner, Arnau Ramisa, René Vidal, Maheswaran Sathiamoorthy, Atoosa Kasirzadeh, and Silvia Milano. 2024. A Review of Modern Recommender Systems using Generative Models (Gen-RecSys). In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 6448–6458.

[3] Yashar Deldjoo, Zhankui He, Julian McAuley, Anton Korikov, Scott Sanner, Ar nau Ramisa, Rene Vidal, Maheswaran Sathiamoorthy, Atoosa Kasrizadeh, Silvia Milano, et al. 2024. Recommendation with Generative Models. arXiv preprint arXiv:2409.15173 (2024).

[4] Yashar Deldjoo, Nikhil Mehta, Maheswaran Sathiamoorthy, Shuai Zhang, Pablo Castells, and Julian McAuley. 2025. Toward Holistic Evaluation of Recommender Systems Powered by Generative Models. SIGIR’25 (2025).

[5] Yashar Deldjoo, Tommaso Di Noia, and Felice Antonio Merra. 2021. A survey on adversarial recommender systems: from attack/defense strategies to generative adversarial networks. ACM Computing Surveys (CSUR) 54, 2 (2021), 1–38.

[6] Wenqi Fan, Yujuan Ding, Liangbo Ning, Shijie Wang, Hengyun Li, Dawei Yin, Tat-Seng Chua, and Qing Li. 2024. A survey on rag meeting llms: Towards

retrieval-augmented large language models. In Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 6491–6501.

[7] Yi Liu, Gelei Deng, Yuekang Li, Kailong Wang, Zihao Wang, Xiaofeng Wang, Tianwei Zhang, Yepang Liu, Haoyu Wang, Yan Zheng, et al. 2023. Prompt Injection attack against LLM-integrated Applications. arXiv preprint arXiv:2306.05499 (2023).

[8] Fatemeh Nazary, Yashar Deldjoo, and Tommaso di Noia. 2025. Poison-rag: Adver sarial data poisoning attacks on retrieval-augmented generation in recommender systems. In European Conference on Information Retrieval. Springer, 239–251.

[9] N Reimers. 2019. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. arXiv preprint arXiv:1908.10084 (2019).

[10] Yifei Wang, Dizhan Xue, Shengjie Zhang, and Shengsheng Qian. 2024. BadAgent: Inserting and Activating Backdoor Attacks in LLM Agents. arXiv preprint arXiv:2406.03007 (2024).

[11] Alexander Wei, Nika Haghtalab, and Jacob Steinhardt. 2024. Jailbroken: How does llm safety training fail? Advances in Neural Information Processing Systems 36 (2024).

[12] Jiaqi Xue, Mengxin Zheng, Yebowen Hu, Fei Liu, Xun Chen, and Qian Lou. 2024. BadRAG: Identifying Vulnerabilities in Retrieval Augmented Generation of Large Language Models. arXiv preprint arXiv:2406.00083 (2024)

[13] Wei Zou, Runpeng Geng, Binghui Wang, and Jinyuan Jia. 2024. Poisonedrag: Knowledge poisoning attacks to retrieval-augmented generation of large lan-guage models. arXiv preprint arXiv:2402.07867 (2024).

### 在线资源

- [论文：arXiv 2505.05196](https://arxiv.org/abs/2505.05196)
- [PDF源文件](/papers/2505.05196.pdf)
