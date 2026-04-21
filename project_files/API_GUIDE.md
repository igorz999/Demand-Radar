# Data Sources & API Integration Guide

## 1. Wikipedia Pageviews API

### Overview

- **Endpoint:** `https://pageviews.toolforge.org/`
- **Maintained by:** Tools Labs (Wikimedia Foundation)
- **Authentication:** None required (public API)
- **Rate Limit:** ~100,000 requests per second (very generous)
- **Data Format:** JSON
- **Language:** English Wikipedia
- **Granularity:** Daily pageviews

### API Endpoint Structure

```
https://pageviews.toolforge.org/per-article/en.wikipedia/monthly/{start_date}/{end_date}/{article_name}
```

**Parameters:**

- `start_date`: YYYYMM format (e.g., 202601 for Jan 2026)
- `end_date`: YYYYMM format
- `article_name`: URL-encoded article name (spaces → underscores or %20)

### Example Request

```python
import requests

# Get pageviews for "flu" article (2025-01 to 2026-03)
url = "https://pageviews.toolforge.org/per-article/en.wikipedia/monthly/202501/202603/Influenza"
response = requests.get(url)
data = response.json()
```

### Example Response

```json
{
  "items": [
    {
      "timestamp": "2025010100",
      "views": 12345
    },
    {
      "timestamp": "2025020100",
      "views": 15620
    },
    ...
  ]
}
```

### Data Strategy

- Fetch monthly aggregates to ensure sufficient data volume
- Convert monthly to weekly by interpolation/averaging (if needed)
- Store raw data, then aggregate in processing pipeline

### Article Name Mapping

Our keywords may not always have Wikipedia articles with exact matching names:

| Keyword               | Wikipedia Article              | Notes                         |
| --------------------- | ------------------------------ | ----------------------------- |
| Influenza             | Influenza                      | Exact match                   |
| Common cold           | Common cold                    | Exact match                   |
| Flu                   | Influenza                      | Redirect to Influenza         |
| Respiratory infection | Respiratory infection          | Exact match (might not exist) |
| Cough                 | Cough                          | Exact match                   |
| Fever                 | Fever                          | Exact match                   |
| Sore throat           | Pharyngitis                    | Medical term                  |
| Chills                | Rigors (medicine)              | Medical term                  |
| Nasal congestion      | Rhinitis                       | Medical term, not exact       |
| Runny nose            | Rhinorrhea                     | Medical term                  |
| Body aches            | Myalgia                        | Medical term                  |
| Fatigue               | Fatigue                        | Exact match                   |
| Decongestant          | Decongestant                   | Exact match                   |
| Antihistamine         | Antihistamine                  | Exact match                   |
| Acetaminophen         | Acetaminophen (or Paracetamol) | May be two separate articles  |
| Ibuprofen             | Ibuprofen                      | Exact match                   |
| Cough medicine        | Antitussive or Cough medicine  | May not exist                 |
| Lozenges              | Lozenge (pharmaceutical)       | Exact match                   |

**Note:** We'll need to test which Wikipedia articles exist and are trackable via API

---

## 2. GDELT News Mentions API

### Overview

- **Project:** Global Event, Language, and Tone (GDELT)
- **Endpoint:** `https://api.gdelt.org/api/v2/tone`
- **Alternative:** Use GDELT 2.0 Search API
- **Authentication:** API Key (free tier available)
- **Rate Limit:** Depends on tier (check documentation)
- **Data Format:** CSV or JSON
- **Coverage:** 100+ languages, 300+ source countries
- **Update Frequency:** 15-minute increments
- **Update Lag:** ~45 minutes behind real-time

### API Endpoint Structure (GDELT 2.0 Search)

```
https://api.gdelt.org/api/v2/search/gkg?query={keyword}&mode=timeline&timespan={timespan}&sort=date&format=csv
```

**Parameters:**

- `query`: Search keyword (URL-encoded)
- `mode`: 'timeline' for time-series aggregation
- `timespan`: Time range (e.g., 90d, 1y)
- `sort`: 'date' to sort chronologically
- `format`: 'csv' or 'json'

### Alternative Endpoint (Tone API - Count-Based)

```
https://api.gdelt.org/api/v2/tone?query={keyword}&mode=timeline&timespan={timespan}&sort=date&format=csv
```

