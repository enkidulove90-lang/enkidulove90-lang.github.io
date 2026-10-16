---
title: "MemOCR: Layout-Aware Visual Memory for Efficient Long-Horizon Reasoning"
date: 2026-01-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2601.21468
arxiv_id: "2601.21468"
---

## 一、简介

Long-horizon agentic reasoning necessitates effectively compressing growing interaction histories into a limited context window. Most existing memory systems serialize history as text, where token-level cost is uniform and scales linearly with length, often spending scarce budget on low-value details. To this end, we introduce MemOCR, a multimodal memory agent that improves long-horizon reasoning under tight context budgets by allocating memory space with adaptive information density through visual layout. Concretely, MemOCR maintains a structured rich-text memory (e.g., headings, highlights) and renders it into an image that the agent consults for memory access, visually prioritizing crucial evidence while aggressively compressing auxiliary details. To ensure robustness across varying memory budgets, we train MemOCR with reinforcement learning under budget-aware objectives that expose the agent to diverse compression levels. Across long-context multi-hop and single-hop question-answering benchmarks, MemOCR out performs strong text-based baselines and achieves more effective context utilization under extreme budgets. Our code is available at https:// github.com/meituan/MemOCR.

## 二、论文方法

In this section, we introduce MemOCR, a multimodal memory agent that improves long-horizon reasoning under tight context budgets by allocating memory space with adaptive information density through visual layout. As shown in Figure 2, MemOCR formulates and utilizes visual memory with a two-stage lifecycle: memory drafting in the text domain (§3.1), followed by memory reading in the vision domain (§3.2) after rendering. Finally, we present our budget-aware training objectives that train the agent to remain effective under different memory budgets (§3.3).

## 三、论文里的图与解释

### 图 1

![Figure 7. Case study at an extreme memory budget (16 tokens). (Left) The textual baseline fails due to hard truncation of the context. (Middle) MemOCR without layout control fails because uniform text becomes unreadable after down-sampling. (Right) MemOCR preserves the crucial evidence “Gene MacLellan” through adaptive layout, enabling correct reasoning even at low resolution.](/images/papers/2601.21468/8ded92beebf30e4c851ff408a0e4e69922a0cba01fb8b0b5c34ee0ad13d08b4a.jpg)

**原图说明：** Figure 7. Case study at an extreme memory budget (16 tokens). (Left) The textual baseline fails due to hard truncation of the context. (Middle) MemOCR without layout control fails because uniform text becomes unreadable after down-sampling. (Right) MemOCR preserves the crucial evidence “Gene MacLellan” through adaptive layout, enabling correct reasoning even at low resolution.

**图示解释：** 该图对应论文中的“Figure 7. Case study at an extreme memory budget (16 tokens). (Left) The textual baseline fails due to hard truncation of the context. (Middle) MemOCR without layout control fails because uniform text becomes unreadable after down-sampling. (Right) MemOCR preserves the crucial evidence “Gene MacLellan” through adaptive layout, enabling correct reasoning even at low resolution.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Figure 8. Failure Mode Analysis under Resource Constraints (16-token budget). (Top) In comparative reasoning (i.e., to choose among two candidates), while the layout successfully highlights entity headers, the body text containing crucial attributes is compressed into unreadable noise during downsampling. (Bottom) When the rich-text memory length exceeds the visual canvas capacity, the forced font scaling drops below the visual encoder’s resolution threshold, resulting in information loss.](/images/papers/2601.21468/1b434ef24e833e7fbb912a55d8efdf1100c56a17b852f0b3ddae450c8dbff5e8.jpg)

**原图说明：** Figure 8. Failure Mode Analysis under Resource Constraints (16-token budget). (Top) In comparative reasoning (i.e., to choose among two candidates), while the layout successfully highlights entity headers, the body text containing crucial attributes is compressed into unreadable noise during downsampling. (Bottom) When the rich-text memory length exceeds the visual canvas capacity, the forced font scaling drops below the visual encoder’s resolution threshold, resulting in information loss.

