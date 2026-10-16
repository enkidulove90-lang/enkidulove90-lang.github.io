---
title: "HySemRAG"
date: 2025-08-01
year: 2025
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2508.05666
arxiv_id: "2508.05666"
---

## 一、简介

We present HySemRAG, a framework that combines Extract, Transform, Load (ETL) pipelines with Retrieval-Augmented Generation (RAG) to automate large-scale literature synthesis and identify methodological research gaps. The system addresses limitations in existing RAG architectures through a multi-layered approach: hybrid retrieval combining semantic search, keyword filtering, and knowledge graph traversal; an agentic self-correction framework with iterative quality assurance; and post-hoc citation verification ensuring complete traceability. Our implementation processes scholarly literature through eight integrated stages: multi-source metadata acquisition, asynchronous PDF retrieval, custom document layout analysis using modified Docling architecture, bibliographic management, LLM-based field extraction, topic modeling, semantic unification, and knowledge graph construction. The system creates dual data products - a Neo4j knowledge graph enabling complex relationship queries and Qdrant vector collections supporting semantic search - serving as foundational infrastructure for verifiable information synthesis. Evaluation across 643 observations from 60 testing sessions demonstrates structured field extraction achieving 35.1% higher semantic similarity scores $( 0 . 6 5 5 \pm 0 . 1 7 8 )$ compared to PDF chunking approaches (0.485 ± 0.204, p < 0.000001). The agentic quality assurance mechanism achieves 68.3% single-pass success rates with 99.0% citation accuracy in validated responses. Applied to geospatial epidemiology literature on ozone exposure and cardiovascular disease, the system identifies methodological trends and research gaps, demonstrating broad applicability across scientific domains for accelerating evidence synthesis and discovery.

Keywords Literature Synthesis • Retrieval-Augmented Generation • Knowledge Graphs • Natural Language Processing • Qwen3 • Large Language Models • Extract Transform Load

## 二、论文方法

A PREPRINT

Alejandro Godinez Department of Environmental Health Sciences University at Albany, State University of New York Albany, 12222

Bandit Environmental Solutions LLC Albany agodinez@albany.edu

2025-07-31

## 三、论文里的图与解释

### 图 1

![Figure 1: Graphical Abstract](/images/papers/2508.05666/a83b0cf30eeb22b1aa40c2d832e85b27134f9e8fc256ce3c7e10d7b437f480ad.jpg)

**原图说明：** Figure 1: Graphical Abstract

**图示解释：** 该图对应论文中的“Figure 1: Graphical Abstract”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Figure 8: Table Missclassification](/images/papers/2508.05666/34d9aec98286aed2e08b78d00c5c636d6150c3597006792484c6983475aac122.jpg)

**原图说明：** Figure 8: Table Missclassification

**图示解释：** 该图对应论文中的“Figure 8: Table Missclassification”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Figure 9: Table Correction](/images/papers/2508.05666/672b928d8c3e0f47a3afde6977cfe35c4bc996c19d7159e1a0f6b194c4380570.jpg)

**原图说明：** Figure 9: Table Correction

**图示解释：** 该图对应论文中的“Figure 9: Table Correction”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 4

![Figure 10: Query example](/images/papers/2508.05666/ed78fbae966e452d9df19cfdc5e77fe8f2bb4080d91145231f9d85d52295d1ad.jpg)

**原图说明：** Figure 10: Query example

**图示解释：** 该图对应论文中的“Figure 10: Query example”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

The semantic unification pipeline represents a contribution, using sentence transformers with cosine similarity and threshold-based mapping to resolve terminological ambiguity with broad applicability. The agentic self-correction framework addresses RAG limitations, though modest improvement from iterative refinement suggests the approach needs refinement.

Custom Docling modifications demonstrate practical solutions to real-world PDF processing challenges, particularly for scholarly documents with complex layouts. The hybrid retrieval approach combining semantic search, keyword filtering, and knowledge graph traversal provides comprehensive coverage addressing individual method limitations.

## 五、实验数据集选择

- PubMed
- OpenAlex
- Scopus
- Unpaywall API

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

We evaluated HySemRAG using 643 observations across 60 testing sessions conducted during system development. While this represents controlled developer testing rather than independent evaluation, it provides insight into system capabilities and limitations.

Retrieval Performance: Structured field extraction achieved higher semantic similarity scores $( 0 . 6 5 5 \pm 0 . 1 7 8 , \mathtt { n } { = } 1 6 5 )$ compared to PDF text chunking (0.485 ± 0.204, n=263). Mann-Whitney U testing confirmed this 35.1% performance difference as statistically significant $\mathrm { ( p < 0 . 0 0 0 0 0 0 1 ) }$

Evidence Quality Distribution: Classification revealed 100 observations (24.5%) as high quality (≥ 70% similarity), 258 observations (63.2%) as medium quality (30-69% similarity), and 50 observations (12.3%) as low quality (<30% similarity).

Quality Assurance Mechanisms: The agentic self-correction system demonstrated 68.3% single-pass success rate, requiring average 2.33 iterations per query. Quality-controlled analysis of 394 verified observations (61.3% acceptance rate) showed citation accuracy of 99.0% ± 4.5% and semantic similarity scores of $1 . 0 0 0 \pm 0 . 0 0 0$

## 八、总结

We present HySemRAG, a framework addressing limitations in automated literature synthesis through integrated ETL processing and multi-agent RAG capabilities. The system demonstrates improvements in retrieval accuracy and citation verification while enabling systematic identification of methodological gaps across research domains.

