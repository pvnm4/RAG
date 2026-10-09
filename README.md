# RAG Roadmap
### From Basics → Working Pipeline → Advanced Techniques → Production-Grade RAG

> **Goal:** Learn Retrieval-Augmented Generation deeply enough to **build** RAG systems that work on real, messy data, **measure** whether they work, and **run** them in production.
>
> **Rule:** Don't try to finish everything at once. Follow the phases in order, build something small in every phase, and mark things off as you go.

---

## 🧭 How to Use This Roadmap

### The One-Topic Rule

- [ ] Pick **ONE** topic
- [ ] Learn it for **30–60 minutes**
- [ ] Write a tiny explanation in your own words
- [ ] Build or run **ONE small experiment** (a notebook cell counts)
- [ ] Mark it complete
- [ ] Move on

### Your learning loop

```text
LEARN → EXPLAIN → BUILD → MEASURE → BREAK → IMPROVE
```

RAG is an **engineering** topic, not a theory topic. You only understand a technique when you've seen it **fix a failure** in your own pipeline.

### Completion levels

- [ ] 🟢 **Know** — I understand the concept
- [ ] 🟡 **Explain** — I can explain it without notes
- [ ] 🔵 **Build** — I've implemented it on real data
- [ ] 🟣 **Production** — I can discuss trade-offs, cost, latency, and failure modes

### The most important rule of RAG

```text
Don't add a technique because it's popular.
Add it because your EVALUATION showed a specific failure it fixes.
```

> Build the **evaluation set early (Phase 12 basics can start in Phase 2)**. Without it, every "improvement" is a guess.

---

## 🗺️ The Big Picture

```text
                    OFFLINE (Ingestion)
┌────────┐   ┌───────┐   ┌───────┐   ┌─────────┐   ┌──────────────┐
│ Source │ → │ Parse │ → │ Chunk │ → │  Embed  │ → │ Vector Store │
│  docs  │   │ clean │   │ +meta │   │         │   │ + keyword idx│
└────────┘   └───────┘   └───────┘   └─────────┘   └──────┬───────┘
                                                          │
                    ONLINE (Query time)                   │
┌───────┐   ┌─────────┐   ┌──────────┐   ┌────────┐       │
│ Query │ → │ Rewrite │ → │ Retrieve │ ←─┴────────┴───────┘
└───────┘   │ /route  │   │ (hybrid) │
            └─────────┘   └────┬─────┘
                               ↓
                         ┌──────────┐   ┌──────────┐   ┌──────────┐
                         │ Rerank   │ → │ Build    │ → │   LLM    │ → Answer
                         │          │   │ context  │   │ + cites  │   + sources
                         └──────────┘   └──────────┘   └──────────┘

        EVALUATION + OBSERVABILITY + SECURITY wrap around everything
```

---

## ⏱️ Suggested Timeline

| Stage | Phases | Rough time (≈1 hr/day) |
|---|---|---|
| Foundations | 0–1 | 1 week |
| Working RAG | 2–7 | 3–4 weeks |
| Quality | 8–10, 12 | 3 weeks |
| Advanced | 11 | 3 weeks |
| Production | 13–16 | 3–4 weeks |
| Mastery | 17–22 | ongoing |

Don't treat this as a deadline. It's a pacing guide.

---

# PHASE 0 — Prerequisites

> Goal: Make sure the basics aren't slowing you down.

## 0.1 Python & API Skills

- [ ] Python async / await
- [ ] Type hints and Pydantic models
- [ ] HTTP clients (`httpx`, `requests`)
- [ ] FastAPI basics (routes, dependencies, streaming responses)
- [ ] Environment variables and secrets
- [ ] Working with JSON
- [ ] Reading and writing files (PDF, HTML, Markdown, CSV)
- [ ] Jupyter notebooks for experiments
- [ ] Logging

## 0.2 Databases

- [ ] PostgreSQL basics
- [ ] Indexes (why they exist)
- [ ] Full-text search basics (`tsvector`)
- [ ] JSONB columns
- [ ] Connection pooling

## 0.3 Math You Actually Need (light)

- [ ] What a vector is
- [ ] Dot product
- [ ] Cosine similarity
- [ ] Euclidean (L2) distance
- [ ] Normalization (unit vectors)
- [ ] High-dimensional space intuition (why "nearest" gets tricky)

### Must be able to explain

- [ ] Why cosine similarity of normalized vectors = dot product
- [ ] What "similar" means for two vectors
- [ ] Why an exact nearest-neighbor search gets slow at scale

## 0.4 NLP Basics

- [ ] Tokens and tokenization
- [ ] Words vs subword tokens
- [ ] TF-IDF
- [ ] BM25 (high-level idea)
- [ ] Stemming / lemmatization
- [ ] Stop words
- [ ] Why keyword search and semantic search behave differently

---

# PHASE 1 — LLM Basics for RAG

> Goal: Understand the model you're feeding context into, and why RAG exists.

## 1.1 How LLMs Work (practical level)

- [ ] Tokens
- [ ] Context window
- [ ] Input vs output tokens
- [ ] Temperature
- [ ] Top-p
- [ ] Max output tokens
- [ ] System prompt vs user prompt
- [ ] Stateless API calls
- [ ] Streaming responses
- [ ] Structured outputs / JSON mode
- [ ] Tool / function calling
- [ ] Prompt caching
- [ ] Token costs and latency

## 1.2 Why RAG Exists

- [ ] Knowledge cutoff
- [ ] Hallucination
- [ ] Private / company data
- [ ] Data that changes frequently
- [ ] Need for citations and traceability
- [ ] Access control on data

## 1.3 RAG vs Alternatives

- [ ] RAG vs fine-tuning
- [ ] RAG vs long-context ("just paste everything")
- [ ] RAG vs prompt-only
- [ ] RAG vs traditional search
- [ ] RAG vs text-to-SQL / structured query
- [ ] When to combine them

```text
Fine-tuning  → changes HOW the model behaves / writes
RAG          → changes WHAT the model knows at answer time
Long context → works for small corpora, costs more per query
```

### Must be able to answer

- [ ] When is RAG the wrong choice?
- [ ] Why not just fine-tune on our documents?
- [ ] Why not just put all documents in the context window?
- [ ] Does RAG eliminate hallucinations? (No. Why not?)

### Practice