**图示解释：** 该图对应论文中的“Figure 8. Failure Mode Analysis under Resource Constraints (16-token budget). (Top) In comparative reasoning (i.e., to choose among two candidates), while the layout successfully highlights entity headers, the body text containing crucial attributes is compressed into unreadable noise during downsampling. (Bottom) When the rich-text memory length exceeds the visual canvas capacity, the forced font scaling drops below the visual encoder’s resolution threshold, resulting in information loss.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. 提出从一维文本记忆到二维视觉记忆的范式转变，将历史表示为图像而非 token 流，通过视觉显著性（标题、加粗、字号）实现非均匀预算分配，解耦信息密度与 token 成本。
2. 设计两阶段记忆生命周期：文本域的记忆草稿（增量维护富文本记忆并分配视觉优先级）和视觉域的记忆阅读（轻量渲染器将富文本编译为 2D 图像，作为唯一工作上下文），并通过分辨率调整灵活控制预算。
3. 提出预算感知的强化学习训练目标，构建标准 QA、增强记忆 QA（4× 下采样）和增强问题 QA 三种互补任务，防止智能体采用均匀中等字号的捷径策略，迫使关键证据在极端压缩下仍保持可见。

## 五、实验数据集选择

Datasets. We train on HotpotQA (Yang et al., 2018) and pad each sample with distractor documents to reach ∼30K tokens during training. We evaluate on multi-hop HotpotQA and 2WikiMultiHopQA (2Wiki) (Ho et al., 2020), as well as single-hop Natural Questions (NQ) (Kwiatkowski et al., 2019) and TriviaQA (Joshi et al., 2017). During evaluation, contexts are padded to 10K/30K/100K tokens. We report subword exact match as accuracy, averaged over three runs.

Baselines. We compare MemOCR against two categories of baselines: (1) Raw History Memory with uncompressed context, including the standard Qwen2.5-Instruct (Yang et al., 2024), the Qwen model distilled from DeepSeek-R1 (R1-Distill Qwen) (DeepSeek-AI et al., 2025) and Qwen2.5- 1M-Instruct (Yang et al., 2025); (2) Textual Summary Memory, represented by Mem0 (Chhikara et al., 2025), Mem-α (Wang et al., 2025) and MemAgent (Yu et al., 2025). We use Qwen2.5-7B-Instruct (Yang et al., 2024) as the default backbone LLM for text-based methods, and Qwen2.5- VL-7B-Instruct (Bai et al., 2025) for MemOCR.

Memory Budget. We study long-context QA with an explicit memory budget constraint $B \in \{ 1 6 , 6 4 , 2 5 6 , 1 0 2 4 \}$ where the “memory budget” controls the number of tokens occupied in the context window at answer time. For textual summary agents, we constrain summary length by only keeping the first B tokens in the latest memory state $| M _ { T } |$ For MemOCR, we adjust the resolution of the rendered memory image so that the number of visual patch tokens is no greater than B. Additional details are in Appendix C.

## 六、消融实验

We ablate MemOCR by progressively removing training objectives. Specifically, we compare vanilla MemOCR trained with full objectives $( \overline { { J _ { \mathrm { s t d } } } } { + } \overline { { J _ { \mathrm { a u g M } } } } { + } \overline { { J _ { \mathrm { a u g Q } } } } )$ with three variants: (1) w/o $\tau _ { \mathrm { a u g M } } \left( 2 \right)$ w/o $\mathcal { T } _ { \mathrm { a u g M } } , \mathcal { T } _ { \mathrm { a u g Q } }$ , and (3) w/o $\mathcal { T } _ { \mathrm { s t d } } , \mathcal { T } _ { \mathrm { a u g M } } .$ $ { \mathcal { T } } _ { \mathrm { a u g Q } }$ . Results are reported in Table 4.

