# Demand RADAR Dashboard

Demand RADAR is an explainable early-warning system designed to detect demand signals for cold and flu related products using public data sources.

This project was developed as part of the Digital Innovation & Design Thinking course at HEC Lausanne.

---

## Overview

The goal of the system is to support decision makers by identifying early demand trends from multiple weak signals and transforming them into actionable insights.

The dashboard combines:

- Wikipedia pageviews (public interest)
- GDELT news mentions (media attention)
- Aggregated signals across multiple keywords

---

## Key Features

- **Trend Detection**  
  Identifies spikes, sustained increases, and drops in demand signals

- **Multi-Signal Validation**  
  Reduces false positives by requiring confirmation across multiple sources

- **Explainable Alerts**  
  Shows why an alert was triggered and which signals contributed

- **Confidence Score**  
  Helps users assess the reliability of each alert

- **Interactive Dashboard**  
  Allows users to explore signals and interpret trends visually

---

## Prototype Preview


Example:

![Dashboard Screenshot](project_files/screenshots/dashboard.png)

---

## How It Works

1. Collect signals from public data sources (Wikipedia, GDELT)
2. Aggregate signals across multiple keywords
3. Detect anomalies (spikes, trends, drops)
4. Validate signals across sources
5. Generate alerts with explanation and confidence score

---

## How to Run the Prototype

### Option 1 — Using virtual environment

```bash
cd project_files
../.venv/bin/streamlit run dashboard/app.py
```

### Option 2 - If Streamlit installed globally

```bash
cd project_files
streamlit run dashboard/app.py
```
