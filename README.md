# Fulginn

**Cross-surface memory for AI agents.**

Fulginn is an open source infrastructure layer that gives AI agents persistent, semantically searchable memory across isolated surfaces — desktop apps, web apps, mobile apps, coding environments, or anything that speaks MCP.

---

## The problem

Every AI surface you use is an island.

You explain your project to Claude on your desktop. Later you open a mobile chat and explain it again. Your coding assistant has no idea what you discussed with your writing assistant. Every session starts from zero. Every surface is amnesiac by design.

This isn't a model problem. Models are plenty capable of using context. The problem is that context has nowhere to live between surfaces.

---

## What Fulginn does

Fulginn is a shared memory substrate. It stores conversational context as semantic vectors and retrieves the most relevant prior context regardless of which surface originally produced it.

When Surface A writes context to Fulginn, Surface B can query it. The query doesn't need to match keywords — it matches meaning. Ask about database performance and Fulginn surfaces prior conversations about indexing strategies, even if those words never appeared in the query.

---

## How it works

Fulginn exposes two operations via MCP:

**store** — A surface summarises what it considers important about the current conversation and writes it to Fulginn. The text is embedded into a vector and stored with a surface identifier and timestamp.

**search** — A surface queries Fulginn with a natural language string. Fulginn embeds the query, runs a cosine similarity search against the vector store, and returns the most semantically relevant prior context regardless of which surface wrote it.

That is the entire interface. Everything else is implementation detail.

---

## Architecture

- **Storage:** PostgreSQL with the pgvector extension
- **Embeddings:** Local sentence-transformers — no API key required, no data leaves your machine
- **Search:** HNSW index for approximate nearest neighbour search
- **Interface:** MCP server exposing store and search tools
- **Identity:** Every stored vector carries a surface ID and timestamp

Fulginn is intentionally model-agnostic. It does not care which LLM is running on which surface. Any surface that can make an MCP call can read from and write to Fulginn.

---

## What Fulginn is not

- Not a RAG document retrieval system
- Not a fine-tuning platform
- Not an agent framework
- Not a chat application
- Not a cloud service

Fulginn is infrastructure. It provides the substrate. What you build on top of it is up to you.

---

## Requirements

- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- Any MCP-compatible surface

---

## Installation

```bash
git clone https://github.com/your-username/fulginn.git
cd fulginn
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Initialise the database:

```bash
python3 db.py
```

Start the MCP server:

```bash
python3 server.py
```

---

## Configuration

Copy `.env.example` to `.env` and set your database credentials:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fulginn
DB_USER=fulginn
DB_PASSWORD=your_password
```

---

## Connecting a surface

Any MCP-compatible surface can connect to Fulginn. Add Fulginn to your MCP configuration and two tools become available:

**store(surface_id, payload)** — Write context to the substrate.

**search(query, limit)** — Retrieve semantically relevant context.

The surface is responsible for deciding what to store and when. Fulginn does not make that decision. A surface might store a summary at the end of a session, after a significant decision, or on a timer. The substrate does not care.

---

## Cold start

New to Fulginn? You likely have months of conversational context sitting in Claude, ChatGPT, or other tools. Fulginn can ingest exported conversation history to warm the substrate before you start using it live.

Export instructions for supported platforms are in `docs/import.md`.

---

## Privacy

Fulginn is local-first by design. In the open source configuration:

- All embeddings are computed locally using sentence-transformers
- No data is sent to any external service
- The database runs on your own infrastructure
- You control the encryption, the backups, and the access

---

## MCP integration

Fulginn implements the Model Context Protocol. Once the server is running, configure your MCP-compatible surface to connect to it and the store and search tools are immediately available.

For Claude Desktop configuration see `docs/claude-desktop.md`.

---

## Roadmap

- [ ] Conversation import from Claude, ChatGPT, and other platforms
- [ ] Associative graph layer for relationship-aware retrieval
- [ ] Per-user and per-organisation isolation
- [ ] Unix-style permission model for knowledge promotion
- [ ] Hosted version for teams

---

## Contributing

Fulginn is early. The core is working. There is a lot left to build.

If you find it useful, open an issue, submit a PR, or start a discussion. The architecture decisions behind Fulginn are documented in `docs/architecture.md` for anyone who wants to understand the design before contributing.

---

## Name

Fulginn is an invented word. It carries a loose reference to the Old Norse concept of memory and to *fulgin* — a shade so dark it reflects no light. The substrate operates beneath your surfaces, invisible, persisting what would otherwise be lost.

---

## License

AGPLv3

Fulginn is free to use, modify, and self-host under the terms of the GNU Affero General Public License v3. If you run a modified version of Fulginn as a network service you must make your modifications available under the same license.

For commercial licensing inquiries contact us at mark dot dhas plus fulginn at gmail dot com.
