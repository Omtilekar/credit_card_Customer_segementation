# Comparative Customer Segmentation Using Credit Card Data

**Course:** Data Mining  
**Author:** Om Tilekar — MS in Data Science  

## Project Overview

Comparative analysis of four clustering algorithms applied to credit card 
behavioral data (8,950 customers, 17 features). Algorithms evaluated:
K-Means, Agglomerative Clustering, DBSCAN, and Gaussian Mixture Models (GMM).

## Results Summary

| Model         | k | Silhouette | Davies-Bouldin | Calinski-Harabasz |
|---------------|---|------------|----------------|-------------------|
| K-Means       | 4 | **0.2099** | 1.6708         | **2245.8**        |
| Agglomerative | 4 | 0.1774     | 1.7218         | 1870.3            |
| DBSCAN        | 3 | 0.1160     | **0.9681***    | 14.5              |
| GMM           | 7 | 0.1644     | 2.3007         | 1334.6            |

*DBSCAN DB index excludes 8.1% noise points — not directly comparable.

**Best model: K-Means (k=4)** — wins 2 of 3 metrics.

## Customer Segments Identified

| Segment | Size | Key Behavior |
|---|---|---|
| Installment Buyers | 2,141 (23.9%) | High installment purchases, best repayment rate |
| Cash-Dependent Users | 2,718 (30.4%) | High cash advances, near-zero purchases, highest risk |
| High-Value Transactors | 2,435 (27.2%) | Highest purchases, credit limit, and payments |
| Low-Engagement Users | 1,656 (18.5%) | Minimal activity across all dimensions |

## Repository Structure
├── data/              # Raw dataset (CC_GENERAL.csv)
├── notebooks/         # Jupyter notebooks (EDA, clustering, profiling)
├── figures/           # All output figures
├── outputs/           # Saved CSVs (scaled data, labels, metrics)
└── report/            # IEEE LaTeX paper

## Setup & Usage

### Requirements
```bash
pip install pandas numpy matplotlib seaborn scikit-learn scipy joblib
```

### Run in order

```bash
# Step 1 — Preprocessing & EDA
jupyter notebook notebooks/EDA.ipynb

# Step 2 — Clustering (all 4 models)
jupyter notebook notebooks/clusturing.ipynb

# Step 3 — Cluster profiling & visualization
jupyter notebook notebooks/final.ipynb
```

### Dataset

Download `CC_GENERAL.csv` from:  
[https://www.kaggle.com/arjunbhasin2013/ccdata](https://www.kaggle.com/arjunbhasin2013/ccdata)  
Place it in the `data/` folder before running notebooks.

## Key Figures

| Figure | Description |
|---|---|
| `fig_all_models_comparison.png` | PCA 2D projections — all 4 algorithms |
| `fig_radar_charts.png` | Behavioral fingerprints per segment |
| `fig_centroid_heatmap.png` | Standardized centroid comparison |
| `fig_kmeans_elbow_silhouette.png` | K-Means k selection |

## References

Full references in `report/credit_card_segmentation.tex`.  
Dataset: Bhasin, A. (2019). Credit Card Dataset for Clustering. Kaggle.