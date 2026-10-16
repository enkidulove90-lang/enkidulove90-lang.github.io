---
title: "Efficient Retrieval Scaling with Hierarchical Indexing for Large-Scale Recommendation"
date: 2026-04-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2604.12965
arxiv_id: "2604.12965"
---

## 一、简介

The increase in data volume, computational resources, and model parameters during training has led to the development of numerous large-scale industrial retrieval models for recommendation tasks. However, efectively and eficiently deploying these largescale foundational retrieval models remains a critical challenge that has not been fully addressed. Common quick-win solutions for deploying these massive models include relying on ofline computations (such as cached user dictionaries) or distilling large models into smaller ones. Yet, both approaches fall short of fully leveraging the representational and inference capabilities of foundational models. In this paper, we explore whether it is possible to learn a hierarchical organization over the memory of foundational retrieval models. Such a hierarchical structure would enable more eficient search by reducing retrieval costs while preserving exactness. To achieve this, we propose jointly learning a hierarchical index using cross-attention and residual quantization for large-scale retrieval models. We also present its real-world deployment at Meta, supporting daily advertisement recommendations for billions of Facebook and Instagram users. Interestingly, we discovered that the intermediate nodes in the learned index correspond to a small set of high-quality data. Fine-tuning the model on this set further improves inference performance, and concretize the concept of "test-time training" within the recommendation system domain. We demonstrate these findings using both internal and public datasets with strong baseline comparisons and hope they contribute to the community’s eforts in developing the next generation of foundational retrieval models.

## 二、论文方法

HILL方法首先利用交叉注意力机制学习单层映射，将物品嵌入软分配到索引节点；然后通过残差量化逐层堆叠，将低层残差传递到高层，形成层次结构。训练过程中采用温度调度、平衡正则化和预热策略优化。此外，还提供了基于EM算法和FAISS的近似版本，以降低计算资源需求。

## 三、论文里的图与解释

### 图 1

![Overall Pipeline of MoNN Foundation Retrieval Model with HILL Index.](/images/papers/2604.12965/figure_001_framework.png)

**原图说明：** Overall Pipeline of MoNN Foundation Retrieval Model with HILL Index.

**图示解释：** 该图对应论文中的“Overall Pipeline of MoNN Foundation Retrieval Model with HILL Index.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![A MoNN Block](/images/papers/2604.12965/figure_002_MoNN.png)

**原图说明：** A MoNN Block

**图示解释：** 该图对应论文中的“A MoNN Block”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![A Hierarchical Index Example Learnt by HILL.](/images/papers/2604.12965/figure_003_HILL.png)

**原图说明：** A Hierarchical Index Example Learnt by HILL.

**图示解释：** 该图对应论文中的“A Hierarchical Index Example Learnt by HILL.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 创新点1：提出HILL分层索引学习方法，利用交叉注意力机制和残差量化，在基础检索模型之上构建层次化索引树，实现从粗到细的近似搜索，大幅降低推理成本。
2. 创新点2：发现索引树的中间层节点可生成高质量的用户-索引节点数据对，用于测试时训练（Test-Time Training），在不依赖真实标签的情况下微调模型，进一步提升检索性能。
3. 创新点3：设计了软硬分配过渡的温度调度器、平衡索引分布的FLOPs正则化器以及预热策略等训练技巧，确保索引学习的稳定性和有效性。

## 五、实验数据集选择

Here, we choose both public benchmark datasets and internal datasets to demonstrate the performance. For the public datasets, we select Gowalla, Yelp 2018, and Amazon-Book, as shown in Table 2, which records various user-item interactions and are publicly available2. The internal datasets are from daily Ads Recommendation tasks from Meta Platform.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

Here, the performance will be demonstrated in two aspects, $\mathrm { i . e . }$ internal test, public benchmark, and ablation study to verify the important components.

Internal Test. The efectiveness and eficiency analysis of MoNN with baselines are shown in Table 1, where all MoNN models are equipped with joint optimization of HILL and show significant performance, $\mathrm { e . g . , } > 0 . 0 5 \%$ NE Gain is significant [19].

