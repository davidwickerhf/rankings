# Reflections

This document consolidates the repository's reflective notes that were
previously spread across separate files on composite rankings, disruption, and
statistical trends.

## Composite Rankings

Two composite ideas were explored during the project.

The first was a weighted geometric mean over normalized centralities. It was
useful as an exploration because it made the complementarity question explicit:
could one measure capture highly relevant judgments while another captured the
lower-relevance tail? In practice, this route was informative but it did not
become part of the paper-traceable workflow. It added another optimization
surface and drifted away from the ranking logic eventually described in the
manuscript.

The second was threshold-based composition. This became the more important line
of work because it aligned with the core empirical question: whether rankings
benefit from combining a measure that is strong at the high-relevance end with a
measure that is stronger lower in the distribution. The main takeaway was not
that one mathematical form solved the problem universally, but that the
high-relevance and low-relevance signals were genuinely complementary.

This is why the active repository now keeps the threshold-based composite
analyses as maintained scripts and archives the weighted-geometric experiment as
historical exploration.

## Disruption

Disruption was worth studying because it behaved differently from the more
standard citation-based centralities.

Most centrality measures in this project correlate negatively with the
relevance-related ground truths: higher centrality tends to align with lower
numerical ground-truth values and therefore greater legal importance.
Disruption often moved in the opposite direction. That made it interesting, but
also harder to interpret in the same framework as PageRank, in-degree, or
degree.

The main lesson was that disruption seemed more sensitive to structurally
isolated or weakly integrated cases and therefore had more value near the
low-relevance end of the distribution than for identifying the strongest
precedents. It was also sensitive to network density. As the graph became
denser, the distinctive signal that disruption relied on weakened.

So disruption remained conceptually useful, but it did not become the dominant
measure in the paper-facing results. The reflection here is that not every
structurally interesting measure translates into a practically strong ranking
signal for precedent value.

## Statistical Trends

Another line of thinking concerned how the centrality measures behaved over time
and across scales rather than only how they ranked cases within one network.

The statistical notes showed that the centrality measures did not all move in
the same way over time. Some increased, some decreased, and the ranges were not
uniformly comparable. This reinforced an important methodological point:
comparing raw centrality magnitudes across measures is often less meaningful
than comparing their relative ranking behavior and their correlation with the
ground truths.

That insight is part of why the active code relies so heavily on Spearman
correlation and rank-based comparisons. The project gradually moved away from
treating centralities as directly commensurable raw values and toward treating
them as competing ranking signals.

## What Changed In The Final Repo

The repository now reflects these lessons more cleanly:

- the active code emphasizes the scripts that directly regenerate the paper-used
  networks, centrality tables, and paper-facing analyses
- exploratory methods and legacy results are archived rather than mixed into the
  active path
- the reflections themselves are consolidated here instead of being spread
  across separate technical notes

The goal of this document is not to present final claims, but to preserve the
reasoning that shaped the final reproducibility package.
