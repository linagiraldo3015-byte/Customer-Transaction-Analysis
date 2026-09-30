# Olist Analytics — Roadmap

> Este archivo cambia a medida que avanza el proyecto. Actualízalo cuando se cierre algo o se tome una decisión.
> El contexto estable está en `CLAUDE.md`; qué se construye, en `SPEC.md`.

**Fase actual:** terminado. Dashboard publicado en Streamlit Cloud, sin trabajo en curso
**Bloqueante principal:** —
**Última revisión:** 29 sep 2026

---

## Fase 1 — Carga ✅
Dataset de Olist (99.441 órdenes, 2016–2018) en PostgreSQL 16, trabajado desde DBeaver. `creacion_schemas.sql` y `creacion_tablas_staging.sql`: todo entra como TEXT para que ningún CSV falle al importar.

## Fase 2 — Limpieza y transformación ✅
`limpieza_datos.sql` audita la calidad; `transformacion_datos.sql` arma las tablas de `analytics` con sus tipos reales y la tabla maestra `customer_transactions`.

## Fase 3 — Segmentación RFM ✅
`analisis_rfm.sql` calcula los puntajes con `NTILE(5)` y reparte ~93.350 clientes en seis segmentos: Campeón, Cliente leal, Potencial, Regular, En riesgo, Perdido.

## Fase 4 — Dashboard ✅
`dashboard.py` en Streamlit, publicado, leyendo `rfm_data.csv`.

---

## Pendientes menores
- [ ] El `CLAUDE.md` que está dentro de `olist_analytics/` es el genérico que genera Claude Code y está en inglés. Si se retoma el proyecto, vale la pena reescribirlo en español como los demás
- [ ] La carpeta tiene un nivel de más (`olist-analytics/olist_analytics/`). Funciona, pero no se parece a los otros proyectos. **No moverlo sin revisar antes las rutas del dashboard publicado**

---

## Decisiones tomadas
| Fecha | Decisión | Por qué |
|---|---|---|
| may 2026 | El cliente es `customer_unique_id`, no `customer_id` | `customer_id` cambia en cada transacción: contarlo como cliente inflaría el número y arruinaría el RFM |
| may 2026 | Solo órdenes `delivered` con fecha de entrega | Una orden cancelada o sin entregar no es comportamiento de compra |
| may 2026 | La recencia se mide contra la fecha más reciente del dataset, no contra hoy | Los datos terminan en 2018; medir contra hoy dejaría a todo el mundo como "perdido" |
| may 2026 | Los segmentos se arman solo con R y F | El monetario se calcula pero no entra en la regla: con él, los clientes de ticket alto y una sola compra se mezclaban con los leales |
