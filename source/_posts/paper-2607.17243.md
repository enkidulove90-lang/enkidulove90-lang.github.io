---
title: "LenGuard-GPC: Length Guarding with Guided-Prompt Consistency for Spatial Reasoning Reinforcement Learning"
date: 2026-07-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2607.17243
arxiv_id: "2607.17243"
---

## 一、简介

Multi-view spatial reasoning requires vision-language models to compare visual evidence across images, align object correspondences, and infer spatial relations over long visual contexts, a setting where chain-of-thought reasoning tends to grow verbose without becoming more accurate. Reinforcement learning with verifiable rewards is a natural fit for this task, but standard GRPO reward relies on sparse outcome-level feedback and gives no signal about where a reasoning trajectory goes wrong, nor any control over its length. We propose LenGuard-GPC, a dense reward framework that addresses both problems together. For each sampled trajectory, it compares the token-wise predictive distributions under a standard prompt and a guided prompt, and uses the resulting token-sum KL divergence as a dense reward si nal. Since this KL enalt accumulates over tokens and would otherwise reward shorter res onses re ardless of their ualit , we introduce a sta ed len th bonus that keeps reasoning length within a controlled range without simply encouraging brevity. On six multi-view spatial reasoning benchmarks, LenGuard-GPC improves accuracy over vanilla GRPO while reducing average response length.

## 二、论文方法

论文在GRPO框架基础上，对每条采样轨迹同时计算标准提示和引导提示下的token级预测分布，以两者的KL散度作为密集一致性奖励。引导提示分布通过teacher forcing在固定轨迹上并行计算，避免二次生成。同时引入分阶段长度奖励，根据长度边界和奖励水平动态调节长度激励，与一致性奖励共同构成最终奖励函数。

## 三、论文里的图与解释

### 图 1

![Figure 1: Overview ofLenGuard-GPCfor multi-view spatial reasoning. Within the staged interval [l , l ], LenGuard-GPC adaptively balances the negative KL-based consistency reward and the length bonus. When the mean per-token KL is high, the consistency reward dominates and encourages more concise reasoning. When the mean per-token KL is low, the length bonus becomes relatively stronger, preventing the model from collapsing into overly short and content-poor chains of thought.](/images/papers/2607.17243/428faa2d9215b9e54e6deef28047a0031030884be8972e2a1a4c842a698ab400.jpg)

**原图说明：** Figure 1: Overview ofLenGuard-GPCfor multi-view spatial reasoning. Within the staged interval [l , l ], LenGuard-GPC adaptively balances the negative KL-based consistency reward and the length bonus. When the mean per-token KL is high, the consistency reward dominates and encourages more concise reasoning. When the mean per-token KL is low, the length bonus becomes relatively stronger, preventing the model from collapsing into overly short and content-poor chains of thought.

**图示解释：** 该图对应论文中的“Figure 1: Overview ofLenGuard-GPCfor multi-view spatial reasoning. Within the staged interval [l , l ], LenGuard-GPC adaptively balances the negative KL-based consistency reward and the length bonus. When the mean per-token KL is high, the consistency reward dominates and encourages more concise reasoning. When the mean per-token KL is low, the length bonus becomes relatively stronger, preventing the model from collapsing into overly short and content-poor chains of thought.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. We identify a key challenge in GRPO-based multi-view spatial reasoning: sparse outcome rewards ofer limited guidance for local cross-view reasoning errors, while naive token-sum KL shaping can bias models toward overly short responses.

2. We introduce LenGuard-GPC, a length-guarded guided-prompt consistency reward that converts guided-prompt token-wise distributional discrepancies into a GRPO-compatible reward signal, enabling dense process-level feedback without an additional supervised loss.

3. We propose a staged length-guard mechanism that mitigates short-answer collapse and boundary- seeking behavior, while demonstrating LenGuard-GPC as a general reward-based framework for long-context multimodal reinforcement learning.

## 五、实验数据集选择

