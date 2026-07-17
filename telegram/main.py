"""Telegram bot entrypoint for Hikma."""

from __future__ import annotations

import logging
import logging.config
import os
from typing import Final

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ApplicationBuilder

from src.handlers import build_handlers
from src.services.client import KatherApiClient

TOKEN_ENV_VAR: Final[str] = "TELEGRAM_BOT_TOKEN"
LOG_LEVEL_ENV_VAR: Final[str] = "LOG_LEVEL"
DEFAULT_LOG_LEVEL: Final[str] = "INFO"


def configure_logging() -> None:
    """Configure a consistent structured logging setup for the bot."""

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": os.getenv(LOG_LEVEL_ENV_VAR, DEFAULT_LOG_LEVEL).upper(),
            },
            "loggers": {
                "httpx": {"level": "WARNING"},
                "telegram": {"level": "WARNING"},
                "telegram.ext": {"level": "INFO"},
            },
        }
    )


async def health_check(application: Application) -> None:
    """Verify Telegram credentials and log the resolved bot identity."""

    logger = logging.getLogger(__name__)
    bot_me = await application.bot.get_me()
    logger.info(
        "Telegram bot authenticated successfully as @%s (%s)",
        bot_me.username,
        bot_me.id,
    )


async def shutdown_client(application: Application) -> None:
    """Gracefully close shared resources on application shutdown."""

    logger = logging.getLogger(__name__)
    client = application.bot_data.get("kather_client")

    if client is None:
        logger.info("Shutdown requested without a shared API client.")
        return

    if isinstance(client, KatherApiClient):
        logger.info("Closing Kather API client.")
        await client.__aexit__(None, None, None)
        application.bot_data.pop("kather_client", None)
        return

    logger.warning("Unexpected client type found in bot_data during shutdown: %s", type(client).__name__)


def build_application(token: str) -> Application:
    """Build and configure the Telegram application."""

    client = KatherApiClient()
    application = ApplicationBuilder().token(token).post_init(health_check).post_shutdown(shutdown_client).build()
    application.bot_data["kather_client"] = client

    for handler in build_handlers(client):
        application.add_handler(handler)

    return application


def main() -> None:
    """Load configuration, bootstrap logging, and start polling."""

    load_dotenv()
    configure_logging()

    token = os.getenv(TOKEN_ENV_VAR)
    if not token:
        raise RuntimeError(f"Missing required environment variable: {TOKEN_ENV_VAR}")

    logger = logging.getLogger(__name__)
    logger.info("Starting Hikma Telegram bot.")

    application = build_application(token)
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        close_loop=True,
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
