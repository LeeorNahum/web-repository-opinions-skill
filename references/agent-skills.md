# Agent Skills

Build an Agent Skill when an agent needs workflow guidance for using a product. Base that guidance on the public product contract, not the internal storage model, and keep product rules in the product rather than reimplementing them in prose.

Keep selection metadata and operating instructions separate. The skill description states what the skill does and when it applies. The `SKILL.md` body carries the instructions the agent follows after selection.

Teach the agent to search with the narrowest filter the interface offers, preserve canonical product and source URLs, and route to supporting material only when the current task needs it. Match every instruction to fields and operations the public interface actually exposes.

Use the open Agent Skills directory contract for the shared instruction artifact. Keep host-specific installation metadata and connection steps in the owning adapter when they are only packaging concerns. When configuring that host is the skill's workflow, keep its required connection steps and runtime prerequisites in the skill instructions, including how the agent satisfies them.
