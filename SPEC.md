# Olist Analytics — Spec

> Qué se construye y cómo debe funcionar. El orden y las fechas van en `ROADMAP.md`.
> El detalle técnico está en `olist_analytics/CLAUDE.md`, que manda sobre este archivo si difieren.

## 1. Qué es
Una segmentación RFM de los clientes de un e-commerce brasileño, con el pipeline de SQL que la produce y un dashboard para explorarla.

## 2. Para quién
Un equipo comercial o de CRM que necesita saber a qué clientes hablarle distinto: a quién retener, a quién reactivar y a quién dejar ir. También es pieza de portafolio: enseña el camino de datos crudos a segmentos accionables.

## 3. Qué debe tener
- Pipeline en PostgreSQL ejecutable en orden, de los CSV crudos a las tablas de análisis.
- Puntajes de recencia, frecuencia y monetario por cliente.
- Seis segmentos con nombres que un área comercial entienda sin glosario.
- Un dashboard publicado que muestre el tamaño de cada segmento y lo que aporta.

## 4. Cómo debe verse
Dashboard de Streamlit: primero cuántos clientes hay en cada segmento y cuánto pesan en ingresos; el detalle, después.

## 5. Qué NO debe tener
- **No predice**: describe lo que ya pasó. Un cliente "en riesgo" lo es por su comportamiento pasado, no por un modelo.
- No trabaja con datos de una empresa real: el dataset de Olist es público.
- No recomienda campañas ni descuentos concretos; ordena a quién hablarle primero.

## 6. Comportamiento
- Un cliente con una sola compra puede quedar en un segmento alto por recencia: es correcto, y por eso el segmento se lee junto con la frecuencia.
- Las categorías de producto vacías se guardan como `sin_categoria`, no se descartan: descartarlas cambiaría los totales.
- `NTILE(5)` reparte en quintiles, así que los segmentos son **relativos a este dataset**. Con otros datos, los mismos números caerían en otro segmento.

## 7. Criterio de terminado
- El pipeline corre de principio a fin sobre una base vacía y deja las tablas de `analytics` listas.
- Los ~93.350 clientes quedan repartidos en los seis segmentos, sin que uno solo se lleve casi todo.
- El dashboard abre desde su enlace público sin nada instalado.
