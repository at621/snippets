# Prompt: Multivariate Analysis Methodology Document (PD IRB)

---

## INSTRUCTION

You are writing a chapter of a bank's internal model development methodology. The chapter covers **multivariate analysis** within the PD (Probability of Default) model development framework under the IRB (Internal Ratings-Based) approach.

This is a **bank-wide methodological standard** — it is not a model-specific development report. It prescribes the process, criteria, and decision rules that any PD model development team within the bank must follow when performing multivariate analysis. It will be reviewed by internal model validation, internal audit, and external supervisors (ECB/SSM or equivalent national competent authority).

---

## REGULATORY FOUNDATION

The document must be grounded in and make explicit reference to:

- **EBA Guidelines on PD estimation, LGD estimation, and the treatment of defaulted exposures (EBA/GL/2017/16)**, in particular the sections on risk differentiation (§§108–109), data requirements (§§73–75), and the expectation that risk drivers have an appropriate and economically intuitive effect on risk.
- **ECB Guide to Internal Models (consolidated version)**, in particular §4.3.2 on model development, variable selection, the balance between statistical and judgmental criteria, the expectation that alternatives are considered, and the principle that models should be sufficiently simple to be understood, validated, and monitored.

References to specific regulatory paragraphs should be woven naturally into the text where the relevant requirement is discussed — not collected in a separate references section. The tone should convey that the methodology *implements* these regulatory expectations, not merely that it is *aware* of them.

---

## SCOPE AND BOUNDARIES

The chapter covers the multivariate analysis stage only. It begins where univariate analysis and WoE (Weight of Evidence) transformation have been completed, and it ends with a final model specification (functional form, variable set, estimated coefficients) ready to be passed to the calibration stage.

The following topics are explicitly **out of scope** and must not be duplicated from other methodology chapters:
- Data preparation, default definition, observation/outcome window design
- Univariate variable screening and WoE transformation
- PD calibration (mapping scores to PDs, long-run average calibration)
- Out-of-sample and out-of-time validation
- Ongoing model monitoring and performance review
- Model governance, approval workflows, and model risk management

Where a boundary with an adjacent chapter is relevant (e.g., the inputs received from univariate analysis, or the outputs handed to calibration), a brief cross-reference is appropriate, but the substance belongs in the other chapter.

---

## DOCUMENT STRUCTURE

The chapter must contain the following seven sections, in this order:

### Section 1: Scope and Prerequisites
Brief framing of what this chapter covers within the broader model development methodology. Define the boundary: this chapter begins after univariate analysis and WoE transformation and ends with a final model specification ready for calibration. Summarize the expected inputs: the candidate variable longlist with confirmed univariate discriminatory power (IV thresholds per EBA GL/2017/16 §108–109 on risk differentiation), WoE-transformed variables, the defined development sample with the default definition and observation/outcome windows already established. Reference the ECB Guide to Internal Models §4.3.2 on expectations for the variable selection and model specification process. Keep this section short — it is a handshake with the preceding chapter, not a repetition of it.

### Section 2: Correlation Analysis and Multicollinearity Assessment
The first analytical step of the multivariate stage. Pairwise correlation analysis across all candidate variables — Pearson and/or Spearman depending on variable characteristics — with explicit thresholds for flagging highly correlated pairs. When two variables are highly correlated, describe the decision rule for which one is retained (typically: higher univariate IV, better economic interpretability, better population coverage). Then move to formal multicollinearity diagnostics: Variance Inflation Factor (VIF) computed on the candidate set, with the threshold used (commonly 5 or 10) and the rationale for the chosen threshold. Reference EBA GL/2017/16 §109 on the expectation that risk drivers are not redundant and each contributes independently to risk differentiation. Discuss how clustering of variables by risk dimension (e.g., leverage, profitability, liquidity) is used to ensure the model captures distinct aspects of obligor risk rather than multiple proxies for the same factor. Document the reduced variable set that exits this section.

### Section 3: Variable Selection Methodology
The core analytical engine of the chapter. Describe the approach to selecting variable combinations — typically a combination of statistical procedures and expert judgment, consistent with ECB Guide §4.3.2 on the balance between statistical and judgmental criteria. Cover the statistical selection procedure: stepwise regression (forward, backward, or bidirectional) with stated entry/removal criteria (p-value thresholds or information criteria such as AIC/BIC). Address the known limitations of stepwise approaches — instability, path dependence, overfitting — and the mitigants applied (e.g., bootstrap stability analysis: running the selection procedure on resampled datasets and retaining only variables selected in a defined proportion of iterations). Define the hard constraints applied at each step: coefficient sign must be economically intuitive (per EBA GL/2017/16 §109 — risk drivers must have an "appropriate effect" on risk differentiation), all retained variables must be statistically significant at a defined confidence level, VIF must remain below threshold after each variable addition. Describe how expert judgment is applied: override rules when a statistically selected variable lacks economic rationale, or when a variable with marginal statistical contribution is retained for economic or regulatory reasons.

