-- Habilita la extensión pgvector en la base (T-211).
-- Se ejecuta sólo al inicializar un volumen nuevo (docker-entrypoint-initdb.d).
CREATE EXTENSION IF NOT EXISTS vector;
