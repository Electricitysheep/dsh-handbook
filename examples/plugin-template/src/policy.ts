/**
 * Pure policy for the template plugin: decide a reasoning_effort from the
 * recent tool-call history. Replace with your own logic — keep it
 * dependency-free so it unit-tests in milliseconds.
 */

export type EffortId = 'low' | 'high' | 'max'

export interface ToolCallSample {
  name: string
  argsSize: number
}

export interface PolicyInput {
  recentCalls: readonly ToolCallSample[]
  selected: EffortId
}

/** Simple/deterministic tool names (dsh built-ins: write/read/grep/glob/edit/bash…). */
const SIMPLE_RE = /^(write|read|grep|glob|edit|bash|ls|cat|fs_|todo)/i
const HEAVY = 800

export function decidePolicy(input: PolicyInput): EffortId {
  const { recentCalls, selected } = input
  if (recentCalls.length === 0) return selected
  const simple = recentCalls.filter(c => SIMPLE_RE.test(c.name) && c.argsSize < HEAVY).length
  return simple / recentCalls.length >= 0.75 ? 'low' : selected
}
