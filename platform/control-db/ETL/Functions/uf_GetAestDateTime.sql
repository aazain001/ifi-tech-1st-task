CREATE FUNCTION ELT.[uf_GetAestDateTime]()
RETURNS DATETIME
WITH EXECUTE AS CALLER
AS
 BEGIN
    -- Despite the function name (kept for backward compatibility with existing callers),
    -- the timezone is no longer a hardcoded Australian value. It is read from ELT.Config
    -- so a differently-located deployment only needs to update that config row, not this
    -- function.
    DECLARE @timeZone SYSNAME = COALESCE(
        (SELECT TOP (1) [ConfigValue] FROM [ELT].[Config] WHERE [ConfigKey] = 'TimeZone'),
        'UTC'
    );

    RETURN CONVERT(datetime, CONVERT(datetimeoffset, getdate()) AT TIME ZONE @timeZone)
END

GO
