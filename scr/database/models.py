from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import random
import string

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    is_captain = Column(Boolean, default=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    
    team = relationship("Team", back_populates="members")


class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    captain_id = Column(BigInteger, nullable=False)
    max_members = Column(Integer, nullable=False, default=6)
    
    members = relationship("User", back_populates="team")


def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


engine = create_engine('sqlite:///hackathon_bot.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_session():
    return Session()


def create_user(telegram_id, full_name, phone, is_captain=False):
    session = get_session()
    user = User(
        telegram_id=telegram_id,
        full_name=full_name,
        phone=phone,
        is_captain=is_captain
    )
    session.add(user)
    session.commit()
    user_id = user.id
    session.close()
    return user_id


def create_team(name, captain_id, max_members=6):
    session = get_session()
    
    while True:
        code = generate_team_code()
        existing_team = session.query(Team).filter_by(code=code).first()
        if not existing_team:
            break
    
    team = Team(
        name=name,
        code=code,
        captain_id=captain_id,
        max_members=max_members
    )
    session.add(team)
    session.commit()
    
    user = session.query(User).filter_by(telegram_id=captain_id).first()
    if user:
        user.team_id = team.id
        session.commit()
    
    team_id = team.id
    team_code = team.code
    session.close()
    return team_id, team_code


def join_team(telegram_id, team_code):
    session = get_session()
    
    team = session.query(Team).filter_by(code=team_code.upper()).first()
    if not team:
        session.close()
        return False, "Команду з таким кодом не знайдено"
    
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        session.close()
        return False, "Користувача не знайдено"
    
    if user.team_id:
        session.close()
        return False, "Ви вже є в команді"
    
    current_members = session.query(User).filter_by(team_id=team.id).count()
    if current_members >= team.max_members:
        session.close()
        return False, f"Команда вже заповнена ({team.max_members} учасників)"
    
    user.team_id = team.id
    session.commit()
    session.close()
    return True, f"Успішно приєдналися до команди {team.name}"


def get_user(telegram_id):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()
    return user


def get_team_by_code(code):
    session = get_session()
    team = session.query(Team).filter_by(code=code.upper()).first()
    session.close()
    return team
