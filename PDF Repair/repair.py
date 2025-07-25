import fitz  # PyMuPDF
import pikepdf
import os
import subprocess

# Folder paths
INPUT_FOLDER = "originals"
OUTPUT_FOLDER = "fixed"
LOG_FILE = "repair_log.txt"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def repair_pdf(input_pdf, output_pdf):
    try:
        print(f"Processing: {input_pdf}")

        # Step 1: Try opening with pikepdf first (fixes structure issues)
        try:
            with pikepdf.open(input_pdf) as pdf:
                recovered_pdf = os.path.join(OUTPUT_FOLDER, "temp_recovered.pdf")
                pdf.save(recovered_pdf)
            input_pdf = recovered_pdf  # Use the recovered file for further processing
        except Exception as e:
            print(f"Skipping {input_pdf}: Cannot open with pikepdf - {e}")
            with open(LOG_FILE, "a") as log:
                log.write(f"{input_pdf}: Cannot open with pikepdf - {e}\n")
            return False

        # Step 2: Open with PyMuPDF (fitz)
        repaired_pdf = fitz.open()
        damaged_pdf = fitz.open(input_pdf)

        if len(damaged_pdf) == 0:
            print(f"Skipping {input_pdf}: No pages found.")
            with open(LOG_FILE, "a") as log:
                log.write(f"{input_pdf}: No pages found\n")
            return False

        for page_num in range(len(damaged_pdf)):
            repaired_pdf.insert_pdf(damaged_pdf, from_page=page_num, to_page=page_num)

        temp_pdf = os.path.join(OUTPUT_FOLDER, "temp_repaired.pdf")
        repaired_pdf.save(temp_pdf)
        repaired_pdf.close()
        damaged_pdf.close()

        # Step 3: Optimize with pikepdf
        with pikepdf.open(temp_pdf) as pdf:
            pdf.save(output_pdf, linearize=True)

        os.remove(temp_pdf)
        print(f"✅ Repaired and saved: {output_pdf}")
        return True

    except Exception as e:
        print(f"❌ Error processing {input_pdf}: {e}")
        with open(LOG_FILE, "a") as log:
            log.write(f"{input_pdf}: {e}\n")
        return False

def repair_with_mutool(input_pdf, output_pdf):
    try:
        print(f"🔄 Attempting secondary repair with mutool: {input_pdf}")

        # Ensure mutool is installed and available in PATH
        mutool_output = os.path.join(OUTPUT_FOLDER, os.path.basename(output_pdf))
        subprocess.run(["mutool", "clean", input_pdf, mutool_output], check=True)

        print(f"✅ Successfully repaired using mutool: {mutool_output}")
        return True

    except Exception as e:
        print(f"❌ mutool repair failed for {input_pdf}: {e}")
        with open(LOG_FILE, "a") as log:
            log.write(f"{input_pdf}: mutool repair failed - {e}\n")
        return False

def process_folder():
    pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in the 'originals' folder.")
        return

    for pdf in pdf_files:
        input_pdf = os.path.join(INPUT_FOLDER, pdf)
        output_pdf = os.path.join(OUTPUT_FOLDER, pdf)

        # Primary repair using pikepdf and PyMuPDF
        success = repair_pdf(input_pdf, output_pdf)

        # If primary repair fails, try mutool clean
        if not success:
            repair_with_mutool(input_pdf, output_pdf)

if __name__ == "__main__":
    process_folder()
