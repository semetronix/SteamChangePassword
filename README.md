1) Файл с аккаунтами (logpass.txt)

Каждая строка в формате:

login:old_password:new_password

2) maFiles/
В папке maFiles должны находиться .maFile файлы для каждого аккаунта: maFiles/login.maFile


3) Запуск через командную строку:
python main.py logpass.txt --max-attempts 5 --attempt-delay 5 --account-delay 10

Параметры:
input — путь к txt файлу (по умолчанию logpass.txt). 

--max-attempts — максимальное количество попыток для одного аккаунта (по умолчанию 5).

--attempt-delay — пауза между попытками (секунды).

--account-delay — пауза между аккаунтами (секунды).

--success-file — файл для успешных результатов (по умолчанию success.txt).

--failed-file — файл для неудачных (по умолчанию failed.txt).


```bash
Установка
git clone https://github.com/semetronix/SteamChangePassword.git
cd SteamChangePassword
pip install -r requirements.txt