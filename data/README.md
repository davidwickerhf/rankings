# Data Directory

This directory contains all raw and processed data files for the ECHR centrality analysis.

## Recent Updates (December 2024)

- **Data Collection**: Completed ECHR case data collection and validation
- **Metadata Processing**: Enhanced case metadata with importance and doctype labels
- **Citation Data**: Processed citation relationships between cases
- **Quality Assurance**: Implemented data validation and error checking

## Directory Structure

### `/ECHR/` - ECHR Network Data

- **edges.csv**: Citation relationships between cases
- **nodes.csv**: Case metadata and attributes

### `/FULL/` - Complete Dataset

- **edgesRefactored.csv**: Standardized edge format
- **nodesRefactored.csv**: Standardized node format

### `/JUDGEMENTS/` - Judgment Analysis

- **judgments_removed_degree_15orless_in_degree_5orless_TOTAL.csv**: Filtered judgments
- **judgments_removed_degree_15orless_in_degree_5orless_TOTAL.xlsx**: Excel version

### `/METADATA/` - Case Metadata

- **echr_metadata.csv**: Complete case metadata
- **edges.csv**: Citation edges
- **nodes.csv**: Case nodes
- **missing_cases.csv**: Cases with missing references

### `/RAW/` - Raw Data Files

- **1959.json** through **2025.json**: Annual case data
- **downloadedEdges.csv**: Downloaded citation data
- **downloadedNodes.csv**: Downloaded case data
- **metadata.csv**: Raw metadata
- **raw.json**: Combined raw data

## Data Sources

- **ECHR Database**: European Court of Human Rights case law
- **Case Metadata**: Importance scores, document types, dates
- **Citation Network**: References between cases

## Current Status

✅ **Completed**: Data collection and validation  
✅ **Completed**: Metadata processing and enrichment  
✅ **Completed**: Citation network construction  
🔄 **In Progress**: Data quality optimization  
📋 **Planned**: Additional data source integration
