from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import random
import os

try:
    from app import models, database, schemas
except ImportError:
    import models, database, schemas

app = FastAPI(title="Galactic Bounty Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

database.Base.metadata.create_all(bind=database.engine)

# Imagem estável de fundo espacial para quem ficar sem foto
FALLBACK_IMAGE = "https://static-mh.content.disney.io/starwars/assets/navigation/navigation_stars_left-879f9de0bc61.jpg"

@app.get("/", response_class=HTMLResponse)
def read_root():
    caminho_html = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    if os.path.exists(caminho_html):
        with open(caminho_html, "r", encoding="utf-8") as file:
            return file.read()
    return "<h1>Terminal Conectado. Coloque o index.html na pasta templates.</h1>"

# --- ROTAS DE CAÇADORES ---

@app.get("/hunters/")
def list_hunters(db: Session = Depends(database.get_db)):
    return db.query(models.Hunter).all()

@app.post("/hunters/", status_code=status.HTTP_201_CREATED)
def create_hunter(hunter_in: schemas.HunterCreate, db: Session = Depends(database.get_db)):
    # Se o campo de URL estiver vazio ou contiver apenas espaços, define a imagem padrão
    if not hunter_in.avatar_url or hunter_in.avatar_url.strip() == "":
        hunter_in.avatar_url = FALLBACK_IMAGE
        
    db_hunter = models.Hunter(**hunter_in.dict())
    db.add(db_hunter)
    db.commit()
    db.refresh(db_hunter)
    return db_hunter

@app.delete("/hunters/{hunter_id}")
def delete_hunter(hunter_id: int, db: Session = Depends(database.get_db)):
    hunter = db.query(models.Hunter).filter(models.Hunter.id == hunter_id).first()
    if not hunter:
        raise HTTPException(status_code=404, detail="Caçador não encontrado.")
    db.query(models.Bounty).filter(models.Bounty.hunter_id == hunter_id, models.Bounty.status == "Em Progresso").update(
        {"hunter_id": None, "status": "Disponível"}
    )
    db.delete(hunter)
    db.commit()
    return {"detail": "Ficha desativada."}

# --- ROTAS DE CONTRATOS (BOUNTIES) ---

@app.get("/bounties/")
def list_bounties(db: Session = Depends(database.get_db)):
    return db.query(models.Bounty).all()

@app.post("/bounties/", status_code=status.HTTP_201_CREATED)
def create_bounty(bounty_in: schemas.BountyCreate, db: Session = Depends(database.get_db)):
    # Se o campo de URL estiver vazio ou contiver apenas espaços, define a imagem padrão
    if not bounty_in.target_image_url or bounty_in.target_image_url.strip() == "":
        bounty_in.target_image_url = FALLBACK_IMAGE
        
    db_bounty = models.Bounty(**bounty_in.dict())
    db.add(db_bounty)
    db.commit()
    db.refresh(db_bounty)
    return db_bounty

@app.post("/bounties/{bounty_id}/accept/{hunter_id}")
def accept_bounty(bounty_id: int, hunter_id: int, db: Session = Depends(database.get_db)):
    bounty = db.query(models.Bounty).filter(models.Bounty.id == bounty_id).first()
    if not bounty or bounty.status != "Disponível":
        raise HTTPException(status_code=400, detail="Contrato indisponível.")
    bounty.hunter_id = hunter_id
    bounty.status = "Em Progresso"
    db.commit()
    return bounty

@app.post("/bounties/{bounty_id}/complete")
def complete_bounty(bounty_id: int, db: Session = Depends(database.get_db)):
    bounty = db.query(models.Bounty).filter(models.Bounty.id == bounty_id).first()
    if not bounty or bounty.status != "Em Progresso":
        raise HTTPException(status_code=400, detail="Alvo não está em combate.")
        
    hunter = db.query(models.Hunter).filter(models.Hunter.id == bounty.hunter_id).first()
    
    dado = random.randint(1, 20)
    poder_total = dado + hunter.starship_firepower
    defesa_alvo = bounty.difficulty_rating * 4
    
    if poder_total >= defesa_alvo:
        bounty.status = "Concluído"
        hunter.xp += bounty.difficulty_rating * 10
        hunter.credits_balance += bounty.reward_credits
        hunter.level = (hunter.xp // 50) + 1
        db.commit()
        return {
            "resultado": "SUCESSO",
            "evento": f"{hunter.name} capturou {bounty.target_name}!",
            "dados": f"Dado: {dado} + Armamento: {hunter.starship_firepower} = {poder_total} vs Defesa: {defesa_alvo}",
            "recompensa": f"+{bounty.reward_credits} créditos galácticos obtidos!"
        }
    else:
        prejuizo = bounty.difficulty_rating * 100
        hunter.credits_balance = max(0, hunter.credits_balance - prejuizo)
        bounty.status = "Disponível"
        bounty.hunter_id = None
        db.commit()
        return {
            "resultado": "FALHA",
            "evento": f"{bounty.target_name} contra-atacou e escapou!",
            "dados": f"Dado: {dado} + Armamento: {hunter.starship_firepower} = {poder_total} vs Defesa: {defesa_alvo}",
            "consequencia": f"Nave danificada. Gastou {prejuizo} créditos em reparos."
        }

@app.delete("/bounties/{bounty_id}")
def delete_bounty(bounty_id: int, db: Session = Depends(database.get_db)):
    bounty = db.query(models.Bounty).filter(models.Bounty.id == bounty_id).first()
    if not bounty:
        raise HTTPException(status_code=404, detail="Contrato inexistente.")
    db.delete(bounty)
    db.commit()
    return {"detail": "Contrato removido."}