To be specific, in Table 1, by scaling up the model size, we can observe that MoNN Large performs the best, in terms of NE and Recall metrics. However, it brings considerable infrastructure cost. Therefore, we propose to stack MoNN blocks and make the lower level take the majority (but not all) of the data during the training . As shown in the last three rows of Table 1, which largely reduces the infrastructure cost and keeps the competitive efectiveness. In addition to theoretical eficiency analysis, we present the cost of serving the MoNN model based on the following parameters: $\mathbf { I } _ { 1 }$ (number of nodes in $\mathrm { L } _ { 1 }$ layer), $\mathbf { I } _ { 2 }$ (number of nodes in $\mathrm { L } _ { 2 }$ layer) and V (number of items in the corpus), $\mathbf { M } _ { X S }$ denotes the cost to serve Two Tower model, $\mathbf { M } _ { S }$ denotes the cost to serve MoNN Small, ${ \bf { M } } _ { M }$ the cost to serve MoNN Medium, $\mathbf { M } _ { L }$ the cost to serve MoNN Large.

Ablation Studies. After showing that HILL can serve the large retrieval model efectively and eficiently, we then execute ablation studies to verify our theoretical design.

First, we design three training tricks during HILL optimizations, i.e., Softmax Temperature Scheduler, Balanced Index Distribution, Warmup Strategy. In Table 4, we observe that (1) the full version of including all training tricks has the best performance; (2) removing each one can reduce the performance, and they do not conflict with each other; (3) the Softmax Temperature Scheduler has the most significant loss when it is removed.

Second, in Table 5, we show that the EM version of HILL can also achieve a competitive performance, given the NE loss is less than 0.04%, which also suggests that the full version of HILL has a fair reason to be considered when the computing resource allows

Table 3: Comparison of Baselines across Gowalla, Yelp2018, and Amazon-Book.

