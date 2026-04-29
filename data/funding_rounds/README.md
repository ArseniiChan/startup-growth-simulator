# Funding-round data (populated in Phase 3, Week 3)

This directory will hold public funding-round data (Wikipedia, TechCrunch,
press releases) used by Notebook 6 (cubic-spline interpolation between
rounds).

## Schema

```json
{
  "company": "Stripe",
  "source": "Wikipedia, TechCrunch",
  "rounds": [
    { "date": "2011-06", "series": "Seed", "amount_millions": 2,  "valuation_millions": 20 },
    { "date": "2012-02", "series": "A",    "amount_millions": 18, "valuation_millions": 100 }
  ]
}
```

## Target list

- `stripe.json`
- `airbnb.json`

Notebook 6 is marked CUTTABLE in the implementation plan; if Week 3 of
Phase 3 compresses, this directory may stay empty and the spline
interpolation will run on synthetic funding-round data instead.
