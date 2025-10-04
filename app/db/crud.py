from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.db_models import Game, DayLog

def ensure_game(db: Session) -> Game:
    game = db.query(Game).first()
    if not game:
        game = Game(fecha=date.today())
        db.add(game)
        db.commit()
        db.refresh(game)
    return game

def reset_game(db: Session, consumo: float | None = None) -> Game:
    game = db.query(Game).first()
    if game:
        db.delete(game)
        db.commit()
    game = Game(consumo=consumo if consumo is not None else 5.0, fecha=date.today())
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

# Helpers nuevos
def set_location(db: Session, lat: float, lon: float) -> Game:
    game = ensure_game(db)
    game.lat = lat
    game.lon = lon
    update_game(db, game)
    return game

def set_date(db: Session, new_date: date) -> Game:
    game = ensure_game(db)
    game.fecha = new_date
    update_game(db, game)
    return game

def next_date(db: Session) -> Game:
    game = ensure_game(db)
    game.fecha = (game.fecha or date.today()) + timedelta(days=1)
    update_game(db, game)
    return game
