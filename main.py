from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()



# Configuración de la base de datos SQLite
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definición del modelo de datos
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ruta para crear un nuevo ítem
@app.post("/items/")
def create_item(id:int,name: str, description: str, db: Session = Depends(get_db)):
    db_item = Item(id=id , name=name, description=description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Ruta para obtener todos los ítems en el orden deseado
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    ordered_items = [{key: getattr(item, key) for key in ["id", "name", "description"]} for item in items]
    return ordered_items


# Ruta para obtener un ítem específico
@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/items/{item_id}")
def eliminar_item(item_id: int, db: Session = Depends(get_db)):
    # Buscar el ítem por su ID
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado, fallo al remover")

    # Si se encuentra el ítem, eliminarlo
    db.delete(item)
    db.commit()

    # Retornar un mensaje de confirmación
    return {"detail": "Item eliminado correctamente"}