Training Data. Our training set is derived from VST-500K (Yang et al., 2025b). We sample approximately 13,000 instances from its multi-view spatial reasoning data, where each example contains multiple images captured from diferent viewpoints and requires the model to reason over cross-view spatial relations. Unlike single-image visual question answering, these samples require the model to compare visual evidence across views, establish object correspondences, and infer spatial layouts from partially overlapping observations. Therefore, this training set provides a suitable foundation for studying GRPO-based multi-view spatial reasoning and for evaluating whether guided-prompt consistency rewards can improve reasoning behavior under long and visually dense contexts.

Implementation Details. We use Qwen3-VL-8B-Instruct as the base model and train the policy with GRPO. The learning rate is set to $1 \times 1 0 ^ { - 6 }$ . The task reward is composed of an accuracy reward and a format reward:

$$
r _ {\mathrm{task}} (y) = \lambda_ {\mathrm{acc}} r _ {\mathrm{acc}} (y) + \lambda_ {\mathrm{format}} r _ {\mathrm{format}} (y).\tag{7}
$$

Here, $r _ { \mathrm { a c c } } ( y )$ measures whether the final answer is correct, and $r _ { \mathrm { f o r m a t } } ( y )$ measures whether the response follows the required output format. In implementation, we use a format reward of 0.2 to encourage valid response formatting.

The guided-prompt consistency reward is computed from the accumulated token-level KL score:

$$
S _ {\mathrm{KL}} (y) = \sum_ {t = 1} ^ {T} D _ {t},\tag{8}
$$

and is incorporated into the final reward with coeficient $\lambda _ { \mathrm { K L } } = 5 \times 1 0 ^ { - 3 }$ . Equivalently, this corresponds to a KL-score coeficient of $\mathrm { - 5 \times 1 0 ^ { - 3 } }$ in implementation.

For the staged length guard, we set the length boundaries as $l _ { 1 } = 1 6 0 , l _ { 2 } = 3 6 0$ , and $l _ { 3 } = 7 6 8$ . The length bonus starts from $r _ { 1 } = 0 . 2 5$ at $l _ { 1 } = 1 6 0$ tokens and increases by $2 . 5 \times 1 0 ^ { - 4 }$ for each additional token until it reaches $r _ { 2 } = 0 . 3 0$ at $l _ { 2 } = 3 6 0$ tokens. From $l _ { 2 }$ to $l _ { 3 } .$ , the length bonus remains fixed at 0.30. No length bonus is granted beyond $l _ { 3 } = 7 6 8$ tokens, so the staged guard does not encourage excessively long reasoning trajectories.

The final reward combines task performance, guided-prompt consistency, and staged length regulation:

$$
r (y) = \lambda_ {\mathrm{task}} r _ {\mathrm{task}} (y) - \lambda_ {\mathrm{KL}} S _ {\mathrm{KL}} (y) + \lambda_ {\mathrm{len}} r _ {\mathrm{len}} (T).\tag{9}
$$

These settings are designed to balance the negative guided-prompt consistency reward with suficient reasoning length, preventing short-answer collapse while avoiding unnecessary verbosity

