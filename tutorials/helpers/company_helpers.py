import logging
from django.utils.dateparse import parse_date

logger = logging.getLogger(__name__)

def validate_required_fields(data, required_fields):
    for field in required_fields:
        if not data.get(field):
            error_msg = f"Field '{field}' is required but missing or empty."
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug(f"Field '{field}' value: {data.get(field)}")

def parse_reviews(reviews):
    try:
        return float(reviews) if reviews else None
    except ValueError:
        logger.warning("Failed to convert company_reviews to float. Setting reviews to None.")
        return None

def parse_deadline(deadline_str):
    if not deadline_str:
        raise ValueError("Application deadline is required.")
    deadline = parse_date(deadline_str)
    if not deadline:
        raise ValueError(f"Invalid date format for application_deadline: {deadline_str}. Expected YYYY-MM-DD.")
    return deadline