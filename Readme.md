How to run edit this project

- activate the venv
    `source env/Scripts/activate`

- karena unicorn diisntal di venv maka run unicorn seperti berikut
    `python -m uvicorn api.main:app --reload`

- create migration from models
    `alembic revision --autogenerate -m "creating a user table"`
- update the latest migrate
    `alembic upgrade head`