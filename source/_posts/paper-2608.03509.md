---
title: "SkillJack: Persistent Skill Backdoors in Self-Evolving Agents"
date: 2026-08-01
year: 2026
venue_type: "arXiv预印本"
venue_name: "arXiv"
categories: [推荐系统, 论文速递]
tags: [论文速递]
slug: paper-2608.03509
arxiv_id: "2608.03509"
---

## 一、简介

Self-evolving agents increasingly convert interaction histories into reusable skills that persist beyond individual tasks. While prior work studies memory and retrieval poisoning, such attacks only affect agents when poisoned records are retrieved as context. We uncover a new and more fundamental risk: poisoned experiences can be transformed by the agent itself into durable behavioral artifacts. We present SkillJack, the first attack that exploits the experience-toskill pipeline of self-evolving agents. Instead of directly manipulating runtime context, SkillJack hijacks the agent’s own learning process to implant malicious behaviors into its reusable skill repertoire. We identify three key properties of this transformation: sanitization whitewashing, where malicious intent is obscured during skill extraction; cross-layer promotion, where transient experiences become persistent capabilities; and persistence isolation, where the attack survives removal of its original source records. We evaluate SkillJack on two representative systems, SkillX and Anything2Skill, using a shared dataset of 150 trajectories across four policy-risk categories. Results show that skill extraction substantially reduces attack detectability: in SkillX, safety detection drops from 98.5% for poisoned trajectories to 11.4% for extracted skills, while Anything2Skill shows a similar effect. Meanwhile, the implanted skills remain effective, achieving attack success rates of 56.2% and 89.2% on the two systems, respectively. Furthermore, 80.0% of skill-mediated attacks persist after deleting the original poisoned records, and some skills unintentionally activate on benign queries. Our findings reveal skill evolution as a new attack surface and motivate provenance-aware skill lifecycle protection. Our code is available at https://github.com/Tencent/AI-Infra-Guard/research/skilljack.

![](images/12b818979f21f43cd84017ad3b418afd79d792a718b4eb3a2c84738b63ad3783.jpg)  
Figure 1 | SkillJack. An attacker influences only the experience layer; the agent’s own experience-to-skill pipeline then compiles the poisoned record into a separately stored, reusable skill that is routed to future tasks and outlives the source record.

## 二、论文方法

We formalize the attack and its objective, then describe the payloads that realize it. The pipeline stages and threat model are those of Section 2.

## 三、论文里的图与解释

### 图 1

![Sanitization whitewashing across systems. For each configuration, the LLM judge flags the raw trajectory far more often than the skill later extracted from it: SkillX $98.5%$ vs.\ $11.4%$, A2S DOC mode $100.0%$ vs.\ $44.4%$, and A2S SDK mode $100.0%$ vs.\ $28.6%$. Extraction reduces detectability in every case; the reduction is largest for SkillX, which produces the most abstracted skills.](/images/papers/2608.03509/figure_001_fig_whitewashing.png)

**原图说明：** Sanitization whitewashing across systems. For each configuration, the LLM judge flags the raw trajectory far more often than the skill later extracted from it: SkillX $98.5%$ vs.\ $11.4%$, A2S DOC mode $100.0%$ vs.\ $44.4%$, and A2S SDK mode $100.0%$ vs.\ $28.6%$. Extraction reduces detectability in every case; the reduction is largest for SkillX, which produces the most abstracted skills.

**图示解释：** 该图对应论文中的“Sanitization whitewashing across systems. For each configuration, the LLM judge flags the raw trajectory far more often than the skill later extracted from it: SkillX $98.5%$ vs.\ $11.4%$, A2S DOC mode $100.0%$ vs.\ $44.4%$, and A2S SDK mode $100.0%$ vs.\ $28.6%$. Extraction reduces detectability in every case; the reduction is largest for SkillX, which produces the most abstracted skills.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 2

![Trigger rates in the matched 25-task evaluation, per risk category and overall (25 tasks). Direct-context injection triggers most often, but the skill pathway is durable: 80.0% of skill-based triggers survive deletion of the source trajectories (post-deletion versus skill-based, overall $32.0/40.0$). Values are percentages.](/images/papers/2608.03509/figure_002_fig_persistence.png)

**原图说明：** Trigger rates in the matched 25-task evaluation, per risk category and overall (25 tasks). Direct-context injection triggers most often, but the skill pathway is durable: 80.0% of skill-based triggers survive deletion of the source trajectories (post-deletion versus skill-based, overall $32.0/40.0$). Values are percentages.

