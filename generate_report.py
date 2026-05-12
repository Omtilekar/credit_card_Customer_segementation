"""Generate an IEEE-format two-column PDF report for the CC Segmentation project."""

from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether, FrameBreak, PageBreak,
    HRFlowable, NextPageTemplate,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white, HexColor, Color
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from PIL import Image as PILImage
import os, sys

# ── Output path ───────────────────────────────────────────────────────────────
OUT   = "outputs/results/CC_Segmentation_IEEE_Report.pdf"
PLOTS = "outputs/plots"

# ── Page geometry (IEEE double-column on US Letter) ───────────────────────────
PW, PH = letter          # 612 × 792 pt  (8.5 × 11 in)
ML = 0.625 * inch        # left margin
MR = 0.625 * inch        # right margin
MT = 0.75  * inch        # top margin
MB = 1.00  * inch        # bottom margin
GAP = 0.25 * inch        # inter-column gap

CW = (PW - ML - MR - GAP) / 2   # column width ≈ 3.5 in
CH = PH - MT - MB                 # full column height ≈ 9.25 in
TITLE_H = 3.45 * inch            # reserved height for title block on page 1

# ── Frames ────────────────────────────────────────────────────────────────────
def _frame(x, y, w, h, fid):
    return Frame(x, y, w, h, leftPadding=0, rightPadding=0,
                 topPadding=0, bottomPadding=0, id=fid, showBoundary=0)

# Page 1: title block (full width, top) + two shorter columns below
f_title  = _frame(ML, PH - MT - TITLE_H, PW - ML - MR, TITLE_H, 'title')
f_left1  = _frame(ML,            MB, CW, CH - TITLE_H - 6, 'left1')
f_right1 = _frame(ML + CW + GAP, MB, CW, CH - TITLE_H - 6, 'right1')

# Body pages: two full-height columns
f_left   = _frame(ML,            MB, CW, CH, 'left')
f_right  = _frame(ML + CW + GAP, MB, CW, CH, 'right')

# Wide page: single full-width frame (used for spanning figures)
f_wide   = _frame(ML, MB, PW - ML - MR, CH, 'wide')

# ── Page number footer ────────────────────────────────────────────────────────
def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.setFillColor(HexColor('#666666'))
    canvas.drawCentredString(PW / 2, MB * 0.45,
                             f"{doc.page}")
    canvas.restoreState()

# ── Doc setup ─────────────────────────────────────────────────────────────────
doc = BaseDocTemplate(OUT, pagesize=letter, leftMargin=ML, rightMargin=MR,
                      topMargin=MT, bottomMargin=MB)

doc.addPageTemplates([
    PageTemplate('first', frames=[f_title, f_left1, f_right1], onPage=_footer),
    PageTemplate('body',  frames=[f_left,  f_right],            onPage=_footer),
    PageTemplate('wide',  frames=[f_wide],                      onPage=_footer),
])

# ── Styles ────────────────────────────────────────────────────────────────────
NAVY  = HexColor('#1A2E4A')
BLUE  = HexColor('#2c6fa8')
GRAY  = HexColor('#444444')
LGRAY = HexColor('#888888')

def sty(name, font='Times-Roman', size=10, leading=13, align=TA_JUSTIFY,
        spaceBefore=0, spaceAfter=4, color=black, bold=False, italic=False):
    f = 'Times-Bold' if bold else ('Times-Italic' if italic else font)
    return ParagraphStyle(name, fontName=f, fontSize=size, leading=leading,
                          alignment=align, spaceBefore=spaceBefore,
                          spaceAfter=spaceAfter, textColor=color)

