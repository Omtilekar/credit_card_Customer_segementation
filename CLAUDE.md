# Credit Card Customer Segmentation — Build Spec

You are working inside this repo. Build out exactly **three Jupyter notebooks**
in `notebooks/` plus the supporting outputs. Do **not** add extra notebooks,
extra scripts, or refactor things into Python modules unless asked. Keep it
simple — the human wants to read each notebook top to bottom.

## Repo layout (already created — do not change)

```
cc_segmentation/
├── data/
│   ├── raw/CC_GENERAL.csv          # user already placed this
│   └── processed/                  # save cleaned/scaled data here
├── notebooks/
│   ├── 01_EDA.ipynb
│   ├── 02_Clustering.ipynb
│   └── 03_Modeling.ipynb
├── outputs/
│   ├── plots/                      # every figure saved as PNG, dpi=150
│   └── results/                    # CSV/JSON metric tables
├── models/                         # joblib-pickled final model + scaler
├── requirements.txt
└── CLAUDE.md                       # this file
```

## Global conventions

- `RANDOM_STATE = 42` everywhere it applies.
- Read raw data from `../data/raw/CC_GENERAL.csv` (paths are relative to
  `notebooks/`).
- Save every figure with `plt.savefig("../outputs/plots/<descriptive_name>.png",
  dpi=150, bbox_inches="tight")` *before* `plt.show()`.
- Save every metrics table as both `.csv` (for humans) under
  `../outputs/results/`.
- Use `seaborn` for styling: `sns.set_theme(style="whitegrid")` at the top of
  each notebook.
- After each major step, print a one-line summary so the notebook reads like a
  narrative.

---

## Notebook 1 — `01_EDA.ipynb` (Data Information + Preprocessing)

**Purpose:** understand the data, clean it, scale it, and write the processed
matrix to disk so notebooks 2 and 3 can load it directly.

Sections in this order:

1. **Setup** — imports, `RANDOM_STATE`, seaborn theme.
2. **Load data** — `pd.read_csv("../data/raw/CC_GENERAL.csv")`. Print `shape`,
   `dtypes`, `head()`, `describe()`.
3. **Missing values** — `isna().sum()`. The Kaggle CC_GENERAL set has nulls in
   `MINIMUM_PAYMENTS` (~313 rows) and `CREDIT_LIMIT` (1 row). Fill both with
   the column **median** and explain why (right-skewed, robust to outliers).
