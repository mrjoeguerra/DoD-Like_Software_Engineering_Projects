from __future__ import annotations

from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from ..extensions import db, limiter
from ..models import Task
from ..schemas import TaskCreateSchema, TaskUpdateSchema
from ..security import require_roles
from ..audit import write_audit

bp = Blueprint("tasks", __name__)

create_schema = TaskCreateSchema()
update_schema = TaskUpdateSchema()


@bp.get("/tasks")
@jwt_required()
@limiter.limit("30 per minute")
def list_tasks():
    tasks = Task.query.order_by(Task.updated_at.desc()).all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "priority": t.priority,
        "status": t.status,
        "assigned_to": t.assigned_to,
        "created_by": t.created_by,
        "created_at": t.created_at.isoformat() + "Z",
        "updated_at": t.updated_at.isoformat() + "Z",
    } for t in tasks])


@bp.post("/tasks")
@require_roles(["admin"])
@limiter.limit("20 per minute")
def create_task():
    payload = request.get_json(silent=True) or {}
    data = create_schema.load(payload)

    actor = get_jwt_identity()
    task = Task(
        title=data["title"],
        description=data.get("description"),
        priority=data.get("priority", "medium"),
        status="open",
        assigned_to=data.get("assigned_to"),
        created_by=actor,
        updated_at=datetime.utcnow(),
    )
    db.session.add(task)
    db.session.commit()

    write_audit("task.created", {"task_id": task.id, "assigned_to": task.assigned_to, "priority": task.priority})
    return jsonify({"id": task.id}), 201


@bp.patch("/tasks/<int:task_id>")
@require_roles(["admin", "operator"])
@limiter.limit("30 per minute")
def update_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    payload = request.get_json(silent=True) or {}
    data = update_schema.load(payload)

    role = get_jwt().get("role")
    if role == "operator" and task.assigned_to not in (None, get_jwt_identity()):
        return jsonify({"error": "forbidden", "message": "Operators may only modify assigned tasks"}), 403

    for field in ["title", "description", "priority", "status", "assigned_to"]:
        if field in data:
            setattr(task, field, data[field])

    task.updated_at = datetime.utcnow()
    db.session.commit()

    write_audit("task.updated", {"task_id": task.id, "changed_fields": list(data.keys())})
    return jsonify({"ok": True})


@bp.delete("/tasks/<int:task_id>")
@require_roles(["admin"])
@limiter.limit("10 per minute")
def delete_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()

    write_audit("task.deleted", {"task_id": task_id})
    return jsonify({"ok": True})
