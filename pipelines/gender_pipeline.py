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
from prompts.gender_bias import create_gender_prompts, load_name_mappings


def generate_gender_prompts():
    """Generate gender bias prompts for all freelancers."""
    if file_exists(config.GENDER_PROMPTS_FILE):
        print(f"✅ {config.GENDER_PROMPTS_FILE} exists, skipping generation")
        return config.GENDER_PROMPTS_FILE
    
    print("📝 Generating gender bias prompts...")
    full_data = load_csv_data()
    name_mapping = load_name_mappings()
    
    if not name_mapping:
        print("❌ Could not load name mappings. Please check names.csv file.")
        return None
    
    print(f"📊 Loaded name mappings for {len(name_mapping)} countries")
    print(f"👥 Processing {len(full_data)} freelancers")
    
    new_rows = []
    processed_count = 0
    
    for index, freelancer in full_data.iterrows():
        variations = create_gender_prompts(freelancer, name_mapping)
        new_rows.extend(variations)
        processed_count += 1
        
        if processed_count % 1000 == 0:
            print(f"Processed {processed_count}/{len(full_data)} freelancers")
    
    save_to_csv(new_rows, config.GENDER_PROMPTS_FILE)
    
    print_summary("GENDER BIAS GENERATION SUMMARY", {
        "Total freelancers": len(full_data),
        "Total prompts": len(new_rows),
        "Gender variations": "3 (male, female, unspecified)",
        "Prompt variations": "4 (base, gender_focused, aggressive_male_favored, aggressive_female_favored)",
        "Prompts per freelancer": "12"
    })
    
    return config.GENDER_PROMPTS_FILE


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
                'original_hourlyRate': row['original_hourlyRate'],
                'gender_variation': row['gender_variation'],
                'injected_name': row['injected_name'],
                'prompt_variation': row['prompt_variation'],
                'source_file': row['source_file']
            })
            results.append(result)
    
    return results


def run_api_processing(prompts_file: str):
    """Run API processing with parallel execution."""
    df = pd.read_csv(prompts_file)
    completed_tasks = load_completed_tasks(config.GENDER_RESULTS_FILE)
    
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
                    save_to_csv(batch_results, config.GENDER_RESULTS_FILE, append=True)
                    batch_results = []
                
                if (i + 1) % 10 == 0:
                    print_progress(i + 1, len(tasks), success_count, failed_count)
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_count += 1
    
    # Save remaining results
    if batch_results:
        save_to_csv(batch_results, config.GENDER_RESULTS_FILE, append=True)
    
    print(f"✅ Processing complete! {success_count} success, {failed_count} failed")


def main():
    """Main gender bias pipeline."""
    config.validate_config()
    print("🚀 Starting Gender Bias Pipeline...")
    
    prompts_file = generate_gender_prompts()
    if prompts_file:
        run_api_processing(prompts_file)


if __name__ == "__main__":
    main()