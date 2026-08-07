# Sprint 02 – Dashboard Experience Polish

Status: Planned

---

# Objective

Transform the Today page from a dashboard that presents information into a workspace that communicates today's market within 30 seconds.

No new functionality should be introduced.

This sprint focuses entirely on presentation, usability, and information hierarchy.

---

# Scope

Included

- Hero
- Market Snapshot
- Global Drivers
- Economic Ripple
- Market Movers
- Continue Research
- Latest Dispatches

Excluded

- Company Page
- Industries Page
- Macro Page
- Research Page
- Backend
- Database
- AI prompts
- Report generation
- Navigation

---

# Sprint Goal

When a user opens the Today page, they should immediately understand:

- What happened today?
- Why markets are moving?
- What is the biggest risk?
- What is the biggest opportunity?
- Which companies and sectors deserve attention?
- How India is affected?

without reading multiple paragraphs.

---

# Design Goals

Reduce reading.

Increase scanning.

Improve visual hierarchy.

Improve whitespace.

Reduce cognitive load.

Maintain analytical depth.

---

# Implementation Tasks

## Hero

Keep:

- Mood
- Headline
- Confidence
- Importance
- Read Full Story

Replace long narrative with:

Key Points

Maximum five bullets.

---

## Market Snapshot

Replace paragraphs with structured summaries.

Top Risk

- Title
- Severity
- Affected sectors

Top Opportunity

- Title
- Confidence
- Beneficiaries

---

## Driver Cards

Each card should contain:

- Driver
- Trend
- Importance
- Confidence
- Impacted sectors

Cards should have equal heights.

---

## Economic Ripple

Represent information visually.

Preferred flow:

Global Event

↓

Transmission

↓

India

↓

Sector

↓

Company

Detailed explanation belongs inside an expander.

---

## Market Movers

Compact rows.

Display:

Company

Direction

Reason

No paragraphs.

---

## Continue Research

Display as research chips/cards.

Avoid long descriptions.

---

## Latest Dispatches

Display only:

Headline

Classification

Source

Time

Limit to five.

---

# Engineering Constraints

No backend modifications.

No schema changes.

No database changes.

No additional AI calls.

Reuse existing data only.

---

# Acceptance Criteria

The Today page should allow a first-time user to answer within thirty seconds:

✓ What happened?

✓ Why?

✓ Biggest risk?

✓ Biggest opportunity?

✓ Companies to watch?

✓ India's exposure?

If these questions cannot be answered quickly, Sprint 2 is incomplete.

---

# Out of Scope

Treemap

Impact Graph

Historical Timeline

Company Workspace

Industry Workspace

Macro redesign

Research redesign

These belong to future sprints.

---

# Definition of Done

- Functionality preserved
- Cleaner hierarchy
- Reduced text
- Better visual scanning
- No regressions
- Existing interactions remain functional