

from typing import List,Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column, Integer, String, Float, Boolean, create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from enum import Enum


# Database setup
DATABASE_URL = "postgresql://postgres:Mkubwa*94@localhost/itemsDb"  # Update with your credentials
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    price = Column(Float)
    quantity = Column(Integer)
    is_registered = Column(Boolean, default=False, nullable=False)
# Database model

class RoleEnum(str, Enum):
    admin = "admin"
    guest = "guest"
    supporter = "supporter"

class StatusEnum(str, Enum):
    active = "active"
    suspended = "suspended"
    pending = "pending"
    disabled = "disabled"

class LevelOfEducationEnum(str, Enum):
    primary = "primary"
    secondary = "secondary"
    degree = "degree"
    postgraduate = "postgraduate"
    none = "none"  # For users with no formal education

class IncomeEnum(str, Enum):
    below_1000 = "below_1000_tsh"
    below_10000 = "below_10000_tsh"
    below_30000 = "below_30000_tsh"


# User model
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    createdDate = Column(DateTime, default=datetime.utcnow)
    role = Column(String, nullable=False,default=RoleEnum.guest.value)
    # role = Column(Enum(RoleEnum), nullable=False,default=RoleEnum.guest.value)

    status = Column(String, nullable=False,default=StatusEnum.active.value)
    # status = Column(Enum(StatusEnum), nullable=False,default=StatusEnum.active.value)
    phonenumber = Column(String, nullable=True)
    profilePicture = Column(Text, nullable=True)  # Use Text for larger image data or a URL
    region = Column(String, nullable=True)
    street = Column(String, nullable=True)
    # levelOfEducation = Column(String, nullable=True)
    # income = Column(Float, nullable=True)
    levelOfEducation = Column(String, nullable=False, default=LevelOfEducationEnum.none.value)
    income = Column(String, nullable=False, default=IncomeEnum.below_1000.value)
    # levelOfEducation = Column(Enum(LevelOfEducationEnum), nullable=False, default=LevelOfEducationEnum.none.value)
    # income = Column(Enum(IncomeEnum), nullable=True)
    email = Column(String, unique=True, nullable=False)

    # Relationships
    skills = relationship("SkillDB", back_populates="user")
    works = relationship("WorkDB", back_populates="user")
    products = relationship("ProductDB", back_populates="user")

class SkillEnum(str, Enum):
    beginer = "beginer"
    intermidiate = "intermidiate"
    advanced = "advanced"
    expert = "expert"
# Skill model
class SkillDB(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, nullable=False)
    skill_level = Column(String, nullable=False, default=SkillEnum.beginer.value)
    # skill_level = Column(Enum(SkillEnum), nullable=False, default=SkillEnum.beginer.value)
    comments = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserDB", back_populates="skills")

# Work model
class WorkEnum(str, Enum):
    parttime = "parttime"
    fulltime = "fulltime"
    freelance = "freelance"
   
class WorkExperience(str, Enum):
    beginer = "beginer"
    intermidiate = "intermidiate"
    advanced = "advanced"
class WorkDB(Base):
    __tablename__ = "works"
    id = Column(Integer, primary_key=True, index=True)
    work_title = Column(String, nullable=False)
    work_description = Column(Text, nullable=False)
    work_type = Column(String, nullable=False, default=WorkEnum.parttime.value)
    work_experience = Column(String, nullable=False, default=WorkExperience.beginer.value)
    # work_type = Column(Enum(WorkEnum), nullable=False, default=WorkEnum.parttime.value)
    # work_experience = Column(Enum(WorkExperience), nullable=False, default=WorkExperience.beginer.value)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserDB", back_populates="works")

# Product model
class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    productName = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserDB", back_populates="products")

# Create database tables
Base.metadata.create_all(bind=engine)

# FastAPI setup
app = FastAPI()

# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)

class Item(BaseModel):
    name: str 
    description: str = None
    price: float 
    quantity: int 
    is_registered: bool = False

    # class Config:   orm_mode = True
    #     from_attributes = True
