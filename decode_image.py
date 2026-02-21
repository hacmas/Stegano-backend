from PIL import Image
from security import decrypt_text # NEW IMPORT

# Add 'password' to the arguments
def decode_image(image_path, password):
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())
    
    binary_data = ""
    decoded_text = ""
    
    for pixel in pixels:
        for color_value in pixel:
            binary_data += str(color_value & 1)
            
            if len(binary_data) == 8:
                char = chr(int(binary_data, 2))
                decoded_text += char
                binary_data = ""
                
                if decoded_text.endswith("#####"):
                    # Extract the encrypted gibberish (remove the #####)
                    encrypted_data = decoded_text[:-5]
                    
                    # --- NEW AES LAYER ---
                    final_message = decrypt_text(encrypted_data, password)
                    
                    if final_message is None:
                        raise ValueError("Incorrect Password! Access Denied.")
                    
                    return final_message
                    
    raise ValueError("No hidden message found.")

# --- RUN THE DECODE CODE ---
# Make sure "encoded_image.png" exists in your folder!

# hidden_message = decode_image("encoded_cat.png")

# print("\n-------------------------")
# print(f"SECRET MESSAGE: {hidden_message}")
# print("-------------------------")