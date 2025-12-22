# RAG Accuracy Benchmark Guide

## Overview

This benchmark evaluates the accuracy and performance of your RAG (Retrieval-Augmented Generation) system using **Mem0 + Qdrant**.

**What it tests:**
- ✅ Memory storage and retrieval accuracy
- ✅ Semantic similarity matching
- ✅ Keyword relevance
- ✅ Precision and recall metrics
- ✅ Negative case handling (avoiding false positives)

---

## Quick Start

### Run the Benchmark

```bash
python test_rag_benchmark.py
```

### Expected Output

```
🚀 RAG ACCURACY BENCHMARK - Mem0 + Qdrant
================================================================================
Tenant ID: benchmark_test
User ID: test_user
Total Test Cases: 5

🧪 Test Case: Basic Fact Retrieval
   🔍 Query: 'where do I work?'
   ✅ PASS
      Precision: 100%
      Found keywords: ['Google', 'software engineer']

📈 FINAL BENCHMARK REPORT
   Pass Rate: 85% (17/20)
   Precision: 82%
   Recall: 78%
```

---

## Understanding the Metrics

### 1. **Pass Rate**
- **What it measures:** Percentage of queries that successfully retrieved relevant memories
- **Good:** ≥ 80%
- **Acceptable:** 60-80%
- **Poor:** < 60%

### 2. **Precision**
- **What it measures:** How many retrieved memories are actually relevant
- **Formula:** `relevant_retrieved / total_retrieved`
- **Good:** ≥ 70%
- **Interpretation:** High precision = low noise, few irrelevant results

### 3. **Recall**
- **What it measures:** How many relevant memories were successfully retrieved
- **Formula:** `relevant_retrieved / total_relevant`
- **Good:** ≥ 70%
- **Interpretation:** High recall = comprehensive, not missing important info

### 4. **Keyword Matching**
- **What it measures:** Presence of expected keywords in retrieved memories
- **Use case:** Validates factual accuracy (e.g., "Google" when asked "where do I work?")

---

## Test Cases Explained

### Test Case 1: Basic Fact Retrieval
**Purpose:** Test simple factual recall

**Example:**
- Store: "I work as a software engineer at Google"
- Query: "where do I work?"
- Expected: Should retrieve memory containing "Google" and "software engineer"

**Pass criteria:** Precision ≥ 70%

---

### Test Case 2: Timesheet Context
**Purpose:** Test domain-specific (timesheet) memory retrieval

**Example:**
- Store: "I worked 8 hours yesterday on bug fixes"
- Query: "how many hours did I work yesterday?"
- Expected: Should retrieve "8 hours", "yesterday", "bug fixes"

**Pass criteria:** Precision ≥ 70%

---

### Test Case 3: Multi-Fact Retrieval
**Purpose:** Test retrieval of multiple related facts

**Example:**
- Store: "I prefer Python", "I'm learning Rust", "5 years experience"
- Query: "what programming languages do I know?"
- Expected: Should retrieve all three languages

**Pass criteria:** Precision ≥ 60% (more lenient for multi-fact)

---

### Test Case 4: Semantic Similarity
**Purpose:** Test understanding of semantically similar concepts

**Example:**
- Store: "I'm feeling overwhelmed with work"
- Query: "am I stressed?"
- Expected: Should match "overwhelmed" with "stressed" semantically

**Pass criteria:** Precision ≥ 50% (lower threshold for semantic matching)

---

### Test Case 5: Negative Cases
**Purpose:** Ensure system doesn't retrieve incorrect information

**Example:**
- Store: "I work at Google"
- Query: "do I work at Microsoft?"
- Expected: Should NOT retrieve memories about Microsoft

**Pass criteria:** No unexpected keywords found

---

## Interpreting Results

### ✅ Excellent Performance (Pass Rate ≥ 80%)
```
✅ Excellent RAG performance! System is production-ready.
```
**Action:** Deploy with confidence

---

### ⚠️ Good Performance (Pass Rate 60-80%)
```
⚠️ Good performance, but some queries need improvement.
→ Consider tuning embedding model or retrieval parameters
```

**Possible improvements:**
1. **Increase retrieval limit (k):** Change from `k=5` to `k=10` in `retrieve_context()`
2. **Adjust similarity threshold:** Lower threshold for broader matches
3. **Improve memory extraction:** Store more detailed context in memories

---

