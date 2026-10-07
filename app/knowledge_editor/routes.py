from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.service import User, get_current_user, get_db
from app.moderation.service import is_moderator
from app.security.rate_limit import rate_limit
from . import public_export, service
from .schemas import CorrectionRequest, DraftCreate, DraftReplace, PublishRequest, ReviewRequest, VersionRequest

router = APIRouter(prefix="/knowledge-editor", tags=["knowledge-editor"], dependencies=[
    Depends(rate_limit(120, 60, prefix="knowledge-editor", include_path=True))])


def private_response(response: Response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"


@router.get("/capabilities")
def capabilities(response: Response, user: User = Depends(get_current_user)):
    private_response(response)
    return {"can_review": is_moderator(user), "schema_version": service.SCHEMA_VERSION,
        "publication_scope": "editorial_candidate_not_globe_corpus"}


@router.get("/drafts")
def list_drafts(response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    rows = db.query(service.EditorDraft).filter_by(owner_id=user.id).order_by(service.EditorDraft.updated_at.desc()).all()
    return [service.serialize_draft(db, row, user) for row in rows]


@router.get("/review-queue")
def review_queue(response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    service.moderator(user)
    rows = db.query(service.EditorDraft).filter_by(state="submitted").order_by(service.EditorDraft.updated_at).all()
    return [service.serialize_draft(db, row, user) for row in rows]


@router.post("/drafts", status_code=201)
def create(payload: DraftCreate, response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    item = service.create_draft(db, user, payload.content)
    return service.serialize_draft(db, item, user)


@router.get("/drafts/{draft_id}")
def read(draft_id: str, response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    return service.serialize_draft(db, service.private_draft(db, user, draft_id), user)


@router.put("/drafts/{draft_id}")
def replace(draft_id: str, payload: DraftReplace, response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    item = service.private_draft(db, user, draft_id, author_only=True)
    return service.serialize_draft(db, service.replace_draft(db, user, item, payload.expected_version, payload.content), user)


@router.post("/drafts/{draft_id}/submit")
def submit(draft_id: str, payload: VersionRequest, response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    item = service.private_draft(db, user, draft_id, author_only=True)
    return service.serialize_draft(db, service.submit_draft(db, user, item, payload.expected_version), user)


@router.post("/drafts/{draft_id}/review")
def review(draft_id: str, payload: ReviewRequest, response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    service.moderator(user)
    item = service.private_draft(db, user, draft_id)
    return service.serialize_draft(db, service.review_draft(db, user, item, payload), user)


@router.post("/drafts/{draft_id}/publish")
def publish(draft_id: str, payload: PublishRequest, response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    service.moderator(user)
    item = service.private_draft(db, user, draft_id)
    return service.serialize_draft(db, service.publish_revision(db, user, item, payload), user)


@router.post("/revisions/{revision_id}/corrections", status_code=201)
def correction(revision_id: str, payload: CorrectionRequest, response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    return service.serialize_draft(db, service.create_correction(db, user, revision_id, payload), user)


@router.get("/drafts/{draft_id}/history")
def history(draft_id: str, response: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    private_response(response)
    item = service.private_draft(db, user, draft_id)
    return service.history(db, user, item)


@router.get("/public/objects")
def published_objects(response: Response, db: Session = Depends(get_db)):
    private_response(response)
    rows = db.query(service.EditorObject).filter(service.EditorObject.published_snapshot_id.isnot(None)).order_by(service.EditorObject.created_at.desc()).all()
    return [service.public_object(db, row.id) for row in rows]


@router.get("/public/objects/{entity_id}")
def published_object(entity_id: str, response: Response, db: Session = Depends(get_db)):
    private_response(response)
    return service.public_object(db, entity_id)


@router.get("/public/snapshots/{snapshot_id}")
def published_snapshot(snapshot_id: str, response: Response, db: Session = Depends(get_db)):
    private_response(response)
    return service.public_snapshot(db, snapshot_id)


@router.get("/public/objects/{entity_id}/history")
def published_history(entity_id: str, response: Response, db: Session = Depends(get_db)):
    private_response(response)
    return service.public_history(db, entity_id)


@router.get("/public/objects/{entity_id}/export")
def export_public_history(entity_id: str, db: Session = Depends(get_db)):
    try:
        data = public_export.public_export(db, entity_id)
        filename_id = str(UUID(entity_id))
    except service.KnowledgeEditorError:
        raise
    except public_export.PublicExportTooLarge:
        service.fail("export_too_large", 413)
    except Exception:
        # Never send stored content or schema/database diagnostics to readers.
        service.fail("public_export_unavailable", 500)
    # Successful schema validation guarantees a system UUID, never a title/path.
    return Response(content=data, media_type="application/json; charset=utf-8", headers={
        "Content-Disposition": f'attachment; filename="artemis-editor-{filename_id}-public.json"',
        "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


async def knowledge_editor_error_handler(request: Request, exc: service.KnowledgeEditorError):
    return JSONResponse(status_code=exc.status_code,
        content={"error": exc.detail["code"], "detail": exc.detail,
            "request_id": getattr(request.state, "request_id", None)},
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})
