"""Project 3 source layer: one single-purpose fetcher per source type.

Design principle (see docs/values-as-ip-plan.md §2): fetch diverges, downstream
converges. Each source module casts as wide as its source allows and yields a
common `SourceRecord`; everything after (chunk -> classify -> embed -> score) is
the shared pipeline and never learns where the text came from.

Each source module exposes:
  NAME      str
  REGISTER  str   (one of base.REGISTERS)
  explore(cfg, client, limit) -> base.ExploreResult   # cheap census, for Phase 1a
  fetch(cfg, client)          -> Iterator[SourceRecord] # full pull, for Phase 1b

Register a module by importing it in base.REGISTRY.
"""
