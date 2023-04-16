# @classmethod
# def load_file_to_sql(cls, models: Generator, session: sessionmaker = SessionLocal):
#     error_records = []
#     records_to_load = []
#     _loaded_counter = 0
#     with session() as db:
#         logger.info(f"Loading records to SQL")
#         for record in models:
#             records_to_load.append(record)
#             if len(records_to_load) == 50000:
#                 try:
#                     db.add_all(records_to_load)
#                     db.commit()
#                     _loaded_counter += len(records_to_load)
#                 except Exception as e:
#                     error_records.extend(records_to_load)
#                     logger.error(e)
#                 records_to_load = []
#         db.add_all(records_to_load)
#         db.commit()
#         _loaded_counter += len(records_to_load)
#     logger.info(f"Loaded {_loaded_counter} records to SQL successfully")
#     logger.info(f"Loaded {_loaded_counter} records to SQL")