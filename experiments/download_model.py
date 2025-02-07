"""
python download_model.py --output-path ~/models sentence-transformers/all-MiniLM-L6-v2
"""
import argparse
import os
from transformers import AutoTokenizer, AutoModel
import sys
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def download_model(model_name, output_path, logger):
    try:
        logger.info(f"Starting download of model: {model_name}")

        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        logger.info(f"Model will be saved to: {output_path}")

        # Download both the model and tokenizer
        logger.info("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(output_path)

        logger.info("Downloading model...")
        model = AutoModel.from_pretrained(model_name)
        model.save_pretrained(output_path)

        logger.info("Download completed successfully!")
        return True

    except Exception as e:
        logger.error(f"An error occurred while downloading the model: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download a Hugging Face model to a specified directory')
    parser.add_argument('model_name', type=str, help='Name of the model to download (e.g., "bert-base-uncased")')
    parser.add_argument('--output-path', type=str, default=os.getcwd(),
                      help='Directory path where the model should be saved (default: current directory)')
    args = parser.parse_args()

    # Convert relative path to absolute path
    output_path = os.path.abspath(args.output_path) + "/" + args.model_name

    logger = setup_logging()

    if not download_model(args.model_name, output_path, logger):
        sys.exit(1)

if __name__ == "__main__":
    main()