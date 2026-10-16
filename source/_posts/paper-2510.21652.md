---
title: "AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite"
date: 2025-10-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2510.21652
arxiv_id: "2510.21652"
---

## 一、简介

AI agents hold the potential to revolutionize scientific productivity by automating literature reviews, replicating experiments, analyzing data, and even proposing new directions of inquiry; indeed, there are now many such agents, ranging from generalpurpose “deep research” systems to specialized science-specific agents, such as AI Scientist and AIGS. Rigorous evaluation of these agents is critical for progress. Yet existing benchmarks fall short on several fronts: they often (1) lack reproducible agent tools necessary for a controlled comparison of core agentic capabilities; (2) do not account for confounding variables such as model cost and tool access; (3) do not provide standardized interfaces for quick agent prototyping and evaluation; (4) fail to provide holistic, product-informed measures of real-world use cases such as science research; and (5) lack comprehensive baseline agents necessary to identify true advances. In response, we define principles and tooling for more rigorously benchmarking agents. Using these, we present AstaBench, a suite that provides a holistic measure of agentic ability to perform scientific research, comprising 2400+ problems spanning the entire scientific discovery process and multiple scientific domains, and including many problems inspired by actual user requests to deployed Asta agents. Our suite comes with the first scientific research environment with production-grade search tools that enable controlled, reproducible evaluation, better accounting for confounders. Alongside, we provide a comprehensive suite of nine science-optimized classes of Asta agents and numerous baselines. Our extensive evaluation of 57 agents across 22 agent classes reveals several interesting findings, most importantly that despite meaningful progress on certain individual aspects, AI remains far from solving the challenge of science research assistance.

## 二、论文方法

Implement the integration of CBP and IDL by:
1. Using CBP to generate complex reasoning chains for the questions
2. Using IDL to select similar examples with their reasoning steps
3. Combining both in a unified prompt that includes both the complex
↔ reasoning guidance and the similar examples
4. Implementing an adaptive mechanism that adjusts the weight given to
↔ CBP vs. IDL based on question characteristics

## 三、论文里的图与解释

### 图 1

![Figure 4: Score vs. cost analysis for Literature Understanding QA benchmarks (Table 13). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (ScholarQA-CS2, LitQA2-FullText). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.](/images/papers/2510.21652/d56e7480c924a302120c09584c6cbcc8c29c7ac9838e8ceb69979c8f7eddeffe.jpg)

**原图说明：** Figure 4: Score vs. cost analysis for Literature Understanding QA benchmarks (Table 13). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (ScholarQA-CS2, LitQA2-FullText). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.

**图示解释：** 该图对应论文中的“Figure 4: Score vs. cost analysis for Literature Understanding QA benchmarks (Table 13). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (ScholarQA-CS2, LitQA2-FullText). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Figure 8: Score vs. cost analysis for End-to-End Discovery benchmarks (Table 17). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (E2E-Bench, E2E-Bench-Hard). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.](/images/papers/2510.21652/f58ba4301a10798320cf700d000c1356314d661dd11c9e3d959f875fa449509d.jpg)

**原图说明：** Figure 8: Score vs. cost analysis for End-to-End Discovery benchmarks (Table 17). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (E2E-Bench, E2E-Bench-Hard). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.

**图示解释：** 该图对应论文中的“Figure 8: Score vs. cost analysis for End-to-End Discovery benchmarks (Table 17). Points indicate means; error bars denote 95% confidence intervals. Points on the Pareto frontier are connected with dotted lines, representing optimal quality-cost trade-offs for each eval (E2E-Bench, E2E-Bench-Hard). Note: the x-axis (cost) uses a log scale. † denotes models not pinned to a date-stamped version.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

Authors listed in alphabetical order within each section:

• Project leadership, framework, and general agent development: Jonathan Bragg, Mike D’Arcy

• Research by task category (benchmarks and agents):

– Literature Understanding (paper finding): Dan Bareket, Yoav Goldberg, Sigal Rahamimov, Aryeh Tiktinsky, Guy Wiener

– Literature Understanding (summarization and QA): Nishant Balepur, Doug Downey, Sergey Feldman, Dany Haddad, Jena D. Hwang, Varsha Kishore, Aakanksha Naik, Amanpreet Singh, Daniel S. Weld

– Literature Understanding (table generation):

Benchmark: Aakanksha Naik

\* Agent: Mike D’Arcy, Dany Haddad, Aakanksha Naik

– Code & Execution: Mike D’Arcy, Kyle Richardson

