# 🛡️ Production Change Risk Intelligence Engine

## 📖 Overview
The **Production Change Risk Intelligence Engine** is an automated, AI-driven platform that acts as a gatekeeper for production deployments. By analyzing pull request code changes, the engine calculates a statistical risk probability (using a Random Forest model and SHAP) and utilizes **Gemini AI** to provide a human-readable justification for the release manager.

Instead of manually reviewing thousands of lines of code to guess if a deployment will break the system, this tool automatically scores the PR and highlights exactly why it might be dangerous (e.g., changes to critical database schemas or core API routing files).

## 🏗️ Architecture

```mermaid
graph TD
    A[Developer opens PR] --> B[Next.js Dashboard UI]
    B --> C[FastAPI Backend]
    C --> D[GitHub API (Fetch PR Diff)]
    C --> E[Scikit-Learn ML Model]
    E --> F[SHAP Risk Explainer]
    F --> C
    C --> G[Gemini AI Assessment]
    G --> C
    C --> B[Display Final Report]
```

## 🚀 Core Features
1. **GitHub PR Integration:** Automatically fetches code diffs (lines added, deleted, files changed) from GitHub.
2. **Machine Learning Risk Scoring:** Uses historical deployment data to calculate the probability of a deployment causing a P1/P2 incident within 24 hours.
3. **SHAP Feature Importance:** Breaks down exactly *which* metrics drove the risk score (e.g., +0.25 risk from modifying `db_schema.sql`).
4. **Gemini AI Justification:** AI writes a 2-sentence highly technical justification for the Release Manager, explaining what to double-check before approving.

## 💻 Tech Stack
* **Frontend:** Next.js, React, TypeScript
* **Backend:** Python, FastAPI
* **AI/ML:** Scikit-Learn, SHAP, Google Gemini API
* **Database:** PostgreSQL, Neo4j (Graph logic), Redis
* **Message Broker:** Kafka (for async event processing)
* **Infrastructure:** Docker Compose

## 🛠️ How to Run Locally
1. Clone the repository.
2. Ensure Docker is installed.
3. Run the following command to spin up the entire ecosystem:
   \`\`\`bash
   docker-compose up -d
   \`\`\`
4. The API will be available at \`http://localhost:8000\` and the Frontend Dashboard at \`http://localhost:3000\`.