**图示解释：** 该图对应论文中的“Trigger rates in the matched 25-task evaluation, per risk category and overall (25 tasks). Direct-context injection triggers most often, but the skill pathway is durable: 80.0% of skill-based triggers survive deletion of the source trajectories (post-deletion versus skill-based, overall $32.0/40.0$). Values are percentages.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

### 图 3

![Routing-level outcomes on SkillX over a 356-skill library (305 poisoned, 51 clean), across 32 attack-oriented and 15 clean tasks. Trigger rate is the share of tasks routed to a skill that satisfies the policy-violation proxy; expected-category match is the share routed to a skill of the intended category (undefined for clean tasks). The clean-task trigger rate of 20.0% reflects collateral selection. Values are percentages.](/images/papers/2608.03509/figure_003_fig_routing.png)

**原图说明：** Routing-level outcomes on SkillX over a 356-skill library (305 poisoned, 51 clean), across 32 attack-oriented and 15 clean tasks. Trigger rate is the share of tasks routed to a skill that satisfies the policy-violation proxy; expected-category match is the share routed to a skill of the intended category (undefined for clean tasks). The clean-task trigger rate of 20.0% reflects collateral selection. Values are percentages.

**图示解释：** 该图对应论文中的“Routing-level outcomes on SkillX over a 356-skill library (305 poisoned, 51 clean), across 32 attack-oriented and 15 clean tasks. Trigger rate is the share of tasks routed to a skill that satisfies the policy-violation proxy; expected-category match is the share routed to a skill of the intended category (undefined for clean tasks). The clean-task trigger rate of 20.0% reflects collateral selection. Values are percentages.”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。

## 四、模块创新点

1. A new attack surface. We are, to our knowledge, the first to identify and formalize experience-to-skill poisoning as a distinct security risk of self-evolving agents, and we characterize three properties that emerge only from the composition of experience poisoning with automated skill extraction: sanitization whitewashing, cross-layer promotion, and persistence isolation.

2. A transformation-resilient attack method. We design transformation-resilient payloads (Section 3.2) that survive the extraction pipeline’s compression and abstraction while retaining a policy-relevant action. A paired comparison against directly malicious wording, together with an ablation over skill names, descriptions, and content, shows both that the method works and why: framing survives extraction where overt wording is filtered or exposed.

3. Cross-system empirical validation. We validate the attack on two independently implemented systems, SkillX and Anything2Skill, under a shared dataset and configuration, establishing extraction-stage whitewashing and measuring persistence, downstream triggering, collateral routing, and defense sensitivity. The results show the risk is a property of the paradigm rather than of one implementation.

## 五、实验数据集选择

Representative systems. We evaluate SkillX [14] and Anything2Skill (A2S) [10] as two representative implementations of experience-to-skill automation. SkillX uses plan-based trajectory extraction and LLM-native progressive-disclosure routing; its pipeline includes a plan extractor, a functional-skill extractor, and a skill library. A2S uses taxonomy-guided compilation of heterogeneous experience records into structured skill contracts; we evaluate both its SDK and document-ingestion modes, with DOC mode providing the primary results.1

Benchmark and model. We adopt the AppWorld [13] format: 9 applications, 457 APIs, and a trajectory JSONL schema. All extraction, routing, judgment, and agent reasoning use DeepSeekv4-flash via API; the model is an implementation detail, and our conclusions have not yet been replicated across models.

Dataset. The dataset comprises 150 trajectory records: 65 functionally framed poisoned trajectories (20 data exfiltration, 15 privilege escalation, 15 unauthorized transfer, and 15 persistentbackdoor cases), 65 directly malicious wording baselines paired to the framed set, and 20 clean AppWorld-format trajectories. The identical 65+65+20 trajectory files are supplied to both extractors. SkillX produces 264 framed skills and 241 direct-baseline skills. A2S document mode yields reusable outputs for 27 framed trajectories (30 extracted skills in the subsequent retrieval bank) and for 0 directly malicious baselines. The clean SkillX routing library contains 51 clean baseline skills; the 356-skill routing library used in the routing evaluation contains 305 poisoned skills and 51 clean skills. Because a single trajectory can yield multiple skills, “505 extracted skills” refers to the two SkillX poisoned extraction sets, not a single shared runtime library.

Detectors and success criterion. We employ two proxy detectors: (1) pattern matching, using regexes for pre-specified risky patterns, and (2) an LLM judge, in which DeepSeek-v4-flash classifies a skill as malicious or benign. These are evaluation instruments, not certified security controls. We call their combination the policy-violation proxy. A task counts as triggered when the routed skill satisfies this proxy; consequently, all trigger rates and ASR figures in this section are routing-level surrogates, not live-compromise rates.

Research questions. The evaluation is organized around five questions, each answered by the experiments that follow.

