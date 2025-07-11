# Ideation: Credit Risk Ontology Design Document

## Overview
This document outlines the design for a comprehensive Credit Risk Ontology based on EU Capital Requirements Regulation (CRR) 575/2013, following FIBO patterns and conventions.
The examples are illustrative and the list of objects is not comprehensive. 

## Key Design Principles
- **Alignment with FIBO**: Extends and reuses FIBO classes and properties where applicable
- **CRR Compliance**: Covers all aspects of credit risk as defined in CRR Title II
- **Facility vs Obligor**: Maintains clear distinction between counterparty-level and transaction-level concepts
- **Multi-Approach Support**: Accommodates Standardised (STA), Foundation IRB (FIRB), and Advanced IRB (AIRB) approaches

## Total Scope
- **Estimated Classes**: ~300+
- **Core Modules**: 12
- **Regulatory Articles Covered**: 107-239

---

## 1. Credit Risk Approaches

### 1.1 CreditRiskApproach (abstract)
**Properties:**
- `cmns-rga:isGovernedBy` → CRRRegulation
- `fibo-fnd-law-cor:isConferredBy` → CompetentAuthority
- `cmns-dt:hasEffectiveDate` → Date
- `cmns-doc:hasDescription` → Approach description

**Metadata:**
- Label: "credit risk approach"
- Definition: "Method for calculating credit risk capital requirements under CRR"
- Source: "CRR Article 107"

### 1.2 StandardisedApproach
**Properties:**
- `uses` → ExternalCreditAssessment
- `appliesRiskWeights` → StandardisedRiskWeightTable
- `allowsCRM` → StandardisedCRMRules

**Metadata:**
- Label: "standardised approach"
- Definition: "Credit risk approach using fixed risk weights"
- Source: "CRR Articles 111-141"

### 1.3 InternalRatingsBasedApproach (abstract)
**Properties:**
- `requiresPermission` → IRBPermission
- `hasRatingSystem` → InternalRatingSystem
- `hasValidationProcess` → ValidationFramework

### 1.4 FoundationIRB
**Properties:**
- `estimatesOnly` → ProbabilityOfDefault
- `usesSupervisory` → [LGD, EAD, Maturity]
- `excludes` → RetailExposures

**Metadata:**
- Label: "foundation IRB approach"
- Abbreviation: "FIRB"
- Source: "CRR Article 143"

### 1.5 AdvancedIRB
**Properties:**
- `estimatesAll` → [PD, LGD, EAD, Maturity]
- `requiresApproval` → AdvancedIRBPermission
- `hasBacktestingRequirement` → BacktestingProcess

**Metadata:**
- Label: "advanced IRB approach"
- Abbreviation: "AIRB"

---

## 2. Credit Risk Entities

### 2.1 Obligor (extends cmns-org:LegalPerson)
**Properties:**
- `hasObligorID` → Identifier
- `hasObligorRating` → ObligorRating
- `hasTotalExposure` → MonetaryAmount
- `hasDefaultStatus` → DefaultStatus
- `belongsToGroup` → ObligorGroup
- `hasFinancialStatements` → FinancialReport
- `hasSector` → IndustrySector
- `hasJurisdiction` → Jurisdiction

**Metadata:**
- Label: "obligor"
- Definition: "Counterparty that has or may have obligations under a credit agreement"
- Synonym: "counterparty", "borrower"

### 2.2 Facility (extends fibo-fbc-dae-dbt:CreditAgreement)
**Properties:**
- `hasFacilityID` → Identifier
- `belongsToObligor` → Obligor
- `hasFacilityType` → FacilityType
- `hasCommittedAmount` → MonetaryAmount
- `hasDrawnAmount` → MonetaryAmount
- `hasMaturityDate` → Date
- `hasInterestRate` → InterestRate
- `hasSeniority` → SeniorityLevel
- `hasCollateral` → Collateral
- `hasFacilityRating` → FacilityRating

**Metadata:**
- Label: "credit facility"
- Definition: "Specific credit arrangement or transaction with an obligor"

### 2.3 ObligorGroup
**Properties:**
- `hasGroupMembers` → [Obligor]
- `hasConsolidationMethod` → ConsolidationApproach
- `hasGroupSupport` → GroupSupportAgreement
- `hasConnectedClients` → ConnectionType

---

## 3. Exposure Classification

### 3.1 ExposureClass (extends cmns-cls:Classifier)
**Properties:**
- `hasRiskWeightFunction` → RiskWeightFormula
- `hasMinimumRequirements` → EligibilityCriteria
- `allowedUnderApproach` → [CreditRiskApproach]

