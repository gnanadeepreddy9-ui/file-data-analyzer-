import os
import sys
import argparse
from datetime import datetime
from src.analyzer import FileAnalyzer
from src.visualizer import DataVisualizer
from src.cleaner import DataCleaner

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def print_table(df, title: str):
    """Prints a styled table to console."""
    print(f"\n{'='*70}")
    print(f"  {title.upper()}")
    print(f"{'='*70}")
    if df is None or len(df) == 0:
        return

    if HAS_TABULATE:
        print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
    else:
        print(df.to_string(index=False))


def save_text_report(overview, col_details, num_stats, cat_summary, cleaned_summary, output_path="output/analysis_report.txt"):
    """Generates an offline text report for documentation."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("="*75 + "\n")
        f.write("             FILE DATA ANALYZER - AUTOMATED SUMMARY REPORT\n")
        f.write(f"             Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*75 + "\n\n")

        f.write("1. DATASET OVERVIEW\n" + "-"*40 + "\n")
        for k, v in overview.items():
            f.write(f"  * {k:<25}: {v}\n")
        f.write("\n")

        f.write("2. COLUMN SPECIFICATIONS & NULL COUNTS\n" + "-"*40 + "\n")
        f.write(col_details.to_string(index=False) + "\n\n")

        if len(num_stats) > 0:
            f.write("3. NUMERICAL DESCRIPTIVE STATISTICS & OUTLIERS\n" + "-"*40 + "\n")
            f.write(num_stats.to_string(index=False) + "\n\n")

        if len(cat_summary) > 0:
            f.write("4. CATEGORICAL ATTRIBUTES BREAKDOWN\n" + "-"*40 + "\n")
            f.write(cat_summary.to_string(index=False) + "\n\n")

        f.write("5. DATA CLEANING & PREPROCESSING SUMMARY\n" + "-"*40 + "\n")
        for k, v in cleaned_summary.items():
            f.write(f"  * {k}: {v}\n")
        f.write("\n" + "="*75 + "\n")


def main():
    parser = argparse.ArgumentParser(description="File Data Analyzer - Automated Exploratory Data Analysis & Cleaning")
    parser.add_argument("--file", "-f", type=str, help="Path to input data file (.csv, .xlsx, .json, .txt)")
    args = parser.parse_args()

    print("\n" + "#"*70)
    print("       FILE DATA ANALYZER  |  Automated Exploratory Data Analysis")
    print("       Author: Sunkara Gnanadeep Reddy (B.Tech CSE - Data Science)")
    print("#"*70)

    file_path = args.file
    if not file_path:
        default_file = os.path.join("sample_data", "sample_students.csv")
        print(f"\n[?] Enter file path to analyze")
        print(f"    (Press ENTER to use sample dataset: '{default_file}'): ")
        try:
            user_input = input(">> ").strip()
            file_path = user_input if user_input else default_file
        except EOFError:
            file_path = default_file

    if not os.path.exists(file_path):
        print(f"\n[!] Error: File '{file_path}' does not exist. Please check the path.")
        sys.exit(1)

    print(f"\n[*] Processing dataset: {file_path}")

    # 1. Core Analysis
    try:
        analyzer = FileAnalyzer(file_path)
    except Exception as e:
        print(f"[!] Failed to parse file: {e}")
        sys.exit(1)

    overview = analyzer.get_basic_overview()
    print_table(None, "Dataset Overview")
    for k, v in overview.items():
        print(f"  * {k:<22}: {v}")

    col_details = analyzer.get_column_details()
    print_table(col_details, "Column Attributes & Missing Data")

    num_stats = analyzer.get_numerical_statistics()
    if len(num_stats) > 0:
        print_table(num_stats, "Descriptive Numerical Statistics")

    cat_summary = analyzer.get_categorical_summary()
    if len(cat_summary) > 0:
        print_table(cat_summary, "Categorical Features Summary")

    # 2. Automated Visualizations
    print(f"\n{'='*70}")
    print("  GENERATING VISUALIZATIONS")
    print(f"{'='*70}")
    try:
        visualizer = DataVisualizer(analyzer.df)
        plots = visualizer.generate_all_plots()
        if plots:
            for p in plots:
                print(f"  [+] Chart generated: {p}")
        else:
            print("  [-] No applicable numerical columns for plotting.")
    except Exception as e:
        print(f"  [!] Visualization generation skipped: {e}")

    # 3. Data Cleaning & Sanitization
    print(f"\n{'='*70}")
    print("  PERFORMING AUTOMATED DATA CLEANING")
    print(f"{'='*70}")
    cleaner = DataCleaner(analyzer.df)
    dups_removed = cleaner.remove_duplicates()
    imputed = cleaner.impute_missing_values()
    cleaned_path = cleaner.export_cleaned_data()

    print(f"  * Duplicates Removed : {dups_removed}")
    for col, detail in imputed.items():
        print(f"  * Imputation ({col}) : {detail}")
    print(f"  * Sanitized File Saved: {cleaned_path}")

    # 4. Save Comprehensive Report
    clean_summary = {
        "Duplicates Removed": dups_removed,
        "Imputations Applied": imputed if imputed else "None required (No missing data)",
        "Cleaned CSV Export": cleaned_path
    }
    report_file = os.path.join("output", "analysis_report.txt")
    save_text_report(overview, col_details, num_stats, cat_summary, clean_summary, report_file)
    print(f"\n[OK] Complete Analysis Report saved to: {report_file}")
    print("\n" + "#"*70)
    print("       ANALYSIS & PREPROCESSING COMPLETED SUCCESSFULLY!")
    print("#"*70 + "\n")


if __name__ == "__main__":
    main()
