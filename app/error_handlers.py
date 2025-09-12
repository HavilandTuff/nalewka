from flask import jsonify

from app.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    InternalServerErrorException,
    NalewkaException,
    NotFoundException,
    ValidationException,
)


def register_error_handlers(app) -> None:
    """Register centralized error handlers for the application."""

    @app.errorhandler(NalewkaException)
    def handle_nalewka_exception(error: NalewkaException):
        """Handle custom Nalewka exceptions."""
        response = {
            "error": error.message,
            "status_code": error.status_code,
        }

        if error.details:
            response["details"] = error.details

        return jsonify(response), error.status_code

    @app.errorhandler(ValidationException)
    def handle_validation_exception(error: ValidationException):
        """Handle validation exceptions."""
        response = {
            "error": error.message,
            "status_code": error.status_code,
        }

        if error.details:
            response["details"] = error.details

        return jsonify(response), error.status_code

    @app.errorhandler(AuthenticationException)
    def handle_authentication_exception(error: AuthenticationException):
        """Handle authentication exceptions."""
        response = {
            "error": error.message,
            "status_code": error.status_code,
        }

        if error.details:
            response["details"] = error.details

        return jsonify(response), error.status_code

    @app.errorhandler(AuthorizationException)
    def handle_authorization_exception(error: AuthorizationException):
        """Handle authorization exceptions."""
        response = {
            "error": error.message,
            "status_code": error.status_code,
        }

        if error.details:
            response["details"] = error.details

        return jsonify(response), error.status_code

    @app.errorhandler(NotFoundException)
    def handle_not_found_exception(error: NotFoundException):
        """Handle not found exceptions."""
        response = {
            "error": error.message,
            "status_code": error.status_code,
        }

        if error.details:
            response["details"] = error.details

        return jsonify(response), error.status_code

    @app.errorhandler(ConflictException)
    def handle_conflict_exception(error: ConflictException):
        """Handle conflict exceptions."""
        response = {
            "error": error.message,
            "status_code": error.status_code,
        }

        if error.details:
            response["details"] = error.details

        return jsonify(response), error.status_code

    @app.errorhandler(InternalServerErrorException)
    def handle_internal_server_error_exception(error: InternalServerErrorException):
        """Handle internal server error exceptions."""
        response = {
            "error": error.message,
            "status_code": error.status_code,
        }

        if error.details:
            response["details"] = error.details

        return jsonify(response), error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad request errors."""
        return (
            jsonify(
                {"error": "Bad request", "status_code": 400, "details": str(error)}
            ),
            400,
        )

    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle unauthorized errors."""
        return (
            jsonify(
                {"error": "Unauthorized", "status_code": 401, "details": str(error)}
            ),
            401,
        )

    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle forbidden errors."""
        return (
            jsonify({"error": "Forbidden", "status_code": 403, "details": str(error)}),
            403,
        )

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle not found errors."""
        return (
            jsonify(
                {
                    "error": "Resource not found",
                    "status_code": 404,
                    "details": str(error),
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle method not allowed errors."""
        return (
            jsonify(
                {
                    "error": "Method not allowed",
                    "status_code": 405,
                    "details": str(error),
                }
            ),
            405,
        )

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Handle internal server errors."""
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "status_code": 500,
                    "details": (
                        str(error)
                        if app.config.get("DEBUG")
                        else "An unexpected error occurred"
                    ),
                }
            ),
            500,
        )
