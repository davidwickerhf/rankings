# Rebuttal

We thank the reviewers for their careful reading and constructive feedback. We appreciate the positive assessment of the paper's relevance, clarity, and empirical motivation. The reviews identify three main areas for improvement: clearer positioning relative to prior work, clearer definition of the high-/low-relevance categories, and a more explicit discussion of the scope and limitations of the composite ranking. We agree with these points and will revise the paper accordingly.

## Summary of Revisions

In the revised version, we will:

1. clarify the paper's contribution relative to prior legal citation-network studies;
2. explicitly define how "high relevance" and "low relevance" map to the ground-truth values;
3. revise the description of Figure 3 and correct the Figure 2 caption issue;
4. state more clearly that the composite is an empirically optimized ranking strategy rather than a pure standalone centrality measure;
5. provide anonymized supplementary materials containing the scripts and generated outputs underlying the submission.

## Response to Reviewer 1

### 1. Methodological arbitrariness in balancing and threshold optimization

We agree that balancing and thresholding are modeling choices, and we will make this clearer in the revision. Our aim is not to claim that there is a uniquely correct balancing strategy or threshold. Rather, the contribution is to show that conclusions about centrality performance are sensitive to class imbalance and to whether performance is evaluated separately at the high-relevance and low-relevance ends of the distribution.

We will revise the methods and limitations sections to clarify that:

- balancing is used as an evaluation device to test how class imbalance affects which centrality measures appear strongest;
- the threshold parameter is selected by grid search over `tau in [0.05, 0.95]` in steps of `0.05`;
- the optimized threshold should be interpreted as an empirically selected ranking parameter, not as a theoretically unique value.

### 2. Availability of supplementary materials

We agree that the supplementary materials should have been available during review. We will provide anonymized supplementary materials containing the scripts and generated result files used for the submitted paper, including the high/low performer analysis, the optimized-threshold composite analysis, the low- vs high-priority comparison, and the balanced-network overlay visualizations.

### 3. Practical implications

We appreciate this suggestion and will strengthen the discussion of practical implications. In particular, we will state more directly that:

- centrality evaluation on highly imbalanced legal data can be misleading if the imbalance is ignored;
- no single individual centrality dominates all settings;
- composite ranking strategies combining complementary signals can outperform single metrics across many more subnetworks.

## Response to Reviewer 2

### 1. Composite measure not computable from citation structure alone

We agree with this limitation and will make it more explicit. In the revision, we will clarify that the composite should be understood as an empirically optimized ranking strategy rather than as a pure standalone centrality measure computable from citation structure alone.

At the same time, we will sharpen the statement of contribution. The paper's contribution is not only the proposal of a composite ranking. It is also the demonstration that:

1. class imbalance materially affects conclusions about which centrality measures appear strongest;
2. performance differs between the high-relevance and low-relevance ends of the distribution;
3. combining complementary signals substantially improves performance across subnetworks.

The generated results used in the submission support this directly. In the optimized-threshold analysis, `Degree+Eigenvector` wins `45/66` subnetworks for `importance` and `43/66` for `doctypebranch`, while `Degree+InDegree` wins `45/66` subnetworks for both ground truths. We will make clearer that this is the main empirical takeaway, while also acknowledging that a threshold-free structural estimator would be an important next step.

### 2. Description of Figure 3

We agree that the current description of Figure 3 is too compressed and should be revised. We will rewrite the corresponding passage so that it directly describes what the figure shows: frequency counts over subnetworks, separated by dataset variant and by ground truth. We will also remove the current "2 out of 3" phrasing, which is not the clearest description of the visualized results.

### 3. If Degree performs well at both ends, why is a composite needed?

Degree is indeed one of the most consistently strong individual measures, and we will make that clearer. However, Degree is not uniformly best across all network types and both ground truths. The composite evaluation shows that combining Degree with complementary incoming-citation-based signals improves performance substantially across subnetworks. We will revise the text to make this distinction explicit: Degree is a strong backbone measure, but the composite improves performance by incorporating information captured by other measures such as Eigenvector and In-Degree.

### 4. Explicit definition of high relevance and low relevance

We agree and will add this definition explicitly in the methods section. In our analyses:

- high relevance corresponds to ground-truth value `1`;
- low relevance corresponds to ground-truth values `2` and `3`.

Operationally, this means:

- `Importance`: high relevance = `1`; low relevance = `2-3`;
- `Court Branch`: high relevance = `Grand Chamber (1)`; low relevance = `Chamber / Committee (2-3)`.

Because this distinction is central to the paper, we agree it should be stated explicitly rather than left implicit.

### 5. Figure 2 caption

Thank you. We will correct the caption/reference in the revision.

## Response to Reviewer 3

### 1. Relation to prior work and contribution

We agree that the paper needs to position its contribution more sharply relative to prior legal citation-network work. We will revise the introduction and related-work sections accordingly.

The paper's contribution is not simply another comparison of centrality measures. Rather, it makes three more specific contributions:

1. it shows that class imbalance materially changes which centrality measures appear strongest when evaluated against legal ground truths;
2. it evaluates performance separately at the high-relevance and low-relevance ends of the distribution, rather than relying only on a single overall correlation;
3. it tests composite ranking strategies built from complementary high- and low-relevance signals and shows that these outperform individual measures across many more subnetworks.

We will expand the related-work section to situate these contributions more clearly relative to prior case-law citation-network studies.

### 2. Applying the framework to other datasets

We agree. Applying the framework to additional jurisdictions and citation networks is an important next step and would help assess external validity. In the revision, we will make the domain-specific scope of the current claims clearer and identify cross-jurisdiction validation as an important direction for future work.

## Closing

Overall, we believe the reviewers' comments will improve the paper substantially. The revision will sharpen the contribution, clarify the operational definitions used throughout the analysis, make the limitations of the composite ranking more explicit, and improve reproducibility through anonymized supplementary materials.
