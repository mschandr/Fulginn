# Fulginn — Product Development Schedule
**Start date:** Monday April 27th 2026  
**Working hours:** 4 productive hours/day · 6 days/week  
**Solo developer · Python · Dev server ready · PoC complete**

---

## Already Shipped

The following are complete as of April 26th 2026:

- Project scaffolding
- Postgres + pgvector setup
- Basic data model (context_vectors table)
- Embedding model integration (sentence-transformers, all-MiniLM-L6-v2)
- store tool (basic)
- search tool (basic)
- MCP server via SSE (FastMCP)
- Nginx reverse proxy (fulginn.local)
- Claude Desktop connected and verified
- Cross-surface retrieval proven (MacBook Air + dev server)
- README.md
- .gitignore
- GitHub repository live (fulginn.com domain registered)

---

## Phase 0 — Foundation Hardening
**Estimated duration: ~2 days**  
**Dates: April 27–28**

These tasks have no dependencies and unblock everything else. Do these first before writing any feature code.

| Task | PERT | Notes |
|------|------|-------|
| requirements.txt | 2.0 | Pin all current dependencies |
| AGPLv3 LICENSE file | 0 | Copy-paste, zero effort |
| .env fully wired | 3.17 | All config variables across all modules |

**Parallel opportunity:** All three can be done simultaneously in a single sitting. LICENSE takes 5 minutes. requirements.txt and .env together take an afternoon.

**Milestone 0:** Clean, reproducible install from scratch. `pip install -r requirements.txt` works. All config comes from `.env`. No hardcoded values anywhere.

---

## Phase 1 — Data Model
**Estimated duration: ~2 days**  
**Dates: April 29–30**

Schema work must come before any feature code. Get the foundation right before building on it.

| Task | PERT | Notes |
|------|------|-------|
| User identity table | 8.0 (combined) | UUID, token hash, created_at |
| Device registry table | | device_id, user_id FK, write_approved, created_at |
| Update context_vectors | | Add write_intent, ownership, last_retrieved, decay_score, is_purged |
| Migration from current schema | | Live data migration, handle carefully |

**Cannot start until:** Phase 0 complete (.env wired, clean install confirmed)

**Parallel opportunity:** None — schema tasks are sequential. Each table may have FK dependencies on the previous.

**Milestone 1:** Clean schema with all tables, all fields, all indexes. Migration runs without data loss. Existing PoC data preserved.

---

## Phase 2 — Identity & Authentication
**Estimated duration: ~10 days**  
**Dates: May 1–12**

The security foundation. Nothing else can be built without user identity.

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| Token generation | 3.67 | No — start here | Issue UUID token, hash with Argon2, store hash |
| Token validation | 5.67 | No — depends on generation | Hash incoming token, compare, return user context |
| TokenManager class | 13.0 | No — depends on above two | generate, validate, reissue, invalidate, cascade reset |
| Device registration | 2.83 | No — depends on TokenManager | Auto-register device, write_approved defaults false |
| BasePermissionScorer | 3.17 | Yes — can start alongside Device registration | Abstract interface only, no logic |
| UserPermissionScorer | 8.0 | No — depends on BasePermissionScorer | User tier only, explicit > general > timed |

**Cannot start until:** Phase 1 complete (user identity table exists)

**Parallel opportunity:** BasePermissionScorer is a pure Python abstract class with no database dependency. Can be written alongside device registration while waiting for TokenManager to stabilise.

**Milestone 2:** A user can connect to Fulginn, receive a token, register a device, and have write approval granted. Zero-knowledge — Fulginn knows nothing about who the user is beyond their token hash.

---

## Phase 3 — Timer & Session
**Estimated duration: ~5 days**  
**Dates: May 13–19**

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| TimerManager class | 13.17 | No — start here | 30 min rolling window, flush on disconnect, reset on reconnect |
| Session boundary detection | 13.17 | Yes — can start alongside TimerManager | Detects natural conversation end, integrates with timer |

**Cannot start until:** Phase 2 complete (device registration working, write approval model in place)

**Parallel opportunity:** Session boundary detection and TimerManager are conceptually coupled but technically independent. TimerManager manages the clock. Session boundary detection decides what constitutes a session. They can be developed in parallel and integrated at the end of the phase.

**Milestone 3:** Fulginn automatically packages and flushes conversation content every 30 minutes. Disconnection triggers immediate flush. Sessions are cleanly bounded.

---

## Phase 4 — Write Pipeline
**Estimated duration: ~14 days**  
**Dates: May 20 — June 4**

