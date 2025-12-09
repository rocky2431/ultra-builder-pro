# Thinking Modes Test & Validation Guide

**Purpose**: Verify ultrathink and /max-think have been successfully separated and can be used independently

---

## Test Preparation

### 1. Confirm Modifications

```bash
# Check if /max-think description has been updated
head -5 ~/.claude/commands/max-think.md

# Should see new description:
# description: 6-dimensional structured analysis framework...
```

### 2. Restart Claude Code (if needed)

```bash
# Exit current session
exit

# Restart Claude Code
claude
```

---

## Test Cases

### ✅ Test 1: ultrathink Independent Use

**Input**:
```
ultrathink What are the key considerations for building a scalable API?
```

**Expected Behavior**:
- ✅ Claude should perform deep thinking (31,999 tokens)
- ✅ Output free-form analysis
- ❌ **Should NOT** auto-trigger /max-think command
- ❌ **Should NOT** show 6-dimensional structured framework

**Success Indicators**:
- Output lacks fixed "Phase 1", "Phase 2" structure
- No explicit "Technical Dimension", "Business Dimension" sections
- Thinking process flows naturally, non-templated

---

### ✅ Test 2: /max-think Independent Use

**Input**:
```
/max-think "Should we use REST or GraphQL for our new API?"
```

**Expected Behavior**:
- ✅ Should trigger /max-think command
- ✅ Output 6-dimensional structured analysis
- ✅ Include: Problem Understanding, Multi-Dimensional Analysis, Scenario Planning, Recommendation

**Success Indicators**:
- Output contains explicit 6 dimensions (Technical, Business, Team, Ecosystem, Strategic, Meta)
- Has 3+ scenario comparisons
- Has clear recommendation and implementation path

---

### ✅ Test 3: think Keyword (Lower Level)

**Input**:
```
think What's the difference between REST and GraphQL?
```

**Expected Behavior**:
- ✅ Uses 4,000 tokens thinking budget (less than ultrathink)
- ✅ Free-form output
- ❌ Does not trigger /max-think

---

### ✅ Test 4: megathink Keyword (Mid Level)

**Input**:
```
megathink How should I design a microservices architecture?
```

**Expected Behavior**:
- ✅ Uses 10,000 tokens thinking budget
- ✅ Free-form output
- ❌ Does not trigger /max-think

---

### ✅ Test 5: Combined Usage

**Input**:
```
ultrathink /max-think "Design a distributed caching strategy for high-traffic e-commerce platform"
```

**Expected Behavior**:
- ✅ ultrathink allocates 31,999 tokens
- ✅ /max-think provides 6-dimensional framework
- ✅ Combined effect: ultra-deep reasoning + structured output

**Success Indicators**:
- Output extremely detailed (due to ultrathink's deep thinking)
- Has clear structure (6-dimensional framework)
- Possibly includes 5+ scenario comparisons (vs standard 3)

---

### ✅ Test 6: Normal Conversation (No Keywords)

**Input**:
```
What is the difference between var, let, and const in JavaScript?
```

**Expected Behavior**:
- ✅ Uses standard conversation mode (~4K tokens)
- ✅ Concise, clear answer
- ❌ Does not trigger any special thinking modes

---

## Test Results Recording

### Test 1: ultrathink Independent Use
- [ ] Pass
- [ ] Fail (describe issue): ___________

### Test 2: /max-think Independent Use
- [ ] Pass
- [ ] Fail (describe issue): ___________

### Test 3: think Keyword
- [ ] Pass
- [ ] Fail (describe issue): ___________

### Test 4: megathink Keyword
- [ ] Pass
- [ ] Fail (describe issue): ___________

### Test 5: Combined Usage
- [ ] Pass
- [ ] Fail (describe issue): ___________

### Test 6: Normal Conversation
- [ ] Pass
- [ ] Fail (describe issue): ___________

---

## Troubleshooting

### Issue 1: ultrathink Still Triggers /max-think

**Possible Causes**:
1. Claude's description matching mechanism still detecting relevance
2. Modifications not effective (need restart)
3. Cache issues

**Solutions**:
```bash
# 1. Confirm description updated
cat ~/.claude/commands/max-think.md | head -5

# 2. Clear Claude cache (if exists)
rm -rf ~/.claude/cache/

# 3. Full restart of Claude Code
killall claude
claude

# 4. If still failing, further modify description to completely remove "analysis" keyword
# Change to more specific terms like "multi-dimensional framework"
```

---

### Issue 2: /max-think Not Working

**Possible Causes**:
1. Command file corrupted
2. Description modification error

**Solutions**:
```bash
# Verify command file syntax
cat ~/.claude/commands/max-think.md | head -10

# Ensure YAML frontmatter format correct (surrounded by ---)
```

---

### Issue 3: Combined Usage Not Working

**Possible Causes**:
1. ultrathink and /max-think conflict
2. Token budget exceeded

**Solutions**:
```bash
# Check MAX_THINKING_TOKENS setting in settings.json
cat ~/.claude/settings.json | grep MAX_THINKING_TOKENS

# If set to 64000, consider lowering to 32000
```

---

## Performance Benchmarks

### Token Consumption Comparison (Reference)

| Test Scenario | Thinking Tokens | Output Tokens | Total |
|--------------|----------------|---------------|-------|
| Normal conversation | ~1K | ~2K | ~3K |
| think | 4K | ~2K | ~6K |
| megathink | 10K | ~3K | ~13K |
| ultrathink | 31,999 | ~4K | ~36K |
| /max-think (Simple) | 8K | ~5K | ~13K |
| /max-think (Medium) | 16K | ~8K | ~24K |
| /max-think (Complex) | 24K | ~12K | ~36K |
| ultrathink + /max-think | 31,999 + 24K | ~15K | ~71K |

---

## Success Criteria

All 6 test cases pass, meaning:
- ✅ ultrathink independent use, does not trigger /max-think
- ✅ /max-think independent use, works normally
- ✅ think and megathink work normally
- ✅ Combined usage produces expected effect
- ✅ Normal conversation unaffected

---

## Next Steps

After tests pass:
1. ✅ Start using new separated mode
2. ✅ Refer to `thinking-modes-guide.md` to choose appropriate tool
3. ✅ Adjust configuration based on actual usage

If tests fail:
1. Check troubleshooting section
2. If necessary, contact technical support or submit issue

---

**Test Date**: ___________
**Tester**: ___________
**Claude Code Version**: ___________
**Test Result**: [ ] All Pass [ ] Partial Pass [ ] Fail
