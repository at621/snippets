import PyPDF2
import pandas as pd

# Convert PDF to Text
def convert_pdf_to_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        text = ""
        for page in range(reader.numPages):
            text += reader.getPage(page).extractText()
    return text

# Extract headings and body
def extract_data(text):
    lines = text.split('\n')
    data = []
    level_1_label, level_2_label, level_3_label, level_4_label = None, None, None, None
    body_buffer = []
    special = False
    collecting_special_paragraph = False

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        # Start collecting for a special paragraph
        if stripped_line.startswith("&&"):
            collecting_special_paragraph = True
            stripped_line = stripped_line[2:].strip()

        # End collecting for a special paragraph
        if stripped_line.endswith("^^"):
            collecting_special_paragraph = False
            stripped_line = stripped_line[:-2].strip()
            special = True

        # Append to the buffer and continue if we're collecting lines for a special paragraph
        if collecting_special_paragraph or special:
            body_buffer.append(stripped_line)
            if not collecting_special_paragraph:
                data.append([level_1_label, level_2_label, level_3_label, level_4_label, ' '.join(body_buffer), special])
                body_buffer = []
                special = False
            continue

        # Empty line indicates end of a paragraph
        if not stripped_line and body_buffer:
            data.append([level_1_label, level_2_label, level_3_label, level_4_label, ' '.join(body_buffer), special])
            body_buffer = []
            continue

        # Detect headings based on our markers
        if stripped_line.startswith("######"):
            level_4_label = stripped_line.replace("######",
