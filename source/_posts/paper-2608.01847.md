---
title: "FOCUS: FP4 Optimization via Coupled-Relaxation and Dual-Granularity Scaling"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.01847
arxiv_id: "2608.01847"
---

## 一、简介

Large language models (LLMs) achieve remarkable performance but are expensive to deploy due to their enormous size. FP4 quantization, with formats such as MXFP4 and NVFP4, ofers an appealing solution with native hardware support on modern accelerators. However, maintaining accuracy under FP4 precision remains dificult. A key bottleneck lies in scale optimization: existing methods tightly couple the quantization and dequantization scales, forcing both to conform to the discrete low-precision format required by hardware (e.g., E8M0 in MXFP4). Yet the quantization scale is never stored and need not obey this constraint, suggesting a significant untapped optimization space. In this work, we propose FOCUS, a post-training quantization framework with end-to-end scale learning for FP4 Optimization via Coupled-Relaxation and Dual-Granularity Scaling. Coupled-Relaxation Scaling (CRS) relaxes the tight coupling between quantization and dequantization scales with a learnable full-precision coeficient, enabling more efective optimization without breaking hardware compliance. Dual-Granularity Scaling (DGS) further refines the quantization scale at a finer sub-block granularity, allowing more precise adaptation to local weight distributions. Experiments across multiple LLM families and benchmarks show that FOCUS achieves state-of-the-art FP4 accuracy under both MXFP4 and NVFP4 formats, while introducing no additional inference overhead. We will release the code and quantized models of FOCUS at https://github.com/tencent/AngelSlim.

## 二、论文方法

In this section, we present FOCUS as illustrated in Figure 3. We begin with FP4 preliminaries, then introduce a scalelearning baseline and the key insight behind FOCUS. We next present two core components, CRS and DGS, which relax the precision and granularity constraints on quantization scales. Finally, we discuss deployment considerations without transformation-based overhead.

## 三、论文里的图与解释

### 图 1

![Figure 3: Overview of FOCUS. (a) End-to-end Scale Learning Baseline: learns FP8 scales via STE while weights are frozen during quantization and dequantization. (b) Coupled-Relaxation Scaling (CRS): introduces learnable relaxation coeficients for additional flexibility beyond FP8 precision. (c) Dual-Granularity Scaling (DGS): partitions each block into sub-blocks with independent coeficients for fine-grained scale adjustment. (d) Output Model: only FP4 weights and dequantization scales are stored, while quantization scales are discarded.](/images/papers/2608.01847/966cd100a2b1895042d0fed27684915935663075fb7de8a7e338c07b767500ac.jpg)

**原图说明：** Figure 3: Overview of FOCUS. (a) End-to-end Scale Learning Baseline: learns FP8 scales via STE while weights are frozen during quantization and dequantization. (b) Coupled-Relaxation Scaling (CRS): introduces learnable relaxation coeficients for additional flexibility beyond FP8 precision. (c) Dual-Granularity Scaling (DGS): partitions each block into sub-blocks with independent coeficients for fine-grained scale adjustment. (d) Output Model: only FP4 weights and dequantization scales are stored, while quantization scales are discarded.

**图示解释：** 该图对应论文中的“Figure 3: Overview of FOCUS. (a) End-to-end Scale Learning Baseline: learns FP8 scales via STE while weights are frozen during quantization and dequantization. (b) Coupled-Relaxation Scaling (CRS): introduces learnable relaxation coeficients for additional flexibility beyond FP8 precision. (c) Dual-Granularity Scaling (DGS): partitions each block into sub-blocks with independent coeficients for fine-grained scale adjustment. (d) Output Model: only FP4 weights and dequantization scales are stored, while quantization scales are discarded.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 关键洞察：量化尺度在推理时不被存储，因此不受硬件精度格式和块粒度约束，而现有方法将量化尺度与反量化尺度紧耦合，浪费了这一优化自由度。
2. 耦合松弛缩放（CRS）：引入可学习的全精度系数c_i，以乘法形式松弛量化尺度与反量化尺度的紧耦合，将优化从离散低精度空间提升到连续全精度空间，同时保持训练稳定性。
3. 双粒度缩放（DGS）：将每个硬件块（MXFP4为32元素，NVFP4为16元素）划分为子块（大小为8），每个子块分配独立的可学习系数，使量化尺度以比反量化尺度更细的粒度适应块内权重变化。
4. 无推理开销且框架兼容：FOCUS仅学习尺度参数，不修改权重，不依赖Hadamard变换等在线计算，部署模型保持标准MXFP4/NVFP4格式，与主流推理框架无缝兼容。

## 五、实验数据集选择

