import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import logging
import os
from typing import Dict
from archive_engines.orchestration.ontology import global_registry

logger = logging.getLogger(__name__)

class UOD_IngestionEngine:
    """
    Module 3: INGESTION ENGINE
    Validates CSV/JSON against Global Ontology and outputs Apache Parquet.
    """
    def __init__(self, output_dir: str = "./data/parquet_store"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def ingest_dataframe(self, df: pd.DataFrame, object_type: str, mapping: Dict[str, str]):
        """
        mapping: { csv_column_name: ontology_property_name }
        """
        logger.info(f"Ingesting {object_type} with {len(df)} rows.")
        
        # 1. Map columns to ontology
        mapped_df = df.rename(columns=mapping)
        
        # 2. Drop unmapped columns (Core Principle: strictly typed)
        valid_cols = [col for col in mapped_df.columns if global_registry.get(col)]
        dropped = set(mapped_df.columns) - set(valid_cols)
        if dropped:
            logger.warning(f"Dropping unmapped columns: {dropped}")
        
        final_df = mapped_df[valid_cols].copy()
        
        # 3. Validate EVERY row (Reject invalid data early)
        for col in valid_cols:
            prop = global_registry.get(col)
            # This is a vectorized validation for performance
            if prop.data_type == "float":
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
            elif prop.data_type == "int":
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce').astype('Int64')
            elif prop.data_type == "datetime":
                final_df[col] = pd.to_datetime(final_df[col], errors='coerce')

            # Fail if any nulls were introduced by failed conversion
            if final_df[col].isnull().any():
                failed_count = final_df[col].isnull().sum()
                raise ValueError(f"Validation Failure: {failed_count} rows in '{col}' do not conform to type '{prop.data_type}'. Computation rejected.")

        # 4. Save to Parquet
        output_path = os.path.join(self.output_dir, f"{object_type}.parquet")
        table = pa.Table.from_pandas(final_df)
        pq.write_table(table, output_path)
        
        logger.info(f"Successfully ingested {object_type} to {output_path}")
        return output_path

    def ingest_file(self, file_path: str, object_type: str, mapping: Dict[str, str]):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext == '.json':
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        return self.ingest_dataframe(df, object_type, mapping)

global_uod_ingestion = UOD_IngestionEngine()
