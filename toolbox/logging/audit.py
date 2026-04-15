# toolbox/logging/audit.py

from toolbox.logging.app_logger import get_logger


def audit_event(
    action: str,
    actor_id=None,
    actor_role: str | None = None,
    target: str | None = None,
    target_id=None,
    metadata: dict | None = None,
) -> None:
    logger = get_logger("audit")
    logger.info(
        "AUDIT action={action} actor_id={actor_id} actor_role={actor_role} "
        "target={target} target_id={target_id} metadata={metadata}",
        action=action,
        actor_id=actor_id,
        actor_role=actor_role,
        target=target,
        target_id=target_id,
        metadata=metadata or {},
    )