![](images/8ded92beebf30e4c851ff408a0e4e69922a0cba01fb8b0b5c34ee0ad13d08b4a.jpg)  
Figure 7. Case study at an extreme memory budget (16 tokens). (Left) The textual baseline fails due to hard truncation of the context. (Middle) MemOCR without layout control fails because uniform text becomes unreadable after down-sampling. (Right) MemOCR preserves the crucial evidence “Gene MacLellan” through adaptive layout, enabling correct reasoning even at low resolution.

Obs. 4.1: Training is necessary for budget-robust memory layout. Across datasets and context lengths, simply removing all the training signals underperforms substantially. This indicates that the desired layout arrangement behavior does not emerge reliably without explicit training.

Obs. 4.2: Robustness gains accumulate with multiple training signals. Using $\mathcal { T } _ { \mathrm { s t d } }$ alone yields the weakest trained variant, which reflects limited ability to prioritize question-relevant evidence through layout control. Adding $ { \mathcal { T } } _ { \mathrm { a u g Q } }$ improves low-budget robustness, suggesting that the diverse queries strengthen evidence utilization. Further adding $ { \mathcal { T } } _ { \mathrm { a u g M } }$ brings a larger boost in the low-budget regime, consistent with the concept of learning more effective layout control and memory budget allocation.

## 七、Benchmark 结果与解释

We compare MemOCR with baselines across datasets, context lengths (10K/30K/100K), and budgets, to test whether MemOCR improves overall performance and remains robust as the budget tightens. Table 1 reports the main results.

Obs. 1.1: MemOCR achieves the best overall performance across different context lengths. MemOCR attains the highest average accuracy from 10K to 100K contexts, indicating that MemOCR scales to long histories. For example, at 10K context with full budget, MemOCR reaches 74.6% average accuracy, surpassing the strongest baseline at 67.8%. Statistical significance is provided in Appendix D.1. We also observe poor performance on HotpotQA under 30K and 100K context lengths, and our analysis on bad cases helps explain this phenomenon in Appendix E.

Table 1. Comparison of accuracy (%) across different context lengths (10K, 30K, and 100K tokens). Best results are highlighted in bold and second best in underline. The percentages in the Average column represent the performance drop relative to the 1024-token budget.

