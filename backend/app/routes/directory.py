"""GET /directory — public contact search."""
from fastapi import APIRouter, Query
from app.db import fetch_all

router = APIRouter()


@router.get("")
def search(
    category: str = Query(None),
    search: str = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, le=100),
):
    clauses, params = ["1=1"], []
    if category:
        clauses.append("category = %s")
        params.append(category)
    if search:
        clauses.append("(name ILIKE %s OR location ILIKE %s OR genre ILIKE %s)")
        params.extend([f"%{search}%"] * 3)
    where = " AND ".join(clauses)
    contacts = fetch_all(f"SELECT * FROM contacts WHERE {where} ORDER BY name LIMIT %s OFFSET %s", params + [per_page, (page - 1) * per_page])
    return {"contacts": contacts, "page": page}
