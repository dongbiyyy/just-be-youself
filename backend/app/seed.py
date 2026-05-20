"""Seed demo data. Run with: python -m app.seed

Creates a small group structure:
  集团母公司 (Holding)
   ├─ 子公司A: 智能科技
   ├─ 子公司B: 绿色能源
   └─ 子公司C: 国际贸易
        └─ 孙公司: 海外销售

Plus 5 demo persons with overlapping positions to exercise the conflict engine,
plus initial shareholdings.
"""
from datetime import date

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_id_card, hash_password
from app.models import Company, Person, Position, Shareholding, User
from app.services.conflict import ensure_default_rules, detect_conflicts, detect_term_expiry


def _get_or_create_company(db, **fields):
    inst = db.query(Company).filter(Company.name == fields["name"]).first()
    if inst:
        return inst
    inst = Company(**fields)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


def _get_or_create_person(db, *, name: str, id_card: str, **extra):
    h = hash_id_card(id_card)
    inst = db.query(Person).filter(Person.id_card_hash == h).first()
    if inst:
        return inst
    inst = Person(name=name, id_card_hash=h, id_card_last4=id_card[-4:], **extra)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(
                User(
                    username="admin",
                    email="admin@example.com",
                    full_name="系统管理员",
                    hashed_password=hash_password("admin123"),
                    role="superadmin",
                )
            )
            db.commit()

        holding = _get_or_create_company(
            db,
            name="示例控股集团有限公司",
            credit_code="91110000DEMO00001X",
            short_name="示例集团",
            legal_representative="张三",
            reg_capital=100000000,
            established_date=date(2005, 6, 1),
            reg_address="北京市朝阳区示例路1号",
            company_type="股份有限公司",
        )
        a = _get_or_create_company(
            db, name="示例智能科技有限公司", credit_code="91110000DEMO00002A",
            short_name="智能科技", legal_representative="李四", reg_capital=20000000,
            established_date=date(2012, 3, 8), parent_company_id=holding.id,
            company_type="有限责任公司",
        )
        b = _get_or_create_company(
            db, name="示例绿色能源有限公司", credit_code="91110000DEMO00003B",
            short_name="绿色能源", legal_representative="王五", reg_capital=50000000,
            established_date=date(2015, 9, 20), parent_company_id=holding.id,
            company_type="有限责任公司",
        )
        c = _get_or_create_company(
            db, name="示例国际贸易有限公司", credit_code="91110000DEMO00004C",
            short_name="国际贸易", legal_representative="赵六", reg_capital=30000000,
            established_date=date(2010, 11, 11), parent_company_id=holding.id,
            company_type="有限责任公司",
        )
        d = _get_or_create_company(
            db, name="示例海外销售（香港）有限公司", credit_code="91110000DEMO00005D",
            short_name="海外销售", legal_representative="赵六", reg_capital=10000000,
            established_date=date(2018, 4, 1), parent_company_id=c.id,
            company_type="有限责任公司",
        )

        zhang = _get_or_create_person(db, name="张三", id_card="11010119700101001X", phone="13800000001")
        li = _get_or_create_person(db, name="李四", id_card="110101198202020022", phone="13800000002")
        wang = _get_or_create_person(db, name="王五", id_card="110101197503030033", phone="13800000003")
        zhao = _get_or_create_person(db, name="赵六", id_card="110101198804040044", phone="13800000004")
        sun = _get_or_create_person(db, name="孙七", id_card="110101199005050055", phone="13800000005")

        # Wipe and reseed positions for idempotency.
        if db.query(Position).count() == 0:
            positions = [
                # 张三：集团董事长 + 子公司董事
                Position(person_id=zhang.id, company_id=holding.id, position_type="董事长",
                         start_date=date(2020, 1, 1), end_date=date(2026, 12, 31)),
                Position(person_id=zhang.id, company_id=a.id, position_type="董事",
                         start_date=date(2021, 1, 1), end_date=date(2026, 6, 30)),
                # 李四：智能科技法定代表人 + 总经理
                Position(person_id=li.id, company_id=a.id, position_type="法定代表人",
                         start_date=date(2019, 5, 1)),
                Position(person_id=li.id, company_id=a.id, position_type="总经理",
                         start_date=date(2019, 5, 1)),
                # 王五：绿色能源 + 集团兼任监事
                Position(person_id=wang.id, company_id=b.id, position_type="法定代表人",
                         start_date=date(2018, 1, 1)),
                Position(person_id=wang.id, company_id=holding.id, position_type="监事",
                         start_date=date(2022, 1, 1), end_date=date(2026, 1, 1)),
                # 赵六：国际贸易法人 + 海外子公司法人；会触发母子同任高管告警
                Position(person_id=zhao.id, company_id=c.id, position_type="法定代表人",
                         start_date=date(2017, 6, 1)),
                Position(person_id=zhao.id, company_id=d.id, position_type="法定代表人",
                         start_date=date(2019, 6, 1)),
                Position(person_id=zhao.id, company_id=c.id, position_type="总经理",
                         start_date=date(2017, 6, 1)),
                # 孙七：故意制造监事兼董事冲突场景
                Position(person_id=sun.id, company_id=b.id, position_type="监事",
                         start_date=date(2022, 3, 1)),
                Position(person_id=sun.id, company_id=a.id, position_type="董事",
                         start_date=date(2022, 4, 1), end_date=date(2025, 7, 1)),
            ]
            db.add_all(positions)
            db.commit()

        if db.query(Shareholding).count() == 0:
            shareholdings = [
                # 张三持股控股集团 60%、李四 10%
                Shareholding(company_id=holding.id, shareholder_type="person", shareholder_id=zhang.id,
                             ratio=60, amount=60000000, contribute_date=date(2005, 6, 1)),
                Shareholding(company_id=holding.id, shareholder_type="person", shareholder_id=li.id,
                             ratio=10, amount=10000000, contribute_date=date(2005, 6, 1)),
                # 集团对各子公司控股
                Shareholding(company_id=a.id, shareholder_type="company", shareholder_id=holding.id,
                             ratio=80, amount=16000000, contribute_date=date(2012, 3, 8)),
                Shareholding(company_id=b.id, shareholder_type="company", shareholder_id=holding.id,
                             ratio=100, amount=50000000, contribute_date=date(2015, 9, 20)),
                Shareholding(company_id=c.id, shareholder_type="company", shareholder_id=holding.id,
                             ratio=90, amount=27000000, contribute_date=date(2010, 11, 11)),
                Shareholding(company_id=d.id, shareholder_type="company", shareholder_id=c.id,
                             ratio=100, amount=10000000, contribute_date=date(2018, 4, 1)),
            ]
            db.add_all(shareholdings)
            db.commit()

        ensure_default_rules(db)
        detect_conflicts(db)
        detect_term_expiry(db)
        print("种子数据初始化完成。可用账号: admin / admin123")
    finally:
        db.close()


if __name__ == "__main__":  # pragma: no cover
    run()
