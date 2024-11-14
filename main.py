import os

from aiohttp.web import run_app

from app.web import setup_app

if __name__ == "__main__":
    run_app(
        setup_app(
            config_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "config.yml"
            )
        )
    )
