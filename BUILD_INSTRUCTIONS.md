# Binance Futures Bot - Build Instructions

## Creating EXE from Source

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Build EXE

```bash
pyinstaller build_exe.spec
```

The EXE will be created in the `dist/` folder as `BinanceFuturesBot.exe`

### 3. Update Mechanism

**IMPORTANT:** Before building, update the repository information in `updater.py`:

```python
# Line 22 in updater.py
def __init__(self, repo_owner="YOUR_GITHUB_USERNAME", repo_name="YOUR_REPO_NAME", branch="main", current_version="1.0.0", lang='tr'):
```

Replace:
- `YOUR_GITHUB_USERNAME` with your GitHub username
- `YOUR_REPO_NAME` with your repository name
- `main` with your default branch if different

### 4. How Update Works

The bot will:
1. Check for updates on startup (after 3 seconds delay)
2. Manually check when user clicks "Update" button
3. Compare local commit hash with remote commit hash
4. Download latest version if update is available
5. Extract and replace files automatically

### 5. GitHub Repository Setup

After uploading to GitHub, ensure:
- Public repository (or accessible)
- Main branch exists
- Files are properly committed

### 6. Version Management

To update the bot version:
1. Make changes to your code
2. Commit and push to GitHub
3. Users will automatically be notified on next startup
4. They can click "Update" to download latest version

## Notes

- The updater works for both Python source and compiled EXE
- Update downloads the entire repository ZIP and extracts files
- Local files are backed up before updating
- The bot must be closed during update process