<table><tr><td>Model</td><td>Size</td><td>MMSI*</td><td>ViewSpatial*</td><td>MindCube*,‡</td><td>3DSR◇</td><td>BLINK◇</td><td>CV◇</td><td>Avg.</td></tr><tr><td>RandomChoice</td><td>-</td><td>25.0</td><td>26.3</td><td>33.0</td><td>45.8</td><td>38.1</td><td>42.5</td><td>35.1</td></tr><tr><td colspan="9">Close-source models</td></tr><tr><td>Gemini-2.5-Pro</td><td>-</td><td>38.0</td><td>46.0</td><td>57.6</td><td>59.3</td><td>73.5</td><td>85.9</td><td>60.1</td></tr><tr><td>GPT-5</td><td>-</td><td>41.8</td><td>45.5</td><td>56.3</td><td>60.3</td><td>68.0</td><td>84.6</td><td>59.4</td></tr><tr><td>Gemini-3-Pro-Preview</td><td>-</td><td>45.2</td><td>50.3</td><td>70.8</td><td>68.9</td><td>76.0</td><td>92.0</td><td>67.2</td></tr><tr><td colspan="9">Open-source General Models</td></tr><tr><td>InternVL3-2B (Zhu et al., 2025)</td><td>2B</td><td>26.5</td><td>32.5</td><td>37.5</td><td>47.7</td><td>50.8</td><td>76.5</td><td>45.3</td></tr><tr><td>InternVL3-8B (Zhu et al., 2025)</td><td>8B</td><td>28.0</td><td>38.6</td><td>41.5</td><td>44.3</td><td>53.5</td><td>81.0</td><td>47.8</td></tr><tr><td>Qwen2.5-VL-3B-Instruct (Bai et al., 2025b)</td><td>3B</td><td>28.6</td><td>31.9</td><td>37.6</td><td>43.5</td><td>48.7</td><td>71.8</td><td>43.7</td></tr><tr><td>Qwen2.5-VL-7B-Instruct (Bai et al., 2025b)</td><td>7B</td><td>26.8</td><td>36.8</td><td>36.0</td><td>47.5</td><td>55.9</td><td>75.4</td><td>46.4</td></tr><tr><td>Qwen3-VL-2B-Instruct (Bai et al., 2025a)</td><td>2B</td><td>28.9</td><td>36.9</td><td>34.5</td><td>47.5</td><td>53.2</td><td>78.4</td><td>46.6</td></tr><tr><td>Qwen3-VL-4B-Instruct (Bai et al., 2025a)</td><td>4B</td><td>30.1</td><td>42.5</td><td>37.0</td><td>52.5</td><td>62.6</td><td>84.7</td><td>51.6</td></tr><tr><td>Qwen3-VL-8B-Instruct (Bai et al., 2025a)</td><td>8B</td><td>31.0</td><td>42.2</td><td>29.4</td><td>53.9</td><td>66.7</td><td>85.1</td><td>51.4</td></tr><tr><td colspan="9">Spatial Intelligence Models</td></tr><tr><td>SpatialLadder-3B (Li et al., 2025b)</td><td>3B</td><td>27.4</td><td>39.8</td><td>43.4</td><td>42.8</td><td>43.0</td><td>73.7</td><td>45.0</td></tr><tr><td>SpaceR-7B (Ouyang et al., 2025)</td><td>7B</td><td>27.4</td><td>35.8</td><td>37.9</td><td>40.5</td><td>49.6</td><td>74.8</td><td>44.3</td></tr><tr><td>ViLaSR-7B (Wu et al., 2025c)</td><td>7B</td><td>30.2</td><td>35.7</td><td>35.1</td><td>46.6</td><td>51.4</td><td>76.7</td><td>46.0</td></tr><tr><td>Cambrian-S-3B (Yang et al., 2025d)</td><td>3B</td><td>25.2</td><td>39.0</td><td>32.5</td><td>41.4</td><td>37.7</td><td>75.2</td><td>41.8</td></tr><tr><td>Cambrian-S-7B (Yang et al., 2025d)</td><td>7B</td><td>25.8</td><td>40.9</td><td>39.6</td><td>45.0</td><td>37.9</td><td>76.9</td><td>44.4</td></tr><tr><td>VST-3B-RL (Yang et al., 2025b)</td><td>3B</td><td>32.0</td><td>45.0</td><td>36.4</td><td>56.5</td><td>57.2</td><td>84.2</td><td>51.9</td></tr><tr><td>VST-7B-RL (Yang et al., 2025b)</td><td>7B</td><td>34.8</td><td>42.4</td><td>39.1</td><td>60.1</td><td>62.6</td><td>86.5</td><td>54.3</td></tr><tr><td>Vanilla GRPO</td><td>8B</td><td>32.2</td><td>44.4</td><td>44.7</td><td>59.4</td><td>65.7</td><td>85.2</td><td>55.3</td></tr><tr><td colspan="9">Ours</td></tr><tr><td>LENGUARD-GPC</td><td>8B</td><td>36.1</td><td>46.9</td><td>48.4</td><td>60.1</td><td>66.8</td><td>85.5</td><td>57.3</td></tr></table>

