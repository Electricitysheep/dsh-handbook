import { describe, expect, it, vi } from 'vitest'
import { apply } from '../src/index.ts'

type RequestHandler = (
  payload: Record<string, unknown>,
  next: () => unknown,
) => unknown | Promise<unknown>

function createHarness() {
  let eventName: string | undefined
  let handler: RequestHandler | undefined
  const on = vi.fn((event: string, callback: RequestHandler) => {
    eventName = event
    handler = callback
  })

  apply({ on } as unknown as Parameters<typeof apply>[0])

  return {
    eventName,
    on,
    run: async (payload: Record<string, unknown>, next: () => unknown) => {
      if (!handler) throw new Error('plugin did not register a request handler')
      return handler(payload, next)
    },
  }
}

function agentWithEvents(events: readonly unknown[]) {
  return { agent: { session: { events } } }
}

describe('plugin waterfall contract', () => {
  it('registers exactly one agent/request listener', () => {
    const harness = createHarness()

    expect(harness.eventName).toBe('agent/request')
    expect(harness.on).toHaveBeenCalledTimes(1)
  })

  it('awaits next, preserves the seed, and only overrides reasoning effort', async () => {
    const harness = createHarness()
    const next = vi.fn(async () => ({
      provider: 'deepseek-official',
      model: 'deepseek-reasoner',
      reasoningEffort: 'max',
      tools: ['read', 'write'],
    }))

    const result = await harness.run(agentWithEvents([]), next)

    expect(next).toHaveBeenCalledTimes(1)
    expect(result).toEqual({
      provider: 'deepseek-official',
      model: 'deepseek-reasoner',
      reasoningEffort: 'high',
      tools: ['read', 'write'],
    })
  })

  it('uses only the eight most recent tool calls', async () => {
    const harness = createHarness()
    const oldHeavyCalls = Array.from({ length: 5 }, () => ({
      type: 'tool/call',
      data: { name: 'mcp__database', arguments: 'x'.repeat(4000) },
    }))
    const recentSimpleCalls = Array.from({ length: 8 }, () => ({
      type: 'tool/call',
      data: { name: 'write', arguments: '{"path":"note.md"}' },
    }))

    const result = await harness.run(
      agentWithEvents([...oldHeavyCalls, ...recentSimpleCalls]),
      async () => ({ reasoningEffort: 'max' }),
    )

    expect(result).toEqual({ reasoningEffort: 'low' })
  })

  it('ignores non-tool events when deciding the effort', async () => {
    const harness = createHarness()
    const result = await harness.run(
      agentWithEvents([
        { type: 'agent/status', data: { name: 'mcp__database', arguments: 'x'.repeat(4000) } },
        { type: 'tool/call', data: { name: 'read', arguments: '{"path":"README.md"}' } },
      ]),
      async () => ({ provider: 'mock', reasoningEffort: 'max' }),
    )

    expect(result).toEqual({ provider: 'mock', reasoningEffort: 'low' })
  })

  it('propagates downstream waterfall failures', async () => {
    const harness = createHarness()
    const error = new Error('downstream listener failed')

    await expect(harness.run(agentWithEvents([]), async () => {
      throw error
    })).rejects.toBe(error)
  })
})
