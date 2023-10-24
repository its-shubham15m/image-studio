import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO
import easyocr
import tempfile
from fpdf import FPDF
from PIL import Image as PILImage
import os
import base64

st.set_page_config(
    page_title="ImageStudio",
    page_icon="picture.png",
    layout="wide"
)

# Set the Streamlit app title
st.title("Image Studio - Versatile Image Processing Tool")

st.markdown(
    f"""
    <style>
    .stApp {{
        background: url("https://unsplash.com/photos/6JffLQi_XqY/download?ixid=M3wxMjA3fDB8MXxzZWFyY2h8Mjh8fGJvb2tzaGVsZnxlbnwwfHx8fDE2OTgxMzkzODB8MA&force=true");
        background-size: cover;
        background-position: center;
    }}

    .thumbnail-container {{
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    }}

    .thumbnail-image {{
        width: 100%;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.write("### Welcome to Our Image Studio!")
st.write("Unleash the Power of Your Images! Transform your photos with our versatile Image Processing Tool. Remove backgrounds, extract text, resize, mirror, rotate, create PDFs, or compress - we've got it all.")
st.write("Elevate your images to the next level. Give it a try!")

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB


# Function to download the fixed image
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im


# Function to extract text using EasyOCR
def extract_text(image_path):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image_path)
    extracted_text = " ".join([result[1] for result in results])
    return extracted_text


# Function to resize an image
def resize_image(image, width, height):
    resized_image = image.resize((width, height))
    return resized_image


# Function to mirror and rotate an image
def mirror_and_rotate_image(image, flip, rotation):
    mirrored_rotated = image.transpose(flip).rotate(rotation)
    return mirrored_rotated


# Function to convert image to PDF
def convert_to_pdf(image, label):
    pdf = FPDF()
    pdf.add_page()

    # Convert the image to RGB mode if it's not
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Save the image to a temporary file in a supported format (e.g., PNG)
    temp_image_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_image_file.close()  # Close the file
    image.save(temp_image_file.name, "PNG")

    # Add the image to the PDF
    pdf.image(temp_image_file.name, w=190)

    # Generate the PDF file
    pdf_temp_file_name = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(pdf_temp_file_name)

    return pdf_temp_file_name



# Function to compress an image
def compress_image(image, quality):
    img_buffer = BytesIO()
    image.save(img_buffer, format="JPEG", quality=quality)
    img_buffer.seek(0)
    return img_buffer


st.write("## Upload and Process :gear:")

# Allow users to upload multiple images
my_uploads = st.file_uploader("Upload one or more images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if my_uploads:
    for idx, my_upload in enumerate(my_uploads):
        if my_upload.size > MAX_FILE_SIZE:
            st.error(f"Image {idx + 1}: The uploaded file is too large. Please upload an image smaller than 15MB.")
        else:
            col1, col2 = st.columns(2)  # Create two equal-sized columns

            # Load and process the image in col1
            col1.write(f"Image {idx + 1}: Original Image")
            image = Image.open(my_upload)
            col1.image(image, caption="Original Image :file:")
            col1.markdown("\n")


            # Define a function to create download links
            def create_download_links(image_data, image_format, label):
                file_data = convert_image(image_data)
                href = f'<a href="data:application/octet-stream;base64,{base64.b64encode(file_data).decode()}" download="{label}.{image_format}">Download {label}</a>'
                return href


            # Dropdown for processing options and results in col2
            with col2:
                processing_option = st.selectbox(f"Image {idx + 1}: Choose Processing Option",
                                                 ["Background Remover", "Text Extractor", "Resize Image",
                                                  "Mirror and Rotate Image", "Convert to PDF", "Compress Images"])

                if processing_option == "Background Remover":
                    # Remove background and display
                    fixed = remove(image)
                    st.image(fixed, caption="Fixed Image :background_removed")
                    st.markdown("\n")
                    st.markdown(create_download_links(fixed, "png", f"Download Fixed Image {idx + 1}"))

                elif processing_option == "Text Extractor":
                    # Save the fixed image as a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                        temp_file_path = temp_file.name
                        fixed = remove(image)
                        fixed.save(temp_file_path)

                    # Extract text using EasyOCR
                    extracted_text = extract_text(temp_file_path)
                    st.write(f"Image {idx + 1}: Extracted Text")
                    st.write(extracted_text)

                elif processing_option == "Resize Image":
                    st.write(f"Image {idx + 1}: Resize Image")
                    width = st.number_input("Enter Width (pixels):", min_value=1)
                    height = st.number_input("Enter Height (pixels):", min_value=1)
                    if st.button("Resize"):
                        resized = resize_image(image, width, height)
                        st.image(resized, caption=f"Resized Image ({width}x{height})")
                        st.markdown("\n")
                        st.markdown(create_download_links(resized, "png", f"Download Resized Image {idx + 1}"))

                elif processing_option == "Mirror and Rotate Image":
                    st.write(f"Image {idx + 1}: Mirror And Rotate Image Online")
                    flip = st.selectbox(f"Image {idx + 1}: Mirror:", ["None", "Vertical", "Horizontal"])
                    rotation = st.selectbox(f"Image {idx + 1}: Rotate:", ["0°", "90°", "180°", "270°"])

                    # Mapping for flip and rotation
                    flip_mapping = {"None": PILImage.FLIP_TOP_BOTTOM, "Vertical": PILImage.FLIP_LEFT_RIGHT,
                                    "Horizontal": PILImage.FLIP_TOP_BOTTOM}
                    rotation_mapping = {"0°": 0, "90°": 90, "180°": 180, "270°": 270}

                    if st.button(f"Image {idx + 1}: Apply Mirror and Rotate"):
                        flip_code = flip_mapping[flip]
                        rotation_angle = rotation_mapping[rotation]
                        mirrored_rotated = mirror_and_rotate_image(image, flip_code, rotation_angle)
                        st.image(mirrored_rotated, caption=f"Image {idx + 1}: Mirrored and Rotated Image")
                        st.markdown("\n")
                        mirrored_rotated_temp_file_name = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                        mirrored_rotated.save(mirrored_rotated_temp_file_name)
                        st.markdown(create_download_links(mirrored_rotated, "png",
                                                          f"Download Mirrored and Rotated Image {idx + 1}"))

                elif processing_option == "Convert to PDF":
                    st.write(f"Image {idx + 1}: Convert to PDF")
                    if st.button(f"Convert Image {idx + 1} to PDF"):
                        # Convert the image to PDF and display the PDF
                        pdf_temp_file_name = convert_to_pdf(image, f"image{idx + 1}")
                        with open(pdf_temp_file_name, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                            st.markdown(
                                f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}" class="contact-button" download="image{idx + 1}.pdf">Download PDF</a>',
                                unsafe_allow_html=True)

                elif processing_option == "Compress Images":
                    st.write(f"Image {idx + 1}: Compress Images")
                    quality = st.slider(f"Image {idx + 1}: Select Quality (0-100):", min_value=0, max_value=100,
                                        value=80, step=1)
                    if st.button(f"Compress Image {idx + 1}"):
                        # Compress the image and display it
                        compressed = compress_image(image, quality)
                        st.image(compressed, caption=f"Image {idx + 1}: Compressed Image (Quality: {quality})")
                        st.markdown(f"Size of Compressed Image: {len(compressed.getvalue()) / 1024:.2f} KB")
                        st.markdown(create_download_links(compressed, "jpg", f"Download Compressed Image {idx + 1}"))

                elif processing_option == "Cropping Tool":
                    st.write(f"Image {idx + 1}: Cropping Tool")
                    st.markdown(
                        f"Use the sliders to select the area you want to crop. Click 'Crop' to apply the cropping for Image {idx + 1}.")

                    # Initialize the cropping margins
                    crop_margin_key = f"crop_margins_image_{idx}"
                    if crop_margin_key not in st.session_state:
                        st.session_state[crop_margin_key] = (0, 0, image.width, image.height)

                    left, top, right, bottom = st.slider(f"Image {idx + 1}: Left Margin (pixels)", 0, image.width,
                                                         st.session_state[crop_margin_key][0], 1), st.slider(
                        f"Image {idx + 1}: Top Margin (pixels)", 0, image.height, st.session_state[crop_margin_key][1],
                        1), st.slider(f"Image {idx + 1}: Right Margin (pixels)", 0, image.width,
                                      st.session_state[crop_margin_key][2], 1), st.slider(
                        f"Image {idx + 1}: Bottom Margin (pixels)", 0, image.height,
                        st.session_state[crop_margin_key][3], 1)

# Section for merging images into a single PDF
st.write("## Merge Images into PDF :page_facing_up:")

# Allow users to select multiple images to merge into a PDF
pdf_images = st.file_uploader("Select multiple images to merge into a PDF", type=["png", "jpg", "jpeg"],
                              accept_multiple_files=True)

if pdf_images:
    # Convert selected images to PDF
    pdf = FPDF()
    pdf_temp_files = []

    for idx, pdf_image in enumerate(pdf_images):
        image = Image.open(pdf_image)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
            image.save(temp_image.name)
            pdf_temp_files.append(temp_image.name)
            pdf.add_page()
            pdf.image(temp_image.name, w=190)

    pdf_temp_file_name = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(pdf_temp_file_name)

    # Display the merged PDF
    with open(pdf_temp_file_name, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        st.markdown(
            f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}" class="contact-button" download="merged_images.pdf">Download Merged PDF</a>',
            unsafe_allow_html=True)

    # Close and remove temporary image and PDF files
    for temp_file in pdf_temp_files:
        os.remove(temp_file)
    os.remove(pdf_temp_file_name)

# Define the CSS style for the button
st.markdown(
    """
    <style>
    .contact-button {
        background-color: #262730;
        color: white !important;
        padding: 5px 10px;
        text-align: center;
        text-decoration: none !important;
        display: inline-block;
        font-size: 18px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add a footer
st.markdown("Made with ❤️ by **Shubham Gupta**")
