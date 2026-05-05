"""
main.py

makes everything happen
"""

from data import load_all_data
from strategies import run_all_strategies
from analysis import analyze_results

def main():
    all_data = load_all_data()
    results = run_all_strategies(all_data)
    analyze_results(results)

if __name__ == "__main__":
    main()