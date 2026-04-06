"""
Simple in-memory resource store for demonstration purposes.
In production, replace with a proper database model.
"""

# Simulated resource store: {id: {"id": int, "name": str}}
_resources = {
    1: {"id": 1, "name": "Resource Alpha"},
    2: {"id": 2, "name": "Resource Beta"},
    3: {"id": 3, "name": "Resource Gamma"},
    42: {"id": 42, "name": "Resource Delta"},
    100: {"id": 100, "name": "Resource Epsilon"},
}


def resource_exists(resource_id: int) -> bool:
    return resource_id in _resources


def delete_resource(resource_id: int) -> bool:
    """
    Delete a resource by ID.
    Returns True if deleted, False if it didn't exist.
    Handles idempotency: deleting a non-existent resource returns False.
    """
    if resource_id in _resources:
        del _resources[resource_id]
        return True
    return False


def get_all_resources():
    return list(_resources.values())
