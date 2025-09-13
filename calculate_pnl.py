import argparse
import sys
from collections import deque
from typing import Deque, Dict, Tuple
import pandas as pd

def match_lots(lots: Deque[dict], trade_px: float, qty: float, sign: int,pop_left: bool, TOL: float) -> float:
    """
    Consume qty from lots using FIFO/LIFO.
    sign = +1 for (sell vs long) realized calc: (trade_px - entry_px)*q
    sign = -1 for (buy vs short) realized calc: (entry_px - trade_px)*q  (same formula via sign)
    Returns realized pnl; mutates 'lots' and returns leftover qty to caller via remaining variable.
    """
    realized = 0.0
    remaining = qty
    while remaining > TOL and lots:
        lot = lots[0] if pop_left else lots[-1]
        take = min(remaining, lot["qty"])
        realized += sign * (trade_px - lot["price"]) * take
        lot["qty"] -= take
        remaining -= take
        if lot["qty"] <= TOL:
            if pop_left:
                lots.popleft()
            else:
                lots.pop()
    return realized, remaining
def calculate_PnL(input_path,rule='fifo'):
    """

    :param input: Dataframe, trade records, columns:'TIMESTAMP','SYMBOL','BUY_OR_SELL','PRICE','QUANTITY'
    :param output: Dataframe, pnl records,
    :return:
    """
    input=pd.read_csv(input_path)
    #output=pd.DataFrame(columns=['TIMESTAMP','SYMBOL','PNL'])
    # Stable sort within (SYMBOL, TIMESTAMP) while preserving index for re-align
    df_sorted = input.sort_values(["SYMBOL", "TIMESTAMP"], kind="mergesort")
    pnl_sorted = pd.Series(0.0, index=df_sorted.index)
    realized_event = pd.Series(False, index=df_sorted.index)

    # Per-symbol inventory (deques of {"qty": float, "price": float})
    long_lots: Dict[str, Deque[dict]] = {}
    short_lots: Dict[str, Deque[dict]] = {}
    assert rule in ['fifo','lifo'],"rule must be either fifo or lifo"
    pop_left = (rule == "fifo")
    TOL = 1e-12

    realized_rows = []

    for _, row in input.iterrows():
        sym, side, px, qty, ts = row["SYMBOL"], row["BUY_OR_SELL"], float(row["PRICE"]), float(row["QUANTITY"]), row[
            "TIMESTAMP"]
        long_lots.setdefault(sym, deque())
        short_lots.setdefault(sym, deque())

        realized = 0.0
        matched_qty = 0.0
        #BUY or SELL PNL calculation
        if side == "B":
            # Cover shorts first → realized = (short_entry - buy_px)*q  ==  - (buy_px - entry)*q
            r, rem = match_lots(short_lots[sym], px, qty, sign=-1,pop_left=pop_left,TOL=TOL)
            realized += r
            matched_qty += (qty - rem)
            if rem > TOL:  # leftover opens long lot
                long_lots[sym].append({"qty": rem, "price": px})

        else:
            # Consume longs first → realized = (sell_px - long_entry)*q == + (trade_px - entry)*q
            r, rem = match_lots(long_lots[sym], px, qty, sign=1,pop_left=pop_left,TOL=TOL)
            realized += r
            matched_qty += (qty - rem)
            if rem > TOL:  # leftover opens short lot
                short_lots[sym].append({"qty": rem, "price": px})

        if matched_qty > TOL:
            realized_rows.append({"TIMESTAMP": ts, "SYMBOL": sym, "PNL": realized})

    out = pd.DataFrame(realized_rows)
    if not out.empty:
        out = out.sort_values(["SYMBOL", "TIMESTAMP"]).reset_index(drop=True)

    return out

def main():
    parser = argparse.ArgumentParser(
        description="Compute realized PnL with FIFO/LIFO matching (shorts supported). Prints to stdout."
    )
    parser.add_argument("csv", help="Path to trades CSV (TIMESTAMP,SYMBOL,BUY_OR_SELL,PRICE,QUANTITY)")
    parser.add_argument("rule", nargs="?", default="FIFO", help="FIFO or LIFO (default: FIFO)")
    args = parser.parse_args()

    try:
        df_out = calculate_PnL(args.csv, rule=args.rule)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if df_out.empty:
        # Print nothing or a minimal note; choose minimal note for clarity
        print("No realized PnL rows (all trades opened inventory).")
        return

    # Format PNL to exactly two decimals as strings, then print a pretty table
    df_print = df_out.copy()
    df_print["PNL"] = df_print["PNL"].map(lambda v: f"{v:.2f}")
    print(df_print.to_string(index=False))


if __name__=='__main__':
    input=pd.DataFrame([[101,'TFS','B',11,15],[102,'TFS','B',12.5,15],[103,'TFS','S',13,20],[104,'TFS','S',12.75,10]],
                       columns=['TIMESTAMP','SYMBOL','BUY_OR_SELL','PRICE','QUANTITY'])
    # out=calculate_PnL(input,'fifo')

    main()