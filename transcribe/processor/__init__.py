
import sentry_sdk
import transcribe.config as config


def sentry_report(e):
    if not config.DEVELOPMENT_MODE:
        sentry_sdk.capture_exception(e)
