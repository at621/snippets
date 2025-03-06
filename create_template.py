import pypandoc

markdown_text = """
# Introduction

## Purpose

This section should clearly and concisely define the objectives and intended use of the PD model. The model developer should:

- State the Primary Objectives: Explain why the model is being developed. Is it primarily for regulatory capital calculation (CRR/Basel III), internal risk management, loan pricing, provisioning, stress testing, or a combination of these? Explicitly link the model's purpose to both regulatory requirements and the bank's internal risk appetite.
- Define Model Scope: Clearly indicate that this model is specifically for mortgage exposures. Connect this to the broader business context – why is a dedicated mortgage PD model needed?
- Describe Result Usage: Explain, in detail, how the model's outputs (PD estimates) will be used. Provide specific examples of decisions and processes that will be informed by the model. This should include both regulatory reporting and internal management actions. Go beyond general statements and provide concrete examples (e.g., "The PD estimates will be used as a direct input into the IRB capital calculation under Article [Specific Article] of the CRR," or "The PD estimates will be used by loan officers during the loan origination process to assess borrower risk and inform pricing decisions.").
- Explain the business rationale: Justify why this model is important to the business.

## Range of Application

This section must meticulously define the boundaries of the model's applicability. The model developer should:

- Detail Portfolio Segmentation: Provide a granular description of the segments of the mortgage portfolio covered by the model. Don't just list segmentation criteria; explain why those criteria are chosen. Include:
  - Product Types: Exhaustively list all mortgage product types included (e.g., fixed-rate, variable-rate, interest-only, buy-to-let, etc.). Explain the rationale for including/excluding each type.
  - Geographic Regions: Specify all countries or regions covered. Explain any regional considerations relevant to risk assessment.
  - Borrower Characteristics: Define relevant borrower segments (e.g., prime vs. subprime, first-time buyers, high-net-worth). Justify these distinctions.
  - Loan Characteristics: Describe relevant loan characteristics (e.g., LTV ranges, loan purpose, amortization schedule). Explain how these factors relate to default risk.
- Explicitly State Inclusions and Exclusions: Clearly list any specific loan types, borrower types, or other criteria that are excluded from the model's scope, and provide a concise justification for each exclusion. This is just as important as defining what's included.
- Ensure Consistency: Demonstrate that the defined range of application is consistent with the bank's overall rating system structure and any relevant regulatory requirements. If the bank uses multiple rating systems, explain how this model fits within the broader framework. Reference relevant internal policies.

## Portfolio Overview

This section should provide a high-level, yet informative, summary of the mortgage portfolio. The model developer should:

- Describe Key Attributes: Present a concise overview of the portfolio, including quantitative data where appropriate. Include:
  - Portfolio Size: Total outstanding balance and number of loans. This provides context for the model's importance.
  - Geographic Distribution: Breakdown of the portfolio by region or country, highlighting any concentrations.
  - Collateral Types: Distribution of loans by property type (e.g., single-family homes, apartments, condos).
  - LTV Distribution: A summary of the LTV distribution, perhaps using ranges (e.g., <70%, 70-80%, 80-90%, >90%). This highlights potential risk concentrations.
  - Origination Vintage: Distribution of loan origination dates, showing the age profile of the portfolio.
- Identify Concentration Risks: Explicitly point out any known concentration risks within the portfolio (e.g., geographic concentration in a specific region, a large proportion of loans to a particular borrower segment). Explain why these concentrations are considered risks.
- Highlight Unique Characteristics: Describe any unique or unusual features of the portfolio that might influence model development or calibration. This could include a significant proportion of loans with specific features (e.g., interest-only periods, balloon payments) or a portfolio that is particularly sensitive to certain economic factors.
- Provide context for the later sections: Connect the overview to the model by explaining how these portfolio details will be considered in the later development steps.

## Overview of the Process and Governance

This section should outline the entire model lifecycle and the governance framework surrounding it. The model developer should:

- Describe the Model Lifecycle: Provide a step-by-step description of the entire process, from data collection to ongoing monitoring. This should include:
  - Data Preparation: Briefly describe the steps involved in sourcing, cleaning, and transforming the data.
  - Model Development: Outline the process of selecting risk drivers, choosing a modeling methodology, and building candidate models.
  - Calibration: Explain the approach to estimating PD values.
  - Validation: Describe the independent validation process.
  - Implementation: Explain how the model will be deployed into the bank's systems.
  - Monitoring: Describe the ongoing monitoring and recalibration process.
- Define Responsibilities: Clearly assign roles and responsibilities for each stage of the model lifecycle. Identify specific teams or individuals responsible for:
  - Model Development
  - Model Validation
  - Model Ownership (the business unit responsible)
  - Model Approval (committees or individuals with approval authority)
- Describe the Governance Framework: Explain the controls and procedures in place to ensure model integrity and compliance. This should include:
  - Model Documentation Standards: Specify the requirements for documenting all aspects of the model.
  - Change Management Process: Describe the formal process for approving and implementing any changes to the model.
  - Periodic Review Schedule: Define the frequency of regular model reviews (e.g., annually, or more frequently if needed).
- Regulatory Alignment: Explicitly state that the model development process and governance framework comply with relevant regulatory guidelines, such as the EBA Guidelines on PD estimation, LGD estimation, and treatment of defaulted exposures, and any other applicable regulations (e.g., CRR, Basel III). Reference specific sections of the guidelines where appropriate.

## Role of Expert Judgement

This section must carefully define how and when expert judgment is used in the model development and application process. The model developer should:

- Explain the Complementary Role: Clearly state that expert judgment is used to supplement statistical methods, not to replace them. Emphasize that the model is primarily data-driven.
- Provide Specific Examples: Give concrete examples of where expert judgment might be applied, including:
  - Risk Driver Selection: How expert input can inform the selection or refinement of risk drivers.
  - Model Overrides: Under what circumstances model outputs might be overridden, and what information would justify an override.
  - Calibration Adjustments: How expert views on economic conditions or portfolio-specific risks might lead to adjustments in PD estimates.
  - Handling of missing data: Justify how the expert judgement is used to guide data imputation.
- Document Override Policies: Describe the bank's policies and procedures for applying overrides. This should cover:
  - Justification Requirements: What level of justification is required for an override?
  - Documentation Requirements: How must overrides be documented (e.g., in a dedicated system, with clear rationale and approval records)?
  - Approval Process: Who is authorized to approve overrides?
  - Monitoring and Review: How are overrides monitored and reviewed for appropriateness and potential bias?
- Emphasize Transparency and Consistency: Stress the importance of applying expert judgment in a transparent, consistent, and well-documented manner. Explain how the bank ensures that expert judgment is not applied arbitrarily or inconsistently.
- Provide Justification: Explain how the balance between expert judgement and statistical precision is obtained.

# Reference Dataset

## Data Sources and Data Collection

This section should provide a comprehensive inventory of all data sources used and a detailed description of the data collection process. The model developer should:

- List All Internal Data Sources: Provide a complete list of all internal systems and databases used to obtain data, with a brief description of the type of data obtained from each. Be specific (e.g., "Loan Origination System (LOS) - provides loan-level data including loan amount, interest rate, LTV, origination date, borrower demographics...", "Credit Bureau Data Feed (Experian) - provides borrower credit scores, credit history, and public record information..."). Do not just list system names; describe the relevant data.
- List All External Data Sources: Provide a complete list of all external data sources used, including the name of the data provider and a description of the type of data obtained. Be specific (e.g., "Macroeconomic Data Feed (National Statistical Office) - provides monthly data on national unemployment rates, GDP growth, and inflation...", "Property Price Index (XYZ Real Estate Data) - provides quarterly data on property price changes at the regional level...").
- Describe the Data Collection Process (ETL): Provide a detailed, step-by-step description of the process for extracting, transforming, and loading (ETL) data from the various sources into a unified dataset. This should include:
  - Data Extraction Frequency: How often is data extracted from each source?
  - Data Validation Checks: What checks are performed during the extraction process to ensure data quality (e.g., range checks, consistency checks)?
  - Data Transformation Steps: Describe any transformations applied to the data (e.g., data type conversions, creating derived variables, handling of missing values at this stage). Be specific about the transformations.
  - Data Loading Procedures: Explain how the data is loaded into the development environment.
- Data Governance and Security: Briefly describe the data governance framework in place to ensure data quality, security, and compliance with data privacy regulations.
- Third-party data: Explain how you will ensure the quality and appropriateness of third-party data.

## Segmentation and Representativeness Analysis

This section should explain the rationale for segmentation and the steps taken to ensure data representativeness. The model developer should:

- Explain the Need for Segmentation: Clearly articulate why segmentation is necessary for accurate PD estimation in the context of the mortgage portfolio. Explain that different segments have different risk profiles and that a single, unsegmented model would likely be inaccurate. Reference the concept of homogeneous risk pools.
- Define Segmentation Criteria: List and justify the criteria used for segmentation (e.g., product type, LTV, borrower characteristics, geographic region). Explain why each criterion is relevant to default risk.
- Describe Representativeness Checks: Detail the specific checks that will be performed to ensure that the data used for model development and calibration is representative of each segment and of the overall application portfolio. This should include:
  - Statistical Tests: Specify the statistical tests that will be used (e.g., Kolmogorov-Smirnov, Chi-squared, t-tests, ANOVA) and the purpose of each test. Explain how the results of these tests will be interpreted.
  - Qualitative Assessments: Describe any qualitative assessments that will be performed (e.g., reviewing lending standards, analyzing economic trends).
  - Data Coverage Analysis: Explain how the model developer will ensure sufficient data is available for each segment, especially low-default segments.
- Address Potential Challenges: Acknowledge and discuss potential challenges to representativeness, such as:
  - Changes in Default Definitions: Explain how changes in the definition of default over time will be addressed.
  - Evolving Market Conditions: Explain how the model will account for changes in economic conditions and their impact on borrower behavior.
  - Shifts in Lending Standards: Explain how changes in the bank's lending policies will be addressed.
- Dynamic Segmentation: Discuss if and how the approach will account for the evolution of the segments in the future.
- Document thoroughly all analysis and justifications.

## Analysis of Data Quality and Data Cleansing

This section should detail the rigorous assessment and cleansing of the data. The model developer should:

- Define Data Quality Dimensions: List and define the eight (or however many are used) dimensions of data quality that are assessed. Don't just list them; provide a clear definition of each dimension in the context of this project (e.g., "Accuracy: The degree to which the data correctly reflects the true value of the attribute being measured. For example, the accuracy of the LTV data is assessed by comparing it to appraisal values..."). Common dimensions include Accuracy, Completeness, Consistency, Timeliness, Validity, Uniqueness, Integrity, and Reasonability.
- Describe Assessment Methods: For each data quality dimension, describe the specific methods used to assess data quality. Be concrete (e.g., "Completeness: We calculate the percentage of missing values for each variable. Variables with more than [X]% missing values are flagged for further investigation...", "Accuracy: We compare the reported income data to credit bureau data and flag any discrepancies exceeding [Y]%..."). Provide thresholds where applicable.
- Detail Cleansing Techniques: For each data quality issue identified, describe the specific techniques used to address the issue. Be very specific (e.g., "Missing Values: Missing LTV values are imputed using the median LTV for loans with similar characteristics (product type, geographic region, origination date)...", "Outliers: Outliers in the income data are identified using the interquartile range (IQR) method and are winsorized at the 99th percentile..."). Explain the rationale for each technique.
- Document a Scoring Framework: Explain the thresholds for data quality, and what scores deem the data fit for purpose.
- Provide Justification: Justify the choice of cleansing techniques. Explain why a particular method was chosen over alternatives.
- Document Everything: Emphasize the importance of thoroughly documenting all data quality assessment and cleansing steps, including the methods used, the issues identified, the actions taken, and the rationale for those actions. This documentation is essential for auditability and validation.

## Reference Dataset Development

This section describes the final, cleaned dataset that will be used for model development and calibration. The model developer should:

- Describe the Final Dataset: Provide a comprehensive description of the final, clean dataset. This should include:
  - Data Structure: Explain the organization of the data (e.g., tables, rows, columns).
  - Data Dictionary: State that a comprehensive data dictionary is included in the documentation, defining each variable, its data type, its source, and any transformations applied.
  - Time Period Covered: Specify the start and end dates of the data included in the dataset.
  - Number of Observations: State the total number of observations (loans) in the dataset.
- Explain Segmentation Incorporation: Describe how the segmentation defined in Range of Application is implemented in the reference dataset. This could involve creating separate datasets for each segment or adding segmentation variables to a single dataset.
- Detail Default Event Identification: Clearly explain how historical default events are identified and linked to borrower and loan characteristics. This is the foundation of the PD model. Specify the definition of default used (consistent with regulatory guidelines and internal policies) and how it is operationalized in the data.
- Describe Risk Driver Integration: Explain how the potential risk drivers (to be analyzed in later stages) are integrated into the dataset.
- Emphasize Traceability: Stress that every data point in the reference dataset can be traced back to its original source. This is crucial for auditability and validation.
- Final Data Validation: Confirm that the final reference dataset has undergone a final round of thorough validation to ensure its accuracy, completeness, and consistency before being used for model development.
- Alignment with model scope: Confirm that the dataset contains all data required to meet the model's objective.
- Consistency: Ensure that data definitions are consistent, and defaults are correctly combined with risk drivers.

# Single Factor Analysis

## Differentiation Dataset Creation

This section should clearly define the subset of data used for the initial model building (differentiation) stage. The model developer should:

- Define the Development Sample: Clearly state that this is the subset of data used for model development (identifying risk drivers and building the initial model). This is often referred to as the training dataset.
- Explain Sample Selection Criteria: Describe, in detail, the criteria and methodology used to select the development sample from the overall reference dataset. This could involve:
  - Random Sampling: Explain the process for selecting a random subset.
  - Stratified Sampling: Explain how the sample is stratified to ensure representation of key characteristics (e.g., LTV, borrower type, geographic region).
  - Time-Based Split: Explain if data is split by time (e.g., using older data for development and newer data for validation) and the rationale.
- Justify Default Representation: Explain how the development sample ensures a sufficient number of both defaulted and non-defaulted observations. This is absolutely critical for building a model that can effectively discriminate between good and bad borrowers. If the default rate is low, discuss whether oversampling techniques were considered and, if so, how they were implemented and any potential biases addressed.
- Justify Sample Size: Provide a clear justification for the size of the development sample. Explain how the sample size is deemed sufficient for the complexity of the model, the number of potential risk drivers, and the desired level of statistical power.

## Handling of Missing Values

This section should provide a comprehensive account of how missing data is addressed in the development sample. The model developer should:

- Describe Missing Data Analysis: Present a detailed analysis of the extent and patterns of missing data. This should include:
  - Percentage of Missing Values: Report the percentage of missing values for each variable in the development sample.
  - Missing Data Mechanisms: Discuss the likely reasons for missing data. Determine whether data is likely to be Missing Completely at Random (MCAR), Missing at Random (MAR), or Missing Not at Random (MNAR). Explain the implications of each mechanism.
- Specify MCAR Tests (if applicable): If statistical tests are used to assess MCAR (e.g., Little's MCAR test), describe the tests and their results.
- Detail Imputation Methods: For each variable with missing values, describe the specific imputation method used. Provide a clear and complete explanation of the method, not just its name. Examples:
  - Mean, Median, or Mode Imputation: Explain why the mean, median, or mode was chosen.
  - Regression Imputation: Describe the regression model used to predict missing values (including the dependent and independent variables).
  - Multiple Imputation: Explain the multiple imputation process, including the number of imputations and the software used.
  - K-Nearest Neighbors: Explain the distance measure and choice of K.
- Explain Missing Categories: If separate missing categories are created for variables where missingness itself might be informative, explain the rationale and how these categories are treated in the model.
- Document Business Rules: Describe any business rules used to handle missing values (e.g., assigning a conservative value to a missing LTV based on expert judgment).
- Justify Imputation Choices: Provide a clear justification for the choice of each imputation method. Explain why the chosen method is appropriate for the specific variable and the likely missing data mechanism.
- Address Bias Mitigation: Explain how the chosen methods are designed to minimize bias in the model. Discuss the potential limitations of the imputation methods and how their impact on model performance will be evaluated.

## Creation of the Long List

This section should document the initial set of potential risk drivers considered for the model. The model developer should:

- List All Initial Candidate Variables: Provide a comprehensive list of all potential risk drivers that were initially considered for inclusion in the model. This should be a broad list, drawing from multiple sources.
- Explain Sources of Candidate Variables: Describe the sources used to identify potential risk drivers. This should include:
  - Business Knowledge: Input from experienced loan officers, credit analysts, and other business experts.
  - Literature Review: Findings from academic research and industry publications on mortgage default risk.
  - Regulatory Guidance: Risk drivers mentioned in relevant regulatory guidelines (e.g., EBA Guidelines).
  - Data Availability: Consideration of the variables available in the reference dataset.
- Describe Univariate Exploration: Explain the univariate analysis performed on each candidate variable. This involves examining:
  - Distribution: How were the distributions of each variable examined (e.g., histograms, box plots, density plots)?
  - Summary Statistics: What summary statistics were calculated (e.g., mean, median, standard deviation, percentiles, skewness, kurtosis)?
  - Relationship with Default: How was the relationship between each variable and the default outcome assessed (e.g., calculating default rates for different categories of a categorical variable, calculating default rates for different ranges of a continuous variable, plotting default rates against the variable)?
- Summarize Preliminary Results: Present a summary of the key findings from the univariate analysis, including:
  - Strength of Association with Default: Report measures of association (e.g., correlation coefficients, Information Value, Cramer's V) for each variable.
  - Stability Over Time: Describe how the stability of the relationship between each variable and default was assessed (e.g., comparing relationships across different time periods).
  - Data Coverage: Report the percentage of observations for which each variable is available (non-missing).
- Explain Variable Grouping (if applicable): If any variables were grouped (e.g., creating bins for continuous variables), explain the rationale and methodology for grouping. This should include the criteria used to define the groups and the justification for the chosen number of groups.

## Selection of Risk Drivers

This section should meticulously document the process of selecting risk drivers from the Long List to create the Short List. The model developer should:

- Describe the Transition Process: Clearly explain the process for moving from the initial Long List of candidate variables to the final Short List of risk drivers that will be used in the model.
- Specify Quantitative Criteria: List and define the quantitative criteria used for variable selection. Provide specific thresholds or decision rules where applicable. Examples include:
  - Predictive Power: Specify metrics used (e.g., Information Value, Gini coefficient, AUC, KS statistic) and any thresholds used (e.g., "Variables with an Information Value below 0.02 were excluded.").
  - Statistical Significance: Specify the statistical tests used (e.g., t-tests, chi-squared tests) and the significance level (e.g., p-value < 0.05).
  - Stability: Describe how stability was assessed (e.g., comparing relationships across different time periods) and any criteria used (e.g., "Variables where the relationship with default differed significantly between time periods were excluded.").
  - Multicollinearity: Explain how multicollinearity (high correlation between risk drivers) was assessed (e.g., Variance Inflation Factor - VIF) and any thresholds used (e.g., "Variables with a VIF greater than 5 were excluded.").
- Specify Qualitative Criteria: List and explain the qualitative criteria used for variable selection. Examples include:
  - Business Rationale: Explain how business knowledge and expert judgment were used to ensure that the selected variables have a clear and logical relationship with default risk.
  - Interpretability: Explain how the interpretability of the variables was considered.
  - Data Availability and Quality: Explain how data availability and quality were factored into the selection process.
  - Regulatory Guidance: Explain alignment with regulatory guidance.
- Emphasize Consistency: Stress that the selection process was based on predefined tests and criteria that were applied consistently to all candidate variables.
- Describe Iterative Process (if applicable): If variable selection was an iterative process (involving multiple rounds of analysis and refinement), describe the steps involved.
- Document thoroughly: All steps, criteria and justification must be documented.

## Overview of the Short List

This section should present the final set of risk drivers selected for the model. The model developer should:

- List Final Risk Drivers: Provide a clear and concise list of all risk drivers included in the Short List (the final set of variables to be used in the model).
- Justify Inclusion: For each risk driver on the Short List, provide a brief but clear justification for its inclusion. This should summarize its predictive power, its business rationale, and its consistency with regulatory guidance.
- Highlight Potential Synergy: Discuss any potential interactions or synergies between the selected risk drivers. For example, explain if the combined effect of two or more variables is expected to be more predictive than the individual effects.
- Describe Variable Transformations: Describe any transformations applied to the variables on the Short List (e.g., logarithmic transformations, standardization, binning). Explain the rationale for each transformation.
- Indicate Expected Signs: For each risk driver, indicate the expected direction of the relationship with the probability of default (e.g., "Higher LTV is expected to be associated with a higher PD," "Higher credit score is expected to be associated with a lower PD").

# Multivariate Analysis

## Review of Methodology

This section should justify the choice of modeling technique. The model developer should:

- State the Chosen Approach: Clearly state the selected modeling approach (e.g., logistic regression, survival analysis, decision tree, neural network, etc.).
- Provide Detailed Justification: Offer a comprehensive justification for the chosen approach, explaining why it is appropriate for this specific PD model, the available data, and the bank's needs. This justification should address:
  - Regulatory Expectations: Demonstrate that the chosen approach is consistent with relevant regulatory guidelines (e.g., EBA Guidelines). Reference specific sections of the guidelines, if applicable.
  - Internal Use Cases: Explain how the chosen approach aligns with the intended uses of the model (e.g., capital calculation, loan pricing, risk management). Consider factors like interpretability, ease of implementation, and maintenance.
  - Data Characteristics: Explain how the chosen approach is suitable for the type of data available (e.g., continuous vs. categorical variables, distribution of the default outcome).
  - Model Performance: Provide evidence, if available, that the chosen approach is likely to perform well on this type of data (e.g., based on previous experience, academic research, or pilot studies).
  - Complexity and Interpretability: Justify the choice of model complexity, considering balance between accuracy and explainability.
- Explain Staged Blocks (if applicable): If a staged approach is used (e.g., separate models for different segments or different groups of risk drivers), provide a clear explanation of the rationale and structure of the staged approach.
- Discuss Alternatives Considered: Briefly mention any alternative modeling approaches that were considered and explain why they were rejected. This demonstrates a thorough and thoughtful selection process.

## Developing Model Candidates

This section should document the iterative process of building and refining different model variations. The model developer should:

- Describe the Iterative Process: Explain, in detail, the steps involved in building and refining candidate models. This should be a step-by-step description of the model building process, including:
  - Starting Point: Describe the initial model (e.g., a simple model with only a few key risk drivers).
  - Variable Addition or Removal: Explain how variables were added and removed from the model (e.g., based on statistical significance, business rationale, or performance metrics).
  - Interaction Testing: Describe how potential interactions between variables were explored and tested.
  - Transformation Experiments: Explain any experiments with different transformations of variables (e.g., logarithmic, square root, polynomial).
- Specify Statistical Criteria: List and define the statistical criteria used to evaluate and compare candidate models at each stage of the iterative process. Provide thresholds or decision rules where applicable. Examples include:
  - Goodness-of-Fit: (e.g., Hosmer-Lemeshow test, likelihood ratio test, AIC, BIC).
  - Predictive Power: (e.g., AUC, Gini coefficient, KS statistic).
  - Statistical Significance of Coefficients: (e.g., p-values, Wald test).
  - Stability of Coefficients: How was the stability of coefficients across different model iterations assessed?
- Emphasize Business Reasoning: Stress the importance of incorporating business knowledge and expert judgment throughout the model development process. Explain how expert input was used to:
  - Ensure the model makes intuitive sense.
  - Avoid overfitting to the development data.
  - Consider the practical implications of the model.
- Discuss Model Complexity: Explain how the balance between model complexity and interpretability was considered. A simpler, more interpretable model is often preferred, even if it sacrifices a small amount of predictive power.
- Document Each Iteration: Keep a detailed record of each model iteration, including the variables included, the transformations applied, the statistical criteria, and the rationale for any changes made.
- Software used: Document which software was used for developing the models.

## Review of Model Candidates

This section should detail the thorough evaluation of the candidate models. The model developer should:

- Describe Performance Checks: Explain, in detail, the checks performed to evaluate the performance of each candidate model. This should include:
  - In-Sample Performance: How was the model's performance evaluated on the development data (the data used to build the model)?
  - Out-of-Sample Performance: How was the model's performance evaluated on a holdout sample (data not used for model development)? This is crucial for assessing the model's ability to generalize to new data. Explain the process for creating the holdout sample.
  - Stability: How was the stability of model coefficients and performance over time assessed?
- Detail Stability Checks: Describe specific checks for model stability and overfitting (e.g., comparing coefficients across different subsamples, examining learning curves).
- Explain Interpretability Checks: Explain how the interpretability of each candidate model was assessed. This should involve:
  - Examining Coefficient Signs and Magnitudes: Were the signs and magnitudes of the coefficients consistent with business expectations?
  - Assessing Explanatory Power: Could the model be easily explained to stakeholders (e.g., loan officers, senior management, regulators)?
- Address Overfitting or Underfitting: Explicitly discuss how the risks of overfitting and underfitting were addressed during the model review process.
- Define Comparison Metrics: Clearly list and define the metrics used to compare candidate models (e.g., AUC, Gini, KS statistic, Hosmer-Lemeshow test). Explain why these metrics were chosen.
- State Selection Criteria: Clearly state the criteria used to select the final model from among the candidate models. Explain how trade-offs between performance, stability, and interpretability were considered.
- Document All Results: Thoroughly document the results of all performance, stability, and interpretability checks for each candidate model.

## Overview of the Final Differentiation Model

This section provides a comprehensive description of the final selected model. The model developer should:

- Describe Model Architecture: Provide a complete and detailed description of the final model, including:
  - Model Type: (e.g., logistic regression).
  - Variables: List all variables included in the final model.
  - Coefficients: Report the estimated coefficients for each variable.
  - Functional Form: Provide the full equation for the model (e.g., the equation for a logistic regression model, including the intercept and all coefficients).
- Explain Scoring or Weighting: If the model produces a score, explain precisely how the score is calculated from the input variables and how the score relates to the probability of default.
- Detail Variable Transformations: Describe any transformations applied to the variables in the final model (e.g., logarithmic transformations, standardization, binning). Explain the rationale for each transformation.
- Explain Interactions: If any interaction terms are included in the model, explain their meaning and rationale.
- Summarize Validation Results: Summarize the key validation results for the final model (in-sample performance, out-of-sample performance, stability). This is a preliminary summary; more detailed validation will be documented elsewhere.
- Report Relevant Metrics: Report the key performance metrics for the final model (e.g., AUC, Gini, KS statistic, Hosmer-Lemeshow test) on both the development and holdout samples.

## Model Testing

This section outlines the initial testing performed on the final, differentiated (but not yet calibrated) model. The model developer should:

- Describe Preliminary Back-testing: Explain the preliminary back-testing performed to assess the model's discriminatory power and stability before calibration. This is distinct from the more comprehensive validation performed later.
- Detail Back-testing Methodology: Describe the specific back-testing methodology used. This should include:
  - Data Used: Specify the dataset used for back-testing (e.g., holdout sample, a separate historical dataset).
  - Performance Metrics: List and define the performance metrics used (e.g., AUC, Gini, KS statistic). Explain why these metrics are appropriate.
  - Comparison Methods: Explain how predicted probabilities of default (or scores) were compared to actual observed default rates. This might involve grouping observations into risk buckets and comparing predicted vs. actual default rates within each bucket.
  - Calibration Assessment (pre-calibration): Even though this is before formal calibration, assess how well the relative ordering of predicted PDs aligns with observed default rates.
- Demonstrate Rating Philosophy Alignment: Explain how the preliminary back-testing results are consistent with the chosen rating philosophy (Point-in-Time, Through-the-Cycle, or Hybrid). For example, a PIT model should show greater variation in predicted PDs over time than a TTC model.
- Confirm Business Expectations: Discuss whether the model's results align with business expectations and expert judgment. Are there any unexpected patterns or anomalies?
- Acknowledge Limitations: Acknowledge any limitations of the preliminary back-testing (e.g., limited historical data, potential for changes in economic conditions, the fact that the model is not yet calibrated).
- Outline Further Validation: Clearly state that this is preliminary testing and that more comprehensive validation will be performed by an independent validation team (and documented separately).

# Model Calibration

## Pooling

This section explains how exposures are grouped for calibration. The model developer should:

- Explain the Rationale for Pooling: Clearly explain why pooling is used (or not used). Pooling is typically used to improve the stability of PD estimates, especially for segments with limited historical default data.
- Describe Pooling Criteria: If pooling is used, describe the specific criteria used to group exposures into pools. This might be based on:
  - Risk Grades: Grouping exposures assigned to the same risk grade.
  - Risk Drivers: Grouping exposures with similar values for key risk drivers (e.g., LTV, credit score).
  - Model Scores: Grouping exposures with similar model-predicted scores (or score ranges).
- Justify Homogeneity: Explain how the pooling criteria ensure that exposures within each pool are reasonably homogeneous in terms of risk.
- Explain PD Derivation: Explain precisely how the final PD is derived for each pool. This typically involves calculating a weighted average of the observed default rates for the exposures within the pool.
- Key drivers: List the key drivers considered.

## Merging Application and Portfolio Scores

This section should explain how the scores from the Application model and Portfolio model are merged for calibration purposes. The model developer should:

- Explain the Dual Model Approach: Clearly describe why separate models are used for new applications and existing customers. Detail the differences in available information, risk drivers, and predictive power between the two models.
- Document Score Comparability Analysis: Explain the analysis performed to ensure scores from both models are comparable before merging. This might include:
  - Distributional Analysis: Comparing the distributions of scores across both models to identify any systematic differences.
  - Correlation Analysis: Assessing how well scores from both models correlate for customers who have both application and portfolio scores.
  - Default Rate Analysis: Comparing how well similar scores from each model predict similar default rates.
- Detail the Merging Methodology: Describe the specific methodology used to combine the two scoring systems, such as:
  - Score Transformation: If scores are transformed to a common scale, explain the transformation method and rationale.
  - Weighted Average: If a weighted average of scores is used, explain how weights are determined.
  - Score Mapping: If scores from one model are mapped to another, explain the mapping procedure.
- Explain Score Migration Handling: Describe how customers migrating from application to portfolio scoring are handled, including any transition period or blending of scores.
- Address Point-in-Time vs Through-the-Cycle Considerations: If the application and portfolio models have different rating philosophies (PIT vs TTC), explain how these differences are reconciled in the merged scoring approach.
- Document Validation of Merged Approach: Summarize the validation performed to ensure the merged scoring system maintains predictive power and is calibrated appropriately.
- Outline Governance and Controls: Describe the governance framework for maintaining and updating the merged scoring system over time.

## Calibration Dataset Creation

This section describes the dataset used specifically for calibration. The model developer should:

- Describe the Final Dataset: Provide a detailed description of the dataset used for calibrating the PD estimates. This may be a subset of the reference dataset or a separate dataset.
- Specify Data Sources: Clearly identify the sources of the data used for calibration.
- Indicate Time Period: Specify the time period covered by the calibration data.
- Explain Handling of Overrides or Special Cases: Explain how any overrides or special cases (e.g., loans with manual PD adjustments) are handled in the calibration dataset. Are they included, excluded, or treated separately? Justify the approach.
- Describe Pooling or Smoothing (if applicable): If any pooling or smoothing techniques are used to improve the stability of PD estimates (especially for low-default segments), describe the techniques in detail and provide a justification.
- Confirm Data Validation: Reiterate that the calibration dataset has undergone thorough validation to ensure its accuracy, completeness, and consistency.

## Rating Philosophy

This section reiterates and justifies the chosen rating philosophy. The model developer should:

- State the Chosen Approach: Clearly state the chosen rating philosophy: Point-in-Time (PIT), Through-the-Cycle (TTC), or Hybrid.
- Provide Detailed Justification: Provide a comprehensive justification for the chosen approach, explaining why it is appropriate for this specific model, the mortgage portfolio, and the bank's intended uses of the PD estimates. This justification should consider:
  - Internal Uses: How does the rating philosophy align with the bank's needs for pricing, provisioning, stress testing, and other internal risk management activities?
  - Regulatory Requirements: Demonstrate that the chosen approach is consistent with relevant regulatory guidelines (e.g., EBA Guidelines). Reference specific sections.
  - Portfolio Characteristics: How does the rating philosophy reflect the characteristics of the mortgage portfolio (e.g., its sensitivity to economic cycles)?
- Explain Alignment: Explain how the chosen rating philosophy is consistent with the calibration methodology and the data used for calibration.
- Emphasize Consistency: Stress the importance of consistently applying the chosen rating philosophy throughout the model's lifecycle.

## Calculation of Long Run Average Default Rates

This section details the calculation of the long-run average (LRA) default rates, a key input to calibration. The model developer should:

- Describe the Aggregation Method: Provide a detailed description of the method used to aggregate historical default rates. This is typically a weighted average of one-year default rates. Explain:
  - Arithmetic vs. Weighted Average: State whether a simple arithmetic average or a weighted average is used. If a weighted average is used, fully explain the weighting scheme and the rationale.
  - One-Year Default Rate Calculation: Explain precisely how the one-year default rates are calculated (numerator and denominator). Reference the definition of default.
- Specify the Observation Period: Clearly state the historical observation period used for calculating the LRA default rate. Justify the choice of this period, demonstrating that it is sufficiently long to cover a range of economic conditions, including both good and bad years. Reference the EBA Guidelines (minimum 5 years, but often longer).
- Explain Bad Years and Good Years Identification: Explain how bad years (periods of high default rates) and good years (periods of low default rates) are identified. This might involve using macroeconomic indicators (e.g., GDP growth, unemployment, interest rates). Provide specific criteria or thresholds.
- Detail Any Adjustments: Describe any adjustments made to the historical default rates. Justify each adjustment thoroughly. Examples include adjustments for:
  - Changes in the definition of default.
  - Changes in lending standards.
  - Expected future economic conditions (if moving towards a PIT approach).
- Document All Steps: Provide comprehensive documentation of all steps in the calculation of the LRA default rate, including the data used, the aggregation method, the weighting scheme (if applicable), and any adjustments made. This documentation should be clear, concise, and auditable.
- Representativeness: Explain how the observation period is representative of the long run.

## Model Testing

This section describes the testing of the calibrated model. The model developer should:

- Reassess Post-Calibration Accuracy: Explain that the model's predictive accuracy is reassessed after calibration to ensure that the calibration process has not distorted the model's ability to discriminate between good and bad borrowers.
- Perform Calibration Specific Tests: Conduct specific tests to assess the calibration quality (e.g., Hosmer-Lemeshow).
- Report Performance Metrics: Report the key performance metrics (e.g., AUC, Gini, KS statistic) on the calibration dataset after calibration.
- Verify Default Rate Alignment: Cross-check that the calibrated PD estimates are aligned with the calculated long-run average default rates (and any adjustments made for economic conditions or other factors). Any significant deviations should be investigated and justified.
- Compare Pre- and Post-Calibration Performance: Compare the model's performance before and after calibration to assess the impact of the calibration process. Calibration should improve the accuracy of PD estimates without significantly degrading the model's discriminatory power.
- Assess Stability: Assess the stability of the calibrated PD estimates over time.

# Deficiencies and Margin of Conservatism

## Identification of Deficiencies

This section outlines the process for identifying and categorizing model weaknesses. The model developer should:

- Describe the Comprehensive Review Process: Explain the systematic process for identifying potential deficiencies in the model's data, methodology, and implementation. This should be a proactive and ongoing process.
- List Potential Data Deficiencies: Provide examples of potential data deficiencies that would be flagged. This should include, but not be limited to:
  - Missing data
  - Inaccurate data
  - Biased data
  - Non-representative data
  - Outdated data
  - Data inconsistencies
- List Potential Methodology Deficiencies: Provide examples of potential methodological deficiencies. This could include:
  - Inappropriate modeling technique
  - Incorrect variable selection
  - Overfitting or underfitting
  - Incorrect functional form
  - Inadequate calibration
  - Violation of model assumptions
- List Potential Implementation Deficiencies: Provide examples of potential implementation deficiencies. This might include:
  - Errors in coding the model in the IT systems
  - Incorrect data feeds
  - Inconsistent application of the model across different business units
- Categorize Deficiencies: Explain how identified deficiencies are categorized, typically using categories like those suggested by the EBA Guidelines (Category A: data and methodological deficiencies; Category B: changes in underwriting standards, risk appetite, etc.; Category C: general estimation error). Provide clear definitions of each category.
- Data Quality Checks: Describe the specific data quality checks that are systematically performed.

## Appropriate Adjustments

This section explains how identified deficiencies are addressed before applying a Margin of Conservatism. The model developer should:

- Explain Bias Correction: Describe the methodologies used to correct for any identified biases in the model stemming from the deficiencies. The goal is to get to a best estimate before adding a Margin of Conservatism.
- Provide Examples of Adjustments: Give concrete examples of adjustments that might be made. This could include:
  - Adjusting data (e.g., correcting errors, imputing missing values using more sophisticated methods).
  - Refining model assumptions.
  - Re-estimating model parameters.
  - Changing the model specification (e.g., adding or removing variables).
- Justification and Documentation: Emphasize the need to thoroughly justify and document every adjustment made. This documentation should include:
  - The specific deficiency being addressed.
  - The adjustment made.
  - The rationale for the adjustment.
  - The impact of the adjustment on the PD estimates.
  - Evidence that it results in a best estimate
- Consistency: Ensure that adjustments are consistent with best practices and regulatory guidance.
- Link to Deficiencies: Clearly link each adjustment to a specific, identified deficiency.

## Margin of Conservatism

This section details the application of the Margin of Conservatism (MoC). The model developer should:

- Explain the Purpose of MoC: Clearly explain that the MoC is added to the best estimate PD to account for remaining uncertainty and potential errors that cannot be fully addressed through adjustments. It is a buffer against model risk.
- Describe the Framework: Describe the bank's framework for quantifying and applying the MoC. This framework should be consistent with regulatory guidelines (e.g., EBA Guidelines).
- Categorize MoC: Explain how the MoC is categorized, typically following the categories of deficiencies (Category A, B, and C, as described in Identification of Deficiencies).
- Quantify MoC: Explain, in detail, the methodologies used to quantify the MoC for each category of deficiency. This is a critical step and should be described thoroughly. Examples might include:
  - Category A (Data and Methodological Deficiencies): Quantifying the potential impact of remaining data limitations or methodological weaknesses on the PD estimates. This might involve sensitivity analysis or expert judgment.
  - Category B (Changes in Underwriting Standards, etc.): Quantifying the potential impact of changes in underwriting standards, risk appetite, collection and recovery policies, or other factors that are not fully reflected in the historical data.
  - Category C (General Estimation Error): Quantifying the inherent uncertainty in the statistical estimation process. This might involve using confidence intervals or other statistical measures of uncertainty.
- Document Aggregation: Explain how the MoC components for different categories are aggregated to arrive at a final MoC.
- Justification and Documentation: Thoroughly justify and document the MoC calculation for each category and in aggregate. This documentation should include:
  - The specific deficiencies or uncertainties being addressed.
  - The methodology used to quantify the MoC.
  - The rationale for the chosen methodology.
  - The resulting MoC value.
- Ensure Conservatism, but Avoid Excessiveness: Confirm that the MoC does not lower risk estimates, and is proportionate to the identified risks.
- Regular Review: Explain that the MoC is regularly reviewed and updated as needed to reflect changes in the model, the data, or the economic environment.

# Implementation and Use

## Implementation

This section describes the deployment of the model into the bank's IT systems. The model developer should:

- Describe IT Systems: Specify the IT systems into which the model is implemented (e.g., loan origination system, credit risk engine, capital calculation system).
- Detail Implementation Process: Describe the process for implementing the model, including:
  - Code Translation: How is the model code translated into the production environment?
  - Testing: What testing is performed to ensure that the model is implemented correctly and produces the expected results?
  - Data Integration: How is the model integrated with the necessary data feeds?
  - User Interface: How will users (e.g., loan officers, credit analysts) interact with the model?
- Document Version Control: Describe the version control procedures in place to track changes to the model code and ensure that the correct version is being used.
- Ensure Data Security: Briefly describe the data security measures in place to protect the model and the data it uses.

## Integration into Everyday Processes

This section explains how the model is used in the bank's day-to-day operations. The model developer should:

- Describe Use in Loan Origination: Explain how the model's PD estimates are used during the loan origination process to assess borrower risk, inform pricing decisions, and set credit limits.
- Describe Use in Credit Risk Management: Explain how the model is used for ongoing credit risk management, including portfolio monitoring, risk reporting, and stress testing.
- Describe Use in Capital Calculation: Explain how the model's PD estimates are used as inputs to the IRB capital calculation. Reference the specific regulatory formulas and parameters.
- Describe Use in Provisioning: Explain how the PD estimates inform the bank's provisioning process.
- Automation: Describe how the model is automated, and which steps, if any, require human intervention.
- System Updates: Explain how the model's outputs are integrated into other IT systems (e.g., reporting systems, management information systems).

## User Training and Documentation

This section describes the training and documentation provided to users of the model. The model developer should:

- Describe User Training: Describe the training provided to all users of the model (e.g., loan officers, credit analysts, risk managers). This should cover:
  - Model Overview: An explanation of the model's purpose, methodology, and outputs.
  - Model Inputs: An explanation of the data used by the model.
  - Model Interpretation: How to interpret the model's PD estimates and other outputs.
  - Model Limitations: A clear explanation of the model's limitations.
  - Override Procedures: Training on the bank's policies and procedures for overriding model outputs (if applicable).
- Detail Model Documentation: Describe the comprehensive documentation provided for the model. This should include:
  - Model Development Report: This document itself.
  - Technical Documentation: Detailed technical specifications of the model, including the model equation, variable definitions, and calibration methodology.
  - User Manual: A guide for users on how to use the model and interpret its outputs.
  - Validation Report: The independent validation team's report on the model.
  - Override Procedures: Documentation of the bank's policies and procedures for overriding model outputs.
- Ensure Accessibility: Explain how the documentation is made accessible to all relevant users.
- Regular Updates: State that all training materials and documentation are kept up to date.
"""


output = pypandoc.convert_text(
    markdown_text,        # The string above
    'docx',               # Output format
    format='md',          # Input format is Markdown
    outputfile='output16.docx',
    extra_args=['--reference-doc=template_fix.docx']
)
