"""
PDF to Images to Markdown using GPT-4o

This script converts PDF pages to images and uses GPT-4o vision capabilities
to extract content as markdown from each image.
"""

import sys
import os
from pathlib import Path
import logging
from typing import List, Optional, Dict
from dotenv import load_dotenv
import base64
from io import BytesIO

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv()

try:
    import fitz  # PyMuPDF
    from PIL import Image
    import openai
except ImportError as e:
    print(f"Missing required packages. Please install:")
    print("pip install PyMuPDF pillow openai")
    print(f"Error: {e}")
    sys.exit(1)


class PDFToImagesGPT4oConverter:
    """Convert PDF pages to images and extract markdown using GPT-4o"""
    
    def __init__(self, input_dir: str, output_dir: str, dpi: int = 300):
        """
        Initialize the converter
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory to save markdown files and images
            dpi: DPI for image conversion (higher = better quality, larger files)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.dpi = dpi
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.output_dir / "page_images"
        self.images_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        self._setup_openai()
    
    def _setup_openai(self):
        """Setup OpenAI client with API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        self.logger.info("OpenAI client initialized successfully")
    
    def get_pdf_files(self) -> List[Path]:
        """Get all PDF files from the input directory"""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        self.logger.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files
    
    def pdf_to_images(self, pdf_path: Path) -> List[Path]:
        """
        Convert PDF pages to images
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of paths to the generated image files
        """
        try:
            self.logger.info(f"Converting {pdf_path.name} to images...")
            
            # Open PDF
            doc = fitz.open(pdf_path)
            image_paths = []
            
            # Create subfolder for this PDF's images
            pdf_images_dir = self.images_dir / pdf_path.stem
            pdf_images_dir.mkdir(exist_ok=True)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(self.dpi/72, self.dpi/72)  # Scale factor for DPI
                pix = page.get_pixmap(matrix=mat)
                
                # Save as PNG
                image_filename = f"page_{page_num + 1:03d}.png"
                image_path = pdf_images_dir / image_filename
                pix.save(image_path)
                image_paths.append(image_path)
                
                self.logger.info(f"Saved page {page_num + 1} as {image_filename}")
            
            doc.close()
            self.logger.info(f"Converted {len(image_paths)} pages to images")
            return image_paths
            
        except Exception as e:
            self.logger.error(f"Failed to convert {pdf_path.name} to images: {e}")
            return []
    
    def encode_image_base64(self, image_path: Path) -> str:
        """
        Encode image as base64 for OpenAI API
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to encode {image_path.name}: {e}")
            return ""
    
    def extract_markdown_from_image(self, image_path: Path) -> str:
        """
        Use GPT-4o to extract markdown content from an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Markdown content extracted from the image
        """
        try:
            self.logger.info(f"Processing {image_path.name} with GPT-4o...")
            
            # Encode image
            base64_image = self.encode_image_base64(image_path)
            if not base64_image:
                return f"# Error\n\nFailed to encode image: {image_path.name}\n"
            
            # Create the prompt
            prompt = """Please analyze this image and convert ALL content to markdown format. Include:

