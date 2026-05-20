# Fleet API Reference: Robot State Endpoints

The Fleet API exposes robot state via REST endpoints under `/api/v2/robots`. All endpoints require an OAuth bearer token with the `robots:read` or `robots:write` scope as appropriate.

## GET /api/v2/robots

Returns a paginated list of robots visible to the authenticated user. Visibility is scoped to the user's organization and assigned facilities.

**Query parameters:**

- `facility_id` (optional): filter to a single facility
- `status` (optional): one of `idle`, `working`, `charging`, `offline`, `error`
- `limit` (default 50, max 200): page size
- `cursor` (optional): opaque pagination cursor from a previous response

**Response:**

```json
{
  "robots": [
    {
      "robot_id": "wx7-r-00482",
      "facility_id": "fac-reno-01",
      "status": "working",
      "battery_pct": 67,
      "current_task_id": "task-9c4d2a",
      "firmware_version": "3.7.3"
    }
  ],
  "next_cursor": "eyJvZmZzZXQiOjUwfQ=="
}
```

## GET /api/v2/robots/{robot_id}

Returns detailed state for a single robot, including the last 100 telemetry samples.

## POST /api/v2/robots/{robot_id}/commands

Issues a command to a specific robot. Requires the `robots:write` scope. Supported commands:

- `pause`: stop current task and hold position
- `resume`: continue paused task
- `return_to_charger`: abandon current task and navigate to nearest charging station
- `emergency_stop`: immediate halt; requires manual reset before resuming

## Rate Limits

API consumers are limited to 600 requests per minute per token, with burst capacity of 100 requests per second. Rate limit headers are returned with every response. Exceeding the limit returns HTTP 429 with a `Retry-After` header.
