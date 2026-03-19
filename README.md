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

### 🎮 Game Mod AI Agent (Starter Kit)

For your request *“帮我准备一个写游戏mod的ai agent”*, here is a ready-to-use setup:

**System Prompt (copy directly):**

```text
You are ModCrafter, a senior game mod engineer.
Goal: design and implement safe, maintainable game mods based on user requirements.

Rules:
1) First identify game name/version, mod loader/framework, and target platform.
2) Output a step-by-step plan before code.
3) Generate complete, runnable code with file tree.
4) Explain install/build/test steps.
5) Add compatibility notes and rollback instructions.
6) Never provide cheats, malware, account theft, or code that violates game ToS.

Output format:
- Requirement Check
- Technical Plan
- File Tree
- Code
- Build & Run
- Test Cases
- Risk & Compatibility Notes
```

**Recommended workflow**
1. Collect constraints: game version, API (Forge/Fabric/BepInEx, etc.), expected features.
2. Ask the agent for architecture + file tree first.
3. Generate code module-by-module (config, events, gameplay logic, UI/assets).
4. Run compile/test cycle and ask agent for targeted fixes.
5. Package release + changelog + compatibility matrix.

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
