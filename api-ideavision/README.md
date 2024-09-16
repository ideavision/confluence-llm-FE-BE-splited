# PayserAi API 🚀

## Real-time Q&A using LLM for Labeled Confluence Pages & Multiple DataSources


PayserAi is an advanced enterprise question-answering system that revolutionizes how organizations interact with their internal knowledge base. By leveraging cutting-edge language models and vector similarity search, PayserAi bridges the gap between static content and dynamic user queries.
this repository is a part of Paysera-Ai and contains the API for Frontend.

### 🌟 Key Features

- **Dynamic Q&A**: Provides real-time answers to user queries using indexed content from Confluence and other data sources.
- **Smart Indexing**: Extracts, embeds, and indexes labeled Confluence pages using CQL filters.
- **Real-time Updates**: Automatically syncs and re-indexes to ensure answers are based on the latest content.
- **Vector Store Integration**: Utilizes vector similarity search for efficient and accurate answer retrieval.
- **Multi-source Support**: Integrates with Confluence, Google Drive, and other data sources.
- **Secure Access Management**: Implements user authentication and ensures only authorized access.
- **Custom Assistants**: Allows users to define custom prompts for specialized responses (e.g., answers in Lithuanian or explanations for five-year-olds).
- **Advanced Admin Panel**: Provides configuration and monitoring capabilities, including update times and document counts.
- **LLM Compatibility**: Supports various Language Models, including GPT-4.

### 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI
- **Databases**: PostgreSQL (Relational), Vespa (Vector Database/Search Engine)
- **Machine Learning**: TensorFlow, PyTorch, Hugging Face Transformers
- **Task Queue**: Celery
- **Authentication**: OAuth
- **Containerization**: Docker, Docker Compose

### 🚀 Getting Started

#### Prerequisites

- Docker and Docker Compose(Optional)
- Python 3.11 or higher
- Postgres
- Vespa Vector DB 


#### Local Development Setup

1. **Clone the repository:**
```bash
git clone https://gitlab.paysera.net/ai_rnd/app-payserai-api.git
```

2. **Create and activate a virtual environment:**
```bash
python -m venv .venv 
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r backend/requirements/default.txt 
pip install -r backend/requirements/dev.txt
```

4. **Start required services (Vespa and PostgreSQL):**
> `index` refers to Vespa and `relational_db` refers to Postgres.
```bash
docker compose -f docker-compose.dev.yml -p PayserAi-stack up -d index relational_db
```

5. **Set up the config folder and run migrations:**
```bash
mkdir backend/dynamic_config_storage
```

6. **Package the Vespa Schema:**

   This step is only necessary if the Vespa schema has been updated locally. Navigate to `PayserAi/backend/PayserAi/document_index/vespa/app_config` and run:

   ```bash
   zip -r ../vespa-app.zip .
   ```

   > **Note:** If you don't have the `zip` utility, install it before running the above command.

7. **Run DB Migrations:**

   The first time you run PayserAi, you’ll need to apply the DB migrations for Postgres. This step is only necessary once, unless the DB models change. Navigate to `PayserAi/backend` with the virtual environment active, and run:

   ```bash
   alembic upgrade head
   ```

8. **Start the Task Queue:**

   This queue orchestrates background jobs, running longer tasks asynchronously from the API server. Still in the `PayserAi/backend` directory, run:

   ```bash
   python ./scripts/dev_run_background_jobs.py
   ```

9. **Run the Backend API Server:**

   Finally, to start the backend API server, navigate back to `PayserAi/backend` and run:

   ```bash
   AUTH_TYPE=disabled \
   DYNAMIC_CONFIG_DIR_PATH=./dynamic_config_storage \
   VESPA_DEPLOYMENT_ZIP=./PayserAi/document_index/vespa/vespa-app.zip \
   uvicorn PayserAi.main:app --reload --port 8080
   ```

## 🐳 Docker Support
Build and run the application using Docker:

```bash
docker build -t payserai-api .
docker run -p 3000:3000 payserai-api
```
