# Steam Password Changer

[![Python: versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)]()
[![GitHub](https://img.shields.io/github/license/semetronix/SteamChangePassword)](https://github.com/semetronix/SteamChangePassword)
[![GitHub stars](https://img.shields.io/github/stars/semetronix/SteamChangePassword)](https://github.com/semetronix/SteamChangePassword/stargazers)

## Description

Script for batch changing Steam account passwords. Works only with accounts that have Steam Guard Mobile Authenticator enabled.

## Requirements

- Python 3.9 - 3.12 (Python 3.13+ is not supported)
- Steam accounts with Steam Guard Mobile Authenticator
- `.maFile` files for each account (exported from SDA or similar tools)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/semetronix/SteamChangePassword.git
cd SteamChangePassword
```

2. Create virtual environment:
```bash
python -m venv .venv
```

3. Activate virtual environment:

**Windows (PowerShell):**
```powershell
.venv\Scripts\activate
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
pip install pysteamlib==1.0.1
```

## Configuration

### 1. Create `logpass.txt` file

Create a file `logpass.txt` in the project root with the following format:

```
login1:old_password1:new_password1
login2:old_password2:new_password2
login3:old_password3:new_password3
```

Each line contains:
- `login` - Steam account login
- `old_password` - current password
- `new_password` - new password to set

### 2. Add maFile files

Create a `maFile/` folder in the project root and add `.maFile` files for each account.

File naming format: `{login}.maFile`

Example:
```
maFile/
  login1.maFile
  login2.maFile
  login3.maFile
```

`.maFile` must contain the following fields:
```json
{
  "shared_secret": "...",
  "identity_secret": "...",
  "device_id": "android:...",
  "Session": {
    "SteamID": "76561198000000000"
  }
}
```

You can export `.maFile` from:
- Steam Desktop Authenticator (SDA)
- Other Steam Guard management tools

### 3. Configure delays (optional)

In `main.py` you can adjust delays between account processing:

```python
MIN_DELAY = 30  # Minimum delay in seconds
MAX_DELAY = 60  # Maximum delay in seconds
```

## Usage

Run the script:

```bash
python main.py
```

The script will:
1. Load accounts from `logpass.txt`
2. Load corresponding `.maFile` for each account
3. Change passwords one by one with random delays
4. Save results to `results.txt`
5. Write logs to `password_change.log`

## Output

### results.txt

After completion, `results.txt` will contain:

```
login1:new_password1:SUCCESS
login2:new_password2:FAILED
login3:new_password3:SUCCESS
```

### password_change.log

Detailed log of all operations with timestamps.

## Programmatic Usage

You can also use the library in your own code:

```python
import asyncio
from steampassword.chpassword import SteamPasswordChange
from steampassword.steam import CustomSteam

async def main():
    steam = CustomSteam(
        login='your_login',
        password='your_password',
        shared_secret='your_shared_secret',
        identity_secret='your_identity_secret',
        device_id='android:your_device_id',
        steamid=76561198000000000,
    )

    changer = SteamPasswordChange(steam)
    await changer.change('new_password')

asyncio.run(main())
```

## Troubleshooting

### ModuleNotFoundError: No module named 'steamlib.api'

Make sure you installed the correct package:
```bash
pip install pysteamlib==1.0.1
```

### lxml build errors

Use Python 3.12 or lower. Python 3.13+ is not supported due to dependency issues.

### Password change failed

- Verify that `.maFile` contains correct `shared_secret` and `identity_secret`
- Check that the account has Steam Guard Mobile Authenticator enabled
- Ensure old password is correct

## Author

[semetronix](https://github.com/semetronix)

## License

MIT