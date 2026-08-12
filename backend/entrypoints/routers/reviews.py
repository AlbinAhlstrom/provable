"""
Reviews & Code Approval API Router — Handles agent code review, diff viewing, code approval, merge, branch previews, and bug reporting.
"""

from fastapi import APIRouter, BackgroundTasks
from entrypoints.schemas import (
    ApprovePayload, ReportBugPayload, CheckoutPreviewPayload,
    RejectPayload, FeedbackPayload
)
from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services

router = APIRouter()

@router.get("/api/diff/{ticket_id}")
def get_diff(ticket_id: str):
    return services.get_diff(ticket_id)


@router.get("/api/diff-files/{ticket_id}")
def get_diff_files(ticket_id: str):
    return services.get_diff_files(ticket_id)


@router.get("/api/reviews")
def get_reviews():
    uow = SqliteUnitOfWork()
    return services.get_code_reviews(uow=uow)


@router.post("/api/approve-code")
def approve_code(payload: ApprovePayload):
    uow = SqliteUnitOfWork()
    services.approve_code(payload.id, uow=uow)
    return {"success": True, "message": "Code approved, moving to Test phase."}


@router.post("/api/reject-code")
def reject_code(payload: RejectPayload):
    uow = SqliteUnitOfWork()
    services.reject_code(payload.id, payload.feedback, uow=uow)
    return {"success": True, "message": "Code rejected, moving to In_Progress phase."}


@router.post("/api/submit-feedback")
def submit_feedback(payload: FeedbackPayload):
    uow = SqliteUnitOfWork()
    services.submit_review_feedback(payload.id, payload.feedback, uow=uow)
    return {"success": True, "message": "Feedback submitted successfully."}


@router.post("/api/merge-code")
def merge_code(payload: ApprovePayload, background_tasks: BackgroundTasks):
    uow = SqliteUnitOfWork()
    return services.merge_code(payload.id, uow=uow, background_tasks=background_tasks)


@router.post("/api/report-bug")
def report_bug(payload: ReportBugPayload, background_tasks: BackgroundTasks):
    uow = SqliteUnitOfWork()
    return services.report_bug(
        title=payload.title,
        parent_id=payload.parentId,
        steps=payload.steps,
        expected=payload.expected,
        actual=payload.actual,
        uow=uow,
        background_tasks=background_tasks
    )


@router.post("/api/checkout-preview")
def checkout_preview(payload: CheckoutPreviewPayload):
    return services.checkout_preview(payload.branch)