4. **Drop non-informative columns** — drop `CUST_ID` (it's just an identifier).
5. **Distributions** — for every numeric feature, plot a histogram + KDE in a
   single grid figure. Save as `outputs/plots/feature_distributions.png`.
   Comment on which features are heavily right-skewed.
6. **Outliers** — boxplots in a grid. Save as
   `outputs/plots/feature_boxplots.png`. Note them but do **not** remove rows —
   in customer segmentation, the tails are often the most interesting
   customers. We will rely on scaling + (optional) log transform instead.
7. **Correlation** — `sns.heatmap(df.corr(), annot=False, cmap="coolwarm",
   center=0)`. Save as `outputs/plots/correlation_heatmap.png`. Call out the
   obvious pairs (e.g. `PURCHASES` ↔ `ONEOFF_PURCHASES` /
   `INSTALLMENTS_PURCHASES`, `CASH_ADVANCE` ↔ `CASH_ADVANCE_TRX`).
8. **Skew handling** — apply `np.log1p` to the strongly right-skewed monetary
   columns: `BALANCE`, `PURCHASES`, `ONEOFF_PURCHASES`,
   `INSTALLMENTS_PURCHASES`, `CASH_ADVANCE`, `CASH_ADVANCE_TRX`,
   `PURCHASES_TRX`, `CREDIT_LIMIT`, `PAYMENTS`, `MINIMUM_PAYMENTS`. Keep the
   `*_FREQUENCY` columns as is (they're already 0–1).
9. **Scaling** — fit `StandardScaler` on the cleaned frame, transform it.
10. **PCA (exploratory)** — fit `PCA()` on the scaled matrix, plot cumulative
    explained variance. Save as `outputs/plots/pca_cumulative_variance.png`.
    Note the number of components that reach 0.90 cumulative variance — we'll
    use that for visualization in notebook 2 but **cluster on the full scaled
    matrix**, not on PCA-reduced data (clustering on PCA throws away
    information).
11. **Persist processed data** — save three files into `data/processed/`:
    - `cc_clean.csv` — post-imputation, post-drop-id, pre-scaling (human
      readable).
    - `cc_scaled.npy` — the `np.ndarray` after StandardScaler.
    - `feature_names.json` — list of column names matching the scaled matrix.
    Also `joblib.dump` the fitted scaler to `models/scaler.joblib`.
12. **Wrap-up** — one markdown cell summarising shape after cleaning, what was
    imputed, what was log-transformed, and what the next notebook will do.

---

## Notebook 2 — `02_Clustering.ipynb` (Try all models)

**Purpose:** run every candidate algorithm, sweep their main hyperparameter,
score each with three metrics, and write one consolidated comparison table.

Sections:

1. **Setup + load** — load `data/processed/cc_scaled.npy` and
   `feature_names.json`. Also fit a 2-component PCA *only for plotting*.

2. **K-Means** —
   - Elbow plot: inertia for `k` in 2..10. Save as
     `outputs/plots/kmeans_elbow.png`.
   - Silhouette vs k plot for the same range. Save as
     `outputs/plots/kmeans_silhouette.png`.
   - For each k, record silhouette, Davies-Bouldin, Calinski-Harabasz, inertia
     into a dataframe.
   - Pick the best k by silhouette and plot its clusters in PCA-2D. Save as
     `outputs/plots/kmeans_pca_scatter.png`.

3. **Agglomerative Clustering** —
   - Sweep `n_clusters` in 2..8 with `linkage="ward"`.
   - Record the same three metrics.
   - Plot a dendrogram on a sample of 500 rows (full dendrogram on 9k rows is
     unreadable) using `scipy.cluster.hierarchy.linkage(..., method="ward")`
     and `dendrogram(..., truncate_mode="level", p=5)`. Save as
     `outputs/plots/agglomerative_dendrogram.png`.
   - PCA scatter of the best-by-silhouette result. Save as
     `outputs/plots/agglomerative_pca_scatter.png`.

4. **DBSCAN** —
   - k-distance plot to choose `eps`: sort the distance to the 5th nearest
     neighbour for every point, plot it. Save as
     `outputs/plots/dbscan_k_distance.png`. Pick `eps` at the elbow.
   - Sweep `eps` over 3–4 values near that elbow with `min_samples=5`.
   - Record the three metrics **only over non-noise points** (mask out
     `label == -1` before scoring). Also record `n_clusters_found` and
     `n_noise`.
   - PCA scatter of the best run with noise points coloured grey. Save as
     `outputs/plots/dbscan_pca_scatter.png`.
   - In a markdown cell, be honest: DBSCAN often dumps most CC customers into
     one cluster + a lot of noise. Report what happened, don't sugar-coat it.

5. **Gaussian Mixture Model** —
   - Sweep `n_components` in 2..8 with `covariance_type="full"`.
   - Record silhouette, Davies-Bouldin, Calinski-Harabasz, plus BIC and AIC.
   - Plot BIC + AIC vs n_components. Save as
     `outputs/plots/gmm_bic_aic.png`.
   - PCA scatter of the best-by-silhouette result. Save as
     `outputs/plots/gmm_pca_scatter.png`.

6. **Consolidated comparison** —
   - Build one dataframe `comparison` with columns: `algorithm`, `params`,
     `n_clusters`, `silhouette`, `davies_bouldin`, `calinski_harabasz` (plus
     `n_noise` / `bic` where they apply, with `NaN` elsewhere).
   - Save to `outputs/results/clustering_comparison.csv`.
   - Bar chart comparing the **best** configuration of each algorithm on
     silhouette. Save as `outputs/plots/algorithm_comparison_silhouette.png`.
   - Markdown cell: pick the winning algorithm + parameters, justify it using
     the metric table (higher silhouette + higher CH + lower DB), and call out
     interpretability (e.g. "K-Means with k=4 gives the cleanest, most
     interpretable groupings"). Save this decision as a single-row JSON to
     `outputs/results/best_model_choice.json` with keys `algorithm`, `params`,
     `silhouette`, `davies_bouldin`, `calinski_harabasz`.

---

## Notebook 3 — `03_Modeling.ipynb` (Final model + profiling)

**Purpose:** refit the winner cleanly, profile the clusters in business terms,
and persist everything needed to reuse the model.

Sections:

1. **Setup + load** — load processed data, `feature_names.json`,
   `outputs/results/best_model_choice.json`. Print the choice.
2. **Refit** — instantiate the chosen algorithm with the chosen params and
   `random_state=42` where applicable. Fit on the full scaled matrix. Get
   labels.
3. **Final metrics** — recompute silhouette, Davies-Bouldin,
   Calinski-Harabasz. Save as `outputs/results/final_metrics.json`.
4. **Cluster sizes** — bar plot of cluster sizes. Save as
   `outputs/plots/final_cluster_sizes.png`.
5. **Cluster profiles (the most important part)** —
   - Attach labels to the **un-scaled, un-log-transformed** clean dataframe
     (the one saved as `cc_clean.csv` in notebook 1) so the numbers are
     interpretable in real units (dollars, frequencies).
   - Compute `groupby("cluster").mean()` and save to
     `outputs/results/cluster_profiles.csv`.
   - Heatmap of cluster means, **z-scored across clusters per feature** so the
     colour shows *which cluster is high/low on each feature*. Save as
     `outputs/plots/cluster_profile_heatmap.png`.
   - For each cluster, write a short markdown paragraph naming it (e.g.
     "Cluster 0 — Revolvers: high balance, low full-payment ratio, heavy cash
     advance use") based on which features that cluster is high/low on.
6. **2D visualisation** — PCA-2D scatter coloured by final cluster, with
   cluster centroids marked. Save as `outputs/plots/final_clusters_pca.png`.
7. **Persist the model** — `joblib.dump` the fitted model to
   `models/final_model.joblib`. Also save `models/cluster_labels.npy` (label
   per row in the same order as the processed data).
8. **Conclusion** — one markdown cell: how many segments, what they mean, what
   a bank could do with each one (target the transactors with rewards cards,
   offer the revolvers balance-transfer products, etc.), and the limitations
   (DBSCAN found noise, customers near boundaries, dataset is one snapshot in
   time).

---

## Style rules for the notebooks themselves

- Mix markdown and code cells generously. Every code cell deserves a line or
  two of context above it.
- Don't dump 200-line cells. Break logical steps into separate cells.
- No `print(df)` of the whole frame — use `df.head()` or `df.describe()`.
- All figures: figsize at least (8, 5); titles, axis labels, legends present;
  `plt.tight_layout()` before save.
- Comment any non-obvious line of code.