### 3.2 CentralGovernmentExposure
**Properties:**
- `hasSovereignRating` → SovereignCreditRating
- `hasCurrency` → Currency
- `isDomestic` → Boolean
- `hasRiskWeight` → Percentage

**Metadata:**
- Label: "central government exposure"
- Source: "CRR Article 114"

### 3.3 CorporateExposure
**Properties:**
- `hasObligorSize` → CorporateSize
- `hasAnnualSales` → MonetaryAmount
- `hasTotalAssets` → MonetaryAmount
- `isRated` → Boolean
- `hasCorporateRating` → CorporateCreditRating

**Metadata:**
- Label: "corporate exposure"
- Source: "CRR Article 122"

### 3.4 RetailExposure
**Properties:**
- `hasRetailSubtype` → RetailExposureType
- `hasPoolAssignment` → RetailPool
- `hasNumberOfExposures` → Integer
- `meetsDiversificationCriteria` → Boolean

**Metadata:**
- Label: "retail exposure"
- Source: "CRR Article 123"

### 3.5 SpecialisedLendingExposure
**Properties:**
- `hasSLCategory` → [ProjectFinance, ObjectFinance, CommodityFinance, IPRE, HVCRE]
- `hasSlottingCategory` → SupervisorySlottingCategory
- `hasProjectPhase` → ProjectPhase

**Metadata:**
- Label: "specialised lending exposure"
- Source: "CRR Article 122a"

---

## 4. Risk Parameters

### 4.1 ProbabilityOfDefault (extends fibo-fnd-acc-cur:PercentageMonetaryAmount)
**Properties:**
- `hasTimeHorizon` → Duration (1 year)
- `hasEstimationMethod` → PDEstimationMethod
- `hasDataHistory` → DataHistoryPeriod
- `isPointInTime` → Boolean
- `hasConfidenceLevel` → Percentage
- `hasDefaultDefinition` → DefaultDefinition
- `hasFloor` → Percentage (0.03% for corporates)

**Metadata:**
- Label: "probability of default"
- Abbreviation: "PD"
- Definition: "Likelihood of default within one year"
- Source: "CRR Article 4(1)(54)"

### 4.2 LossGivenDefault (extends fibo-fnd-acc-cur:PercentageMonetaryAmount)
**Properties:**
- `isDownturn` → Boolean
- `considersSeniority` → SeniorityLevel
- `considersCollateral` → CollateralValue
- `hasRecoveryRate` → Percentage
- `hasWorkoutPeriod` → Duration
- `hasFloor` → Percentage (varies by type)

**Metadata:**
- Label: "loss given default"
- Abbreviation: "LGD"
- Source: "CRR Article 4(1)(55)"

### 4.3 ExposureAtDefault (extends fibo-fnd-acc-cur:MonetaryAmount)
**Properties:**
- `hasOnBalanceComponent` → MonetaryAmount
- `hasOffBalanceComponent` → MonetaryAmount
- `hasCCF` → CreditConversionFactor
- `considersNetting` → NettingAgreement

**Metadata:**
- Label: "exposure at default"
- Abbreviation: "EAD"
- Source: "CRR Article 166"

### 4.4 EffectiveMaturity
**Properties:**
- `hasYears` → Decimal
- `hasCalculationMethod` → MaturityCalculationMethod
- `hasFloor` → Decimal (1 year)
- `hasCap` → Decimal (5 years)

---

## 5. Default Framework

### 5.1 DefaultDefinition
**Properties:**
- `hasDaysPastDue` → Integer
- `hasMaterialityThreshold` → MaterialityThreshold
- `hasUTPCriteria` → [UTPIndicator]
- `appliesTo` → ExposureClass

**Metadata:**
- Label: "definition of default"
- Source: "CRR Article 178"

### 5.2 DefaultEvent (extends fibo-fnd-dt-oc:Occurrence)
**Properties:**
- `hasDefaultDate` → Date
- `hasDefaultType` → DefaultType
- `affectsObligor` → Obligor
- `affectsFacilities` → [Facility]
- `hasDefaultAmount` → MonetaryAmount

### 5.3 UnlikelinessToPayIndicator
**Properties:**
- `hasIndicatorType` → UTPType
- `hasEvidence` → Documentation
- `wasIdentifiedOn` → Date

**Subtypes:**
- BankruptcyFiling
- DistressedRestructuring
- MaterialCreditLoss
- SignificantWriteOff