- WikiText2
- C4
- ARC-Challenge
- ARC-Easy
- HellaSwag
- PIQA
- Winogrande
- GSM8K
- MMLU

## 六、消融实验

Efect ofCRS and DGS. Table 4 presents an ablation study on Qwen3-4B, progressively adding each proposed component. Starting from RTN, the naive scale learning baseline already yields substantial gains, particularly under MXFP4 where Wiki2 perplexity drops from 18.60 to 12.96, confirming the value of end-to-end scale optimization. Adding CRS further improves zero-shot accuracy by up to 1.0% under NVFP4, validating that relaxing the coupling between quantization and dequantization scales enables better FP4 assignments. Incorporating DGS provides further gains under both formats, showing that sub-block granularity refines FP4 assignments beyond block-level relaxation alone. The full method achieves the best results in all settings, improving zero-shot average by 1.13% and 0.96% over the baseline under NVFP4 and MXFP4, respectively.

Efect of sub-block size in DGS. Table 5 investigates the impact of sub-block granularity in DGS. When the subblock size equals the native block size (32 for MXFP4, 16 for NVFP4), DGS reduces to CRS, as each block shares a single relaxation coeficient. Decreasing the sub-block size introduces finer-grained coeficients, enabling more precise control over rounding boundaries at the cost of additiona trainable parameters during calibration. For MXFP4, reducing the sub-block size from 32 to 16 yields a notable improvement (e.g., Avg.: 64.81 → 65.65), while further reduction to 8 achieves comparable performance. For NVFP4, sub-block sizes 8 and 4 perform similarly, so we use size 8 for both formats to balance accuracy and cost.

<table><tr><td>Format</td><td>Sub-block Size</td><td>Wiki2↓</td><td>C4↓</td><td>Avg.↑</td></tr><tr><td rowspan="4">NVFP4</td><td>16 (CRS)</td><td>12.61</td><td>16.96</td><td>66.91</td></tr><tr><td>8</td><td>12.57</td><td>16.97</td><td>67.05</td></tr><tr><td>4</td><td>12.57</td><td>16.91</td><td>67.05</td></tr><tr><td>2</td><td>12.62</td><td>16.92</td><td>66.94</td></tr><tr><td rowspan="4">MXFP4</td><td>32 (CRS)</td><td>12.99</td><td>17.95</td><td>64.81</td></tr><tr><td>16</td><td>12.98</td><td>17.79</td><td>65.65</td></tr><tr><td>8</td><td>12.85</td><td>17.77</td><td>65.65</td></tr><tr><td>4</td><td>12.83</td><td>17.78</td><td>64.94</td></tr></table>

Table 5: Efect of sub-block size in DGS. Evaluated on Qwen3-4B. Setting sub-block size to the native block size reduces DGS to CRS. Best results are in bold.

## 七、Benchmark 结果与解释

Language Modeling (Perplexity). As shown in Tables 1 and 2, FOCUS achieves the lowest perplexity in nearly all settings across five models. Notably, on Qwen3-8B, FOCUS attains 9.76 (MXFP4) and 9.47 (NVFP4) on WikiText2, nearly matching the FP16 baseline of 9.73. The gains are particularly significant under MXFP4, where FOCUS reduces perplexity by 1.5–2.5 points over MR-GPTQ on Qwen models, demonstrating the efectiveness of scale optimization under more restrictive quantization constraints. Under NVFP4, FOCUS remains best or competitive, outperforming format-specific methods such as RaZeR and 4over6 by clear margins.

<table><tr><td>Model</td><td>Method</td><td>GSM8K-CoT</td><td>MMLU-CoT</td></tr><tr><td rowspan="5">LLaMA-3.23B-Instruct</td><td>FP16</td><td>77.86</td><td>64.57</td></tr><tr><td>RTN</td><td>55.42</td><td>53.96</td></tr><tr><td>GPTQ</td><td>51.10</td><td>51.60</td></tr><tr><td>MR-GPTQ</td><td>60.20</td><td>55.16</td></tr><tr><td>FOCUS</td><td>64.14</td><td>59.09</td></tr><tr><td rowspan="5">LLaMA-3.18B-Instruct</td><td>FP16</td><td>85.67</td><td>72.71</td></tr><tr><td>RTN</td><td>59.29</td><td>57.90</td></tr><tr><td>GPTQ</td><td>63.84</td><td>61.81</td></tr><tr><td>MR-GPTQ</td><td>72.40</td><td>63.39</td></tr><tr><td>FOCUS</td><td>73.31</td><td>65.53</td></tr></table>

Table 3: Chain-of-thought reasoning results on GSM8K and MMLU under MXFP4 format. Best results (excluding FP16) are in bold.

