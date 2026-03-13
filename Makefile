PYTHON ?= venv/bin/python

.PHONY: help smoke load networks supporting-results paper-analyses paper-results from-metadata

help:
	@printf '%s\n' \
	  'Available targets:' \
	  '  make smoke               Validate that the active Python scripts import and compile.' \
	  '  make load                Rebuild metadata-derived load outputs under results/load/.' \
	  '  make networks            Rebuild networks/merged-article-edges/ from load outputs.' \
	  '  make supporting-results  Regenerate the supporting statistics table and correlation matrix.' \
	  '  make paper-analyses      Regenerate the paper-facing analysis outputs from fixed total_df.csv bundles.' \
	  '  make paper-results       Run supporting-results and paper-analyses.' \
	  '  make from-metadata       Run load and networks targets.'

smoke:
	$(PYTHON) -m py_compile scripts/generate/*.py scripts/shared/*.py scripts/load/*.py scripts/analysis/*.py

load:
	$(PYTHON) scripts/load/process_metadata.py
	$(PYTHON) scripts/load/extract_edges.py

networks:
	$(PYTHON) scripts/generate/00_generate_merged_article_edge_networks.py

supporting-results:
	$(PYTHON) scripts/generate/01_generate_network_statistics.py
	$(PYTHON) scripts/generate/03_generate_correlation_matrix.py

paper-analyses:
	$(PYTHON) scripts/analysis/01_find_best_high_low.py
	$(PYTHON) scripts/analysis/03_test_paper_composite.py
	$(PYTHON) scripts/analysis/04_test_optimized_threshold_composite.py
	$(PYTHON) scripts/analysis/05_compare_across_network_types.py
	$(PYTHON) scripts/analysis/06_test_low_relevance_priority.py
	$(PYTHON) scripts/analysis/07_compare_priority_approaches.py
	$(PYTHON) scripts/analysis/08_visualize_balanced_overlay.py

paper-results: supporting-results paper-analyses

from-metadata: load networks
