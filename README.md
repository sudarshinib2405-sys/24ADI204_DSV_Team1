<div align="center">

# 💳 Credit Card Fraud Detection
### Data Science & Visualization · Team 1 · 24ADI204

**An end-to-end exploratory data analysis pipeline on 1.29M+ real-world credit card transactions — from raw data to cleaned, outlier-handled, and richly visualized fraud insights.**

![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white&style=flat-square)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white&style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-EDA-150458?logo=pandas&logoColor=white&style=flat-square)
![Rows](https://img.shields.io/badge/records-1.29M-informational?style=flat-square)
![Weeks](https://img.shields.io/badge/lab%20weeks-4-orange?style=flat-square)
![License](https://img.shields.io/badge/license-Academic-lightgrey?style=flat-square)

**[📖 About](#-about) · [🎯 Objectives](#-objectives) · [🗂 Dataset](#-dataset) · [🗓 Timeline](#-project-timeline-week-by-week) · [📁 Structure](#-repository-structure) · [🚀 Run](#-how-to-run) · [🔎 Findings](#-key-findings) · [❓ FAQ](#-faq) · [👥 Team](#-team)**

</div>

<br>

## 📖 About

This repository documents a **four-week lab progression** building a complete exploratory data analysis (EDA) workflow for credit card fraud detection, developed for the Data Science & Visualization (24ADI204) course.

Starting from a raw 1.29-million-row transaction dataset, the project moves through data understanding, cleaning, outlier handling, and finally deep univariate, bivariate, and multivariate analysis — surfacing the temporal, geographic, and behavioral patterns that separate fraudulent transactions from legitimate ones.

> 🎯 **Target variable:** `is_fraud` — a **severely imbalanced** binary target (fraud makes up only ~0.58% of all transactions), which shapes the entire analytical and future modeling approach.

<br>

## 🎯 Objectives

- 🔍 Understand the structure, quality, and distribution of a large real-world transaction dataset
- 🧹 Detect and treat outliers and inconsistencies using statistically grounded methods (IQR)
- 📊 Characterize each feature individually before exploring relationships between them
- 🔗 Uncover temporal, geographic, and categorical patterns associated with fraud
- 📐 Quantify class imbalance and its implications for downstream fraud-classification models
- 📝 Produce a clear, reproducible, and well-documented analysis trail across all four weeks

<br>

## 🗂 Dataset

| | |
|---|---|
| **Source** | [Kaggle — Credit Card Transactions Fraud Detection Dataset](https://www.kaggle.com/datasets/kartik2112/fraud-detection) by `kartik2112` |
| **Files used** | `fraudTrain.csv`, `fraudTest.csv` |
| **Size** | **1,296,675 rows × 23 columns** (training set) |
| **Target variable** | `is_fraud` (binary: 0 = legitimate, 1 = fraud) |
| **Key numerical features** | `amt`, `city_pop`, `lat`, `long`, `merch_lat`, `merch_long` |
| **Key categorical features** | `category`, `gender`, `state`, `job` |
| **Other fields** | transaction timestamp, merchant, customer name, address, date of birth, transaction number |

### 📊 Dataset snapshot

| Check | Result |
|---|---|
| Missing values | ✅ None found |
| Duplicate rows | ✅ None found |
| Legitimate transactions | 1,289,169 (**99.42%**) |
| Fraudulent transactions | 7,506 (**0.58%**) |
| `amt` range | \$1.00 – \$28,948.90 (mean ≈ \$70.35, median = \$47.52) |
| `amt` distribution | Strongly right-skewed (skewness ≈ 42.3) |
| `city_pop` distribution | Strongly right-skewed (skewness ≈ 5.6) |

<details>
<summary>⚠️ <b>Note on dataset files in this repo</b></summary>
<br>

The CSVs in <code>archive (2)/</code> and <code>Week 3/fraudTrain_cleaned.csv</code> are tracked via **Git LFS**. Make sure you have [Git LFS](https://git-lfs.com/) installed and run `git lfs pull` after cloning, or download the dataset directly from Kaggle using the link above.

</details>

<br>

## 🗓 Project Timeline (Week-by-Week)

**📊 Week 1: Proposal & Report**  ➡️  **🔍 Week 2: Basic Data Analysis**  ➡️  **🧹 Week 3: Cleaning & Outliers**  ➡️  **📈 Week 4: Full EDA**

| Week | Focus | Deliverables |
|:---:|---|---|
| 1️⃣ | Project proposal & problem framing | 📄 `DSV_Team1_Week1_Lab_Report_CreditCardFraudDetection.docx`<br>📊 `Credit_Card_Fraud_Detection.pptx` |
| 2️⃣ | Dataset structure, statistical & target-variable analysis | 📓 `data_analysis.ipynb` |
| 3️⃣ | Outlier detection (IQR method) & data cleaning / visualization | 📓 `Outlier_Analysis.ipynb`<br>📓 `week3 data_visualization.ipynb`<br>📝 `week3data cleaning report.odt`<br>🔗 `colab_link.md`<br>🧾 `fraudTrain_cleaned.csv` |
| 4️⃣ | Full EDA — univariate, bivariate & multivariate analysis | 📓 `Fraud_Detection_EDA_Univariate_Analysis.ipynb`<br>📓 `Bivariate_Multivariate_EDA.ipynb`<br>📕 `Credit_Card_Fraud_EDA_Report.pdf` |

<br>

## 🧪 Methodology

| Step | What happens |
|---|---|
| **1. Data Understanding** | Load, inspect dimensions, dtypes, and sample records across all supported environments (Kaggle / Colab / Jupyter / VS Code). |
| **2. Data Quality Assessment** | Check for missing values, duplicate rows, constant columns, invalid numeric values, and negative amounts. |
| **3. Outlier Handling** | Apply the **Interquartile Range (IQR)** method to flag and treat outliers in transaction amounts and other skewed numeric fields. |
| **4. Univariate Analysis** | Examine each feature independently — distribution shape, skewness, and class-imbalance of `is_fraud`. |
| **5. Bivariate & Multivariate Analysis** | Correlation matrices, violin/box plots of amount vs. fraud status, category × gender × fraud interactions, hour-of-day fraud-rate heatmaps, and a derived **customer–merchant distance** feature (Haversine formula) compared across fraud classes. |
| **6. Synthesis** | Consolidate patterns into a final report connecting EDA insights to future feature-engineering and modeling decisions. |

<br>

## 📁 Repository Structure

```
24ADI204_DSV_Team1/
│
├── Week 1/                                          🗂 Proposal
│   ├── Credit_Card_Fraud_Detection.pptx
│   └── DSV_Team1_Week1_Lab_Report_CreditCardFraudDetection.docx
│
├── Week 2/                                          🔍 Basic Analysis
│   └── data_analysis.ipynb
│
├── Week 3/                                          🧹 Cleaning & Outliers
│   ├── Outlier_Analysis.ipynb
│   ├── week3 data_visualization.ipynb
│   ├── week3data cleaning report.odt
│   ├── colab_link.md
│   └── fraudTrain_cleaned.csv                       (Git LFS)
│
├── Week 4/                                          📈 Full EDA
│   ├── Fraud_Detection_EDA_Univariate_Analysis.ipynb
│   ├── Bivariate_Multivariate_EDA.ipynb
│   └── Credit_Card_Fraud_EDA_Report.pdf
│
└── archive (2)/                                     📦 Raw dataset
    ├── fraudTrain.csv                                (Git LFS)
    └── fraudTest.csv                                 (Git LFS)
```

<br>

## 🚀 How to Run

<details open>
<summary><b>Option A — Google Colab (recommended, zero setup)</b></summary>
<br>

Open the Week 3 notebook directly in Colab:

➡️ **[Launch in Google Colab](https://colab.research.google.com/drive/17RQqWje2Pausdl7xxV0rCsfPljlTI9sA?usp=sharing)**

</details>

<details>
<summary><b>Option B — Run locally</b></summary>
<br>

```bash
# 1. Clone the repository
git clone https://github.com/sudarshinib2405-sys/24ADI204_DSV_Team1.git
cd 24ADI204_DSV_Team1

# 2. Pull the large dataset files (Git LFS)
git lfs pull

# 3. Install dependencies
pip install pandas numpy matplotlib seaborn jupyter

# 4. Launch Jupyter and open any notebook
jupyter notebook
```

Notebooks auto-detect the dataset path across **Kaggle, Colab, Jupyter, and VS Code** environments, so they run with minimal path changes.

</details>

<details>
<summary><b>Option C — Kaggle Notebook</b></summary>
<br>

Attach the [original Kaggle dataset](https://www.kaggle.com/datasets/kartik2112/fraud-detection) to a new Kaggle notebook and upload any `.ipynb` file from this repo — the loader cells will detect the Kaggle input path automatically.

</details>

<br>

## 🔎 Key Findings

| | Category | Insight |
|:---:|---|---|
| 📦 | **Data Quality** | No missing values and no duplicate rows across all 1,296,675 records — the dataset required no imputation. |
| ⚖️ | **Class Imbalance** | Fraud accounts for only **0.58%** of transactions. Accuracy alone would be a weak evaluation metric — precision, recall, F1, and PR-AUC are needed for any future model. |
| 💰 | **Transaction Amount** | Right-skewed distribution (skewness ≈ 42.3); legitimate vs. fraudulent amount distributions differ in shape and spread. |
| 🕒 | **Temporal Patterns** | Fraud rate varies measurably by hour of day, day of week, and month — extracted via feature engineering on the transaction timestamp. |
| 🗺️ | **Geographic Patterns** | A derived customer–merchant distance (Haversine formula) shows different spread between legitimate and fraudulent transactions. |
| 🏷️ | **Category & Demographics** | Fraud rate varies across transaction category, and further across category × gender combinations. |
| 📈 | **Outliers** | IQR-based detection flags roughly 67K potential outliers in `amt` and 243K in `city_pop`, both consistent with their right-skewed nature. |

📕 Full write-up available in [`Week 4/Credit_Card_Fraud_EDA_Report.pdf`](./Week%204/Credit_Card_Fraud_EDA_Report.pdf)

<br>

## 🛠 Tech Stack

<div align="left">

![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=for-the-badge)
![Pandas](https://img.shields.io/badge/-Pandas-150458?logo=pandas&logoColor=white&style=for-the-badge)
![NumPy](https://img.shields.io/badge/-NumPy-013243?logo=numpy&logoColor=white&style=for-the-badge)
![Matplotlib](https://img.shields.io/badge/-Matplotlib-11557C?style=for-the-badge)
![Seaborn](https://img.shields.io/badge/-Seaborn-3776AB?style=for-the-badge)
![Jupyter](https://img.shields.io/badge/-Jupyter-F37626?logo=jupyter&logoColor=white&style=for-the-badge)
![Google Colab](https://img.shields.io/badge/-Google%20Colab-F9AB00?logo=googlecolab&logoColor=white&style=for-the-badge)

</div>

<br>

## 🧭 Roadmap

- [x] Data understanding & structure analysis
- [x] Data quality assessment (missing values, duplicates)
- [x] Outlier detection & treatment (IQR)
- [x] Univariate analysis of all key features
- [x] Bivariate & multivariate analysis
- [x] Temporal & geographic pattern analysis
- [ ] Feature engineering for modeling
- [ ] Baseline fraud-classification model (e.g., Logistic Regression / Tree-based)
- [ ] Model evaluation with precision, recall, F1, and PR-AUC

<br>

## ❓ FAQ

<details>
<summary><b>Why is accuracy not used as the main metric?</b></summary>
<br>
Because fraud makes up only 0.58% of the data, a model that predicts "not fraud" every single time would still be ~99.4% accurate — while catching zero fraud. Precision, recall, F1-score, and PR-AUC are far more informative for this kind of imbalanced problem.
</details>

<details>
<summary><b>Why IQR for outlier detection instead of Z-score?</b></summary>
<br>
Several numeric features (like <code>amt</code> and <code>city_pop</code>) are strongly right-skewed, so the IQR (1.5× rule) is more robust here than a Z-score approach, which assumes a roughly normal distribution.
</details>

<details>
<summary><b>Where can I find the raw dataset if the CSVs don't download?</b></summary>
<br>
Grab it directly from Kaggle: <a href="https://www.kaggle.com/datasets/kartik2112/fraud-detection">Credit Card Transactions Fraud Detection Dataset</a>, and make sure Git LFS is installed for the copies tracked in this repo.
</details>

<br>

## 🤝 Contributing

This is an academic lab repository for Team 1 (24ADI204). Team members can contribute via pull requests following this pattern:

```bash
git checkout -b week-x/your-feature
# make your changes
git commit -m "Week X: describe your change"
git push origin week-x/your-feature
```

<br>

## 📄 License

This project is submitted as coursework for the **24ADI204 — Data Science & Visualization** lab and is intended for academic/educational use.

<br>

## 👥 Team

**Team 1 · 24ADI204 — Data Science & Visualization**

| Member | Notes |
|---|---|
| Sudarshini B 25BAD116 | Repository owner |
| Suhani 25BAD119 | Contributor |
| Shreya 25BAD105 | Contributor |
| Thanesha V 25BAD125 | Contributor |



<br>

---

<div align="center">

*Built with 📊 and ☕ for the 24ADI204 Data Science & Visualization Lab*

**[⬆ Back to top](#-credit-card-fraud-detection)**

</div>
