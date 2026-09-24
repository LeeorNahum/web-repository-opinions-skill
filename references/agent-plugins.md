# Agent Plugins

Package each shared skill and any shared protocol implementation once across agent hosts. Add small host-specific descriptors only where each host's installation contract requires them, and keep host-specific setup in its owning adapter. Derive repeated identity, version, and endpoint values from one owner, then validate the files that are actually packaged.

Treat discovery and freshness as separate contracts. Marketplace metadata, installed package files, a live tool catalog, and instructions already read into a conversation can each update at a different time. An update reaching one layer does not prove that another layer refreshed.

Verify automatic discovery, instruction following, and update pickup in fresh sessions. Test main sessions and child agents separately because tool and instruction inheritance is host behavior, not a property of the package format. State compatibility from observed client behavior rather than from a shared file format alone.

Before grading a fresh-client run, confirm that the intended configuration, plugin version, skill catalog, and connection reached that session. An installed package or a configuration listing proves setup state, not model-visible context. Classify setup failures separately from product behavior failures.
