# Review-Errors Agent Memory

## Project Patterns

- **SQL**: DocumentStore uses `better-sqlite3` with parameterized queries (good pattern)
- **Vector DB**: VectorStore wraps `@lancedb/lancedb` -- LanceDB uses raw filter strings for delete, which is an injection risk surface
- **No typed errors**: As of 2026-02-18, storage layer has no custom error types (e.g., StorageError, DocumentStoreError)
- **No try/catch**: Storage modules have zero error handling -- raw library errors propagate to callers
- **Persona engine**: Pure Functional Core -- all modules are pure functions/type defs with no I/O. Minimal error surface by design.
- **xstate v5**: Emotion state machine uses xstate createMachine. Invalid events are silently ignored (framework design).

## Common Issues in This Codebase

- I/O methods without try/catch (storage, capture modules)
- LanceDB filter strings accepted as raw user-supplied text
- Use-after-close patterns (VectorStore nullifies db without guard)
- Constructor resource leaks (DB opened, init fails, no cleanup)
- Bare catch blocks: `catch { return false }` pattern in ScreenshotPipeline.tick() -- error param not even bound
- Fire-and-forget async: `void this.tick()` in start()/setInterval without error surfacing
- Error-as-valid-state: catch returns same value as a normal code path (false = dedup skip AND error)
- Callback errors swallowed: onContext callback inside try block, errors caught by catch-all
- Error messages lack input context (buffer size, timestamp, provider info)
- **onError optional pattern**: Both ScreenshotPipeline and ActivityMonitor use optional `onError` callback. When not provided, errors from onContext callbacks are silently swallowed via `this.onError?.(error)`.
- **Consistent wrapping**: Both pipelines use `new Error(msg, { cause })` for error wrapping -- good pattern but messages still lack operational context.
- **User-supplied callbacks without protection**: evaluateTriggers calls trigger.check(input) without try/catch; if check throws, no context about which trigger failed.

- **Save-then-schedule pattern**: CronService saves to DB before scheduling, so failures in scheduling leave orphaned records. Validate/schedule first, persist after.
- **Loop abort on first failure**: start() methods that iterate over stored records and schedule them abort entirely if one record is invalid. Need per-item error isolation.
- **try/finally without catch**: CronService callback uses try/finally (no catch) -- error propagates into library scheduler, finally block masks errors.

- **Bare catch recurring in new code**: MemoryExtractor has two bare `catch {}` blocks (dedup loop + onError wrapper) -- same pattern as ScreenshotPipeline.tick() and skill-loader.ts. Developers consistently omit error binding in catch blocks.
- **Promise.all for independent I/O recurring**: MemoryOrchestrator.persistExtractionResults uses Promise.all for memory embeddings -- same pattern as AiOrchestrator.initialize(). Third occurrence of this anti-pattern.
- **Dual-ID problem**: MemoryOrchestrator generates separate UUIDs for vector store and document store for the same memory -- no cross-store correlation possible.
- **Zero error handling in orchestrator**: MemoryOrchestrator has no try/catch in any method (init, recall, persistExtractionResults) -- all I/O errors propagate raw. Same pattern as AiOrchestrator.

- **No-op onError default escalation**: EveningPipeline uses `config?.onError ?? (() => {})` -- concrete no-op rather than optional chaining. Even worse than `this.onError?.()` since it looks intentional. Third variant of the onError-optional pattern (ScreenshotPipeline uses `?.`, ActivityMonitor uses `?.`, EveningPipeline uses `?? no-op`).
- **Multi-phase pipeline without per-phase error isolation**: EveningPipeline executeEveningPipeline() runs 5 sequential phases with zero try/catch. Partial completion emits events for completed phases but caller only sees generic error. Same orchestrator-no-try-catch pattern as AiOrchestrator and MemoryOrchestrator.
- **Public API vs internal asymmetry**: EveningPipeline trigger() has no error wrapping but the cron handler path does. Two paths to same function with different error handling guarantees.
- **Handler loop without error isolation (recurring)**: channel-registry, slack/index, whatsapp/index all iterate handler arrays in for-of loops without try/catch. A throwing handler aborts remaining handlers. Same pattern as callback errors in ScreenshotPipeline/ActivityMonitor.
- **Status state 'error' defined but unused**: ChannelStatus includes 'error' but neither channel implementation ever transitions to it on failure.
- **Async handler return discarded**: MessageHandler returns `void | Promise<void>` but callers never await or .catch() the return -- fire-and-forget async on user callbacks.

## Reviewed Files Log

- 2026-02-18: activity-monitor.ts, activity-monitor.test.ts, types.ts, index.ts (task-4 activity monitor)
- 2026-02-18: screenshot-pipeline.ts, screenshot-processor.ts, phash.ts (task-3 screenshot pipeline)
- 2026-02-18: emotion-state-machine.ts, intimacy-tracker.ts, persona-template.ts, emotion-bridge.ts, response-generator.ts, types.ts, index.ts (task-5 persona engine)
- 2026-02-19: cron-service.ts, job-store.ts (task-12 cron-service iter1 -- 0 P0, 5 P1, 2 P2)
- 2026-02-19: memory-extractor.ts, memory-orchestrator.ts, document-store.ts, vector-store.ts (task-14 memory-pipeline iter1 -- 2 P0, 5 P1, 2 P2)
- 2026-02-20: evening-pipeline.ts, evening-pipeline.test.ts (task-15 integration-checkpoint iter1 -- 0 P0, 4 P1, 1 P2)
- 2026-02-20: channel-registry.ts, slack/index.ts, whatsapp/index.ts (task-16 channels-extra iter1 -- 0 P0, 5 P1, 2 P2, 1 P3)
