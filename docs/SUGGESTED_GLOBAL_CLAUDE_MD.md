# Suggested Global CLAUDE.md

Copy the content below to `~/.claude/CLAUDE.md`:

---

```markdown
## Project Organization

### Structure (adapt to project size)
```
project/
├── README.md                              # Overview + status (always)
├── ARCHITECTURE.md                        # Design (larger projects)
├── DECISIONS.md                           # Choices + rationale (larger projects)
├── DAILY_SCHEDULE_{date}.md               # Today's tasks (temp → archive/)
├── docs/                                  # Feature proposals, hardware, specs
├── phase{N}/ (or fase/sprint)             # Work by milestone
│   └── Phase{N}_Implementation_Plan.md    # HOW + order of tasks
└── archive/                               # Never delete, always archive
```

### Key Terms
- **Schedule/Planning** = WHEN do we do WHAT (time-bound)
- **Plan** = HOW do we do WHAT, in what ORDER (implementation)

### Plan Mode Rules
1. Plans go in project repo, NEVER only in `~/.claude/plans/`
2. Implementation plans: `phase{N}/Phase{N}_Implementation_Plan.md`
3. Daily schedules: root temporarily → `archive/daily-schedules/`
4. Update progress in both phase plans AND root README.md
5. Archive outdated content, never delete

### Quality Principles
- **SOLID, DRY, KISS** - Default yes, adapt to project needs
- **Modularity & flexibility** - Important for most projects
- **Testing** - Manual or automated based on requirements (ask if unclear)
- **Security** - Consider but not always enterprise-level (project dependent)

### Always
- Read README.md first, then relevant phase plan
- One source of truth (no duplicate info)
- Ask when project conventions are unclear
```
