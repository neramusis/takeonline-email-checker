import logging

from sqlalchemy import (Boolean, Column, DateTime, Integer, String,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Settings

Base = declarative_base()

settings = Settings()
logger = logging.getLogger(__name__)


class OrderStats(Base):
    __tablename__ = "order_stats"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(255))
    email_date = Column(DateTime)
    email_id = Column(String(255))
    status = Column(Integer)
    tracking_id = Column(String(255), nullable=True)


db_url_sync = (
    f"mysql+pymysql://{settings.mysql_username}:{settings.mysql_password}"
    f"@localhost:3306/{settings.mysql_database}"
)
engine = create_engine(db_url_sync)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


def store_order_stats(
    external_id: str,
    email_date: str,
    email_id: str,
    status: int,
    tracking_id: str,
) -> None:
    session = Session()
    session.add(
        OrderStats(
            external_id=external_id,
            email_date=email_date,
            email_id=email_id,
            status=status,
            tracking_id=tracking_id,
        )
    )
    session.commit()
    session.close()


def store_response(
    order_id: str,
    open_api_json: dict,
    external_id: str,
    email_date: str,
    email_id: str,
) -> None:
    try:
        logger.info(f"Store for order id: `{order_id}`.")
        if str(open_api_json["order_id"]).replace(" ", "") == order_id:
            if isinstance(open_api_json["tracking_id"], list):
                for tracking_id in open_api_json["tracking_id"]:
                    store_order_stats(
                        external_id=external_id,
                        email_date=email_date,
                        email_id=email_id,
                        status=open_api_json["status"],
                        tracking_id=str(tracking_id),
                    )
            else:
                store_order_stats(
                    external_id=external_id,
                    email_date=email_date,
                    email_id=email_id,
                    status=open_api_json["status"],
                    tracking_id=(
                        str(open_api_json["tracking_id"])
                        if open_api_json["tracking_id"]
                        else None
                    ),
                )
    except Exception as exc:
        logger.error(f"Error storing order stats. Error: `{exc!r}`.")


def check_email_exists(email_id: str) -> bool:
    session = Session()
    try:
        exists = (
            session.query(OrderStats).filter(OrderStats.email_id == email_id).first()
            is not None
        )
        return exists
    except Exception as exc:
        logger.error(f"Error checking if email exists. Error: `{exc!r}`.")
        return False
    finally:
        session.close()
