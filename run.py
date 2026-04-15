from app.api import create_app


app = create_app()


if __name__ == "__main__":
    config = app.config["APP_SETTINGS"]
    app.run(host=config.host, port=config.port, debug=True)