This returns counts of articles mentioning the keyword in the dataset.

### Example Request

```python
import requests

# Get news mentions of "flu epidemic" for past 90 days
url = "https://api.gdelt.org/api/v2/search/gkg"
params = {
    "query": "flu epidemic",
    "mode": "timeline",
    "timespan": "90d",
    "sort": "date",
    "format": "csv"
}
response = requests.get(url, params=params)
```

### Example Response (CSV)

```
date,count
2026031001,42
2026031002,48
2026031003,35
...
```

### Data Collection Strategy

- Query each keyword weekly (batch process)
- Store counts as: `date`, `keyword`, `mention_count`
- Track article URLs if available (for alert explanations)

### Important Notes

- **Historical data:** Limited to ~10 years in some cases
- **Real-time:** Updates every 15 minutes
- **Specificity:** "flu" vs "influenza" may capture different articles
- **Noise:** News mentions ≠ actual demand (but good leading indicator)

---

## 3. Optional Data Sources (For Later Phases)

### Google Trends

- **Endpoint:** Unofficial APIs available (library: `pytrends`)
- **Limitation:** No historical data export, real-time only
- **Consideration:** Anti-bot protection, may require proxy

### YouTube Metadata

- **Endpoint:** YouTube Data API v3
- **Cost:** Free tier available (limited queries)
- **Query:** Search for videos with keyword, count upload dates

### Weather Data

- **Endpoint:** OpenWeatherMap API or NOAA
- **Relevance:** Cold/dry air increases flu transmission
- **Use:** Optional correlation with regional flu spikes

---

## Implementation Plan

### Week 1 Tasks

1. **Test Wikipedia API**
   - [ ] Verify which of our 18 keywords have Wikipedia articles
   - [ ] Fetch sample data for 2025-2026 (4-6 months)
   - [ ] Check data quality, missing values

2. **Test GDELT API**
   - [ ] Register for free API key
   - [ ] Test keyword queries
   - [ ] Fetch sample news mention counts for same period
   - [ ] Compare with Wikipedia data

3. **Build Data Fetchers**
   - [ ] Create `wikipedia_fetcher.py` module
   - [ ] Create `gdelt_fetcher.py` module
   - [ ] Error handling & retry logic
   - [ ] Data validation

### Week 2 Tasks

4. **Collect Historical Data**
   - [ ] Fetch 12-16 weeks of data (Oct 2025 - Mar 2026)
   - [ ] Store in CSV format
   - [ ] Document any gaps or issues

---

## Data Storage Format

### Wikipedia Data (wikipedia_weekly_data.csv)

```
date,keyword,pageviews
2025-10-01,influenza,12345
2025-10-01,common cold,8920
2025-10-08,influenza,13200
...
```

### GDELT Data (gdelt_weekly_data.csv)

```
date,keyword,mention_count,source_count
2025-10-01,flu epidemic,245,180
2025-10-08,flu outbreak,198,145
...
```

**Note:** `source_count` = number of distinct news sources

---

## Expected Data Patterns

### Wikipedia

- **Baseline:** ~5-20k monthly pageviews for disease terms
- **Seasonal:** Winter peaks (Dec-Jan-Feb)
- **Spike:** 2-3x baseline during major outbreaks
- **Lag:** Articles updated during/after outbreaks

### GDELT

- **Baseline:** ~50-200 articles/week mentioning keywords
- **Seasonal:** Winter spikes consistent with flu season
- **Spike:** 3-5x baseline during disease outbreak news
- **Lag:** Articles published during/immediately after news events

### Expected Correlation

- Wikipedia pageviews should correlate with GDELT mentions (0.6-0.8 correlation expected)
- Symptom terms (fever, cough) may lag disease terms
- Product terms (ibuprofen) may follow symptom terms by 1-2 weeks

---

## Troubleshooting

| Issue               | Cause                              | Solution                              |
| ------------------- | ---------------------------------- | ------------------------------------- |
| 404 on Wikipedia    | Article doesn't exist              | Use medical term alternative          |
| Empty GDELT results | Keyword too common or too specific | Try different keyword variation       |
| Rate limit exceeded | Too many API requests              | Implement caching, backoff strategy   |
| Data gaps           | API downtime                       | Use interpolation or skip that period |
| High noise          | Unrelated keyword mentions         | Require multi-keyword confirmation    |
