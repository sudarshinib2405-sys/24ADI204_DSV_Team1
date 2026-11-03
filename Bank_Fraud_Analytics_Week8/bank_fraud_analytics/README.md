# Bank Fraud Analytics – 3-page fast sample dashboard

## Pages
1. **Executive Overview** – sample-level volume, fraud rate, fraud-labelled value, average amount and transaction mix.
2. **Risk Hotspots** – category-level fraud counts/rates, hourly pattern, plus a geographical review with state-level transaction volume, fraud count, fraud rate and fraud-labelled transaction value.
3. **Transaction Review** – a capped table of historical fraud-labelled records with CSV export.

## Setup
1. Put `fraudTrain_cleaned.csv` in `data/`.
2. Install dependencies: `py -m pip install -r requirements.txt`
3. Run: `py -m streamlit run app.py`

## Performance
The dashboard reads only the required columns and the first **50,000 rows** of the CSV. This is intentionally a small sample to reduce loading and chart-rendering time. All displayed KPIs and charts describe that sample only; they must not be presented as full-dataset or bank-wide totals.

The first load still reads the CSV from disk. Subsequent reruns use Streamlit's cache. If the CSV changes, clear the Streamlit cache from the app menu or restart the app.

## Interpretation and limitations
- Fraud-labelled transaction value is not confirmed net bank loss.
- Counts by state/category are not risk rates unless compared with the total transaction volume for that group.
- The dashboard is historical descriptive analysis only. It does not train a model, predict fraud, block transactions or send real-time alerts.
- The record review excludes direct customer identifiers and is not a case-management system.
