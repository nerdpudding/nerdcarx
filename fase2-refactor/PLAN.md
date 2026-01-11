# Fase 2: Refactor + Docker

**Status:** Gepland (na Fase 1 + TTS)
**Doel:** Code opschonen en volledig dockerizen

## Scope

Na Fase 1 hebben we een werkende desktop demo. In Fase 2 maken we de code:
- **Beter onderhoudbaar** (SOLID, KISS, DRY)
- **Volledig containerized** (docker-compose voor hele stack)
- **Klaar voor Pi integratie** (API's stabiel, documentatie compleet)

---

## Te Doen

### 1. Code Cleanup

**Orchestrator (`fase1-desktop/orchestrator/`):**
- [ ] Split `main.py` in modules (routes, services, models)
- [ ] Dependency injection voor config
- [ ] Error handling verbeteren
- [ ] Logging toevoegen
- [ ] Tests schrijven

**VAD Client (`fase1-desktop/vad-desktop/`):**
- [ ] Code review en cleanup
- [ ] Betere error handling

### 2. Dockerizen

**Orchestrator:**
- [ ] Dockerfile maken
- [ ] Toevoegen aan docker-compose.yml
- [ ] Health checks configureren

**Volledige Stack:**
```yaml
# docker-compose.yml (concept)
services:
  voxtral:    # STT - GPU1
  ollama:     # LLM - GPU0
  tts:        # TTS - GPU? (na onderzoek)
  orchestrator:
    depends_on: [voxtral, ollama, tts]
```

### 3. Documentatie

- [ ] API documentatie (OpenAPI/Swagger)
- [ ] Setup instructies updaten
- [ ] Troubleshooting guide

### 4. Testing

- [ ] Unit tests voor orchestrator
- [ ] Integration tests (hele pipeline)
- [ ] Performance benchmarks

---

## Principes

Uit de README:

> **KISS** - Keep It Simple, Stupid
> **SOLID** - Single responsibility, etc.
> **DRY** - Don't Repeat Yourself

### Concreet:

| Principe | Toepassing |
|----------|------------|
| KISS | Geen onnodige abstracties |
| Single Responsibility | Aparte modules voor routes, services, config |
| DRY | Centrale config, geen duplicatie |
| Loose Coupling | Services communiceren via HTTP/WS |

---

## Niet in Scope

- Pi hardware integratie (→ Fase 3)
- Nieuwe features (→ Fase 1 of later)
- Wake word (→ Fase 3)

---

## Exit Criteria

Fase 2 is klaar wanneer:
- [ ] `docker compose up` start hele stack
- [ ] Alle tests slagen
- [ ] Code review gedaan
- [ ] API documentatie compleet

---

[← Terug naar README](../README.md)