@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/items", response_model=Item) 
def create_item(item: Item):
    db = SessionLocal()
    new_item = ItemDB(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()
    return  jsonable_encoder(new_item) 

@app.get("/items/{item_id}") 
def get_item(item_id: int):
    db = SessionLocal()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    db.close()
    if item:
        return item
    else:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

@app.get("/items") 
def get_all_items(limit: int = Query(100, ge=1),offset: int = Query(0, ge=0)):
    db = SessionLocal()
    items = db.query(ItemDB).offset(offset).limit(limit).all()
    db.close()
    return items

@app.put("/items/{item_id}")
def update_item(item_id: int, updated_item: Item):
    db = SessionLocal()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if item:
        for key, value in updated_item.model_dump().items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        db.close()
        return item
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        db.close()
        return {"item_id": item_id, "deleted_item": item}
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    

    # // Note: The following code is for the  new models and their CRUD operations
    # Create a User



# // Note: The following code is for the  new models and their CRUD operations


# User model

class User(BaseModel):
    fullname: str
    username: str
    password: str
    createdDate: Optional[datetime] = None
    role: RoleEnum = RoleEnum.guest
    status: StatusEnum = StatusEnum.active
    phonenumber: Optional[str] = None
    profilePicture: Optional[str] = None  # URL or path
    region: Optional[str] = None
    street: Optional[str] = None
    levelOfEducation: LevelOfEducationEnum = LevelOfEducationEnum.none
    income: IncomeEnum = IncomeEnum.below_1000
    email: str

    class Config:
        from_attributes = True

@app.post("/users", response_model=User)
def create_user(user: User):
    db = SessionLocal()
    new_user = UserDB(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return jsonable_encoder(new_user)

# Read a User by ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    db.close()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")


@app.get("/users") 
def get_all_users(limit: int = Query(100, ge=1),offset: int = Query(0, ge=0)):
    db = SessionLocal()
    users = db.query(UserDB).offset(offset).limit(limit).all()
    db.close()
    return users

# Update a User
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User):
    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        for key, value in updated_user.model_dump().items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        db.close()
        return user
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

# Delete a User
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        db.close()
        return {"user_id": user_id, "message": "User deleted successfully"}
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")


#  Skill API Model

class Skill(BaseModel):
    skill_name: str
    skill_level: SkillEnum = SkillEnum.beginer
    comments: Optional[str] = None
    # skill_id: int  
    user_id: int  # Foreign key reference to the user

    class Config:
        from_attributes = True

@app.post("/skills", response_model=Skill)
def create_skill(skill: Skill):
    db = SessionLocal()
    new_skill = SkillDB(**skill.model_dump())
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    db.close()
    return jsonable_encoder(new_skill)

# Read a Skill by ID
@app.get("/skills/{skill_id}", response_model=Skill)
def get_skill(skill_id: int):
    db = SessionLocal()
    skill = db.query(SkillDB).filter(SkillDB.id == skill_id).first()
    db.close()
    if skill:
        return skill
    else:
        raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")


@app.get("/skills") 
def get_all_skills(limit: int = Query(100, ge=1),offset: int = Query(0, ge=0)):
    db = SessionLocal()
    skills = db.query(SkillDB).offset(offset).limit(limit).all()
    db.close()
    return skills

# Update a Skill
@app.put("/skills/{skill_id}", response_model=Skill)
def update_skill(skill_id: int, updated_skill: Skill):
    db = SessionLocal()
    skill = db.query(SkillDB).filter(SkillDB.id == skill_id).first()
    if skill:
        for key, value in updated_skill.model_dump().items():
            setattr(skill, key, value)
        db.commit()
        db.refresh(skill)
        db.close()
        return skill
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")

# Delete a Skill
@app.delete("/skills/{skill_id}")
def delete_skill(skill_id: int):
    db = SessionLocal()
    skill = db.query(SkillDB).filter(SkillDB.id == skill_id).first()
    if skill:
        db.delete(skill)
        db.commit()
        db.close()
        return {"skill_id": skill_id, "message": "Skill deleted successfully"}
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")

    


#  Work API Model

class Work(BaseModel):
    work_title: str
    work_type: WorkEnum= WorkEnum.parttime
    work_description: Optional[str] = None
    work_experience: WorkExperience= WorkExperience.beginer
    # work_id: int   
    user_id: int  # Foreign key reference to the user

    class Config:
        from_attributes = True

@app.post("/works", response_model=Work)
def create_work(work: Work):
    db = SessionLocal()
    new_work = WorkDB(**work.model_dump())
    db.add(new_work)
    db.commit()
    db.refresh(new_work)
    db.close()
    return jsonable_encoder(new_work)

# Read a Work by ID
@app.get("/works/{work_id}", response_model=Work)
def get_work(work_id: int):
    db = SessionLocal()
    work = db.query(WorkDB).filter(WorkDB.id == work_id).first()
    db.close()
    if work:
        return work
    else:
        raise HTTPException(status_code=404, detail=f"Work {work_id} not found")


@app.get("/works") 
def get_all_works(limit: int = Query(100, ge=1),offset: int = Query(0, ge=0)):
    db = SessionLocal()
    works = db.query(WorkDB).offset(offset).limit(limit).all()
    db.close()
    return works

# Update a Work
@app.put("/works/{work_id}", response_model=Work)
def update_work(work_id: int, updated_work: Work):
    db = SessionLocal()
    work = db.query(WorkDB).filter(WorkDB.id == work_id).first()
    if work:
        for key, value in updated_work.model_dump().items():
            setattr(work, key, value)
        db.commit()
        db.refresh(work)
        db.close()
        return work
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"Work {work_id} not found")

# Delete a Work
@app.delete("/works/{work_id}")
def delete_work(work_id: int):
    db = SessionLocal()
    work = db.query(WorkDB).filter(WorkDB.id == work_id).first()
    if work:
        db.delete(work)
        db.commit()
        db.close()
        return {"work_id": work_id, "message": "Work deleted successfully"}
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"Work {work_id} not found")

    
#  Product API Model
class Product(BaseModel):
    productName: str
    description: Optional[str] = None
    price: float 
    image: Optional[str] = None  # URL or path
    comments: Optional[str] = None
    # product_id: int  
    user_id: int  # Foreign key reference to the user

    class Config:
        from_attributes = True

@app.post("/products", response_model=Product)
def create_product(product: Product):
    db = SessionLocal()
    new_product = ProductDB(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    db.close()
    return jsonable_encoder(new_product)

# Read a Product by ID
@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    db = SessionLocal()
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    db.close()
    if product:
        return product
    else:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    

@app.get("/products")
def get_all_products(limit: int = Query(100, ge=1),offset: int = Query(0, ge=0)):
    db = SessionLocal()
    products = db.query(ProductDB).offset(offset).limit(limit).all()
    db.close()
    return products

# Update a Product
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_product: Product):
    db = SessionLocal()
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product:
        for key, value in updated_product.model_dump().items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        db.close()
        return product
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

# Delete a Product
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        db.close()
        return {"product_id": product_id, "message": "Product deleted successfully"}
    else:
        db.close()
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")