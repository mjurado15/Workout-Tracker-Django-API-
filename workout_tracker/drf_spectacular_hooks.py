from drf_spectacular.utils import OpenApiParameter, extend_schema_view, extend_schema
import uuid


def preprocess_schema(endpoints, **kwargs):
    model_methods = {
        "POST": "create",
        "GET": "list",
        "GET_pk": "retrieve",
        "PATCH": "partial_update",
        "PUT": "update",
        "DELETE": "destroy",
    }

    for path, path_regex, method, callback in endpoints:
        # Check if the route contains the 'workout_pk' parameter
        if "{workout_pk}" in path:
            http_method = "GET_pk" if (method == "GET" and "{pk}" in path) else method
            custom_method = model_methods[http_method]

            extend_schema_view(
                **{
                    custom_method: extend_schema(
                        parameters=[
                            OpenApiParameter(
                                name="workout_pk",
                                location=OpenApiParameter.PATH,
                                required=True,
                                type=uuid.UUID,
                            )
                        ]
                    )
                }
            )(callback.cls)

        # Check if the route contains the 'pk' parameter
        if "{pk}" in path:
            http_method = "GET_pk" if method == "GET" else method
            custom_method = model_methods[http_method]

            extend_schema_view(
                **{
                    custom_method: extend_schema(
                        parameters=[
                            OpenApiParameter(
                                name="id",
                                location=OpenApiParameter.PATH,
                                required=True,
                                type=uuid.UUID,
                            )
                        ]
                    )
                }
            )(callback.cls)

    return endpoints
