from PIL import Image
import numpy as np
import cv2

# -------- LSB Decryption -------- #
def try_lsb(image_path):
    try:
        img = Image.open(image_path)
        binary_message = ""
        stop_marker = "#####"

        for pixel in img.getdata():
            for channel in pixel[:3]:  # R, G, B only
                binary_message += str(channel & 1)

        chars = [chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)]
        message = ''.join(chars)

        if stop_marker in message:
            return {
                "method": "LSB",
                "message": message.split(stop_marker)[0]
            }

    except Exception as e:
        print("LSB Decryption failed:", e)
    return None

# -------- DCT Decryption -------- #
def try_dct(image_path):
    try:
        stop_marker = "#####"
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (512, 512))

        message = ""
        binary_message = ""
        for i in range(0, 512, 8):
            for j in range(0, 512, 8):
                block = img[i:i+8, j:j+8]
                dct = cv2.dct(np.float32(block))
                coeff = int(dct[4, 3])
                binary_message += str(coeff & 1)

        chars = [chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)]
        message = ''.join(chars)

        if stop_marker in message:
            return {
                "method": "DCT",
                "message": message.split(stop_marker)[0]
            }

    except Exception as e:
        print("DCT Decryption failed:", e)
    return None

# -------- Alpha Channel Decryption -------- #
def try_alpha(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        binary_message = ""
        stop_marker = "#####"

        for pixel in img.getdata():
            alpha = pixel[3]
            binary_message += str(alpha & 1)

        chars = [chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)]
        message = ''.join(chars)

        if stop_marker in message:
            return {
                "method": "Alpha Channel",
                "message": message.split(stop_marker)[0]
            }

    except Exception as e:
        print("Alpha Channel Decryption failed:", e)
    return None

# -------- Stego Detection Stub -------- #
def is_steganography(image_path):
    # Placeholder for your AI model
    return True  # Assume every image is stego for now

# -------- Classifier and Decryption -------- #
def classify_and_decrypt(image_path):
    decryptors = [try_lsb, try_dct, try_alpha]

    for decryptor in decryptors:
        result = decryptor(image_path)
        if result:
            return {
                "is_stego": True,
                "method": result["method"],
                "plain_text": result["message"]
            }

    return {
        "is_stego": True,
        "method": "unknown",
        "plain_text": None
    }

# -------- Main Execution -------- #
def main(image_path):
    if is_steganography(image_path):
        result = classify_and_decrypt(image_path)
        print(result)
    else:
        print({"is_stego": False})

# Example Run
# if __name__ == "__main__":
#     main("lsb_output.png")