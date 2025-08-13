from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.comment import Comment
from app.db.models.course import Course
from app.schemas.comment import CommentCreate, CommentOut
from app.api.deps import get_current_user, get_db

router = APIRouter()

@router.post("/courses/{course_id}/comments/", response_model=CommentOut)
def add_comment(course_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db_comment = Comment(content=comment.content, user_id=current_user.id, course_id=course_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/courses/{course_id}/comments/", response_model=list[CommentOut])
def list_comments(course_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.course_id == course_id).all()

@router.put("/comments/{comment_id}", response_model=CommentOut)
def edit_comment(
    comment_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to edit this comment")
    db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/comments/{comment_id}", response_model=dict)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this comment")
    db.delete(db_comment)
    db.commit()
    return {"detail": "Comment deleted successfully"}
