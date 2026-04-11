import os
import json
import traceback

def fix_jsonl_file(input_path, output_path):
    print(f"Processing: {input_path}")
    count_fixed = 0
    count_total = 0
    
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            count_total += 1
            if not line.strip():
                continue
                
            try:
                row = json.loads(line)
                
                # Check for the specific problem: 'authors' is a list of dictionaries
                if 'authors' in row and isinstance(row['authors'], list):
                    # Check if it's a list containing dictionaries with 'name' (e.g. Semantic Scholar)
                    if len(row['authors']) > 0 and isinstance(row['authors'][0], dict) and 'name' in row['authors'][0]:
                        # Convert [{"name": "Alice"}, {"name": "Bob"}] structure to "Alice, Bob" String
                        # This matches the ArXiv dataset 'authors' schema of Value('string')
                        row['authors'] = ", ".join([a.get('name', 'Unknown') for a in row['authors']])
                        count_fixed += 1
                        
                # Write the (possibly modified) row back out
                outfile.write(json.dumps(row) + '\n')
                
            except json.JSONDecodeError:
                print(f"Skipping malformed JSON line {count_total} in {input_path}")
            except Exception as e:
                print(f"Error processing line {count_total} in {input_path}: {e}")
                
    print(f"Finished {input_path} - Fixed {count_fixed} rows out of {count_total} total rows.")

def main():
    input_dir = 'dataset'
    output_dir = 'dataset_fixed'
    
    # Ensure dataset directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Directory '{input_dir}' not found.")
        return
        
    # Create fixed dataset directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
        
    found_jsonl = False
    
    # Process all JSONL files in the directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.jsonl'):
            found_jsonl = True
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            fix_jsonl_file(input_path, output_path)
            
    if not found_jsonl:
        print(f"Warning: No .jsonl files found in the '{input_dir}' directory.")
    else:
        print(f"\nAll done! The fixed dataset files are saved in the '{output_dir}' directory.")
        print("Upload the files from the 'dataset_fixed' directory to Hugging Face instead.")

if __name__ == "__main__":
    main()
