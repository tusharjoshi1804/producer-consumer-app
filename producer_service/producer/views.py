import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response


def _is_valid_id(resource_id: str) -> bool:
    """Validate that the ID is a non-empty integer string."""
    try:
        val = int(resource_id)
        return val > 0
    except (ValueError, TypeError):
        return False


@api_view(["POST"])
def send_delete(request, resource_id):
    """
    POST /send-delete/<id>/

    Validates the resource ID, then forwards a DELETE request to the
    Consumer service. Handles all edge cases gracefully.
    """

    # Edge Case 3: Invalid ID format
    if not _is_valid_id(str(resource_id)):
        return Response(
            {"error": f"Invalid resource ID '{resource_id}'. Must be a positive integer."},
            status=400,
        )

    consumer_url = f"{settings.CONSUMER_URL}/resource/{resource_id}/"
    headers = {"Authorization": f"Bearer {settings.SECRET_TOKEN}"}

    try:
        response = requests.delete(
            consumer_url,
            headers=headers,
            timeout=settings.REQUEST_TIMEOUT,  # Edge Case 6: timeout
        )

        # Edge Case 7: Consumer returns unexpected 5xx error
        if response.status_code >= 500:
            return Response(
                {
                    "error": "Consumer service encountered an internal error.",
                    "detail": response.text,
                },
                status=502,
            )

        # Edge Case 1 & 4: Resource not found or already deleted — forward 404
        if response.status_code == 404:
            return Response(
                {"error": f"Resource {resource_id} not found or already deleted."},
                status=404,
            )

        # Edge Case 5: Unauthorized — forward 401
        if response.status_code == 401:
            return Response(
                {"error": "Unauthorized. Invalid or missing authentication token."},
                status=401,
            )

        # Success
        if response.status_code == 200:
            return Response(
                {"message": f"Resource {resource_id} successfully deleted."},
                status=200,
            )

        # Any other unexpected status
        return Response(
            {"error": f"Unexpected response from consumer: {response.status_code}"},
            status=502,
        )

    # Edge Case 2: Consumer service is down
    except requests.exceptions.ConnectionError:
        return Response(
            {"error": "Consumer service is unreachable. Please try again later."},
            status=503,
        )

    # Edge Case 6: Request timed out
    except requests.exceptions.Timeout:
        return Response(
            {"error": "Request to Consumer service timed out."},
            status=504,
        )

    except requests.exceptions.RequestException as e:
        return Response(
            {"error": f"Unexpected error communicating with Consumer: {str(e)}"},
            status=502,
        )
