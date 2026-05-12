# Credit Card Customer Segmentation

Compare clustering techniques (K-Means, Agglomerative, DBSCAN, GMM) on the
Kaggle `CC_GENERAL` credit card dataset and pick the most meaningful
segmentation.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m ipykernel install --user --name cc-seg
```

Place the raw data at `data/raw/CC_GENERAL.csv` (already there in your case).

## Running the project

Open the notebooks in this order in VS Code:

1. `notebooks/01_EDA.ipynb` — data information + preprocessing.
   Produces `data/processed/cc_scaled.npy`, `cc_clean.csv`,
   `feature_names.json`, and `models/scaler.joblib`.

2. `notebooks/02_Clustering.ipynb` — runs all four candidate algorithms,
   sweeps their main hyperparameter, and writes
   `outputs/results/clustering_comparison.csv` plus
   `outputs/results/best_model_choice.json`.

3. `notebooks/03_Modeling.ipynb` — refits the winner, profiles each cluster
   in business terms, saves the model to `models/final_model.joblib`.

All plots → `outputs/plots/`. All metric tables → `outputs/results/`.

## Using with Claude Code

Open this repo in VS Code, launch Claude Code, and ask it to:

> Read `CLAUDE.md` and build the three notebooks exactly as specified.

`CLAUDE.md` contains the full per-notebook spec (sections, plots to save,
files to write).

## Structure

```
.
├── data/
│   ├── raw/CC_GENERAL.csv          # your raw data
│   └── processed/                  # written by notebook 1
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_Clustering.ipynb
│   └── 03_Modeling.ipynb
├── outputs/
│   ├── plots/                      # all PNGs
│   └── results/                    # all CSV/JSON
├── models/                         # fitted scaler + final model
├── requirements.txt
├── CLAUDE.md                       # build spec for Claude Code / Codex
└── README.md
```
