import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from utils.data_loader import prepare_location_data
from utils.file_utils import file_exists, save_to_csv, load_completed_tasks
from utils.progress import print_progress, print_summary
from services.openrouter import call_api
from prompts.location_bias import create_location_prompts


def generate_location_prompts():
    """Generate location bias prompts."""
    if file_exists(config.LOCATION_PROMPTS_FILE):
        print(f"✅ {config.LOCATION_PROMPTS_FILE} exists, skipping generation")
        return config.LOCATION_PROMPTS_FILE
    
    print("📝 Generating location bias prompts...")
    us_freelancers, philippines_freelancers = prepare_location_data()
    
    new_rows = []
    
    # Process US freelancers
    print("Processing US freelancers...")
    for _, freelancer in us_freelancers.iterrows():
        for country in config.LOCATION_COUNTRIES:
            variations = create_location_prompts(freelancer, country)
            new_rows.extend(variations)
    
    # Process Philippines freelancers
    print("Processing Philippines freelancers...")
    for _, freelancer in philippines_freelancers.iterrows():
        for country in config.LOCATION_COUNTRIES:
            variations = create_location_prompts(freelancer, country)
            new_rows.extend(variations)
    
    save_to_csv(new_rows, config.LOCATION_PROMPTS_FILE)
    
    print_summary("LOCATION BIAS GENERATION SUMMARY", {
        "US freelancers": len(us_freelancers),
        "Philippines freelancers": len(philippines_freelancers),
        "Total prompts": len(new_rows),
        "Countries tested": f"{len(config.LOCATION_COUNTRIES)} ({', '.join(config.LOCATION_COUNTRIES)})",
        "Prompt variations": 4
    })
    
    return config.LOCATION_PROMPTS_FILE


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
                'original_country': row['original_country'],
                'modified_location': row['modified_location'],
                'version': row['version'],
                'source_file': row['source_file']
            })
            results.append(result)
    
    return results


def run_api_processing(prompts_file: str):
    """Run API processing with parallel execution."""
    df = pd.read_csv(prompts_file)
    completed_tasks = load_completed_tasks(config.LOCATION_RESULTS_FILE)
    
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
                    save_to_csv(batch_results, config.LOCATION_RESULTS_FILE, append=True)
                    batch_results = []
                
                if (i + 1) % 10 == 0:
                    print_progress(i + 1, len(tasks), success_count, failed_count)
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_count += 1
    
    # Save remaining results
    if batch_results:
        save_to_csv(batch_results, config.LOCATION_RESULTS_FILE, append=True)
    
    print(f"✅ Processing complete! {success_count} success, {failed_count} failed")


def main():
    """Main location bias pipeline."""
    config.validate_config()
    print("🚀 Starting Location Bias Pipeline...")
    
    prompts_file = generate_location_prompts()
    run_api_processing(prompts_file)


if __name__ == "__main__":
    main()