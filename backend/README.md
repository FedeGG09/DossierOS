# Qualipharma Backend

Backend FastAPI para dossiers regulatorios UE con:
- Supabase + RLS
- Groq
- pgvector
- ingesta EMA
- OCR para PDFs escaneados
- versionado de dossiers
- audit trail regulatorio

## Estructura
- `app/` código Python
- `sql/` scripts para Supabase
- `Dockerfile` listo para Render

## Uso local
1. Crear `.env` a partir de `.env.example`
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar:
   ```bash
   uvicorn app.main:app --reload
   ```

## SQL en Supabase
Ejecutar en este orden:
1. `sql/schema.sql`
2. `sql/rls_policies.sql`

## Endpoints
- `GET /health`
- `POST /api/v1/agent/decision`
- `POST /api/v1/dossiers/create`
- `POST /api/v1/dossiers/compare`
- `POST /api/v1/dossiers/compare-upload`
- `POST /api/v1/dossiers/{dossier_id}/version`
- `POST /api/v1/admin/reindex`
- `POST /api/v1/admin/ingest-ema`

## Seguridad
Los endpoints de usuario requieren JWT de Supabase en:
`Authorization: Bearer <token>`

Los endpoints admin requieren `X-Admin-Key` si definís `ADMIN_KEY`.
