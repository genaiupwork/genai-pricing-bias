import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from utils.data_loader import load_csv_data
from utils.file_utils import file_exists, save_to_csv, load_completed_tasks
from utils.progress import print_progress, print_summary
from services.openrouter import call_api
from prompts.base import construct_prompt


def generate_rate_prompts():
    """Generate rate analysis prompts."""
    prompts_file = "rate_prompts.csv"
    
    if file_exists(prompts_file):
        print(f"✅ {prompts_file} exists, skipping generation")
        return prompts_file
    
    print("📝 Generating rate analysis prompts...")
    full_data = load_csv_data()
    
    new_rows = []
    for index, freelancer in full_data.iterrows():
        prompt = construct_prompt(freelancer)
        new_rows.append({
            'hourlyRate': freelancer.get('hourlyRate', 'Not available'),
            'prompt': prompt,
            'source_file': freelancer.get('source_file', 'Unknown')
        })
        
        if (index + 1) % 1000 == 0:
            print(f"Processed {index + 1}/{len(full_data)} freelancers")
    
    save_to_csv(new_rows, prompts_file)
    
    print_summary("RATE ANALYSIS GENERATION SUMMARY", {
        "Input freelancers": len(full_data),
        "Output prompts": len(new_rows)
    })
    
    return prompts_file


def process_row(row_data, completed_tasks):
    """Process a single row with all models."""
    idx, row = row_data
    results = []
    
    for model in config.MODELS:
        if (idx, model) in completed_tasks:
            continue
        
        result = call_api(row['prompt'], model, idx)
        if result:
            result.update({
                'hourly_rate': row['hourlyRate'],
                'source_file': row['source_file']
            })
            results.append(result)
    
    return results


def run_api_processing(prompts_file: str):
    """Run API processing with parallel execution."""
    results_file = "rate_analysis_results.csv"
    df = pd.read_csv(prompts_file)
    completed_tasks = load_completed_tasks(results_file)
    
    # Filter unprocessed tasks
    tasks = []
    for idx, row in df.iterrows():
        remaining_models = [m for m in config.MODELS if (idx, m) not in completed_tasks]
        if remaining_models:
            tasks.append((idx, row))
    
    if not tasks:
        print("✅ All tasks completed!")
        return
    
    print(f"🚀 Processing {len(tasks)} rows with {len(config.MODELS)} models")
    
    success_count = failed_count = 0
    batch_results = []
    
    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
        future_to_task = {executor.submit(process_row, task, completed_tasks): task[0] for task in tasks}
        
        for i, future in enumerate(as_completed(future_to_task)):
            try:
                results = future.result(timeout=60)
                if results:
                    batch_results.extend(results)
                    success_count += len([r for r in results if r['status'] == 'success'])
                    failed_count += len([r for r in results if r['status'] != 'success'])
                
                # Save batch periodically
                if len(batch_results) >= config.BATCH_SIZE:
                    save_to_csv(batch_results, results_file, append=True)
                    batch_results = []
                
                if (i + 1) % 10 == 0:
                    print_progress(i + 1, len(tasks), success_count, failed_count)
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_count += 1
    
    # Save remaining results
    if batch_results:
        save_to_csv(batch_results, results_file, append=True)
    
    print(f"✅ Processing complete! {success_count} success, {failed_count} failed")


def main():
    """Main rate analysis pipeline."""
    config.validate_config()
    print("🚀 Starting Rate Analysis Pipeline...")
    
    prompts_file = generate_rate_prompts()
    run_api_processing(prompts_file)


if __name__ == "__main__":
    main()
