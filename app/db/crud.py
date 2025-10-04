from sqlalchemy.orm import Session
from app.models.db_models import Game, DayLog

def ensure_game(db: Session) -> Game:
    game = db.query(Game).first()
    if not game:
        game = Game()
        db.add(game)
        db.commit()
        db.refresh(game)
    return game

def reset_game(db: Session, consumo: float | None = None) -> Game:
    game = db.query(Game).first()
    if game:
        db.delete(game)
        db.commit()
    game = Game(consumo=consumo if consumo is not None else 5.0)
    db.add(game)
    db.query(DayLog).delete()
    db.commit()
    db.refresh(game)
    return game

def update_game(db: Session, game: Game):
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

def add_daylog(db: Session, **kwargs) -> DayLog:
    log = DayLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_history(db: Session, limit: int = 30):
    return db.query(DayLog).order_by(DayLog.id.desc()).limit(limit).all()
