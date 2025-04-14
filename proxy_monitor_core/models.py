from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

# 서버-그룹 연결 테이블
server_group_association = Table(
    'server_group_association',
    Base.metadata,
    Column('server_id', Integer, ForeignKey('servers.id')),
    Column('group_id', Integer, ForeignKey('server_groups.id'))
)

class Server(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)
    address = Column(String(200), unique=True, nullable=False)
    description = Column(String(500))
    groups = relationship('ServerGroup', secondary=server_group_association, back_populates='servers')

    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'description': self.description,
            'groups': [group.name for group in self.groups]
        }

class ServerGroup(Base):
    __tablename__ = 'server_groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    servers = relationship('Server', secondary=server_group_association, back_populates='groups')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'servers': [server.address for server in self.servers]
        }

# 데이터베이스 연결 설정
engine = create_engine('sqlite:///proxy_monitor.db')
Base.metadata.create_all(engine)

# 세션 생성
Session = sessionmaker(bind=engine) 