RQ1 Stealth. Does compiling a poisoned trajectory into a skill make it harder to detect than the raw trajectory, and is functional framing responsible? (Sections 4.2 and 4.3)

RQ2 Generality. Does the same extraction-stage laundering appear in a second, independently implemented system? (Section 4.4)

RQ3 Persistence. Do derived skills keep triggering after their source records are deleted? (Section 4.5)

RQ4 Reach. Are derived skills routed to and triggered on later tasks, and do they misfire on unrelated benign tasks? (Sections 4.6 and 4.7)

RQ5 Mechanism and defense. What makes the skills evade the judge, and do extraction-time review or runtime monitoring mitigate the attack? (Sections 4.8 and 4.9)

These questions trace the attack lifecycle: RQ1 and RQ2 establish that the attack is stealthy and not tied to one implementation; RQ3 and RQ4 show it is durable and far-reaching; and

Table 2 | Extraction and post-extraction detectability across the two representative systems. Extraction is the share of input trajectories that yield at least one skill; SkillX yields skills for essentially all inputs, so its extraction entry is fixed at 100.0%. Detection and evasion are reported for the framed (attack) skills unless the payload column states otherwise. All values are rates.

<table><tr><td>System</td><td>Payload</td><td>Extraction</td><td>Raw-traj. LLM det.</td><td>Derived LLM det.</td><td>Derived pattern det.</td><td>LLM evasion</td></tr><tr><td>SkillX</td><td>Framed</td><td>100.0%</td><td>98.5%</td><td>11.4%</td><td>11.0%</td><td>88.6%</td></tr><tr><td>SkillX</td><td>Direct baseline</td><td>100.0%</td><td>n/a</td><td>27.0%</td><td>27.8%</td><td>73.0%</td></tr><tr><td>A2S (SDK)</td><td>Framed</td><td>10.8%</td><td>100.0%</td><td>28.6%</td><td>28.6%</td><td>71.4%</td></tr><tr><td>A2S (DOC)</td><td>Framed</td><td>41.5%</td><td>100.0%</td><td>44.4%</td><td>3.7%</td><td>55.6%</td></tr><tr><td>A2S (DOC)</td><td>Direct baseline</td><td>0.0%</td><td>100.0%</td><td>n/a</td><td>n/a</td><td>n/a</td></tr></table>

SkillX raw-trajectory detection is measured on the 65 framed trajectories. A2S SDK extracts a single direct-baseline skill (1.5%), which the judge flags (100.0% detection); A2S DOC extracts none, so its direct-baseline derived detection and evasion are undefined (n/a). Overtly malicious skill names appear in 0/264 framed versus 20/241 (8.3%) SkillX direct-baseline skills.

RQ5 explains why the skills evade detection and probes whether defenses catch them. Each maps to one of the three properties of Section 3.1: RQ1 to sanitization whitewashing, RQ4 to cross-layer promotion, and RQ3 to persistence isolation. SkillX supports the full suite; A2S repeats the extraction, whitewashing, retrieval, downstream-triggering, ablation, and defense phases with the same inputs and judge, using its own skill representation and routing. A small code-generation check (Section 4.10) provides supplementary evidence.

## 六、消融实验

论文未报告独立的消融实验。

## 七、Benchmark 结果与解释

Functional framing yields lower LLM-judge detection and no overtly malicious skill names in this extracted sample.

## 八、总结

We introduced SkillJack, to our knowledge the first attack to show that a self-evolving agent’s own experience-to-skill pipeline can turn poisoned experience into a persistent, reusable skill. In both SkillX and Anything2Skill the pipeline launders the attack and carries it downstream: an LLM judge that flags 98.5% of the raw trajectories flags only 11.4% of the skills distilled from them, those skills are then routed and trigger the intended violation for 56.2% of attack tasks on SkillX and 89.2% on Anything2Skill, and 80% of the triggers survive deletion of the records that produced them. The practical consequence is that clearing memory no longer clears the attack: defenders must track each derived skill back to its source, revoke it when that source is removed, and re-check its behavior at every transformation boundary. Extending this study to more models, independently collected experience, and live execution is the work we leave open.

## References

[1] Z. Chen, Z. Xiang, C. Xiao, D. Song, and B. Li. Agentpoison: Red-teaming llm agents via poisoning memory or knowledge bases. Advances in Neural Information Processing Systems, 37:130185–130213, 2024.

[2] P. Dash, T. Ge, A. Jain, T. Shah, and Z. Shang. From untrusted input to trusted memory: A systematic study of memory poisoning attacks in llm agents. arXiv preprint arXiv:2606.04329, 2026.

