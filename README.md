# three-ex-plus-one

*Exploring the Collatz Conjecture — 2022 and 2026*

---

## What This Is

This repository contains two bodies of work on the Collatz conjecture, separated by four years.

**2022 — The Original Investigation**

In July 2022, the original author built a Dockerized R analysis pipeline to explore the Collatz map through a specific lens: rather than visualizing individual trajectories, the work grouped integers by stopping time, collected all members of each equivalence class, and overlaid their complete trajectories simultaneously. The resulting visualizations — stored as high-resolution TIFFs in `image_files/` — revealed unexpected geometric structure: cathedral-shaped trajectory profiles, sub-harmonic peak spacing, and apparent internal stratification within equivalence classes.

The core approach: build a z/k matrix where z contains starting values and k records their stopping times, then visualize the population geometry of each stopping-time equivalence class. This inversion of the standard Collatz visualization — going to the population rather than the individual — was the original contribution.

The original R code is preserved exactly as written in 2022 in `functions/` and `analysis_files/`. It is the origin document. It does not change.

**2026 — The Formal Investigation**

In March 2026, the original observations were scaled, quantified, and subjected to formal statistical analysis using Python. 100,000 random odd integers from [1, 1,000,000] were analyzed (random seed 1993). The visual patterns from 2022 were confirmed, extended, and formalized into two statistically robust findings.

---

## The Two Main Findings

### Finding 1 — Universal Internal Stratification with 2-adic Correspondence

Every one of the 30 most populated stopping-time equivalence classes in the sample exhibits internal stratification into distinct subfamilies, characterized by bimodal peak-iteration distributions. Subfamily membership is predicted by the 2-adic valuation profile of the starting integer.

- 30/30 classes stratified (Hartigan dip test, all significant)
- 30/30 classes show significant stepwise 2-adic profile separation
- Convergence node density increases monotonically with stopping time depth (Spearman rho = 0.7495, p = 1.88e-6)
- Inter-peak spacing increases monotonically with stopping time depth (Spearman rho = 0.8954, p = 2.39e-11)

**Plain language:** Numbers that take the same number of steps to reach 1 are not a homogeneous group. They split into distinct families with different shaped trajectories. Those families are algebraically characterized by a specific property of the starting number — how the powers of 2 distribute along its path. This structure is universal across all modal equivalence classes tested.

### Finding 2 — Structural Peak Magnitude-Timing Relationship

Within stopping-time equivalence classes, trajectories that peak later in their journey peak higher in magnitude. This relationship is independent of starting number size and is structural to the 3x+1 map itself.

- Mean raw within-class Pearson r = 0.335 (30/30 positive, 30/30 significant, p = 8.65e-20)
- Mean partial r controlling for original_number = 0.372 (strengthens, not weakens)
- Mean partial r controlling for log10(original_number) = 0.373 (mean absolute change 0.004 — heavy-tail effects ruled out)
- Spearman rank-based partial r = 0.694 (30/30 positive, 30/30 significant, p = 9.69e-15)
- Starting number magnitude acts as suppressor: positively predicts peak_value (mean r = 0.210) but negatively predicts peak_iteration (mean r = -0.077, 27/30 classes)

**Plain language:** Within any group of numbers that share a stopping time, the ones that take longer to reach their maximum value reach a higher maximum. This is not because they started larger — it is because the Collatz map itself requires more steps to generate larger peaks. The road determines the mountain, not the traveler's size.

---

## Repository Structure

```
functions/          Original 2022 R functions
analysis_files/     Original 2022 R analysis scripts
image_files/        Original 2022 TIFF visualizations (the origin images)
data_files/         Original 2022 experiment data
python/             2026 Python analysis engine and scripts
output/             2026 computational outputs, figures, and CSVs
findings/           Written findings reports
```

---

## Reproducibility

All 2026 analyses use random seed 1993. The full pipeline runs in approximately 6 minutes on a modern CPU. Dependencies: numpy, pandas, matplotlib, scipy, scikit-learn, seaborn, tqdm.

To reproduce:
```bash
cd python/analysis
python collatz_geometric_analysis.py
python collatz_partial_correlation_analysis.py
python collatz_partial_correlation_robustness.py
```

The original 2022 R analysis is containerized via Docker:
```bash
./build_run_docker.sh
```

---

## On the Origin of This Work

The visual approach — equivalence class population overlay — was developed in July 2022 by Brian Daniel Farin, a statistician and software engineer, as a private mathematical exploration. The original TIFFs in `image_files/` are the first record of the findings. They sat unformalized for four years.

The 2026 formal analysis was conducted in March 2026, the night the author decided the work deserved to be presented to the world.

The findings are dedicated to Malky.

---

## Status

The formal findings are being prepared for submission as an observation note to arXiv (math.DS / math.NT).
