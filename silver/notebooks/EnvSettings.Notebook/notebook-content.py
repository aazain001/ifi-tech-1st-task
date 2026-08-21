# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # EnvSettings
# Resolves every environment-specific value (lakehouse IDs, control DB name, timezone,
# batch-size limits) from the `VL_PlatformConfig` variable library.
#
# This notebook is never run standalone - it is pulled in via `%run /EnvSettings` at the
# top of any notebook that needs environment config (see DeltaLakeFunctions, CommonTransforms,
# L1Transform-Generic-Fabric). Adding a variable here makes it available to every consumer
# notebook automatically; you do not need to edit each notebook individually.
#
# Do not hardcode a workspace ID, lakehouse ID, or connection value anywhere below this
# line - if a new environment-specific value is needed, add it to VL_PlatformConfig first
# and reference it from here.

# CELL ********************

import notebookutils

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Pull the active value set for this workspace (Dev/Test/Prod resolves automatically -
# Fabric tracks which value set is active per workspace, this code never needs to know which one)
vl = notebookutils.variableLibrary.getLibrary("VL_PlatformConfig")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# --- Lakehouse item references ---
# Stored in the library as ItemReference (workspaceId + itemId), not by name, so we
# never depend on lakehouse display names matching across environments.

bronzeWorkspaceId = vl.BronzeLakehouse["workspaceId"]
bronzeLakehouseId = vl.BronzeLakehouse["itemId"]

silverWorkspaceId = vl.SilverLakehouse["workspaceId"]
silverLakehouseId = vl.SilverLakehouse["itemId"]

goldWorkspaceId = vl.GoldLakehouse["workspaceId"]
goldLakehouseId = vl.GoldLakehouse["itemId"]

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# --- Pre-built OneLake ABFS paths ---
# abfss://<workspaceId>@onelake.dfs.fabric.microsoft.com/<lakehouseId> is a deterministic
# URI - we can build it straight from the IDs above with zero extra API calls, and it works
# identically in Dev, Test, and Prod because the IDs come from the active value set.

bronzeAbfsPath = f"abfss://{bronzeWorkspaceId}@onelake.dfs.fabric.microsoft.com/{bronzeLakehouseId}"
silverAbfsPath = f"abfss://{silverWorkspaceId}@onelake.dfs.fabric.microsoft.com/{silverLakehouseId}"
goldAbfsPath = f"abfss://{goldWorkspaceId}@onelake.dfs.fabric.microsoft.com/{goldLakehouseId}"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# --- Control DB / ELT config ---

controlDatabaseName = vl.ControlDatabaseName
timeZone = vl.TimeZone
maxIngestInstance = vl.MaxIngestInstance
maxTransformInstance = vl.MaxTransformInstance

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Uncomment to sanity-check what this workspace resolved to. Leave commented in committed code -
# this is a manual debugging aid, not something that should run on every pipeline execution.

# print(f"bronzeAbfsPath = {bronzeAbfsPath}")
# print(f"silverAbfsPath = {silverAbfsPath}")
# print(f"goldAbfsPath = {goldAbfsPath}")
# print(f"controlDatabaseName = {controlDatabaseName}")
# print(f"timeZone = {timeZone}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
