# Supplier Data API

This endpoint retrieves information about suppliers and their associated parts.

## Endpoint

```
GET api/dicts/{version}/{type}/{timestamp}
```

## Parameters

| Parameter | Type   | Description                    | Required |
|-----------|--------|--------------------------------|----------|
| version   | string | Version identifier of the schema| Yes      |
| type      | string | Type of data (e.g., SUPPLIERS_PARTS) | Yes      |
| timestamp | int    | Timestamp of the schema        | Yes      |


## Response Format

The response is a JSON object mapping suppliers to their available parts.

## Example Usage

```python
import requests

version = "sample_version"
timestamp = 1
type = "SUPPLIERS_PARTS"
get_supplier_data = f"/api/dicts/{version}/{type}/{timestamp}"

response = requests.get(get_supplier_data)
supplier_data = response.json()
```

## Example Response

```json
{
    "supplier_id_1": [
        "part_id_1",
        "part_id_2",
        ...
    ],
    "supplier_id_2": [
        "part_id_3",
        "part_id_4",
        ...
    ]
}
```

## Notes
- The API provides real-time supplier and parts availability data
