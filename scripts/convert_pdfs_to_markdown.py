"""
PDF to Markdown Converter using marker-pdf

This script converts all PDF files in the dndbeyond-pdf-test directory
to markdown format using the marker-pdf library.
"""

import sys
import os
from pathlib import Path
import logging
from typing import List, Optional
from dotenv import load_dotenv

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv()

try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    from marker.config.parser import ConfigParser
except ImportError as e:
    print(f"Error importing marker-pdf: {e}")
    print("Please ensure marker-pdf is installed: pip install marker-pdf")
    sys.exit(1)


class PDFToMarkdownConverter:
    """Convert PDF files to markdown using marker-pdf"""
    
    def __init__(self, input_dir: str, output_dir: str, use_llm: bool = False):
        """
        Initialize the converter
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory to save markdown files
            use_llm: Whether to use LLM for enhanced accuracy
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.use_llm = use_llm
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize converter
        self._setup_converter()
    
    def _setup_converter(self):
        """Setup the marker PDF converter"""
        try:
            config = {
                "output_format": "markdown",
                "force_ocr": False,  # Set to True if PDFs have poor text quality
                "extract_images": True,  # Extract images from PDFs
                "paginate_output": True,  # Add page breaks in output
            }
            
            if self.use_llm:
                llm_service = self._configure_llm_service(config)
                if llm_service:
                    self.logger.info(f"LLM mode enabled with {llm_service}")
                else:
                    self.logger.warning("LLM mode requested but no API keys found. Continuing without LLM.")
                    self.use_llm = False
            
            config_parser = ConfigParser(config)
            
            self.converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=create_model_dict(),
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
                llm_service=config_parser.get_llm_service() if self.use_llm else None
            )
            
            self.logger.info("PDF converter initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize converter: {e}")
            raise
    
    def _configure_llm_service(self, config: dict) -> Optional[str]:
        """Configure LLM service based on available API keys"""
        
        # Check for OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            config.update({
                "use_llm": True,
                "llm_service": "marker.services.openai.OpenAIService",
                "openai_api_key": openai_key,
                "openai_model": "gpt-4o-mini",  # Fast and cost-effective model
            })
            return "OpenAI GPT-4o-mini"
        
        # Check for Anthropic API key
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            config.update({
                "use_llm": True,
                "llm_service": "marker.services.claude.ClaudeService",
                "claude_api_key": anthropic_key,
                "claude_model_name": "claude-3-haiku-20240307",  # Fast and cost-effective model
            })
            return "Anthropic Claude-3-Haiku"
        
        # Check for Google API key (Gemini)
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key:
            config.update({
                "use_llm": True,
                "llm_service": "marker.services.gemini.GoogleGeminiService",
                "gemini_api_key": google_key,
            })
            return "Google Gemini"
        
        return None
    
    def get_pdf_files(self) -> List[Path]:
        """Get all PDF files from the input directory"""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        self.logger.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files
    
    def convert_single_pdf(self, pdf_path: Path) -> Optional[Path]:
        """
        Convert a single PDF to markdown
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Path to the output markdown file, or None if conversion failed
        """
        try:
            self.logger.info(f"Converting {pdf_path.name}...")
            
            # Convert PDF
            rendered = self.converter(str(pdf_path))
            
            # Extract text and images
            text, metadata, images = text_from_rendered(rendered)
            
            # Create output filename
            output_filename = pdf_path.stem + ".md"
            output_path = self.output_dir / output_filename
            
            # Save markdown file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Save images if any
            if images:
                images_dir = self.output_dir / f"{pdf_path.stem}_images"
                images_dir.mkdir(exist_ok=True)
                
                for img_name, img_data in images.items():
                    img_path = images_dir / img_name
                    
                    # Handle different image data formats
                    if hasattr(img_data, 'save'):
                        # It's a PIL Image object
                        img_data.save(img_path)
                    elif isinstance(img_data, bytes):
                        # It's raw bytes
                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_data)
                    else:
                        # Try to convert to bytes if it's a different format
                        try:
                            with open(img_path, 'wb') as img_file:
                                img_file.write(bytes(img_data))
                        except Exception as img_error:
                            self.logger.warning(f"Could not save image {img_name}: {img_error}")
                            continue
                
                self.logger.info(f"Saved {len(images)} images to {images_dir}")
            
            # Save metadata
            metadata_path = self.output_dir / f"{pdf_path.stem}_metadata.txt"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(f"Metadata for {pdf_path.name}\n")
                f.write("=" * 40 + "\n\n")
                
                if 'table_of_contents' in metadata:
                    f.write("Table of Contents:\n")
                    for item in metadata['table_of_contents']:
                        f.write(f"  - {item.get('title', 'Untitled')} (Level {item.get('heading_level', '?')})\n")
                    f.write("\n")
                
                if 'page_stats' in metadata:
                    f.write(f"Total pages: {len(metadata['page_stats'])}\n")
                    for i, stats in enumerate(metadata['page_stats']):
                        f.write(f"Page {i+1}: {stats.get('text_extraction_method', 'unknown')} extraction\n")
            
            self.logger.info(f"Successfully converted {pdf_path.name} -> {output_path.name}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to convert {pdf_path.name}: {e}")
            return None
    
    def convert_all_pdfs(self) -> dict:
        """
        Convert all PDF files in the input directory
        
        Returns:
            Dictionary with conversion results
        """
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            self.logger.warning("No PDF files found in input directory")
            return {"converted": [], "failed": []}
        
        results = {"converted": [], "failed": []}
        
        for pdf_file in pdf_files:
            output_path = self.convert_single_pdf(pdf_file)
            
            if output_path:
                results["converted"].append({
                    "input": str(pdf_file),
                    "output": str(output_path)
                })
            else:
                results["failed"].append(str(pdf_file))
        
        # Print summary
        self.logger.info(f"\nConversion Summary:")
        self.logger.info(f"Successfully converted: {len(results['converted'])} files")
        self.logger.info(f"Failed conversions: {len(results['failed'])} files")
        
        if results["failed"]:
            self.logger.warning("Failed files:")
            for failed_file in results["failed"]:
                self.logger.warning(f"  - {failed_file}")
        
        return results


def main():
    """Main function to run the PDF conversion"""
    
    # Define directories
    input_dir = project_root / "dndbeyond-pdf-test"
    output_dir = project_root / "converted_pdfs_markdown"
    
    print("PDF to Markdown Converter")
    print("=" * 40)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Check available API keys
    available_apis = []
    if os.getenv('OPENAI_API_KEY'):
        available_apis.append("OpenAI")
    if os.getenv('ANTHROPIC_API_KEY'):
        available_apis.append("Anthropic Claude")
    if os.getenv('GOOGLE_API_KEY'):
        available_apis.append("Google Gemini")
    
    if available_apis:
        print(f"\nAvailable LLM services: {', '.join(available_apis)}")
        use_llm_input = input("Use LLM for enhanced accuracy? (y/N): ").strip().lower()
        use_llm = use_llm_input in ['y', 'yes']
    else:
        print("\nNo API keys found in .env file. Running without LLM enhancement.")
        use_llm = False
    
    try:
        # Create converter
        converter = PDFToMarkdownConverter(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            use_llm=use_llm
        )
        
        # Get available PDF files and let user choose
        pdf_files = converter.get_pdf_files()
        if not pdf_files:
            print("No PDF files found!")
            return 1
        
        print(f"\nAvailable PDF files:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf_file.name}")
        
        # Ask user to select a file or convert all
        choice = input(f"\nSelect a PDF to convert (1-{len(pdf_files)}) or 'all' for all files: ").strip().lower()
        
        if choice == 'all':
            # Convert all PDFs
            results = converter.convert_all_pdfs()
        else:
            # Convert single PDF
            try:
                file_index = int(choice) - 1
                if 0 <= file_index < len(pdf_files):
                    selected_pdf = pdf_files[file_index]
                    print(f"\nConverting {selected_pdf.name}...")
                    
                    output_path = converter.convert_single_pdf(selected_pdf)
                    
                    if output_path:
                        results = {
                            "converted": [{"input": str(selected_pdf), "output": str(output_path)}],
                            "failed": []
                        }
                    else:
                        results = {
                            "converted": [],
                            "failed": [str(selected_pdf)]
                        }
                else:
                    print("Invalid selection!")
                    return 1
            except ValueError:
                print("Invalid input! Please enter a number or 'all'.")
                return 1
        
        print(f"\nConversion completed!")
        print(f"Markdown files saved to: {output_dir}")
        
        if results["converted"]:
            print("\nConverted files:")
            for item in results["converted"]:
                print(f"  - {Path(item['input']).name} -> {Path(item['output']).name}")
    
    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
