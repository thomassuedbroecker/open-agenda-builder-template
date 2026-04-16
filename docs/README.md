# Documentation

Navigation: [Repository Root](../README.md) | [Architecture](ARCHITECTURE.md) | [Deployment Guide](DEPLOYMENT.md) | [Dependency Transparency](dependency-transparency.md) | [Latest Smoke-Test Status](local-container-test-status.md)

This directory contains maintained project documentation.

## Table of Contents

1. [Purpose](#1-purpose)
2. [Documents](#2-documents)
3. [Maintenance Rule](#3-maintenance-rule)

## 1. Purpose

The files in this directory explain the architecture, deployment path, dependency record, and latest generated smoke-test status for the repository.

## 2. Documents

- [ARCHITECTURE.md](ARCHITECTURE.md): system design and major decisions
- [DEPLOYMENT.md](DEPLOYMENT.md): local single-container deployment guide
- [dependency-transparency.md](dependency-transparency.md): pinned dependency and tooling record
- [local-container-test-status.md](local-container-test-status.md): latest generated smoke-test result

## 3. Maintenance Rule

Documentation must reflect the code that actually ships and the tests that actually run. If behavior changes, update the relevant document in the same change set or regenerate it from the authoritative script.