### Section 4: Candidate Model Development
This section addresses the requirement to develop multiple distinct candidate model specifications. The purpose is to demonstrate that the model space has been genuinely explored and that the final specification is a deliberate, justified choice rather than the output of a single mechanical procedure. Critically, candidate models must be meaningfully different from one another — they should represent different economic narratives about what drives default risk, not minor permutations of the same core specification. For example, one candidate might emphasize leverage and debt service capacity, while another emphasizes profitability trends and liquidity; a third might combine elements differently or include a sector-specific variable absent from the others. Candidates that differ only by swapping one marginally significant variable, or that share the majority of their variable set and produce near-identical score distributions, do not constitute genuine alternatives and should not be presented as such. Define the minimum differentiation criteria: candidates should differ in at least a meaningful subset of their variable composition, produce observably different rank-orderings of obligors (measurable via rank correlation of predicted scores), and ideally reflect different hypotheses about the economic drivers of default in the portfolio. State how many candidate models are expected (a minimum of three is a reasonable starting point, though this depends on portfolio complexity and the breadth of the available variable set). Reference ECB Guide §4.3.2 and EBA GL/2017/16 §109 on the expectation that model choice is well-reasoned and that alternatives have been considered. Describe how candidates are generated: by varying the variable selection procedure (e.g., forward vs. backward stepwise, different entry thresholds), by imposing different expert constraints (e.g., forcing inclusion of a particular risk dimension), or by exploring different variable groupings from the risk dimension clusters identified in Section 2.

### Section 5: Candidate Model Selection
This section defines the structured framework for selecting the preferred model from the candidates generated in Section 4. The selection must not be based on a single criterion; rather, it requires a multi-dimensional assessment that balances competing objectives. Define the following evaluation dimensions, and for each, state how it is measured and what constitutes acceptable performance:

- **Discriminatory power**: AUROC/Gini on the development sample, and critically, on the holdout or out-of-time sample if available at this stage. A model with marginally lower in-sample Gini but stronger out-of-sample performance is generally preferable. State the minimum acceptable Gini threshold.
- **Statistical robustness**: significance of all coefficients, absence of multicollinearity, correct coefficient signs, goodness-of-fit. Any candidate failing hard constraints is eliminated regardless of other performance.
- **Stability**: coefficient stability across bootstrap resamples or rolling estimation windows, consistency of variable selection under perturbation, Population Stability Index of score distributions across time periods.
- **Parsimony**: fewer variables are preferred, all else being roughly equal. Information criteria (AIC/BIC) can formalize this trade-off. Reference ECB Guide §4.3.2 on the expectation that models are sufficiently simple.
- **Economic interpretability**: the retained variable set should tell a coherent story about what drives default in the portfolio.
- **Portfolio coverage and data quality**: variables must have sufficient population rates, reliable data sourcing, and reasonable expectations of continued availability.

Describe how these dimensions are synthesized into a selection decision (weighted scorecard, hierarchical elimination, or narrative justification). The key regulatory expectation is that the decision is transparent, documented, and not reducible to "highest Gini." Present the comparison as a structured table. Identify the preferred model and the runner-up with explicit rationale.

### Section 6: Final Model Estimation and In-Sample Diagnostics
Full estimation and diagnostic assessment of the preferred model (and the runner-up for comparative purposes). State the model form — logistic regression with log-odds as a linear function of WoE-transformed risk drivers — and the estimation method (maximum likelihood). Describe the interpretation of coefficients: in a WoE-based framework, all coefficients should be positive and roughly similar in magnitude absent strong reasons otherwise. Discuss practical estimation issues relevant to IRB portfolios: convergence, complete or quasi-complete separation (particularly in low-default portfolios — reference EBA GL/2017/16 §§73–75), and when penalized estimation methods may be warranted. Address the principle of parsimony per ECB Guide §4.3.2. In-sample diagnostics must include: AUROC/Gini (referencing EBA GL/2017/16 §108), Kolmogorov-Smirnov statistic, Cumulative Accuracy Profile, Hosmer-Lemeshow goodness-of-fit test. Residual diagnostics: deviance residuals, influential observations via Cook's distance or DFBETAS. Sensitivity analysis: jackknife variable removal to confirm no single variable disproportionately drives the result.

