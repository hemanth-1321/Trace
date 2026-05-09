# Trace Architecture Spec

## Purpose
Trace is a local-first personal memory system for screenshots and images. The mobile app keeps raw images on device, extracts lightweight device metadata locally, and syncs only semantic metadata and embeddings to the backend. The backend provides auth, temporary vision processing, semantic search, chat over memories, and retrieval for the mobile app and web UI.

## Product Decisions
- Mobile is the primary product surface.
- Web is a companion surface for search, demo, and review.
- Raw images should stay on device by default.
- The backend should persist only semantic memory, not permanent photo storage.
- Vision processing can temporarily receive an image for extraction, but the image must not be stored long term on the backend.
- Auth should be Google sign-in only through Clerk.

## Current Repo State
The repo currently has a partial backend skeleton and no committed mobile implementation yet.

### Implemented or Drafted
- [backend/main.py](backend/main.py) contains a minimal FastAPI app that mounts the upload router.
- [backend/app/core/config.py](backend/app/core/config.py) defines Pydantic settings with environment variables and caching.
- [backend/app/db/base.py](backend/app/db/base.py) defines the SQLAlchemy declarative base.
- [backend/app/db/session.py](backend/app/db/session.py) defines an async session factory and a DB dependency.
- [backend/app/db/models.py](backend/app/db/models.py) defines a draft `Memory` table with pgvector support and uniqueness indexes.
- [backend/app/schemas/memory.py](backend/app/schemas/memory.py) defines batch sync and memory response schemas.
- [backend/app/schemas/search.py](backend/app/schemas/search.py) defines search request/result schemas.
- [backend/app/schemas/vision.py](backend/app/schemas/vision.py) defines vision request/response schemas.
- [backend/app/services/vision/openrouter.py](backend/app/services/vision/openrouter.py) contains a draft OpenRouter vision provider.
- [backend/api/upload.py](backend/api/upload.py) contains a placeholder upload route.
- [backend/pyproject.toml](backend/pyproject.toml) already includes the core Python dependencies for the backend stack.

### Missing or Not Yet Wired
- No `app/api` router package is wired into the backend yet.
- No Clerk JWT verification exists yet.
- No Alembic migration setup exists yet.
- No search route exists yet.
- No chat route exists yet.
- No sync batch route exists yet.
- No worker queue entrypoint exists yet.
- No Redis cache wrapper exists yet.
- No image utility layer exists yet.
- No mobile app scaffold is committed yet.

## Target Architecture

```text
Mobile App (Expo / React Native)
  - local image storage
  - SQLite source of truth for local state
  - gallery watcher / manual import
  - sync queue
  - local display of images
        |
        | sync semantic metadata only
        v
FastAPI Backend
  - auth
  - vision proxy
  - embeddings
  - semantic search
  - chat over memories
  - sync batch ingest
        |
        +--> PostgreSQL + pgvector
        +--> Redis cache
        +--> Redis queue / RQ worker
        +--> OpenRouter vision and embeddings
```

## Data Ownership

### On Device
Store locally:
- `local_image_id`
- `local_uri`
- `image_hash`
- `summary`
- `category`
- `tags`
- `sync_status`
- `backend_memory_id`
- timestamps

### On Backend
Store in Postgres:
- `id`
- `user_id`
- `local_image_id`
- `image_hash`
- `summary`
- `category`
- `tags`
- `embedding`
- `status`
- timestamps

### Do Not Persist Server-Side
- Raw image files
- Permanent media buckets for user images
- Client auth secrets
- Client-side user IDs sent as trusted input

## Backend API Surface

### Required Endpoints
- `GET /health` - health check.
- `POST /api/vision/extract` - temporary vision extraction, returns semantic metadata.
- `POST /api/sync/batch` - batch sync semantic memories from mobile.
- `POST /api/search` - semantic retrieval using embeddings.
- `POST /api/chat` - chat over memories and retrieved context.

### API Rules
- All authenticated endpoints must derive the user from the Clerk JWT.
- The frontend must never supply a trusted `user_id` in the request body.
- Search should return device-side identifiers so the mobile app can resolve the actual image locally.
- Sync should accept batches, not one request per memory.

## Database Rules
- Use async SQLAlchemy only.
- Use PostgreSQL with pgvector.
- Use Alembic migrations only; do not create tables on app startup.
- Index at minimum:
  - `(user_id, created_at)`
  - `(user_id, local_image_id)` unique
  - `(user_id, image_hash)` unique
  - pgvector index on `embedding`

## Worker Rules
- Use Redis plus RQ for background jobs.
- Workers should do vision extraction, embedding generation, and semantic enrichment.
- Workers must be horizontally scalable.
- Workers should not own auth or request routing.

## Mobile Rules
- Expo is the mobile stack.
- Store raw images locally.
- Use SQLite as the on-device source of truth.
- Use background sync for semantic metadata.
- Use local metadata first, AI enrichment second.
- The app must still work if an image is deleted locally; the semantic memory can remain but should be flagged as missing on the device.

## Auth Rules
- Google sign-in only.
- Clerk is the auth provider.
- Backend validates Clerk JWTs.
- Backend derives `user_id` from the token, not from client input.

## Non-Goals For Now
Do not add these yet:
- Kafka
- Go or Rust workers
- Kubernetes
- Multi-region replication
- Custom auth system
- Permanent cloud storage of raw images
- CRDT sync
- Peer-to-peer sync
- Microservice split before the monolith is working

## Remaining Work Checklist

### Backend
- [ ] Wire `app/api/router.py` into `main.py`.
- [ ] Add `app/api/deps/auth.py` for Clerk JWT validation.
- [ ] Add `app/api/routes/vision.py`.
- [ ] Add `app/api/routes/memories.py`.
- [ ] Add `app/api/routes/search.py`.
- [ ] Add `app/api/routes/chat.py`.
- [ ] Add `app/services/cache.py`.
- [ ] Add `app/services/embeddings.py`.
- [ ] Add `app/workers/queue.py`.
- [ ] Add `app/workers/vision_worker.py`.
- [ ] Add `app/utils/hashing.py` and image helpers.
- [ ] Add Alembic environment and first migration.
- [ ] Add request validation, file limits, and rate limiting.

### Mobile
- [ ] Scaffold Expo app.
- [ ] Add local SQLite schema.
- [ ] Add gallery scan/import flow.
- [ ] Add local sync queue.
- [ ] Add API client.
- [ ] Add search and memory views.

### Product
- [ ] Decide whether the first mobile version uses manual import or gallery watcher.
- [ ] Decide whether vision upload is direct to backend or through a temporary object store.
- [ ] Decide the exact initial UX: gallery-first, search-first, or chat-first.

## Definition of Done For the MVP
- A user can sign in with Google.
- A user can add or detect an image on device.
- The app can extract or submit semantic metadata.
- The backend can store memory records and embeddings.
- The app can search memories semantically.
- The app can show the actual local image for a retrieved memory.
- The system never requires permanent server-side image storage.

## Notes On Current Gaps
The current backend code is still at the prototype stage. The main technical gaps are the missing router structure, missing auth middleware, missing migration system, and missing worker/search implementations. The architecture is sound, but the repo is not yet at the production-ready shape described above.
