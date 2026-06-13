# Stack

Default building blocks for a serious web product. Swap any tool, keep the role it fills.

| Role | Default | Swap when |
| --- | --- | --- |
| Monorepo | Turborepo + pnpm | A single deployable with no shared packages |
| Rendered public or hybrid surface | Next.js App Router + TypeScript | Static-only site, or a non-React target |
| Private client SPA | Vite + TypeScript | Server rendering or framework routing is required |
| Protocol-only HTTP app | Hono + TypeScript | The runtime already provides an equally small standards-based router |
| Styling | Tailwind + shadcn/ui + lucide-react | A design system already exists |
| App data + live sync | Convex | No realtime need, or an existing database |
| Auth | Clerk | Enterprise SSO requirements Clerk cannot meet |
| Billing | Stripe | A region or model Stripe does not serve |
| Heavy media | Cloudflare R2 | Already standardized on S3 or another store |
| Hosting | Vercel | A surface Vercel cannot host well |
| DNS | Cloudflare | Registrar lock-in |
| Email | Resend | An existing transactional provider |
| Rich text | BlockNote or block JSON | Plain text or markdown is enough |
| LLM calls | Vercel AI SDK | A provider SDK with no AI SDK adapter |

Pick the role first, then the tool. Do not let a tool dictate architecture: the same product rules must hold if the tool changes.

Keep the chosen tool out of paradigm names. A folder is `auth`, not `clerk`. A module is `origins`, not `vercel-origins`. Name by what it does, not who provides it.

TypeScript is the floor, not a choice. Prefer one language across apps, packages, and backend so types and helpers cross boundaries cleanly.

Prefer the latest stable release of each tool, and follow its current conventions rather than an older major's. Keep the parts of the toolchain that must agree on the same major, so the config, build, types, and rendered runtime stay consistent.
