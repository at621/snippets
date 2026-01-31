# Testing Plan: Regulatory Q&A System

## Workflow Diagram (Inferred from Code)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              USER OPENS APP                                      │
│                         (Split-screen UI loads)                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: QUESTION FORMULATION                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  User types question in chat                                             │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  question_formulation node (LLM)                                         │    │
│  │  - Analyzes user input                                                   │    │
│  │  - Decides: needs_clarification = True/False                             │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                          │                    │                                  │
│            ┌─────────────┘                    └─────────────┐                    │
│            ▼                                                ▼                    │
│  ┌──────────────────────┐                    ┌──────────────────────────────┐   │
│  │ needs_clarification  │                    │ needs_clarification = False  │   │
│  │ = True               │                    │ Submission ready:            │   │
│  │                      │                    │ - Subject                    │   │
│  │ LLM asks follow-up   │                    │ - Legal references           │   │
│  │ questions            │                    │ - Topic                      │   │
│  └──────────┬───────────┘                    │ - Keywords (max 4)           │   │
│             │                                │ - Question                   │   │
│             │ User answers                   │ - Background                 │   │
│             └────────────┐                   └──────────────┬───────────────┘   │
│                          │                                  │                    │
│                          ▼                                  ▼                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  INTERRUPT: wait_for_submission_review                                   │    │
│  │  User sees submission in right panel                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                          │                    │                                  │
│            ┌─────────────┘                    └─────────────┐                    │
│            ▼                                                ▼                    │
│  ┌──────────────────────┐                    ┌──────────────────────────────┐   │
│  │ "Request Changes"    │                    │ "Approve Submission"         │   │
│  │ User provides        │                    │ submission_approved = True   │   │
│  │ feedback             │                    └──────────────┬───────────────┘   │
│  └──────────┬───────────┘                                   │                    │
│             │                                               │                    │
│             └───────► Back to question_formulation          │                    │
│                       (revise with feedback)                │                    │
└─────────────────────────────────────────────────────────────┼────────────────────┘
                                                              │
                                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: KNOWLEDGE BASE SEARCH                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  search_knowledge_base node                                              │    │
│  │  1. Semantic search (embeddings + cosine similarity)                     │    │
│  │  2. Keyword search (TF-IDF)                                              │    │
│  │  3. Deduplicate → max 20 results                                         │    │
│  │  4. LLM curation → select top 8 most relevant                            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  INTERRUPT: wait_for_source_review                                       │    │
│  │  User sees:                                                              │    │
│  │  - Initial RAG results (with scores)                                     │    │
│  │  - Curated results (with LLM explanations)                               │    │
│  │  User can:                                                               │    │
│  │  - Remove curated sources                                                │    │
│  │  - Add custom sources (max 5)                                            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  "Proceed to Answer Generation"                                          │    │
│  │  sources_approved = True                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┬────────────────────┘
                                                              │
                                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: ANSWER GENERATION                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  generate_answer node (RegulatoryQABot)                                  │    │
│  │  - Uses curated sources + user-added sources                             │    │
│  │  - Generates answer with citations [1], [2], etc.                        │    │
│  │  - Returns: answer, confidence_level, references_used                    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  INTERRUPT: wait_for_answer_review                                       │    │
│  │  User sees:                                                              │    │
│  │  - Confidence level (HIGH/MEDIUM/LOW)                                    │    │
│  │  - Full answer with citations                                            │    │
│  │  - References used                                                       │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                          │                    │                                  │
│            ┌─────────────┘                    └─────────────┐                    │
│            ▼                                                ▼                    │
│  ┌──────────────────────┐                    ┌──────────────────────────────┐   │
│  │ "Request Changes"    │                    │ "Approve Answer"             │   │
│  │ User provides        │                    │ answer_approved = True       │   │
│  │ feedback             │                    └──────────────┬───────────────┘   │
│  └──────────┬───────────┘                                   │                    │
│             │                                               │                    │
│             └───────► Back to generate_answer               │                    │
│                       (regenerate with feedback)            │                    │
└─────────────────────────────────────────────────────────────┼────────────────────┘
                                                              │
                                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: DOCUMENT BUILDING                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  build_document node                                                     │    │
│  │  - Creates RegulatoryQADocument                                          │    │
│  │  - Generates ID: LEG-YYYY-MMDD-HHMM                                      │    │
│  │  - Maps cited sources to legal references (L1/L2/L3)                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  EXPORT OPTIONS                                                          │    │
│  │  - Download Word (.docx)                                                 │    │
│  │  - Download PDF (.pdf)                                                   │    │
│  │  - Download JSON (.json)                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┬────────────────────┘
                                                              │
                                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 5: FOLLOW-UP Q&A (Optional)                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  INTERRUPT: wait_for_document_qa                                         │    │
