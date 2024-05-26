import streamlit as st
import img2pdf
import os

def convert_images_to_pdf(images, output_filename):
    """Converts a list of images to a PDF file."""
    with open(output_filename, "wb") as f:
        f.write(img2pdf.convert(images))

def main():
    """Main function of the Streamlit app."""
    st.title("Image to PDF Converter")

    # File upload
    uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    # Output filename input
    output_filename = st.text_input("Output Filename", value="converted.pdf")

    # Conversion button
    if st.button("Convert to PDF"):
        if uploaded_files:
            # Convert images to PDF
            convert_images_to_pdf(uploaded_files, output_filename)

            # Download button
            with open(output_filename, "rb") as f:
                st.download_button("Download PDF", f, file_name=output_filename)
        else:
            st.error("Please select some images to convert.")

if __name__ == "__main__":
    main()
