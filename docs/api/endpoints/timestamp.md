# Get Timestamp API

This endpoint retrieves all available timestamp information for a specific version of the supply chain schema.

## Endpoint

```
GET /archive/timestamp/{version}
```

## Parameters

| Parameter | Type   | Description                    | Required |
|-----------|--------|--------------------------------|----------|
| version   | string | Version identifier of the schema| Yes      |

## Response Format

The response is a JSON object containing timestamp information for the specified schema version.

## Example Usage

```python
import requests

version = "sample_version"
get_timestamp = f"/archive/timestamp/{version}"

response = requests.get(get_timestamp)
timestamp_data = response.json()
```

## Example Response

```json
[
    1,
    2,
    3,
    4,
    5,
    6
]
```

## Notes
- This endpoint is used to get the timestamp information for a specific schema version
- The timestamp information helps track when the schema was last updated