Table 1: Overall accuracy (%) on six evaluation benchmarks. Benchmarks marked with ∗ follow the same multi-view spatial reasoning domain as our training data, while benchmarks marked with ⋄ are used as out-of-domain evaluations. MindCube is additionally marked with ‡ because we only use itfor evaluation and do not use its provided training set.

Evaluation Setting. We evaluate the trained models on six benchmarks covering both in-domain and out- of-domain reasoning scenarios. Specifically, MMSI-Bench (Yang et al., 2025e), MindCube, and ViewSpatial-Bench (Li et al., 2025a) are multi-image spatial reasoning benchmarks, where each instance requires the model to compare visual evidence across multiple views and infer spatial relations. These benchmarks are most aligned with our training data, which also consists of multi-view spatial reasoning samples. Notably, MindCube is used only for evaluation, and we do not use its provided training set.

To further assess the generalization ability of our method and verify that the training procedure does not overfit to the in-domain data, we additionally evaluate on three out-of-domain benchmarks: 3DSR (Ma et al., 2025) and CV-Bench (Tong et al., 2024), which focus on single-image spatial reasoning, and BLINK (Fu et al., 2024), which involves multi-image reasoning but is not primarily centered on spatial relation inference. This evaluation protocol allows us to examine whether the proposed guided-prompt consistency reward improves performance on in-domain multi-view spatial reasoning tasks while maintaining robustness on related spatial and multi-image reasoning tasks beyond the training distribution.

## 六、消融实验

We conduct ablation studies on MMSI-Bench to isolate the contributions of key components as shown in Table 3. First, replacing our structured two-stage output with free-form reasoning under RL (“Free format Reasoning + RL”) reduces overall accuracy from 35.4 to 33.4, indicating that enforcing an explicit spatial pre-thinking stage helps mitigate shortcut behaviors and improves robustness. Second, removing GRPO (“w/o GRPO”) leads to a larger drop (35.4 → 32.4), demonstrating that RL optimization with group- relative advantages is important for improving correctness under multi-view inputs beyond SFT alone. Third, removing the format reward (“w/o Format Reward”) yields a modest decrease in MMSI accuracy (35.4 → 35.0) but noticeably changes the distribution across subcategories, consistent with the role of the format reward as a stabilizer that maintains disciplined generation and prevents bypassing the intended inference protocol. Taken together, the ablations confirm that both the two-stage reasoning supervision and GRPO-based RL are necessary to achieve the strongest and most reliable multi-view spatial reasoning performance.

## 七、Benchmark 结果与解释

Table 1 reports the overall accuracy on six evaluation benchmarks. Compared with the base Qwen3-VL-8B-Instruct model, vanilla GRPO improves the average accuracy from 51.4% to 55.3%, showing that RL training can enhance multi-view spatial reasoning performance. Our LenGuard-GPC further improves the average accuracy to 57.3%, yielding a gain of +2.0 points over vanilla GRPO and +5.9 points over the base model.

The improvement is most pronounced on benchmarks that follow the same multi-view spatial reasoning domain as our training data. On MMSI, LenGuard-GPC improves over vanilla GRPO from 32.2% to 36.1%, corresponding to a +3.9 point gain. On MindCube, which is used only for evaluation without using its provided training set, the accuracy increases from 44.7% to 48.4%. On ViewSpatial, LenGuard-GPC further improves the accuracy from 44.4% to 46.9%. These results suggest that the proposed reward design generalizes beyond the exact training source while remaining efective within the multi-view spatial reasoning domain.

