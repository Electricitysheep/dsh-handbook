import { describe, expect, it } from 'vitest'
import { decidePolicy } from '../src/policy.ts'

describe('decidePolicy', () => {
  it('keeps selected effort for a fresh prompt', () => {
    expect(decidePolicy({ recentCalls: [], selected: 'high' })).toBe('high')
  })
  it('downgrades simple tool chains to low', () => {
    expect(decidePolicy({
      recentCalls: [{ name: 'write', argsSize: 40 }],
      selected: 'high',
    })).toBe('low')
  })
  it('keeps selected for heavy tools', () => {
    expect(decidePolicy({
      recentCalls: [{ name: 'mcp__db', argsSize: 4000 }],
      selected: 'high',
    })).toBe('high')
  })
})
