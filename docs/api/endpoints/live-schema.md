# Live Schema API

This endpoint retrieves live/current schema data for a specific version.

## Endpoint

```
GET /live/schema/{version}
```

## Parameters

| Parameter | Type   | Description                    | Required |
|-----------|--------|--------------------------------|----------|
| version   | string | Version identifier of the schema| Yes      |

## Response Format

The response is a JSON object containing the current schema data including:
- Node values
- Link values
- Real-time relationships between entities
- Current inventory levels
- Active facilities and warehouses

## Example Usage

```python
import requests

version = "sample_version"
get_live_data = f"/live/schema/{version}"

response = requests.get(get_live_data)
live_data = response.json()
```

## Example Response

```json
{
    "directed": true,
    "multigraph": false,
    "graph": {},
    "node_types": {
        "BUSINESS_GROUP": [...],
        "PRODUCT_FAMILY": [...],
        "PRODUCT_OFFERING": [...],
        "WAREHOUSE": [...],
        "FACILITY": [...],
        "PARTS": [...],
        "SUPPLIERS": [...]
    },
    "relationship_types": {
        "BUSINESS_GROUPToPRODUCT_FAMILY" : [...],
        "PRODUCT_FAMILYToPRODUCT_OFFERING": [...],
        "SUPPLIERSToWAREHOUSE": [...],
        "WAREHOUSEToPARTS": [...],
        "WAREHOUSEToPRODUCT_OFFERING": [...],
        "FACILITYToPARTS": [...],
        "FACILITYToPRODUCT_OFFERING": [...],
        "PARTSToFACILITY": [...]
    },
    "node_values": {
        "BUSINESS_GROUP": [...],
        "PRODUCT_FAMILY": [...],
        "PRODUCT_OFFERING": [...],
        "WAREHOUSE": [...],
        "FACILITY": [...],
        "PARTS": [...],
        "SUPPLIERS": [...]
    },
    "relationship_values": {
        "BUSINESS_GROUPToPRODUCT_FAMILY": [...],
        "PRODUCT_FAMILYToPRODUCT_OFFERING": [...],
        "SUPPLIERSToWAREHOUSE": [...],
        "WAREHOUSEToPARTS": [...],
        "WAREHOUSEToPRODUCT_OFFERING": [...],
        "FACILITYToPARTS": [...],
        "FACILITYToPRODUCT_OFFERING": [...],
        "PARTSToFACILITY": [...]
    }
}
```

## Notes
- This endpoint provides real-time supply chain network data
- Used for monitoring current inventory levels and facility status
- Data structure is similar to archived schema but reflects current state