│  │  User can ask follow-up questions in chat                                │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  document_qa node                                                        │    │
│  │  - LLM answers with document context                                     │    │
│  │  - Loops back to wait_for_document_qa                                    │    │
│  └──────────────────────────────────────────────┬──────────────────────────┘    │
│                                                 │                                │
│                                                 └────────► (loop until reset)    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Tester Questions (40 Questions)

### A. Setup & Configuration (5 questions)
| # | Question | Answer |
|---|----------|--------|
| 1 | OpenAI API key configured? | [ ] Yes / [ ] No |
| 2 | Which model used? | [ ] gpt-5.2 / [ ] gpt-4o / [ ] gpt-4o-mini |
| 3 | Knowledge base source? | [ ] Parquet file / [ ] PostgreSQL |
| 4 | What regulatory topic tested? | [ ] PD / [ ] LGD / [ ] LGD in-default / [ ] Downturn / [ ] Data req / [ ] Overarching |
| 5 | Sample question used: | ________________________________ |

### B. Phase 1 - Question Formulation (8 questions)
| # | Test Step | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 6 | App loads with split-screen layout (chat left, results right) | [ ] | |
| 7 | Welcome message displays in chat panel | [ ] | |
| 8 | User can type question and submit | [ ] | |
| 9 | LLM responds (clarifying questions OR completed submission) | [ ] | |
| 10 | If clarification asked: user can answer and LLM continues | [ ] | |
| 11 | Submission displays in right panel (subject, topic, legal refs, keywords) | [ ] | |
| 12 | "Request Changes" → feedback box appears → revised submission returned | [ ] | |
| 13 | "Approve Submission" → proceeds to search phase | [ ] | |

### C. Phase 2 - Search & Curation (7 questions)
| # | Test Step | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 14 | Initial RAG results display with scores (color-coded) | [ ] | |
| 15 | Curated results display with LLM explanations | [ ] | |
| 16 | User can remove a curated source | [ ] | |
| 17 | User can add a custom source (title + text) | [ ] | |
| 18 | Maximum 5 custom sources enforced | [ ] | |
| 19 | Curation summary explains LLM's selection rationale | [ ] | |
| 20 | "Proceed to Answer Generation" → proceeds to answer phase | [ ] | |

### D. Phase 3 - Answer Generation (7 questions)
| # | Test Step | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 21 | Answer displays with confidence badge (HIGH/MEDIUM/LOW) | [ ] | |
| 22 | Answer contains citations [1], [2], etc. | [ ] | |
| 23 | Citations map correctly to sources in "References Used" | [ ] | |
| 24 | "Request Changes" → feedback box appears → answer regenerated | [ ] | |
| 25 | Regenerated answer incorporates user feedback | [ ] | |
| 26 | "Approve Answer" → proceeds to document phase | [ ] | |
| 27 | Only CITED sources appear in final references (not all curated) | [ ] | |

### E. Phase 4 - Document Export (5 questions)
| # | Test Step | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 28 | Document ID generated (format: LEG-YYYY-MMDD-HHMM) | [ ] | |
| 29 | Word download works and opens correctly | [ ] | |
| 30 | PDF download works and opens correctly | [ ] | |
| 31 | JSON download contains complete document data | [ ] | |
| 32 | Document contains correct legal reference types (L1/L2/L3) | [ ] | |

### F. Phase 5 - Follow-up Q&A (3 questions)
| # | Test Step | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 33 | User can ask follow-up question in chat after document generated | [ ] | |
| 34 | LLM answers with document context | [ ] | |
| 35 | Multiple follow-up questions work in sequence | [ ] | |

### G. UI & Error Handling (5 questions)
| # | Test Step | Pass/Fail | Notes |
|---|-----------|-----------|-------|
| 36 | Status banner updates at each workflow stage | [ ] | |
| 37 | API usage counter increments (tokens displayed in sidebar) | [ ] | |
| 38 | Chat input disables during LLM processing (spinner shown) | [ ] | |
| 39 | "Reset Conversation" clears all state and starts fresh | [ ] | |
| 40 | Error messages display clearly if something fails | [ ] | |

---

## Issues Found
| # | Description | Severity | Steps to Reproduce |
|---|-------------|----------|-------------------|
| | | [ ] Critical / [ ] Major / [ ] Minor | |
| | | [ ] Critical / [ ] Major / [ ] Minor | |
| | | [ ] Critical / [ ] Major / [ ] Minor | |

---

## Overall Assessment
| Question | Answer |
|----------|--------|
| End-to-end workflow works? | [ ] Yes / [ ] No |
| All revision loops work? | [ ] Yes / [ ] No |
| Exports production-ready? | [ ] Yes / [ ] No |
| Blocking issues found? | [ ] Yes / [ ] No |
| **Recommendation:** | [ ] Ready / [ ] Needs fixes / [ ] Major rework |