<table><tr><td rowspan="2">Models</td><td colspan="6">Positional Relationship</td><td colspan="2">Attribute</td><td colspan="2">Motion</td><td>MSR</td><td>Avg.</td></tr><tr><td>Cam.-Cam.</td><td>Obj.-Obj.</td><td>Reg.-Reg.</td><td>Cam.-Obj.</td><td>Obj.-Reg.</td><td>Cam.-Reg.</td><td>Meas.</td><td>Appr.</td><td>Cam.</td><td>Obj.</td><td>-</td><td></td></tr><tr><td>RandomChoice</td><td>25.0</td><td>25.0</td><td>25.0</td><td>25.0</td><td>25.0</td><td>25.0</td><td>25.0</td><td>25.0</td><td>25.0</td><td>25.0</td><td>25.0</td><td>25.0</td></tr><tr><td colspan="13">Close-source models</td></tr><tr><td>Gemini-2.5-Pro</td><td>38.7</td><td>34.0</td><td>40.7</td><td>44.2</td><td>38.8</td><td>41.0</td><td>62.5</td><td>30.3</td><td>39.2</td><td>25.0</td><td>33.3</td><td>38.0</td></tr><tr><td>GPT-5</td><td>41.9</td><td>33.0</td><td>35.8</td><td>49.8</td><td>42.4</td><td>68.7</td><td>54.7</td><td>37.4</td><td>28.3</td><td>40.8</td><td>36.4</td><td>41.8</td></tr><tr><td colspan="13">Open-source General Models</td></tr><tr><td>InternVL3-2B (Zhu et al., 2025)</td><td>31.2</td><td>22.3</td><td>28.4</td><td>30.2</td><td>28.2</td><td>28.9</td><td>25.0</td><td>22.7</td><td>16.2</td><td>28.9</td><td>26.8</td><td>26.5</td></tr><tr><td>InternVL3-8B (Zhu et al., 2025)</td><td>22.6</td><td>22.3</td><td>34.6</td><td>31.4</td><td>42.4</td><td>33.7</td><td>25.0</td><td>19.7</td><td>20.3</td><td>34.2</td><td>24.8</td><td>28.0</td></tr><tr><td>Qwen2.5-VL-3B-Instruct (Bai et al., 2025b)</td><td>36.6</td><td>30.9</td><td>28.4</td><td>26.7</td><td>28.2</td><td>31.3</td><td>31.2</td><td>16.7</td><td>16.2</td><td>35.5</td><td>28.8</td><td>28.6</td></tr><tr><td>Qwen2.5-VL-7B-Instruct (Bai et al., 2025b)</td><td>28.0</td><td>26.6</td><td>19.8</td><td>32.6</td><td>38.8</td><td>28.9</td><td>23.4</td><td>21.2</td><td>20.3</td><td>30.3</td><td>24.8</td><td>26.8</td></tr><tr><td>Qwen3-VL-2B-Instruct (Bai et al., 2025a)</td><td>26.9</td><td>29.8</td><td>30.9</td><td>38.4</td><td>35.3</td><td>33.7</td><td>23.4</td><td>28.8</td><td>29.7</td><td>28.9</td><td>21.2</td><td>28.9</td></tr><tr><td>Qwen3-VL-8B-Instruct (Bai et al., 2025a)</td><td>28.0</td><td>37.2</td><td>32.1</td><td>31.4</td><td>35.3</td><td>38.5</td><td>37.5</td><td>15.2</td><td>27.0</td><td>28.9</td><td>29.8</td><td>31.1</td></tr><tr><td colspan="13">Spatial Intelligence Models</td></tr><tr><td>SpatialLadder-3B (Li et al., 2025b)</td><td>36.6</td><td>29.8</td><td>29.6</td><td>32.6</td><td>30.6</td><td>24.1</td><td>18.8</td><td>31.8</td><td>23.0</td><td>23.7</td><td>23.2</td><td>27.4</td></tr><tr><td>Spatial-MLLM-4B (Wu et al., 2025a)</td><td>24.7</td><td>21.3</td><td>28.4</td><td>30.2</td><td>29.4</td><td>28.9</td><td>18.8</td><td>34.9</td><td>10.8</td><td>23.7</td><td>29.8</td><td>26.1</td></tr><tr><td>SpaceR-7B (Ouyang et al., 2025)</td><td>25.8</td><td>31.9</td><td>29.6</td><td>25.6</td><td>31.8</td><td>22.9</td><td>26.6</td><td>28.8</td><td>16.2</td><td>34.2</td><td>27.3</td><td>27.4</td></tr><tr><td>ViLaSR-7B (Wu et al., 2025c)</td><td>29.0</td><td>35.1</td><td>28.4</td><td>39.5</td><td>40.0</td><td>44.6</td><td>31.2</td><td>16.7</td><td>17.6</td><td>31.6</td><td>23.2</td><td>30.2</td></tr><tr><td>Cambrian-S-3B (Yang et al., 2025d)</td><td>25.8</td><td>28.7</td><td>24.7</td><td>48.8</td><td>24.7</td><td>33.7</td><td>29.7</td><td>22.7</td><td>20.3</td><td>28.9</td><td>18.7</td><td>27.0</td></tr><tr><td>Cambrian-S-7B (Yang et al., 2025d)</td><td>24.7</td><td>26.6</td><td>24.7</td><td>47.7</td><td>22.4</td><td>31.3</td><td>32.8</td><td>24.2</td><td>12.2</td><td>30.3</td><td>24.2</td><td>27.1</td></tr><tr><td>Vanilla GRPO</td><td>47.3</td><td>29.8</td><td>28.4</td><td>34.9</td><td>32.9</td><td>43.4</td><td>43.8</td><td>27.3</td><td>32.4</td><td>27.6</td><td>21.2</td><td>32.2</td></tr><tr><td colspan="13">Ours</td></tr><tr><td>LENGUARD-GPC</td><td>48.4</td><td>35.1</td><td>29.6</td><td>48.8</td><td>40.0</td><td>55.4</td><td>50.0</td><td>19.7</td><td>33.8</td><td>23.7</td><td>24.8</td><td>36.1</td></tr></table>

