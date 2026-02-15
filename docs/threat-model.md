# Threat Model

## Primary risks

- Malicious generated Python code
- Container breakout attempts
- DoS from long or frequent renders
- Unsafe imports/calls in scripts

## Mitigations implemented

- AST validation denylist
- Docker sandbox execution for render mode
- Network disabled for sandbox container
- CPU/memory/pids/time limits
- Rate limiting middleware on API

## Remaining hardening

- Tight seccomp profile
- Non-root fs mount hardening verification
- Per-tenant auth and rate policy
