USE backlog_nacional;

CREATE TABLE IF NOT EXISTS backlog_nacional_historial (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    CUENTA VARCHAR(255),
    OT VARCHAR(255),
    DESCRIPCION TEXT,
    usuario_descripcion TEXT,
    fecha_descripcion DATETIME,
    fecha_archivado DATETIME,
    solicitud TEXT,
    motivo TEXT,
    fecha_reagendar DATETIME,
    franja_horaria VARCHAR(100),
    razon_comercial VARCHAR(255),
    INDEX idx_cuenta (CUENTA),
    INDEX idx_ot (OT)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
