from flask import Flask, render_template, request, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        
        text = request.form['text']
        color = request.form['color']  # Get the color from the form
        position = request.form['position']  # Get the position from the form
        meme_image = create_meme(image_path, text, color, position)
        
        meme_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'meme_' + file.filename)
        meme_image.save(meme_image_path)
        
        return render_template('index.html', meme_image=meme_image_path)

def create_meme(image_path, text, color, position):
    image = Image.open(image_path)
    image = image.resize((300, 300))  # Resize to meme size (300x300) or adjust as needed
    draw = ImageDraw.Draw(image)

    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", 40)  # Change 40 to your desired font size
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font if the specified font is not found

    # Define maximum width for the text
    max_width = image.size[0] - 20  # Leave some padding on the sides
    wrapped_text = wrap_text(draw, text, font, max_width)

    # Calculate the height of the wrapped text
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text)

    # Draw text based on selected position
    if position == "top":
        y_text = 10  # Start drawing text 10 pixels from the top
    else:  # position == "bottom"
        y_text = image.size[1] - (10 + total_text_height)  # Start drawing text 10 pixels from the bottom

    for line in wrapped_text:
        # Calculate the width of each line
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        text_width = right - left
        draw.text(((image.size[0] - text_width) / 2, y_text), line, fill=color, font=font)
        y_text += bottom - top  # Move down for the next line

    return image

def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within the specified width."""
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        # Check if adding the next word would exceed the max width
        test_line = f"{current_line} {word}".strip()
        left, top, right, bottom = draw.textbbox((0, 0), test_line, font=font)
        text_width = right - left
        if text_width <= max_width:
            current_line = test_line
        else:
            # If it exceeds, add the current line to lines and start a new line
            if current_line:
                lines.append(current_line)
            current_line = word  # Start a new line with the current word

    # Add the last line if it exists
    if current_line:
        lines.append(current_line)

    return lines

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