### 5.4 MaterialityThreshold
**Properties:**
- `hasAbsoluteThreshold` → MonetaryAmount
- `hasRelativeThreshold` → Percentage
- `appliesTo` → ExposureClass

---

## 6. Credit Risk Mitigation

### 6.1 CreditRiskMitigation (abstract)
**Properties:**
- `mitigates` → CreditExposure
- `hasValue` → MonetaryAmount
- `hasHaircut` → Percentage
- `hasLegalCertainty` → LegalOpinion

### 6.2 FundedCreditProtection
**Properties:**
- `hasCollateralType` → CollateralType
- `hasValuation` → CollateralValuation
- `hasValuationFrequency` → Frequency
- `hasCustodian` → Custodian

### 6.3 FinancialCollateral
**Properties:**
- `hasISIN` → Identifier
- `hasMarketValue` → MonetaryAmount
- `hasVolatilityAdjustment` → Percentage
- `isEligible` → Boolean
- `hasCreditQuality` → CreditRating

**Subtypes:**
- CashCollateral
- DebtSecurities
- Equities
- Gold

### 6.4 UnfundedCreditProtection
**Properties:**
- `hasProtectionProvider` → CreditProtectionProvider
- `hasProviderRating` → CreditRating
- `hasCoverageAmount` → MonetaryAmount
- `hasMaturityMismatch` → Boolean

### 6.5 Guarantee
**Properties:**
- `hasGuarantor` → Guarantor
- `isUnconditional` → Boolean
- `isIrrevocable` → Boolean
- `coversAmount` → MonetaryAmount

---

## 7. Rating Systems

### 7.1 InternalRatingSystem
**Properties:**
- `hasRatingPhilosophy` → RatingPhilosophy
- `hasRatingScale` → MasterScale
- `hasAssignmentCriteria` → RatingCriteria
- `hasOverridePolicy` → OverrideRules
- `hasValidationReport` → ValidationReport

### 7.2 ObligorRating
**Properties:**
- `hasRatingGrade` → RatingGrade
- `hasAssignedPD` → ProbabilityOfDefault
- `hasRatingDate` → Date
- `hasRatingAnalyst` → Person
- `hasRatingModel` → RatingModel
- `hasOverride` → RatingOverride

### 7.3 FacilityRating
**Properties:**
- `hasLGDGrade` → LGDGrade
- `hasAssignedLGD` → LossGivenDefault
- `hasEADEstimate` → ExposureAtDefault
- `considersFacilityFeatures` → [FacilityFeature]

### 7.4 RatingModel
**Properties:**
- `hasModelType` → ModelType
- `hasVariables` → [RiskDriver]
- `hasPerformanceMetrics` → ModelPerformance
- `hasDevelopmentDate` → Date
- `hasValidationStatus` → ValidationStatus

---

## 8. Capital Calculation

### 8.1 RiskWeight
**Properties:**
- `hasPercentage` → Percentage
- `appliesTo` → ExposureClass
- `underApproach` → CreditRiskApproach
- `hasFloor` → Percentage

### 8.2 RiskWeightedAssets
**Properties:**
- `hasExposureValue` → MonetaryAmount
- `hasRiskWeight` → RiskWeight
- `hasRWAAmount` → MonetaryAmount
- `includesCRM` → Boolean

### 8.3 ExpectedLoss
**Properties:**
- `hasPD` → ProbabilityOfDefault
- `hasLGD` → LossGivenDefault
- `hasEAD` → ExposureAtDefault
- `hasELAmount` → MonetaryAmount

### 8.4 CapitalRequirement
**Properties:**
- `hasRWA` → RiskWeightedAssets
- `hasCapitalRatio` → Percentage (8%)
- `hasRequiredCapital` → MonetaryAmount
- `includesBuffers` → [CapitalBuffer]

---

## 9. External Credit Assessment

### 9.1 ECAI
**Properties:**
- `hasRecognition` → ECAIRecognition
- `hasMethodology` → RatingMethodology
- `hasCoverageScope` → MarketCoverage
- `hasTrackRecord` → HistoricalPerformance

### 9.2 CreditQualityStep
**Properties:**
- `hasStepNumber` → Integer (1-6)
- `mapsToRatings` → [ExternalRating]
- `hasRiskWeight` → Percentage
- `appliesTo` → ExposureClass

### 9.3 ECAIMapping
**Properties:**
- `hasECAI` → ECAI
- `hasCreditQualityStep` → CreditQualityStep
- `hasRatingNotches` → [RatingNotch]
- `hasValidationDate` → Date

