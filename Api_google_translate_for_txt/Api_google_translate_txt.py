import requests
import time
import os
import re
from tqdm import tqdm
import json

# --- Configuration ---
API_KEY = "AIzaSyD_5Aye31mk3p_N3ZA3JXVdzHLP16QElHA"  # Replace with your key
REQUEST_TIMEOUT = 30  # API timeout in seconds

# --- Translation Functions ---
def translate_batch(texts, source_language, target_language):
    """Translate a batch of texts using Google Cloud Translation API with proper JSON body."""
    url = "https://translation.googleapis.com/language/translate/v2"
    
    # Prepare the request data as JSON
    data = {
        "q": texts,
        "source": source_language,
        "target": target_language,
        "format": "text"
    }
    
    params = {
        "key": API_KEY
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(
            url,
            params=params,
            json=data,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return [t["translatedText"] for t in response.json()["data"]["translations"]]
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if response.status_code == 429:
            error_msg += " (Rate Limited)"
        raise Exception(f"API request failed: {error_msg}")

# --- Helper Functions ---
def is_non_translatable(text):
    """Check if a text contains only numbers/symbols."""
    if not isinstance(text, str):
        return True
    return bool(re.match(r'^[\W\d_]+$', str(text)))

def count_words(text):
    """Simple word counter (split by whitespace)."""
    return len(str(text).split()) if text else 0

def split_into_paragraphs(text, max_paragraph_length=500):
    """Split text into paragraphs of reasonable length for translation."""
    paragraphs = []
    current_paragraph = ""
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            if current_paragraph:
                paragraphs.append(current_paragraph)
                current_paragraph = ""
            paragraphs.append("")  # Empty line
            continue
            
        if len(current_paragraph) + len(line) + 1 > max_paragraph_length:
            if current_paragraph:
                paragraphs.append(current_paragraph)
                current_paragraph = line
            else:
                paragraphs.append(line)
        else:
            if current_paragraph:
                current_paragraph += "\n" + line
            else:
                current_paragraph = line
    
    if current_paragraph:
        paragraphs.append(current_paragraph)
    
    return paragraphs

# --- Main Translation Function ---
def translate_txt(input_file, source_language="zh", target_language="en"):
    # Initialize counters
    translated_words = 0
    failed_words = 0
    
    # Set up file paths
    input_dir = os.path.dirname(input_file)
    input_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(input_dir, f"{input_name}_translated.txt")
    log_file = os.path.join(input_dir, f"{input_name}_log.txt")

    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        original_text = f.read()

    # Split into paragraphs for better translation
    paragraphs = split_into_paragraphs(original_text)
    
    # Filter out non-translatable paragraphs
    texts_to_translate = []
    paragraph_indices = []
    for idx, para in enumerate(paragraphs):
        if para and not is_non_translatable(para):
            texts_to_translate.append(para)
            paragraph_indices.append(idx)

    # Prepare log data
    log_data = []
    translated_paragraphs = paragraphs.copy()

    # --- Translation Process ---
    MAX_CHARS_PER_MINUTE = 600000  # Google's limit
    MAX_TEXTS_PER_BATCH = 128      # Google's limit
    MAX_CHARS_PER_BATCH = 30000    # Reduced from 1M to avoid 411 errors
    total_chars = 0
    start_time = time.time()

    # Process in batches
    with tqdm(total=len(texts_to_translate), desc="Translating") as pbar:
        i = 0
        while i < len(texts_to_translate):
            # Create batch
            batch = []
            batch_indices = []
            batch_chars = 0
            
            while (i < len(texts_to_translate) and 
                   len(batch) < MAX_TEXTS_PER_BATCH and 
                   batch_chars + len(texts_to_translate[i]) <= MAX_CHARS_PER_BATCH):
                text = texts_to_translate[i]
                batch.append(text)
                batch_indices.append(paragraph_indices[i])
                batch_chars += len(text)
                i += 1

            # Rate limiting
            elapsed = time.time() - start_time
            if total_chars + batch_chars > MAX_CHARS_PER_MINUTE:
                delay = max(60 - elapsed, 0)
                print(f"\nRate limit approaching. Waiting {delay:.1f}s...")
                time.sleep(delay)
                total_chars = 0
                start_time = time.time()

            # Translate with retries
            translated = None
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    translated = translate_batch(batch, source_language, target_language)
                    break
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print(f"\nFinal attempt failed: {e}")
                    else:
                        wait_time = 2 ** attempt
                        print(f"\nAttempt {attempt + 1} failed: {e}. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue

            # Update results
            if translated and len(translated) == len(batch):
                for idx, translation in zip(batch_indices, translated):
                    translated_paragraphs[idx] = translation
                    translated_words += count_words(translation)
            else:
                print(f"\nFailed to translate batch of {len(batch)} items")
                for idx, original in zip(batch_indices, batch):
                    log_data.append(f"Failed to translate paragraph at position {idx}: {original[:100]}...")
                    failed_words += count_words(original)

            total_chars += batch_chars
            pbar.update(len(batch))

    # Save translated file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(translated_paragraphs))

    # Save log file
    with open(log_file, 'w', encoding='utf-8') as f:
        if log_data:
            f.write('\n'.join(log_data))
        else:
            f.write("All translations were successful.")

    # --- Final Summary ---
    total_words = translated_words + failed_words
    print("\nTranslation Summary:")
    print(f"- Successfully translated: {translated_words:,} words")
    print(f"- Failed translations: {failed_words:,} words")
    print(f"- Total processed: {total_words:,} words")
    print(f"\nTranslated file saved to: {output_file}")
    print(f"Log file saved to: {log_file}")

# --- Run Script ---
if __name__ == "__main__":
    input_file = input("Enter path to TXT file: ").strip('"')
    translate_txt(input_file)