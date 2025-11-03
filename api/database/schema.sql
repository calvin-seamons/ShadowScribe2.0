-- ShadowScribe 2.0 Database Schema
-- MySQL 8.0+

CREATE DATABASE IF NOT EXISTS shadowscribe 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE shadowscribe;

-- Characters table: stores full character data as JSON
CREATE TABLE IF NOT EXISTS characters (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    race VARCHAR(100),
    character_class VARCHAR(100),
    level INT,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
