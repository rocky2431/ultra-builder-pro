#!/usr/bin/env python3
"""
User Prompt Agent Hook - UserPromptSubmit
Analyzes user intent and suggests appropriate agents

Keyword triggers:
- auth/login/password/payment -> pr-review-toolkit:code-reviewer (MANDATORY)
- smart contract -> smart-contract-specialist + auditor

This is a reminder only, does not block.
"""

import sys
import json
import re

# Intent patterns to agent mapping
INTENT_AGENTS = [
    # Security triggers (MANDATORY) - use pr-review-toolkit:code-reviewer
    (r'\b(auth|authentication|login|logout|session)\b',
     'pr-review-toolkit:code-reviewer', 'Authentication-related - SECURITY REVIEW MANDATORY'),
    (r'\b(password|credential|secret|token|api[_-]?key)\b',
     'pr-review-toolkit:code-reviewer', 'Credential handling - SECURITY REVIEW MANDATORY'),
    (r'\b(payment|checkout|billing|stripe|paypal)\b',
     'pr-review-toolkit:code-reviewer', 'Payment processing - SECURITY REVIEW MANDATORY'),
    (r'\b(permission|role|access|authorization|rbac|acl)\b',
     'pr-review-toolkit:code-reviewer', 'Authorization logic - SECURITY REVIEW MANDATORY'),
    (r'\b(encrypt|decrypt|hash|salt|crypto)\b',
     'pr-review-toolkit:code-reviewer', 'Cryptography - SECURITY REVIEW MANDATORY'),

    # Smart contract triggers (BOTH agents for any contract work)
    (r'\b(solidity|smart\s*contract|erc-?20|erc-?721|defi|web3|hardhat|foundry)\b',
     'smart-contract-specialist', 'Smart contract development - BOTH AGENTS MANDATORY'),
    (r'\b(solidity|smart\s*contract|erc-?20|erc-?721|defi|web3|hardhat|foundry)\b',
     'smart-contract-auditor', 'Smart contract security - BOTH AGENTS MANDATORY'),
    (r'\b(audit|vulnerability|exploit|reentrancy|overflow|underflow)\b.*\b(contract|solidity)\b',
     'smart-contract-auditor', 'Contract security audit - PRIORITY'),

    # Refactoring triggers
    (r'\b(refactor|cleanup|clean\s+up|dead\s+code|unused)\b',
     'refactor-cleaner', 'Code cleanup task'),
    (r'\b(remove|delete)\s+(?:unused|dead)\s+(?:code|imports|dependencies)\b',
     'refactor-cleaner', 'Dead code removal'),

    # PR Review triggers - ONLY for explicit review requests
    (r'\b(review|check)\s+(?:my\s+)?(?:pr|pull\s*request)\b',
     'pr-review-toolkit:code-reviewer', 'PR code review - comprehensive review'),
    (r'\b(code\s*review|review\s+(?:the\s+)?code)\b',
     'pr-review-toolkit:code-reviewer', 'Code review - CLAUDE.md compliance check'),
    (r'\b(ready\s+(?:to|for)\s+(?:merge|pr|commit))\b',
     'pr-review-toolkit:code-reviewer', 'Pre-merge review recommended'),
    (r'\b(test\s+coverage|missing\s+tests|test\s+quality)\b',
     'pr-review-toolkit:pr-test-analyzer', 'Test coverage analysis'),
    (r'\b(error\s+handling|silent\s+fail|catch\s+block)\b',
     'pr-review-toolkit:silent-failure-hunter', 'Error handling review'),
    (r'\b(simplify|complexity|too\s+complex)\b',
     'pr-review-toolkit:code-simplifier', 'Code simplification'),
    (r'\b(type|types|typing|interface)\s+(?:design|quality|review)\b',
     'pr-review-toolkit:type-design-analyzer', 'Type design analysis'),
]