<table><tr><td rowspan="2">Method</td><td rowspan="2">Memory Budget (Tokens)</td><td colspan="3">HotpotQA</td><td colspan="3">2Wiki</td><td colspan="3">NQ</td><td colspan="3">TriviaQA</td><td colspan="3">Average</td></tr><tr><td>10K</td><td>30K</td><td>100K</td><td>10K</td><td>30K</td><td>100K</td><td>10K</td><td>30K</td><td>100K</td><td>10K</td><td>30K</td><td>100K</td><td>10K</td><td>30K</td><td>100K</td></tr><tr><td colspan="17">Raw History Memory</td></tr><tr><td>Qwen2.5</td><td>100K</td><td>70.3</td><td>-</td><td>-</td><td>53.9</td><td>61.1</td><td>-</td><td>50.8</td><td>-</td><td>-</td><td>71.1</td><td>-</td><td>-</td><td>61.5</td><td>-</td><td>-</td></tr><tr><td>R1-Distill Qwen</td><td>100K</td><td>50.8</td><td>12.5</td><td>0.8</td><td>50.8</td><td>26.6</td><td>2.3</td><td>35.2</td><td>3.9</td><td>1.6</td><td>54.7</td><td>11.7</td><td>0.8</td><td>47.9</td><td>13.7</td><td>1.4</td></tr><tr><td>Qwen2.5-1M</td><td>100K</td><td>75.0</td><td>66.4</td><td>68.8</td><td>67.2</td><td>65.6</td><td>54.7</td><td>53.1</td><td>43.8</td><td>50.8</td><td>71.1</td><td>77.3</td><td>59.4</td><td>66.6</td><td>63.3</td><td>58.4</td></tr><tr><td colspan="17">Textual Summary Memory</td></tr><tr><td rowspan="4">Mem0</td><td>1024</td><td>70.3</td><td>66.1</td><td>64.1</td><td>60.4</td><td>47.7</td><td>40.9</td><td>47.7</td><td>48.8</td><td>48.2</td><td>69.5</td><td>70.6</td><td>61.4</td><td>62.0</td><td>58.3</td><td>53.6</td></tr><tr><td>256</td><td>71.1</td><td>65.6</td><td>63.8</td><td>57.8</td><td>44.8</td><td>43.5</td><td>46.9</td><td>51.1</td><td>49.7</td><td>69.5</td><td>70.6</td><td>62.8</td><td>61.3 (-1.1%)</td><td>58.0 (-0.5%)</td><td>55.0 (+2.5%)</td></tr><tr><td>64</td><td>56.7</td><td>60.9</td><td>56.2</td><td>53.9</td><td>42.2</td><td>43.3</td><td>46.9</td><td>43.8</td><td>50.0</td><td>66.4</td><td>65.9</td><td>62.5</td><td>56.0 (-9.7%)</td><td>53.2 (-8.8%)</td><td>53.0 (-1.2%)</td></tr><tr><td>16</td><td>37.0</td><td>43.3</td><td>34.9</td><td>28.4</td><td>31.5</td><td>27.6</td><td>41.4</td><td>34.1</td><td>43.0</td><td>65.3</td><td>62.8</td><td>58.9</td><td>43.0 (-30.6%)</td><td>42.9 (-26.4%)</td><td>41.1 (-23.4%)</td></tr><tr><td rowspan="4">Mem-α</td><td>1024</td><td>75.0</td><td>77.9</td><td>79.4</td><td>47.7</td><td>40.1</td><td>50.0</td><td>45.6</td><td>44.8</td><td>43.0</td><td>21.1</td><td>23.2</td><td>19.3</td><td>47.3</td><td>46.5</td><td>47.9</td></tr><tr><td>256</td><td>57.8</td><td>57.3</td><td>57.0</td><td>38.3</td><td>32.8</td><td>41.7</td><td>47.9</td><td>33.6</td><td>38.0</td><td>17.2</td><td>24.2</td><td>18.3</td><td>40.3 (-14.9%)</td><td>37.0 (-20.5%)</td><td>38.7 (-19.2%)</td></tr><tr><td>64</td><td>25.8</td><td>29.7</td><td>28.9</td><td>34.9</td><td>31.5</td><td>39.1</td><td>27.1</td><td>25.0</td><td>24.0</td><td>13.0</td><td>19.5</td><td>13.8</td><td>25.2 (-46.8%)</td><td>26.4 (-43.2%)</td><td>26.4 (-44.9%)</td></tr><tr><td>16</td><td>24.0</td><td>30.2</td><td>26.3</td><td>35.4</td><td>32.3</td><td>40.1</td><td>23.7</td><td>26.3</td><td>24.2</td><td>11.7</td><td>19.0</td><td>14.3</td><td>23.7 (-50.0%)</td><td>27.0 (-42.0%)</td><td>26.2 (-45.3%)</td></tr><tr><td rowspan="4">MemAgent</td><td>1024</td><td>82.3</td><td>78.9</td><td>79.4</td><td>65.4</td><td>63.8</td><td>61.2</td><td>53.4</td><td>46.1</td><td>55.5</td><td>70.1</td><td>78.1</td><td>66.7</td><td>67.8</td><td>66.7</td><td>65.7</td></tr><tr><td>256</td><td>82.3</td><td>76.8</td><td>76.6</td><td>66.1</td><td>62.5</td><td>58.1</td><td>51.3</td><td>44.3</td><td>53.6</td><td>69.5</td><td>77.6</td><td>67.2</td><td>67.3 (-0.7%)</td><td>65.3 (-2.1%)</td><td>63.9 (-2.8%)</td></tr><tr><td>64</td><td>50.8</td><td>52.3</td><td>51.0</td><td>38.5</td><td>42.7</td><td>36.2</td><td>48.7</td><td>36.5</td><td>47.9</td><td>64.6</td><td>69.5</td><td>59.6</td><td>50.7 (-25.3%)</td><td>50.3 (-24.7%)</td><td>48.7 (-25.9%)</td></tr><tr><td>16</td><td>24.0</td><td>26.6</td><td>23.2</td><td>28.4</td><td>26.3</td><td>16.7</td><td>24.5</td><td>20.1</td><td>27.3</td><td>49.7</td><td>56.3</td><td>41.7</td><td>31.6 (-53.3%)</td><td>32.3 (-51.6%)</td><td>27.2 (-58.6%)</td></tr><tr><td colspan="17">Visual Memory</td></tr><tr><td rowspan="4">MemOCR (Ours)</td><td>1024</td><td>84.8</td><td>75.1</td><td>78.3</td><td>72.2</td><td>73.7</td><td>62.7</td><td>61.8</td><td>49.2</td><td>55.4</td><td>79.6</td><td>81.3</td><td>69.8</td><td>74.6</td><td>69.8</td><td>66.6</td></tr><tr><td>256</td><td>82.2</td><td>75.4</td><td>75.7</td><td>71.2</td><td>72.8</td><td>65.5</td><td>57.3</td><td>48.8</td><td>58.3</td><td>79.7</td><td>80.9</td><td>68.9</td><td>72.6 (-2.7%)</td><td>69.5 (-0.5%)</td><td>67.1 (+0.8%)</td></tr><tr><td>64</td><td>77.6</td><td>68.1</td><td>67.2</td><td>62.9</td><td>66.2</td><td>62.4</td><td>51.0</td><td>43.6</td><td>47.5</td><td>77.6</td><td>80.7</td><td>70.2</td><td>67.3 (-9.8%)</td><td>64.7 (-7.4%)</td><td>60.7 (-8.8%)</td></tr><tr><td>16</td><td>67.2</td><td>57.9</td><td>52.4</td><td>57.9</td><td>56.0</td><td>45.7</td><td>42.8</td><td>35.9</td><td>45.9</td><td>80.8</td><td>72.2</td><td>67.2</td><td>62.2 (-16.6%)</td><td>55.5 (-20.5%)</td><td>52.8 (-20.7%)</td></tr></table>

