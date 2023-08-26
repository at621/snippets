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
    in_special_mode = False

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        # Detect start of special paragraph
        if stripped_line.startswith("&&"):
            in_special_mode = True
            stripped_line = stripped_line[2:].strip()  # remove the "&&"

        # Detect end of special paragraph
        if stripped_line.endswith("^^") and in_special_mode:
            in_special_mode = False
            stripped_line = stripped_line[:-2].strip()  # remove the "^^"
            special = True

        # If in special mode, just append to body buffer and continue
        if in_special_mode:
            body_buffer.append(stripped_line)
            continue

        # Detect headings based on our markers
        if stripped_line.startswith("######"):
            level_4_label = stripped_line.replace("######", "").strip()
        elif stripped_line.startswith("#####"):
            level_3_label = stripped_line.replace("#####", "").strip()
            level_4_label = None
        elif stripped_line.startswith("####"):
            level_2_label = stripped_line.replace("####", "").strip()
            level_3_label, level_4_label = None, None
        elif stripped_line.startswith("###"):
            level_1_label = stripped_line.replace("###", "").strip()
            level_2_label, level_3_label, level_4_label = None, None, None
        else:
            body_buffer.append(stripped_line)

        # Empty line or end of special paragraph indicates end of a paragraph
        if (not stripped_line or special) and body_buffer:
            data.append([level_1_label, level_2_label, level_3_label, level_4_label, ' '.join(body_buffer), special])
            body_buffer = []
            special = False

    # Add the last buffered body text if present
    if body_buffer:
        data.append([level_1_label, level_2_label, level_3_label, level_4_label, ' '.join(body_buffer), special])

    return data

pdf_path = "path_to_your_pdf_file.pdf"
text = convert_pdf_to_text(pdf_path)
data = extract_data(text)

# Convert data to Pandas DataFrame
df = pd.DataFrame(data, columns=['Level_1_Label', 'Level_2_Label', 'Level_3_Label', 'Level_4_Label', 'Body', 'Special'])

# Save the DataFrame to a CSV file if needed
df.to_csv('output.csv', index=False)
