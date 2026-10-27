"""Signal Deduplication & Integrity State Synchronization Utility."""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import IntegritySignal, StudentEnrolment, utc_now
from app.logging_config import logger


async def deduplicate_existing_signals(session: AsyncSession) -> int:
    """Safely cleans up any pre-existing duplicate active signals and syncs student integrity status.
    Keeps valid human reviewer resolutions and the earliest active finding; deletes redundant duplicates.
    """
    stmt = (
        select(IntegritySignal.student_id, IntegritySignal.rule_code)
        .group_by(IntegritySignal.student_id, IntegritySignal.rule_code)
        .having(func.count(IntegritySignal.id) > 1)
    )
    res = await session.execute(stmt)
    duplicate_groups = res.all()

    if not duplicate_groups:
        return 0

    deleted_count = 0
    now = utc_now()

    for student_id, rule_code in duplicate_groups:
        sig_stmt = (
            select(IntegritySignal)
            .where(
                IntegritySignal.student_id == student_id,
                IntegritySignal.rule_code == rule_code,
            )
            .order_by(IntegritySignal.created_at.asc())
        )
        sig_res = await session.execute(sig_stmt)
        sigs = sig_res.scalars().all()

        resolved = [s for s in sigs if s.review_status != "PENDING"]
        pending = [s for s in sigs if s.review_status == "PENDING"]

        if resolved:
            # Retain the most complete/recent reviewer decision
            best_resolved = resolved[-1]
            for r in resolved[:-1]:
                await session.delete(r)
                deleted_count += 1
            # Re-upload pending signals created after resolution are redundant duplicates
            for p in pending:
                await session.delete(p)
                deleted_count += 1
        else:
            # All are pending; keep earliest original finding and drop subsequent duplicates
            for p in pending[1:]:
                await session.delete(p)
                deleted_count += 1

    await session.flush()

    # Re-synchronize student integrity statuses for affected students
    affected_student_ids = {s_id for s_id, _ in duplicate_groups}
    for student_id in affected_student_ids:
        rem_stmt = select(IntegritySignal).where(IntegritySignal.student_id == student_id)
        rem_res = await session.execute(rem_stmt)
        remaining_sigs = rem_res.scalars().all()

        st_stmt = select(StudentEnrolment).where(StudentEnrolment.id == student_id)
        st_res = await session.execute(st_stmt)
        student = st_res.scalar_one_or_none()
        if student:
            has_active = any(s.review_status == "PENDING" for s in remaining_sigs)
            has_resolved = any(s.review_status != "PENDING" for s in remaining_sigs)
            if has_active:
                student.integrity_status = "FLAGGED_FOR_REVIEW"
            elif has_resolved:
                student.integrity_status = "RESOLVED"
            else:
                student.integrity_status = "CLEARED"
            student.updated_at = now

    await session.commit()
    logger.info(f"Signal deduplication completed: removed {deleted_count} duplicate signals across {len(duplicate_groups)} groups.")
    return deleted_count
