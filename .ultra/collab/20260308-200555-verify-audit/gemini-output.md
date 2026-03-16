经对 `ultra-verify` 技能实现的审计，以下是详细发现。报告按严重程度排列：

### [P1] 关键超时策略冲突 (Timeout Mismatch)
*   **描述**：`SKILL.md` 和 `orchestration-flow.md` 明确要求 Bash 工具调用时设置 `timeout: 600000` (10分钟)，但 `verify_wait.py` 脚本内部默认超时为 1200s (20分钟)，且 `SKILL.md` 中的调用指令也使用了 `--timeout 1200`。
*   **后果**：由于外部 Bash 工具会在 10 分钟时强制终止脚本，脚本内部的 20 分钟逻辑永远无法触达。对于文档中提到的“Codex 可能需要 5-10+ 分钟”的情况，如果加上 Gemini 的时间或 Codex 稍有延迟，脚本会被提前杀死，导致 Claude 无法获取最终的 JSON 结果进行合成。

### [P2] 退出码逻辑导致的流程阻断 (Exit Code vs. Fallback)
*   **描述**：在超时且无任何 AI 完成时，脚本执行 `sys.exit(1)`。
*   **后果**：虽然脚本打印了包含状态的 JSON，但 `sys.exit(1)` 会导致 Claude 的环境将其标记为“命令失败”。根据 `SKILL.md` 第 4 步“必须依赖第 3 步 JSON”的要求，若命令被视为失败，Claude 可能会停止执行或跳过解析 JSON，从而无法触发“双 AI 失败则进入仅 Claude 分析”的降级逻辑。
*   **建议**：脚本应始终 `exit 0`，除非发生系统级错误（如路径不存在），而任务的完成状态应完全由 JSON 字段 `status` 表达。

### [P3] 脚本注释与实现不一致 (Docstring Mismatch)
*   **描述**：`verify_wait.py` 的 docstring 声明退出码 `0` 表示 “All AIs completed”，但代码逻辑 `sys.exit(0 if any_done else 1)` 表明只要有一个 AI 完成就会返回 `0`。
*   **后果**：低风险，但会误导对脚本行为的预期，尤其是在调试“部分完成”的场景时。

### [OK] 稳定性检查逻辑 (Stability Check)
*   **审计结论**：**设计精良**。脚本通过 `prev_sizes` 记录上一次轮询的大小，并要求 `cur_sizes == prev_sizes` 且 `size > 0` 才能判定为 `complete`。这有效地解决了 `>` 重定向立即创建空文件，以及 `tee` 这种流式写入导致的“文件存在但内容未写完”的竞态问题。

### [OK] TOCTOU 安全性 (TOCTOU Safety)
*   **审计结论**：**通过**。`_file_size` 函数使用了 `try/except` 捕获 `FileNotFoundError`，而不是先 `exists()` 再 `stat()`，有效避免了文件在检查间隙被删除或移动导致的崩溃。

### [OK] 错误日志过滤设计 (Error Log Handling)
*   **审计结论**：**通过**。脚本严格遵守了“仅在超时时检查错误日志”的原则。这很好地避开了 Codex 或 Gemini CLI 在启动阶段向 stderr 打印初始化信息（如 MCP 挂载日志）而导致的误报。

### [OK] Codex 审计模式兼容性
*   **审计结论**：**通过**。脚本同时检测 `codex-output.md` 和 `codex-raw.txt`。在 `codex_stable` 逻辑中，它巧妙地利用 `-1 == -1` (即两个文件均不存在) 的特性，兼容了两种不同的输出文件名，不会因为其中一个文件的缺失而阻塞另一个文件的完成判定。

---
**总结建议**：
1. **立即修复 P1**：将 Bash 工具的超时时间调整为与脚本一致（如 `1300000`ms），或将脚本超时缩短至 10 分钟以内。
2. **优化 P2**：确保 `verify_wait.py` 在超时输出 JSON 后返回 `exit 0`，以保证 Claude 能够解析 JSON 并执行降级逻辑。
