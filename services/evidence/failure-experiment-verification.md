# Failure experiment verification

October 13, 2026. Browser: /?pipeline=failure.

Real Langfuse provider preview returned four ERROR observations. Analyst request returned HTTP 200 through local EXO. Verified returned agentInput equals the configured task plus the exact preview JSON, byte-for-byte. Output appeared on failure-analyst. Direct MCP grant failure:failure-analyst remained disabled with no tools.

The response named a model connection failure, cited fb709c4ac74063d0, 5d0b12a80cfb21ad, 88eaef06d8d96f2c, and 1eef158959d5a95c, and suggested verifying the LLM connection. This matches recorded connection-error text; it does not establish a root cause or perform the suggested check.

Disconnected the provider: no Run agent with logs action was available. Reconnected by dragging handles: execution action returned. Reload preserved the two-node graph, one context wire, and analyst output. Fixed wire-label pointer interception discovered during this test. Final frontend build passed. Graph was left connected, with the verified output available for inspection.
