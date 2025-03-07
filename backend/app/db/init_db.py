from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.models.quiz import Category, DifficultyLevel, Path

def init_db(db: Session) -> None:
    # Create admin user
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    # Create default difficulty levels
    levels = [("Easy", 1), ("Medium", 2), ("Hard", 3)]
    for level_name, value in levels:
        level = db.query(DifficultyLevel).filter(DifficultyLevel.name == level_name).first()
        if not level:
            level = DifficultyLevel(
                name=level_name,
                value=value
            )
            db.add(level)
    
    # Create default categories
    categories = ["Math", "Science", "History", "Geography", "Language"]
    for cat_name in categories:
        category = db.query(Category).filter(Category.name == cat_name).first()
        if not category:
            category = Category(
                name=cat_name,
                description=f"{cat_name} related questions",
                icon=f"{cat_name.lower()}-icon"
            )
            db.add(category)
    
    # Create default paths
    paths = ["Beginner", "Intermediate", "Advanced"]
    for path_name in paths:
        path = db.query(Path).filter(Path.name == path_name).first()
        if not path:
            path = Path(
                name=path_name,
                description=f"{path_name} learning path",
                required_points=0 if path_name == "Beginner" else 100 if path_name == "Intermediate" else 300,
                creator_id=admin.id
            )
            db.add(path)
    
    db.commit()
