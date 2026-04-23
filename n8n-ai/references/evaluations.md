# Evaluations

Guide for evaluating AI workflows in n8n.

---

## Why Evaluate?

AI models are black boxes — unlike deterministic code. You only build confidence by running data through them and observing output. Evaluation is crucial both during building and after production deployment.

---

## Benefits

- Test workflow over a range of inputs (including edge cases)
- Make changes with confidence (without degrading other areas)
- Compare performance between different models or prompts

---

## Types of Evaluation

| | Light Evaluation (Pre-deploy) | Metric-based Evaluation (Post-deploy) |
|---|---|---|
| Performance improvements per iteration | Large | Small |
| Dataset size | Small | Large |
| Dataset sources | Hand-generated, AI-generated, other | Production executions, AI-generated, other |
| Expected outputs | Optional | Usually necessary |
| Evaluation metric | Optional | Required |

---

## Light Evaluation (Pre-deployment)

For testing with a handful of examples during development.

**Steps:**
1. **Create dataset:** Data table or Google Sheet with input, expected output (optional), actual output (blank)
2. **Connect to workflow:** Add Evaluation Trigger, connect to workflow
3. **Write outputs:** Add Evaluation node with operation "Set outputs" mapping outputs to dataset columns
4. **Execute:** Click "Evaluate all" on trigger — runs once per dataset row

---

## Metric-based Evaluation (Post-deployment)

For large datasets where eyeballing isn't sufficient. Assigns numerical scores to each test run.

### Native Metrics

| Metric | Description | Scale |
|--------|-------------|-------|
| **Correctness (AI-based)** | Whether meaning is consistent with reference | 1-5 (5 = best) |
| **Helpfulness (AI-based)** | Whether response answers the query | 1-5 (5 = best) |
| **String Similarity** | Character-by-character closeness (edit distance) | 0-1 |
| **Categorization** | Exact match with reference | 0 or 1 |
| **Tools Used** | Whether execution used tools | 0-1 |

### Custom Metrics

Calculate custom metrics inside the workflow and map to Evaluation node using "Set Metrics" > "Custom Metrics".

### Cost Optimization

Place metric logic after "Check if evaluating" to avoid cost/latency on production executions.

---

## Tips and Common Issues

**Multiple triggers:** Use Merge/No-op node to combine branches from different triggers.

**Evaluation breaking chat:** Add extra branch coming off the agent. Lower branches execute last in n8n. Use No-op node to pass through agent output.

**Accessing tool data in metrics:** Enable "Return intermediate steps" on agent to access `intermediateSteps` in downstream nodes.

**Multiple evaluations on same workflow:** Only one evaluation trigger per workflow. To test different parts, use sub-workflows.

**Inconsistent results:** Duplicate dataset rows to smooth out natural LLM variation.