Table 2: Fine-grained accuracy (%) breakdown on MMSI-Bench. We compare LenGuard-GPC with baselines that are included in the main results table and also have fine-grained MMSI results available.

On out-of-domain benchmarks, LenGuard-GPC also maintains consistent gains over vanilla GRPO. It improves 3DSR from 59.4% to 60.1%, BLINK from 65.7% to 66.8%, and CV-Bench from 85.2% to 85.5%. Although these gains are smaller than those on in-domain benchmarks, they indicate that the guided-prompt consistency reward and staged length guard do not overfit to the training distribution or sacrifice general reasoning ability.

Compared with existing open-source baselines, LenGuard-GPC achieves the best average performance among the listed open-source models. These results demonstrate that explicitly regulating reasoning behavior with guided-prompt consistency and staged length control is efective for improving multi-view spatial reasoning while preserving robustness on out-of-domain evaluations.

Table 2 further provides a fine-grained breakdown on MMSI-Bench. Compared with vanilla GRPO, LenGuard-GPC improves the overall accuracy from 32.2% to 36.1% and achieves gains in most subcategories. The largest improvements appear in cross-view positional reasoning, including Cam.–Obj. (+13.9 points), Cam.–Reg. (+12.0 points), Obj.–Reg. (+7.1 points), and Obj.–Obj. (+5.3 points), sug- gesting that our reward design mainly strengthens spatial relation reasoning across views. In addition, LenGuard-GPC improves Attribute Meas., Motion Cam., and MSR, while the drops on Attribute Appr. and Motion Obj. indicate that appearance-based attributes and object-motion reasoning remain challenging.

Although LenGuard-GPC evaluates each sampled trajectory under both the standard and guided prompts, this does not require two full autoregressive generations. The trajectory is sampled only once from the standard prompt, while the guided-prompt distribution is computed over the fixed trajectory using teacher forcing, allowing token-level predictions to be evaluated in parallel. Moreover, the remaining GRPO operations, including advantage computation, backpropagation, and parameter updates, are shared with the vanilla training pipeline. Consequently, the additional guided-prompt evaluation increases the overall training time by only approximately 1.6×, rather than doubling it. The shorter trajectories induced by LenGuard-GPC further ofset part of this additional cost.uality here is therefore not a function of length; what matters is whether the trace resolves cross-view correspondence at all.

