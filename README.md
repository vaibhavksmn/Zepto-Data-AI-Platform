# Zepto Data Engineering & AI Assignment

This repository contains the end-to-end implementation of three core data and AI modules for the Zepto analytics and support workflow. The project spans data ingestion, predictive modeling, and a Generative AI support system.

## Repository Structure

```text
zepto-assignment/
├── data_pipeline/         # Module 1: ETL Pipeline & Data Modeling
├── analytics/             # Module 2: EDA & Predictive Modeling
├── support_assistant/     # Module 3: RAG-based LLM Support Service
└── README.md              # Master project overview
Module Overview
Module 1 - Data Pipeline: An ETL script that scrapes live product catalog data, cleans it, applies a fixed baseline currency conversion, and loads it into a normalized SQLite relational database. Includes SQL and Pandas verification.

Module 2 - Analytics Pipeline: A cohesive machine learning workflow on the Titanic dataset. Covers automated missing-value handling, exploratory data analysis (EDA), statistical correlation, hyperparameter tuning, and a side-by-side evaluation of classification and regression models.

Module 3 - Support Assistant: A local, Dockerized GenAI support service built with LangGraph, ChromaDB, and FastAPI. It routes queries based on intent and retrieves grounded context to answer policy questions using a deterministic structured output schema.

Environment & Execution
This project was developed and tested using Python 3.10 and Google Colab. Each module is self-contained with its own dependencies and execution instructions. Please navigate to the specific module's directory to view its dedicated README.md for exact run steps.