– Data Analysis: Bodhisattwa Prasad Majumder, Harshit Surana

– End-to-End Discovery: Peter Clark, Bhavana Dalvi, Peter Jansen, Rosni Vasu

## 五、实验数据集选择

This section presents additional details on evaluating on the LitQA2 dataset. When evaluating on our own literature search agent (PaperFinder), we provide it with the question text as is, without including the multiple choices and without attempting to translate the question into a paper-finding query-form. We did not do any task-specific modifications or tuning of PaperFinder for this task.

Table 22: Models run in our study. Model names are mapped to the model identifiers used during API calls, with ‡ used to disambiguate models that were called without their date identifiers for full transparency.

<table><tr><td>Name</td><td>Model ID</td><td>Organization</td><td>Open-Weight</td><td>Inference Provider</td></tr><tr><td>gpt-3.5-turbo</td><td>gpt-3.5-turbo-0125</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-4o-mini</td><td>gpt-4o-mini</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-4o</td><td>gpt-4o-2024-08-06</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-4o†</td><td>gpt-4o</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-4.1</td><td>gpt-4.1-2025-04-14</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-4.1†</td><td>gpt-4.1</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-4.1-mini</td><td>gpt-4.1-mini</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-5-mini</td><td>gpt-5-mini-2025-08-07</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-5-mini†</td><td>gpt-5-mini</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-5</td><td>gpt-5-2025-08-07</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>gpt-5†</td><td>gpt-5</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>o3-mini</td><td>o3-mini</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>o3</td><td>o3-2025-04-16</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>o3†</td><td>o3</td><td>OpenAI</td><td>×</td><td>OpenAI</td></tr><tr><td>claude-3-5-haiku</td><td>claude-3-5-haiku-20241022</td><td>Anthropic</td><td>×</td><td>Anthropic</td></tr><tr><td>claude-3-7-sonnet</td><td>claude-3-7-sonnet-20250219</td><td>Anthropic</td><td>×</td><td>Anthropic</td></tr><tr><td>claude-sonnet-4</td><td>claude-sonnet-4-20250514</td><td>Anthropic</td><td>×</td><td>Anthropic</td></tr><tr><td>gemini-2-flash</td><td>gemini-2.0-flash</td><td>Google</td><td>×</td><td>Google Vertex AI</td></tr><tr><td>gemini-2.5-flash</td><td>gemini-2.5-flash-preview-05-20</td><td>Google</td><td>×</td><td>Google Vertex AI</td></tr><tr><td>gemini-2.5-flash†</td><td>gemini-2.5-flash</td><td>Google</td><td>×</td><td>Google Vertex AI</td></tr><tr><td>gemini-2.5-pro</td><td>gemini-2.5-pro</td><td>Google</td><td>×</td><td>Google Vertex AI</td></tr><tr><td>sonar-deep-research</td><td>sonar-deep-research</td><td>Perplexity</td><td>×</td><td>Perplexity</td></tr><tr><td>llama-4-scout</td><td>Llama-4-Scout-17B-16E-Instruct</td><td>Meta</td><td>√</td><td>Together AI</td></tr><tr><td>llama-3.1-</td><td>llama-3.1-</td><td rowspan="2">Meta /Allen AI</td><td rowspan="2">√</td><td rowspan="2">Self-hosted</td></tr><tr><td>openscholar-8b</td><td>openscholar-8b</td></tr></table>

As LitQA2 was designed as a full-text search benchmark, our main results are on the LitQA2- FullText-Search subset, for which our corpus contains full-text to all papers. Here we report results also on the original LitQA2 dataset of Skarlinski et al. (2024), in which 114 out of the 199 queries have only their abstracts, and not full text, represented in our search index. The results in Table 23 show that PaperFinder agent obtains very similar results to the agent of Skarlinski et al. (2024) despite having access to only abstracts for over half the papers, and scores significantly higher on the subsets where full text is available.

Table 23: Retrieval scores on full set of LitQA2 dataset

<table><tr><td>Name</td><td>original-set portion</td><td>full-text percentage</td><td>recall</td><td>recall @30</td></tr><tr><td>PaperQA2 (Skarlinski et al. (2024))</td><td>full (199)</td><td>100%</td><td>69.9</td><td>62.8</td></tr><tr><td>PaperFinder (ours)</td><td>full (199)</td><td>&lt;50%</td><td>70.3</td><td>64.3</td></tr><tr><td>PaperFinder (ours)</td><td>LitQA2-FullText-Search Test (75)</td><td>100%</td><td>93.3</td><td>90.7</td></tr><tr><td>PaperFinder (ours)</td><td>LitQA2-FullText-Search Val (10)</td><td>100%</td><td>80</td><td>80</td></tr></table>

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

