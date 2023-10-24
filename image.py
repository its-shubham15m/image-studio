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

# Define the function to convert an image to PDF
def convert_to_pdf(image, pdf_filename):
    pdf = FPDF()
    pdf.add_page()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
        image.save(temp_image.name)
        pdf.image(temp_image.name, w=190)
        pdf_temp_file_name = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        pdf.output(pdf_temp_file_name)
    return pdf_temp_file_name

# Function to compress an image
def compress_image(image, quality):
    img_buffer = BytesIO()
    image.save(img_buffer, format="JPEG", quality=quality)
    img_buffer.seek(0)
    return img_buffer

# Function to crop an image
def crop_image(image, crop_area):
    cropped = image.crop(crop_area)
    return cropped

# Function to save an uploaded file to a temporary location
def save_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name

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
            col1.download_button(f"Download Original Image", convert_image(image), f"image{idx + 1}.png", "image/png")

            # Dropdown for processing options and results in col2
            with col2:
                processing_option = st.selectbox(f"Image {idx + 1}: Choose Processing Option", ["Background Remover", "Text Extractor", "Resize Image", "Mirror and Rotate Image", "Convert to PDF", "Compress Images"])

                if processing_option == "Background Remover":
                    # Remove background and display
                    fixed = remove(image)
                    st.image(fixed, caption="Fixed Image :background_removed")
                    st.markdown("\n")
                    st.download_button(f"Download Fixed Image", convert_image(fixed), f"image{idx + 1}-fixed.png", "image/png")

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
                        st.download_button(f"Download Resized Image", convert_image(resized), f"image{idx + 1}-resized.png", "image/png")

                elif processing_option == "Mirror and Rotate Image":
                    col2.write(f"Image {idx + 1}: Mirror And Rotate Image Online")
                    flip = st.selectbox(f"Image {idx + 1}: Mirror:", ["None", "Vertical", "Horizontal"])
                    rotation = st.selectbox(f"Image {idx + 1}: Rotate:", ["0°", "90°", "180°", "270°"])

                    # Mapping for flip and rotation
                    flip_mapping = {"None": PILImage.FLIP_TOP_BOTTOM, "Vertical": PILImage.FLIP_LEFT_RIGHT, "Horizontal": PILImage.FLIP_TOP_BOTTOM}
                    rotation_mapping = {"0°": 0, "90°": 90, "180°": 180, "270°": 270}

                    if st.button(f"Image {idx + 1}: Apply Mirror and Rotate"):
                        flip_code = flip_mapping[flip]
                        rotation_angle = rotation_mapping[rotation]
                        mirrored_rotated = mirror_and_rotate_image(image, flip_code, rotation_angle)
                        st.image(mirrored_rotated, caption=f"Image {idx + 1}: Mirrored and Rotated Image")
                        st.markdown("\n")
                        mirrored_rotated_temp_file_name = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                        mirrored_rotated.save(mirrored_rotated_temp_file_name)
                        st.download_button(f"Download Mirrored and Rotated Image", open(mirrored_rotated_temp_file_name, "rb").read(), f"image{idx + 1}-mirrored-rotated.png", "image/png")

                elif processing_option == "Convert to PDF":
                    def get_binary_file_downloader_html(bin_file, label):
                        with open(bin_file, 'rb') as f:
                            data = f.read()
                        bin_str = base64.b64encode(data).decode()
                        href = f'<a href="data:application/pdf;base64,{bin_str}" class="contact-button" download="{label}">Download {label}</a>'
                        return href


                    st.write("Convert the Image to PDF")
                    st.image(image, caption="Selected Image")
                    if st.button("Convert to PDF"):
                        # Convert the image to PDF and save it to a file
                        pdf_temp_file_name = convert_to_pdf(image, "converted_image.pdf")

                        # Provide a download link for the PDF
                        st.markdown(get_binary_file_downloader_html(pdf_temp_file_name, "PDF"),
                                    unsafe_allow_html=True)


                elif processing_option == "Compress Images":
                    col2.write(f"Image {idx + 1}: Compress Images")

# Section for merging images into a single PDF
st.write("## Merge Images into PDF :page_facing_up:")

# Allow users to select multiple images to merge into a PDF
pdf_images = st.file_uploader("Select multiple images to merge into a PDF", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

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
        st.markdown(f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}" class="contact-button" download="merged_images.pdf">Download Merged PDF</a>', unsafe_allow_html=True)

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