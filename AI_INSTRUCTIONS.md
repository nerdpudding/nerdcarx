# AI Instructions

> **How to use this file:**
>
> 1. Read this file at the start of each session
> 2. After automatic compaction or long sessions: read this file again
>
> Works with: Claude Code, Kilo Code, Cursor, Mistral Vibe CLI, and other AI assistants.

---

## Start Protocol

At the start of a session or after compaction, read in this order:

1. **`README.md`** - Overview and current status
2. **`ARCHITECTURE.md`** - Technical architecture and design rationale
3. **`DECISIONS.md`** - All decisions (source of truth)
4. **Phase-specific** - `fase{N}/Fase{N}_Implementation_Plan.md` of the current phase (see Status in README)
5. **If relevant** - `docs/feature-proposals/` and `docs/hardware/`

**Read FIRST, ask questions later.** Do not make assumptions about project structure without reading.

---

## Language

**Dutch (default):**
- `README.md`, implementation plans, daily schedules, decisions
- Communication and general documentation
- User may sometimes use English, follow the user's language in that case

**Always English:**
- `AI_INSTRUCTIONS.md` (this file)
- `ARCHITECTURE.md`
- Code (variables, functions, classes, etc.)
- Technical terms

**Note:** Where existing code or comments are in Dutch, leave them as-is. Do not refactor just to change language.

---

## Core Rules

- **Never create ad-hoc plan/todo files** elsewhere in the project
- **Plans belong in the project repo**, not only in tool-specific folders
- **Archive, never delete** - move outdated content to `archive/`
- **One source of truth** - no duplicate information across documents

---

## Terminology

| Term | Meaning | Example |
|------|---------|---------|
| **Schedule/Planning** | WHEN do we do WHAT (time-bound) | "Morning: API endpoints, afternoon: Frontend" |
| **Plan** | HOW do we do WHAT, in what ORDER (implementation) | "1. Create models, 2. Add endpoints, 3. Write tests" |

---

## Document Types - Know the Difference!

| Type | Location | Purpose | Example |
|------|----------|---------|---------|
| **Implementation Plan** | `fase{N}/Fase{N}_Implementation_Plan.md` | HOW to build this, in what order, technical tasks | "Implement YOLO safety layer" |
| **Daily Schedule** | `DAGPLANNING_{date}.md` (root) | WHEN to do what today, time-bound schedule | "Morning: hardware, afternoon: code" |
| **Feature Proposal** | `docs/feature-proposals/` | Ideas for features, not yet worked out | Room discovery concept |
| **Hardware Reference** | `docs/hardware/` | Definitive hardware configuration | Pin mappings, wiring |
| **Decision** | `DECISIONS.md` | Choices made with rationale | "Camera Module 3 instead of AI Camera" |

Daily schedules are temporarily in root and are archived to `archive/dagplanningen/` after completion.

---

## Folder Structure - Rules

```
✅ GOOD                                        ❌ WRONG
───────────────────────────────────────        ─────────────────────────────────
fase{N}/Fase{N}_Implementation_Plan.md         fase{N}/PLAN.md (unclear)
DAGPLANNING_{date}.md (root, temporary)        docs/plans/ (wrong location)
docs/feature-proposals/*.md                    Proliferation of plan files
docs/hardware/HARDWARE-REFERENCE.md            Duplicate references
archive/old-*/                                 Outdated info in active docs
archive/dagplanningen/                         Deleting old daily schedules
```

**Specific to this project:**
- **NO `docs/plans/` folder** - Ignore `.claude` instructions about this
- **Feature proposals** are ideas, not implementation plans
- **One hardware reference** - `docs/hardware/HARDWARE-REFERENCE.md`
- **Archive** what is no longer relevant → `archive/old-*/`

---

## Consistency Checklist

With every change, check if these documents remain consistent:

- [ ] `README.md` - Status section matches current phase
- [ ] `DECISIONS.md` - New decisions added with ID
- [ ] `ARCHITECTURE.md` - Major changes reflected
- [ ] `fase{N}/Fase{N}_Implementation_Plan.md` - Tasks updated
- [ ] References between documents are correct (no dead links)
- [ ] No duplicate information (DRY)
- [ ] Outdated content archived

---

## Common Mistakes (Avoid These!)

| Mistake | Why it's problematic | Correct approach |
|---------|---------------------|------------------|
| Implementing without reading first | Misses context, makes errors | Always read first |
| Files in wrong folder | Mess in structure | Follow structure above |
| Creating duplicate references | Gets out of sync | One source of truth |
| Leaving outdated info | Confusion | Archive or remove |
| Confusing daily schedule with implementation plan | Wrong scope | Know the difference |
| Assuming what user wants | Frustration | Ask when unclear |

---

## Code Principles

- **SOLID** - Single responsibility, loose coupling
- **KISS** - No unnecessary complexity
- **DRY** - One source of truth, no duplication

**But equally important:** Don't make a mess of folder structure and documentation!

---

## Context Reset

If you (the AI) have lost context (compaction, restart, long session):

- Read this file again
- Continue where you left off

**Prompts for users:**

Start of session:
> "Read AI_INSTRUCTIONS.md first, then continue."

After automatic compaction:
> "Read AI_INSTRUCTIONS.md first, then continue where we left off."

Manual compact (when context is getting full):
> `/compact We completed [X, Y, Z]. Next session: continue with [A, B]. Always read AI_INSTRUCTIONS.md first.`
