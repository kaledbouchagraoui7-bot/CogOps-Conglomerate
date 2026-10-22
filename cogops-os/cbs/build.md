# CBS Ch.2 — Build (OS §7)
1. All builds go through the platform (pull-only): site factory → brand site; gateway → assistant; CRM → pipeline. No bespoke stacks.
2. KB grounding: assistant answers come from the company's own facts first (KB-first routing); anything else is labeled by provider mode. **Never fake AI.**
3. Design system: one skin, per-brand config. New company = content + configuration, not a rebuild.
4. Boring stack rule: proven infra (Pages-class static + Postgres/KV-class data). Experimental tech needs a DR.
