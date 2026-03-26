-- =============================================================
-- DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System
-- MySQL Database Schema
-- =============================================================

CREATE DATABASE IF NOT EXISTS campus_incidents_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE campus_incidents_db;

-- -------------------------------------------------------------
-- Table: users
-- Role-based authentication: 'admin' or 'staff'
-- Passwords stored as Werkzeug PBKDF2-SHA256 hashes
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id            INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    email         VARCHAR(120)    NOT NULL,
    password_hash VARCHAR(255)    NOT NULL,
    first_name    VARCHAR(100)    NOT NULL,
    last_name     VARCHAR(100)    NOT NULL,
    role          ENUM('admin','staff') NOT NULL DEFAULT 'staff',
    phone         VARCHAR(20)     NULL,
    is_active     TINYINT(1)      NOT NULL DEFAULT 1,
    created_at    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table: incidents
-- Supporting files stored as LONGBLOB (binary) inside the DB.
-- file_data  — raw bytes of the uploaded file
-- file_name  — original filename (used for Content-Disposition)
-- file_mime  — MIME type (used for Content-Type on download)
-- supporting_file — legacy filesystem path (kept for PDF gen)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incidents (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    incident_id     VARCHAR(30)     NOT NULL,
    date            DATE            NOT NULL,
    time            TIME            NOT NULL,
    location        VARCHAR(255)    NOT NULL,
    cause           VARCHAR(255)    NOT NULL,
    description     LONGTEXT        NOT NULL,

    -- BLOB storage for uploaded supporting documents
    file_data       LONGBLOB        NULL COMMENT 'Binary content of the supporting file',
    file_name       VARCHAR(255)    NULL COMMENT 'Original filename for download',
    file_mime       VARCHAR(100)    NULL COMMENT 'MIME type of the stored file',

    -- Legacy filesystem path (used by PDF generator)
    supporting_file VARCHAR(255)    NULL,
    pdf_file        VARCHAR(255)    NULL,

    status          ENUM('Pending','In Progress','Solved') NOT NULL DEFAULT 'Pending',
    reported_by     INT UNSIGNED    NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_incident_id (incident_id),
    CONSTRAINT fk_incident_reported_by
        FOREIGN KEY (reported_by) REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
