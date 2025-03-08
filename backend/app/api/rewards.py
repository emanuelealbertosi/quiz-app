from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.core.auth import get_current_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.reward import Reward, RewardPurchase, student_reward_shop_association
from app.schemas.reward import (
    RewardCreate, RewardUpdate, Reward as RewardSchema, 
    StudentRewardAssignment, BulkRewardAssignment, 
    RewardPurchaseCreate, RewardPurchase as RewardPurchaseSchema,
    StudentShopReward, RewardPurchaseUpdate, ParentStudentShopReward
)

router = APIRouter()

# Admin endpoints for reward management
@router.post("/rewards/", response_model=RewardSchema, tags=["rewards"])
def create_reward(
    reward: RewardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new reward (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_reward = Reward(
        name=reward.name,
        description=reward.description,
        image_url=reward.image_url,
        point_cost=reward.point_cost,
        is_active=reward.is_active,
        creator_id=current_user.id
    )
    
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward

@router.get("/rewards/", response_model=List[RewardSchema], tags=["rewards"])
def get_rewards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of all rewards (Admin and Parent)"""
    is_admin = current_user.role == UserRole.ADMIN
    is_parent = current_user.role == UserRole.PARENT
    
    if not (is_admin or is_parent):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    rewards = db.query(Reward).offset(skip).limit(limit).all()
    return rewards

@router.get("/rewards/{reward_id}", response_model=RewardSchema, tags=["rewards"])
def get_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific reward by ID (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    return reward

@router.put("/rewards/{reward_id}", response_model=RewardSchema, tags=["rewards"])
def update_reward(
    reward_id: int,
    reward_update: RewardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a reward (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not db_reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    # Update fields if provided
    if reward_update.name is not None:
        db_reward.name = reward_update.name
    if reward_update.description is not None:
        db_reward.description = reward_update.description
    if reward_update.image_url is not None:
        db_reward.image_url = reward_update.image_url
    if reward_update.point_cost is not None:
        db_reward.point_cost = reward_update.point_cost
    if reward_update.is_active is not None:
        db_reward.is_active = reward_update.is_active
    
    db.commit()
    db.refresh(db_reward)
    return db_reward

@router.delete("/rewards/{reward_id}", tags=["rewards"])
def delete_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a reward (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not db_reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    db.delete(db_reward)
    db.commit()
    return {"detail": "Reward deleted successfully"}

# Assign rewards to student shops
@router.post("/rewards/assign/", tags=["rewards"])
def assign_reward_to_student_shop(
    assignment: StudentRewardAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign a reward to a student's shop (Admin or Parent only)"""
    # Verify permissions
    is_admin = current_user.role == UserRole.ADMIN
    is_parent = current_user.role == UserRole.PARENT
    
    if not (is_admin or is_parent):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # If parent, check if the student is their child
    if is_parent:
        student = db.query(User).filter(
            User.id == assignment.student_id,
            User.id.in_([s.id for s in current_user.students])
        ).first()
        if not student:
            raise HTTPException(status_code=403, detail="Not authorized to assign rewards to this student")
    else:
        student = db.query(User).filter(User.id == assignment.student_id).first()
        if not student or student.role != UserRole.STUDENT:
            raise HTTPException(status_code=404, detail="Student not found")
    
    # Verify reward exists
    reward = db.query(Reward).filter(Reward.id == assignment.reward_id).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    # Check if the student already has this reward in their shop
    association = db.query(student_reward_shop_association).filter(
        student_reward_shop_association.c.student_id == assignment.student_id,
        student_reward_shop_association.c.reward_id == assignment.reward_id
    ).first()
    
    if association:
        # Update the quantity
        db.execute(
            student_reward_shop_association.update().where(
                student_reward_shop_association.c.student_id == assignment.student_id,
                student_reward_shop_association.c.reward_id == assignment.reward_id
            ).values(quantity=student_reward_shop_association.c.quantity + assignment.quantity)
        )
    else:
        # Create a new association
        db.execute(
            student_reward_shop_association.insert().values(
                student_id=assignment.student_id,
                reward_id=assignment.reward_id,
                quantity=assignment.quantity
            )
        )
    
    db.commit()
    return {"detail": "Reward assigned to student shop successfully"}

@router.post("/rewards/assign/bulk/", tags=["rewards"])
def bulk_assign_reward(
    bulk_assignment: BulkRewardAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Bulk assign a reward to multiple students' shops (Admin or Parent only)"""
    # Verify permissions
    is_admin = current_user.role == UserRole.ADMIN
    is_parent = current_user.role == UserRole.PARENT
    
    if not (is_admin or is_parent):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Filter student IDs based on permissions
    authorized_student_ids = []
    if is_parent:
        parent_student_ids = [s.id for s in current_user.students]
        authorized_student_ids = [
            student_id for student_id in bulk_assignment.student_ids 
            if student_id in parent_student_ids
        ]
        if not authorized_student_ids:
            raise HTTPException(status_code=403, detail="Not authorized to assign rewards to any of these students")
    else:
        authorized_student_ids = bulk_assignment.student_ids
    
    # Verify reward exists
    reward = db.query(Reward).filter(Reward.id == bulk_assignment.reward_id).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    # Assign the reward to each authorized student
    for student_id in authorized_student_ids:
        # Verify student exists and is a student
        student = db.query(User).filter(
            User.id == student_id, 
            User.role == UserRole.STUDENT
        ).first()
        
        if not student:
            continue  # Skip if student doesn't exist or isn't a student
        
        # Check if the student already has this reward in their shop
        association = db.query(student_reward_shop_association).filter(
            student_reward_shop_association.c.student_id == student_id,
            student_reward_shop_association.c.reward_id == bulk_assignment.reward_id
        ).first()
        
        if association:
            # Update the quantity
            db.execute(
                student_reward_shop_association.update().where(
                    student_reward_shop_association.c.student_id == student_id,
                    student_reward_shop_association.c.reward_id == bulk_assignment.reward_id
                ).values(quantity=student_reward_shop_association.c.quantity + bulk_assignment.quantity)
            )
        else:
            # Create a new association
            db.execute(
                student_reward_shop_association.insert().values(
                    student_id=student_id,
                    reward_id=bulk_assignment.reward_id,
                    quantity=bulk_assignment.quantity
                )
            )
    
    db.commit()
    return {"detail": f"Reward assigned to {len(authorized_student_ids)} student shops successfully"}

@router.delete("/rewards/remove-from-shop/{student_id}/{reward_id}", tags=["rewards"])
def remove_reward_from_student_shop(
    student_id: int,
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a reward from a student's shop (Admin or Parent only)"""
    # Verify permissions
    is_admin = current_user.role == UserRole.ADMIN
    is_parent = current_user.role == UserRole.PARENT
    
    if not (is_admin or is_parent):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # If parent, check if the student is their child
    if is_parent and student_id not in [s.id for s in current_user.students]:
        raise HTTPException(status_code=403, detail="Not authorized to remove rewards from this student's shop")
    
    # Delete the association
    result = db.execute(
        student_reward_shop_association.delete().where(
            student_reward_shop_association.c.student_id == student_id,
            student_reward_shop_association.c.reward_id == reward_id
        )
    )
    
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Reward not found in student's shop")
    
    return {"detail": "Reward removed from student's shop successfully"}

# Student shop and purchase endpoints
@router.get("/student/shop/", response_model=List[StudentShopReward], tags=["rewards"])
def get_student_shop(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all rewards in the current student's shop"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Not authorized - only students can access their shop")
    
    # Get rewards from the student's shop with quantity
    shop_rewards = db.query(
        Reward, 
        student_reward_shop_association.c.quantity.label("quantity")
    ).join(
        student_reward_shop_association,
        Reward.id == student_reward_shop_association.c.reward_id
    ).filter(
        student_reward_shop_association.c.student_id == current_user.id,
        Reward.is_active == True
    ).all()
    
    # Convert to response schema
    result = []
    for reward, quantity in shop_rewards:
        reward_dict = {
            "id": reward.id,
            "name": reward.name,
            "description": reward.description,
            "image_url": reward.image_url,
            "point_cost": reward.point_cost,
            "is_active": reward.is_active,
            "creator_id": reward.creator_id,
            "created_at": reward.created_at,
            "updated_at": reward.updated_at,
            "quantity": quantity
        }
        result.append(reward_dict)
    
    return result

@router.post("/student/purchase/", response_model=RewardPurchaseSchema, tags=["rewards"])
def purchase_reward(
    purchase: RewardPurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Purchase a reward from the student's shop using points"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Not authorized - only students can purchase rewards")
    
    # Check if the reward is in the student's shop
    association = db.query(student_reward_shop_association).filter(
        student_reward_shop_association.c.student_id == current_user.id,
        student_reward_shop_association.c.reward_id == purchase.reward_id
    ).first()
    
    if not association:
        raise HTTPException(status_code=404, detail="Reward not found in your shop")
    
    # Get the reward with its current price
    reward = db.query(Reward).filter(
        Reward.id == purchase.reward_id,
        Reward.is_active == True
    ).first()
    
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not available")
    
    # Check if student has enough points
    if current_user.points < reward.point_cost:
        raise HTTPException(status_code=400, detail=f"Not enough points. You need {reward.point_cost} points but have {current_user.points}")
    
    # Create purchase transaction
    db_purchase = RewardPurchase(
        student_id=current_user.id,
        reward_id=reward.id,
        point_cost=reward.point_cost,
        is_delivered=False
    )
    
    # Deduct points from student
    current_user.points -= reward.point_cost
    
    # Reduce quantity in shop or remove if quantity becomes 0
    current_quantity = association.quantity
    if current_quantity <= 1:
        # Delete the association if quantity would become 0
        db.execute(
            student_reward_shop_association.delete().where(
                student_reward_shop_association.c.student_id == current_user.id,
                student_reward_shop_association.c.reward_id == reward.id
            )
        )
    else:
        # Decrease quantity by 1
        db.execute(
            student_reward_shop_association.update().where(
                student_reward_shop_association.c.student_id == current_user.id,
                student_reward_shop_association.c.reward_id == reward.id
            ).values(quantity=current_quantity - 1)
        )
    
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    return db_purchase

@router.get("/student/purchases/", response_model=List[RewardPurchaseSchema], tags=["rewards"])
def get_student_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all purchases made by the current student"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Not authorized - only students can view their purchases")
    
    purchases = db.query(RewardPurchase).filter(
        RewardPurchase.student_id == current_user.id
    ).order_by(RewardPurchase.created_at.desc()).all()
    
    return purchases

# Parent endpoint to view a child's shop
@router.get("/parent/student-shop/{student_id}", response_model=List[ParentStudentShopReward], tags=["rewards"])
def get_student_shop_for_parent(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all rewards in a student's shop (Parent only)"""
    is_admin = current_user.role == UserRole.ADMIN
    is_parent = current_user.role == UserRole.PARENT
    
    if not (is_admin or is_parent):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # If parent, check if the student is their child
    if is_parent and student_id not in [s.id for s in current_user.students]:
        raise HTTPException(status_code=403, detail="Not authorized to view this student's shop")
        
    # Get rewards from the student's shop with quantity
    rewards_query = db.query(
        Reward,
        student_reward_shop_association.c.quantity.label("quantity")
    ).join(
        student_reward_shop_association,
        Reward.id == student_reward_shop_association.c.reward_id
    ).filter(
        student_reward_shop_association.c.student_id == student_id,
        Reward.is_active == True
    )
    
    # Convert to ParentStudentShopReward schema
    result = []
    for reward, quantity in rewards_query:
        result.append(ParentStudentShopReward(
            id=reward.id,
            name=reward.name,
            description=reward.description,
            image_url=reward.image_url,
            point_cost=reward.point_cost,
            quantity=quantity
        ))
        
    return result

# Parent and admin endpoints for managing purchases
@router.get("/admin/purchases/{student_id}", response_model=List[RewardPurchaseSchema], tags=["rewards"])
def get_student_purchases_admin(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all purchases made by a specific student (Admin or Parent only)"""
    # Verify permissions
    is_admin = current_user.role == UserRole.ADMIN
    is_parent = current_user.role == UserRole.PARENT
    
    if not (is_admin or is_parent):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # If parent, check if the student is their child
    if is_parent and student_id not in [s.id for s in current_user.students]:
        raise HTTPException(status_code=403, detail="Not authorized to view this student's purchases")
    
    # Get student's purchases
    purchases = db.query(RewardPurchase).filter(
        RewardPurchase.student_id == student_id
    ).order_by(RewardPurchase.created_at.desc()).all()
    
    return purchases

@router.put("/admin/purchases/{purchase_id}", response_model=RewardPurchaseSchema, tags=["rewards"])
def update_purchase_status(
    purchase_id: int,
    update: RewardPurchaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update the delivery status of a purchase (Admin or Parent only)"""
    # Verify permissions
    is_admin = current_user.role == UserRole.ADMIN
    is_parent = current_user.role == UserRole.PARENT
    
    if not (is_admin or is_parent):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get the purchase
    purchase = db.query(RewardPurchase).filter(
        RewardPurchase.id == purchase_id
    ).first()
    
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    # If parent, check if the student is their child
    if is_parent and purchase.student_id not in [s.id for s in current_user.students]:
        raise HTTPException(status_code=403, detail="Not authorized to update this purchase")
    
    # Update the purchase
    purchase.is_delivered = update.is_delivered
    
    db.commit()
    db.refresh(purchase)
    
    return purchase
