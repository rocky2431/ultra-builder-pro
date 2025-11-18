#!/usr/bin/env ts-node

import * as fs from 'fs';
import * as path from 'path';

interface SkillRule {
  type: string;
  enforcement: 'suggest' | 'block' | 'warn' | 'auto';
  priority: string;
  description: string;
  promptTriggers?: {
    keywords?: string[];
    intentPatterns?: string[];
  };
  fileTriggers?: {
    pathPatterns?: string[];
    pathExclusions?: string[];
    contentPatterns?: string[];
  };
  blockMessage?: string;
}

interface SkillRules {
  version: string;
  description: string;
  skills: Record<string, SkillRule>;
}

interface RecentFile {
  file: string;
  timestamp: string;
}

/**
 * Load skill rules from skill-rules.json
 */
function loadSkillRules(): SkillRules {
  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  // If projectDir already ends with .claude, don't add it again
  const claudeDir = projectDir.endsWith('.claude') ? projectDir : path.join(projectDir, '.claude');
  const rulesPath = path.join(claudeDir, 'skills/skill-rules.json');

  if (!fs.existsSync(rulesPath)) {
    // No rules file, return empty
    return { version: '1.0', description: '', skills: {} };
  }

  try {
    const content = fs.readFileSync(rulesPath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error(`⚠️ Error loading skill-rules.json: ${error}`);
    return { version: '1.0', description: '', skills: {} };
  }
}

/**
 * Get recently modified files from cache
 */
function getRecentFiles(): string[] {
  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  // If projectDir already ends with .claude, don't add it again
  const claudeDir = projectDir.endsWith('.claude') ? projectDir : path.join(projectDir, '.claude');
  const cacheFile = path.join(claudeDir, 'cache/recent-files.json');

  if (!fs.existsSync(cacheFile)) {
    return [];
  }

  try {
    const content = fs.readFileSync(cacheFile, 'utf-8');
    const files: RecentFile[] = JSON.parse(content);
    return files.map(f => f.file);
  } catch (error) {
    return [];
  }
}

/**
 * Match keywords in prompt (case-insensitive)
 */
function matchKeywords(prompt: string, keywords: string[]): boolean {
  const lowerPrompt = prompt.toLowerCase();
  return keywords.some(kw => lowerPrompt.includes(kw.toLowerCase()));
}

/**
 * Match intent patterns using regex
 */
function matchIntentPatterns(prompt: string, patterns: string[]): boolean {
  return patterns.some(pattern => {
    try {
      const regex = new RegExp(pattern, 'i');
      return regex.test(prompt);
    } catch (error) {
      return false;
    }
  });
}

/**
 * Match file path patterns using glob-style matching
 */
function matchFilePatterns(files: string[], patterns: string[], exclusions?: string[]): boolean {
  // Convert glob patterns to regex
  const convertGlobToRegex = (pattern: string): RegExp => {
    const regexPattern = pattern
      .replace(/\*\*/g, '.*')
      .replace(/\*/g, '[^/]*')
      .replace(/\./g, '\\.');
    return new RegExp(`^${regexPattern}$`);
  };

  return files.some(file => {
    // Check exclusions first
    if (exclusions) {
      const excluded = exclusions.some(excl => {
        const regex = convertGlobToRegex(excl);
        return regex.test(file);
      });
      if (excluded) return false;
    }

    // Check if matches any pattern
    return patterns.some(pattern => {
      const regex = convertGlobToRegex(pattern);
      return regex.test(file);
    });
  });
}

/**
 * Analyze prompt and recent files to determine which skills to suggest
 */
function analyzeAndSuggestSkills(prompt: string): string[] {
  const rules = loadSkillRules();
  const recentFiles = getRecentFiles();
  const matchedSkills: Array<{name: string, priority: string, enforcement: string}> = [];

  for (const [skillName, rule] of Object.entries(rules.skills)) {
    let matched = false;
    let matchReason = '';

    // Check prompt triggers
    if (rule.promptTriggers) {
      if (rule.promptTriggers.keywords &&
          matchKeywords(prompt, rule.promptTriggers.keywords)) {
        matched = true;
        matchReason = 'keyword match';
      }

      if (rule.promptTriggers.intentPatterns &&
          matchIntentPatterns(prompt, rule.promptTriggers.intentPatterns)) {
        matched = true;
        matchReason = 'intent pattern match';
      }
    }

    // Check file triggers if we have recent files
    if (recentFiles.length > 0 && rule.fileTriggers?.pathPatterns) {
      if (matchFilePatterns(
        recentFiles,
        rule.fileTriggers.pathPatterns,
        rule.fileTriggers.pathExclusions
      )) {
        matched = true;
        matchReason = matchReason ? `${matchReason} + file context` : 'file context';
      }
    }

    if (matched) {
      matchedSkills.push({
        name: skillName,
        priority: rule.priority,
        enforcement: rule.enforcement
      });
    }
  }

  // Sort by priority (critical > high > medium > low)
  const priorityOrder: Record<string, number> = {
    'critical': 4,
    'high': 3,
    'medium': 2,
    'low': 1
  };

  matchedSkills.sort((a, b) => {
    const priorityDiff = (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
    if (priorityDiff !== 0) return priorityDiff;
    // If same priority, sort by enforcement (block > warn > suggest > auto)
    const enforcementOrder: Record<string, number> = {
      'block': 4,
      'warn': 3,
      'suggest': 2,
      'auto': 1
    };
    return (enforcementOrder[b.enforcement] || 0) - (enforcementOrder[a.enforcement] || 0);
  });

  return matchedSkills.map(s => s.name);
}

/**
 * Generate skill reminder message
 */
function generateSkillReminder(skills: string[]): string {
  if (skills.length === 0) return '';

  const rules = loadSkillRules();
  const critical = skills.filter(s => rules.skills[s]?.priority === 'critical');
  const high = skills.filter(s => rules.skills[s]?.priority === 'high');
  const others = skills.filter(s => !critical.includes(s) && !high.includes(s));

  let message = '\n📚 SKILL SUGGESTIONS\n\n';

  if (critical.length > 0) {
    message += '🔴 **Critical Skills** (强烈建议):\n';
    critical.forEach(skill => {
      const desc = rules.skills[skill]?.description || '';
      message += `  - **${skill}**: ${desc}\n`;
    });
    message += '\n';
  }

  if (high.length > 0) {
    message += '🟡 **High Priority Skills** (建议使用):\n';
    high.forEach(skill => {
      const desc = rules.skills[skill]?.description || '';
      message += `  - **${skill}**: ${desc}\n`;
    });
    message += '\n';
  }

  if (others.length > 0) {
    message += '🔵 **Other Skills** (可选):\n';
    others.forEach(skill => {
      const desc = rules.skills[skill]?.description || '';
      message += `  - **${skill}**: ${desc}\n`;
    });
    message += '\n';
  }

  message += '💡 **使用方式**: 使用 Skill 工具调用相应的 Skill\n';
  message += '📖 **配置位置**: .claude/skills/skill-rules.json\n';

  return message;
}

/**
 * Main execution
 */
function main() {
  try {
    // Get user prompt from environment variable
    const userPrompt = process.env.CLAUDE_USER_PROMPT || '';

    if (!userPrompt) {
      // No prompt to analyze
      process.exit(0);
    }

    // Analyze and get matched skills
    const matchedSkills = analyzeAndSuggestSkills(userPrompt);

    // Generate and output reminder if skills matched
    if (matchedSkills.length > 0) {
      const reminder = generateSkillReminder(matchedSkills);
      console.log(reminder);
    }

    process.exit(0);
  } catch (error) {
    console.error(`⚠️ skill-activation-prompt hook error: ${error}`);
    // Don't block on error
    process.exit(0);
  }
}

// Run main
main();