- [ ] Ask an LLM a question about a private doc **without** RAG → observe the failure
- [ ] Paste the doc in the prompt manually → observe the improvement
- [ ] Write down what "automating that paste step" would require

---

# PHASE 2 — Naive RAG (Your First Working Pipeline)

> Goal: Build the simplest possible end-to-end RAG. Ugly is fine.

## 2.1 The Pipeline

- [ ] Load documents
- [ ] Split into chunks
- [ ] Embed chunks
- [ ] Store vectors
- [ ] Embed the query
- [ ] Retrieve top-k similar chunks
- [ ] Stuff chunks into a prompt
- [ ] Generate an answer

```text
INDEX:  doc → chunks → embeddings → vector store
QUERY:  question → embedding → top-k chunks → prompt → LLM → answer
```

## 2.2 Build It

- [ ] Choose 5–20 documents you actually care about
- [ ] Use a simple local vector store (Chroma / FAISS / pgvector)
- [ ] Build it **without** a framework first (raw SDK calls)
- [ ] Then rebuild it with LlamaIndex or LangChain and compare
- [ ] Print the retrieved chunks for every query

## 2.3 Create Your First Evaluation Set (start now)

- [ ] Write 20–30 real questions
- [ ] For each, write the ideal answer
- [ ] For each, note which document/chunk contains the answer
- [ ] Include some questions that should get "I don't know"
- [ ] Include some multi-part questions
- [ ] Include some questions with exact terms (IDs, error codes, names)

### Must be able to explain

- [ ] What each stage of the pipeline does
- [ ] Why the answer is only as good as the retrieved chunks
- [ ] The two failure types: **retrieval failure** vs **generation failure**

> 🔑 Debugging habit: when an answer is wrong, **look at the retrieved chunks first**. Most RAG bugs are retrieval bugs.

---

# PHASE 3 — Document Ingestion & Parsing

> Goal: Get clean, structured text out of messy real-world files. This is where most production RAG quality is won or lost.

## 3.1 Source Types

- [ ] Plain text / Markdown
- [ ] HTML / web pages
- [ ] PDFs (digital)
- [ ] PDFs (scanned)
- [ ] Word / PowerPoint / Excel
- [ ] Emails
- [ ] Confluence / Notion / wiki pages
- [ ] Slack / chat exports
- [ ] Code repositories
- [ ] Databases / APIs
- [ ] Images, diagrams, charts
- [ ] Audio / video (via transcripts)

## 3.2 Parsing Problems

- [ ] Multi-column layouts
- [ ] Headers and footers repeating on every page
- [ ] Tables (the hardest one)
- [ ] Figures and captions
- [ ] Footnotes
- [ ] Reading order
- [ ] Scanned pages → OCR
- [ ] Broken Unicode / encoding
- [ ] Boilerplate (nav bars, cookie banners)
- [ ] Duplicate documents

## 3.3 Tools to Try

- [ ] Basic PDF text extraction (PyMuPDF / pdfplumber)
- [ ] Layout-aware parsers (e.g., Docling, Unstructured, LlamaParse-style tools)
- [ ] OCR (Tesseract or cloud OCR)
- [ ] Vision-model based parsing (send page image to a multimodal LLM)
- [ ] HTML cleaners (trafilatura, readability-style)

## 3.4 Metadata (extremely important)

- [ ] Source / file name / URL
- [ ] Title
- [ ] Section heading path (`Chapter > Section > Subsection`)
- [ ] Page number
- [ ] Author
- [ ] Created / updated date
- [ ] Document type
- [ ] Language
- [ ] Access permissions / tenant ID
- [ ] Version

### Practice

- [ ] Parse the same PDF with 2–3 parsers and compare the output
- [ ] Parse a PDF containing a table and check whether the table is still readable
- [ ] Store metadata with every chunk
- [ ] Show citations (file + page) in your answers

---

# PHASE 4 — Chunking

> Goal: Split documents so each chunk is **retrievable**, **self-contained**, and **useful to the LLM**.

## 4.1 Why Chunking Matters

- [ ] Embedding models have input limits
- [ ] One embedding per chunk — too big = blurry meaning, too small = no context
- [ ] Chunk size affects retrieval precision, recall, cost, and answer quality

```text
Too small → precise match, but missing context
Too big   → context-rich, but diluted embedding + wasted tokens
```

## 4.2 Chunking Strategies

- [ ] Fixed-size chunking (characters / tokens)
- [ ] Chunk overlap
- [ ] Recursive character splitting
- [ ] Sentence-based chunking
- [ ] Paragraph-based chunking
- [ ] Structure-aware chunking (Markdown headers, HTML tags, sections)
- [ ] Semantic chunking (split where topic changes)
- [ ] Code-aware chunking (functions / classes)
- [ ] Table-aware chunking (keep tables whole, or row-wise with headers)
- [ ] Sliding window
- [ ] LLM-based / agentic chunking
- [ ] Hierarchical chunking (small chunks linked to larger parents)

## 4.3 Enriching Chunks

- [ ] Prepend document title / section path to each chunk
- [ ] Prepend a short LLM-generated context summary (see *Contextual Retrieval*, Phase 11)
- [ ] Attach metadata
- [ ] Generate hypothetical questions per chunk
- [ ] Store a separate summary per chunk or document

## 4.4 Experiments

- [ ] Compare chunk sizes: 128 / 256 / 512 / 1024 tokens
- [ ] Compare overlap: 0% / 10% / 20%
- [ ] Compare fixed vs structure-aware chunking
- [ ] Measure retrieval recall on your eval set for each variant

### Must be able to answer

- [ ] How do I choose a chunk size?
- [ ] Why is there no universal best chunk size?
- [ ] What breaks when a chunk splits mid-table or mid-sentence?
- [ ] Why add the section heading to each chunk?

---

# PHASE 5 — Embeddings

> Goal: Understand how text becomes searchable vectors and how to choose a model.

## 5.1 Concepts

- [ ] What an embedding is
- [ ] Embedding dimensions
- [ ] Semantic similarity
- [ ] Bi-encoder vs cross-encoder
- [ ] Symmetric vs asymmetric search (short query vs long document)
- [ ] Query vs document prefixes / instructions (model-specific)
- [ ] Normalization
- [ ] Max input length and truncation

## 5.2 Choosing a Model

