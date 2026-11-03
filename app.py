"""WSGI entry point for deployments expecting an ``app`` module."""

from stringerai import app


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)