### Section 7: Final Model Specification and Rationale
Consolidation of the multivariate analysis results into the formal model specification that passes to the calibration stage. Present the final coefficient table with confidence intervals. Summarize, for each retained variable, the economic rationale for inclusion and the key statistical evidence (IV, coefficient, p-value, contribution to Gini). Document the variables that were excluded and the reason for exclusion. Present the comparison against runner-up candidate models and the rationale for preferring the chosen specification, cross-referencing the selection framework from Section 5. State any known limitations or sensitivities identified during the analysis. This section produces the definitive specification — the exact functional form and variable set — that all downstream steps work from.

---

## STYLE AND TONE

- **Register**: Formal technical methodology. This is an internal regulatory document, not a textbook, not a slide deck, and not a model development report for a specific portfolio. It prescribes what must be done, not what was done.
- **Voice**: Use prescriptive language throughout. "The development team shall...", "Variables must satisfy...", "The following criteria apply...". Avoid passive constructions where they obscure who is responsible for an action.
- **Terminology**: Use standard IRB and credit risk modelling terminology without defining basic concepts (the audience is model developers and validators who know what logistic regression, WoE, and Gini coefficients are). Do define any bank-specific terms or thresholds that are being established by this methodology.
- **Regulatory references**: Cite specific EBA GL and ECB Guide paragraphs inline where the methodology implements a regulatory requirement. Do not over-cite — reference the regulation where it matters, not on every sentence.
- **No code**: This document is software-agnostic. Do not include code snippets, pseudocode, or references to specific software packages. Describe procedures in statistical and methodological terms.
- **No invented examples**: Do not fabricate illustrative datasets, variable names, or numerical results. Where an example would be helpful, describe it generically (e.g., "a candidate model emphasizing leverage and coverage ratios versus one emphasizing profitability and liquidity metrics") rather than inventing specific numbers.
- **Equations**: Use equations where they add precision (e.g., the logistic regression model form, the VIF formula, the Gini coefficient definition). Do not use equations gratuitously.
- **Cross-references**: Where the methodology depends on or hands off to another chapter (univariate analysis, calibration, validation), use a brief cross-reference rather than restating the other chapter's content.

---

## LENGTH AND FORMATTING

- **Target length**: Approximately 4,000–5,000 words across all seven sections, equivalent to roughly 10–12 pages in a standard Word document with normal margins and 11pt font. Sections 3, 4, and 5 should be the longest (they carry the most methodological substance). Sections 1 and 7 should be the shortest.
- **Section headers**: Use numbered section headers (1, 2, 3, ...) matching the structure above. Use sub-headers within sections where needed for readability, but do not over-fragment — this is a prose document, not a checklist.
- **Paragraphs**: Write in full paragraphs. Bullet points may be used sparingly for lists of criteria or diagnostic tests where a paragraph would be awkward, but the default mode is prose.
- **Tables**: Do not include actual data tables, but describe where tables should appear in practice (e.g., "The comparison of candidate models shall be presented in a structured table showing each candidate's performance across all evaluation dimensions").
- **Formatting**: The document will be formatted as a Word document. Use heading styles consistently. No colors, no graphics, no decorative formatting.

---

## QUALITY CRITERIA

The output will be evaluated on the following dimensions:

1. **Regulatory alignment**: Does the document faithfully implement the expectations of EBA GL/2017/16 and the ECB Guide to Internal Models? Are references accurate and appropriately placed?
2. **Internal consistency**: Do later sections build on earlier ones without contradiction? Does the selection framework in Section 5 align with the candidate generation approach in Section 4? Do the diagnostics in Section 6 correspond to the evaluation criteria in Section 5?
3. **Appropriate specificity**: Does the document prescribe concrete thresholds, criteria, and decision rules (not just "consider multicollinearity" but "apply a VIF threshold of X")? At the same time, does it avoid being so rigid that it cannot accommodate different portfolio types?
4. **Sustained quality**: Is the writing quality, depth, and precision consistent from Section 1 through Section 7, or does it degrade in later sections?
5. **Correct scoping**: Does the document stay within the multivariate analysis boundary, or does it drift into calibration, validation, or data preparation?
6. **Professional tone**: Does it read like a document written by a senior credit risk modelling team for a regulated European bank?

---

Now write the full chapter.