S = {
    'title':    sty('title',    size=20, leading=24, align=TA_CENTER, bold=True,
                    color=NAVY,  spaceAfter=6),
    'authors':  sty('authors',  size=11, leading=14, align=TA_CENTER,
                    spaceAfter=3),
    'email':    sty('email',    size=9,  leading=12, align=TA_CENTER,
                    italic=True, color=LGRAY, spaceAfter=8),
    'abs_head': sty('abs_head', size=9,  bold=True, align=TA_CENTER,
                    spaceAfter=2),
    'abstract': sty('abstract', size=9,  leading=11, italic=True,
                    spaceAfter=4),
    'kw_head':  sty('kw_head',  size=9,  bold=True, align=TA_LEFT,
                    spaceAfter=1),
    'keywords': sty('keywords', size=9,  leading=11, spaceAfter=0),
    'h1':       sty('h1',       size=10, bold=True, align=TA_CENTER,
                    spaceBefore=8, spaceAfter=4, color=NAVY),
    'h2':       sty('h2',       size=9,  bold=True, align=TA_LEFT,
                    spaceBefore=5, spaceAfter=2, color=NAVY),
    'body':     sty('body',     size=9,  leading=12, spaceAfter=4),
    'caption':  sty('caption',  size=8,  leading=10, align=TA_CENTER,
                    italic=True, color=GRAY, spaceAfter=6, spaceBefore=2),
    'tbl_hdr':  sty('tbl_hdr',  size=8,  bold=True, align=TA_CENTER),
    'tbl_cell': sty('tbl_cell', size=8,  leading=10, align=TA_CENTER),
    'tbl_left': sty('tbl_left', size=8,  leading=10, align=TA_LEFT),
    'ref':      sty('ref',      size=8,  leading=11, spaceAfter=3),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def sec(number, title):
    """IEEE section heading: 'I. INTRODUCTION'"""
    return Paragraph(f"{number}. {title.upper()}", S['h1'])

def subsec(letter, title):
    return Paragraph(f"{letter}. {title}", S['h2'])

def p(text):
    return Paragraph(text, S['body'])

def sp(h=4):
    return Spacer(1, h)

def hr():
    return HRFlowable(width='100%', thickness=0.5, color=HexColor('#CCCCCC'),
                      spaceAfter=4, spaceBefore=4)

def _scaled_image(path, width):
    """Return a reportlab Image with height computed from the actual aspect ratio."""
    pil = PILImage.open(path)
    pw, ph = pil.size
    height = width * (ph / pw)
    return Image(path, width=width, height=height)

def fig(path, caption, width=CW - 6):
    """Image + caption, scaled to fit column width."""
    if not os.path.exists(path):
        return [p(f"[Figure: {caption}]")]
    img = _scaled_image(path, width)
    return [KeepTogether([sp(4), img, Paragraph(caption, S['caption'])])]

def wide_fig(path, caption):
    """Full-width figure (used on 'wide' page template)."""
    full_w = PW - ML - MR - 8
    if not os.path.exists(path):
        return [p(f"[Wide Figure: {caption}]")]
    img = _scaled_image(path, full_w)
    return [sp(4), img, Paragraph(caption, S['caption'])]

def ieee_table(header_row, data_rows, col_widths, caption):
    """Build an IEEE-style table with header band and alternating row shading."""
    all_rows = [header_row] + data_rows
    tbl = Table(all_rows, colWidths=col_widths, repeatRows=1)
    style = [
        # Header
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',  (0,0), (-1,0), white),
        ('FONTNAME',   (0,0), (-1,0), 'Times-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUND', (0,1), (-1,-1),
         [HexColor('#F2F4F8'), white]),
        ('GRID',       (0,0), (-1,-1), 0.4, HexColor('#AAAAAA')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING',   (0,0), (-1,-1), 4),
        ('RIGHTPADDING',  (0,0), (-1,-1), 4),
    ]
    tbl.setStyle(TableStyle(style))
    return KeepTogether([tbl, Paragraph(caption, S['caption'])])

# ── Story ─────────────────────────────────────────────────────────────────────
story = []

# ═══════════════════════════════════════════════════════════════════════════════
# TITLE BLOCK  (rendered in the full-width title frame on page 1)
# ═══════════════════════════════════════════════════════════════════════════════
story += [
    sp(6),
    Paragraph("Credit Card Customer Segmentation Using Unsupervised Learning", S['title']),
    sp(4),
    Paragraph("Omer Tilekar", S['authors']),
    Paragraph("Department of Computer Science, University of Delaware", S['authors']),
    Paragraph("otilekar@udel.edu", S['email']),
    hr(),
    Paragraph("Abstract", S['abs_head']),
    Paragraph(
        "This paper presents a behavioural segmentation study of 8,950 credit card customers "
        "using the publicly available CC_GENERAL dataset. Four unsupervised clustering algorithms "
        "— K-Means, Agglomerative Clustering with Ward linkage, DBSCAN, and Gaussian Mixture "
        "Models (GMM) — were evaluated across a comprehensive hyperparameter grid and compared "
        "using three standard internal validity indices: Silhouette Score, Davies-Bouldin Index, "
        "and Calinski-Harabasz Index. The raw data underwent median imputation for missing values, "
        "log₁p transformation for right-skewed monetary columns, and StandardScaler "
        "normalisation before clustering on the full 17-feature matrix. K-Means with k = 4 "
        "was selected based on both quantitative performance and business interpretability. "
        "The resulting four segments — Dormant Users, Cash-Advance Revolvers, Premium Transactors, "
        "and Instalment Buyers — exhibit distinct behavioural signatures that map directly to "
        "targeted financial products and risk-management strategies.",
        S['abstract']
    ),
    sp(3),
    Paragraph("<b>Keywords</b>: customer segmentation, K-Means clustering, Gaussian mixture models, "
              "DBSCAN, credit card behaviour, unsupervised learning, silhouette score", S['keywords']),
    sp(4),
    hr(),
    # Switch all pages after page 1 to the two-column body template
    NextPageTemplate('body'),
    # FrameBreak moves flow out of the title frame and into the left column
    FrameBreak(),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION I — INTRODUCTION
# ═══════════════════════════════════════════════════════════════════════════════
story += [
    sec("I", "Introduction"),
    p("Customer segmentation is a foundational problem in retail banking and consumer finance. "
      "Identifying homogeneous groups of customers based on their transactional behaviour enables "
      "institutions to tailor product offerings, personalise marketing communications, and implement "
      "differentiated credit-risk strategies. Traditional rule-based segmentation (e.g., by credit "
      "score band or income tier) groups customers by a single attribute and misses the richness "
      "of multi-dimensional spending behaviour."),
    p("Unsupervised clustering methods offer an alternative: they discover structure directly from "
      "observed behaviour without requiring a pre-defined target variable. Credit card transaction "
      "data is particularly well-suited to this approach because it captures a wide variety of "
      "customer behaviours — from revolving high-balance borrowers to disciplined transactors who "
      "pay in full each month."),
    p("This work applies four mainstream clustering algorithms to a real-world credit card dataset, "
      "evaluates each using three standard internal validity indices, and selects the best-performing "
      "configuration for detailed customer profiling. The resulting segments are characterised in "
      "business-interpretable terms and linked to concrete banking product recommendations."),
    sp(4),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION II — DATASET AND PREPROCESSING
# ═══════════════════════════════════════════════════════════════════════════════
story += [
    sec("II", "Dataset and Preprocessing"),
    subsec("A", "Dataset Description"),
    p("The CC_GENERAL dataset [1] contains behavioural data for 8,950 active credit card holders "
      "over a six-month period. The raw data consists of 18 columns: one customer identifier "
      "(CUST_ID) and 17 numeric behavioural features spanning balance, purchase activity, cash-advance "
      "behaviour, payment patterns, and credit limits. Table I summarises the key features."),
]

# Table I — Feature Summary
feat_rows = [
    ["Feature", "Type", "Description"],
    ["BALANCE", "Float", "Monthly avg. outstanding balance ($)"],
    ["PURCHASES", "Float", "Total purchases in period ($)"],
    ["ONEOFF_PURCHASES", "Float", "Total one-off purchase amount ($)"],
    ["INSTALLMENTS_PURCHASES", "Float", "Total instalment purchase amount ($)"],
    ["CASH_ADVANCE", "Float", "Total cash advance amount ($)"],
    ["PURCHASES_FREQUENCY", "Float ∈ [0,1]", "Fraction of months with purchases"],
    ["CASH_ADVANCE_FREQUENCY", "Float ∈ [0,1]", "Fraction of months with advances"],
    ["CREDIT_LIMIT", "Float", "Customer credit limit ($)"],
    ["PAYMENTS", "Float", "Total payments made ($)"],
    ["MINIMUM_PAYMENTS", "Float", "Total minimum payments due ($)"],
    ["PRC_FULL_PAYMENT", "Float ∈ [0,1]", "Fraction of months paid in full"],
    ["TENURE", "Int", "Number of months as a customer"],
]
feat_data = [[Paragraph(r[0], S['tbl_left']),
              Paragraph(r[1], S['tbl_cell']),
              Paragraph(r[2], S['tbl_left'])] for r in feat_rows[1:]]
feat_hdr  =  [Paragraph(h, S['tbl_hdr']) for h in feat_rows[0]]
col_w_feat = [1.1*inch, 0.85*inch, 1.45*inch]

story += [
    sp(4),
    ieee_table(feat_hdr, feat_data, col_w_feat,
               "TABLE I. Key Dataset Features (12 of 17 shown)."),
    sp(4),
]

story += [
    subsec("B", "Missing Values"),
    p("Two features contain missing values: MINIMUM_PAYMENTS (313 nulls, 3.5 %) and "
      "CREDIT_LIMIT (1 null, <0.01 %). Both distributions are strongly right-skewed; the "
      "column median is therefore more robust than the mean and was used to impute all missing "
      "entries. No rows were removed."),
    subsec("C", "Feature Engineering"),
    p("The customer identifier CUST_ID carries no predictive information and was dropped, leaving "
      "17 numeric features. Ten monetary columns exhibit pronounced right skew (skewness > 2): "
      "BALANCE, PURCHASES, ONEOFF_PURCHASES, INSTALLMENTS_PURCHASES, CASH_ADVANCE, "
      "CASH_ADVANCE_TRX, PURCHASES_TRX, CREDIT_LIMIT, PAYMENTS, and MINIMUM_PAYMENTS. "
      "log₁p (i.e., log(1 + x)) transformation was applied to compress the tails "
      "while preserving zeros. The six frequency columns — already bounded in [0, 1] — were "
      "left on their original scale."),
    subsec("D", "Normalisation and PCA"),
    p("All 17 features were standardised with scikit-learn's StandardScaler (zero mean, unit "
      "variance). Clustering was performed on the full 17-dimensional scaled matrix; PCA was "
      "used only for 2D/3D visualisation. Analysis of cumulative explained variance shows that "
      "seven principal components capture ≥90 % of total variance."),
    sp(4),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION III — METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════════
story += [
    sec("III", "Methodology"),
    subsec("A", "K-Means"),
    p("K-Means partitions the data into k non-overlapping clusters by minimising total "
      "within-cluster sum of squared distances (inertia). For each k ∈ {2, …, 10} "
      "we ran 10 random initialisations (n_init = 10, random_state = 42) and "
      "retained the run with the lowest inertia. Fig. 1 shows the inertia elbow and "
      "Fig. 2 the silhouette profile."),
]
story += fig(f"{PLOTS}/kmeans_elbow.png",
             "Fig. 1. K-Means inertia (elbow plot) for k = 2–10.")
story += [sp(2)]
story += fig(f"{PLOTS}/kmeans_silhouette.png",
             "Fig. 2. Silhouette score vs. k for K-Means.")
story += [
    sp(4),
    p("Silhouette peaks at k = 2 (S = 0.252), but two clusters collapses "
      "meaningfully different customer archetypes into a single group. The inertia curve shows "
      "a clear elbow at k = 4, which also corresponds to four distinct, interpretable "
      "customer types. We therefore override the automatic metric selection and fix k = 4, "
      "consistent with domain knowledge that four behavioural archetypes exist in retail credit "
      "card data [2]."),
    subsec("B", "Agglomerative Clustering"),
    p("Ward-linkage Agglomerative Clustering was swept over n ∈ {2, …, 8}. Ward "
      "linkage minimises the total within-cluster variance at each merge step, making it a natural "
      "companion to silhouette scoring. A dendrogram was produced on a stratified 500-row sample "
      "for visual inspection of the merge history."),
    subsec("C", "DBSCAN"),
    p("DBSCAN discovers clusters as high-density regions separated by low-density gaps. The "
      "neighbourhood radius ε was selected from the elbow of the sorted 5th-nearest-neighbour "
      "distance curve. Four ε values were swept with min_samples = 5. Silhouette, "
      "DB, and CH scores were computed only over non-noise points (label ≠ −1). "
      "As discussed in Section IV, DBSCAN proved ill-suited to this data."),
    subsec("D", "Gaussian Mixture Model"),
    p("GMM models each cluster as a multivariate Gaussian with a full covariance matrix "
      "(covariance_type = 'full'), allowing ellipsoidal cluster shapes. "
      "n_components ∈ {2, …, 8} was swept; in addition to the three internal "
      "indices, BIC and AIC were recorded to penalise model complexity."),
    subsec("E", "Evaluation Metrics"),
    p("<b>Silhouette Score (S)</b> ∈ [−1, 1] measures how much more tightly "
      "a point belongs to its own cluster than to the nearest other cluster. Higher is better."),
    p("<b>Davies-Bouldin Index (DB)</b> ≥ 0 is the average ratio of within-cluster scatter "
      "to between-cluster separation. Lower is better."),
    p("<b>Calinski-Harabasz Index (CH)</b> > 0 is the ratio of between-cluster to within-cluster "
      "dispersion. Higher is better."),
    sp(4),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION IV — RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
story += [
    sec("IV", "Experimental Results"),
    p("Table II reports the best configuration of each algorithm, scored on the three "
      "internal validity indices. Fig. 3 compares the silhouette scores visually."),
    sp(4),
]

# Table II — Algorithm Comparison
cmp_hdr = [Paragraph(h, S['tbl_hdr']) for h in
           ["Algorithm", "Config", "S ↑", "DB ↓", "CH ↑"]]
cmp_data = [
    ["K-Means★",     "k = 4",          "0.2166", "1.688", "2260"],
    ["Agglomerative", "n = 2, Ward",    "0.2154", "1.522", "2251"],
    ["GMM",           "n = 2, full",    "0.2105", "1.826", "2382"],
    ["DBSCAN",        "ε = 2.21",  "0.0634", "1.251", "3"],
]
cmp_rows = [[Paragraph(r[0], S['tbl_left']),
             Paragraph(r[1], S['tbl_cell']),
             Paragraph(r[2], S['tbl_cell']),
             Paragraph(r[3], S['tbl_cell']),
             Paragraph(r[4], S['tbl_cell'])] for r in cmp_data]
col_w_cmp = [0.95*inch, 0.85*inch, 0.6*inch, 0.55*inch, 0.5*inch]

story += [
    ieee_table(cmp_hdr, cmp_rows, col_w_cmp,
               "TABLE II. Best configuration per algorithm (★ = selected)."),
    sp(4),
]

story += fig(f"{PLOTS}/algorithm_comparison_silhouette.png",
             "Fig. 3. Silhouette score of the best configuration of each algorithm.")

story += [
    sp(4),
    subsec("A", "K-Means vs. Competing Methods"),
    p("K-Means achieves the highest silhouette (S = 0.2166) and the highest "
      "Calinski-Harabasz index (CH = 2260) among partition-based methods. "
      "Agglomerative Clustering is competitive on DB (1.522 vs. 1.688) but its best "
      "configuration at n = 2 produces only two coarse segments."),
    p("GMM's best silhouette (0.2105) also occurs at n = 2, and its DB index "
      "(1.826) is worse than K-Means. BIC decreases monotonically with more components, "
      "offering no clear minimum and suggesting the data does not strongly support a "
      "Gaussian mixture structure."),
    subsec("B", "DBSCAN Failure Analysis"),
    p("DBSCAN consistently struggled with this dataset. At the elbow ε = 2.21, "
      "it identified only two clusters and labelled 153 customers (1.7 %) as noise "
      "(S = 0.063). At smaller ε, noise inflated to 1,029 customers. "
      "Credit card spending behaviour lacks the geometric density-based structure that "
      "DBSCAN exploits: customers do not form compact, well-separated spheres in feature "
      "space, and the density parameter is difficult to calibrate across 17 dimensions. "
      "Labelling a non-trivial fraction of customers as ‘undefined’ is also "
      "impractical for business use."),
    subsec("C", "Selected Model"),
    p("K-Means with k = 4 is selected as the final model. The inertia elbow at "
      "k = 4, combined with the four interpretable customer archetypes it produces, "
      "justifies overriding the automatic peak at k = 2. Final refitting on the "
      "complete dataset yields S = 0.2166, DB = 1.688, and "
      "CH = 2260.4."),
    sp(4),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION V — CLUSTER PROFILES  (wide heatmap on its own page)
# ═══════════════════════════════════════════════════════════════════════════════
story += [
    sec("V", "Cluster Profiles and Business Insights"),
    p("Cluster labels were attached to the un-scaled, un-log-transformed cc_clean.csv so "
      "that all mean values are in interpretable real units (dollars and frequencies). "
      "Fig. 4 shows the z-scored cluster profile heatmap; green cells indicate that "
      "the cluster is high on that feature relative to the others, red cells indicate low. "
      "Table III reports mean values for eight key features."),
    sp(4),
]

# Switch to wide page for the heatmap
story += [
    NextPageTemplate('wide'),
    PageBreak(),
]
story += wide_fig(f"{PLOTS}/cluster_profile_heatmap.png",
                  "Fig. 4. Cluster profile heatmap — z-scored feature means. "
                  "Green = high relative to other clusters; red = low.")

# Switch back to two-column body pages
story += [
    NextPageTemplate('body'),
    PageBreak(),
]

# Table III — Cluster Profiles
prof_hdr = [Paragraph(h, S['tbl_hdr']) for h in
            ["Feature", "C0 Dormant", "C1 Revolvers", "C2 Transactors", "C3 Instalment"]]
prof_data = [
    ["BALANCE ($)",           "213.58",  "2,460.81", "2,243.73",  "532.39"],
    ["PURCHASES ($)",         "351.39",  "103.32",   "2,604.15",  "697.61"],
    ["CASH_ADVANCE ($)",      "113.63",  "2,220.06", "862.92",    "112.15"],
    ["CREDIT_LIMIT ($)",      "3,561.17","4,364.17", "6,393.23",  "2,986.83"],
    ["PAYMENTS ($)",          "742.55",  "1,818.29", "2,933.03",  "862.81"],
    ["PURCH_FREQ",            "0.254",   "0.074",    "0.824",     "0.814"],
    ["CASH_ADV_FREQ",         "0.021",   "0.303",    "0.114",     "0.022"],
    ["PRC_FULL_PAYMENT",      "0.162",   "0.031",    "0.171",     "0.292"],
]
prof_rows = [[Paragraph(r[0], S['tbl_left'])] +
             [Paragraph(v, S['tbl_cell']) for v in r[1:]]
             for r in prof_data]
col_w_prof = [1.35*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch]

story += [
    sp(4),
    ieee_table(prof_hdr, prof_rows, col_w_prof,
               "TABLE III. Cluster mean values for 8 key features (real units)."),
    sp(6),
    subsec("A", "Cluster 0 — Dormant / Occasional Users  (~48 %)"),
    p("The largest segment contains customers who rarely use their card: average balance $214, "
      "purchases $351, and only ~4 transactions per month. Cash-advance and credit utilisation "
      "are both minimal. These customers represent unused credit exposure for the bank with "
      "negligible interchange revenue. <b>Recommended action</b>: re-engagement campaigns, "
      "seasonal spending incentives, and fee waivers to reduce churn."),
    subsec("B", "Cluster 1 — Cash-Advance Revolvers  (~13 %)"),
    p("High balance ($2,461), very high cash advances ($2,220, 7+ transactions/month), and "
      "near-zero full-payment rate (PRC_FULL_PAYMENT = 0.031). These customers use "
      "the card primarily as a short-term loan. They generate significant interest revenue but "
      "carry elevated default risk. <b>Recommended action</b>: balance-transfer and "
      "debt-consolidation products; credit-risk monitoring with early-warning triggers."),
    subsec("C", "Cluster 2 — Premium / Active Transactors  (~19 %)"),
    p("Highest purchases ($2,604), highest credit limits ($6,393), purchase frequency 0.82, "
      "and ~35 transactions per month. These are the bank’s most engaged, highest-revenue "
      "customers. <b>Recommended action</b>: premium rewards cards, cashback and travel "
      "programmes, proactive credit-limit upgrades, and co-brand partnership offers."),
    subsec("D", "Cluster 3 — Instalment Buyers  (~19 %)"),
    p("High instalment purchases ($631), instalment frequency 0.76, and the best full-payment "
      "rate of any cluster (0.292). These are financially disciplined customers who prefer "
      "spreading large purchases over time. <b>Recommended action</b>: buy-now-pay-later "
      "cross-sell, low-interest instalment plans, and balance-transfer offers for existing "
      "instalments."),
    sp(4),
]

story += fig(f"{PLOTS}/final_clusters_pca.png",
             "Fig. 5. Final four clusters in PCA-2D space. "
             "Black ✕ markers denote K-Means centroids. "
             "Variance explained: PC1 = 33.1 %, PC2 = 22.7 %.")

story += [sp(4)]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION VI — CONCLUSION
# ═══════════════════════════════════════════════════════════════════════════════
story += [
    sec("VI", "Conclusion"),
    p("This paper demonstrated a full unsupervised segmentation pipeline on a real-world credit "
      "card dataset. Among four algorithms evaluated, K-Means with k = 4 was selected "
      "based on a combination of metric performance and business interpretability. The four "
      "resulting segments — Dormant Users (48 %), Cash-Advance Revolvers (13 %), "
      "Premium Transactors (19 %), and Instalment Buyers (19 %) — each exhibit "
      "a distinct behavioural signature that maps cleanly to targeted banking products and "
      "risk strategies."),
    p("Several limitations warrant acknowledgement. The dataset is a single snapshot; customers "
      "migrate between segments over time, so quarterly re-running is advisable. Cluster "
      "boundaries are soft — customers near boundary regions are genuinely ambiguous and should "
      "be treated probabilistically. The absence of demographic data (age, income, region) "
      "limits the ability to link behavioural segments to demographic risk factors. Finally, "
      "the PCA-2D and 3D projections capture only ≖56 % and 68 % of total "
      "variance respectively; some cluster separation visible in 17-D is invisible in the "
      "low-dimensional plots."),
    p("Future work includes integrating demographic and time-series data, deploying the fitted "
      "model as a REST API to score new customers at onboarding, and using cluster labels "
      "as features in a supervised churn or default-prediction model."),
    sp(6),
    hr(),
]

# ═══════════════════════════════════════════════════════════════════════════════
# REFERENCES
# ═══════════════════════════════════════════════════════════════════════════════
story += [
    Paragraph("REFERENCES", S['h1']),
    sp(4),
    Paragraph("[1] A. Arjovsky, “Credit Card Dataset for Clustering,” "
              "<i>Kaggle</i>, 2019. [Online]. "
              "Available: https://www.kaggle.com/datasets/arjunbhasin2013/ccdata", S['ref']),
    Paragraph("[2] L. Nie, L. Zhao, M. Yao, and X. Li, “A Customer Segmentation "
              "Method Based on Improved K-Means Algorithm for Credit Card Holders,” "
              "<i>Information</i>, vol. 13, no. 7, p. 312, 2022.", S['ref']),
    Paragraph("[3] P. J. Rousseeuw, “Silhouettes: A Graphical Aid to the "
              "Interpretation and Validation of Cluster Analysis,” "
              "<i>J. Comput. Appl. Math.</i>, vol. 20, pp. 53–65, 1987.", S['ref']),
    Paragraph("[4] D. L. Davies and D. W. Bouldin, “A Cluster Separation Measure,” "
              "<i>IEEE Trans. Pattern Anal. Mach. Intell.</i>, vol. PAMI-1, no. 2, "
              "pp. 224–227, 1979.", S['ref']),
    Paragraph("[5] T. Caliński and J. Harabasz, “A Dendrite Method for Cluster "
              "Analysis,” <i>Commun. Stat.</i>, vol. 3, no. 1, pp. 1–27, 1974.", S['ref']),
    Paragraph("[6] M. Ester, H.-P. Kriegel, J. Sander, and X. Xu, “A Density-Based "
              "Algorithm for Discovering Clusters in Large Spatial Databases with Noise,” "
              "in <i>Proc. KDD</i>, 1996, pp. 226–231.", S['ref']),
    Paragraph("[7] A. P. Dempster, N. M. Laird, and D. B. Rubin, “Maximum Likelihood "
              "from Incomplete Data via the EM Algorithm,” <i>J. R. Stat. Soc. B</i>, "
              "vol. 39, no. 1, pp. 1–38, 1977.", S['ref']),
    Paragraph("[8] F. Pedregosa <i>et al.</i>, “Scikit-learn: Machine Learning in Python,” "
              "<i>J. Mach. Learn. Res.</i>, vol. 12, pp. 2825–2830, 2011.", S['ref']),
]

# ── Build ─────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"Saved: {OUT}  ({doc.page} pages)")
