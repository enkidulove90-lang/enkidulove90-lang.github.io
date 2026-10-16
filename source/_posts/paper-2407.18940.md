---
title: "科学文献检索基准LitSearch"
date: 2024-07-01
year: 2024
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2407.18940
arxiv_id: "2407.18940"
description: "本文提出了LitSearch，一个针对科学文献检索的基准数据集，包含597个由人工精心筛选的文献搜索问题。"
---

> 论文：[arXiv 2407.18940](https://arxiv.org/abs/2407.18940) · PDF：[本地阅读](/papers/2407.18940.pdf)

本文提出了LitSearch，一个针对科学文献检索的基准数据集，包含597个由人工精心筛选的文献搜索问题。该基准通过两种方式构建：一是利用GPT-4将论文中的内联引文改写为搜索问题，二是邀请论文作者撰写关于自己论文的搜索问题。实验表明，现有最先进的稠密检索模型（如GritLM）在该基准上表现最佳，但仍有较大提升空间，而商业搜索引擎（如Google）表现不佳。LitSearch能有效区分不同检索模型的性能差异，为文献检索系统提供了更具挑战性和现实意义的测试平台。

## 研究问题

本文提出了LitSearch，一个针对科学文献检索的基准数据集，包含597个由人工精心筛选的文献搜索问题。该基准通过两种方式构建：一是利用GPT-4将论文中的内联引文改写为搜索问题，二是邀请论文作者撰写关于自己论文的搜索问题。实验表明，现有最先进的稠密检索模型（如GritLM）在该基准上表现最佳，但仍有较大提升空间，而商业搜索引擎（如Google）表现不佳。LitSearch能有效区分不同检索模型的性能差异，为文献检索系统提供了更具挑战性和现实意义的测试平台。

## 方法：核心思路与整体框架

LitSearch数据集构建分为两步：1）从S2ORC语料库中采样内联引文段落，使用GPT-4生成搜索问题，并通过词重叠过滤和人工审查确保质量；2）邀请ACL 2023和ICLR 2024论文作者撰写关于自己论文的搜索问题，同样经过人工审查。检索实验采用BM25、GTR、Instructor、E5、GritLM等模型，并利用GPT-4o进行重排序，评估指标为Recall@K。

![图 1：Table 11: Instructions provided in the Google Forms sent to ICLR 2024 and ACL 2023 authors for collecting author-written questions.](/images/papers/2407.18940/6a9b4e2dd78ed82386156fd69a06fb71ba28c55632785eed5371975ea70612ee.jpg)

*图 1 · 原图说明：Table 11: Instructions provided in the Google Forms sent to ICLR 2024 and ACL 2023 authors for collecting author-written questions.*

**图示解释：** LitSearch数据集构建分为两步：1）从S2ORC语料库中采样内联引文段落，使用GPT-4生成搜索问题，并通过词重叠过滤和人工审查确保质量；2）邀请ACL 2023和ICLR 2024论文作者撰写关于自己论文的搜索问题，同样经过人工审查。

![图 2：Table 12: The prompt used for generating questions from inline citations using GPT-4.](/images/papers/2407.18940/e9dc2916bb1ed66249edb37069548bf1b0cb50448a276bcafaee1af4f50dfa00.jpg)

*图 2 · 原图说明：Table 12: The prompt used for generating questions from inline citations using GPT-4.*

**图示解释：** LitSearch数据集构建分为两步：1）从S2ORC语料库中采样内联引文段落，使用GPT-4生成搜索问题，并通过词重叠过滤和人工审查确保质量；2）邀请ACL 2023和ICLR 2024论文作者撰写关于自己论文的搜索问题，同样经过人工审查。

![图 3：Table 13: The prompt used for reranking retrieved documents using GPT-4o (adapted from Sun et al., 2023a).](/images/papers/2407.18940/60751a977115124344076c20fe36b9a96a18cafbcead4c03a7afc541ac3721f1.jpg)

*图 3 · 原图说明：Table 13: The prompt used for reranking retrieved documents using GPT-4o (adapted from Sun et al., 2023a).*

**图示解释：** LitSearch数据集构建分为两步：1）从S2ORC语料库中采样内联引文段落，使用GPT-4生成搜索问题，并通过词重叠过滤和人工审查确保质量；2）邀请ACL 2023和ICLR 2024论文作者撰写关于自己论文的搜索问题，同样经过人工审查。

## 创新点

1. 创新点1：首次提出基于真实研究场景的文献搜索问题基准LitSearch，包含内联引文生成和作者撰写两种问题来源，更贴近实际研究需求。
2. 创新点2：构建了高质量的数据集，所有问题均经过人工审查和过滤，并标注了问题的具体性和质量等级，确保基准的挑战性和可靠性。
3. 创新点3：引入基于LLM的重排序策略（包括vanilla reranking和one-hop reranking），并系统分析了不同检索模型、重排序方法及问题特性（如来源、质量、具体性）对性能的影响。

## 实验：数据、基线与结果

### 数据集与设置

- LitSearch（包含内联引文问题和作者撰写问题两个子集）
- MS-MARCO
- SCIDOCS
- Natural Questions (NQ)
- ArXiv（Gu et al., 2022）

### Benchmark 与结果

在LitSearch上，最佳稠密检索模型GritLM-7B在具体问题上Recall@5达到74.8%，比BM25（50.0%）高出24.8个百分点。使用GPT-4o进行vanilla reranking后，GritLM的Recall@5进一步提升4.4%至79.2%。相比之下，Google Search在具体问题上的Recall@5仅为42.8%。此外，LitSearch能更好地区分不同嵌入模型的性能，例如GritLM与E5在LitSearch具体子集上的nDCG@10差距达15点，而在MS-MARCO上两者几乎持平。



### 消融实验

论文未报告独立的消融实验。

## 总结

本文提出了LitSearch，一个针对科学文献检索的基准数据集，包含597个由人工精心筛选的文献搜索问题。

## References

- LitSearch: A Retrieval Benchmark for Scientific Literature Search：[arXiv 2407.18940](https://arxiv.org/abs/2407.18940)

- [PDF源文件](/papers/2407.18940.pdf)