Obs. 1.2: MemOCR degrades more gracefully under tight budgets. Textual summary methods suffer catastrophic degradation as the budget tightens. For instance, on 10K contexts, MemAgent drops from 67.8% (1024 tokens) to 31.6% (16 tokens) on average. In contrast, MemOCR preserves 62.2% average accuracy at 16 tokens, corresponding to only a 16.6% relative drop. These results suggest that MemOCR retains task-relevant evidence more effectively under severe budget constraints.

Obs. 1.3: On single-hop tasks, low memory budget can be sufficient for sparse evidence. On NQ and TriviaQA, tightening the budget does not necessarily reduce accuracy. For example, on TriviaQA (10K context), MemOCR achieves 80.8% at 16 tokens, even higher than 79.6% at 1024 tokens. We attribute this to single-hop questions relying on atomic evidence, where a lower-resolution memory can still preserve the critical cues while filtering background noise. This phenomenon is not observed for textual baselines, whose performance decreases with smaller budgets.

Comparison against RAG-based Memory. We further compare MemOCR against recent RAG-based memory methods (Fang et al., 2025; Liu et al., 2026; Zhao et al., 2026) that maintain unlimited external storage and retrieve relevant passages at inference time. Table 2 reports results under 10K and 30K contexts.

Obs. 1.4: MemOCR consistently outperforms RAGbased memory methods that operate with unlimited storage budgets. At 10K context, MemOCR with B =

1024 achieves 74.6% average accuracy, surpassing the best unlimited-budget baseline HyMem (56.4%) by 18.2 points. Even under an aggressive 64-token budget, MemOCR obtains 67.3% and exceeds all unlimited baselines by a wide margin. The gap persists at 30K context where MemOCR with B = 256 reaches 69.5% versus 59.0% for the strongest competitor. These results demonstrate that learned memory compression with adaptive information density is more effective than retrieving from large uncompressed stores.

