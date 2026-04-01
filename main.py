import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(filename):
    script_path = os.path.join(BASE_DIR, filename)
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=BASE_DIR,
    )
    if result.returncode != 0:
        print(f"\n[!] Script '{filename}' exited with code {result.returncode}.")


def show_testing_instructions():
    print("\n" + "=" * 55)
    print("      HOW TO USE THE MANUAL TESTING FORM")
    print("=" * 55)
    print("\n  Step 1 - Open a terminal and navigate to this folder:")
    print(f'\n           cd "{BASE_DIR}"\n')
    print("  Step 2 - Start a local server by running:")
    print("\n           python -m http.server 8765\n")
    print("  Step 3 - Open your browser and go to:")
    print("\n           http://localhost:8765/testing/web/index.html\n")
    print("  Step 4 - Fill in the fields and click Search:")
    print("           PDF File Name  ->  PDF name (e.g. 0931)")
    print("           Table          ->  table name (e.g. Vital Signs)")
    print("           Parameter      ->  field name (e.g. BP)")
    print("\n  Step 5 - When done, go back to the terminal from")
    print("           Step 2 and press Ctrl+C to stop the server.")
    print("=" * 55)


def print_menu():
    print("\n" + "=" * 35)
    print("            OPTIONS")
    print("=" * 35)
    print("  1. Create JSON files")
    print("  2. Create Excel file")
    print("  3. Create CSV files")
    print("  5. Open manual testing form")
    print("  6. Exit")
    print("=" * 35)


def main():
    while True:
        print_menu()
        choice = input("Your choice: ").strip()

        if choice == "1":
            print("\n[>] Running save_JSON_format.py ...\n")
            run_script("save_JSON_format.py")
        elif choice == "2":
            print("\n[>] Running dataframe.py ...\n")
            run_script("dataframe.py")
        elif choice == "3":
            print("\n[>] Running save_raw_csv.py ...\n")
            run_script("save_raw_csv.py")
        elif choice == "5":
            show_testing_instructions()
        elif choice == "6":
            print("\nGoodbye!\n")
            break
        else:
            print("\n[!] Invalid option. Please enter 1, 2, 3, 5, or 6.")


if __name__ == "__main__":
    main()