Jonathan Bragg1 Mike D’Arcy1

Nishant Balepur2,∗ Dan Bareket1 Bhavana Dalvi1 Sergey Feldman1 Dany Haddad1 Jena D. Hwang1 Peter Jansen1,3 Varsha Kishore1,6 Bodhisattwa Prasad Majumder1 Aakanksha Naik1 Sigal Rahamimov1 Kyle Richardson1 Amanpreet Singh1 Harshit Surana1 Aryeh Tiktinsky1 Rosni Vasu4,∗ Guy Wiener1

Chloe Anastasiades1 Stefan Candra1 Jason Dunkelberger1 Dan Emery1 Rob Evans1 Malachi Hamada1 Regan Huff1 Rodney Kinney1 Matt Latzke1 Jaron Lochner1 Ruben Lozano-Aguilera1 Cecile Nguyen1 Smita Rao1 Amber Tanaka1 Brooke Vlahos1

Peter Clark1 Doug Downey1 Yoav Goldberg1,5 Ashish Sabharwal1 Daniel S. Weld1 1Asta Team, Allen Institute for AI, 2University of Maryland, 3University of Arizona, 4University of Zurich, 5Bar-Ilan University, 6University of Washington, ∗Work performed while at Ai2 Asta Team.

## 八、总结

In summary, we identify limitations of current approaches to benchmarking agents, and present methodology and tooling for doing so more rigorously. Using this methodology and tooling, we introduce AstaBench, a holistic benchmark suite for scientific research that addresses key limitations. AstaBench is the first major agent benchmark suite to come with standard environment and tools that enable controlled comparison of agents: the Asta Environment, the first scientific research environment for agents with realistic, controlled search tools. Alongside, we present the agentbaselines Agents Suite, a large suite of standardized agents, which we used to conduct experiments on AstaBench with 57 agents across 22 architectural classes. This revealed several interesting findings, most importantly that despite meaningful progress on certain individual aspects, agentic AI remains far from solving the challenge of scientific research assistance. We invite the community to make submissions to the AstaBench Leaderboard, which is powered by our agent-eval Agents Evaluation Toolkit.

This work opens up many exciting possibilities for the agentic AI, scientific research assistance, and automated scientific discovery communities. We are actively pushing the performance-cost frontiers in AstaBench and closing the gap for truly open agents by developing new agent techniques, tools, and open models specialized for scientific research. We are also enhancing agent abilities to manage complex context, from improving on Asta v0 simple orchestration techniques to handling long-duration tasks in complex research projects. We are continuing to research how to refine our LLM-as-a-judge grading procedures, especially for challenging scientific discovery tasks. We plan to develop fresh benchmark problems that use the latest scientific knowledge, which is contaminationresistant and past the training cut-off date of models. We also plan to build benchmarks that test more aspects of collaboration with humans, and deepen coverage of problems in impactful fields such as biomedicine. Finally, we are committed to continuing to measure the latest advances—both by testing the latest LLMs and by adding more agent architectures to agent-baselines.

## References

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal, Danqi Chen, and Tianyu Gao. LitSearch: A retrieval benchmark for scientific literature search. In EMNLP, 2024. URL https: //aclanthology.org/2024.emnlp-main.840/.

All-Hands-AI. OpenHands agent hub, 2025a. URL https://github.com/All-Hands-AI/ OpenHands/tree/55d204ae1b5581b0e55ebbd6465c7e2211b26765/openhand s/agenthub. Accessed: 2025-08-25.

All-Hands-AI. OpenHands evaluation leaderboard, 2025b. URL https://docs.google.co m/spreadsheets/d/1wOUdFCMyY6Nt0AIqF705KN4JKOWgeI4wUGUP60krXXs/ed it?gid=0#gid=0. Accessed: 2025-08-25.

ArcadiaImpact / UK Government BEIS Team. Inspect Evals Dashboard, 2025. URL https: //inspectevalsdashboard-vv8euilv46.streamlit.app/. Accessed: 2025-07- 08; site was down on 2025-08-25.

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi, Amanpreet Singh, Joseph Chee Chang, Kyle Lo, Luca Soldaini, Sergey Feldman, Mike D’Arcy, David Wadden, Matt Latzke, Minyang Tian, Pan Ji, Shengyan Liu, Hao Tong, Bohao Wu, Yanyu Xiong, Luke S. Zettlemoyer, Graham Neubig, Daniel S. Weld, Doug Downey, Wen tau Yih, Pang Wei Koh, and Hanna Hajishirzi. OpenScholar: Synthesizing scientific literature with retrieval-augmented LMs. ArXiv, abs/2411.14199, 2024. URL https://api.semanticscholar.org/CorpusID:274166189.

