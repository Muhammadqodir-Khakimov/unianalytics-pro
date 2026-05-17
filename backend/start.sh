#!/bin/sh
set -e

# Auto-init DB if first time (Railway production)
if [ "$APP_ENV" = "production" ] && [ "$AUTO_INIT_DB" = "true" ]; then
  echo "[start.sh] Auto-init DB..."
  python -c "
import sys
sys.path.insert(0, '.')
try:
    from sqlalchemy import inspect, text
    from app.database import OLTPBase, OLAPBase, oltp_engine, olap_engine
    from app import models
    OLTPBase.metadata.create_all(oltp_engine)
    OLAPBase.metadata.create_all(olap_engine)
    print('  Tables created')

    # Reconcile drifted columns (create_all does not ALTER existing tables).
    # Model has columns added later — bring DB schema up to date.
    with oltp_engine.connect() as conn:
        ins = inspect(conn)
        for tbl in OLTPBase.metadata.sorted_tables:
            if tbl.name not in ins.get_table_names():
                continue
            existing = {c['name'] for c in ins.get_columns(tbl.name)}
            for col in tbl.columns:
                if col.name in existing:
                    continue
                ctype = col.type.compile(oltp_engine.dialect)
                nullable = '' if col.nullable else ' NOT NULL'
                default = ''
                if col.server_default is not None and hasattr(col.server_default, 'arg'):
                    default = f\" DEFAULT '{col.server_default.arg}'\"
                ddl = f'ALTER TABLE {tbl.name} ADD COLUMN IF NOT EXISTS {col.name} {ctype}{default}'
                try:
                    conn.execute(text(ddl)); conn.commit()
                    print(f'  + {tbl.name}.{col.name}')
                except Exception as ex:
                    print(f'  ! {tbl.name}.{col.name}: {ex}')

    # Seed only if empty
    from sqlalchemy.orm import sessionmaker
    from app.models.oltp.user import User
    S = sessionmaker(bind=oltp_engine)
    db = S()
    if db.query(User).count() == 0:
        print('  DB empty, seeding...')
        from scripts.seed_data import main as seed
        seed(reset=False, students=300, teachers=50, grades=10000)
        from app.services.etl_service import run_full_etl
        run_full_etl()
        from scripts.seed_hemis import main as sh
        sh()
        from app.models.oltp.tenant import Tenant
        from app.services.permission_service import seed_permissions
        from app.database import oltp_session
        with oltp_session() as ds:
            if not ds.query(Tenant).first():
                ds.add(Tenant(code='tdu', name='Toshkent Davlat Universiteti', short_name='TDU', email='info@tdu.uz', max_students=15000))
                ds.commit()
            seed_permissions(ds)
        print('  Seed complete')
    else:
        print(f'  DB has {db.query(User).count()} users — skip seed')
    db.close()
except Exception as e:
    print(f'  Init error: {e}')
    import traceback; traceback.print_exc()
"
fi

# Start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
