

# Customer & Transaction Analytics — Olist E-Commerce
[![Dashboard](https://img.shields.io/badge/Dashboard-Live-green)](https://customer-transaction-analysis-m8jxtqbgwcfsrae5y4tt45.streamlit.app/)

Análisis end-to-end de comportamiento de clientes y segmentación RFM 
sobre 99,441 órdenes reales de e-commerce brasileño (2016-2018). 


## Herramientas
- PostgreSQL 16 — limpieza, transformación y análisis
- Python (Pandas, Matplotlib, Seaborn) — visualizaciones
- DBeaver — gestión de base de datos
- VS Code + Jupyter Notebook

## Estructura del proyecto

olist_analytics/
├── sql/
│   ├── creacion_schemas.sql
│   ├── creacion_tablas_staging.sql
│   ├── limpieza_datos.sql
│   ├── transformacion_datos.sql
│   └── analisis_rfm.sql
├── Analisis_rfm.ipynb
├── segmentos_rfm.png
├── revenue_segmentos.png
└── distribucion_rfm.png

## Arquitectura de datos
El proyecto usa una arquitectura de dos esquemas:
- **staging** — datos crudos importados directamente desde CSV
- **analytics** — datos limpios y transformados, listos para análisis

## Hallazgos de calidad de datos
- 2,965 órdenes sin fecha de entrega (órdenes canceladas o en tránsito)
- 8 órdenes con status "delivered" sin fecha de entrega — error real de datos
- 3,345 clientes con múltiples IDs por orden — resuelto usando customer_unique_id
- 610 productos sin categoría — reemplazados con "sin_categoria"

## Resultados RFM

| Segmento | Clientes | % |
|----------|----------|---|
| En riesgo | 22,311 | 23.9% |
| Potencial | 22,311 | 23.9% |
| Perdido | 15,029 | 16.1% |
| Cliente leal | 14,886 | 15.95% |
| Regular | 11,285 | 12.09% |
| Campeon | 7,528 | 8.06% |

## Insights de negocio
- La frecuencia promedio es 1 en todos los segmentos — Olist tiene un problema severo de retención
- El 47.8% de clientes está en segmentos En riesgo o Potencial — oportunidad de retención
- Los Campeones son solo el 8% pero tienen el mayor ticket promedio

## Dataset
[Brazilian E-Commerce — Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
