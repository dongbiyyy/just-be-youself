from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services import excel_io

router = APIRouter(prefix="/imports", tags=["imports"], dependencies=[Depends(get_current_user)])


SUPPORTED = {
    "companies": excel_io.import_companies,
    "persons": excel_io.import_persons,
    "positions": excel_io.import_positions,
    "shareholdings": excel_io.import_shareholdings,
}


@router.get("/templates/{kind}")
def download_template(kind: str):
    if kind not in excel_io.TEMPLATES:
        raise HTTPException(status_code=404, detail="未知模板类型")
    data = excel_io.build_template(kind)
    headers = {"Content-Disposition": f"attachment; filename={kind}_template.xlsx"}
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.post("/{kind}")
async def upload_import(kind: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if kind not in SUPPORTED:
        raise HTTPException(status_code=404, detail="未知导入类型")
    content = await file.read()
    try:
        result = SUPPORTED[kind](db, content)
    except Exception as e:  # pragma: no cover - surface parsing errors clearly
        raise HTTPException(status_code=400, detail=f"导入失败: {e}")
    return {"kind": kind, **result}