Token Fairness and Generalization. A natural question is whether MemOCR’s gains stem from the vision encoder’s higher information density, rather than the learned layout policy. We conduct three comparisons: (a) w.r.t. budget fairness, where text-based agents are granted 4× more tokens; (b) use summarization instead of truncation in textual memory agents; and (c) zero-shot experiments on LO-COMO (Maharana et al., 2024). The results are in Table 3.

Obs. 1.4: MemOCR outperforms text baselines with 4× more token budgets. We compare MemOCR with B = N against baselines with B = 4N (Table 3a). MemOCR still yields superior or comparable performance comparing against textual memory baselines with 4× budgets. At the most extreme setting, MemOCR achieves 62.2% at B = 16, which outperforms MemAgent with B = 64 by 11.5 points.

Obs. 1.5: MemOCR outperforms text baselines augmented with LLM summarization. According to Table 3b, replacing naive truncation with summarization improves MemAgent, e.g., from 31.6 to 58.5 on B = 16.

Table 2. Comparison with recent RAG-based memory baselines with unlimited storage (accuracy %).

<table><tr><td rowspan="2">Method</td><td rowspan="2">Memory Budget (Tokens)</td><td colspan="2">HotpotQA</td><td colspan="2">2Wiki</td><td colspan="2">NQ</td><td colspan="2">TriviaQA</td><td colspan="2">Average</td></tr><tr><td>10K</td><td>30K</td><td>10K</td><td>30K</td><td>10K</td><td>30K</td><td>10K</td><td>30K</td><td>10K</td><td>30K</td></tr><tr><td>SimpleMem</td><td>∞</td><td>73.4</td><td>67.2</td><td>52.3</td><td>41.4</td><td>38.3</td><td>37.5</td><td>57.8</td><td>62.5</td><td>55.5</td><td>52.2</td></tr><tr><td>LightMem</td><td>∞</td><td>64.1</td><td>66.4</td><td>59.4</td><td>50.8</td><td>50.0</td><td>46.1</td><td>42.2</td><td>38.3</td><td>53.9</td><td>50.4</td></tr><tr><td>HyMem</td><td>∞</td><td>65.3</td><td>70.0</td><td>45.8</td><td>49.7</td><td>45.3</td><td>44.5</td><td>69.2</td><td>71.6</td><td>56.4</td><td>59.0</td></tr><tr><td>HyMem</td><td>256</td><td>66.1</td><td>68.4</td><td>41.9</td><td>48.9</td><td>43.8</td><td>43.8</td><td>69.2</td><td>70.8</td><td>55.3</td><td>58.0</td></tr><tr><td rowspan="3">MemOCR</td><td>1024</td><td>84.8</td><td>75.1</td><td>72.2</td><td>73.7</td><td>61.8</td><td>49.2</td><td>79.6</td><td>81.3</td><td>74.6</td><td>69.8</td></tr><tr><td>256</td><td>82.2</td><td>75.4</td><td>71.2</td><td>72.8</td><td>57.3</td><td>48.8</td><td>79.7</td><td>80.9</td><td>72.6</td><td>69.5</td></tr><tr><td>64</td><td>77.6</td><td>68.1</td><td>62.9</td><td>66.2</td><td>51.0</td><td>43.6</td><td>77.6</td><td>80.7</td><td>67.3</td><td>64.7</td></tr></table>

Table 3. Fairness and generalization experiments (accuracy %, 10K context). (a) Budget fairness (MemOCR w/ B = N vs text baselines w/ $B = 4 N$ , Avg over 4 benchmarks). (b) Text summarization replacing truncation for MemAgent (Yu et al., 2025) (Avg over 4 benchmarks. “+Summ.” indicates replacing truncation with summarization). (c) LOCOMO (Maharana et al., 2024) zero-shot evaluation.

