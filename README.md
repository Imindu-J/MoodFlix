# MoodFlix

MoodFlix is a conversational movie recommendation system that helps users discover
movies by describing what they want to watch in natural language.

Instead of relying only on genres, users can express subjective preferences such as:

- “Recommend a funny animated movie under two hours.”
- “I want something relaxing and uplifting.”
- “Give me a science-fiction movie like Interstellar.”
- “Show me another one, but make it more adventurous.”

MoodFlix combines semantic search, structured database filtering, and conversation
memory to produce relevant and explainable recommendations. The recommendation
engine will first be exposed as a normal HTTP API and later connected to WhatsApp
through the Meta WhatsApp Cloud API.

## Project goals

The finished application will:

- Interpret natural-language movie requests.
- Search by mood, themes, tone, and similarity.
- Filter by genre, runtime, language, release year, rating, and age restriction.
- Return recommendations grounded in stored movie data.
- Remember preferences across follow-up messages.
- Exclude movies the user has watched or rejected.
- Support requests such as “more like this” and “show me another.”
- Provide recommendations through both HTTP and WhatsApp.

## How recommendations will work

```text
User message
    ↓
Preference extraction
    ↓
Hard metadata filters
    ↓
Semantic vector search
    ↓
Candidate ranking and exclusions
    ↓
Grounded recommendations
```

The language model will interpret requests and generate natural explanations, but it
will not invent movie information. Movie selection will be based on records retrieved
from the PostgreSQL catalog.

## Architecture

MoodFlix is being developed as a modular FastAPI application.

```text
HTTP API / WhatsApp
        ↓
FastAPI routes
        ↓
Conversation service
        ↓
Preference extraction
        ↓
Recommendation service
   ┌────┴──────────────┐
   ↓                   ↓
Metadata filtering   Vector search
   └────┬──────────────┘
        ↓
PostgreSQL + pgvector
```

The recommendation engine uses a hybrid retrieval approach:

1. PostgreSQL applies exact constraints such as runtime and language.
2. pgvector finds movies with semantically similar descriptions.
3. Application logic combines and ranks the results.
4. Conversation state removes watched, rejected, or previously recommended movies.
5. The language model explains why the final movies match the request.

## Technology stack

- Python 3.14
- FastAPI
- Pydantic
- PostgreSQL 16
- pgvector
- SQLAlchemy
- Alembic
- Sentence Transformers
- A hosted language model
- Docker Compose
- pytest
- Meta WhatsApp Cloud API

## Development plan

### Phase 1 — Planning and architecture

- [x] Define the MVP features.
- [x] Choose the technology stack.
- [x] Design the high-level architecture.
- [x] Plan the project structure.

### Phase 2 — Project setup

- [x] Create the Python project.
- [x] Create a virtual environment.
- [x] Configure project dependencies.
- [x] Add linting and testing tools.

### Phase 3 — FastAPI foundation

- [x] Create the FastAPI application.
- [x] Add a health-check endpoint.
- [x] Add an endpoint test.
- [x] Enable interactive OpenAPI documentation.

### Phase 4 — Database foundation

- [x] Run PostgreSQL with pgvector through Docker Compose.
- [x] Add SQLAlchemy and the PostgreSQL driver.
- [x] Configure database sessions.
- [x] Configure Alembic migrations.
- [x] Enable the pgvector extension through a migration.
- [x] Create the movie database model.

### Phase 5 — Movie data ingestion

- [x] Select a small movie dataset or API.
- [x] Import movie metadata.
- [x] Validate and clean imported records.
- [x] Store genres, runtime, language, ratings, and age ratings.
- [x] Generate searchable movie descriptions.

### Phase 6 — Embeddings

- [ ] Add Sentence Transformers.
- [ ] Generate embeddings for searchable descriptions.
- [ ] Store embeddings in PostgreSQL.
- [ ] Add a vector similarity index.

### Phase 7 — Recommendation engine

- [ ] Implement metadata filters.
- [ ] Implement semantic vector search.
- [ ] Combine similarity and metadata scores.
- [ ] Return three to five ranked recommendations.
- [ ] Support “more like this” searches.

### Phase 8 — Natural-language preference extraction

- [ ] Define a structured preference model.
- [ ] Connect a cost-effective hosted language model.
- [ ] Convert user messages into validated preferences.
- [ ] Handle missing or ambiguous preferences safely.

### Phase 9 — Conversation state

- [ ] Store conversations and messages.
- [ ] Remember preferences between messages.
- [ ] Track watched and rejected movies.
- [ ] Exclude previously recommended movies.
- [ ] Interpret follow-up requests.

### Phase 10 — Grounded responses

- [ ] Generate concise recommendation explanations.
- [ ] Use only facts retrieved from the movie database.
- [ ] Handle cases where no movies satisfy all constraints.
- [ ] Add fallback and error responses.

### Phase 11 — WhatsApp integration

- [ ] Configure the Meta WhatsApp Cloud API.
- [ ] Add webhook verification.
- [ ] Receive WhatsApp messages.
- [ ] Send recommendation replies.
- [ ] Handle retries and duplicate webhook events.

### Phase 12 — Testing and deployment preparation

- [ ] Add unit and integration tests.
- [ ] Test database queries and ranking behavior.
- [ ] Add structured logging.
- [ ] Document local setup and API usage.
- [ ] Prepare production Docker configuration.
- [ ] Document deployment requirements.


### To improve:
To increase movie retrieval and insertion speed:
- Fetching details with bounded concurrency, perhaps five requests - simultaneously.
- Keeping database writes sequential.
- Committing movies in batches instead of committing every movie.

