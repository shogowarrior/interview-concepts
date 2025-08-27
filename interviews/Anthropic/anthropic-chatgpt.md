# 🧠 Anthropic Interview Prep Sheet

## 1. Stack Trace Reconstruction

**Prompt:**  
Given a list of function calls (enter/exit), reconstruct a valid stack trace.

**Practice:**
- Stack data structure (push/pop logic)
- Matching calls with exit order
- Error handling (mismatched calls, early returns)

**Review:**  
Recursive traces, call stack mechanics, handling malformed sequences

---

## 2. Sorting & Data Mutation Challenges

**Prompt:**  
Implement sorting and data mutation logic across multiple steps. Handle edge cases, stability, and performance tradeoffs.

**Practice:**
- Sorting algorithms (quicksort, mergesort, etc.)
- Chained mutations (transform → filter → sort)
- Time/space complexity reasoning

**Review:**  
In-place vs out-of-place, Python’s `sorted()`, stability in sorting

---

## 3. Web Crawler (Concurrency & Async Evolution)

**Prompt:**  
Build a web crawler. Start with synchronous crawling, evolve to asynchronous with concurrency.

**Practice:**
- Sync: `requests` + `BeautifulSoup`
- Async: `aiohttp` + `asyncio` + rate limiting
- Queueing, deduplication, fault tolerance

**Review:**  
Async patterns in Python, producer-consumer, BFS/DFS crawling

---

## 4. GPT / Claude Multi-Threaded Chat System

**Prompt:**  
Design a system to handle multiple user questions in a single GPT/Claude chat thread.

**Practice:**
- Thread/session state management
- Concurrent request handling
- Context switching and isolation of responses

**Review:**  
Message queues, chat memory, stateless vs stateful architecture

---

## 5. File System / In-Memory File Store

**Prompt:**  
Design a file system or in-memory data store with operations like set, get, filter, backup, and restore.

**Practice:**
- In-memory structure (dict-based)
- Backup/versioning logic
- Filtering and query capabilities

**Review:**  
Serialization, snapshotting, CLI-command parsing

---

## 6. Multi-Tiered Banking System

**Prompt:**  
Design a banking system that evolves in stages:
- Basic transaction recording (deposits, transfers)
- Top-K analytics
- Scheduled/cancelable transactions
- Account merging while preserving history

**Practice:**
- Ledger and transaction classes
- Priority queues for ranking
- Scheduling logic (time-based simulation)
- Performance/memory budget constraints

**Review:**  
OOP principles, transaction integrity, scheduled tasks

---

## 7. In-Memory CRUD / OOP Systems

**Prompt:**  
Implement a small in-memory CRUD application:
- Employee timesheets or academic management
- Track time-in/out or grades
- Support unusual/complex operations

**Practice:**
- OOP class models and relationships
- Data validation and constraints
- Handling corrupted or poorly-structured data

**Review:**  
Data modeling, edge case design, object state transitions

---

## 8. Open-Ended Ethics: AI Emotion

**Prompt:**  
What would you do if AI started to feel sad?

**Practice:**
- Reason through emotional simulation
- Address anthropomorphism
- Explore ethical and societal implications

**Review:**  
AI ethics, cognitive modeling, affective computing

---

## ✅ Prep Tips

- Use the structure: **problem → approach → tradeoffs → constraints**
- Practice verbal walkthroughs for design
- Clarify assumptions early
- Prepare for **multi-stage iterations**, especially on banking and file systems
- Stay grounded in **real-world constraints** (scale, latency, memory)