- [ ] Hosted API embeddings vs open-source models
- [ ] Multilingual support
- [ ] Domain fit (legal, medical, code, finance)
- [ ] Dimension size vs storage cost
- [ ] Latency and throughput
- [ ] Cost per million tokens
- [ ] Benchmark awareness (MTEB) — and why to trust **your own eval** more
- [ ] Matryoshka embeddings (truncatable dimensions)
- [ ] Quantized embeddings (int8 / binary) to save memory

## 5.3 Operational Concerns

- [ ] Batching embedding requests
- [ ] Rate limits and retries
- [ ] Caching embeddings
- [ ] **Re-embedding when you change models** (everything must be re-indexed)
- [ ] Storing the model name/version with the vectors
- [ ] Keeping query and document models identical

## 5.4 Fine-tuning Embeddings (advanced)

- [ ] When generic embeddings underperform on your domain
- [ ] Building training pairs (query, relevant chunk)
- [ ] Hard negatives
- [ ] Contrastive learning at a high level
- [ ] Measuring the gain before adopting

### Practice

- [ ] Embed 100 chunks with 2 different models; compare retrieval on your eval set
- [ ] Visualize embeddings (UMAP / t-SNE) to see clusters
- [ ] Find a query where embeddings fail (exact IDs, negation, numbers)

---

# PHASE 6 — Vector Databases & Indexing

> Goal: Understand how similarity search works at scale and which store to choose.

## 6.1 Concepts

- [ ] Exact nearest neighbor (brute force / flat)
- [ ] Approximate nearest neighbor (ANN)
- [ ] Recall vs speed vs memory trade-off
- [ ] Distance metrics: cosine, dot product, L2
- [ ] Metadata filtering
- [ ] Collections / namespaces / tenants

## 6.2 Index Types

- [ ] Flat index
- [ ] IVF (inverted file)
- [ ] HNSW (graph-based) — know this one well
- [ ] PQ (product quantization)
- [ ] Scalar / binary quantization
- [ ] DiskANN-style disk-based indexes

### HNSW parameters to understand

- [ ] `M`
- [ ] `ef_construction`
- [ ] `ef_search`
- [ ] Effect on recall, latency, memory

## 6.3 Vector Stores

- [ ] pgvector (PostgreSQL) — natural fit if you already use Postgres
- [ ] FAISS (library)
- [ ] Chroma (easy local dev)
- [ ] Qdrant
- [ ] Weaviate
- [ ] Milvus
- [ ] Pinecone
- [ ] OpenSearch / Elasticsearch (vector + keyword)
- [ ] Redis vector search
- [ ] MongoDB Atlas vector search

## 6.4 Filtering & Multi-Tenancy

- [ ] Pre-filtering vs post-filtering
- [ ] Why post-filtering can return too few results
- [ ] Filtering by tenant, date, doc type, permissions
- [ ] Per-tenant collections vs shared collection + filter

## 6.5 Operations

- [ ] Index build time
- [ ] Memory footprint estimation (`vectors × dims × bytes`)
- [ ] Updates and deletes
- [ ] Backups
- [ ] Sharding and replication
- [ ] Cost at scale

### Must be able to answer

- [ ] Why not just use brute-force search?
- [ ] What does HNSW trade away for speed?
- [ ] pgvector vs a dedicated vector DB — when does each win?
- [ ] How much RAM do 10M vectors of 1024 dimensions need?

### Practice

- [ ] Store chunks in pgvector with metadata columns
- [ ] Add an HNSW index and compare query time before/after
- [ ] Run a filtered vector query and inspect the query plan

---

# PHASE 7 — Retrieval

> Goal: Get the right chunks into the top results. This is the heart of RAG.

## 7.1 Basic Retrieval

- [ ] Top-k similarity search
- [ ] Choosing `k`
- [ ] Similarity score thresholds
- [ ] "No relevant results" handling
- [ ] Maximal Marginal Relevance (MMR) for diversity
- [ ] Deduplicating near-identical chunks

## 7.2 Keyword (Sparse) Retrieval

- [ ] Inverted index
- [ ] BM25
- [ ] Why BM25 wins on exact terms (IDs, error codes, names, acronyms)
- [ ] Learned sparse retrieval (SPLADE-style) — awareness only

## 7.3 Hybrid Search (production standard)

- [ ] Dense + sparse together
- [ ] Reciprocal Rank Fusion (RRF)
- [ ] Weighted score fusion
- [ ] Score normalization problems
- [ ] When hybrid beats pure vector search

```text
Query → ┬→ Dense retrieval  (top 50) ─┐
        └→ BM25 retrieval   (top 50) ─┴→ Fuse (RRF) → top 20 → Rerank → top 5
```

## 7.4 Metadata & Structured Filters

- [ ] Date filters ("latest", "last quarter")
- [ ] Source / department filters
- [ ] Permission filters
- [ ] Self-querying retrieval (LLM converts the question into a filter + query)

## 7.5 Retrieval Metrics (start measuring)

- [ ] Recall@k
- [ ] Precision@k
- [ ] MRR
- [ ] nDCG
- [ ] Hit rate

### Practice

- [ ] Implement BM25 only, vector only, and hybrid; compare on your eval set
- [ ] Find 5 queries where vector search fails and BM25 succeeds
- [ ] Find 5 queries where BM25 fails and vector search succeeds

---

# PHASE 8 — Reranking

> Goal: Retrieve broadly (high recall), then reorder precisely (high precision).

## 8.1 Why Rerank

- [ ] Bi-encoder retrieval is fast but coarse
- [ ] Cross-encoders read query + chunk **together** → more accurate
- [ ] Too-slow-to-run-on-everything, fine for top 20–100

```text
Retrieve 50  →  Rerank  →  Keep best 5
(cheap, recall)   (expensive, precision)
```

## 8.2 Reranker Types

- [ ] Cross-encoder rerankers (open-source)
- [ ] Hosted rerank APIs
- [ ] LLM-as-reranker (listwise / pointwise)
- [ ] Late-interaction models (ColBERT-style)
- [ ] Learning-to-rank (awareness)

## 8.3 Practical Concerns

- [ ] Latency added by reranking
- [ ] How many candidates to rerank
- [ ] How many to keep after reranking
- [ ] Max token length of the reranker
- [ ] Cost per query
- [ ] Combining rerank score with metadata (recency boost)

### Practice