---

## 10. Governance and Control

### 10.1 CreditRiskControl
**Properties:**
- `hasControlUnit` → OrganizationalUnit
- `hasIndependence` → IndependenceRequirement
- `hasReportingLine` → ReportingStructure
- `hasAuthority` → DecisionAuthority

### 10.2 ValidationFramework
**Properties:**
- `hasValidationType` → ValidationType
- `hasFrequency` → ValidationFrequency
- `hasScope` → ValidationScope
- `hasMethodology` → ValidationMethodology
- `producesReport` → ValidationReport

### 10.3 StressTesting
**Properties:**
- `hasScenarios` → [StressScenario]
- `hasFrequency` → Frequency
- `hasImpactAssessment` → ImpactAnalysis
- `feedsInto` → CapitalPlanning

### 10.4 DataGovernance
**Properties:**
- `hasDataQualityStandards` → DataQualityCriteria
- `hasDataArchitecture` → DataModel
- `hasRetentionPeriod` → Duration
- `hasAccessControls` → AccessPolicy

---

## 11. Regulatory Compliance

### 11.1 IRBPermission
**Properties:**
- `grantedBy` → CompetentAuthority
- `hasScope` → PermissionScope
- `hasConditions` → [PermissionCondition]
- `hasEffectiveDate` → Date
- `hasReviewDate` → Date

### 11.2 ModelApproval
**Properties:**
- `coversModel` → RiskModel
- `hasApprovalDate` → Date
- `hasConditions` → [ApprovalCondition]
- `requiresAnnualReview` → Boolean

### 11.3 RegulatoryReporting
**Properties:**
- `hasReportType` → ReportType
- `hasFrequency` → ReportingFrequency
- `hasSubmissionDeadline` → Deadline
- `hasDataRequirements` → DataSpecification

---

## 12. Specialized Concepts

### 12.1 ADCExposure (Land Acquisition, Development, Construction)
**Properties:**
- `hasProjectType` → ADCProjectType
- `hasCompletionPercentage` → Percentage
- `hasPreSaleLevel` → Percentage
- `hasDevelopmentRisk` → RiskAssessment

### 12.2 CurrencyMismatch
**Properties:**
- `hasLendingCurrency` → Currency
- `hasIncomeCurrency` → Currency
- `hasMismatchFactor` → Percentage
- `hasHedging` → HedgingArrangement

### 12.3 DilutionRisk
**Properties:**
- `appliesTo` → PurchasedReceivables
- `hasDilutionReserve` → MonetaryAmount
- `hasHistoricalDilution` → Percentage

---

## Implementation Notes

### Property Naming Conventions
- Use FIBO properties where they exist
- Prefix with module namespace for new properties
- Follow camelCase convention
- Boolean properties start with "is" or "has"

### Metadata Requirements
Each class should include:
- `rdfs:label` (English)
- `skos:definition`
- `cmns-av:adaptedFrom` (CRR article reference)
- `skos:example` (where helpful)
- `cmns-av:explanatoryNote` (for complex concepts)
- `cmns-av:synonym` (alternative terms)

### Validation Rules
- Ensure disjointness where applicable
- Define cardinality restrictions
- Specify data ranges for numeric properties
- Include regulatory minima/maxima as constraints

### Future Extensions
- Basel III final reforms (CRR3)
- ESG risk factors
- Climate risk adjustments
- Behavioral modeling enhancements
- Machine learning model governance

---

## Appendix: FIBO Property Reference

### Commonly Used FIBO Properties
```
fibo-fnd-rel-rel:evaluates
fibo-fnd-rel-rel:isEvaluatedBy
fibo-fnd-rel-rel:appliesTo
fibo-fbc-dae-dbt:hasBorrower
fibo-fbc-dae-dbt:hasLender
fibo-fbc-dae-dbt:isCollateralizedBy
fibo-fbc-dae-dbt:hasPrincipal
fibo-fnd-arr-asmt:assesses
cmns-cls:isClassifiedBy
cmns-cxtdsg:appliesTo
cmns-col:comprises
cmns-doc:records
```

### Key FIBO Classes to Extend
```
fibo-fbc-dae-dbt:CreditAgreement
fibo-fbc-dae-dbt:Collateral
fibo-fnd-acc-cur:MonetaryAmount
fibo-fnd-acc-cur:PercentageMonetaryAmount
fibo-fbc-dae-crt:CreditRating
fibo-fnd-arr-asmt:AssessmentActivity
```
