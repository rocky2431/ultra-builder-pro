**发现**

- `Critical` 位置：[codex-cli-reference.md](/Users/rocky243/.claude/skills/codex-collab/references/codex-cli-reference.md#L28)  
  文档写的是 `--commit-title`，但本机 `codex review --help` 实际参数是 `--title`。这是可直接导致命令失败的错误 CLI flag。  
  建议：把 `--commit-title "title"` 全部改为 `--title "title"`，并补一条基于 `codex review --help` 的校验说明。

- `Warning` 位置：[orchestration-flow.md](/Users/rocky243/.claude/skills/ultra-verify/references/orchestration-flow.md#L35)、[orchestration-flow.md](/Users/rocky243/.claude/skills/ultra-verify/references/orchestration-flow.md#L47)、[SKILL.md](/Users/rocky243/.claude/skills/ultra-verify/SKILL.md#L38)  
  `audit` 模式里 Codex 用 `codex review --uncommitted` 输出到 `codex-raw.txt`，但后续收集阶段固定读取 `codex-output.md`，而 session 结构也只列了 `codex-output.md`。中间缺少“从 raw 提取成 output.md”的步骤。  
  建议：像 `codex-collab` 一样明确增加提取步骤，或统一改成后续读取 `codex-raw.txt`。

- `Warning` 位置：[codex-prompts.md](/Users/rocky243/.claude/skills/codex-collab/references/codex-prompts.md#L26)  
  `codex exec "Performance analysis of this code: $(cat $FILE) ..."` 把文件内容直接塞进 shell 命令行。风险包括：内容出现在进程列表/历史里、引号和换行破坏命令、超长参数失败。  
  建议：改成 stdin 方案，例如：  
  ```bash
  cat "$FILE" | codex exec "Analyze this code for performance issues..." --sandbox read-only -o "${SESSION_PATH}/output.md" 2>/dev/null
  ```

- `Warning` 位置：[orchestration-flow.md](/Users/rocky243/.claude/skills/ultra-verify/references/orchestration-flow.md#L32)、[codex-prompts.md](/Users/rocky243/.claude/skills/codex-collab/references/codex-prompts.md#L26)  
  同一条命令同时写了 `--full-auto` 和 `--sandbox read-only`。本机帮助显示 `--full-auto` 是 `-a on-request, --sandbox workspace-write` 的别名，所以这里存在语义冲突，且文档未解释优先级。  
  建议：分析场景只保留 `--sandbox read-only`，不要再叠加 `--full-auto`；如果确实要自动执行，明确写成单一策略并说明原因。

- `Warning` 位置：[gemini-collab/SKILL.md](/Users/rocky243/.claude/skills/gemini-collab/SKILL.md#L47)、[gemini-cli-reference.md](/Users/rocky243/.claude/skills/gemini-collab/references/gemini-cli-reference.md#L46)  
  文档要求“始终使用 `--yolo`”，包括 review / understand / opinion 这类本应偏只读的分析任务。即使文档声称默认有 sandbox，这仍是“自动批准所有工具调用”，安全边界过宽。  
  建议：把默认模式改为更保守的只读/plan 模式；只有明确需要工具写操作时才升级到 `--yolo`。

- `Info` 位置：[gemini-collab/SKILL.md](/Users/rocky243/.claude/skills/gemini-collab/SKILL.md#L15)、[ultra-verify/SKILL.md](/Users/rocky243/.claude/skills/ultra-verify/SKILL.md#L15)  
  文档把 `gemini --version` 当作前置验证，但在当前环境里 `gemini --help/--version` 都未快速返回，说明这个健康检查不够稳。  
  建议：改成带超时的 smoke test，并提供失败回退，例如：  
  ```bash
  python3 - <<'PY'
  import subprocess
  subprocess.run(["gemini","-p","ping","--yolo"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=False)
  PY
  ```

- `Info` 位置：[gemini-collab/SKILL.md](/Users/rocky243/.claude/skills/gemini-collab/SKILL.md#L52)、[orchestration-flow.md](/Users/rocky243/.claude/skills/ultra-verify/references/orchestration-flow.md#L40)、[codex-cli-reference.md](/Users/rocky243/.claude/skills/codex-collab/references/codex-cli-reference.md#L96)  
  多处写“Set Bash timeout to 300000ms”，但没有给出实际命令包装方式，`timeout` 也不是所有环境默认存在，文档可执行性偏弱。  
  建议：给出明确可运行示例，或改成宿主工具层的超时参数说明，不要只写抽象要求。

- `Info` 位置：[codex-collab/SKILL.md](/Users/rocky243/.claude/skills/codex-collab/SKILL.md#L20)、[gemini-collab/SKILL.md](/Users/rocky243/.claude/skills/gemini-collab/SKILL.md#L20)  
  Usage 里写了 `/codex-collab review <file>` 和 `/gemini-collab review <file>`，但正文没有定义对应的文件级 review 执行协议。Gemini 示例有 stdin 方案，Codex review 文档则基本围绕 git diff。  
  建议：补一段“单文件 review”的规范命令，并说明何时用 `review`，何时退回 `exec`/stdin 模式。

**验证命令**

```bash
codex review --help
codex exec --help
rg -n -- '--commit-title|--title|codex-raw.txt|codex-output.md|--full-auto|--sandbox read-only|\$\(cat \$FILE\)|gemini --version|300000ms' \
  /Users/rocky243/.claude/skills/codex-collab \
  /Users/rocky243/.claude/skills/gemini-collab \
  /Users/rocky243/.claude/skills/ultra-verify
```

本次审计基于工作区真实文件和本机 `codex` 帮助输出完成；`gemini` 二进制存在，但其 `--help/--version` 在当前环境里未及时返回，所以关于 Gemini CLI flag 的结论以文件内部一致性和运行风险为主。