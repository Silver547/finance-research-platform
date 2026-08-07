# SYSTEM ARCHITECTURE

# Market Intelligence Platform

Version: 1.0

---

# Purpose

This document describes the high-level architecture of the Market Intelligence Platform.

It explains how data moves through the system, how AI agents interact with the pipeline, how information is stored, and how it is presented to users.

The goal is to provide a clear architectural overview without requiring readers to inspect the source code.

---

# System Overview

The platform follows a pipeline-based architecture.

Financial information flows through multiple processing stages before being presented to users as structured market intelligence.

```
News Sources
        │
        ▼
News Ingestion
        │
        ▼
Deduplication
        │
        ▼
AI Tagging
        │
        ▼
AI Impact Analysis
        │
        ▼
Database
        │
        ▼
Daily Report Generation
        │
        ▼
Dashboard
        │
        ▼
Research & RAG
```

Each stage has a single responsibility and can evolve independently.

---

# High-Level Components

The platform consists of six primary subsystems.

## 1. Data Ingestion

Responsible for collecting raw information.

Current sources include:

- RSS feeds
- Macroeconomic datasets
- Stock price data
- Industry reference data

Future sources:

- SEC EDGAR filings
- NSE/BSE disclosures
- Corporate actions
- Earnings transcripts

---

## 2. AI Processing Layer

The AI layer transforms raw information into structured intelligence.

Instead of displaying articles directly, the platform extracts:

- Companies
- Industries
- Sentiment
- Risks
- Opportunities
- Market impact
- Economic relationships

This layer converts unstructured news into structured data.

---

## 3. Database Layer

The database stores:

- News
- AI summaries
- Company mappings
- Industry mappings
- Macro data
- Daily reports
- Research metadata

The database acts as the system's source of truth.

---

## 4. Report Generation

Once all articles have been processed, the Report Agent creates:

- Daily briefing
- Market mood
- Market narrative
- Global drivers
- Risk summary
- Opportunity summary

This produces a single daily market overview.

---

## 5. Dashboard

The Streamlit dashboard presents information through dedicated workspaces.

Current workspaces:

- Today
- Companies
- Industries
- Macro
- Research

Each workspace focuses on answering a specific user question.

---

## 6. Research Layer

The Research layer enables users to explore information more deeply.

It combines:

- Structured AI summaries
- Vector search
- Semantic retrieval
- AI-assisted research

The objective is to support investigation rather than simply display data.

---

# Data Pipeline

The daily workflow follows this sequence.

## Step 1

Fetch news.

---

## Step 2

Remove duplicates.

---

## Step 3

Identify companies and industries.

---

## Step 4

Generate AI impact analysis.

---

## Step 5

Store structured information.

---

## Step 6

Generate the daily market report.

---

## Step 7

Update dashboard data.

---

## Step 8

Refresh research index.

---

# AI Agents

The platform currently contains multiple AI agents.

---

## Tagging Agent

Purpose

Identify relevant companies and industries.

Input

News headline and summary.

Output

Structured company and industry mappings.

---

## Impact Agent

Purpose

Explain why an event matters.

Input

Tagged news article.

Output

- Summary
- Why it matters
- Risks
- Opportunities
- Sentiment
- Classification

---

## Report Agent

Purpose

Generate a daily market briefing.

Input

Processed news from the current day.

Output

- Headline
- Narrative
- Market mood
- Drivers
- Risk
- Opportunity
- Daily briefing

---

# Future AI Agents

Potential future additions include:

- Company Intelligence Agent
- Filing Analysis Agent
- Industry Intelligence Agent
- Macro Intelligence Agent
- Historical Comparison Agent

These are future enhancements rather than current functionality.

---

# Data Flow

The system follows a one-directional flow.

```
External Sources

↓

Raw Data

↓

AI Processing

↓

Structured Database

↓

Reports

↓

Dashboard

↓

User
```

Each stage builds on the previous one.

---

# Dashboard Architecture

The dashboard is organized into dedicated workspaces.

## Today

Daily market intelligence.

---

## Companies

Company-specific intelligence.

---

## Industries

Industry-level analysis.

---

## Macro

Macroeconomic environment.

---

## Research

Deep exploration and AI-assisted investigation.

---

# Design Philosophy

The architecture follows several principles.

## Modular

Each subsystem has a single responsibility.

---

## Explainable

AI outputs should explain decisions rather than simply summarize information.

---

## Structured

Structured data is preferred over free-form text whenever possible.

---

## Scalable

New data sources and AI agents should integrate without requiring major architectural changes.

---

## Research First

The platform exists to improve understanding rather than generate trading signals.

---

# Technology Stack

Frontend

- Streamlit

Backend

- Python

Database

- SQLAlchemy
- SQLite (default)
- PostgreSQL / Supabase (optional)

AI

- Gemini
- OpenRouter
- Ollama

Search

- Chroma Vector Database

Automation

- GitHub Actions

---

# Future Architecture

The long-term architecture will evolve from a dashboard into an integrated Market Intelligence Workspace.

Planned capabilities include:

- Company Workspaces
- Industry Workspaces
- Knowledge Graph
- Historical Event Intelligence
- Filing Analysis
- Cross-linked Research
- Personalized Research

The modular architecture is intended to support these future capabilities without requiring a complete redesign.

---

# Guiding Principle

Every component should contribute to one objective:

**Explain markets, don't just report them.**