[3] E. Debenedetti, J. Zhang, M. Balunovic, L. Beurer-Kellner, M. Fischer, and F. Tramèr. Agentdojo: A dynamic environment to evaluate prompt injection attacks and defenses for llm agents. Advances in neural information processing systems, 37:82895–82920, 2024.

[4] S. Dong, S. Xu, P. He, Y. Li, J. Tang, T. Liu, H. Liu, and Z. Xiang. Memory injection attacks on llm agents via query-only interaction. Advances in Neural Information Processing Systems, 38:46697–46731, 2026.

[5] T. Gu, B. Dolan-Gavitt, and S. Garg. Badnets: Identifying vulnerabilities in the machine learning model supply chain. arXiv preprint arXiv:1708.06733, 2017.

[6] Y. Louck. Securing llm-agent long-term memory against poisoning: Non-malleable, originbound authority with machine-checked guarantees. arXiv preprint arXiv:2606.24322, 2026.

[7] Q. Mi, Z. Ma, M. Yang, H. Li, Y. Wang, H. Zhang, and J. Wang. Skill-pro: Learning reusable skills from experience via non-parametric ppo for llm agents. arXiv preprint arXiv:2602.01869, 2026.

[8] J. Ni, Y. Liu, X. Liu, Y. Sun, M. Zhou, P. Cheng, D. Wang, E. Zhao, X. Jiang, and G. Jiang. Trace2skill: Distill trajectory-local lessons into transferable agent skills. arXiv preprint arXiv:2603.25158, 2026.

[9] T. OWASP. for agentic applications (2026). Owasp top, 10, 10.

[10] Q. Pan, Y. Yang, J. Li, J. Zhou, K. Chen, X. Li, Q. Chen, and L. He. Anything2skill: Compiling external knowledge into reusable skills for agents. arXiv preprint arXiv:2606.09316, 2026.

[11] A. Shafahi, W. R. Huang, M. Najibi, O. Suciu, C. Studer, T. Dumitras, and T. Goldstein. Poison frogs! targeted clean-label poisoning attacks on neural networks. Advances in neural information processing systems, 31, 2018.

[12] S. S. Srivastava and H. He. Memorygraft: Persistent compromise of llm agents via poisoned experience retrieval. arXiv preprint arXiv:2512.16962, 2025.

[13] H. Trivedi, T. Khot, M. Hartmann, R. Manku, V. Dong, E. Li, S. Gupta, A. Sabharwal, and N. Balasubramanian. Appworld: A controllable world of apps and people for benchmarking interactive coding agents. In Proceedings of the 62nd Annual Meeting of the Associationfor Computational Linguistics (Volume 1: Long Papers), pages 16022–16076, 2024.

[14] C. Wang, Z. Yu, X. Xie, W. Yao, R. Fang, S. Qiao, K. Cao, G. Zheng, X. Qi, P. Zhang, et al. Skillx: Automatically constructing skill knowledge bases for agents. arXiv preprint arXiv:2604.04804, 2026.

[15] K. Wang, J. Lou, Z. Zhou, and J. Li. Oep: Poisoning self-evolving llm agents via locally correct but non-transferable experiences. arXiv preprint arXiv:2605.18930, 2026.

[16] Z. Z. Wang, J. Mao, D. Fried, and G. Neubig. Agent workflow memory. arXiv preprint arXiv:2409.07429, 2024.

[17] W. Xu, Z. Liang, K. Mei, H. Gao, J. Tan, and Y. Zhang. A-mem: Agentic memory for llm agents. Advances in Neural Information Processing Systems, 38:17577–17604, 2026.

[18] Y. Yang, J. Li, Q. Pan, B. Zhan, Y. Cai, L. Du, J. Zhou, K. Chen, Q. Chen, X. Li, et al. Autoskill: Experience-driven lifelong learning via skill self-evolution. arXiv preprint arXiv:2603.01145, 2026.

[19] Z. Ying, H. Wang, J. Liu, Q. Zou, A. Liu, J. Yang, Y. Yang, and X. Liu. Agentvisor: Defending llm agents against prompt injection via semantic virtualization. arXiv preprint arXiv:2604.24118, 2026.

[20] Q. Zhan, Z. Liang, Z. Ying, and D. Kang. Injecagent: Benchmarking indirect prompt injections in tool-integrated large language model agents. In Findings of the Association for Computational Linguistics: ACL 2024, pages 10471–10506, 2024.

[21] A. Zhao, D. Huang, Q. Xu, M. Lin, Y.-J. Liu, and G. H

### 在线资源

- [论文：arXiv 2608.03509](https://arxiv.org/abs/2608.03509)
- [代码：GitHub](https://github.com/Tencent/AI-Infra-Guard)
- [PDF源文件](/papers/2608.03509.pdf)
