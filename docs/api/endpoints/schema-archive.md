# Schema Archive API

This endpoint retrieves archived schema data for a specific version at a specific timestamp.

## Endpoint

```
GET /archive/schema/{version}
```

## Parameters

| Parameter | Type   | Description                    | Required |
|-----------|--------|--------------------------------|----------|
| version   | string | Version identifier of the schema| Yes      |
| timestamp | int    | Timestamp of the schema        | Yes      |

## URL
```
/archive/schema/{version}/{timestamp}
```

## Response Format

The response is a JSON object containing the schema data including:
- Node values
- Link values
- Relationships between different entities

## Example Usage

```python
import requests

version = "sample_version"
timestamp = 1
getdata = f"/archive/schema/{version}/{timestamp}"

response = requests.get(getdata)
schema_data = response.json()
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
    "link_values": {
        "BUSINESS_GROUPToPRODUCT_FAMILY" : [...],
        "PRODUCT_FAMILYToPRODUCT_OFFERING": [...],
        "SUPPLIERSToWAREHOUSE": [...],
        "WAREHOUSEToPARTS": [...],
        "WAREHOUSEToPRODUCT_OFFERING": [...],
        "FACILITYToPARTS": [...],
        "FACILITYToPRODUCT_OFFERING": [...],
        "PARTSToFACILITY": [...]
    },
}
```

## Notes
- This endpoint is used to retrieve historical/archived data
- The schema includes complete supply chain network information
- Data includes all the entities and their relationships present in the supply chain network