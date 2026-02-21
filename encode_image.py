from PIL import Image
from security import encrypt_text # NEW IMPORT

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

# Add 'password' to the arguments
def encode_image(image_path, secret_text, password, output_path):
    img = Image.open(image_path).convert("RGB")
    
    # --- NEW AES LAYER ---
    encrypted_text = encrypt_text(secret_text, password)
    # Add delimiter to the ENCRYPTED text, not the plain text
    encrypted_text += "#####" 
    
    binary_message = text_to_binary(encrypted_text)
    data_length = len(binary_message)
    
    pixels = list(img.getdata())
    new_pixels = []
    data_index = 0
    
    # 4. Loop through every pixel
    for pixel in pixels:
        # A pixel is a tuple: (Red, Green, Blue) -> e.g., (255, 100, 50)
        # We process it as a list so we can change values
        pixel = list(pixel)
        
        # Loop through the 3 colors (R, G, B)
        for i in range(3):
            # If we still have data to hide
            if data_index < data_length:
                # Get the bit we want to hide (0 or 1)
                bit_to_hide = int(binary_message[data_index])
                
                # BITWISE MAGIC:
                # bitwise AND with ~1 (11111110) clears the last bit (makes it even)
                # bitwise OR with the bit_to_hide puts our bit in that spot
                pixel[i] = (pixel[i] & ~1) | bit_to_hide
                
                data_index += 1
                
        # Store the modified pixel
        new_pixels.append(tuple(pixel))
        
    # 5. Save the new image
    # Create a new image with the same mode and size
    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_pixels)
    new_img.save(output_path)
    print(f"Success! Message hidden in {output_path}")

# --- RUN THE CODE ---
# Make sure you have an image named 'test.png' in the same folder


# try:
#     encode_image("cat.jpg", "My password is : {Qwerty@#123456}", "encoded_cat.png")
# except Exception as e:
#     print(f"Error: {e}")