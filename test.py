from PIL import Image
import numpy as np
import cv2

# -------- LSB Encryption -------- #
def encrypt_lsb(image_path, message, output_path):
    img = Image.open(image_path)
    encoded = img.copy()
    width, height = img.size
    message += "#####"
    binary_message = ''.join([format(ord(i), "08b") for i in message])
    data_index = 0

    for y in range(height):
        for x in range(width):
            pixel = list(img.getpixel((x, y)))
            for n in range(3):
                if data_index < len(binary_message):
                    pixel[n] = pixel[n] & ~1 | int(binary_message[data_index])
                    data_index += 1
            encoded.putpixel((x, y), tuple(pixel))
            if data_index >= len(binary_message):
                break
        if data_index >= len(binary_message):
            break

    encoded.save(output_path)

# -------- DCT Encryption -------- #
def encrypt_dct(image_path, message, output_path):
    img = cv2.imread(image_path)
    img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)

    y, cr, cb = cv2.split(img_ycrcb)
    y = cv2.resize(y, (512, 512))  # Resize Y channel for DCT

    message += "#####"
    binary_message = ''.join([format(ord(i), '08b') for i in message])
    data_index = 0

    for i in range(0, 512, 8):
        for j in range(0, 512, 8):
            block = y[i:i+8, j:j+8]
            dct = cv2.dct(np.float32(block))

            if data_index < len(binary_message):
                coeff = round(dct[4, 3])
                coeff = abs(coeff)
                coeff = coeff & ~1 | int(binary_message[data_index])
                dct[4, 3] = float(coeff)
                data_index += 1

            idct = cv2.idct(dct)
            y[i:i+8, j:j+8] = np.uint8(np.clip(idct, 0, 255))

            if data_index >= len(binary_message):
                break
        if data_index >= len(binary_message):
            break

    y = cv2.resize(y, (img.shape[0], img.shape[1]))  # Resize Y back
    img_ycrcb = cv2.merge([y, cr, cb])
    final_img = cv2.cvtColor(img_ycrcb, cv2.COLOR_YCrCb2BGR)

    cv2.imwrite(output_path, final_img)



# -------- Alpha Channel Encryption -------- #
def encrypt_alpha(image_path, message, output_path):
    img = Image.open(image_path).convert("RGBA")
    pixels = list(img.getdata())
    message += "#####"
    binary_message = ''.join([format(ord(i), '08b') for i in message])
    data_index = 0
    new_pixels = []

    for pixel in pixels:
        r, g, b, a = pixel
        if data_index < len(binary_message):
            a = (a & ~1) | int(binary_message[data_index])
            data_index += 1
        new_pixels.append((r, g, b, a))

    img.putdata(new_pixels)
    img.save(output_path)

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

        binary_message = ""
        for i in range(0, 512, 8):
            for j in range(0, 512, 8):
                block = img[i:i+8, j:j+8]
                dct = cv2.dct(np.float32(block))
                coeff = round(dct[4, 3])
                coeff = abs(coeff)
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

# -------- Encryption Method Selection -------- #
def encrypt_switch(method, image_path, message, output_path):
    if method.lower() == "lsb":
        encrypt_lsb(image_path, message, output_path)
    elif method.lower() == "dct":
        encrypt_dct(image_path, message, output_path)
    elif method.lower() == "alpha":
        encrypt_alpha(image_path, message, output_path)
    else:
        print("Unknown method selected.")

# -------- Main Execution -------- #
def main(image_path):
    if is_steganography(image_path):
        result = classify_and_decrypt(image_path)
        print(result)
    else:
        print({"is_stego": False})

# Example Run
if __name__ == "__main__":
    # Example encryption call
    # encrypt_switch("dct", "image2.png", "Hey buddy whats up. The new image", "dct_output3.png")
    main("dct_output3.png")