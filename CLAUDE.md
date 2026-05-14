# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is a hackathon project directory for a **Podman Desktop AI Lab** hackathon. The planning guide (`HackaAgent Ideas.pdf`) outlines building local AI agent applications using:

- **Podman Desktop** as the containerized runtime (local, privacy-first, no cloud)
- **Red Hat Granite models** (7B/8B/20B in GGUF format, Q4_K_M quantization)
- **OpenAI-compatible local inference server** exposed by Podman at `localhost`

No source code exists yet — this directory is pre-implementation.

## Intended Tech Stack

When building, expect:
- **Backend**: Python with LangChain or direct HTTP to the local inference server
- **Frontend**: Streamlit or a lightweight web UI
- **Containerization**: Podman Compose

## Key Implementation Patterns (from hackathon guide)

- **Context Injection**: Feed file structures/project maps to the model rather than individual files
- **ReAct pattern**: LLM reasons about data, requests specific columns/chunks, then acts
- **Prompt Templates with few-shot examples** for structured outputs (Markdown tables, JSON → PowerPoint)

## Infrastructure Requirements

Before running any AI workloads, the Podman Machine needs:
- 6+ CPUs
- 12+ GB RAM (default 2 GB will crash containers)
- Models pre-downloaded in GGUF format to avoid bandwidth bottlenecks at runtime

## Candidate Projects

Seven project ideas are documented in the PDF:
1. RAG-based research paper assistant with theme clustering
2. Codebase onboarding / test generation agent (DevOps Partner)
3. Interactive learning tutor with step-by-step guidance (Granite Tutor)
4. PDF comparison and gap analysis (Literature Detective)
5. Paper-to-structured-slide-deck transformer (Paper-to-Pitch)
6. Lab CSV log analysis using ReAct (Experiment Log Scientist)
7. Git repository navigator via context injection (Smart Onboarding)