The core write path. This is where content actually gets into Fulginn.

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| L0/L1/L2 three tier storage | 13.17 | No — start here | Three table writes, three embeddings, linked by FK |
| Async write queue | 8.0 | Yes — can start alongside L0/L1/L2 | Fire and forget, worker pool, retry on failure |
| store tool (full) | 13.17 | No — depends on L0/L1/L2 and queue | Replaces basic store, adds validation, write_intent, ownership |
| remember tool | 8.0 | No — depends on store tool | Thin wrapper, write_intent always explicit |
| register MCP tool | 2.33 | Yes — can start alongside remember tool | Wraps TokenManager + DeviceManager, starts timer |

**Cannot start until:** Phase 3 complete (timer and session working)

**Parallel opportunity:** Async write queue can be developed independently of L0/L1/L2 storage — it's just a queue mechanism. Wire them together at integration. Similarly register MCP tool can be written once TokenManager is stable, independent of the storage tier work.

**Milestone 4:** Full write pipeline working end to end. Surface connects, registers, gets approved, writes content through all three tiers asynchronously. store and remember tools live via MCP.

---

## Phase 5 — TTL & Decay
**Estimated duration: ~5 days**  
**Dates: June 5–11**

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| TTL data layer | 1.0 | No — start here | last_retrieved, decay_score, is_purged fields (may already exist from Phase 1) |
| update_last_retrieved | 2.0 | No — depends on data layer | Called by recall pipeline on every hit |
| calculate_decay | 3.0 | Yes — can start alongside update_last_retrieved | Formula only, write_intent aware |
| scan_for_decay | 3.0 | No — depends on calculate_decay | Finds candidates past threshold |
| scan_for_purge | 1.83 | Yes — can start alongside scan_for_decay | Independent scan, different threshold |
| execute_purge cascade | 2.0 | No — depends on scan_for_purge | Atomic cascade, edges, bloom filter |
| execute_purge hard delete | 2.33 | No — depends on cascade | Runs after cascade confirmed clean |
| TTL background job | 3.0 | No — depends on all above | Nightly scheduler, runs full decay cycle |

**Cannot start until:** Phase 4 complete (nodes are being written, something to decay)

**Parallel opportunity:** calculate_decay and scan_for_purge are mathematically independent and can be developed in parallel. scan_for_decay and scan_for_purge can also run in parallel since they operate on different thresholds.

**Milestone 5:** Memory decays gracefully. Unused nodes lose retrieval weight over time. Hard purge runs nightly. Explicit memories are protected from decay.

---

## Phase 6 — Graph Engine
**Estimated duration: ~26 days**  
**Dates: June 12 — July 9**

The most complex phase. The graph is what makes Fulginn intelligent rather than just a search engine.

### Co-occurrence Edge Detection

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| get_representative_vector | 8.0 | No — start here | Tier expansion and merging logic |
| cosine_similarity | 3.0 | Yes — can start alongside get_representative_vector | Pure math, numpy one-liner |
| calculate_overlap | 5.17 | No — depends on above two | Orchestrates pull, merge, calculate |
| scan_temporal_window | 5.0 | Yes — can start alongside calculate_overlap | Independent DB query |
| identify_candidates | 3.17 | No — depends on all above | Orchestrates full edge detection |

### Edge Creation & Management

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| create_edge | 3.0 | No — start here | New edge insert |
| strengthen_edge | 5.0 | No — depends on create_edge | Increment weight on existing edge |
| upsert_edge | 5.17 | No — depends on above two | Public method, combines create and strengthen |
| strengthen_on_retrieval | 3.17 | Yes — can start alongside upsert_edge | Called by retrieval pipeline |
| weaken_on_decay | 5.17 | Yes — can start alongside upsert_edge | Called by TTL pipeline |
| purge_edges | 7.67 | No — depends on weaken_on_decay | Atomic cascade on node purge |
| get_edge_weight | 2.0 | Yes — can start anytime | Simple read, no dependencies |

### Graph Traversal

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| build_cte_query | 8.0 | No — start here | Constructs recursive Postgres CTE |
| traverse | 5.17 | No — depends on build_cte_query | Main entry point, calls CTE |
| deduplicate_paths | 8.0 | No — depends on traverse | Same node via multiple paths, keep closest |
| rank_by_hop_distance | 8.0 | No — depends on deduplicate_paths | 1 hop more relevant than 3 hops |

### Graph Maintenance

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| find_orphaned_edges | 3.17 | Yes — can start alongside traversal work | Independent scan |
| find_stale_edges | 3.17 | Yes — can start alongside traversal work | Independent scan |
| run() background job | 8.0 | No — depends on all above | Nightly scheduler |

**Cannot start until:** Phase 5 complete (TTL decay working, nodes have decay_score)

**Parallel opportunities:**
- cosine_similarity can be written day one of this phase independently
- get_edge_weight can be written anytime
- find_orphaned_edges and find_stale_edges can be written alongside traversal work
- strengthen_on_retrieval and weaken_on_decay can be developed in parallel once upsert_edge is stable