<table><tr><td rowspan="2">Models</td><td colspan="6">Positional Relationship</td><td colspan="2">Attribute</td><td colspan="2">Motion</td><td>MSR</td><td>Avg.</td></tr><tr><td>Cam.-Cam.</td><td>Obj.-Obj.</td><td>Reg.-Reg.</td><td>Cam.-Obj.</td><td>Obj.-Reg.</td><td>Cam.-Reg.</td><td>Meas.</td><td>Appr.</td><td>Cam.</td><td>Obj.</td><td>-</td><td></td></tr><tr><td>Qwen3-VL-8B-Instruct</td><td>28.0</td><td>37.2</td><td>32.1</td><td>31.4</td><td>35.3</td><td>38.5</td><td>37.5</td><td>15.2</td><td>27.0</td><td>28.9</td><td>29.8</td><td>31.1</td></tr><tr><td>Vanilla GRPO</td><td>47.3</td><td>29.8</td><td>28.4</td><td>34.9</td><td>32.9</td><td>43.4</td><td>43.8</td><td>27.3</td><td>32.4</td><td>27.6</td><td>21.2</td><td>32.2</td></tr><tr><td>w/o Staged Length Reward</td><td>45.2</td><td>34.0</td><td>23.5</td><td>46.5</td><td>32.9</td><td>47.0</td><td>45.3</td><td>25.8</td><td>27.0</td><td>26.3</td><td>24.8</td><td>33.5</td></tr><tr><td>Full Method</td><td>48.4</td><td>35.1</td><td>29.6</td><td>48.8</td><td>40.0</td><td>55.4</td><td>50.0</td><td>19.7</td><td>33.8</td><td>23.7</td><td>24.8</td><td>36.1</td></tr></table>

Table 3: Ablation study on MMSI-Bench (accuracy, %), comparing vanilla GRPO, the variant without the staged length reward, and the full method on fine-grained subcategories and overall performance.

## 八、总结

In this paper, we propose LenGuard-GPC, a GRPO-based training framework for improving multi-view spatial reasoning through guided-prompt consistency and staged length regulation. By comparing model behavior under standard and guided prompts, our method provides dense trajectory-level feedback without introducing any inference-time overhead, while the staged length guard encourages reasoning that is suficient but not unnecessarily verbose. Experiments on six benchmarks show that LenGuard-GPC consistently improves over the base Qwen3-VL-8B-Instruct model and vanilla GRPO, with especially clear gains on in-domain multi-view spatial reasoning tasks. Fine-grained results further indicate that the improvements mainly come from stronger cross-view positional reasoning. Overall, LenGuard-GPC demonstrates that explicitly regulating reasoning behavior is an efective strategy for building more accurate, compact, and robust multimodal spatial reasoning models

## References

Jean-Baptiste Alayrac, Jef Donahue, Pauline Luc, Antoine Miech, Iain Barr, Yana Hasson, Karel Lenc, Arthur Mensch, Katherine Millican, Malcolm Reynolds, et al. Flamingo: a visual language model for few-shot learning. Advances in neural information processing systems, 35:23716–23736, 2022.

Jinze Bai, Shuai Bai, Yunfei Chu, Zeyu Cui, Kai Dang, Xiaodong Deng, Yang Fan, Wenbin Ge, Yu Han, Fei Huang, et al. Qwen technical report. arXiv preprint arXiv:2309.16609, 2023.

Shuai Bai, Yuxuan Cai, Ruizhe Chen, Keqin Chen, Xionghui Chen, Zesen Cheng, Lianghao Deng, Wei Ding, Chang Gao, Chunjiang Ge, Wenbin Ge, Zhifang Guo, Qidong Huang, Jie Huang, Fei Huang, Binyuan Hui, Shutong Jiang, Zhaohai Li, Mingsheng Li, Mei Li, Kaixin Li, Zicheng Lin, Junyang Lin, Xuejing Liu, Jiawei Liu, Chenglong Liu, Yang Liu, Dayiheng Liu, Shixuan Liu, Dunjie Lu, Ruilin Luo, Chenxu Lv, Rui Men, Lingchen Meng, Xuancheng Ren, Xingzhang Ren, Sibo Song, Yuchong Sun, Jun Tang, Jianhong Tu, Jianqiang Wan, Peng Wang, Pengfei Wang, Qiuyue Wang, Yuxuan Wang, Tianbao Xie, Yiheng Xu, Haiyang Xu, Jin Xu, Zhibo Yang, Mingkun Yang, Jianxin Yang, An Yang, Bowen Yu, Fei Zhang, Hang Zhang, Xi Zhang, Bo Zheng, Humen Zhong, Jingren Zhou, Fan Zhou, Jing Zhou, Yuanzhi Zhu, and Ke Zhu. Qwen3-vl technical report, 2025a. URL https://arxiv.org/abs/2511.21631.

