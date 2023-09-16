import os
import fitz
import pandas as pd
import string

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

def sanitize_filename(filename):
    '''Remove or replace characters that are not suitable for filenames.'''
    # Replace unwanted characters with underscores
    sanitized = filename.replace("\n", "_").replace(" ", "_").replace("/", "_").replace("\\", "_")
    # Remove any other characters that might be problematic
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in sanitized if c in valid_chars)
    

def find_figure_label_and_text(page, img_rect):
    '''Search for figure labels near the image using search_terms and capture any text above and below the image.'''
    search_terms = ["Figure", "Fig.", "Fig"]

    # Define a search area for figure label around the image
    margin = 100
    search_rect_label = img_rect + (0, -margin, 0, margin)
    
    figure_label = None
    for term in search_terms:
        for instance in page.search_for(term, clip=search_rect_label):
            label_rect = instance + (0, 0, page.rect.width - instance.x0, instance.y1 - instance.y0)
            label = page.get_text("text", clip=label_rect).strip()
            if label:
                figure_label = label
                break
        if figure_label:
            break

    # Define a search area above and below the image for any text
    search_rect_above = fitz.Rect(0, img_rect.y0 - margin, page.rect.width, img_rect.y0)
    search_rect_below = fitz.Rect(0, img_rect.y1, page.rect.width, img_rect.y1 + margin)

    label_above = page.get_text("text", clip=search_rect_above).strip()
    label_below = page.get_text("text", clip=search_rect_below).strip()

    return figure_label, label_above, label_below

def extract_images_with_labels_from_pdf_updated(pdf_path, img_folder):
    pdf_document = fitz.open(pdf_path)

    # Create an empty DataFrame
    df = pd.DataFrame(columns=["Page Number", "Figure Name", "File Name", "File Size (bytes)", "Text Above", "Text Below"])

    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        img_list = page.get_images(full=True)

        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # Check if "rect" is present in base_image dictionary
            if "rect" in base_image:
                img_rect = fitz.Rect(base_image["rect"])
            else:
                img_rect = page.get_image_rects(xref)[0]  # Use this method to get the image's bounding box

            # Find figure label and text above & below the image
            figure_label, text_above, text_below = find_figure_label_and_text(page, img_rect)

            if figure_label:
                sanitized_label = sanitize_filename(figure_label)
                img_filename = f"{img_folder}/{sanitized_label}.png"
            else:
                img_filename = f"{img_folder}/page_{page_number + 1}_img_{img_index + 1}.png"

            with open(img_filename, "wb") as image_file:
                image_file.write(image_bytes)

            # Get the file size
            file_size = os.path.getsize(img_filename)

            # Append to the DataFrame
            new_row = pd.DataFrame({
                "Page Number": [page_number + 1],
                "Figure Name": [figure_label if figure_label else None],
                "File Name": [img_filename],
                "File Size (bytes)": [file_size],
                "Text Above": [text_above],
                "Text Below": [text_below]
            })
            df = pd.concat([df, new_row], ignore_index=True)

    pdf_document.close()
    return df


pdf_path = "EBA Report on the 2021 Credit Risk Benchmarking Exercise.pdf"
img_folder = "images"
df = extract_images_with_labels_from_pdf_updated(pdf_path, img_folder)

idx = df['File Size (bytes)'] == 10861

df[-idx].sample(30)