**Milestone 6:** Graph is live. New writes create edges. Retrieval traverses associations. The substrate is now associatively intelligent, not just semantically searchable.

---

## Phase 7 — Retrieval Pipeline
**Estimated duration: ~22 days**  
**Dates: July 10 — August 3**

The full recall path. This is what surfaces actually use to get context back.

### Bloom Filter

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| Bloom filter implementation | 8.0 | No — start here | Per-user, in-memory, populated on write, updated on purge |

### Recall Tool — Three Paths

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| Recall explicit path | 8.0 | No — depends on bloom filter | Highest priority, user pinned memories |
| Recall general path | 5.17 | No — depends on explicit path | Mid priority, surface filtered |
| Recall timed path | 3.17 | No — depends on general path | Lowest priority, automatic dumps |

### Priority Ranking

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| IntentScorer | 13.17 | No — start here | explicit > general > timed weighting |
| DecayScorer | 5.17 | Yes — can start alongside IntentScorer | Applies TTL decay_score |
| SimilarityScorer | 8.0 | Yes — can start alongside IntentScorer | Normalises cosine similarity to 0-1 |
| CompositeRanker | 13.17 | No — depends on all three scorers | Combines all scores into final ranking |

### Coarse to Fine

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| Coarse to fine assembly | 5.17 | No — depends on CompositeRanker | L0 first, expand to L1/L2 on demand |

**Cannot start until:** Phase 6 complete (graph traversal working, edges live)

**Parallel opportunities:**
- DecayScorer and SimilarityScorer can be developed in parallel alongside IntentScorer
- Bloom filter can be started at the beginning of this phase independently of the recall paths

**Milestone 7:** Full recall pipeline working. Bloom filter gates unnecessary vector searches. Priority ranking surfaces explicit memories first. Coarse to fine expands only when needed. Graph traversal enriches results with associative context.

---

## Phase 8 — Cold Start & Documentation
**Estimated duration: ~4 days**  
**Dates: August 4–8**

| Task | PERT | Parallel? | Notes |
|------|------|-----------|-------|
| BaseImporter abstract class | 2.0 | No — start here | Abstract interface for all importers |
| ClaudeImporter | 2.83 | No — depends on BaseImporter | Parse Claude JSON export format |
| ChatGPTImporter | 2.83 | No — depends on BaseImporter | Parse ChatGPT JSON export format |
| Systemd service | 5.0 | Yes — can be done anytime | Keep server.py alive, auto-restart |
| Basic documentation | 3.17 | Yes — can be done anytime | Setup guide, MCP tool reference, config reference |

**Cannot start until:** Phase 7 complete (full system working end to end)

**Parallel opportunities:** Systemd service and basic documentation can technically be done at any point — they have no code dependencies. Practical recommendation — write documentation last so it reflects the final implementation accurately.

**Milestone 8 — Open Source Release:** Full system working end to end. Clean install from requirements.txt. Cold start import from at least two platforms. Systemd service keeping it alive. Documentation sufficient for a developer to self-host.

---

## Summary Timeline

| Phase | Description | PERT hrs | Start | End |
|-------|-------------|----------|-------|-----|
| 0 | Foundation Hardening | 5.17 | Apr 27 | Apr 28 |
| 1 | Data Model | 8.0 | Apr 29 | Apr 30 |
| 2 | Identity & Auth | 36.34 | May 1 | May 12 |
| 3 | Timer & Session | 26.34 | May 13 | May 19 |
| 4 | Write Pipeline | 44.67 | May 20 | Jun 4 |
| 5 | TTL & Decay | 19.16 | Jun 5 | Jun 11 |
| 6 | Graph Engine | 103.23 | Jun 12 | Jul 9 |
| 7 | Retrieval Pipeline | 87.86 | Jul 10 | Aug 3 |
| 8 | Cold Start & Docs | 18.16 | Aug 4 | Aug 8 |
| **Total** | | **348.95 hrs** | **Apr 27** | **Aug 8** |

---

## Key Dependencies

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8
```

Strictly sequential at the phase level. Parallel opportunities exist within phases as noted above.

---

## Risk Items

The following tasks have the highest variance between best and worst case and represent the greatest schedule risk:

1. **TokenManager class** — zero-knowledge cascade reset is the hardest single class in the system
2. **TimerManager class** — async connection drop handling is subtle
3. **Graph Engine** — largest phase, most concurrent state management
4. **IntentScorer + CompositeRanker** — retrieval quality depends heavily on getting these right
5. **execute_purge cascade** — atomic deletion across multiple tables and data structures

---

*Generated April 26th 2026 · Solo developer · Python · 4hr days · 6-day week*
*Total: 348.95 points · 87.24 days · 14.54 weeks · ~3.6 months*
*Projected completion: August 8th 2026*
