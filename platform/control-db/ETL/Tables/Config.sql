CREATE TABLE [ELT].[Config] (
    [ConfigKey]   VARCHAR (100) NOT NULL,
    [ConfigValue] VARCHAR (200) NOT NULL,
    CONSTRAINT [PK_Config] PRIMARY KEY CLUSTERED ([ConfigKey] ASC)
);
GO
