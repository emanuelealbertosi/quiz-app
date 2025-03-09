from sqlalchemy import Column, String, Integer, ForeignKey, Text, Table, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, Base

# Association table for the many-to-many relationship between students and rewards in shop
user_reward_shop_association = Table(
    "user_reward_shop_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("reward_id", Integer, ForeignKey("rewards.id")),
    Column("quantity", Integer, default=1),  # Quantity of this reward available in student's shop
)

class Reward(BaseModel):
    """Model for rewards that can be purchased by students with points"""
    
    __tablename__ = "rewards"
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    point_cost = Column(Integer, nullable=False, default=50)
    is_active = Column(Boolean, default=True)
    
    # Foreign keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", foreign_keys=[creator_id])
    users_shops = relationship(
        "User",
        secondary=user_reward_shop_association,
        backref="shop_rewards"
    )
    users = relationship(
        "User",
        secondary="user_reward_association",
        back_populates="rewards"
    )
    purchases = relationship("RewardPurchase", back_populates="reward")
    
    def __repr__(self):
        return f"<Reward {self.name}, cost={self.point_cost}>"

class RewardPurchase(BaseModel):
    """Model for tracking reward purchases by students"""
    
    __tablename__ = "reward_purchases"
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="purchases")
    reward = relationship("Reward", back_populates="purchases")
    
    # Purchase information
    point_cost = Column(Integer, nullable=False)  # Store the point cost at time of purchase
    is_delivered = Column(Boolean, default=False)  # Whether the reward has been delivered
    
    def __repr__(self):
        return f"<RewardPurchase reward_id={self.reward_id}, user_id={self.user_id}>"
