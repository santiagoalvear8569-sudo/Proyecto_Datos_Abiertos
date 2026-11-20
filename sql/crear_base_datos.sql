-- Script re-ejecutable: crea la BD y la tabla solo si no existen.
IF DB_ID('DatosAbiertosDB') IS NULL
    CREATE DATABASE DatosAbiertosDB;
GO
USE DatosAbiertosDB;
GO
IF OBJECT_ID('dbo.RegistrosAPI', 'U') IS NULL
BEGIN
    CREATE TABLE RegistrosAPI (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_api NVARCHAR(100) NOT NULL UNIQUE,   -- id_de_caso
        departamento NVARCHAR(150) NULL,        -- departamento_nom
        municipio NVARCHAR(150) NULL,           -- ciudad_municipio_nom
        edad INT NULL,
        unidad_medida NVARCHAR(10) NULL,        -- 1 = años, 2 = meses, 3 = días
        sexo NVARCHAR(10) NULL,
        estado NVARCHAR(50) NULL,               -- Leve, Moderado, Grave, Fallecido...
        fecha_diagnostico NVARCHAR(50) NULL,
        json_original NVARCHAR(MAX) NULL,
        fecha_captura DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    );
END
GO
-- Si la tabla ya existía de una versión anterior, agrega la columna nueva.
IF COL_LENGTH('dbo.RegistrosAPI', 'unidad_medida') IS NULL
    ALTER TABLE RegistrosAPI ADD unidad_medida NVARCHAR(10) NULL;
GO
