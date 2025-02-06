import fitz

def split_and_landscape_pdf(input_pdf, output_pdf):
    try:
        doc = fitz.open(input_pdf)
        if not doc.is_pdf:
            raise ValueError("Input file is not a PDF.")

        page = doc[0]
        rect = page.rect
        if not (8.4 < rect.width < 8.6 and 10.9 < rect.height < 11.1):
            print("Warning: Input PDF is not standard letter size. Proceeding but results may vary.")

        new_doc = fitz.open()

        for page_num in range(doc.page_count):
            page = doc[page_num]
            width = page.rect.width
            height = page.rect.height

            # Create two NEW landscape pages CORRECTLY
            new_page1 = new_doc.insert_page(new_doc.page_count, width=height, height=width)
            new_page2 = new_doc.insert_page(new_doc.page_count, width=height, height=width)

            # Get the pixmap of the original page
            pix = page.get_pixmap()

            # Define transformation matrices for each half
            mat1 = fitz.Matrix(width / height, 0, 0, (width/2) / height)  # Scale to half width
            mat2 = fitz.Matrix(width / height, 0, 0, (width/2) / height)  # Scale to half width

            # Apply rotation and scaling using the matrix
            new_page1.insert_image(new_page1.rect, image=pix, matrix=mat1, rotate=90)
            new_page2.insert_image(new_page2.rect, image=pix, matrix=mat2, rotate=90)

        new_doc.save(output_pdf)
        print(f"PDF split and converted to landscape: {output_pdf}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
input_pdf_path = "input.pdf"
output_pdf_path = "output.pdf"

split_and_landscape_pdf(input_pdf_path, output_pdf_path)