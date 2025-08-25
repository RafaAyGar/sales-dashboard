#!/bin/bash
set -e

# 1. Initialisation: load initial data into PostgreSQL if table was empty
python -u data_load_postgres_initial.py

# 2. Recurrent mode: daily update table
python -u data_load_postgres_recurrent.py