# Skill patterns - for suggesting our own skills
# NOTE: codex, gemini, promptup are user-invoked tools, NOT auto-triggered
INTENT_SKILLS = [
    # React/Next.js performance - based on SKILL.md triggers
    (r'\b(react|next\.?js|nextjs)\b.*\b(performance|optimize|slow|render)\b',
     'react-best-practices', 'React/Next.js performance optimization'),
    (r'\b(bundle|chunk|lazy\s*load|code\s*split|tree\s*shak)\b',
     'react-best-practices', 'Bundle optimization patterns'),
    (r'\b(rerender|re-render|memo|useMemo|useCallback)\b',
     'react-best-practices', 'React render optimization'),
    (r'\b(data\s*fetch|useSWR|useQuery|getServerSideProps|getStaticProps)\b',
     'react-best-practices', 'Data fetching patterns'),
    (r'\b(server\s*component|client\s*component|use\s*client|use\s*server)\b',
     'react-best-practices', 'React Server Components'),
    (r'\b(suspense|streaming|loading\s*state)\b',
     'react-best-practices', 'Async rendering patterns'),

    # UI/Design guidelines - based on SKILL.md triggers
    (r'\b(ui|ux|design)\s+(?:review|audit|check)\b',
     'web-design-guidelines', 'UI design compliance review'),
    (r'\b(accessibility|a11y|wcag|aria)\b',
     'web-design-guidelines', 'Accessibility compliance check'),
    (r'\breview\s+(?:my\s+)?(?:ui|site|interface)\b',
     'web-design-guidelines', 'UI review'),
    (r'\b(?:ui|web|interface)\s+(?:best\s*practices|guidelines)\b',
     'web-design-guidelines', 'Web interface best practices'),
]


def analyze_prompt(prompt: str) -> tuple:
    """Analyze user prompt and return agent and skill suggestions."""
    agent_suggestions = []
    skill_suggestions = []
    prompt_lower = prompt.lower()

    # Check agent triggers
    for pattern, agent, reason in INTENT_AGENTS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            # Avoid duplicates
            if not any(s['agent'] == agent for s in agent_suggestions):
                is_mandatory = 'MANDATORY' in reason
                agent_suggestions.append({
                    'agent': agent,
                    'reason': reason,
                    'priority': 'MANDATORY' if is_mandatory else 'Recommended'
                })

    # Check skill triggers
    for pattern, skill, reason in INTENT_SKILLS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            # Avoid duplicates
            if not any(s['skill'] == skill for s in skill_suggestions):
                skill_suggestions.append({
                    'skill': skill,
                    'reason': reason
                })

    return agent_suggestions, skill_suggestions


def main():
    # Read stdin for hook input
    try:
        input_data = sys.stdin.read()
        hook_input = json.loads(input_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[user_prompt_agent] Failed to parse input: {e}", file=sys.stderr)
        print(json.dumps({}))
        return

    prompt = hook_input.get('prompt', '')

    if not prompt:
        print(input_data)
        return

    # Analyze prompt
    agent_suggestions, skill_suggestions = analyze_prompt(prompt)

    # Output suggestions to AI context (stdout for UserPromptSubmit)
    if agent_suggestions or skill_suggestions:
        context_lines = []

        if agent_suggestions:
            context_lines.append("[Agent Reminder] Based on user request:")

            # Show mandatory first
            mandatory = [s for s in agent_suggestions if s['priority'] == 'MANDATORY']
            recommended = [s for s in agent_suggestions if s['priority'] == 'Recommended']

            for s in mandatory:
                context_lines.append(f"  [MANDATORY] {s['agent']} - {s['reason']}")

            for s in recommended[:3]:
                context_lines.append(f"  [Recommended] {s['agent']} - {s['reason']}")

        if skill_suggestions:
            context_lines.append("")
            context_lines.append("[Skill Reminder] Consider using:")
            for s in skill_suggestions[:2]:
                context_lines.append(f"  [Skill] /{s['skill']} - {s['reason']}")

        context_lines.append("")
        context_lines.append("Use Task tool with subagent_type to invoke agents.")

        # Output JSON with additionalContext for AI visibility
        result = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n".join(context_lines)
            }
        }
        print(json.dumps(result))
    else:
        # No suggestions, pass through
        print(json.dumps({}))


if __name__ == '__main__':
    main()
