# Alembic migration

## Buyruqlar

### OLTP database
```bash
# Migration yaratish (model o'zgargandan keyin)
alembic -x target=oltp revision --autogenerate -m "tavsif"

# Yangilash
alembic -x target=oltp upgrade head
```

### OLAP database
```bash
alembic -x target=olap revision --autogenerate -m "tavsif"
alembic -x target=olap upgrade head
```

> Eslatma: `alembic.ini` faylida `target` o'zgaruvchisi default olarak `oltp` ga teng.
