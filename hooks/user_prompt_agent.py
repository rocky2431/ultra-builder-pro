#!/usr/bin/env python3
"""
User Prompt Agent Hook - UserPromptSubmit
Analyzes user intent and suggests appropriate agents

Keyword triggers:
- add/implement/create + feature -> tdd-guide
- fix/debug + bug -> tdd-guide
- design/architect -> architect
- choose/select + library/framework -> architect
- e2e/test flow -> e2e-runner
- auth/login/password/payment -> security-reviewer

This is a reminder only, does not block.
"""

import sys
import json
import re

# Intent patterns to agent mapping
INTENT_AGENTS = [
    # Planner triggers (complex tasks need planning first)
    (r'\b(implement|add|build|create)\b.*\b(oauth|authentication|notification|caching|queue|workflow)\b',
     'planner', 'Complex feature - create implementation plan first'),
    (r'\bhow\s+(?:should|do)\s+(?:i|we)\s+implement\b',
     'planner', 'Implementation planning needed'),
    (r'\b(multi-?step|complex|large)\s+(?:feature|task|change)\b',
     'planner', 'Complex task - plan before implementing'),
    (r'\bnot\s+sure\s+(?:where|how)\s+to\s+start\b',
     'planner', 'Unclear path - planner will identify steps'),

    # TDD workflow triggers
    (r'\b(add|implement|create|build)\b.*\b(feature|function|api|endpoint|component)\b',
     'tdd-guide', 'New feature implementation - follow TDD workflow'),
    (r'\b(fix|debug|repair|solve)\b.*\b(bug|issue|error|problem)\b',
     'tdd-guide', 'Bug fix - write failing test first'),

    # Architecture triggers
    (r'\b(design|architect|structure)\b.*\b(system|module|service|api)\b',
     'architect', 'System design decision'),
    (r'\b(choose|select|pick|decide)\b.*\b(library|framework|tool|stack|database)\b',
     'architect', 'Technology choice decision'),
    (r'\b(should\s+(?:we|i)\s+use|which\s+(?:is|should))\b.*\b(better|best|prefer)\b',
     'architect', 'Technical comparison needed'),
    (r'\b(scale|scalability|performance|optimize)\b.*\b(architecture|design)\b',
     'architect', 'Architecture optimization'),

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

    # PR Review triggers
    (r'\b(review|check)\s+(?:my\s+)?(?:pr|pull\s*request|code)\b',
     'pr-review-toolkit:code-reviewer', 'PR code review'),
    (r'\b(create|open|submit)\s+(?:a\s+)?(?:pr|pull\s*request)\b',
     'pr-review-toolkit:code-reviewer', 'Pre-PR review recommended'),
    (r'\b(test\s+coverage|missing\s+tests|test\s+quality)\b',
     'pr-review-toolkit:pr-test-analyzer', 'Test coverage analysis'),
    (r'\b(error\s+handling|silent\s+fail|catch\s+block)\b',
     'pr-review-toolkit:silent-failure-hunter', 'Error handling review'),
    (r'\b(simplify|complexity|too\s+complex)\b',
     'pr-review-toolkit:code-simplifier', 'Code simplification'),
    (r'\b(type|types|typing|interface)\s+(?:design|quality|review)\b',
     'pr-review-toolkit:type-design-analyzer', 'Type design analysis'),
]


def analyze_prompt(prompt: str) -> list:
    """Analyze user prompt and return agent suggestions."""
    suggestions = []
    prompt_lower = prompt.lower()

    for pattern, agent, reason in INTENT_AGENTS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            # Avoid duplicates
            if not any(s['agent'] == agent for s in suggestions):
                is_mandatory = 'MANDATORY' in reason
                suggestions.append({
                    'agent': agent,
                    'reason': reason,
                    'priority': 'MANDATORY' if is_mandatory else 'Recommended'
                })

    return suggestions


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
    suggestions = analyze_prompt(prompt)

    # Output suggestions
    if suggestions:
        print("", file=sys.stderr)
        print("[Agent Suggestion] Based on your request:", file=sys.stderr)

        # Show mandatory first
        mandatory = [s for s in suggestions if s['priority'] == 'MANDATORY']
        recommended = [s for s in suggestions if s['priority'] == 'Recommended']

        for s in mandatory:
            print(f"  [MANDATORY] {s['agent']} - {s['reason']}", file=sys.stderr)

        for s in recommended[:3]:  # Limit to 3 recommendations
            print(f"  [Recommended] {s['agent']} - {s['reason']}", file=sys.stderr)

        print("", file=sys.stderr)

    # Always pass through
    print(input_data)


if __name__ == '__main__':
    main()
