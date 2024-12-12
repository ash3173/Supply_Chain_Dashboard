# Get Versions API

This endpoint retrieves available versions of the supply chain schema.

## Endpoint

```
GET /versions
```

## Parameters
No parameters required.

## Response Format

The response is a JSON array containing available version identifiers.

## Example Usage

```python
import requests

getVersions = "/versions"

response = requests.get(getVersions)
versions = response.json()
```

## Example Response

```json
[
    "sample_version_1",
    "sample_version_2",
    "sample_version_3"
]
```

## Notes
- This endpoint is used to get all available versions of the supply chain schema
- The version identifier is required for other API endpoints