<table><tr><td rowspan="2">Baseline</td><td colspan="2">Gowalla</td><td colspan="2">Yelp 2018</td><td colspan="2">Amazon-Book</td></tr><tr><td>Recall@20</td><td>NDCG@20</td><td>Recall@20</td><td>NDCG@20</td><td>Recall@20</td><td>NDCG@20</td></tr><tr><td>BPR [43]</td><td>0.1627</td><td>0.1378</td><td>0.0576</td><td>0.0468</td><td>0.0338</td><td>0.0261</td></tr><tr><td>GRMF [42]</td><td>0.1477</td><td>0.1205</td><td>0.0571</td><td>0.0462</td><td>0.0354</td><td>0.0270</td></tr><tr><td>GRMF-norm [42]</td><td>0.1557</td><td>0.1261</td><td>0.0561</td><td>0.0454</td><td>0.0352</td><td>0.0269</td></tr><tr><td>HOP-Rec [56]</td><td>0.1399</td><td>0.1214</td><td>0.0517</td><td>0.0428</td><td>0.0309</td><td>0.0232</td></tr><tr><td>ENMF [4]</td><td>0.1523</td><td>0.1315</td><td>0.0624</td><td>0.0515</td><td>0.0359</td><td>0.0281</td></tr><tr><td>MF-CCL [39]</td><td>0.1837</td><td>0.1493</td><td>0.0698</td><td>0.0572</td><td>0.0559</td><td>0.0447</td></tr><tr><td>SimpleX [39]</td><td>0.1872</td><td>0.1557</td><td>0.0701</td><td>0.0575</td><td>0.0583</td><td>0.0468</td></tr><tr><td>NeuMF [52]</td><td>0.1399</td><td>0.1212</td><td>0.0451</td><td>0.0363</td><td>0.0258</td><td>0.0200</td></tr><tr><td>Mult-VAE [32]</td><td>0.1641</td><td>0.1335</td><td>0.0584</td><td>0.0450</td><td>0.0407</td><td>0.0315</td></tr><tr><td>Macrid-VAE [38]</td><td>0.1618</td><td>0.1202</td><td>0.0612</td><td>0.0495</td><td>0.0383</td><td>0.0295</td></tr><tr><td>YouTubeNet [7]</td><td>0.1754</td><td>0.1473</td><td>0.0686</td><td>0.0567</td><td>0.0502</td><td>0.0388</td></tr><tr><td>CMN [9]</td><td>0.1405</td><td>0.1221</td><td>0.0475</td><td>0.0369</td><td>0.0267</td><td>0.0218</td></tr><tr><td>CML [21]</td><td>0.1670</td><td>0.1292</td><td>0.0622</td><td>0.0536</td><td>0.0522</td><td>0.0428</td></tr><tr><td>DeepWalk [41]</td><td>0.1034</td><td>0.0740</td><td>0.0476</td><td>0.0378</td><td>0.0346</td><td>0.0264</td></tr><tr><td>LINE [49]</td><td>0.1335</td><td>0.1056</td><td>0.0549</td><td>0.0446</td><td>0.0410</td><td>0.0318</td></tr><tr><td>Node2Vec [14]</td><td>0.1019</td><td>0.0709</td><td>0.0452</td><td>0.0350</td><td>0.0402</td><td>0.0309</td></tr><tr><td>Item2Vec [2]</td><td>0.1325</td><td>0.1057</td><td>0.0503</td><td>0.0411</td><td>0.0326</td><td>0.0251</td></tr><tr><td>GAT [51]</td><td>0.1401</td><td>0.1401</td><td>0.0543</td><td>0.0431</td><td>0.0326</td><td>0.0235</td></tr><tr><td>JKNet [55]</td><td>0.1622</td><td>0.1391</td><td>0.0608</td><td>0.0502</td><td>0.0268</td><td>0.0343</td></tr><tr><td>DropEdge [44]</td><td>0.1627</td><td>0.1394</td><td>0.0614</td><td>0.0506</td><td>0.0342</td><td>0.0270</td></tr><tr><td>APPNP [26]</td><td>0.1708</td><td>0.1462</td><td>0.0635</td><td>0.0521</td><td>0.0384</td><td>0.0299</td></tr><tr><td>DisenGCN [37]</td><td>0.1356</td><td>0.1174</td><td>0.0558</td><td>0.0454</td><td>0.0329</td><td>0.0254</td></tr><tr><td>LightGCN [18]</td><td>0.1830</td><td>0.1554</td><td>0.0649</td><td>0.0530</td><td>0.0411</td><td>0.0315</td></tr><tr><td>GC-MC [50]</td><td>0.1395</td><td>0.1204</td><td>0.0462</td><td>0.0379</td><td>0.0288</td><td>0.0224</td></tr><tr><td>PinSage [57]</td><td>0.1380</td><td>0.1196</td><td>0.0471</td><td>0.0393</td><td>0.0282</td><td>0.0219</td></tr><tr><td>NIA-GCN [46]</td><td>0.1359</td><td>0.1106</td><td>0.0599</td><td>0.0491</td><td>0.0369</td><td>0.0287</td></tr><tr><td>SGL-ED [54]</td><td>0.1835</td><td>0.1539</td><td>0.0675</td><td>0.0555</td><td>0.0478</td><td>0.0379</td></tr><tr><td>DeosGCF [35]</td><td>0.1784</td><td>0.1477</td><td>0.0626</td><td>0.0504</td><td>0.0410</td><td>0.0316</td></tr><tr><td>IMP-GCN [34]</td><td>0.1845</td><td>0.1567</td><td>0.0653</td><td>0.0531</td><td>0.0460</td><td>0.0357</td></tr><tr><td>BUIR [28]</td><td>0.1575</td><td>0.1301</td><td>0.0647</td><td>0.0526</td><td>0.0439</td><td>0.0346</td></tr><tr><td>DGCF [53]</td><td>0.1842</td><td>0.1561</td><td>0.0654</td><td>0.0534</td><td>0.0422</td><td>0.0324</td></tr><tr><td>IA-GCN [66]</td><td>0.1839</td><td>0.1562</td><td>0.0659</td><td>0.0537</td><td>0.0472</td><td>0.0373</td></tr><tr><td>LT-OCF [6]</td><td>0.1875</td><td>0.1574</td><td>0.0671</td><td>0.0549</td><td>0.0442</td><td>0.0341</td></tr><tr><td>HMLET [27]</td><td>0.1874</td><td>0.1589</td><td>0.0675</td><td>0.0557</td><td>0.0482</td><td>0.0371</td></tr><tr><td>GTN [10]</td><td>0.1870</td><td>0.1588</td><td>0.0679</td><td>0.0554</td><td>0.0450</td><td>0.0346</td></tr><tr><td>MGDCF [22]</td><td>0.1864</td><td>0.1589</td><td>0.0696</td><td>0.0572</td><td>0.0490</td><td>0.0378</td></tr><tr><td>BSPM-LM [5]</td><td>0.1901</td><td>0.1570</td><td>0.0713</td><td>0.0584</td><td>0.0733</td><td>0.0610</td></tr><tr><td>NESCL [47]</td><td>0.1908</td><td>0.1614</td><td>0.0740</td><td>0.0609</td><td>0.0623</td><td>0.0509</td></tr><tr><td>HILL (Ours)</td><td>0.1924</td><td>0.1628</td><td>0.0745</td><td>0.0612</td><td>0.0625</td><td>0.0513</td></tr></table>

