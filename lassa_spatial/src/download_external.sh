#!/usr/bin/env bash
# Re-download the external source files the pipeline reads.
# (GBIF data is fetched directly by fetch_gbif_rodents.py.)
set -euo pipefail
cd "$(dirname "$0")/../data/external"

# Natural Earth admin-1 (boundaries)
curl -sSL -o ne_admin1.zip \
  "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces.zip"
unzip -o -q ne_admin1.zip -d ne_admin1

# WorldPop bottom-up v2.0 admin population tables
curl -sSL -o wpop_admin.zip \
  "https://data.worldpop.org/repo/wopr/NGA/population/v2.0/NGA_population_v2_0_admin.zip"
unzip -o -q wpop_admin.zip -d wpop_admin

# HDX: OPHI subnational MPI (MICS 2021) + Nigeria health facilities
mkdir -p hdx
curl -sSL -o hdx/nga_mpi.csv \
  "https://data.humdata.org/dataset/042c1bf4-2942-475f-8cb2-1fb783f8da91/resource/601f51cd-c46a-4ab2-ba0f-8bef62329ddc/download/nga_mpi.csv"
curl -sSL -o hdx/nga_health.csv \
  "https://data.humdata.org/dataset/3b4a119a-309c-4d3f-900f-18a1f6ca2dfa/resource/4658aa59-0554-4fac-8473-377da4b7a0e9/download/nigeriahealthfacilities.csv"
echo "external data downloaded."