### ❌ Poor Performance (Pass Rate < 60%)
```
❌ Poor performance. System needs significant improvement.
→ Review memory storage format and retrieval strategy
→ Consider different embedding model or vector database settings
```

**Diagnosis steps:**

#### Low Precision (< 70%)
**Problem:** Retrieved memories not relevant enough

**Solutions:**
- Increase similarity threshold
- Improve memory extraction quality
- Use better embeddings model (e.g., `text-embedding-3-large`)

#### Low Recall (< 70%)
**Problem:** Missing relevant memories

**Solutions:**
- Increase retrieval limit (`k` parameter)
- Review memory storage completeness
- Check if memories are being stored correctly

---

## Customizing the Benchmark

### Add Your Own Test Cases

Edit `test_rag_benchmark.py` and add to `_create_test_cases()`:

```python
{
    "name": "Your Custom Test",
    "conversations": [
        ("User message", "AI response"),
        # Add more conversations
    ],
    "queries": [
        {
            "query": "Your test query?",
            "expected_keywords": ["keyword1", "keyword2"],
            "min_relevance": 0.7,
        },
    ]
}
```

### Adjust Thresholds

Change `min_relevance` in test cases:
- **Strict:** 0.8-1.0 (exact matches only)
- **Normal:** 0.6-0.8 (good balance)
- **Lenient:** 0.4-0.6 (semantic similarity)

---

## Benchmark Report

After running, a JSON report is saved:

```
rag_benchmark_report_20251222_183000.json
```

### Report Structure

```json
{
  "timestamp": "2025-12-22T18:30:00",
  "overall_pass_rate": 0.85,
  "overall_precision": 0.82,
  "overall_recall": 0.78,
  "test_results": [
    {
      "name": "Basic Fact Retrieval",
      "pass_rate": 1.0,
      "avg_precision": 0.95,
      "query_results": [...]
    }
  ]
}
```

---

## Troubleshooting

### Issue: All tests fail with "No memories retrieved"

**Cause:** Qdrant not running or connection issue

**Solution:**
```bash
# Check Qdrant status
curl http://localhost:6333/health

# Verify RAG_ENABLED in .env
RAG_ENABLED=true
QDRANT_URL=http://localhost:6333
```

---

### Issue: Low precision across all tests

**Cause:** Embedding model not capturing semantic meaning well

**Solution:**
1. Check embedding model in `llm/config.py`
2. Try different model:
   ```python
   EMBEDDINGS_MODEL=text-embedding-3-large
   ```
3. Increase embedding dimensions

---

### Issue: Memories stored but not retrieved

**Cause:** Indexing delay or collection mismatch

**Solution:**
1. Increase wait time in `setup_test_data()`:
   ```python
   await asyncio.sleep(5)  # Increase from 3 to 5 seconds
   ```
2. Check collection name matches:
   ```python
   collection_name = f"mem0_{tenant_id}"
   ```

---

## Advanced: Comparing Different Configurations

### Test Different Embedding Models

```bash
# Test with text-embedding-3-small
EMBEDDINGS_MODEL=text-embedding-3-small python test_rag_benchmark.py

# Test with text-embedding-3-large
EMBEDDINGS_MODEL=text-embedding-3-large python test_rag_benchmark.py
```

Compare the reports to see which performs better.

---

### Test Different Retrieval Limits

Edit `run_query_test()` in `test_rag_benchmark.py`:

```python
# Test with k=3
retrieved_memories = await self.memory_manager.retrieve_context(
    query=query,
    k=3,  # Change this
    filter={"user_id": self.user_id}
)
```

---

## Integration with CI/CD

### Add to GitHub Actions

```yaml
name: RAG Benchmark

on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run RAG Benchmark
        run: |
          python test_rag_benchmark.py
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: rag-benchmark-report
          path: rag_benchmark_report_*.json
```

---

## Next Steps

1. **Run baseline benchmark:**
   ```bash
   python test_rag_benchmark.py
   ```

2. **Review results and identify weak areas**

3. **Tune configuration based on recommendations**

4. **Re-run benchmark to measure improvement**

5. **Set up automated benchmarking in CI/CD**

---

## Expected Baseline Performance

With default Mem0 + Qdrant configuration:

| Metric | Expected Range | Target |
|--------|---------------|--------|
| **Pass Rate** | 70-85% | ≥ 80% |
| **Precision** | 75-90% | ≥ 80% |
| **Recall** | 70-85% | ≥ 75% |

If your results are significantly lower, review the troubleshooting section.
