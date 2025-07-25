#  Hackathon: Connecting the Dots

Complete solution for Round 1A and Round 1B.

## Features

### Round 1A: PDF Outline Extractor
- Extracts document title and headings (H1, H2, H3)
- Outputs structured JSON with page numbers
- Works offline with CPU-only execution
- Processes PDFs in <10 seconds (for 50-page documents)

### Round 1B: Persona-Driven Document Intelligence
- Analyzes document collection based on persona and job requirements
- Ranks sections by relevance to the given task
- Uses semantic similarity to match content to job needs
- Works within 1GB memory constraint

## Requirements

- Docker
- AMD64 architecture

## How to Build

```bash
docker build --platform linux/amd64 -t  .
