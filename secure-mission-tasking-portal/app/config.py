"""Centralized configuration (env-driven)."""

import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-jwt-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = 15 * 60
    JWT_REFRESH_TOKEN_EXPIRES = 7 * 24 * 60 * 60

    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200 per day;50 per hour")
    RATELIMIT_HEADERS_ENABLED = True

    SECURE_HEADERS = os.getenv("SECURE_HEADERS", "1") == "1"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
