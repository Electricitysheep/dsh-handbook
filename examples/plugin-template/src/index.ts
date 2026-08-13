/**
 * Template host plugin: inject a policy-chosen reasoning_effort into every
 * agent/request waterfall (extension point, see dsh-handbook ch.4).
 */
import type { Context } from '@deepseek-ai/cordis'
import { decidePolicy, type ToolCallSample } from './policy.ts'

const WINDOW = 8

function recentToolCalls(agent: unknown): ToolCallSample[] {
  const events = (agent as { session?: { events?: readonly unknown[] } }).session?.events ?? []
  const out: ToolCallSample[] = []
  for (let i = events.length - 1; i >= 0 && out.length < WINDOW; i--) {
    const e = events[i] as { type?: string; data?: { name?: string; arguments?: unknown } } | undefined
    if (e?.type !== 'tool/call') continue
    out.push({
      name: e.data?.name ?? 'tool',
      argsSize: typeof e.data?.arguments === 'string' ? e.data.arguments.length : 0,
    })
  }
  return out.reverse()
}

export function apply(ctx: Context): void {
  // npm doesn't re-export dsh's event-type augmentation; widen at the boundary.
  const on = ctx.on as unknown as (
    event: string,
    handler: (payload: Record<string, unknown>, next: () => unknown) => unknown | Promise<unknown>,
  ) => void

  on('agent/request', async (payload, next) => {
    const seed = await next() as { reasoningEffort?: unknown } // ⚠️ await next()
    const effort = decidePolicy({ recentCalls: recentToolCalls(payload.agent), selected: 'high' })
    return { ...seed, reasoningEffort: effort }
  })
}
