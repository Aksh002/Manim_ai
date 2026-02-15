# API Contracts

## POST /generate
Input: topic, duration_seconds, style, level, additional_instructions
Output: code, model, warnings

## POST /render
Input: code, quality, retry_on_error
Output: job_id, status

## POST /regenerate
Input: code, instruction
Output: revised code

## GET /status/{job_id}
Output: job lifecycle status and progress

## GET /video/{job_id}
Returns rendered MP4 stream
