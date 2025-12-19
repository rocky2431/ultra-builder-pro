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

interface SkillTriggerLog {
  timestamp: string;
  skill: string;
  matchReason: string;
  enforcement: string;
  priority: string;
  promptPreview: string;
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
 * Log skill trigger event for debugging and optimization
 */
function logSkillTrigger(logs: SkillTriggerLog[]): void {
  if (logs.length === 0) return;

  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const claudeDir = projectDir.endsWith('.claude') ? projectDir : path.join(projectDir, '.claude');
  const logsDir = path.join(claudeDir, 'logs');
  const logFile = path.join(logsDir, 'skill-triggers.jsonl');

  try {
    // Ensure logs directory exists
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }

    // Append logs as JSONL (one JSON object per line)
    const logEntries = logs.map(log => JSON.stringify(log)).join('\n') + '\n';
    fs.appendFileSync(logFile, logEntries);

    // Rotate log file if > 1MB
    const stats = fs.statSync(logFile);
    if (stats.size > 1024 * 1024) {
      const archivePath = path.join(logsDir, `skill-triggers-${Date.now()}.jsonl`);
      fs.renameSync(logFile, archivePath);
    }
  } catch (error) {
    // Silent fail - logging should not block execution
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
function analyzeAndSuggestSkills(prompt: string): { skills: string[], logs: SkillTriggerLog[] } {
  const rules = loadSkillRules();
  const recentFiles = getRecentFiles();
  const matchedSkills: Array<{name: string, priority: string, enforcement: string, matchReason: string}> = [];
  const timestamp = new Date().toISOString();
  const promptPreview = prompt.length > 100 ? prompt.substring(0, 100) + '...' : prompt;

  for (const [skillName, rule] of Object.entries(rules.skills)) {
    let matched = false;
    let matchReason = '';

    // Check prompt triggers
    if (rule.promptTriggers) {
      if (rule.promptTriggers.keywords &&
          matchKeywords(prompt, rule.promptTriggers.keywords)) {
        matched = true;
        matchReason = 'keyword';
      }

      if (rule.promptTriggers.intentPatterns &&
          matchIntentPatterns(prompt, rule.promptTriggers.intentPatterns)) {
        matched = true;
        matchReason = matchReason ? `${matchReason}+intent` : 'intent';
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
        matchReason = matchReason ? `${matchReason}+file` : 'file';
      }
    }

    if (matched) {
      matchedSkills.push({
        name: skillName,
        priority: rule.priority,
        enforcement: rule.enforcement,
        matchReason
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

  // Generate log entries
  const logs: SkillTriggerLog[] = matchedSkills.map(s => ({
    timestamp,
    skill: s.name,
    matchReason: s.matchReason,
    enforcement: s.enforcement,
    priority: s.priority,
    promptPreview
  }));

  return { skills: matchedSkills.map(s => s.name), logs };
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

    // Analyze and get matched skills with logs
    const { skills: matchedSkills, logs } = analyzeAndSuggestSkills(userPrompt);

    // Log skill triggers for debugging and optimization
    logSkillTrigger(logs);

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
