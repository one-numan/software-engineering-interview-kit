# Master GenAI & Python Backend Interview Cheatsheet

This cheatsheet provides the complete, authoritative, and direct questions and answers for all **9 High-Priority Technical Interview Sections**.

---

## Table of Contents
1. [Section 2: Agentic AI (15 Questions)](#2-agentic-ai--very-important)
2. [Section 3: RAG & Vector Search (15 Questions)](#3-rag--very-important)
3. [Section 4: Python – Core Engineering (12 Questions)](#4-python--core-engineering)
4. [Section 5: Django / FastAPI / Backend (12 Questions)](#5-django--fastapi--backend)
5. [Section 6: GCP – Strict Must-Have (9 Questions)](#6-gcp--strict-must-have)
6. [Section 7: Production GenAI & System Design (8 Questions)](#7-production-genai--system-design)
7. [Section 8: Project-Based Questions (12 Questions)](#8-project-based-questions)
8. [Section 9: Live Coding Interview Problems (8 Problems)](#9-live-coding-interview-problems)

---

## 2. Agentic AI – Very Important
*Full deep-dive and code: [`16-genai-and-agentic-ai/01-agentic-ai.md`](../16-genai-and-agentic-ai/01-agentic-ai.md)*

1. **What is Agentic AI?**  
   Autonomous AI systems capable of iterative goal-directed reasoning, planning, tool execution, and self-correction without step-by-step human intervention.
2. **What is the difference between AI Agent and LLM?**  
   The LLM is a stateless next-token prediction engine (the CPU), while an AI Agent is an active system containing memory, planning loops, and tool execution environments (the full computer).
3. **What is the difference between Agentic AI and traditional RAG?**  
   Traditional RAG is a static, linear search pipeline. Agentic RAG dynamically routes queries across multiple tools, validates retrieval relevance, and rewrites queries if retrieved context is insufficient.
4. **What is tool calling / function calling?**  
   A mechanism where an LLM is provided with JSON schema specifications and returns structured JSON specifying a function name and arguments instead of natural text.
5. **How does an AI agent decide which tool to call?**  
   Via semantic attention matching between user intent and the `description` strings of the provided tool JSON schemas, guided by few-shot prompt examples.
6. **What is multi-agent architecture?**  
   A distributed design where specialized agents with scoped responsibilities (e.g. Researcher, Coder, Critic) collaborate to solve complex multi-step problems.
7. **How do agents communicate with each other?**  
   Via shared state objects (blackboard pattern like LangGraph State), direct message passing (dialogue turns), or asynchronous message queues (RabbitMQ/Redis).
8. **What is an orchestration framework?**  
   Runtime infrastructure (like LangGraph or CrewAI) that controls state transitions, loops, tool execution, human-in-the-loop pauses, and persistent checkpointing.
9. **What is the difference between LangChain and LangGraph?**  
   LangChain is built for linear chains and DAGs; LangGraph is purpose-built for cyclic graphs, stateful multi-agent loops, and native human-in-the-loop breakpoints.
10. **How do you prevent infinite agent loops?**  
    Enforce strict recursion limits (`recursion_limit=15`), detect repeated identical tool call hashes, set global timeouts, and enforce token/cost budgets.
11. **How do you maintain agent memory?**  
    Short-term memory (in-context message lists with sliding window compaction), Long-term episodic memory (vector DB semantic retrieval), and Semantic memory (structured SQL user profiles).
12. **How do you handle failures during tool execution?**  
    Catch the exception and return the stack trace as a `ToolMessage` to the LLM so it can analyze the error, self-correct its query, and retry.
13. **How do you implement human-in-the-loop?**  
    Configure graph breakpoints (`interrupt_before=["high_risk_tool"]`), persist state to PostgreSQL, notify human reviewers via webhook, and resume execution upon approval.
14. **How do you manage agent state?**  
    Use immutable typed schemas (`TypedDict` or Pydantic) with explicit reducer functions and durable database checkpointers.
15. **How would you build a production-grade AI agent?**  
    Decouple UI from worker via async queues (Celery/Redis), enforce input/output guardrails (NeMo/Presidio), trace execution with OpenTelemetry/Langfuse, and run code tools in isolated microVMs.

---

## 3. RAG – Very Important
*Full deep-dive and code: [`16-genai-and-agentic-ai/02-rag-and-retrieval.md`](../16-genai-and-agentic-ai/02-rag-and-retrieval.md)*

1. **What is RAG?**  
   Retrieval-Augmented Generation dynamically fetches external domain documents and injects them into the LLM context prompt to provide accurate, grounded answers.
2. **Explain complete RAG architecture.**  
   Ingestion (parsing $\rightarrow$ chunking $\rightarrow$ embedding $\rightarrow$ vector DB) paired with Online Querying (query embedding $\rightarrow$ hybrid search $\rightarrow$ reranking $\rightarrow$ augmented prompt synthesis $\rightarrow$ LLM generation).
3. **What are embeddings?**  
   High-dimensional dense numerical vectors ($D=768$ or $1536$) that represent the semantic meaning of text in continuous vector space.
4. **What is a vector database?**  
   A specialized storage engine (Qdrant, pgvector, Pinecone) optimized for fast Approximate Nearest Neighbor (ANN) search across millions of vectors using HNSW algorithms.
5. **What is semantic search?**  
   Searching by conceptual meaning and intent rather than matching literal keywords.
6. **What is chunking?**  
   Splitting long documents into smaller, semantically coherent passages to fit embedding token limits and avoid diluting vector meaning.
7. **What are different chunking strategies?**  
   Fixed-size, Recursive Character (by paragraphs/sentences), Semantic (distance threshold between sentences), and Layout-Aware (Markdown headers).
8. **How do you decide chunk size and overlap?**  
   Typically 400–600 tokens with 10–15% overlap. Dense technical content needs smaller chunks (256 tokens); legal contracts need larger chunks (800 tokens).
9. **What is cosine similarity?**  
   The cosine of the angle between two vectors: $\frac{A \cdot B}{\|A\|\|B\|}$, measuring orientation rather than magnitude.
10. **What is hybrid search?**  
    Combining Dense Vector Retrieval (semantic concepts) with Sparse Lexical Retrieval (BM25 exact keywords) using Reciprocal Rank Fusion (RRF).
11. **What is reranking?**  
    A two-stage pattern where a fast bi-encoder fetches top 50 chunks, and an accurate Cross-Encoder deep-learning model scores and re-orders the top 5.
12. **How do you improve retrieval accuracy?**  
    Apply HyDE (Hypothetical Document Embeddings), Parent Document / Small-to-Big retrieval, Multi-query expansion, and contextual compression.
13. **What is metadata filtering?**  
    Pre-filtering vector searches by structured attributes (`tenant_id`, `department`, `date`) to ensure multi-tenant data isolation and speed.
14. **How do you handle large documents?**  
    Use vision-based layout-aware parsers (Document AI) to extract tables as Markdown, and build hierarchical section summary indexes.
15. **How do you reduce hallucinations in RAG?**  
    Enforce strict negative constraint prompts, verify claims using automated evaluation metrics (Ragas Faithfulness), and lower LLM temperature to `0.0`.

---

## 4. Python – Core Engineering
*Full deep-dive and code: [`01-python/core-engineering-interview-questions.md`](../01-python/core-engineering-interview-questions.md)*

1. **List vs Tuple vs Set vs Dictionary:**  
   List: mutable ordered array; Tuple: immutable ordered array; Set: mutable unordered unique hash table; Dict: mutable key-value hash map.
2. **What are decorators?**  
   Higher-order functions that take a function as input and dynamically extend its behavior using closures without modifying its source code.
3. **What are generators and yield?**  
   Functions that return items one-by-one lazily via `yield`, maintaining local execution state in $O(1)$ memory.
4. **What is GIL?**  
   A mutex lock in CPython allowing only one native thread at a time to execute Python bytecode, protecting reference counting safety.
5. **Multithreading vs Multiprocessing?**  
   Threading shares memory and is bound by the GIL (best for I/O tasks); Multiprocessing spawns separate OS processes bypassing the GIL (best for CPU tasks).
6. **Asyncio vs threading?**  
   Threading uses OS-level preemptive scheduling; Asyncio uses a single-threaded cooperative event loop where tasks yield control via `await`.
7. **What are Python memory management mechanisms?**  
   Raw OS allocators, PyMalloc small object pools/arenas ($\le 512$ bytes), Reference Counting ($O(1)$ deallocation), and Generational Cyclic GC.
8. **Shallow copy vs Deep copy?**  
   Shallow copy duplicates the container but references the same child objects; Deep copy recursively duplicates all nested objects.
9. **What are closures?**  
   Inner functions that remember and retain variables from their enclosing scope even after the outer function has finished executing.
10. **What are context managers?**  
    Objects that manage setup and teardown resources via `with` statements by implementing `__enter__()` and `__exit__()`.
11. **How does exception handling work?**  
    `try...except...else...finally` where `else` runs if no error occurred, and `finally` runs unconditionally for resource cleanup.
12. **How do you optimize Python applications?**  
    Use optimal algorithms, `__slots__` to cut memory, built-in C data structures (`deque`), async I/O for concurrency, and C/Rust extensions (Cython/PyO3).

---

## 5. Django / FastAPI / Backend
*Full deep-dive and code: [`02-fastapi/backend-interview-questions.md`](../02-fastapi/backend-interview-questions.md)*

1. **Django vs FastAPI?**  
   Django is a monolithic batteries-included WSGI framework; FastAPI is a modern, high-speed asynchronous ASGI microframework powered by Pydantic v2.
2. **Explain Django middleware.**  
   A series of plugin hooks that globally intercept, inspect, and modify HTTP requests before they reach views and responses before they leave.
3. **What are Django QuerySets?**  
   Lazily-evaluated representations of SQL queries that do not hit the database until evaluated (iterated, sliced, or converted to lists).
4. **What is N+1 query problem?**  
   An ORM anti-pattern where 1 query fetches $N$ parent records, followed by $N$ separate queries in a loop to fetch related child records.
5. **select_related vs prefetch_related?**  
   `select_related` executes 1 SQL query using `JOIN` for single-valued relationships; `prefetch_related` executes 2 SQL queries and joins them in Python memory.
6. **How do you implement authentication?**  
   Stateless JWTs: return short-lived access token in `Authorization: Bearer` and long-lived refresh token in an `HttpOnly, Secure` cookie.
7. **How do you design scalable REST APIs?**  
   Enforce stateless servers, database read replicas with connection pooling, cursor-based pagination, idempotency keys, and CDN edge caching.
8. **How do you handle background tasks?**  
   FastAPI `BackgroundTasks` for quick in-process tasks; Celery with RabbitMQ/Redis for heavy, distributed, fault-tolerant background workloads.
9. **How do you implement Redis caching?**  
   Use the Cache-Aside pattern: check Redis RAM first; on miss, query database, store result in Redis with TTL, and return.
10. **How do you handle concurrent API requests?**  
    FastAPI `asyncio` for non-blocking I/O, database row locks (`SELECT ... FOR UPDATE`) for transactional updates, and Redis `SETNX` distributed locks.
11. **How would you integrate an LLM API into FastAPI?**  
    Use `StreamingResponse(media_type="text/event-stream")` with async generators to stream LLM tokens to the client with sub-400ms TTFT.
12. **How do you handle API rate limits and retries?**  
    Use exponential backoff with randomized jitter (`tenacity` library) catching HTTP 429 errors.

---

## 6. GCP – Strict Must-Have
*Full deep-dive and code: [`11-devops/gcp.md`](../11-devops/gcp.md)*

1. **What is Google Cloud Platform?**  
   Google's cloud computing suite offering global private fiber networking, advanced compute, managed databases, and enterprise AI.
2. **What is Cloud Run?**  
   A serverless compute platform that runs stateless OCI container images with automatic scale-to-zero and high concurrency (up to 1,000 requests/container).
3. **What is Google Kubernetes Engine (GKE)?**  
   Managed Kubernetes; GKE Autopilot manages both control plane and worker nodes with per-pod resource billing.
4. **What is Cloud Storage (GCS)?**  
   Exabyte-scale, 11 9's durable object storage with Standard, Nearline, Coldline, and Archive storage tiers.
5. **What is Vertex AI?**  
   Google Cloud's unified machine learning platform offering Model Garden (Gemini 1.5), Vector Search, and managed RAG pipelines.
6. **What is IAM?**  
   Identity and Access Management enforcing least privilege access via Workload Identity Federation (eliminating static private keys).
7. **How do you deploy a Python application on GCP?**  
   Build a multi-stage Docker image, push to Artifact Registry, and deploy to Cloud Run with `gcloud run deploy --set-secrets`.
8. **How do you securely manage API keys and secrets?**  
   Store secrets in Google Cloud Secret Manager and inject them directly as environment variables at container boot via IAM.
9. **How would you monitor an application on GCP?**  
   Cloud Logging (structured JSON), Cloud Trace (distributed waterfall traces), Cloud Monitoring (Golden Signal alerting), and Cloud Profiler.

---

## 7. Production GenAI & System Design
*Full deep-dive and code: [`16-genai-and-agentic-ai/03-production-genai-system-design.md`](../16-genai-and-agentic-ai/03-production-genai-system-design.md)*

1. **How do you reduce LLM response latency?**  
   Stream tokens via SSE, use Redis semantic caching, leverage prefix prompt caching, and route simple queries to small models (Gemini Flash).
2. **How do you reduce token consumption?**  
   Semantic caching ($20-40\%$ savings), prompt compression (LLMLingua), dynamic few-shot retrieval, and structured JSON output.
3. **How do you handle LLM API failures?**  
   Exponential backoff with full jitter, circuit breakers, multi-provider fallbacks (Vertex AI $\rightarrow$ Anthropic Bedrock), and queue buffering.
4. **How do you implement guardrails?**  
   Input guardrails (NeMo injection detection, Presidio PII masking) and Output guardrails (Pydantic schema validation, hallucination checks).
5. **How do you evaluate RAG quality?**  
   Automate the RAG Triad in CI/CD using Ragas: Context Precision, Faithfulness (grounding), and Answer Relevance on a golden test dataset.
6. **How do you monitor AI agents?**  
   Track token costs per user/endpoint, latency breakdown (TTFT, tokens/sec), loop frequency, tool execution failures, and user feedback signals.
7. **How do you handle concurrent users?**  
   Async non-blocking I/O (`httpx.AsyncClient` in FastAPI), token-bucket rate limiting in Redis, and direct streaming without buffering.
8. **Design a scalable document-question-answering system:**  
   Decouple batch ingestion (Document AI $\rightarrow$ Markdown chunking $\rightarrow$ Qdrant) from online query serving (Redis semantic cache $\rightarrow$ Hybrid search $\rightarrow$ Cohere reranking $\rightarrow$ Gemini SSE streaming).

---

## 8. Project-Based Questions
*Full deep-dive and STAR framework: [`15-interview-preparation/project-explanation.md`](../15-interview-preparation/project-explanation.md)*

1. **Explain your most recent GenAI project:** Autonomous Enterprise Document Intelligence & Contract Search platform.
2. **What problem did your project solve?** Reduced contract review time by 75% across 250,000+ unstructured legal documents.
3. **Explain its architecture:** Layout-aware ingestion into Qdrant + Elasticsearch hybrid search, orchestrated via LangGraph and streamed over FastAPI SSE.
4. **Why did you choose that LLM?** Gemini 1.5 Pro/Flash on Vertex AI for native prompt caching, high speed ($320\text{ ms}$ TTFT), and SOC2 enterprise data isolation.
5. **Which embedding model did you use?** Google `text-embedding-004` (768 dimensions) for top MTEB performance and 50% lower RAM index footprint.
6. **Which vector database did you use?** Qdrant for Rust-native speed, payload pre-filtering for multi-tenant isolation, and on-disk scalar quantization.
7. **How did you implement chunking?** Layout-aware hierarchical Markdown chunking (512 tokens, 64 overlap) injecting document section breadcrumbs into every chunk.
8. **What challenges did you face?** Scanned PDF table distortion (solved via Google Document AI table extraction) and clause hallucinations (solved via LangGraph verification node).
9. **How did you optimize performance?** SSE streaming ($380\text{ ms}$ TTFT) and Redis semantic caching answering 28% of repeated queries in $< 20\text{ ms}$.
10. **How did you deploy your application?** GCP Cloud Run serverless containers with Workload Identity and automated GitHub Actions CI/CD.
11. **How did you measure accuracy?** Automated Ragas CI/CD pipeline achieving $96.8\%$ Faithfulness and $92.4\%$ Context Precision on a 250-QA golden dataset.
12. **What would you improve in your architecture?** Integrate GraphRAG (Neo4j) for multi-hop cross-vendor contract reasoning and fine-tune an 8B local routing model.

---

## 9. Live Coding Interview Problems
*Full deep-dive and code: [`13-coding-exercises/python-problems.md`](../13-coding-exercises/python-problems.md)*

1. **Find duplicate elements in a list (Easy):**  
   Use a tracking set; iterate once. If item in seen, append to duplicates set. Time: $O(n)$, Space: $O(n)$.
2. **Find the first non-repeating character (Easy):**  
   Count character frequencies using `collections.Counter(s)`. Scan string again; return first character with count == 1. Time: $O(n)$, Space: $O(1)$.
3. **Count word frequency (Easy):**  
   Tokenize text with `re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())` and return `Counter(tokens).most_common()`.
4. **Two Sum (Easy):**  
   Single pass with complement hash map (`seen[target - num] = index`). Time: $O(n)$, Space: $O(n)$.
5. **Merge two sorted lists (Medium):**  
   Use a dummy head sentinel node; advance pointers on whichever list has the smaller value. Time: $O(n+m)$, Space: $O(1)$.
6. **Implement an API using FastAPI (Medium):**  
   FastAPI app with Pydantic model validation, dependency injection, and HTTP 201/404 exception handling.
7. **Process JSON data using Python (Medium):**  
   Recursive dictionary parser handling nested objects and lists into dot-notation key-value pairs.
8. **Implement an LRU Cache (Medium/Hard):**  
   Hash Map (`dict`) for $O(1)$ lookup paired with a Doubly Linked List for $O(1)$ eviction and front-insertion.
