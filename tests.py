import pandas as pd
from pathlib import Path
import tempfile
from calculate_pnl import calculate_pnl

def write_tmp_csv(rows, tmp_path: Path):
    df = pd.DataFrame(rows)
    p = tmp_path / "trades_sample.csv"
    df.to_csv(p, index=False)
    return p

def test_fifo(tmp_path: Path):
    #fifo
    rows = [
        {"TIMESTAMP":"101","SYMBOL":"TFS","BUY_OR_SELL":"B","PRICE":11,"QUANTITY":15},
        {"TIMESTAMP":"102","SYMBOL":"TFS","BUY_OR_SELL":"B", "PRICE":12.5,"QUANTITY":15},
        {"TIMESTAMP":"103","SYMBOL":"TFS","BUY_OR_SELL":"S", "PRICE":13,"QUANTITY":20},
        {"TIMESTAMP": "104", "SYMBOL": "TFS", "BUY_OR_SELL": "S", "PRICE": 12.75, "QUANTITY": 10}
    ]
    csv_path = write_tmp_csv(rows, tmp_path)
    out = calculate_pnl(str(csv_path), rule="fifo")
    assert len(out) == 2
    assert out.iloc[0]["PNL"] == 32.50
    assert out.iloc[1]["PNL"] == 2.50

def test_lifo(tmp_path: Path):
    #lifo
    rows = [
        {"TIMESTAMP": "101", "SYMBOL": "TFS", "BUY_OR_SELL": "B", "PRICE": 11, "QUANTITY": 15},
        {"TIMESTAMP": "102", "SYMBOL": "TFS", "BUY_OR_SELL": "B", "PRICE": 12.5, "QUANTITY": 15},
        {"TIMESTAMP": "103", "SYMBOL": "TFS", "BUY_OR_SELL": "S", "PRICE": 13, "QUANTITY": 20},
        {"TIMESTAMP": "104", "SYMBOL": "TFS", "BUY_OR_SELL": "S", "PRICE": 12.75, "QUANTITY": 10}
    ]
    csv_path = write_tmp_csv(rows, tmp_path)
    out = calculate_pnl(str(csv_path), rule="lifo")
    assert len(out) == 2
    assert out.iloc[0]["PNL"] == 17.50
    assert out.iloc[0]["PNL"] == 17.50

