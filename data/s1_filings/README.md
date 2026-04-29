# S-1 filing data (populated in Phase 3, Week 3)

This directory will hold hand-curated quarterly revenue from public SEC
S-1 filings, used by Notebook 3 (calibration, Part B). Each company
becomes one JSON file with the schema below.

## Schema

```json
{
  "company": "Shopify",
  "ticker": "SHOP",
  "ipo_date": "2015-05-21",
  "source": "SEC S-1 Filing, Amendment No. 4",
  "metric": "quarterly_revenue_millions_usd",
  "data": [
    { "quarter": "2012-Q1", "revenue": 8.7 },
    { "quarter": "2012-Q2", "revenue": 10.1 }
  ]
}
```

Files match the schema of `data/synthetic/*.json` in spirit so Notebook 3
does not branch on data source.

## Target list

- `shopify.json` (minimum viable; cleanest filing)
- `zoom.json`
- `datadog.json` (drop if Phase 3 schedule compresses)
- `snowflake.json` (drop if Phase 3 schedule compresses)