Key contributions include: (1) hybrid retrieval strategies combining multiple search modalities with Reciprocal Rank Fusion, (2) document layout analysis modifications addressing scholarly PDF processing challenges, (3) semantic unification resolving terminological heterogeneity, (4) multi-agent quality assurance with iterative refinement, and (5) comprehensive citation verification ensuring complete provenance tracking.

Evaluation reveals structured field extraction achieving 35.1% higher semantic similarity compared to PDF chunking approaches, with the system identifying methodological trends in geospatial epidemiology literature. While temporal instability and session heterogeneity indicate areas for improvement, the framework provides a foundation for accelerating evidence synthesis and research discovery.

Future work should address system stability through independent user studies, cross-domain evaluation, and longitudinal performance assessment under real-world conditions. The modular architecture enables extensions to diverse scientific domains, potentially transforming how researchers discover and synthesize evidence across disciplinary boundaries.

## References

Scott Barnett, Stefanus Kurniawan, Srikanth Thudumu, Zach Brannelly, and Mohamed Abdelrazek. Seven Failure Points When Engineering a Retrieval Augmented Generation System. In Proceedings of the IEEE/ACM 3rd International Conference on AI Engineering - Software Engineering for AI, pages 194–199, Lisbon Portugal, April 2024. ACM. ISBN 979-8-4007-0591-5. doi: 10.1145/3644815.3644945.

Stefan Dernbach, Khushbu Agarwal, Alejandro Zuniga, Michael Henry, and Sutanay Choudhury. GLaM: Fine-Tuning Large Language Models for Domain Knowledge Graph Alignment via Neighborhood Partitioning and Generative Subgraph Encoding. Proceedings of the AAAI Symposium Series, 3(1):82–89, May 2024. doi: 10.1609/aaaiss.v3i1. 31186.

Antonio Di Maria, Lorenzo Bellomo, Fabrizio Billeci, Alfio Cardillo, Salvatore Alaimo, Paolo Ferragina, Alfredo Ferro, and Alfredo Pulvirenti. NetMe 2.0: a web-based platform for extracting and modeling knowledge from biomedical literature as a labeled graph. Bioinformatics, 40(5), April 2024. doi: 10.1093/bioinformatics/btae194.

Nurshat Fateh Ali, Md. Mahdi Mohtasim, Shakil Mosharrof, and T. Gopi Krishna. Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation. 2022 International Conference on Innovations in Science, Engineering and Technology (ICISET), pages 1–6, October 2024. doi: 10.1109/iciset62123.2024.10939517.

Zhangyin Feng, Xiaocheng Feng, Dezhi Zhao, Maojin Yang, and Bing Qin. Retrieval-Generation Synergy Augmented Large Language Models. ICASSP 2022 - 2022 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), pages 11661–11665, March 2024. doi: 10.1109/icassp48485.2024.10448015.

Rachael Fleurence, Jiang Bian, Xiaoyan Wang, Hua Xu, Dalia Dawoud, Mitch Higashi, and Jagpreet Chhatwal. Generative AI for Health Technology Assessment: Opportunities, Challenges, and Policy Considerations - an ISPOR Working Group Report. Value in Health, November 2024. doi: 10.1016/j.jval.2024.10.3846.

Bowen Gu, Rishi Desai, Kueiyu Joshua Lin, and Jie Yang. Probabilistic medical predictions of large language models. npj Digital Medicine, 7(1), December 2024. doi: 10.1038/s41746-024-01366-4.

Celeste Ci Ying Gue, Noorul Dharajath Abdul Rahim, William Rojas-Carabali, Rupesh Agrawal, Palvannan Rk, John Abisheganaden, and Wan Fen Yip. Evaluating the OpenAI’s GPT-3.5 Turbo’s performance in extracting information from scientific articles on diabetic retinopathy. Systematic reviews, 13(1):135, May 2024. doi: 10.1186/s13643-024- 02523-2.

Lei Huang, Weijiang Yu, Weitao Ma, Weihong Zhong, Zhangyin Feng, Haotian Wang, Qianglong Chen, Weihua Peng, Xiaocheng Feng, Bing Qin, and Ting Liu. A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions. ACM transactions on office information systems, November 2024. doi: 10.1145/3703155.

F. J. Bolaños, Angelo A. Salatino, Francesco Osborne, and Enrico Motta. Artificial intelligence for literature reviews: opportunities and challenges. Artificial Intelligence Review, 57(10), August 2024. doi: 10.1007/s10462-024-10902-3.

Kory Kreimeyer, Jenna VanLiere Canzoniero, Maria Fatteh, Valsamo Anagnostou, and Taxiarchis Botsis. Using Retrieval-Augmented Generation to Capture Molecularly-Driven Treatment Relationships for Precision Oncology. Studies in health technology and informatics, August 2024. doi: 10.3233/shti240575.

Po-hao Li and Ya-yun Lai. Augmenting Large Language Models with Reverse Proxy Style Retrieval Augmented Generation for Higher Factual Accuracy, May 2024.

Piyush Ranjan Maharana, Ashwini Verma, and Kavita Joshi. Retrieval augmented generation for building datasets from scientific literature, March 2025.

Hsiao-Ching Tsai, Yueh-Fen Huang, and Chih-Wei Kuo. Comparative Analysis of Automatic Literature Review Using Mistral Large Language Model and Human Reviewers. Research Square (Research Square), March 2024. doi: 10.21203/rs.3.rs-4022248/v1.

Rishabh Upadhyay and Marco Viviani. Enhancin

### 在线资源

- [论文：arXiv 2508.05666](https://arxiv.org/abs/2508.05666)
- [PDF源文件](/papers/2508.05666.pdf)
