-- Post-deployment script. Auto-run on every deploy by the Microsoft.Build.Sql SDK
-- (detected by filename convention - no entry needed in controlDB.sqlproj).
--
-- Seeds ELT.Config with default settings for a fresh environment. Uses MERGE so it is
-- idempotent: re-running this script never overwrites a value someone has since changed
-- for their environment (e.g. a non-Australian deployment changing TimeZone).

MERGE INTO [ELT].[Config] AS target
USING (VALUES
    ('TimeZone', 'AUS Eastern Standard Time')
) AS source ([ConfigKey], [ConfigValue])
ON target.[ConfigKey] = source.[ConfigKey]
WHEN NOT MATCHED BY TARGET THEN
    INSERT ([ConfigKey], [ConfigValue])
    VALUES (source.[ConfigKey], source.[ConfigValue]);
GO
