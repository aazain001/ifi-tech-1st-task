# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "cc80a0ab-603d-4df9-bdfc-c35a7e8ab095",
# META       "default_lakehouse_name": "lh_silver",
# META       "default_lakehouse_workspace_id": "8d8d00a7-0e8a-4e3b-8c0e-8dcafac7adec"
# META     }
# META   }
# META }

# CELL ********************

spark.conf.set("spark.native.enabled", "true")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

%run /commonTransforms

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

%run /DeltaLakeFunctions

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Notebook Parameters

# PARAMETERS CELL ********************

L1TransformInstanceID = None
L1TransformID = None
IngestID = None
CustomParameters = None
InputRawFileSystem = None
InputRawFileFolder = None
InputRawFile = None
InputRawFileDelimiter = None
InputFileHeaderFlag = None
OutputL1CurateFileSystem = None
OutputL1CuratedFolder = None
OutputL1CuratedFile = None
OutputL1CuratedFileDelimiter = None
OutputL1CuratedFileFormat = None
OutputL1CuratedFileWriteMode = None
OutputDWStagingTable = None
LookupColumns = None
OutputDWTable = None
OutputDWTableWriteMode = None
ReRunL1TransformFlag = None
WatermarkColName = None
InputRawTable = None
DataFromTimestamp = None
DataToTimestamp = None

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Test values for this transform are NOT stored here. To test this generic notebook
# against a specific source system, use a dedicated test-harness notebook that calls
# notebookutils.notebook.run("L1Transform-Generic-Fabric", <timeout>, {<params>})
# with that source's parameter values - see silver/notebooks/tests/L1Transform-Test-WWI.Notebook
# for a worked example. Keeping any one source system's sample values out of this file
# is what makes it safe to reuse for a different source system without editing this notebook.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Read, cleanse and enrich raw/bronze data

# CELL ********************

#Input is Files
if (
    InputRawFileSystem is not None
    and InputRawFileFolder is not None
    and InputRawFile is not None
    and InputRawTable is None
):
    df = readFile('bronze', InputRawFileSystem, InputRawFileFolder, InputRawFile)
# Input is Mirrored Table
elif (
    InputRawFileSystem is None
    and InputRawFileFolder is None
    and InputRawFile is None
    and InputRawTable is not None
    and "mirror" in InputRawTable.lower()
):
    # Split the table name into database, schema, and table parts
    
    parts = InputRawTable.split(".")
    mirrorDBName, schemaName, tableName = parts[0], parts[1], parts[2]
    mirrorDBWorkspace = notebookutils.runtime.context.get("defaultLakehouseWorkspaceName")
    df = readMirrorDBTable(
        workspaceName=mirrorDBWorkspace,
        mirrorDBName=mirrorDBName,
        schemaName=schemaName,
        tableName=tableName,
        watermarkColumnName=WatermarkColName,
        fromTimeStamp=DataFromTimestamp,
        toTimeStamp=DataToTimestamp
    )

ingestCount = df.count()

ct = CommonTransforms(df)

# Remove duplicates
if LookupColumns is not None:
    df = ct.deDuplicate(LookupColumns.split("|"))
else:
    df = ct.deDuplicate()

# Remove leading and trailing spaces from all string columns
df = ct.trim()

# Replace Null Value with generic values
# Note: ensure CommonTransforms.replaceNull can handle these types/values correctly
df = ct.replaceNull(0)
# Replace string nulls (non-date)
df = ct.replaceNull("NA")
# Replace date-like nulls (YYYY-MM-DD)
df = ct.replaceNull("2020-01-01")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Load standardized/silver data

# CELL ********************

if OutputDWTableWriteMode == 'append' and LookupColumns is not None and ingestCount>0:
    output = upsertDelta(df,OutputDWTable,LookupColumns,WatermarkColName)
    numSourceRows = output["numSourceRows"]
    numTargetRowsInserted = output["numTargetRowsInserted"]
    numTargetRowsUpdated = output["numTargetRowsUpdated"]
    numTargetRowsDeleted = output["numTargetRowsDeleted"]
elif OutputDWTableWriteMode == 'overwrite' and ingestCount>0:
    output = insertDelta (df, OutputDWTable, OutputDWTableWriteMode)
    numSourceRows = ingestCount
    numTargetRowsInserted = output["numOutputRows"]
    numTargetRowsUpdated ="0"
    numTargetRowsDeleted ="0"
else:
    numSourceRows = ingestCount
    numTargetRowsInserted = "0"
    numTargetRowsUpdated ="0"
    numTargetRowsDeleted ="0"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Return Values (to pipeline)

# CELL ********************

import json
notebookutils.notebook.exit(json.dumps({
  "numSourceRows": numSourceRows,
  "numTargetRowsInserted": numTargetRowsInserted,
  "numTargetRowsUpdated": numTargetRowsUpdated,
  "numTargetRowsDeleted": numTargetRowsDeleted
}))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