<table><tr><td colspan="4">(a) Budget Fairness</td><td colspan="3">(b) vs Text Summarization</td><td colspan="3">(c) LOCOMO Zero-Shot</td></tr><tr><td>N</td><td>MemOCR (B = N)</td><td>MemAgent (B = 4N)</td><td>Mem-α (B = 4N)</td><td>Budget</td><td>MemOCR</td><td>MemAgent+Summ.</td><td>Budget</td><td>Mem-α</td><td>MemOCR</td></tr><tr><td>256</td><td>72.6</td><td>67.8</td><td>47.3</td><td>1024</td><td>74.6</td><td>66.8</td><td>1024</td><td>23.83</td><td>33.14</td></tr><tr><td>64</td><td>67.3</td><td>67.3</td><td>40.3</td><td>256</td><td>72.6</td><td>67.2</td><td>256</td><td>23.05</td><td>31.71</td></tr><tr><td>16</td><td>62.2</td><td>50.7</td><td>25.2</td><td>64</td><td>67.3</td><td>62.0</td><td>64</td><td>8.59</td><td>17.52</td></tr><tr><td></td><td></td><td></td><td></td><td>16</td><td>62.2</td><td>58.5</td><td>16</td><td>3.12</td><td>15.63</td></tr></table>

Under this setting, MemOCR still leads across all budgets. This demonstrates that MemOCR’s advantage is not an artifact of comparing against poorly truncated text, but reflects a genuine benefit of the visual memory paradigm over optimized text compression.

Obs. 1.6: MemOCR generalizes to zero-shot conversational memory. On the LOCOMO (Maharana et al., 2024) long-term conversational memory benchmark (Table 3c), MemOCR outperforms Mem-α acrosss all budgets. These results confirm that the learned layout policy transfers beyond QA to conversational content.

## 八、总结

In this paper, we shift agentic memory management from linear textual streams to a flexible, spatial 2D canvas, termed visual memory. Building on this concept, we propose Mem-OCR, which dynamically manipulates visual layout and resolution to decouple information density from token cost, yielding strong robustness under extreme budget constraints. We discuss the limitations of MemOCR in Appendix B.

For future work, a natural next step is to generalize visual memory beyond QA to broader long-horizon agent settings, such as planning and tool-augmented reasoning, and to study long-term stability under lifelong updates. We also plan to improve the budget allocation policy by introducing more flexible rich-text formats (e.g., HTML).

## References

Arlazarov, V., Andreeva, E., Bulatov, K., Nikolaev, D., Petrova, O., Savelev, B., and Slavin, O. Document image analysis and recognition: a survey. Computer Optics, 46 (4):567–589, 2022.

Bai, S., Chen, K., Liu, X., Wang, J., Ge, W., Song, S., Dang, K., Wang, P., Wang, S., Tang, J., et al. Qwen2. 5-vl technical report. arXiv preprint arXiv:2502.13923, 2025.

Bai, Y., Kadavath, S., Kundu, S., Askell, A., Kernion, J., Jones, A., Chen, A., Goldie, A., Mirhoseini, A., McKinnon, C., et al. Constitutional ai: Harmlessness from ai feedback. arXiv preprint arXiv:2212.08073, 2022.

Bian, H., Yao, Z., Hu, S., Xu, Z., Zhang, S., Guo, Y., Yang, Z., Han, X., Wang, H., and Chen, R. Realmem: Benchmarking llms in real-world memory-driven interaction. arXiv preprint arXiv:2601.06966, 2026.

Cheng, J., Liu, Y., Zhang, X., Fei, Y., Hong, W., Lyu, R., Wang, W., Su, Z., Gu, X., Liu, X., et al. Glyph: Scaling context windows via visual-text compression. arXiv preprint arXiv:2510.17800, 2025.

Chhikara, P., Khant, D., Aryan, S., Singh, T., and Yadav, D. Mem0: Building production-ready ai agents with scalable long-term memory. arXiv preprint arXiv:2504.19413, 2025.

