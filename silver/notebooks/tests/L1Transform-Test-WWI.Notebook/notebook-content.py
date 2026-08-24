# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # L1Transform-Test-WWI
# Smoke-tests `L1Transform-Generic-Fabric` using WideWorldImporters sample values, without
# duplicating any of its transform logic. This calls the generic notebook as a job with a
# parameter dict, the same way the Level1 Transform pipeline's Notebook activity does at
# runtime - so a pass here is a reasonable signal the notebook will behave the same way
# when invoked from the pipeline.
#
# To add a test for a different source system, copy this notebook, rename it (e.g.
# `L1Transform-Test-<SourceSystem>`), and change only the `wwiTestParameters` dict below -
# never edit L1Transform-Generic-Fabric itself to add source-specific values.
#
# Not part of the production pipeline. Run manually after changing the generic notebook.

# CELL ********************

wwiTestParameters = {
    "L1TransformInstanceID": 6214,
    "L1TransformID": 84,
    "IngestID": 57,
    "CustomParameters": None,
    "InputRawFileSystem": None,
    "InputRawFileFolder": None,
    "InputRawFile": None,
    "InputRawFileDelimiter": None,
    "InputFileHeaderFlag": None,
    "OutputL1CurateFileSystem": "Tables",
    "OutputL1CuratedFolder": "Application",
    "OutputL1CuratedFile": "PaymentMethods",
    "OutputL1CuratedFileDelimiter": None,
    "OutputL1CuratedFileFormat": None,
    "OutputL1CuratedFileWriteMode": None,
    "OutputDWStagingTable": None,
    "LookupColumns": None,
    "OutputDWTable": "silver.Mirror_Application_PaymentMethods",
    "OutputDWTableWriteMode": "overwrite",
    "ReRunL1TransformFlag": None,
    "WatermarkColName": None,
    "InputRawTable": "WideWorldImporters-mirror.Application.PaymentMethods",
    "DataFromTimestamp": "1900-01-01T00:00:00Z",
    "DataToTimestamp": "2026-04-25T23:53:46Z",
}

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

result = notebookutils.notebook.run(
    "L1Transform-Generic-Fabric",
    3600,
    wwiTestParameters
)

print(result)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
