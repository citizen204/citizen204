# 🚀 Hi, I'm Xi Chen

**Incoming AI Graduate @ University of Adelaide | Ex-Baidu Intern**

I am a software engineer passionate about bridging the gap between **Cloud Infrastructure** and **Artificial Intelligence**. With a background in developing high-availability cloud phone systems at **Baidu**, I am now focusing on building scalable AI applications.

---

### ⭐ Featured Project

**[cloud-ops-ai-agent](https://github.com/citizen204/cloud-ops-ai-agent)** — Async Industrial Execution Engine

An experimental framework merging **Baidu Cloud-Phone** operational patterns with modern async AI agent design. Built as a flagship project to demonstrate production-grade cloud orchestration:

| Feature | Implementation |
|--------|----------------|
| **Bounded Concurrency** | `asyncio.Semaphore` for multi-device batch management |
| **Three-Phase Safety Gateway** | Risk classification → Identity verification → MFA (mirrors Baidu account security) |
| **Cooperative Task Abort** | `CancellationToken` + `raise_if_cancelled()` at high-frequency checkpoints |
| **Config-Driven** | Zero hardcoding — all params from `config.json` |
| **Observability** | TraceID full-chain, Prometheus metrics, AWS S3 log persistence |
| **AWS Academy** | S3 audit logs with Learner Lab session-token support |

*Python · asyncio · boto3 · Prometheus · CI/CD (pytest, flake8)*

---

### 🛠 Technical Stack

- **Languages:** Python (asyncio, Deep Learning), TypeScript, Golang, SQL
- **AI/ML:** PyTorch, LangChain (RAG), OpenCV, Hugging Face
- **Cloud/DevOps:** AWS (EC2, S3, STS), Docker, Kubernetes, CI/CD (GitHub Actions)
- **Front-end:** React, Next.js, H5 Optimization (Performance Focused)

---

### 🏢 Professional Experience (Highlight)

#### **Baidu (Guangzhou Duling Technology) | Front-end & System Intern**
*Role: Cloud Phone Product Optimization*

- **Scalability:** Refactored static documentation into a cross-platform (PC/Android/H5) configurable back-end system, reducing deployment cycles.
- **Security:** Implemented advanced verification mechanisms for high-risk cloud phone operations, significantly enhancing user data safety.
- **UX/DX:** Designed task termination workflows for automation products, improving system controllability.

*→ These patterns are now codified in [cloud-ops-ai-agent](https://github.com/citizen204/cloud-ops-ai-agent) as a reusable async execution engine.*

---

### 📈 GitHub Stats

![GitHub Stats](https://github-readme-stats-fast.vercel.app/api?username=citizen204&show_icons=true&theme=vision-friendly-dark)
![Top Langs](https://github-readme-stats-fast.vercel.app/api/top-langs/?username=citizen204&layout=compact&theme=vision-friendly-dark)

---

### 📫 Connect with me

[LinkedIn](https://www.linkedin.com/in/xi-chen-dev/) · [Email](mailto:cxi9371@outlook.com)

---

### 🧭 Travel Planner Agent (Budget + Comfort)

This repository now includes a minimal planner implementation:

- File: `travel_planner_agent.py`
- Goal: create travel plans that prioritize comfort while staying within budget
- Supports:
  - Input constraints and validation
  - Budget-comfort dual-objective planning
  - Multi-option output (economy comfort / balanced / premium comfort)
  - Dynamic replanning for budget/weather/cancellation events

Quick run:

```bash
python travel_planner_agent.py
```

Run as MCP tool server:

```bash
python travel_planner_agent.py --mcp
```

MCP tool exposed:

- `my_agent_function(input: str) -> str`
- `plan_travel(input: str) -> str`
- Input must be a JSON string; output is JSON string.
