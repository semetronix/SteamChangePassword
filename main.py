import asyncio
import json
from steampassword.chpassword import SteamPasswordChange
from steampassword.steam import CustomSteam


async def change_steam_password(login: str, old_password: str, new_password: str, mafile_path: str) -> bool:
    """
    Смена пароля Steam через библиотеку steam-password-change.

    :param login: Логин от Steam
    :param old_password: Текущий пароль
    :param new_password: Новый пароль
    :param mafile_path: Путь к .maFile (JSON с shared_secret, identity_secret, steamid, device_id и т.д.)
    :return: True если успешно, False иначе
    """
    # читаем maFile
    with open(mafile_path, "r", encoding="utf-8") as f:
        mafile = json.load(f)

    # создаём объект Steam с данными из maFile
    steam = CustomSteam(
        login=login,
        password=old_password,
        shared_secret=mafile.get("shared_secret"),
        identity_secret=mafile.get("identity_secret"),
        device_id=mafile.get("device_id"),
        steamid=int(mafile.get("Session", {}).get("SteamID", mafile.get("steamid", 0)))
    )

    changer = SteamPasswordChange(steam)

    try:
        await changer.change(new_password)
        return True
    except Exception as e:
        print(f"Ошибка при смене пароля: {e}")
        return False


if __name__ == "__main__":
    import argparse
    import time
    import os

    parser = argparse.ArgumentParser(description="Batch change Steam passwords")
    parser.add_argument(
        "input",
        nargs="?",  # делает аргумент необязательным
        default="logpass.txt",  # файл по умолчанию
        help="Путь к txt файлу login:old_pass:new_pass (по умолчанию logpass.txt)"
    )
    parser.add_argument("--max-attempts", type=int, default=5, help="Максимум попыток для одного аккаунта")
    parser.add_argument("--attempt-delay", type=int, default=5, help="Пауза (сек) между попытками")
    parser.add_argument("--account-delay", type=int, default=10, help="Пауза (сек) между аккаунтами")
    parser.add_argument("--success-file", default="success.txt")
    parser.add_argument("--failed-file", default="failed.txt")
    args = parser.parse_args()


    success_lines = []
    failed_lines = []

    with open(args.input, "r", encoding="utf-8") as f:
        accounts = [line.strip() for line in f if line.strip()]

    total = len(accounts)
    print(f"Найдено аккаунтов: {total}")

    for idx, line in enumerate(accounts, start=1):
        parts = line.split(":")
        if len(parts) != 3:
            print(f"[{idx}/{total}] Некорректная строка: {line}")
            continue

        login, old_pass, new_pass = parts
        mafile_path = os.path.join("maFiles", f"{login}.maFile")

        if not os.path.exists(mafile_path):
            print(f"[{idx}/{total}] Нет maFile для {login}")
            failed_lines.append(f"{login}:{old_pass}")
            continue

        print(f"[{idx}/{total}] Смена пароля для {login}...")

        success = False
        for attempt in range(1, args.max_attempts + 1):
            print(f"  Попытка {attempt}/{args.max_attempts}...")
            result = asyncio.run(change_steam_password(login, old_pass, new_pass, mafile_path))
            if result:
                print(f"  ✅ Успех: {login}")
                success_lines.append(f"{login}:{new_pass}")
                success = True
                break
            else:
                print(f"  ❌ Ошибка. Ждём {args.attempt_delay} секунд...")
                time.sleep(args.attempt_delay)

        if not success:
            print(f"  Все попытки неудачны: {login}")
            failed_lines.append(f"{login}:{old_pass}")

        # пауза между аккаунтами
        if idx < total:
            print(f"Пауза {args.account_delay} секунд перед следующим аккаунтом...")
            time.sleep(args.account_delay)

    # сохраняем результаты
    with open(args.success_file, "w", encoding="utf-8") as f:
        for line in success_lines:
            f.write(line + "\n")

    with open(args.failed_file, "w", encoding="utf-8") as f:
        for line in failed_lines:
            f.write(line + "\n")

    print(f"\nГотово! Успехов: {len(success_lines)}, провалов: {len(failed_lines)}")
    print(f"Файлы сохранены: {args.success_file}, {args.failed_file}")
