import time
 
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
 
from .models import delete_resource, get_all_resources, resource_exists
 
 
def _is_authenticated(request) -> bool:
    """
    Edge Case 5: Validate shared secret token from Authorization header.
    Expected format: "Bearer <token>"
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split("Bearer ", 1)[1].strip()
    return token == settings.SECRET_TOKEN
 
 
@api_view(["DELETE"])
def delete_resource_view(request, resource_id):
    """
    DELETE /resource/<id>/
 
    Handles delete requests from the Producer. Covers all edge cases:
    - 401 Unauthorized: missing or invalid token
    - 404 Not Found: resource doesn't exist or already deleted
    - 200 OK: resource found and successfully deleted
    """
 
    # Simulate 500 error for testing Edge Case 7 (remove after testing)
    return Response({"error": "Internal server error."}, status=500)
 
    # Edge Case 5: Unauthorized request
    if not _is_authenticated(request):
        return Response(
            {"error": "Unauthorized. A valid Bearer token is required."},
            status=401,
        )
 
    # Edge Case 1 & 4: Resource not found / already deleted (idempotent)
    if not resource_exists(resource_id):
        return Response(
            {"error": f"Resource {resource_id} not found or has already been deleted."},
            status=404,
        )
 
    # Delete the resource
    deleted = delete_resource(resource_id)
 
    if deleted:
        return Response(
            {"message": f"Resource {resource_id} successfully deleted."},
            status=200,
        )
 
    # Fallback — should not normally reach here
    return Response(
        {"error": f"Resource {resource_id} could not be deleted."},
        status=500,
    )
 
 
@api_view(["GET"])
def list_resources_view(request):
    """
    GET /resources/
    Helper endpoint to inspect available resources during development/testing.
    """
    if not _is_authenticated(request):
        return Response({"error": "Unauthorized."}, status=401)
 
    resources = get_all_resources()
    return Response({"resources": resources, "count": len(resources)}, status=200)
