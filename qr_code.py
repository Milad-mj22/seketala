import qrcode

def generate_qr(url, filename="qrcode.png"):
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add the URL data
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image
    img.save(filename)
    print(f"QR code saved as {filename}")

# Usage
url_to_encode = "https://seketalamanager.ir/contact_us/cards"
generate_qr(url_to_encode)
