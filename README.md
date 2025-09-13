# PNL_calculate
Compute realized PnL with fifo/lifo matching (shorts supported). Prints to stdout.
# `calculate_pnl.py` — Realized PnL with fifo/lifo (shorts supported)

A tiny command-line tool that reads a trades CSV and prints **realized PnL events** using **fifo** or **lifo** inventory matching.  
- Only prints rows where a trade **matches existing inventory** (pure opening trades are omitted).  
- Supports **shorts** (SELL first → later BUY realizes PnL; BUY first → later SELL realizes PnL).  
- **Output only**, no files written. **PNL is printed with two decimal places**.
## Quick Setup (Linux)
**One-time setup script** (creates `.venv` and installs deps):
```bash
# Option A: run the helper script
bash setup.sh

# Then activate the virtual environment
source .venv/bin/activate
```
```bash
# Option B: manually install in requirements.txt

python3 -m pip install --upgrade pip
python3 -m pip install pandas
python3 -m pip install numpy
```

## Usage
```bash
# fifo (default) or lifo
python3 calculate_pnl.py trades.csv fifo
python3 calculate_pnl.py trades.csv lifo
# or make it executable
chmod +x calculate_pnl.py
./calculate_pnl.py trades.csv fifo
```

### CSV schema (required columns)
`TIMESTAMP,SYMBOL,BUY_OR_SELL,PRICE,QUANTITY`

- `TIMESTAMP` → parseable datetime 
- `SYMBOL` → string (e.g., `CL`, `XYZ`)
- `BUY_OR_SELL` → `B`/`S`
- `PRICE` → positive float
- `QUANTITY` → non-negative float

> Rows with invalid timestamps, non-positive prices, or negative quantities cause a clear error.

## What gets printed?
A table with **only** realized events and exactly these columns:
```
TIMESTAMP | SYMBOL | PNL
```
- **PNL is formatted to two decimals** (e.g., `18.00`, `-8.50`).
- Sorted by `(SYMBOL, TIMESTAMP)` for readability.

## Examples

### 1) SELL first, then BUY covers (lifo or fifo both supported)
**trades.csv**
```csv
TIMESTAMP,SYMBOL,BUY_OR_SELL,PRICE,QUANTITY
101,TFS,B,11,15
102,TFS,B,12.5,15
103,TFS,S,13,20
103,TFS,S,12.75,10
```

**Run (fifo):**
```bash
python3 calculate_pnl.py trades.csv fifo
```

**Output:**
```
 TIMESTAMP SYMBOL   PNL
       103    TFS 32.50
       104    TFS  2.50
```

**Run (fifo):**
```bash
python3 calculate_pnl.py trades.csv lifo
```

**Output:**
```
 TIMESTAMP SYMBOL   PNL
       103    TFS 17.50
       104    TFS 17.50
```


## How PnL is computed
- **SELL vs existing long lot:** `PNL = (sell_price - entry_price) * matched_qty`
- **BUY vs existing short lot:** `PNL = (entry_price - buy_price) * matched_qty`
- Matching order is **fifo** (earliest in) or **lifo** (latest in) based on your argument.
- Any unmatched remainder of a trade becomes a **new lot** (opening inventory) and **doesn’t print** a row.


## Tips
- Make sure the input CSV clean and time-ordered; the tool will sort by `(SYMBOL, TIMESTAMP)` just in case.  


## License
MIT (or your choice). If you’re publishing this repo publicly and want others to use it, include a `LICENSE` file (MIT/Apache-2.0 are common).
