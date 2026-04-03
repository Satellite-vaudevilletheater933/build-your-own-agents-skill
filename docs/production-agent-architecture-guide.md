# Production Agent Architecture Guide

This guide is a reusable handoff for building loop-based, tool-using agents inspired by strong patterns seen in modern coding agents.

## The Right Thing To Borrow
Borrow the architecture, not the exact product surface.

The durable ideas are:
- controller loop
- context builder
- tool boundary
- session state
- permissions and approvals
- observability
- evaluation
- product controls for longer workflows

## Reusable Architecture Pattern
1. user provides a goal
2. runtime builds context
3. model decides the next step or requests a tool
4. runtime checks policy
5. runtime executes allowed tools
6. runtime stores results in session state
7. runtime loops until completion, stop condition, or policy boundary

## Production-Readiness Checklist
Before calling an agent serious, define:
- how you will observe it
- how you will evaluate it
- how it fails safely
- how approvals work
- how tool contracts are versioned
