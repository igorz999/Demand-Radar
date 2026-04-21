# Cold & Flu Product Keywords Strategy

**Purpose:** Identify 10-20 keywords that serve as leading indicators for Cold & Flu product demand

**Strategy:** Use a 3-layer approach

- Layer 1: Core disease/condition terms (high relevance, high volume)
- Layer 2: Symptom-specific terms (medium relevance, medium-high volume)
- Layer 3: Treatment/product-specific terms (lower volume, high purchase intent)

---

## Finalized Keyword List (18 keywords)

### Layer 1: Core Disease/Condition Terms (5 keywords)

**Rationale:** High search volume, strong correlation with demand shifts, seasonal spikes

| #   | Keyword               | Wikipedia?   | GDELT News?  | Reasoning                                   |
| --- | --------------------- | ------------ | ------------ | ------------------------------------------- |
| 1   | Influenza             | ✅ High      | ✅ High      | Direct disease term, major epidemic trigger |
| 2   | Common cold           | ✅ High      | ✅ Medium    | Most searched cold-related term             |
| 3   | Flu (short form)      | ✅ Very High | ✅ Very High | Most common colloquial term                 |
| 4   | Respiratory infection | ✅ Medium    | ✅ High      | Broader category, captures varieties        |
| 5   | Cough                 | ✅ High      | ✅ Medium    | Primary symptom, strong demand proxy        |

### Layer 2: Symptom & Experience Terms (7 keywords)

**Rationale:** Medium volume, good specificity, often trigger product searches

| #   | Keyword          | Wikipedia? | GDELT News? | Reasoning                                  |
| --- | ---------------- | ---------- | ----------- | ------------------------------------------ |
| 6   | Fever            | ✅ High    | ✅ High     | Key symptom associated with cold/flu       |
| 7   | Sore throat      | ✅ Medium  | ✅ Medium   | Specific symptom, drives remedies purchase |
| 8   | Chills           | ✅ Low     | ✅ Low      | Symptom, may correlate with fever searches |
| 9   | Nasal congestion | ✅ Medium  | ✅ Low      | Key symptom, drives decongestant demand    |
| 10  | Runny nose       | ✅ Low     | ✅ Low      | Symptom, correlates with antihistamines    |
| 11  | Body aches       | ✅ Medium  | ✅ Low      | Common cold/flu symptom                    |
| 12  | Fatigue          | ✅ High    | ✅ Low      | General symptom but common in cold/flu     |

### Layer 3: Treatment/Product Terms (6 keywords)

**Rationale:** Direct purchase intent, lower noise, high actionability

| #   | Keyword        | Wikipedia? | GDELT News? | Reasoning                                |
| --- | -------------- | ---------- | ----------- | ---------------------------------------- |
| 13  | Decongestant   | ✅ Medium  | ✅ Low      | Core product category we monitor         |
| 14  | Antihistamine  | ✅ Medium  | ✅ Low      | Core product category we monitor         |
| 15  | Acetaminophen  | ✅ Medium  | ✅ Medium   | Pain/fever reliever, strong demand proxy |
| 16  | Ibuprofen      | ✅ High    | ✅ Medium   | Pain/fever reliever, very common         |
| 17  | Cough medicine | ✅ Low     | ✅ Low      | Generic product term                     |
| 18  | Lozenges       | ✅ Low     | ✅ Low      | Throat relief product                    |

---

## Keyword Grouping for Multi-Source Validation

**Disease/Outbreak Group:** (Influenza, Common cold, Flu, Respiratory infection)

- Expect these to rise TOGETHER during outbreaks
- Higher confidence if 2+ of these spike simultaneously

**Symptom Group:** (Cough, Fever, Sore throat, Nasal congestion)

- Expect these to rise TOGETHER with disease terms
- Higher confidence if these correlate with disease terms

**Treatment Group:** (Decongestant, Antihistamine, Acetaminophen, Ibuprofen)

- These are the actual products people buy
- Lower noise if consistent across multiple products

---

## Expected Seasonal Pattern

### Peak Seasons:

- **Winter (Dec-Feb):** Strong flu season, high demand expected
- **Fall transition (Sep-Oct):** Seasonal allergies, moderate demand

### Off-Seasons:

- **Summer (Jun-Aug):** Low baseline, spikes should be investigative

### Known Events:

- Pandemic years: Expected much higher baselines
- Unusual outbreak news: Should trigger spikes

---

## False Positive Mitigation

| Risk              | Keywords Affected                  | Mitigation                                      |
| ----------------- | ---------------------------------- | ----------------------------------------------- |
| Seasonal noise    | Fever, Cough (common in allergies) | Validate against disease terms (Flu, Influenza) |
| Ambiguous terms   | Fatigue, Body aches (many causes)  | Require multi-keyword confirmation              |
| Low-traffic terms | Chills, Lozenges                   | Use higher confidence thresholds (75%+)         |
| Broader contexts  | Respiratory infection              | Cross-check with disease terms                  |

---

## Implementation Notes

### Wikipedia Pageviews Fetching

- Use: `https://pageviews.toolforge.org/`
- Granularity: Daily (we'll aggregate to weekly)
- Language: English Wikipedia
- All keywords available via Pageviews API

### GDELT News Fetching

- Use: GDELT 2.0 API (counts of news mentions)
- Query format: Search for keyword mentions in article text/headlines
- Global coverage: All English-language news
- Update frequency: 15-minute intervals (we'll aggregate to weekly)

### Weighting Strategy

**Initially:** Equal weights for all keywords
**After data analysis:** May increase weight for high-signal keywords (e.g., "Influenza" if very predictive)

### Keyword Validation

Once we fetch data:

1. Check correlation matrix between keywords
2. Identify outliers (keywords that don't correlate with others)
3. May drop low-signal keywords in refinement phase
4. Document which keywords drive most alerts

---

## Alternative Keywords (if we need more/different ones)

- Pandemic
- Epidemic
- Outbreak
- Vaccine / Vaccination (may not correlate with demand for remedies)
- Antibiotic (not typically for cold/flu)
- Illness
- Sick / Sickness
- Flu-like illness (FLI)
- Symptom
- Remedy
- Treatment
- Medicine
