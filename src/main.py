import os
import json
import argparse
import datetime
from typing import List
from src.round1a.pdf_processor import PDFProcessor
from src.round1b.persona_analyzer import PersonaAnalyzer

def run_round1a(input_dir: str, output_dir: str):
    """Run Round 1A processing"""
    processor = PDFProcessor()
    
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            
            print(f"Processing {filename}...")
            try:
                result = processor.process_pdf(input_path)
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"  Saved to {output_path}")
            except Exception as e:
                print(f"  Error processing {filename}: {str(e)}")

def run_round1b(document_dir: str, persona_file: str, job_file: str, output_file: str):
    """Run Round 1B processing"""
    analyzer = PersonaAnalyzer()
    
    # Load persona and job description
    persona = analyzer.load_persona(persona_file)
    job = analyzer.load_job_description(job_file)
    
    # Get document paths
    document_paths = [
        os.path.join(document_dir, f) 
        for f in os.listdir(document_dir) 
        if f.lower().endswith('.pdf')
    ]
    
    print(f"Analyzing {len(document_paths)} documents for persona: {persona['name']}")
    print(f"Job to be done: {job['description']}")
    
    result = analyzer.analyze_documents(document_paths, persona, job)
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Analysis saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adobe Hackathon Solution")
    parser.add_argument('--round', choices=['1a', '1b'], required=True, help="Which round to run")
    
    # Round 1A arguments
    parser.add_argument('--input-dir', help="Input directory for PDFs (Round 1A)")
    parser.add_argument('--output-dir', help="Output directory for JSON (Round 1A)")
    
    # Round 1B arguments
    parser.add_argument('--document-dir', help="Directory with documents (Round 1B)")
    parser.add_argument('--persona-file', help="Persona definition JSON (Round 1B)")
    parser.add_argument('--job-file', help="Job description JSON (Round 1B)")
    parser.add_argument('--output-file', help="Output JSON file (Round 1B)")
    
    args = parser.parse_args()
    
    if args.round == '1a':
        if not args.input_dir or not args.output_dir:
            parser.error("Round 1A requires --input-dir and --output-dir")
        run_round1a(args.input_dir, args.output_dir)
    elif args.round == '1b':
        if not all([args.document_dir, args.persona_file, args.job_file, args.output_file]):
            parser.error("Round 1B requires --document-dir, --persona-file, --job-file, and --output-file")
        run_round1b(args.document_dir, args.persona_file, args.job_file, args.output_file)