Ben Bogin, Kejuan Yang, Shashank Gupta, Kyle Richardson, Erin Bransom, Peter Clark, Ashish Sabharwal, and Tushar Khot. SUPER: Evaluating agents on setting up and executing tasks from research repositories. In EMNLP, 2024. URL https://aclanthology.org/2024.emnl p-main.702.

Jun Shern Chan, Neil Chowdhury, Oliver Jaffe, James Aung, Dane Sherburn, Evan Mays, Giulio Starace, Kevin Liu, Leon Maksin, Tejal Patwardhan, Lilian Weng, and Aleksander Mádry. MLEbench: Evaluating machine learning agents on machine learning engineering. In ICLR, 2025. URL https://openreview.net/forum?id=6s5uXNWGIh.

Hui Chen, Miao Xiong, Yujie Lu, Wei Han, Ailin Deng, Yufei He, Jiaying Wu, Yibo Li, Yue Liu, and Bryan Hooi. MLR-Bench: Evaluating AI agents on open-ended machine learning research. arXiv:2505.19955, 2025a. URL https://arxiv.org/abs/2505.19955.

Ziru Chen, Shijie Chen, Yuting Ning, Qianheng Zhang, Boshi Wang, Botao Yu, Yifei Li, Zeyi Liao, Chen Wei, Zitong Lu, Vishal Dey, Mingyi Xue, Frazier N. Baker, Benjamin Burns, Daniel Adu-Ampratwum, Xuhui Huang, Xia Ning, Song Gao, Yu Su, and Huan Sun. ScienceAgentBench: Toward rigorous assessment of language agents for data-driven scientific discovery. In ICLR, 2025b. URL https://openreview.net/forum?id=6z4YKr0GK6.

Junyan Cheng, Peter Clark, and Kyle Richardson. Language modeling by language models. arXiv:2506.20249, 2025. URL https://arxiv.org/abs/2506.20249.

Nick Craswell, Bhaskar Mitra, Emine Yilmaz, Daniel Fernando Campos, and E. Voorhees. Overview of the TREC 2020 deep learning track. ArXiv, abs/2102.07662, 2021. URL https://api.se manticscholar.org/CorpusId:212737158.

Jesse Dodge, Suchin Gururangan, Dallas Card, Roy Schwartz, and Noah A. Smith. Show your work: Improved reporting of experimental results. In EMNLP, 2019.

Adam Fourney, Gagan Bansal, Hussein Mozannar, Cheng Tan, Eduardo Salinas, Erkang Zhu, Friederike Niedtner, Grace Proebsting, Griffin Bassman, Jack Gerrits, Jacob Alber, Peter Chang, Ricky Loynd, Robert West, Victor Dibia, Ahmed Awadallah, Ece Kamar, Rafah Hosn, and Saleema Amershi. Magentic-One: A generalist multi-agent system for solving complex tasks. arXiv, abs/2411.04468, 2024. URL https://arxiv.org/abs/2411.04468.

Leo Gao, Jonathan Tow, Baber Abbasi, Stella Biderman, Sid Black, Anthony DiPofi, Charles Foster, Laurence Golding, Jeffrey Hsu, Alain Le Noac’h, Haonan Li, Kyle McDonell, Niklas Muennighoff, Chris Ociepa, Jason Phang, Laria Reynolds, Hailey Schoelkopf, Aviya Skowron, Lintang Sutawika, Eric Tang, Anish Thite, Ben Wang, Kevin Wang, and Andy Zou. The language model evaluation harness, 07 2024. URL https://zenodo.org/records/12608602.

Yuling Gu, Oyvind Tafjord, Bailey Kuehl, Dany Haddad, Jesse Dodge, an

### 在线资源

- [论文：arXiv 2510.21652](https://arxiv.org/abs/2510.21652)
- [代码：GitHub](https://github.com/UKGovernmentBEIS/inspect)
- [代码：GitHub](https://github.com/laude-institute/terminal-bench)
- [代码：GitHub](https://github.com/mlfoundations/evalchemy)
- [代码：GitHub](https://github.com/princeton-pli/hal-harness)
- [代码：GitHub](https://github.com/soheeyang/unified-prompt-selection)
- [PDF源文件](/papers/2510.21652.pdf)
