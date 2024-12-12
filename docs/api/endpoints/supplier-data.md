# Supplier Data API

This endpoint retrieves information about suppliers and their associated parts.

## Endpoint

```
GET /supplier-data
```

## Parameters
No parameters required.

## Response Format

The response is a JSON object mapping suppliers to their available parts.

## Example Usage

```python
import requests

response = requests.get("/supplier-data")
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
