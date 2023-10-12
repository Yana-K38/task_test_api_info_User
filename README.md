# task_test_api_info_User

uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
$ docker compose up --build
python src/data/load_sql.py