Table 4: Ablation Study of Training HILL, MoNN Small as Backbone, on Gowalla Dataset.

<table><tr><td>Training Variant</td><td>NE (↓)</td></tr><tr><td>w/o Softmax Temperature Scheduler</td><td>+0.10%</td></tr><tr><td>w/o Balanced Index Distribution</td><td>+0.05%</td></tr><tr><td>w/o Warmup Strategy</td><td>+0.03%</td></tr></table>

Table 5: Ablation Study of HILL Approximation, 2-Layer MoNN as Backbone, on Gowalla Dataset.

<table><tr><td>Model Architecture</td><td>NE (↓)</td></tr><tr><td>HILL</td><td>-0.15%</td></tr><tr><td>HILL (EM)</td><td>-0.11%</td></tr></table>

Public Benchmark. In addition to the internal datasets, we also conduct the experiments on the public dataset to show the efectiveness of HILL by choosing NESCL [47] as the retrieval model and learning the corresponding hierarchical index. To be specific, we first use the EM version of HILL to learn the hierarchical index; then, we extract the <user, index node> data pairs in the index to fine-tune the retrieval model, and finally report the performance in Table 3. For example, in the Gowalla dataset, the outperformance is obtained by setting ???????? = 2, ??ℎ?????? = 0.8 at the second layer, and ??ℎ?????? = 0.4 at the third layer.

Parameter Analysis. Then, a natural question arises: whether including more new data pairs can further improve the performance? To answer this question, we prepare the parameter analysis in Tables 6 and 7, which shows that the small amount but precise test-time data is suficient for the leading performance.

Table 6: Performance with diferent ??DEP.

<table><tr><td> $\phi_{\text{DEP}}$ </td><td># Nodes per Inter-layer</td><td> $\phi_{\text{IR}}$ </td><td>Recall@20</td><td>NDCG@20</td></tr><tr><td>1</td><td>8000</td><td>0.8</td><td>0.1922</td><td>0.1624</td></tr><tr><td>2</td><td>8000, 800</td><td>0.8, 0.4</td><td>0.1924</td><td>0.1628</td></tr><tr><td>3</td><td>8000, 800, 80</td><td>0.8, 0.4, 0.2</td><td>0.1922</td><td>0.1624</td></tr><tr><td>4</td><td>8000, 8000, 80, 8</td><td>0.8, 0.4, 0.2, 0.1</td><td>0.1916</td><td>0.1623</td></tr></table>

Table 7: Performance with diferent $\phi _ { \mathbf { I R } }$ .

<table><tr><td> $\phi_{\text{DEP}}$ </td><td># Nodes per Inter-layer</td><td> $\phi_{\text{IR}}$ </td><td>Recall@20</td><td>NDCG@20</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.1</td><td>0.1916</td><td>0.1624</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.2</td><td>0.1923</td><td>0.1629</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.3</td><td>0.1914</td><td>0.1624</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.4</td><td>0.1924</td><td>0.1628</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.5</td><td>0.1914</td><td>0.1623</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.6</td><td>0.1924</td><td>0.1620</td></tr><tr><td>1</td><td>8000, 800</td><td>0.8, 0.7</td><td>0.1925</td><td>0.1623</td></tr></table>

## 八、总结

To make the large-scale foundation retrieval model serve efectively and eficiently, in this paper, we propose the hierarchical index learning method HILL to learn the index structure over the memory of the foundation model, taking MoNN (i.e., a deployed retrieval model at Meta for Ads Retrieval) for illustration. Moreover, we found that learnt index convey a small set of new and high-quality data pairs that can be used to test-time fine-tune the model to boost the performance.

## References

[1] Newsha Ardalani, Carole-Jean Wu, Zeliang Chen, Bhargav Bhushanam, and Adnan Aziz 2022, Understanding Scaling Laws for Recommendation Models CoRR abs/2208 08489 (2022),doi:10 48550/ARXIV 2208 08489 arXiv:2208 08489

[2] Oren Barkan and Noam Koenigstein. 2016. ITEM2VEC: Neural item embedding for collaborative filtering. In 26th IEEE International Workshop on Machine Learning for Signal Processing, MLSP 2016, Vietri sul Mare, Salerno, Italy, September 13-16, 2016, Francesco A. N. Palmieri, Aurelio Uncini, Kostas I. Diamantaras, and Jan Larsen (Eds.). IEEE, 1–6. doi:10.1109/MLSP.2016.7738886

