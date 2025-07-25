import os
import subprocess

def compress_pdf(input_pdf, output_pdf, quality="/ebook"):
    """
    Compress a PDF file using Ghostscript.

    Parameters:
      input_pdf (str): The path to the input PDF file.
      output_pdf (str): The path to the output compressed PDF file.
      quality (str): Ghostscript quality setting.
          Options:
            - /screen: low-resolution output (smallest file, may reduce readability for print)
            - /ebook: medium-resolution output (good balance for on-screen reading)
            - /printer: high-resolution output (larger file size, best for printing)
            - /prepress: highest quality output (largest file size)
    """
    command = [
        'gs',  # Ghostscript command
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS={quality}',  # Using /ebook for smaller file size while keeping text clear
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_pdf}',
        input_pdf
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Successfully compressed: {input_pdf} -> {output_pdf}")
    except subprocess.CalledProcessError as e:
        print(f"Error compressing {input_pdf}: {e}")

def main():
    input_folder = 'input'
    output_folder = 'output'

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all PDF files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            input_pdf_path = os.path.join(input_folder, filename)
            basename = os.path.splitext(filename)[0]
            output_pdf_filename = f"{basename}-compressed.pdf"
            output_pdf_path = os.path.join(output_folder, output_pdf_filename)

            print(f"Compressing: {input_pdf_path} -> {output_pdf_path}")
            # Using /ebook for better compression. Adjust if needed.
            compress_pdf(input_pdf_path, output_pdf_path, quality="/ebook")

if __name__ == "__main__":
    main()
