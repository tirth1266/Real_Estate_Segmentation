# ML-Based Buyer Segmentation and Investment Profiling for Real Estate Market Intelligence

Unified Mentor internship project. This project groups real estate clients into behavioural segments using K-Means clustering, validates the result with hierarchical clustering, and presents everything in an interactive Streamlit app.

## 1. Goal

Identify distinct buyer segments from transaction history so that sales, marketing and portfolio teams can target each group differently. Segments are built only from purchase behaviour (how much, how often, what type), not from demographics.

## 2. Data

| File | Rows | Description |
|---|---|---|
| `clients.csv` | 2,000 | Client profile: type, gender, date of birth, country, region, acquisition purpose, satisfaction score, loan applied, referral channel |
| `properties.csv` | 10,000 | Listings across 20 towers: transaction date, unit category, unit number, floor area, sale price, listing status, client reference |

Period covered: Jan 2024 to Dec 2025. Raw files are in `data/raw/`; cleaned and derived files are in `data/processed/`.

## 3. Project Structure

```
Real_Estate_Segmentation/
├── app.py                      # Streamlit dashboard
├── README.md
├── data/
│   ├── raw/                    # clients.csv, properties.csv
│   └── processed/              # clients_clean.csv, props_clean.csv,
│                               # client_segments.csv, segment_summary.csv
└── notebooks/
    ├── 01_inspection.ipynb     # structure, types, missing values
    ├── 02_cleaning.ipynb       # parsing, validation, flags
    ├── 03_eda.ipynb            # exploration and feature selection
    ├── 04_scaling.ipynb        # StandardScaler on clustering features
    ├── 05_kmeans.ipynb         # K-Means, elbow, silhouette, profiling
    └── 06_hierarchical.ipynb   # Ward dendrogram, comparison with K-Means
```

## 4. Method

**Cleaning**
- `sale_price` converted from text (`$1,234.00`) to float.
- `date_of_birth` and `transaction_date` parsed to datetime (0 failures).
- `client_ref` is null for all 2,695 Available listings, which is expected; they are kept.
- No rows dropped; no duplicates; all sold listings join to a client.
- 103 Company clients carry filler gender/DOB values. They are kept and marked with an `is_company` flag.
- Only Sold listings count as real purchases. Available listings carry an asking price only.

**EDA findings**
- Monthly sales volume dropped about 34% from Jan 2025, across all towers and both unit types, with flat prices (about $302/sqft). Treated as a volume-only shift.
- Client type, acquisition purpose, gender, loan applied, referral channel, satisfaction and age show almost no relationship with purchase behaviour (gaps under about 2%).
- `avg_price` and `avg_area` correlate at 0.96, and `total_spend` and `n_purchase` at 0.71, so redundant features were left out of clustering.

**Clustering features** (one row per client, built from Sold listings)

| Feature | Meaning |
|---|---|
| `n_purchase` | Number of units bought |
| `avg_price` | Average sale price |
| `avg_price_per_sqft` | Average price per square foot |
| `pct_office` | Share of purchases that are Office units |

`avg_area` and `total_spend` were kept for profiling only. Features were standardised with `StandardScaler`.

**K-Means**
- Tested k = 2 to 10 using elbow and silhouette plots.
- Silhouette scores are low (0.21 to 0.24), meaning the groups overlap, with a local peak at k = 4. k = 4 was chosen.
- Results are visualised with a 2D PCA projection.

**Hierarchical validation**
- Ward linkage with a dendrogram; 4 clusters cut (sizes 758 / 752 / 385 / 105), silhouette 0.195.
- Agreement with K-Means: Adjusted Rand Index 0.471 (moderate).
- All 50 Portfolio Investors fall into one hierarchical cluster; Residential Premium and Mixed-use also map largely to single clusters; Budget Buyers split across two.

## 5. Segments

| Segment | Clients | Revenue share | Profile |
|---|---|---|---|
| Budget Buyers | 694 | 30% | Lower average price per purchase |
| Residential Premium Buyers | 635 | 33% | 0% Office units, higher-priced residential purchases |
| Mixed-Use Buyers | 621 | 32% | Mix of residential and office units |
| Portfolio Investors | 50 | 5% | About 7.3 purchases per client on average; clearly separate from other groups |

Notes:
- Portfolio Investors are few but buy far more units; 70% were referred through the website.
- Segments barely differ on client type, loan, acquisition purpose or satisfaction, so segment names describe purchase behaviour, not stated intent. Only 34% of Portfolio Investors listed Investment as their acquisition purpose.

## 6. Streamlit App

Run from the project root:

```
streamlit run app.py
```

Opens at `http://localhost:8501`.

- **Sidebar filters:** country, region, acquisition purpose, client type
- **Tabs:** Overview, Investor Behavior, Geographic, Segment Insights

## 7. How to Reproduce

1. Place `clients.csv` and `properties.csv` in `data/raw/`.
2. Install dependencies:
   ```
   pip install pandas numpy matplotlib seaborn scikit-learn scipy streamlit
   ```
3. Run notebooks `01` to `06` in order, using Restart Kernel and Run All Cells. Notebook `05` writes `client_segments.csv` and `segment_summary.csv`.
4. Launch the app (see section 6).

## 8. Limitations

- Low silhouette scores show the segments are not sharply separated; Portfolio Investors is the only clearly distinct group.
- Demographic and survey fields (age, gender, satisfaction, loan, referral) did not explain behaviour, so segmentation relies on four transaction features.
- Dataset covers 24 months; the 2025 volume drop could not be explained from the available fields.
- Company clients have placeholder demographic values and are excluded from age and gender analysis.
- Segment labels are interpretive and should be reviewed with business stakeholders before use.

## 9. Tools

Python, pandas, NumPy, scikit-learn, SciPy, Matplotlib, Seaborn, Streamlit, Jupyter.