Zero-Shot Tasks. We further evaluate on five zero-shot benchmarks and report the average accuracy in Tables 1 and 2. FOCUS consistently achieves the highest average across nearly all model-format combinations. On Qwen3-4B, FOCUS obtains 67.05% (NVFP4) and 65.65% (MXFP4), recovering 98.2% and 96.2% of the FP16 accuracy (68.25%), respectively. On Qwen3-8B NVFP4, FOCUS reaches 71.37%, recovering 99.8% of FP16 (71.54%), while the best competing method RaZeR achieves only 70.54%. Under MXFP4, FOCUS outperforms MR-GPTQ by 1.0% in average accuracy.

<table><tr><td>Format</td><td>Method</td><td>Wiki2↓</td><td>C4↓</td><td>Avg.↑</td></tr><tr><td rowspan="4">NVFP4</td><td>RTN</td><td>13.88</td><td>17.29</td><td>65.58</td></tr><tr><td>Baseline</td><td>12.63</td><td>17.02</td><td>65.92</td></tr><tr><td>+ CRS</td><td>12.61</td><td>16.98</td><td>66.91</td></tr><tr><td>+ CRS + DGS</td><td>12.57</td><td>16.97</td><td>67.05</td></tr><tr><td rowspan="4">MXFP4</td><td>RTN</td><td>18.60</td><td>20.62</td><td>62.35</td></tr><tr><td>Baseline</td><td>12.96</td><td>17.98</td><td>64.69</td></tr><tr><td>+ CRS</td><td>12.99</td><td>17.95</td><td>64.81</td></tr><tr><td>+ CRS + DGS</td><td>12.85</td><td>17.77</td><td>65.65</td></tr></table>

Table 4: Efect of CRS and DGS. Each proposed component is progressively added to the naive scale learning baseline on Qwen3-4B. Best results are in bold.

Reasoning Tasks. Table 3 reports chain-of-thought evaluation results on GSM8K and MMLU under MXFP4. We observe that FP4 quantization incurs more pronounced degradation on reasoning tasks compared to perplexity and zero-shot benchmarks, indicating that multi-step reasoning is particularly sensitive to quantization noise. Nevertheless, FOCUS consistently preserves reasoning capability better than all competing methods. On LLaMA-3.1-8B-Instruct, FOCUS achieves 73.31% on GSM8K and 65.53% on MMLU, outperforming MR-GPTQ by 0.9 and 2.1 points, respectively. On LLaMA-3.2-3B-Instruct, FOCUS leads with 64.14% (GSM8K) and 59.09% (MMLU), surpassing MR-GPTQ by approximately 4 points on both benchmarks. These results show that FOCUS improves both token-level prediction and multi-step reasoning.

## 八、总结

We present FOCUS, a post-training quantization framework that rethinks scale optimization for FP4 formats. Building on the observation that the quantization scale is free from hardware constraints, we construct an eficient end-toend scale learning framework that exploits this overlooked freedom along two complementary dimensions. Coupled-Relaxation Scaling (CRS) lifts scale optimization from a discrete hardware-constrained space to a continuous one by introducing a learnable coeficient that relaxes the coupling between the quantization and dequantization scales. Dual-Granularity Scaling (DGS) further extends this idea to the sub-block level, enabling the relaxed scale to adapt to local weight variations within each block. Together, these techniques enable FOCUS to find superior FP4 assignments during calibration, while the deployed model remains in standard MXFP4/NVFP4 format with no additional inference cost. Experiments confirm that FOCUS achieves state-of-the-art FP4 accuracy under both formats, substantially closing the gap to full-precision performance.

## References

Ashkboos, S.; Mohtashami, A.; Croci, M. L.; Li, B.; Cameron, P.; Jaggi, M.; Alistarh, D.; Hoefler, T.; and Hensman, J. 2024. Quarot: Outlier-free 4-bit inference in rotated llms. In NeurIPS.

Bao, C.; Yan, X.; Li, Z.; Qin, G.; Yu, G.; and Zhang, Y. 2026. SOAR: Scale Optimization for Accurate Reconstruction in NVFP4 Quantization. arXiv preprint arXiv:2605.12245.

Bengio, Y.; Léonard, N.; and Courville, A. 2013. Estimating or propagating gradients through stochastic neurons for conditional computation. arXiv preprint arXiv:1308.3432.

Bisk, Y.; Zellers, R.; Gao, J.; Choi, Y.; et al. 2020. Piqa: Reasoning about physical commonsense in natural language. In AAAI.