Shuai Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, Sibo Song, Kai Dang, Peng Wang, Shijie Wang, Jun Tang, et al. Qwen2. 5-vl technical report. arXiv preprint arXiv:2502.13923, 2025b.

Hunar Batra, Haoqin Tu, Hardy Chen, Yuanze Lin, Cihang Xie, and Ronald Clark. Spatialthinker: Reinforcing 3d reasoning in multimodal llms via spatial rewards. arXiv preprint arXiv:2511.07403, 2025.

Boyuan Chen, Zhuo Xu, Sean Kirmani, Brain Ichter, Dorsa Sadigh, Leonidas Guibas, and Fei Xia. Spatialvlm: Endowing vision-language models with spatial reasoning capabilities. In Proceedings ofthe IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 14455–14465, 2024.

Yuhao Dong, Zuyan Liu, Hai-Long Sun, Jingkang Yang, Winston Hu, Yongming Rao, and Ziwei Liu. Insightv: Exploring long-chain visual reasoning with multimodal large language models. In Proceedings of the Computer Vision and Pattern Recognition Conference, pp. 9062–9072, 2025.

Zhiwen Fan, Jian Zhang, Renjie Li, Junge Zhang, Runjin Chen, Hezhen Hu, Kevin Wang, Huaizhi Qu, Dilin Wang, Zhicheng Yan, et al. Vlm-3r: Vision-language models augmented with instruction-aligned 3d reconstruction. arXiv preprint arXiv:2505.20279, 2025.

Kaituo Feng, Kaixiong Gong, Bohao Li, Zonghao Guo, Yibing Wang, Tianshuo Peng, Junfei Wu, Xiaoying Zhang, Benyou Wang, and Xiangyu Yue. Video-r1: Reinforcing video reasoning in mllms. arXiv preprint arXiv:2503.21776, 2025.

Xingyu Fu, Yushi Hu, Bangzheng Li, Yu Feng, Haoyu Wang, Xudong Lin, Dan Roth, Noah A Smith, Wei-Chiu Ma, and Ranjay Krishna. Blink: Multimodal large language models can see but not perceive. In European Conference on Computer Vision, pp. 148–166. Springer, 2024.

Mohsen Gholami, Ahmad Rezaei, Zhou Weimin, Sitong Mao, Shunbo Zhou, Yong Zhang, and Mohammad Akbari. Spatial reasoning with vision-language models in ego-centric multi-view scenes. arXiv preprint arXiv:2509.06266, 2025.

Boyu Gou, Ruohan Wang, Boyuan Zheng, Yanan Xie, Cheng Chang, Yiheng Shu, Huan Sun, and Yu Su. Navigating the digital world as humans do: Universal visual grounding for GUI agents. In The Thirteenth International Conference on Learning Representations, 2025. URL https://openreview.net/forum?id= kxnoqaisCT.

Zirun Guo, Minjie Hong, and Tao Jin. Observe-r1: Unlocking reasoning abilities of mllms with dynamic progressive reinforcement learning. arXiv preprint arXiv:2505.12432, 2025.

Michael Hassid, Gabriel Synnaeve, Yossi Adi, and Roy Schwartz. Don’t overthink it. preferring shorter thinking chains for improved llm reasoning. arXiv preprint arXiv:2505.17813, 2025.

Wenxuan Huang, Bohan Jia, Zijie Zhai, Shaosheng Cao, Zheyu Ye, Fei Zhao, Zhe Xu, Yao Hu, 

### 在线资源

- [论文：arXiv 2607.17243](https://arxiv.org/abs/2607.17243)
- [代码：GitHub](https://github.com/taoxj2001/LenGuard-GPC)
- [PDF源文件](/papers/2607.17243.pdf)
