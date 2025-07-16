import argparse
import os
from fontTools.ttLib import TTFont
from load_lang import load_language_data  # Assuming this is a separate file you have


def check_font(font_path, languages_data):
    """
    Checks a font for support of multiple languages and returns a detailed report.
    """
    report = {
        "font_path": font_path,
        "status": "success",  # Added status to indicate if font loading was successful
        "errors": [],         # Added errors list for professional error reporting
        "language_reports": {}
    }

    try:
        font = TTFont(font_path)
    except Exception as e:
        report["status"] = "error"
        report["errors"].append(f"Failed to load font: {e}")
        return report

    font_characters = font.getBestCmap()

    for lang_name, required_chars in languages_data.items():
        missing_characters = []
        for char_code in required_chars:
            if char_code not in font_characters:
                missing_characters.append(hex(char_code))

        lang_report = {
            "language": lang_name,
            "supported": not bool(missing_characters),
            "required_count": len(required_chars),
            "missing_count": len(missing_characters),
            "missing_characters": missing_characters
        }
        report["language_reports"][lang_name] = lang_report
    return report


def display_report(report):
    """
    Prints a detailed font check report to the console in a clean, professional format.
    """
    print(f"--- {report['font_path']} ---")
    if report["status"] == "error":
        print(f"Status: ❌ Error - {', '.join(report['errors'])}")
    else:
        for lang_name, lang_report in report["language_reports"].items():
            if lang_report["supported"]:
                print(f"  ✅ {lang_name}: Fully supported.")
            else:
                print(
                    f"  ❌ {lang_name}: Missing {lang_report['missing_count']} of {lang_report['required_count']} characters.")
                if lang_report['missing_count'] > 0:
                    # Limit missing characters to the first 20 for console readability
                    display_chars = lang_report['missing_characters'][:20]
                    missing_chars_str = ', '.join(display_chars)
                    if len(lang_report['missing_characters']) > 20:
                        missing_chars_str += " ..."
                    print(f"    Missing: {missing_chars_str}")
    print() # <--- THIS IS THE KEY CHANGE: Add a newline after each report


def save_report(all_reports, output_file):
    """
    Saves all generated reports to a specified file in a clean, professional format.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for report in all_reports:
            f.write(f"--- {report['font_path']} ---\n")
            if report["status"] == "error":
                f.write(f"Status: ❌ Error - {', '.join(report['errors'])}\n")
            else:
                for lang_name, lang_report in report["language_reports"].items():
                    if lang_report["supported"]:
                        f.write(f"  ✅ {lang_name}: Fully supported.\n")
                    else:
                        f.write(f"  ❌ {lang_name}: Missing {lang_report['missing_count']} of {lang_report['required_count']} characters.\n")
                        if lang_report['missing_count'] > 0:
                            # Write all missing characters to the file for full detail
                            missing_chars_str = ', '.join(lang_report['missing_characters'])
                            f.write(f"    Missing: {missing_chars_str}\n")
            f.write("\n")  # Separate reports with a newline for readability


def main():
    parser = argparse.ArgumentParser(description="Check font support for multiple languages.")
    parser.add_argument("path", help="Path to a font file or a folder containing font files.")
    parser.add_argument("-o", "--output", help="Optional: Path to save the full report to a file.")
    args = parser.parse_args()

    lang_data = load_language_data()
    all_reports = []

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        return

    if os.path.isfile(args.path):
        print(f"Processing single file: {args.path}")
        report = check_font(args.path, lang_data)
        all_reports.append(report)
        display_report(report)
    elif os.path.isdir(args.path):
        print(f"Processing folder: {args.path}")
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.lower().endswith((".ttf", ".otf", ".woff", ".woff2")):
                    font_path = os.path.join(root, file)
                    print(f"Checking: {font_path}") # Indicate what's currently being checked
                    report = check_font(font_path, lang_data)
                    all_reports.append(report)
                    display_report(report) # Display report immediately after checking each font
    else:
        print(f"Error: Path '{args.path}' is not a valid file or directory.")
        return

    if args.output and all_reports:
        print(f"\nSaving full report to: {args.output}")
        save_report(all_reports, args.output)
        print("Report saved successfully.")

if __name__ == "__main__":
    main()