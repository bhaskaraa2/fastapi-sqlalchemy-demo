from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session 

from data import models, schemas
from data.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):  
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products/", response_model=list[schemas.Product])
def read_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products


@app.get("/products/{product_id}", response_model=schemas.Product)  
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db.query(models.Product).filter(models.Product.id == product_id).delete(synchronize_session=False)
    db.commit()
    return {"message": "Product deleted successfully"}
