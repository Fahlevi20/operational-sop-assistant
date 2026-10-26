# Retrieval Ranking Check

Offline source-page ranking evaluation of expected-answerable cases only.
Input SHA256: `c346b01e8942ad0e60c36b79d36a994c74f952220a9d73b38b2d7ac14222ac43`

| Case | Recall@1 | Recall@2 | Recall@4 | Reciprocal rank | Retrieved page order |
| --- | ---: | ---: | ---: | ---: | --- |
| response-p1 | 1.000 | 1.000 | 1.000 | 1.000 | 01 p.1 → 03 p.1 → 02 p.1 → 04 p.1 |
| closure | 1.000 | 1.000 | 1.000 | 1.000 | 01 p.1 → 03 p.1 → 02 p.1 → 04 p.1 |
| recurring | 1.000 | 1.000 | 1.000 | 1.000 | 02 p.1 → 03 p.1 → 01 p.1 → 04 p.1 |
| ticket-outage | 0.000 | 1.000 | 1.000 | 0.500 | 01 p.1 → 03 p.1 → 04 p.1 → 02 p.1 |
| update-cadences | 0.500 | 1.000 | 1.000 | 1.000 | 03 p.1 → 04 p.1 → 01 p.1 → 02 p.1 |
| security-after-hours | 0.000 | 0.000 | 1.000 | 0.333 | 03 p.1 → 01 p.1 → 04 p.1 → 02 p.1 |

## Summary

- Cases evaluated: 6
- Mean recall@1: **0.583**
- Mean recall@2: **0.833**
- Mean recall@4: **1.000**
- Mean mrr: **0.806**

## Interpretation

- Recall measures how many annotated required pages appear in the top k; MRR measures how early the first required page appears.
- Multiple sections on one page count as one relevant page. This is page-level evaluation, not section-level entailment.
- Reference labels come from the golden case embedded in this saved run. Incomplete annotations can affect the measurements.
- Returning all four corpus pages guarantees page coverage, not useful ranking. A cross-document question needs all required pages, not just one relevant hit.
- These are development cases, not a held-out embedding benchmark. Do not lower retrieval depth based on averages without inspecting every case.