[3] Jane Bromley, Isabelle Guyon, Yann LeCun, Eduard Säckinger, and Roopak Shah. 1993. Signature Verification Using a Siamese Time Delay Neural Network. In Advances in Neural Information Processing Systems 6, [7th NIPS Conference, Denver, Colorado, USA, 1993], Jack D. Cowan, Gerald Tesauro, and Joshua Alspector (Eds.). Morgan Kaufmann, 737–744. http://papers.nips.cc/paper/769- signature-verification-using-a-siamese-time-delay-neural-network

[4] Chong Chen, Min Zhang, Yongfeng Zhang, Yiqun Liu, and Shaoping Ma. 2020. Eficient Neural Matrix Factorization without Sampling for Recommendation. ACM Trans. Inf. Syst. 38, 2 (2020), 14:1–14:28. doi:10.1145/3373807

[5] Jeongwhan Choi, Seoyoung Hong, Noseong Park, and Sung-Bae Cho. 2023. Blurring-Sharpening Process Models for Collaborative Filtering. In Proceedings of the 46th International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR 2023, Taipei, Taiwan, July 23-27, 2023, Hsin-Hsi Chen, Wei-Jou (Edward) Duh, Hen-Hsen Huang, Makoto P. Kato, Josiane Mothe, and Barbara Poblete (Eds.). ACM, 1096–1106. doi:10.1145/3539618. 3591645

[6] Jeongwhan Choi, Jinsung Jeon, and Noseong Park. 2021. LT-OCF: Learnable-Time ODE-based Collaborative Filtering. In CIKM ’21: The 30th ACM International Conference on Information and Knowledge Management, Virtual Event, Queensland, Australia, November 1 - 5, 2021, Gianluca Demartini, Guido Zuccon, J. Shane Culpepper, Zi Huang, and Hanghang Tong (Eds.). ACM, 251–260. doi:10.1145/3459637.3482449

[7] Paul Covington, Jay Adams, and Emre Sargin. 2016. Deep Neural Networks for YouTube Recommendations. In Proceedings of the 10th ACM Conference on Recommender Systems, Boston, MA, USA, September 15-19, 2016, Shilad Sen, Werner Geyer, Jill Freyne, and Pablo Castells (Eds.). ACM, 191–198. doi:10 1145/2959100.2959190

[8] Matthijs Douze, Alexandr Guzhva, Chengqi Deng, Jef Johnson, Gergely Szilvasy, Pierre-Emmanuel Mazaré, Maria Lomeli, Lucas Hosseini, and Hervé Jégou. 2024. The Faiss library. CoRR abs/2401.08281 (2024). doi:10.48550/ ARXIV.2401.08281 arXiv:2401.08281

[9] Travis Ebesu, Bin Shen, and Yi Fang. 2018. Collaborative Memory Network for Recommendation Systems. In The 41st International ACM SIGIR Conference on Research & Development in Information Retrieval, SIGIR 2018, Ann Arbor, MI, USA, July 08-12, 2018, Kevyn Collins-Thompson, Qiaozhu Mei, Brian D Davison, Yiqun Liu, and Emine Yilmaz (Eds.). ACM, 515–524. doi:10.1145/ 3209978.3209991

[10] Wenqi Fan, Xiaorui Liu, Wei Jin, Xiangyu Zhao, Jiliang Tang, and Qing Li. 2022. Graph Trend Filtering Networks for Recommendation. In SIGIR ’22: The 45th International ACM SIGIR Conference on Research and Development in Information Retrieval, Madrid, Spain, July 11 - 15, 2022, Enrique Amigó, Pablo Castells, Julio Gonzalo, Ben Carterette, J. Shane Culpepper, and Gabriella Kazai (Eds.). ACM, 112–121. doi:10.1145/3477495.3531985

[11] Yan Fang, Jingtao Zhan, Qingyao Ai, Jiaxin Mao, Weihang Su, Jia Chen, and Yiqun Liu. 2024. Scaling Laws For Dense Retrieval. In Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR 2024, Washington DC, USA, July 14-18, 2024, Grace Hui Yang, Hongning Wang, Sam Han, Claudia Hauf, Guido Zuccon, and Yi Zhang (Eds.). ACM, 1339–1349. doi:10.1145/3626772.3657743

[12] Chao Feng, Wuchao Li, Defu Lian, Zheng Liu, 

### 在线资源

- [论文：arXiv 2604.12965](https://arxiv.org/abs/2604.12965)
- [PDF源文件](/papers/2604.12965.pdf)
