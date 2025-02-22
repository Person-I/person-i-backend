import fal_client
import os
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

class FalService:
    def __init__(self):
        # FAL API key should be in .env as FAL_KEY
        self.api_key = os.getenv('FAL_KEY')
        if not self.api_key:
            raise ValueError("FAL_KEY not found in environment variables")

    def _on_queue_update(self, update):
        """Handle progress updates from FAL AI"""
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(f"FAL AI Progress: {log['message']}")

    def extract_text_from_image(self, image_url: str) -> Dict:
        """
        Extract text from image using FAL AI OCR
        Args:
            image_url: URL of the image to process
        Returns:
            Dict containing extracted text and structured information
        """
        try:
            result = fal_client.subscribe(
                "fal-ai/got-ocr/v2",
                arguments={
                    "input_image_urls": [image_url],
                    "multi_page": True
                },
                with_logs=True,
                on_queue_update=self._on_queue_update,
            )
            
            return self._parse_ocr_result(result)
        except Exception as e:
            print(f"Error in FAL AI OCR: {str(e)}")
            return {"error": str(e)}

    def _parse_ocr_result(self, result: Dict) -> Dict:
        """
        Parse OCR result and extract relevant information
        Args:
            result: Raw OCR result from FAL AI
        Returns:
            Dict containing structured information about the user
        """
        try:
            # Extract text from OCR result
            extracted_text = result.get('text', '')
            
            # Create a summary prompt for the extracted information
            prompt = self._create_summary_prompt(extracted_text)
            
            return {
                "raw_text": extracted_text,
                "summary_prompt": prompt
            }
        except Exception as e:
            print(f"Error parsing OCR result: {str(e)}")
            return {"error": str(e)}

    def _create_summary_prompt(self, text: str) -> str:
        """
        Create a prompt for summarizing user information
        Args:
            text: Extracted text from the image
        Returns:
            Formatted prompt for generating summary
        """
        return f"""Based on the following extracted text from a document, please create a concise summary of the person's information:

Extracted Text:
{text}

Please include:
1. Basic personal information (if available)
2. Key professional or educational highlights
3. Any notable achievements or qualifications
4. Areas of expertise or interests

Summary:""" 