1. **Text content**: Convert all text exactly as it appears, maintaining formatting
2. **Tables**: Convert to proper markdown table format
3. **Lists**: Convert to markdown list format (numbered or bulleted as appropriate)
4. **Headers**: Use appropriate markdown headers (# ## ###)
5. **Emphasis**: Use **bold** and *italic* as appropriate
6. **Images/Figures**: Describe with ![description](placeholder.jpg) format
7. **Mathematical formulas**: Convert to LaTeX format within $ or $$ blocks
8. **Code blocks**: Use ```language code``` format if applicable
9. **Links**: Convert to [text](url) format if visible
10. **Special formatting**: Maintain any special formatting like quotes, callouts, etc.

Please be thorough and capture ALL visible content in the image. Do not add any commentary - just provide the clean markdown conversion of everything you see."""

            # Make API call to GPT-4o
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o vision model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"  # High detail for better text recognition
                                }
                            }
                        ]
                    }
                ],
                max_completion_tokens=4000,
                temperature=0.0  # For consistent, deterministic output
            )
            
            markdown_content = response.choices[0].message.content
            self.logger.info(f"Successfully processed {image_path.name}")
            return markdown_content
            
        except Exception as e:
            self.logger.error(f"Failed to process {image_path.name} with GPT-4o: {e}")
            return f"# Error Processing {image_path.name}\n\n{str(e)}\n"
    
    def process_single_pdf(self, pdf_path: Path) -> Optional[Path]:
        """
        Process a single PDF: convert to images and extract markdown
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Path to the combined markdown file
        """
        try:
            self.logger.info(f"Processing PDF: {pdf_path.name}")
            
            # Convert PDF to images
            image_paths = self.pdf_to_images(pdf_path)
            if not image_paths:
                return None
            
            # Create combined markdown file
            output_filename = f"{pdf_path.stem}_gpt4o_extracted.md"
            output_path = self.output_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as combined_file:
                # Write header
                combined_file.write(f"# {pdf_path.name} - Extracted with GPT-4o\n\n")
                combined_file.write(f"Extracted on: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n")
                combined_file.write(f"Total pages: {len(image_paths)}\n\n")
                combined_file.write("---\n\n")
                
                # Process each page
                for i, image_path in enumerate(image_paths, 1):
                    self.logger.info(f"Processing page {i}/{len(image_paths)}")
                    
                    # Extract markdown from image
                    markdown_content = self.extract_markdown_from_image(image_path)
                    
                    # Write to combined file
                    combined_file.write(f"## Page {i}\n\n")
                    combined_file.write(f"*Source: {image_path.name}*\n\n")
                    combined_file.write(markdown_content)
                    combined_file.write(f"\n\n{'---'}\n\n")
                    
                    # Also save individual page markdown
                    page_output_path = self.output_dir / f"{pdf_path.stem}_page_{i:03d}.md"
                    with open(page_output_path, 'w', encoding='utf-8') as page_file:
                        page_file.write(f"# {pdf_path.name} - Page {i}\n\n")
                        page_file.write(f"*Source: {image_path.name}*\n\n")
                        page_file.write(markdown_content)
            
            self.logger.info(f"Successfully processed {pdf_path.name} -> {output_path.name}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to process {pdf_path.name}: {e}")
            return None
    
    def process_all_pdfs(self) -> Dict[str, List[str]]:
        """
        Process all PDF files in the input directory
        
        Returns:
            Dictionary with processing results
        """
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            self.logger.warning("No PDF files found in input directory")
            return {"converted": [], "failed": []}
        
        results = {"converted": [], "failed": []}
        
        for pdf_file in pdf_files:
            output_path = self.process_single_pdf(pdf_file)
            
            if output_path:
                results["converted"].append(str(output_path))
            else:
                results["failed"].append(str(pdf_file))
        
        # Print summary
        self.logger.info(f"\nProcessing Summary:")
        self.logger.info(f"Successfully processed: {len(results['converted'])} files")
        self.logger.info(f"Failed processing: {len(results['failed'])} files")
        
        return results


def main():
    """Main function to run the PDF to GPT-4o markdown conversion"""
    
    # Define directories
    input_dir = project_root / "dndbeyond-pdf-test"
    output_dir = project_root / "gpt4o_extracted_markdown"
    
    print("PDF to Images to Markdown (GPT-4o) Converter")
    print("=" * 50)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("\nError: OPENAI_API_KEY not found in .env file!")
        print("Please add your OpenAI API key to the .env file.")
        return 1
    
    print(f"\nUsing GPT-4o for content extraction")
    
    # DPI setting
    dpi_input = input("Enter DPI for image conversion (default 300, higher = better quality): ").strip()
    try:
        dpi = int(dpi_input) if dpi_input else 300
    except ValueError:
        dpi = 300
    
    print(f"Using DPI: {dpi}")
    
    try:
        # Create converter
        converter = PDFToImagesGPT4oConverter(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            dpi=dpi
        )
        
        # Get available PDF files and let user choose
        pdf_files = converter.get_pdf_files()
        if not pdf_files:
            print("No PDF files found!")
            return 1
        
        print(f"\nAvailable PDF files:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf_file.name}")
        
        # Ask user to select a file or process all
        choice = input(f"\nSelect a PDF to process (1-{len(pdf_files)}) or 'all' for all files: ").strip().lower()
        
        if choice == 'all':
            # Process all PDFs
            results = converter.process_all_pdfs()
        else:
            # Process single PDF
            try:
                file_index = int(choice) - 1
                if 0 <= file_index < len(pdf_files):
                    selected_pdf = pdf_files[file_index]
                    print(f"\nProcessing {selected_pdf.name} with GPT-4o...")
                    
                    output_path = converter.process_single_pdf(selected_pdf)
                    
                    if output_path:
                        results = {"converted": [str(output_path)], "failed": []}
                    else:
                        results = {"converted": [], "failed": [str(selected_pdf)]}
                else:
                    print("Invalid selection!")
                    return 1
            except ValueError:
                print("Invalid input! Please enter a number or 'all'.")
                return 1
        
        print(f"\nProcessing completed!")
        print(f"Results saved to: {output_dir}")
        
        if results["converted"]:
            print("\nGenerated files:")
            for file_path in results["converted"]:
                print(f"  - {Path(file_path).name}")
        
        if results["failed"]:
            print("\nFailed files:")
            for file_path in results["failed"]:
                print(f"  - {Path(file_path).name}")
    
    except Exception as e:
        print(f"Error during processing: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
