#!/usr/bin/env python3
"""
User Prompt Agent Hook - UserPromptSubmit
Analyzes user intent and suggests appropriate agents

Keyword triggers:
- e2e/test flow -> e2e-runner
- auth/login/password/payment -> security-reviewer
- smart contract -> smart-contract-specialist + auditor

This is a reminder only, does not block.
"""

import sys
import json
import re

# Intent patterns to agent mapping
INTENT_AGENTS = [
    # E2E testing triggers
    (r'\b(e2e|end-to-end|integration)\s+test\b',
     'e2e-runner', 'E2E testing task'),
    (r'\btest\s+(?:the\s+)?(?:user\s+)?flow\b',
     'e2e-runner', 'User flow testing'),
    (r'\bplaywright\b',
     'e2e-runner', 'Playwright testing'),
    (r'\b(flaky|failing)\s+(?:e2e|integration)\s+test\b',
     'e2e-runner', 'E2E test debugging'),

    # Security triggers (MANDATORY)
    (r'\b(auth|authentication|login|logout|session)\b',
     'security-reviewer', 'Authentication-related - SECURITY REVIEW MANDATORY'),
    (r'\b(password|credential|secret|token|api[_-]?key)\b',
     'security-reviewer', 'Credential handling - SECURITY REVIEW MANDATORY'),
    (r'\b(payment|checkout|billing|stripe|paypal)\b',
     'security-reviewer', 'Payment processing - SECURITY REVIEW MANDATORY'),
    (r'\b(permission|role|access|authorization|rbac|acl)\b',
     'security-reviewer', 'Authorization logic - SECURITY REVIEW MANDATORY'),
    (r'\b(encrypt|decrypt|hash|salt|crypto)\b',
     'security-reviewer', 'Cryptography - SECURITY REVIEW MANDATORY'),

    # Smart contract triggers (BOTH agents for any contract work)
    (r'\b(solidity|smart\s*contract|erc-?20|erc-?721|defi|web3|hardhat|foundry)\b',
     'smart-contract-specialist', 'Smart contract development - BOTH AGENTS MANDATORY'),
    (r'\b(solidity|smart\s*contract|erc-?20|erc-?721|defi|web3|hardhat|foundry)\b',
     'smart-contract-auditor', 'Smart contract security - BOTH AGENTS MANDATORY'),
    (r'\b(audit|vulnerability|exploit|reentrancy|overflow|underflow)\b.*\b(contract|solidity)\b',
     'smart-contract-auditor', 'Contract security audit - PRIORITY'),

    # Frontend triggers
    (r'\b(ui|ux|component|styled?|css|tailwind|responsive)\b',
     'frontend-developer', 'Frontend development'),
    (r'\b(react|vue|svelte|angular|nextjs|nuxt)\b.*\b(component|page|hook)\b',
     'frontend-developer', 'Frontend framework task'),
    (r'\b(accessibility|a11y|aria|screen\s*reader)\b',
     'frontend-developer', 'Accessibility implementation'),

    # Documentation triggers
    (r'\b(document|readme|docs|api\s+doc)\b',
     'doc-updater', 'Documentation task'),
    (r'\b(update|write|generate)\b.*\b(documentation|readme)\b',
     'doc-updater', 'Documentation update'),

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
    except json.JSONDecodeError:
        print(input_data)
        return

    prompt = hook_input.get('prompt', '')

    if not prompt:
        print(input_data)
        return

    # Analyze prompt
    agent_suggestions, skill_suggestions = analyze_prompt(prompt)

    # Output suggestions
    if agent_suggestions or skill_suggestions:
        print("", file=sys.stderr)

        if agent_suggestions:
            print("[Agent Suggestion] Based on your request:", file=sys.stderr)

            # Show mandatory first
            mandatory = [s for s in agent_suggestions if s['priority'] == 'MANDATORY']
            recommended = [s for s in agent_suggestions if s['priority'] == 'Recommended']

            for s in mandatory:
                print(f"  [MANDATORY] {s['agent']} - {s['reason']}", file=sys.stderr)

            for s in recommended[:3]:  # Limit to 3 recommendations
                print(f"  [Recommended] {s['agent']} - {s['reason']}", file=sys.stderr)

            print("", file=sys.stderr)

        if skill_suggestions:
            print("[Skill Suggestion] Consider using:", file=sys.stderr)
            for s in skill_suggestions[:2]:  # Limit to 2 skills
                print(f"  [Skill] /{s['skill']} - {s['reason']}", file=sys.stderr)
            print("", file=sys.stderr)

    # Always pass through
    print(input_data)


if __name__ == '__main__':
    main()