DeepSeek-AI, Guo, D., Yang, D., Zhang, H., Song, J., Zhang, R., Xu, R., Zhu, Q., Ma, S., Wang, P., Bi, X., Zhang, X., Yu, X., Wu, Y., Wu, Z. F., Gou, Z., Shao, Z., Li, Z., Gao, Z., Liu, A., Xue, B., Wang, B., Wu, B., Feng, B., Lu, C., Zhao, C., Deng, C., Zhang, C., Ruan, C., Dai, D., Chen, D., Ji, D., Li, E., Lin, F., Dai, F., Luo, F., Hao, G., Chen, G., Li, G., Zhang, H., Bao, H., Xu, H., Wang, H., Ding, H., Xin, H., Gao, H., Qu, H., Li, H., Guo, J., Li, J., Wang, J., Chen, J., Yuan, J., Qiu, J., Li, J., Cai, J. L., Ni, J., Liang, J., Chen, J., Dong, K., Hu, K., Gao, K., Guan, K., Huang, K., Yu, K., Wang, L., Zhang, L., Zhao, L., Wang, L., Zhang, L., Xu, L., Xia, L., Zhang, M., Zhang, M., Tang, M., Li, M., Wang, M., Li, M., Tian, N., Huang, P., Zhang, P., Wang, Q., Chen, Q., Du, Q., Ge, R., Zhang, R., Pan, R., Wang, R., Chen, R. J., Jin, R. L., Chen, R., Lu, S., Zhou, S., Chen, S., Ye, S., Wang, S., Yu, S., Zhou, S., Pan, S., and Li, S. S. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. CoRR, abs/2501.12948, 2025. doi: 10.48550/ARXIV.2501.12948.

Du, M., Xu, B., Zhu, C., Wang, X., and Mao, Z. Deepresearch bench: A comprehensive benchmark for deep research agents. arXiv preprint arXiv:2506.11763, 2025a.

Du, Y., Huang, W., Zheng, D., Wang, Z., Montella, S., Lapata, M., Wong, K.-F., and Pan, J. Z. Rethinking memory in llm based agents: Representations, operations, and emerging topics. arXiv preprint arXiv:2505.00675, 2025b.

Duverger, R., Bonnin, A., Granier, R., Marolleau, Q., Blanchard, C., Zahzam, N., Bidel, Y., Cadoret, M., Bresson, A., and Schwartz, S. Metrology of microwave fields based on trap-loss spectroscopy with cold rydberg atoms. Physical Review Applied, 22(4):044039, 2024.

Fang, J., Deng, X., Xu, H., Jiang, Z., Tang, Y., Xu, Z., Deng, S., Yao, Y., Wang, M., Qiao, S., Chen, H., and Zhang, N. Lightmem: Lightweight and efficient memory-augmented generation. CoRR, abs/2510.18866, 2025. URL https://doi.org/10. 48550/arXiv.2510.18866.

Feng, L., Yang, F., Chen, F., Cheng, X., Xu, H., Wan, Z., Yan, M., and An, B. Agentocr: Reimagining agent history via optical self-compression. arXiv preprint arXiv:2601.04786, 2026.

Ho, X., Nguyen, A.-K. D., Sugawara, S., and Aizawa, A. Constructing a multi-hop qa dataset for comprehensive evaluation of reasoning steps. In Proceedings ofthe 28th International Conference on Computational Linguistics, pp. 6609–6625, 2020.

Hsieh, C.-P., Sun, S., Kriman, S., Acharya, S., Rekesh, D., Jia, F., Zhang, Y., and Ginsburg, B. Ruler: What’s the

real context size of your long-context language models? arXiv preprint arXiv:2404.06654, 2024.

Hu, S., Wei, Y., Ran, J., Yao, Z., and Zou, L. Does memory need graphs? a unified framework and empirical analysis for long-term dialog memory. arXiv preprint arXiv:2601.01280, 2026.

Hu

### 在线资源

- [论文：arXiv 2601.21468](https://arxiv.org/abs/2601.21468)
- [PDF源文件](/papers/2601.21468.pdf)
