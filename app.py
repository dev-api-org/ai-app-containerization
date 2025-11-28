import os
# Ensure compatibility with installed huggingface_hub versions that may
# not expose `HfFolder` (which older/newer Gradio releases expect).
# If the symbol is missing, add a lightweight shim so Gradio's import
# doesn't fail inside the container. This keeps the app robust across
# minor dependency mismatches during CI/build.
try:
    import huggingface_hub as _hf_hub
    if not hasattr(_hf_hub, "HfFolder"):
        class HfFolder:
            @staticmethod
            def path():
                return None
        _hf_hub.HfFolder = HfFolder
except Exception:
    # If huggingface_hub isn't installed yet, we'll rely on the normal
    # import path to raise an error later during startup.
    pass

import gradio as gr
import google.generativeai as genai
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hardcoded configuration
MODEL_NAME = "gemini-2.0-flash"  # Working model from api_test.py
TEMPERATURE = 0.4

# Configure Gemini API with error handling
def initialize_gemini_api():
    """Initialize and validate Gemini API configuration."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set")
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )
    
    # Validate API key format (basic check)
    if len(api_key) < 20 or not api_key.strip():
        logger.error("GEMINI_API_KEY appears to be invalid (too short or empty)")
        raise ValueError(
            "GEMINI_API_KEY appears to be invalid. "
            "Please check your API key format."
        )
    
    try:
        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {str(e)}")
        raise RuntimeError(f"Failed to configure Gemini API: {str(e)}")

# Initialize API
initialize_gemini_api()

# Generation configuration
generation_config = {
    "temperature": TEMPERATURE,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

DEFAULT_STATUS_MESSAGE = "_Waiting for image upload..._"
DEFAULT_RESULTS_MESSAGE = "_Upload an image and click 'Analyze Car' to see results..._"

def validate_image(image_path):
    """Validate image file before processing."""
    # Check file exists
    if not os.path.exists(image_path):
        raise ValueError("Image file does not exist")
    
    # Check file size (max 10MB)
    file_size = os.path.getsize(image_path)
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise ValueError(f"Image file too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is 10MB.")
    
    if file_size == 0:
        raise ValueError("Image file is empty")
    
    # Try to open and validate image
    try:
        image = Image.open(image_path)
        
        # Verify it's actually an image
        image.verify()
        
        # Reopen after verify (verify closes the file)
        image = Image.open(image_path)
        
        # Check image format
        supported_formats = ['JPEG', 'PNG', 'WEBP', 'JPG', 'BMP', 'GIF']
        if image.format not in supported_formats:
            raise ValueError(f"Unsupported image format: {image.format}. Supported: {', '.join(supported_formats)}")
        
        # Check image dimensions
        width, height = image.size
        if width < 50 or height < 50:
            raise ValueError(f"Image too small ({width}x{height}). Minimum size is 50x50 pixels.")
        
        if width > 10000 or height > 10000:
            raise ValueError(f"Image too large ({width}x{height}). Maximum size is 10000x10000 pixels.")
        
        logger.info(f"Image validated: {width}x{height}, format: {image.format}, size: {file_size / 1024:.1f}KB")
        return image
        
    except Image.UnidentifiedImageError:
        raise ValueError("File is not a valid image or is corrupted")
    except Exception as e:
        if "cannot identify image file" in str(e).lower():
            raise ValueError("File is not a valid image")
        raise


def verify_car_in_image(image):
    """Verify if the image contains a car with robust checking."""
    # Create a new model instance for thread safety
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=generation_config,
    )
    
    verification_prompt = """Look at this image carefully. Does it contain a real car, truck, SUV, or any motor vehicle?
    
Answer with ONLY one word: either 'YES' if it shows a real vehicle, or 'NO' if it doesn't.
    
Do not provide any explanation, just YES or NO."""
    
    try:
        verification_response = model.generate_content([verification_prompt, image])
        verification_text = verification_response.text.strip().upper()
        
        logger.info(f"Car verification response: {verification_text}")
        
        # Robust checking - look for explicit YES
        # This avoids false negatives from responses like "No, it's not a bicycle, it's a car"
        if "YES" in verification_text:
            # Make sure it's not "NO, YES" or similar ambiguous response
            if "NO" in verification_text and verification_text.index("NO") < verification_text.index("YES"):
                return False
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error during car verification: {str(e)}")
        raise


def analyze_car(image_path, progress=gr.Progress()):
    """Main function to analyze car images with comprehensive validation and error handling."""
    
    if image_path is None:
        return "⚠️ Please upload an image first.", DEFAULT_STATUS_MESSAGE
    
    try:
        # Step 1: Validate image file
        progress(0, desc="📤 Uploading and validating image...")
        logger.info(f"Starting analysis for image: {image_path}")
        
        # Clear the waiting message immediately
        status_update = "🔄 **Processing started...**\n\n"
        
        image = validate_image(image_path)
        
        status_update = f"✅ **Image validated successfully**\n- Size: {image.size[0]}x{image.size[1]}px\n- Format: {image.format}\n\n"
        
        # Step 2: Verify if it's a car
        progress(0.3, desc="🔍 Checking if image contains a car...")
        logger.info("Verifying if image contains a car...")
        status_update += "🔍 **Verifying vehicle presence...**\n\n"
        
        is_car = verify_car_in_image(image)
        
        if not is_car:
            logger.info("No car detected in image")
            return "⚠️ **Not a Car Detected**\n\nPlease upload an image of a car, truck, SUV, or other motor vehicle for analysis.", status_update + "❌ **No vehicle detected**\n\n_Upload a new image to try again._"
        
        status_update += "✅ **Car detected!**\n\n"
        
        # Step 3: Detailed car analysis
        progress(0.6, desc="🤖 AI analyzing the vehicle...")
        logger.info("Car detected, performing detailed analysis...")
        status_update += "🤖 **Performing detailed AI analysis...**\n\n"
        
        # Create a new model instance for thread safety
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=generation_config,
        )
        
        analysis_prompt = """Analyze this car image and provide the following details in a structured format:

- Make (manufacturer)
- Model
- Approximate year or generation
- Body type (sedan, SUV, coupe, hatchback, truck, etc.)
- Color
- Visible condition (excellent, good, fair, poor)
- Any distinctive features or modifications
- Interesting facts about this car model

Be specific and detailed in your analysis. Format your response clearly."""
        
        analysis_response = model.generate_content([analysis_prompt, image])
        analysis_text = analysis_response.text.strip()
        
        progress(1.0, desc="✅ Analysis complete!")
        logger.info("Analysis completed successfully")
        status_update += "✅ **Analysis completed successfully!**\n\n"
        status_update += "👇 **Scroll down to view the detailed analysis results below.**"
        
        # Format the output
        result = f"""✅ **Car Detected Successfully!**

🚗 **AI Analysis Results:**

{analysis_text}

---
*Powered by Gemini 2.0 Flash | Temperature: {TEMPERATURE}*
"""
        
        return result, status_update
    
    except ValueError as e:
        # Validation errors (user-friendly)
        logger.warning(f"Validation error: {str(e)}")
        return f"⚠️ **Invalid Image**\n\n{str(e)}\n\nPlease upload a valid car image.", "❌ **Validation failed**\n\n_Upload a valid image to try again._"
    
    except Exception as e:
        # Unexpected errors
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        error_msg = f"❌ **Error during analysis:**\n\n{str(e)}\n\nPlease try again with a different image."
        return error_msg, "❌ **Analysis failed**\n\n_Please try again with a different image._"


def handle_image_change(image_path):
    if image_path is None:
        return DEFAULT_RESULTS_MESSAGE, DEFAULT_STATUS_MESSAGE
    return gr.update(), gr.update()


# Custom CSS for minimal, clean design
custom_css = """
.gradio-container {
    font-family: 'Inter', sans-serif;
    max-width: 1200px;
    margin: auto;
}

#title {
    text-align: center;
    margin-bottom: 1rem;
}

#description {
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
}

/* Center all headings */
.gradio-container h1,
.gradio-container h2,
.gradio-container h3,
.gradio-container h4 {
    text-align: center;
}

.primary-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    font-weight: 600;
}
"""

# Build Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="AI Car Inspector") as interface:
    
    gr.Markdown(
        """
        # 🚗 AI Car Inspector
        ### Powered by Gemini 2.0 Flash
        """,
        elem_id="title"
    )
    
    gr.Markdown(
        "Upload a car image to get instant AI-powered analysis with detailed information about make, model, year, and more.",
        elem_id="description"
    )
    
    # Upload and Status Section (Side by Side)
    with gr.Row():
        # Upload Section
        with gr.Column(scale=1):
            image_input = gr.Image(
                type="filepath",
                label="📸 Upload Car Image",
                height=400
            )
            
            analyze_btn = gr.Button(
                "🔍 Analyze Car",
                variant="primary",
                size="lg",
                elem_classes="primary-btn"
            )
            
            gr.Markdown(
                """
                **Supported formats:** JPG, PNG, WEBP  
                **Tip:** Clear, well-lit photos work best!
                """
            )
        
        # Status Section
        with gr.Column(scale=1):
            gr.Markdown("## ⚙️ Processing Status")
            status_box = gr.Markdown(
                value=DEFAULT_STATUS_MESSAGE
            )
    
    # Separator
    gr.Markdown("---")
    
    # Results Section (Full Width)
    with gr.Column():
        gr.Markdown("## 📊 Analysis Results")
        output = gr.Markdown(
            value=DEFAULT_RESULTS_MESSAGE
        )
    
    # Connect button to function
    analyze_btn.click(
        fn=analyze_car,
        inputs=image_input,
        outputs=[output, status_box]
    )

    image_input.change(
        fn=handle_image_change,
        inputs=image_input,
        outputs=[output, status_box]
    )

# Launch configuration
if __name__ == "__main__":
    interface.launch(
        server_name="0.0.0.0",  # Important for Docker
        server_port=7860,
        share=False,
        show_error=True
    )