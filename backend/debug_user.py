"""
Debug script to check the User model and schemas
"""
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserDetailResponse

def debug_users():
    """Check the users in the database and their role field"""
    db = next(get_db())
    users = db.query(User).all()
    
    print("\nRaw Users from Database:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}, Type: {type(user.role)}")
    
    # Test serialization of the first user
    admin_user = db.query(User).filter(User.username == "admin").first()
    if admin_user:
        print("\nAdmin User Details:")
        print(f"ID: {admin_user.id}")
        print(f"Username: {admin_user.username}")
        print(f"Role: {admin_user.role}")
        print(f"Role type: {type(admin_user.role)}")
        
        # Convert to Pydantic model
        user_response = UserDetailResponse.model_validate(admin_user)
        user_dict = user_response.model_dump()
        
        print("\nSerialized User (UserDetailResponse):")
        for key, value in user_dict.items():
            if key != "students":  # Skip complex nested data
                print(f"{key}: {value} (type: {type(value)})")
        
        print("\nRole specifically:", user_dict.get("role"))
    else:
        print("No admin user found!")

if __name__ == "__main__":
    debug_users()