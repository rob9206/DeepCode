# Slingshot Installation Guide for Windows

## Option 1: Clone from GitHub (Recommended)

### Prerequisites
- Git installed (download from https://git-scm.com/download/win)
- Python 3.8+ installed (you have Python 3.14 ✅)

### Step-by-Step Instructions

**1. Open PowerShell**
```powershell
# Press Win+X, select "Windows PowerShell" or "Terminal"
```

**2. Navigate to your desired location**
```powershell
cd C:\Users\dawso
# Or wherever you want the code
```

**3. Clone the repository**
```powershell
git clone https://github.com/rob9206/DeepCode.git
cd DeepCode

# Switch to the slingshot branch
git checkout claude/scaffold-stock-scanner-01XtNFDF42QeQrajhyXeQHTM
```

**4. Navigate to the slingshot folder**
```powershell
cd slingshot
```

**5. Install dependencies**
```powershell
pip install -r requirements.txt
```

**6. Test the installation**
```powershell
# List all themes
python -m slingshot themes

# View AI theme
python -m slingshot themes --theme AI

# Scan top 5 stocks (requires internet)
python -m slingshot scan --top 5
```

### Troubleshooting

**Error: "git is not recognized"**
- Install Git from https://git-scm.com/download/win
- Restart PowerShell after installation

**Error: "pip is not recognized"**
- Add Python to PATH
- Or use: `python -m pip install -r requirements.txt`

**Error: "No module named slingshot"**
- Make sure you're in the `DeepCode/slingshot` folder
- Run `pwd` to check your current directory

### Updating Later

```powershell
cd C:\Users\dawso\DeepCode
git pull origin claude/scaffold-stock-scanner-01XtNFDF42QeQrajhyXeQHTM
cd slingshot
```

---

## What You Get

After installation, you can run:

**Browse themes:**
```powershell
python -m slingshot themes
python -m slingshot themes --theme AI
```

**Scan stocks:**
```powershell
python -m slingshot scan --top 10
python -m slingshot scan --tickers NVDA,AMD,TSLA
python -m slingshot scan --theme Semiconductors
```

**Deep dive:**
```powershell
python -m slingshot ticker NVDA
python -m slingshot ticker MSFT --output msft.json
```

**Get help:**
```powershell
python -m slingshot --help
python -m slingshot scan --help
```
