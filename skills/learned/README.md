# Learned Patterns

此目录存储通过 `/learn` 命令提取的模式。

## 文件命名约定

- `pattern-name_unverified.md` - 刚提取，置信度为 Speculation
- `pattern-name.md` - 已验证，置信度为 Inference 或 Fact

## 置信度级别

| 级别 | 文件后缀 | 描述 |
|------|---------|------|
| Speculation | `_unverified` | 刚提取，未经验证 |
| Inference | 无后缀 | 人工审查通过 |
| Fact | 无后缀 + 文件内标注 | 多次成功使用验证 |

## 验证流程

1. 运行 `/learn` 提取模式
2. 模式保存为 `*_unverified.md`
3. 人工审查，如果有效则移除 `_unverified` 后缀
4. 多次成功使用后，在文件内更新置信度为 Fact

## 加载优先级

当模式冲突时: Fact > Inference > Speculation
