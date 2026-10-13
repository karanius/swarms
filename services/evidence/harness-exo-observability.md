# Harness → EXO observability verification

Date: October 13, 2026. Harness d743267388. Runtime http://127.0.0.1:3080, EXO http://127.0.0.1:52416/v1.

- Harness Web started through its supported dsh launcher with isolated home and explicit OpenAI-completions provider exo-local.
- Browser selector displayed Llama 3.2 3B · EXO.
- First turn: requested an exact sentinel response with no tools. Request completed, but the model emitted an unfinished tool-like JSON string as text. No actual tool execution was observed. Agent instruction following is not established.
- First turn: Session Log showed request/context provider exo-local, model mlx-community/Llama-3.2-3B-Instruct-4bit, contextWindow 131072. Usage showed inputTokens 11658, outputTokens 31, totalTokens 11694, cacheReadTokens 5. UI reported completed in 9 seconds, one turn/one step and 64 tokens/sec. These are reported measurements, not an independent benchmark.
- Log recorded turn/start, step/start, system/user messages, request header/context, assistant stream, usage, finish, step/end and turn/end. Session records remained visible after page reload.
- Second turn: “What is 2 + 2? Answer in one sentence. Do not use tools.” Response: “The answer is 4.”
- NodeJS Inspector Network displayed three captured completions requests (including title generation), all HTTP 200. Selected second-turn request: POST http://127.0.0.1:52416/v1/chat/completions, 200 OK, 444 ms displayed duration.
- Evidence: harness-exo-session-log.png and harness-exo-network.png.

Limits: Tool execution and multi-agent coordination were not tested. Canvas execution is not wired. External OTel delivery is disabled and untested. Experimental DevTools prints unsupported CDP-method console errors; the tested Session Log and Network functions still operated.
