-- =====================================================================
-- Usuario de aplicacion del modulo Desembolso (minimo privilegio)
-- Solicitud a Infraestructura del Modelo Referencial (seccion 10).
-- * Sin DELETE en ninguna tabla del modulo.
-- * des_auditoria y des_validacion: solo SELECT e INSERT.
-- Reemplazar la contrasena ANTES de ejecutar y no versionar la real.
-- No forma parte de 99_bna_unificado.sql.
-- =====================================================================
CREATE USER IF NOT EXISTS 'des_app'@'%' IDENTIFIED BY 'CAMBIAR_ANTES_DE_EJECUTAR';

GRANT SELECT, INSERT, UPDATE ON bna.des_orden               TO 'des_app'@'%';
GRANT SELECT, INSERT         ON bna.des_validacion          TO 'des_app'@'%';
GRANT SELECT, INSERT, UPDATE ON bna.des_evento_entrega      TO 'des_app'@'%';
GRANT SELECT, INSERT         ON bna.des_auditoria           TO 'des_app'@'%';
GRANT SELECT, INSERT, UPDATE ON bna.des_solicitud_reversion TO 'des_app'@'%';
GRANT SELECT, INSERT, UPDATE ON bna.des_correlativo         TO 'des_app'@'%';
GRANT SELECT ON bna.des_v_ordenes_inciertas   TO 'des_app'@'%';
GRANT SELECT ON bna.des_v_entregas_pendientes TO 'des_app'@'%';
GRANT SELECT ON bna.des_v_conciliacion_diaria TO 'des_app'@'%';
