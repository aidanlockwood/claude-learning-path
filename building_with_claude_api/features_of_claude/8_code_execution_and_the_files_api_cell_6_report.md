# Cell 6 Output: Streaming Service Churn Analysis

This document reformats the analysis output associated with the code-execution flow in `8_code_execution_and_the_files_api.ipynb` into a cleaner, easier-to-scan report.

## Code

### 1) Client setup

```python
from utils.util_funcs import *

client, model = api_client_setup()

# Checking which model got loaded
print(f'Anthropic Client loaded for {client} with model: {model}')
```

### 2) Upload the CSV file

```python
file_metadata = upload('./supporting_materials/streaming.csv')
file_metadata
```

### 3) Run the analysis with code execution

```python
messages = []

add_user_message(
    messages,
    [
        {
            "type": "text",
            "text": """
Run a detailed analysis to determine major drivers of churn.
Your final output should include at least one detailed plot summarizing your findings.

Critical note: Every time you execute code, you're starting with a completely clean slate. 
No variables or library imports from previous executions exist. You need to redeclare/reimport all variables/libraries.
            """,
        },
        {"type": "container_upload", "file_id": file_metadata.id},
    ],
)

chat(messages, tools=[{"type": "code_execution_20250825", "name": "code_execution"}])
```

### 4) Download the resulting file

```python
download_file('')
```

## Dataset Overview

- Records: 500
- Features: 10
- Missing values: None

### Columns

- `UserID`
- `SubscriptionTier`
- `TotalViewingHoursLastMonth`
- `TopGenre`
- `BingeWatchingSessionsLastMonth`
- `NumberOfUniqueTitlesWatchedLastMonth`
- `AverageSessionDurationMinutes`
- `CustomerServiceInteractionsLastYear`
- `MonthlyCost`
- `Churned`

## Churn Distribution

| Class | Count | Share |
| --- | ---: | ---: |
| Not churned (`0`) | 307 | 61.4% |
| Churned (`1`) | 193 | 38.6% |

## Churn by Subscription Tier

| Subscription Tier | Total | Churned | Churn Rate |
| --- | ---: | ---: | ---: |
| Basic | 207 | 90 | 43.5% |
| Premium | 83 | 20 | 24.1% |
| Standard | 210 | 83 | 39.5% |

## Churn by Top Genre

| Genre | Total | Churned | Churn Rate |
| --- | ---: | ---: | ---: |
| Horror | 44 | 23 | 52.3% |
| Thriller | 29 | 14 | 48.3% |
| Action | 74 | 33 | 44.6% |
| Romance | 55 | 23 | 41.8% |
| SciFi | 42 | 17 | 40.5% |
| Drama | 102 | 36 | 35.3% |
| Comedy | 100 | 33 | 33.0% |
| Documentary | 54 | 14 | 25.9% |

## Numerical Feature Comparison

### Average by Churn Status

| Feature | Not Churned Mean | Churned Mean | Direction |
| --- | ---: | ---: | --- |
| Total viewing hours last month | 83.22 | 66.58 | Lower for churned users |
| Binge-watching sessions last month | 7.69 | 6.17 | Lower for churned users |
| Unique titles watched last month | 23.74 | 19.45 | Lower for churned users |
| Average session duration minutes | 57.76 | 49.42 | Lower for churned users |
| Customer service interactions last year | 2.49 | 3.18 | Higher for churned users |
| Monthly cost | 12.11 | 11.18 | Slightly lower for churned users |

## Correlation With Churn

| Feature | Correlation |
| --- | ---: |
| Churned | 1.0000 |
| CustomerServiceInteractionsLastYear | 0.2794 |
| TopGenre_encoded | 0.0544 |
| SubscriptionTier_encoded | -0.0367 |
| MonthlyCost | -0.1263 |
| AverageSessionDurationMinutes | -0.2178 |
| NumberOfUniqueTitlesWatchedLastMonth | -0.2239 |
| BingeWatchingSessionsLastMonth | -0.2368 |
| TotalViewingHoursLastMonth | -0.2464 |

## Random Forest Feature Importance

| Feature | Importance |
| --- | ---: |
| TotalViewingHoursLastMonth | 0.2387 |
| AverageSessionDurationMinutes | 0.2026 |
| NumberOfUniqueTitlesWatchedLastMonth | 0.1631 |
| BingeWatchingSessionsLastMonth | 0.1084 |
| TopGenre_encoded | 0.1055 |
| CustomerServiceInteractionsLastYear | 0.1012 |
| MonthlyCost | 0.0493 |
| SubscriptionTier_encoded | 0.0310 |

## Model Performance

| Metric | Value |
| --- | ---: |
| Accuracy | 0.61 |
| ROC-AUC | 0.6010 |

### Classification Report

| Class | Precision | Recall | F1-score | Support |
| --- | ---: | ---: | ---: | ---: |
| Not churned (`0`) | 0.65 | 0.79 | 0.72 | 92 |
| Churned (`1`) | 0.50 | 0.33 | 0.40 | 58 |
| Macro avg | 0.58 | 0.56 | 0.56 | 150 |
| Weighted avg | 0.59 | 0.61 | 0.59 | 150 |

## Key Takeaways

1. Churn is lower among users with higher engagement: more viewing hours, more binge sessions, more titles watched, and longer sessions all trend downward for churned users.
2. Customer service interactions stand out as the strongest positive signal for churn.
3. Premium subscribers churn far less often than Basic and Standard users.
4. Horror, Thriller, and Action viewers show the highest churn rates among genres.
5. The model is only moderately predictive, with accuracy just above 60% and ROC-AUC near 0.60.
