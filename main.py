import asyncio
import json
import logging
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from steampassword.chpassword import SteamPasswordChange
from steampassword.steam import CustomSteam

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('password_change.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent
LOGPASS_FILE = BASE_DIR / 'logpass.txt'
MAFILES_DIR = BASE_DIR / 'maFile'
RESULTS_FILE = BASE_DIR / 'results.txt'

# Delay settings (in seconds)
MIN_DELAY = 30  # Minimum delay between accounts
MAX_DELAY = 60  # Maximum delay between accounts


@dataclass
class AccountData:
    login: str
    old_password: str
    new_password: str
    shared_secret: Optional[str] = None
    identity_secret: Optional[str] = None
    device_id: Optional[str] = None
    steamid: Optional[int] = None


def load_mafile(login: str) -> dict:
    """Load .maFile for account by login."""
    mafile_path = MAFILES_DIR / f'{login}.maFile'
    if not mafile_path.exists():
        raise FileNotFoundError(f'maFile not found: {mafile_path}')

    with open(mafile_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_logpass_line(line: str) -> Optional[AccountData]:
    """Parse line from logpass.txt."""
    line = line.strip()
    if not line:
        return None

    parts = line.split(':')
    if len(parts) != 3:
        logger.warning(f'Invalid line format: {line}')
        return None

    return AccountData(
        login=parts[0],
        old_password=parts[1],
        new_password=parts[2]
    )


def load_accounts() -> list[AccountData]:
    """Load all accounts from logpass.txt and enrich with maFile data."""
    accounts = []

    with open(LOGPASS_FILE, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            account = parse_logpass_line(line)
            if not account:
                continue

            try:
                mafile_data = load_mafile(account.login)
                account.shared_secret = mafile_data.get('shared_secret')
                account.identity_secret = mafile_data.get('identity_secret')
                account.device_id = mafile_data.get('device_id')

                # Extract steamid from Session
                session = mafile_data.get('Session', {})
                steamid_str = session.get('SteamID')
                if steamid_str:
                    account.steamid = int(steamid_str)

                accounts.append(account)
            except FileNotFoundError as e:
                logger.error(f'Line {line_num}: {e}')
            except json.JSONDecodeError as e:
                logger.error(f'Line {line_num}: Invalid JSON in maFile for {account.login}: {e}')

    return accounts


async def change_password(account: AccountData) -> bool:
    """Change password for single account."""
    try:
        steam = CustomSteam(
            login=account.login,
            password=account.old_password,
            shared_secret=account.shared_secret,
            identity_secret=account.identity_secret,
            device_id=account.device_id,
            steamid=account.steamid,
        )

        changer = SteamPasswordChange(steam)
        await changer.change(account.new_password)
        return True

    except Exception as e:
        logger.error(f'[{account.login}] Error: {e}')
        return False


def save_result(login: str, new_password: str, success: bool):
    """Save result to results file."""
    status = 'SUCCESS' if success else 'FAILED'
    with open(RESULTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{login}:{new_password}:{status}\n')


async def main():
    logger.info('Loading accounts...')
    accounts = load_accounts()
    logger.info(f'Loaded {len(accounts)} accounts')

    if not accounts:
        logger.error('No accounts found!')
        return

    # Clear results file
    RESULTS_FILE.write_text('')

    success_count = 0
    failed_count = 0

    for i, account in enumerate(accounts, 1):
        logger.info(f'[{i}/{len(accounts)}] Processing: {account.login}')

        success = await change_password(account)

        if success:
            success_count += 1
            logger.info(f'[{account.login}] Password changed successfully!')
        else:
            failed_count += 1
            logger.error(f'[{account.login}] Password change failed!')

        save_result(account.login, account.new_password, success)

        # Delay before next account (except for the last one)
        if i < len(accounts):
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            logger.info(f'Waiting {delay} seconds before next account...')
            await asyncio.sleep(delay)

    logger.info('=' * 50)
    logger.info(f'Completed! Success: {success_count}, Failed: {failed_count}')
    logger.info(f'Results saved to: {RESULTS_FILE}')


if __name__ == '__main__':
    asyncio.run(main())