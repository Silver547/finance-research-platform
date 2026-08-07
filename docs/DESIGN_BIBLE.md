# DESIGN BIBLE

# Market Intelligence Platform

Version: 1.0

---

# Purpose

The Design Bible defines how every page, component, and interaction in the Market Intelligence Platform should look and behave.

Its purpose is to ensure that every future feature feels like part of the same product.

Design decisions should never be made ad hoc.

When implementing new features, follow this document before introducing new UI patterns.

---

# Design Philosophy

The platform should feel:

- Professional
- Modern
- Premium
- Calm
- Trustworthy
- Information-focused

The design should help users understand markets quickly rather than impress them with excessive visual effects.

---

# Product Identity

This platform is not a news website.

It is not a trading terminal.

It is not a stock screener.

It is an AI-powered Market Intelligence Workspace.

Every design decision should reinforce that identity.

---

# Design Principles

## Principle 1 – Clarity before Density

Showing more information does not make the product better.

Always prefer:

Clear understanding

over

Maximum information.

---

## Principle 2 – Information before Decoration

Visual elements exist to improve understanding.

Avoid decorative graphics that do not communicate information.

---

## Principle 3 – Progressive Disclosure

Users should discover information gradually.

Always follow this flow:

Summary

↓

Explanation

↓

Evidence

↓

Reference

Never expose every detail immediately.

---

## Principle 4 – Every Card Answers One Question

Examples:

Hero

"What is today's story?"

Market Snapshot

"What should I care about?"

Driver Card

"What is moving markets?"

Ripple

"How does this affect India?"

Research

"What should I investigate next?"

If a card answers multiple unrelated questions, redesign it.

---

# Layout System

## Maximum Content Width

Use a consistent centered layout.

Avoid extremely wide text blocks.

---

## Card Spacing

Primary cards:

24px spacing

Secondary cards:

16px spacing

Internal spacing:

16–20px

Avoid cramped layouts.

---

## Card Heights

Cards within the same row should have equal height whenever practical.

---

# Visual Hierarchy

Level 1

Hero

Market Snapshot

---

Level 2

Drivers

Economic Ripple

---

Level 3

Market Movers

Research

---

Level 4

Latest Dispatches

Supporting Evidence

Historical Information

---

# Typography

Hero Headline

Largest text on the page.

Bold.

High contrast.

---

Section Titles

Medium size.

Consistent across all pages.

---

Body Text

Readable.

Never dominate the layout.

---

Metadata

Smallest text.

Muted color.

Examples:

Source

Time

Updated

Tags

---

# Text Rules

Maximum paragraph length:

3 lines

If content exceeds this:

Convert into:

- bullets
- chips
- badges
- indicators
- expanders

Never allow long blocks of text on dashboard pages.

---

# Color System

Green

Opportunity

Positive movement

Constructive outlook

---

Red

Risk

Negative movement

Warning

---

Blue

Macroeconomic information

Government

Central banks

Policy

---

Orange

Items requiring attention.

Watch list.

Emerging risks.

---

Gray

Supporting information

Metadata

Secondary labels

---

# Cards

Every card must have:

Clear title

Single objective

Visual hierarchy

Consistent padding

Minimal text

No unnecessary borders

---

# Driver Card Standard

Required Elements

- Driver Name
- Direction (▲ ▼ →)
- Importance
- Confidence
- Impacted sectors
- Read More

Optional

Short explanation

Never paragraphs.

---

# Market Snapshot Standard

Required

Market Mood

Confidence

Importance

Top Risk

Top Opportunity

Affected Areas

---

# Economic Ripple Standard

Always show cause and effect visually.

Preferred format:

Global Event

↓

Transmission

↓

India

↓

Sector

↓

Company

Paragraph explanations belong inside an expander.

---

# Market Movers Standard

Each row should contain:

Company

Direction

Reason

Nothing else.

Avoid paragraphs.

---

# Research Card Standard

Research should guide exploration.

Examples:

Continue Research

AI Infrastructure

Semiconductors

Oil

China

The card should encourage investigation rather than summarize.

---

# Latest Dispatches

Purpose:

Provide evidence.

Not explanation.

Display:

Headline

Classification

Source

Time

Limit:

Five items

Use "View More" for additional articles.

---

# Icons

Icons communicate category.

Do not use icons for decoration.

Examples:

🌍 Global

🏢 Company

🏭 Industry

📊 Macro

⚠ Risk

💡 Opportunity

🧠 AI

📄 Research

---

# Interaction Rules

Clickable items should look clickable.

Hover states should communicate interaction.

Never create fake buttons.

Never replace interactive Streamlit widgets with static HTML.

---

# Dashboard Rules

The first screen should answer:

- What happened?
- Why did it happen?
- Why should I care?
- What should I watch?

Users should understand the market before they begin reading news.

---

# Component Reuse

Every new feature should reuse existing components whenever possible.

Avoid creating slightly different versions of the same card.

Consistency is more valuable than variety.

---

# Accessibility

Maintain sufficient color contrast.

Avoid communicating meaning through color alone.

Support keyboard navigation where practical.

Readable font sizes.

Clear visual hierarchy.

---

# Responsive Design

Desktop

Primary experience.

Tablet

Maintain card hierarchy.

Mobile

Prioritize Hero, Snapshot, Drivers.

Collapse supporting sections.

---

# Performance

Avoid unnecessary animations.

Fast loading is more valuable than visual effects.

Prioritize responsiveness over decoration.

---

# Future Rule

Every future design decision must answer:

Does this help users understand the market faster?

If the answer is no,

do not implement it.