Chen, M.; Wu, M.; Jin, H.; Yuan, Z.; Liu, J.; Zhang, C.; Li, Y.; Huang, J.; Ma, J.; Xue, Z.; et al. 2025. INT vs FP: A Comprehensive Study of Fine-Grained Low-bit Quantization Formats. arXiv preprint arXiv:2510.25602.

Chen, Y.; Dai, X.; Hyun, J.; Chang, C.-C.; Jang, W.; Wu, Y.; Tambe, T.; sun Seo, J.; and Abdelfattah, M. S. 2026. RaZeR: Pushing the Limits of NVFP4 Quantization with Redundant Zero Remapping. arXiv preprint arXiv:2501.04052v2.

Chhugani, J.; Jeong, G.; Su, B.-Y.; Pan, Y.; Yang, H.; Ankit, A.; Yu, J.; Deng, S.; Chen, Y.; Satish, N.; and Kim, C. 2026. Unveiling the Potential of Quantization with MXFP4: Strategies for Quantization Error Reduction. In ICML.

Clark, P.; Cowhey, I.; Etzioni, O.; Khot, T.; Sabharwal, A.; Schoenick, C.; and Tafjord, O. 2018. Think you have solved question answering? try arc, the ai2 reasoning challenge. arXiv preprint arXiv:1803.05457.

Cobbe, K.; Kosaraju, V.; Bavarian, M.; Chen, M.; Jun, H.; Kaiser, L.; Plappert, M.; Tworek, J.; Hilton, J.; Nakano, R.; et al. 2021. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168.

Cook, J.; Guo, J.; Xiao, G.; Lin, Y.; and Han, S. 2025. Four Over Six: More Accurate NVFP4 Quantization with Adaptive Block Scaling. arXiv preprint arXiv:2512.02010.

Dettmers, T.; Lewis, M.; Belkada, Y.; and Zettlemoyer, L. 2022. GPT3.int8(): 8-bit Matrix Multiplication for Transformers at Scale. In NeurIPS.

Dubey, A.; Jauhri, A.; Pandey, A.; Kadian, A.; Al-Dahle, A.; Letman, A.; Mathur, A.; Schelten, A.; Yang, A.; Fan, A.; et al. 2024. The llama 3 herd of models. arXiv preprint arXiv:2407.21783.

Egiazarian, V.; Castro, R. L.; Kuznedelev, D.; Panferov, A.; Kurtic, E.; Pandit, S.; Marques, A. N.; Kurtz, M.; Ashkboos, S.; Hoefler, T.; and Alistarh, D. 2026. Bridging the Gap Between Promise and Performance for Microscaling FP4 Quantization. In ICLR.

Frantar, E.; Ashkboos, S.; Hoefler, T.; and Alistarh, D. 2023. GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers. In ICLR.

Guo, D.; Yang, D.; Zhang, H.; Song, J.; Zhang, R.; Xu, R.; Zhu, Q.; Ma, S.; Wang, P.; Bi, X.; et al. 2025. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2501.12948.

Hendrycks, D.; Burns, C.; Basart, S.; Zou, A.; Mazeika, M.; Song, D.; and Steinhardt, J. 2021. Measuring massive multitask language understanding. In ICLR.

Hu, X.; Cheng, Y.; Yang, D.; Chen, Z.; Xu, Z.; Yu, J.; Chen, X.; Yuan, Z.; Jiang, Z.; and Zhou, S. 2025. OSTQuant: Refining Large Language Model Quantization with Orthogonal and Scaling Transformations for Better Distribution Fitting. In ICLR.

Li, H.; Tian, S.; Lin, C.; Zhao, Z.; and Zhan, K. 2026a. FAAR: Format-Aware Adaptive Rounding for NVFP4. arXiv preprint arXiv:2603.22370.

Li, J.-F.; Zhang, M.; Xia, X.; Bao, H.; Bai, H.; Dong, Z.; and Yu, X. 2026b. BATQuant: Outlier-resilient MXFP4 Quantization via Learnable Block-wise Optimization. arXiv preprint arXiv:2603.16590.

Li, Y.; Gong, R.; Tan, X.; Yang, Y.; Hu, P.; Zhang, Q.; Yu, F.; Wang, W.; and Gu, S. 2021. BRECQ: Pushing the Limit of Post-Training Quantization by Block Reconstruction. In ICLR.

Li, Z.; Yan, X.; Zhang, T.; Qin, H.; Xie, D.; Tian, J.; Kong, L.; Zhang, Y.; Yang, X.; et al. 2025. Arb-llm: Alternating refined binarizations for large language mod

### 在线资源

- [论文：arXiv 2608.01847](https://arxiv.org/abs/2608.01847)
- [代码：GitHub](https://github.com/tencent/AngelSlim)
- [PDF源文件](/papers/2608.01847.pdf)