- [ ] Add a reranker to your pipeline
- [ ] Measure the change in Recall@5 / nDCG
- [ ] Measure the added latency
- [ ] Decide: is it worth it for your use case?

---

# PHASE 9 — Query Understanding & Transformation

> Goal: Fix the fact that users ask bad, vague, or complex questions.

## 9.1 Problems With Raw Queries

- [ ] Too short ("refund policy?")
- [ ] Ambiguous pronouns in chat ("what about the second one?")
- [ ] Multiple questions in one
- [ ] Different vocabulary than the documents
- [ ] Typos
- [ ] Questions needing several documents

## 9.2 Techniques

- [ ] Query rewriting / normalization
- [ ] Conversation-aware (standalone) query rewriting
- [ ] Multi-query generation (several rephrasings, merge results)
- [ ] Query decomposition (split into sub-questions)
- [ ] Step-back prompting (ask a more general question first)
- [ ] HyDE (embed a hypothetical answer instead of the question)
- [ ] Query expansion (synonyms, acronyms)
- [ ] Query routing (choose which index / tool to use)
- [ ] Intent classification (chitchat vs retrieval vs action)
- [ ] Self-querying (extract filters)

## 9.3 Routing

- [ ] Route to different indexes (docs / tickets / code)
- [ ] Route to text-to-SQL for structured questions
- [ ] Route to web search for fresh facts
- [ ] Route to "no retrieval needed"
- [ ] Fallback behavior

### Practice

- [ ] Build a chat RAG that correctly handles follow-up questions
- [ ] Add multi-query and measure the recall gain vs the extra cost
- [ ] Add a router with 2–3 destinations

---

# PHASE 10 — Context Building & Generation

> Goal: Turn retrieved chunks into **grounded, trustworthy answers**.

## 10.1 Context Assembly

- [ ] Ordering chunks (by score vs by document order)
- [ ] The "lost in the middle" effect
- [ ] Token budgeting
- [ ] Merging adjacent chunks
- [ ] Deduplication
- [ ] Including metadata in the prompt (source, date)
- [ ] Context compression / summarization
- [ ] Neighbor-chunk expansion (fetch the chunks before and after)

## 10.2 Prompt Design for RAG

- [ ] Clear instructions: "answer only from the provided context"
- [ ] "If the answer isn't in the context, say you don't know"
- [ ] Delimiting context clearly (XML-style tags)
- [ ] Citation instructions (`[1]`, `[2]`)
- [ ] Answer format (bullets, JSON, steps)
- [ ] Handling conflicting sources
- [ ] Handling outdated sources
- [ ] Tone and length control

## 10.3 Grounding & Citations

- [ ] Inline citations
- [ ] Quote-then-answer pattern
- [ ] Verifying citations actually support claims
- [ ] Showing source snippets in the UI
- [ ] Citation-level faithfulness checks

## 10.4 Output Handling

- [ ] Streaming tokens to the client
- [ ] Structured output (JSON schema)
- [ ] Refusals / "I don't know" responses
- [ ] Follow-up suggestions
- [ ] Feedback buttons (👍 / 👎)

### Must be able to answer

- [ ] Why does the model still hallucinate with retrieved context?
- [ ] How do I make the model say "I don't know" reliably?
- [ ] What happens when retrieved chunks contradict each other?
- [ ] Why is more context not always better?

### Practice

- [ ] Add citations to your answers and click through to verify them
- [ ] Test with questions whose answers are **not** in the corpus
- [ ] Test with contradictory documents

---

# PHASE 11 — Advanced RAG Techniques

> Goal: Know the techniques used in modern production systems, and **when each is justified**.

> ⚠️ Learn these only after you have an eval set and know your failure modes. Each one adds complexity and cost.

## 11.1 Better Chunk Representations

- [ ] **Parent-document retrieval** (embed small chunks, return the larger parent)
- [ ] **Sentence-window retrieval** (retrieve a sentence, return surrounding window)
- [ ] **Small-to-big retrieval**
- [ ] **Multi-vector retrieval** (several embeddings per document: summary, questions, chunks)
- [ ] **Hypothetical question indexing** (embed questions each chunk answers)
- [ ] **Contextual retrieval** (LLM adds document-level context to each chunk before embedding / BM25)
- [ ] **Late chunking** (embed full document first, then pool into chunks)
- [ ] **Proposition-level indexing**

## 11.2 Better Retrieval Models

- [ ] ColBERT / late-interaction retrieval (multi-vector token embeddings)
- [ ] Learned sparse + dense combos
- [ ] Domain-fine-tuned embedding models
- [ ] Instruction-tuned embeddings

## 11.3 Hierarchical & Graph-Based RAG

- [ ] RAPTOR (recursive summarization tree)
- [ ] Document → section → chunk hierarchies
- [ ] **GraphRAG** (entity / relationship graph + community summaries)
- [ ] Knowledge graph + vector hybrid
- [ ] Entity linking
- [ ] When graphs help (multi-hop, "global" questions about a whole corpus)
- [ ] When graphs are overkill (simple lookup questions)

## 11.4 Self-Correcting & Adaptive RAG

- [ ] **Self-RAG** (model decides when to retrieve and critiques its output)
- [ ] **Corrective RAG (CRAG)** (grade retrieved docs, re-search if poor)
- [ ] **Adaptive RAG** (choose strategy by question complexity)
- [ ] Retrieval-grading step (is this chunk relevant?)
- [ ] Answer-grading step (is the answer grounded?)
- [ ] Retry loops with a cap
- [ ] Fallback to web search

## 11.5 Agentic RAG

- [ ] Retrieval as a **tool** the LLM calls
- [ ] Multi-step retrieval loops
- [ ] Planning and decomposition
- [ ] Multi-hop reasoning
- [ ] Multiple tools (vector search, SQL, web, code)
- [ ] Iterative refinement
- [ ] Stopping conditions and step limits
- [ ] Cost / latency control for agent loops
- [ ] Agent observability

```text
Simple RAG:  retrieve once → answer
Agentic RAG: think → retrieve → read → think again → retrieve more → answer
```

## 11.6 Multimodal RAG

- [ ] Image embeddings (CLIP-style)
- [ ] Page-image retrieval (embed whole page screenshots, e.g., ColPali-style)
- [ ] Caption-then-embed approach
- [ ] Chart and table understanding
- [ ] Audio / video via transcripts
- [ ] Passing images to a multimodal LLM

