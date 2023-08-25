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

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        # Empty line indicates end of a paragraph
        if not stripped_line and body_buffer:
            data.append([level_1_label, level_2_label, level_3_label, level_4_label, ' '.join(body_buffer)])
            body_buffer = []
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

    # Add the last buffered body text if present
    if body_buffer:
        data.append([level_1_label, level_2_label, level_3_label, level_4_label, ' '.join(body_buffer)])

    return data

pdf_path = "path_to_your_pdf_file.pdf"
text = convert_pdf_to_text(pdf_path)
data = extract_data(text)

# Convert data to Pandas DataFrame
df = pd.DataFrame(data, columns=['Level_1_Label', 'Level_2_Label', 'Level_3_Label', 'Level_4_Label', 'Body'])

# Save the DataFrame to a CSV file if needed
df.to_csv('output.csv', index=False)
