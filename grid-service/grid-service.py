import os


db_name = os.getenv("DB_NAME")
db_user_name = os.getenv("DB_USER_NAME")
db_password_file = os.getenv("DB_PASSWORD_FILE")

print(f"{db_name=} {db_user_name=} {db_password_file=}")

f = open(db_password_file)
db_password = f.read()
f.close()

print(f"{db_password=}")