## 11.7 Structured & Specialized RAG

- [ ] Text-to-SQL RAG (schema retrieval + SQL generation + validation)
- [ ] Table QA
- [ ] Code RAG (repo indexing, symbol-aware chunking, AST)
- [ ] Conversational RAG with memory
- [ ] Personalized RAG (user-specific context)
- [ ] Temporal RAG (freshness-aware, versioned docs)
- [ ] Multi-lingual / cross-lingual RAG
- [ ] Enterprise RAG over many connectors

## 11.8 Context Optimization

- [ ] Contextual compression (extract only relevant sentences)
- [ ] Prompt caching for stable context
- [ ] Context window packing
- [ ] Long-context + RAG hybrid (retrieve broadly, let the model read a lot)
- [ ] Citations with quote extraction

### Practice

- [ ] Add parent-document retrieval; measure the change
- [ ] Add contextual retrieval to a subset of chunks; compare recall
- [ ] Build a small corrective-RAG loop with a retry cap
- [ ] Turn retrieval into a tool and build a simple agentic RAG
- [ ] Try GraphRAG on a small corpus and decide whether it was worth the cost

### Decision table (fill this in as you learn)

| Failure you observe | Technique to try |
|---|---|
| Exact terms / IDs missed | Hybrid search (BM25 + dense) |
| Right doc retrieved, wrong chunk ranked first | Reranker |
| Chunk lacks context ("it", "the company") | Contextual retrieval, header prepending |
| Answer needs surrounding paragraphs | Parent-document / sentence-window |
| Vague or conversational queries | Query rewriting, multi-query |
| Multi-part questions | Decomposition / agentic RAG |
| "Summarize the whole corpus" questions | RAPTOR / GraphRAG |
| Questions about numbers in tables | Table-aware parsing, text-to-SQL |
| Irrelevant chunks causing hallucination | Relevance grading, thresholds, CRAG |
| Different vocabulary than documents | HyDE, query expansion, fine-tuned embeddings |
| Visual documents (slides, charts) | Multimodal / page-image retrieval |

---

# PHASE 12 — Evaluation (Critical)

> Goal: Know — with numbers — whether your RAG is good, and whether changes improved it.

## 12.1 Evaluate Retrieval and Generation Separately

```text
Bad answer?
   ├─ Was the right chunk retrieved?   NO  → retrieval problem
   │                                   YES → ↓
   └─ Did the LLM use it correctly?    NO  → generation problem
```

## 12.2 Retrieval Metrics

- [ ] Recall@k
- [ ] Precision@k
- [ ] MRR
- [ ] nDCG
- [ ] Hit rate
- [ ] Context precision
- [ ] Context recall

## 12.3 Generation Metrics

- [ ] **Faithfulness / groundedness** (is every claim supported by the context?)
- [ ] **Answer relevance** (does it answer the question?)
- [ ] **Answer correctness** (vs a reference answer)
- [ ] Citation accuracy
- [ ] Completeness
- [ ] Refusal correctness (said "I don't know" when it should)
- [ ] Tone / format compliance

## 12.4 Building the Test Set

