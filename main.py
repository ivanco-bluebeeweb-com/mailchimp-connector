"""Entrypoint for Mailchimp Connector validation and deployment."""
import os
import sys
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
for name in ("app", "schemas", "mailchimp_client", "handlers_connection", "handlers_entities", "handlers_reports", "panels", "panels_settings"):
    sys.modules.pop(name, None)
from app import ext, chat  # noqa: E402,F401
import handlers_connection  # noqa: E402,F401
import handlers_entities  # noqa: E402,F401
import handlers_reports  # noqa: E402,F401
import panels  # noqa: E402,F401
import panels_settings  # noqa: E402,F401