- [ ] Real user questions (best source)
- [ ] Questions written by domain experts
- [ ] Synthetic questions generated from chunks by an LLM
- [ ] Adversarial questions
- [ ] Unanswerable questions
- [ ] Multi-hop questions
- [ ] Questions with exact identifiers
- [ ] Versioned test set (don't silently change it)
- [ ] Separate dev set and held-out set

## 12.5 Evaluation Methods

- [ ] LLM-as-judge (with a clear rubric)
- [ ] Known weaknesses of LLM judges (position bias, verbosity bias, self-preference)
- [ ] Calibrating the judge against human labels
- [ ] Human review samples
- [ ] Pairwise comparison (A vs B)
- [ ] Regression tests in CI
- [ ] Online metrics (thumbs up/down, follow-up rate, escalations)
- [ ] A/B testing

## 12.6 Tools

- [ ] RAGAS
- [ ] DeepEval
- [ ] TruLens
- [ ] LangSmith / Langfuse / Phoenix evaluations
- [ ] Custom evaluation scripts (often the best option)

### Practice

- [ ] Build a 50-question eval set
- [ ] Write a script that runs the pipeline and reports Recall@5 + Faithfulness
- [ ] Change one thing (chunk size, reranker, etc.) and compare before/after
- [ ] Label 30 judge outputs manually and see how often you agree with the LLM judge

---

# PHASE 13 — Production Architecture

> Goal: Move from a notebook to a service that runs reliably for real users.

## 13.1 Ingestion Pipeline

- [ ] Connectors / crawlers for each source
- [ ] Queue-based ingestion (workers)
- [ ] Idempotent processing
- [ ] Parse → chunk → embed → upsert as separate stages
- [ ] Batch embedding
- [ ] Retry and dead-letter handling
- [ ] **Incremental updates** (only re-process changed documents)
- [ ] Content hashing for change detection
- [ ] **Deletion handling** (removed documents must disappear from the index)
- [ ] Document versioning
- [ ] Backfills and re-indexing
- [ ] Blue-green index swaps (build new index, then switch)
- [ ] Ingestion monitoring and failure alerts

```text
Source → Queue → Parser worker → Chunker → Embedder worker → Vector DB + Keyword index
                                                  ↓
                                            Metadata DB (Postgres)
```

## 13.2 Query Service

- [ ] FastAPI service with async I/O
- [ ] Streaming responses (SSE / WebSocket)
- [ ] Timeouts on every external call
- [ ] Retries with exponential backoff and jitter
- [ ] Circuit breakers for LLM / vector DB failures
- [ ] Rate limiting per user / tenant
- [ ] Request validation
- [ ] Graceful degradation (e.g., skip rerank if it's down)
- [ ] Fallback models / providers
- [ ] Concurrency control

## 13.3 Latency Engineering

- [ ] Latency budget per stage

```text
Query rewrite   ~300 ms
Embedding       ~50  ms
Retrieval       ~50  ms
Rerank          ~200 ms
LLM first token ~500 ms
```

- [ ] Run dense + sparse retrieval in parallel
- [ ] Stream the answer
- [ ] Smaller models for rewriting / routing / grading
- [ ] Prompt caching
- [ ] Precompute where possible
- [ ] Time-to-first-token vs total latency

## 13.4 Caching

- [ ] Embedding cache
- [ ] Retrieval-result cache
- [ ] Exact-match response cache
- [ ] **Semantic cache** (reuse answers for similar questions)
- [ ] Risks of semantic caching (stale or wrong-user answers)
- [ ] Cache invalidation when documents change
- [ ] LLM prompt caching

## 13.5 Cost Control

- [ ] Cost per query breakdown (embedding, rerank, LLM input/output)
- [ ] Smaller / cheaper models for sub-tasks
- [ ] Reduce `k` and context size
- [ ] Contextual compression
- [ ] Caching
- [ ] Batch / offline processing for ingestion
- [ ] Quantized vectors
- [ ] Budgets and per-tenant quotas
- [ ] Model routing by question difficulty

## 13.6 Scalability

- [ ] Stateless query service (scale horizontally)
- [ ] Vector DB sharding and replication
- [ ] Read replicas for metadata DB
- [ ] Autoscaling ingestion workers
- [ ] Hot vs cold index tiers
- [ ] Capacity planning (docs → chunks → vectors → RAM)
- [ ] Multi-region considerations
- [ ] Load testing

## 13.7 Multi-Tenancy & Access Control

- [ ] Tenant isolation strategies
- [ ] **Permission-aware retrieval** (filter by user ACL **before** the LLM sees anything)
- [ ] Syncing permissions from source systems
- [ ] Handling permission changes
- [ ] Audit logging
- [ ] Data residency requirements
- [ ] Per-tenant encryption / deletion

> 🔑 The model must **never** see a chunk the user isn't allowed to read. Don't rely on the prompt to enforce permissions.

## 13.8 Deployment

- [ ] Docker
- [ ] CI/CD for the app **and** for eval runs
- [ ] Environment configs
- [ ] Secrets management
- [ ] Feature flags for new retrieval strategies
- [ ] Canary releases
- [ ] Prompt and config versioning
- [ ] Index versioning and rollback

### Practice

- [ ] Wrap your RAG in a FastAPI service with streaming
- [ ] Add an ingestion worker with queue + incremental updates
- [ ] Implement document deletion and verify it disappears from answers
- [ ] Add per-user permission filtering and test that it can't leak

---

# PHASE 14 — Observability & Monitoring

> Goal: See exactly what happened in every request, so you can debug and improve.

## 14.1 Tracing

- [ ] Trace every request end-to-end
- [ ] Log: original query, rewritten query, retrieved chunk IDs + scores, reranked results, final prompt, answer, citations
- [ ] Per-stage latency
- [ ] Token usage and cost per request
- [ ] Tools: Langfuse, LangSmith, Arize Phoenix, OpenTelemetry

## 14.2 Metrics to Monitor

- [ ] Latency (p50 / p95 / p99), time-to-first-token
- [ ] Error rates (by stage)
- [ ] Cost per query / per tenant
- [ ] Empty-retrieval rate
- [ ] "I don't know" rate
- [ ] Average retrieval score
- [ ] Thumbs up / down ratio
- [ ] Citation click-through
- [ ] Ingestion lag (how stale is the index?)
- [ ] Failed-ingestion counts

## 14.3 Feedback Loops

- [ ] Collect user feedback
- [ ] Review low-rated answers weekly
- [ ] Turn failures into new eval-set questions
- [ ] Identify content gaps (questions with no good documents)
- [ ] Track drift (new topics, new document types)

## 14.4 Debugging Playbook

```text
1. Open the trace for the bad answer
2. Was the right document in the index at all?       → ingestion problem
3. Was the right chunk retrieved in top-k?           → retrieval / chunking / embedding problem
4. Was it ranked high enough to be included?         → rerank / k problem
5. Was it in the final prompt?                       → context-assembly problem
6. Did the LLM use it correctly?                     → prompt / model problem
```

### Practice

- [ ] Add tracing to your pipeline
- [ ] Debug 10 failed answers using the playbook above
- [ ] Categorize your failures (ingestion / retrieval / ranking / generation)

---

# PHASE 15 — Security, Privacy & Safety

> Goal: RAG connects an LLM to your data. That's a big attack surface.

## 15.1 Prompt Injection

- [ ] **Direct** prompt injection (user tries to override instructions)
- [ ] **Indirect** prompt injection (malicious text hidden **inside retrieved documents**)
- [ ] Why retrieved content must be treated as **untrusted data**
- [ ] Delimiting and labeling retrieved content
- [ ] Not letting retrieved text trigger tool actions without checks
- [ ] Output filtering
- [ ] Least-privilege tools

## 15.2 Data Leakage

- [ ] Cross-tenant leakage
- [ ] Permission bypass through retrieval
- [ ] System-prompt leakage
- [ ] Leaking PII in answers
- [ ] Logging sensitive content safely
- [ ] Data retention rules

## 15.3 Poisoning & Integrity

- [ ] Index poisoning (bad documents added deliberately)
- [ ] Source trust levels
- [ ] Document provenance
- [ ] Review process for ingested content

## 15.4 PII & Compliance

- [ ] PII detection and redaction before indexing
- [ ] Encryption at rest and in transit
- [ ] Right-to-delete (remove a user's data from index **and** caches)
- [ ] GDPR / DPDP-style requirements (awareness)
- [ ] Sending data to third-party LLM / embedding APIs — what's allowed?
- [ ] Self-hosted vs hosted models for sensitive data

## 15.5 Guardrails

- [ ] Input guardrails (topic, abuse, injection detection)
- [ ] Output guardrails (groundedness, toxicity, PII)
- [ ] Scope limiting ("only answer about X")
- [ ] Human escalation paths
- [ ] Red-teaming your own system

### Practice

- [ ] Plant a malicious instruction inside a test document and see whether your RAG follows it
- [ ] Test whether user A can retrieve user B's documents
- [ ] Add a defense and re-test

---

# PHASE 16 — Frameworks & Tooling

> Goal: Use tools wisely without becoming dependent on abstractions you don't understand.

## 16.1 Frameworks

- [ ] LlamaIndex (strong on ingestion / indexing / retrieval abstractions)
- [ ] LangChain (general LLM app building)
- [ ] LangGraph (stateful agent / workflow graphs)
- [ ] Haystack
- [ ] DSPy (programmatic prompt / pipeline optimization)
- [ ] Vendor SDKs directly (often the simplest)

## 16.2 Evaluating Whether to Use a Framework

- [ ] What does it hide from me?
- [ ] Can I see the exact prompts it sends?
- [ ] Can I swap the vector DB / LLM easily?
- [ ] Is it stable between versions?
- [ ] Would 100 lines of my own code be clearer?

## 16.3 Supporting Tools

- [ ] Document parsers (Docling, Unstructured, etc.)
- [ ] Observability (Langfuse, Phoenix)
- [ ] Evaluation (RAGAS, DeepEval)
- [ ] Workflow orchestration (Airflow, Prefect, Temporal) for ingestion
- [ ] Message queues (Kafka, SQS, Celery / Redis queues)
- [ ] Object storage for raw documents

> Rule: **Build it once from scratch before using a framework.** Then you'll know what the framework is doing for you.

---

# PHASE 17 — Common Failure Modes

> Goal: Recognize problems quickly. Most RAG pain falls into these categories.

## 17.1 Ingestion Failures

- [ ] Garbled PDF text
- [ ] Tables flattened into nonsense
- [ ] Missing pages / failed OCR
- [ ] Duplicate documents inflating results
- [ ] Stale documents never updated
- [ ] Deleted documents still retrievable
- [ ] Missing metadata

## 17.2 Chunking Failures

- [ ] Answer split across two chunks
- [ ] Chunk lacks context ("this policy" — which policy?)
- [ ] Chunks too large and diluted
- [ ] Chunks too small to be meaningful

## 17.3 Retrieval Failures

- [ ] Exact identifiers not found (needs BM25)
- [ ] Semantic mismatch (user vocabulary ≠ document vocabulary)
- [ ] Negation ignored ("not eligible" retrieved as "eligible")
- [ ] Numbers and dates handled poorly
- [ ] Right chunk retrieved but ranked 15th
- [ ] Filter too aggressive → no results
- [ ] Too many near-duplicate chunks

## 17.4 Generation Failures

- [ ] Hallucinating beyond the context
- [ ] Ignoring relevant context in the middle
- [ ] Mixing facts from different documents
- [ ] Wrong or fabricated citations
- [ ] Failing to say "I don't know"
- [ ] Over-answering or under-answering
- [ ] Following instructions hidden in documents

## 17.5 System Failures

- [ ] Slow responses
- [ ] Cost blow-ups
- [ ] LLM / vector DB outages
- [ ] Rate limits during ingestion
- [ ] Index and model version mismatches
- [ ] Silent quality regressions after a change

---

# PHASE 18 — Projects (Build Ladder)

> Goal: Learn by building. Do these in order, and keep each one simple.

## Level 1 — Naive RAG

- [ ] Q&A over a few Markdown / PDF files
- [ ] Raw SDK calls, no framework
- [ ] Prints retrieved chunks and sources

## Level 2 — Better RAG

- [ ] Structure-aware chunking with metadata
- [ ] Hybrid search (BM25 + vectors) with RRF
- [ ] Reranker
- [ ] Citations
- [ ] 50-question eval set + eval script

## Level 3 — Chat RAG Service

- [ ] FastAPI backend with streaming
- [ ] Conversation-aware query rewriting
- [ ] PostgreSQL + pgvector
- [ ] Tracing (Langfuse / Phoenix)
- [ ] Simple web UI or API client

## Level 4 — Production-Style RAG

- [ ] Queue-based ingestion with incremental updates and deletions
- [ ] Multi-tenant, permission-aware retrieval
- [ ] Caching + rate limiting
- [ ] CI that runs the eval set on every change
- [ ] Dockerized deployment
- [ ] Cost and latency dashboard

## Level 5 — Advanced RAG

- [ ] Agentic RAG with retrieval + SQL + web tools
- [ ] Contextual retrieval or parent-document retrieval
- [ ] Corrective loop with relevance grading
- [ ] Multimodal document support
- [ ] Prompt-injection defenses and tests

## Project Ideas (pick what you'd actually use)

- [ ] Documentation assistant for an open-source project (e.g., the repo you're contributing to)
- [ ] Chat over your own notes, resume, and project READMEs
- [ ] Codebase Q&A assistant
- [ ] Research-paper assistant with citations
- [ ] Customer-support assistant over an FAQ + tickets
- [ ] Legal / policy document assistant with strict citations
- [ ] Text-to-SQL analytics assistant over a sample database
- [ ] Meeting / transcript search assistant

---

# PHASE 19 — RAG System Design Problems

> Practice explaining RAG in system-design interview format.

- [ ] Design a company-wide knowledge-base assistant
- [ ] Design a customer-support RAG chatbot
- [ ] Design a RAG system for 10 million documents
- [ ] Design a multi-tenant RAG SaaS
- [ ] Design an enterprise search with per-user permissions
- [ ] Design a code-search assistant
- [ ] Design a legal document Q&A system
- [ ] Design a real-time RAG system with fresh data
- [ ] Design a multimodal document-search system
- [ ] Design an agentic research assistant
- [ ] Design a RAG evaluation platform

### Use this framework

```text
Requirements (users, doc types, volume, freshness, accuracy, latency, privacy)
      ↓
Estimates (docs → chunks → vectors → storage → QPS → cost/query)
      ↓
Ingestion pipeline
      ↓
Index design (vector + keyword + metadata)
      ↓
Query pipeline (rewrite → retrieve → rerank → generate)
      ↓
Evaluation plan
      ↓
Scaling, caching, cost
      ↓
Security & permissions
      ↓
Failures & monitoring
      ↓
Trade-offs
```

### Estimation drill

```text
1M documents × 20 chunks = 20M chunks
20M × 1024 dims × 4 bytes ≈ 80 GB (float32)
With int8 quantization ≈ 20 GB
+ index overhead + metadata + replicas
```

- [ ] Practice estimating storage, RAM, QPS, and cost for 3 different scenarios

---

# PHASE 20 — Trade-offs

Learn to compare:

- [ ] Naive RAG vs advanced RAG
- [ ] Large vs small chunks
- [ ] Dense vs sparse vs hybrid retrieval
- [ ] Reranking vs just retrieving more
- [ ] pgvector vs dedicated vector DB
- [ ] Hosted vs self-hosted embeddings
- [ ] Hosted vs self-hosted LLMs
- [ ] RAG vs fine-tuning
- [ ] RAG vs long context
- [ ] Single-pass RAG vs agentic RAG
- [ ] GraphRAG vs vector RAG
- [ ] Semantic cache vs no cache
- [ ] Batch ingestion vs streaming ingestion
- [ ] Framework vs custom pipeline
- [ ] LLM-as-judge vs human evaluation
- [ ] Accuracy vs latency vs cost

### Rule

Never memorize:

> "X is better than Y."

Instead learn:

> "X is useful when ___, while Y is useful when ___."

---

# PHASE 21 — Staying Current

> RAG changes fast. Don't chase every new paper; track the ideas that pass your eval set.

- [ ] Follow 3–5 reliable sources (engineering blogs of model / DB / RAG tool vendors, a few researchers)
- [ ] Read one paper or engineering post per week
- [ ] Summarize it in 5 bullets
- [ ] Ask: "What failure of mine would this fix?"
- [ ] Test it on your eval set before adopting it
- [ ] Keep a "techniques tried" log with results

### Key ideas worth reading the original sources for

- [ ] RAG (original retrieval-augmented generation paper)
- [ ] DPR (dense passage retrieval)
- [ ] ColBERT
- [ ] HyDE
- [ ] Self-RAG
- [ ] Corrective RAG
- [ ] RAPTOR
- [ ] GraphRAG
- [ ] "Lost in the Middle"
- [ ] Contextual Retrieval (Anthropic engineering post)
- [ ] RAGAS
- [ ] ColPali (visual document retrieval)

---

# PHASE 22 — Your RAG Notebook

For every topic, keep ONE short note:

```markdown
# Topic

## What is it?

...

## What problem does it solve?

...

## When should I use it?

...

## When should I NOT use it?

...

## How did it change my eval results?

Before: ...
After: ...

## Cost / latency impact

...

## Trade-offs

...

## Interview explanation (60 seconds)

...
```

Also keep an **experiment log**:

```text
Date:
Change:
Hypothesis:
Eval result (before → after):
Latency / cost change:
Keep or revert?
```

---

# PHASE 23 — Final Mastery Checklist

## Foundations

- [ ] Embeddings and similarity
- [ ] LLM context and tokens
- [ ] RAG vs fine-tuning vs long context
- [ ] Basic RAG pipeline

## Data Pipeline

- [ ] Document parsing
- [ ] Chunking strategies
- [ ] Metadata design
- [ ] Incremental ingestion
- [ ] Deletion and versioning

## Retrieval

- [ ] Vector search and ANN indexes
- [ ] BM25
- [ ] Hybrid search + RRF
- [ ] Metadata filtering
- [ ] Reranking
- [ ] Query rewriting, multi-query, HyDE
- [ ] Query routing

## Generation

- [ ] Context assembly
- [ ] Grounded prompting
- [ ] Citations
- [ ] Handling "I don't know"
- [ ] Streaming

## Advanced

- [ ] Parent-document retrieval
- [ ] Contextual retrieval
- [ ] Multi-vector / ColBERT-style retrieval
- [ ] Self-RAG / CRAG
- [ ] Agentic RAG
- [ ] GraphRAG / RAPTOR
- [ ] Multimodal RAG
- [ ] Text-to-SQL RAG

## Evaluation

- [ ] Retrieval metrics
- [ ] Faithfulness / relevance metrics
- [ ] Test-set creation
- [ ] LLM-as-judge (and its limits)
- [ ] Regression testing

## Production

- [ ] Queue-based ingestion
- [ ] Caching
- [ ] Latency budgeting
- [ ] Cost control
- [ ] Multi-tenancy and ACLs
- [ ] Observability and tracing
- [ ] Failure handling
- [ ] Deployment and versioning

## Security

- [ ] Prompt injection (direct and indirect)
- [ ] Data leakage prevention
- [ ] PII handling
- [ ] Guardrails

---

# 🧠 Weekly Routine

Don't study RAG for 6 hours in one sitting. Keep it small and consistent.

## Monday — Learn

- [ ] Learn 1 concept
- [ ] Write 5 bullet points
- [ ] Explain it aloud

## Tuesday — Build

- [ ] Implement a tiny version in a notebook
- [ ] Run it on your own documents

## Wednesday — Measure

- [ ] Run your eval set
- [ ] Record the numbers
- [ ] Compare against the previous version

## Thursday — Break

- [ ] Find 5 queries where it fails
- [ ] Classify each failure (ingestion / retrieval / ranking / generation)

## Friday — Review

- [ ] Re-explain 3 concepts
- [ ] Update your notebook
- [ ] Update your experiment log

## Weekend — Real System

- [ ] Read one production RAG architecture post
- [ ] Redraw it from memory
- [ ] Write what you'd change and why
- [ ] Improve your project

---

# 🚦 The "Don't Get Lost" Rule

If you encounter something you don't understand:

```text
STOP
 ↓
Write the unknown term
 ↓
Learn only that term
 ↓
Return to the roadmap
```

Do **not** open 15 tabs and start learning every new RAG paper at once.

---

# 🏁 Your Definition of "Mastered"

You don't need to know every framework or vector database.

You have reached a strong RAG level when you can:

- [ ] Explain every stage of a RAG pipeline and why it exists
- [ ] Parse messy documents into clean, metadata-rich chunks
- [ ] Choose chunking, embedding, and index strategies with reasons
- [ ] Build hybrid retrieval with reranking
- [ ] Improve vague, conversational, and multi-part queries
- [ ] Produce grounded answers with verifiable citations
- [ ] Build an evaluation set and measure changes objectively
- [ ] Diagnose a bad answer to its exact stage (ingestion / retrieval / ranking / generation)
- [ ] Decide which advanced technique a given failure needs
- [ ] Design incremental ingestion with updates and deletions
- [ ] Enforce permissions at retrieval time
- [ ] Defend against prompt injection and data leakage
- [ ] Estimate storage, latency, and cost for a given scale
- [ ] Monitor quality in production and feed failures back into evaluation
- [ ] Build agentic RAG without losing control of cost and latency
- [ ] Defend your design decisions in an interview

---

# ⭐ The Golden Rule

> **RAG is not about using the fanciest retriever or the newest technique.**
>
> **It is about getting the right information to the model, proving the answer is grounded in it, and measuring every change.**

Start with **Phase 0**.

Build the naive version by **Phase 2**.

Write your eval set **before** you optimize anything.

**One checkbox at a time.**
