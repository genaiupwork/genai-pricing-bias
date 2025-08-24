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
from prompts.age_bias import create_age_prompts


def clean_description(description: str) -> str:
    """Clean description using AI to remove age-related information."""
    if pd.isna(description) or description == 'Not available':
        return 'Not available'
    
    prompt = f"""Please remove all references to the individual's age and any details that directly or indirectly reveal their years of experience from the following Upwork profile listing. This includes explicit mentions of age, dates (like years or ranges), duration of work experience, education graduation years, or phrases indicating experience length (e.g., "10+ years," "since 2010," "over a decade," etc.). Please retain all other information and don't make any modification to the other parts of the listing.

Input: {description}"""
    
    try:
        result = call_api(prompt, config.PROFILE_CLEANING_MODEL, 0)
        if result and result.get('status') == 'success' and result.get('response'):
            return result['response'].strip()
    except Exception:
        pass
    
    # If cleaning fails, return original
    return description


def clean_all_descriptions(full_data):
    """Clean all descriptions with progress tracking."""
    import pickle
    checkpoint_file = config.CLEANING_CHECKPOINT
    
    # Load existing cleaned descriptions if available
    cleaned_descriptions = {}
    if file_exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'rb') as f:
                cleaned_descriptions = pickle.load(f)
            print(f"📋 Loaded {len(cleaned_descriptions)} already cleaned descriptions")
        except Exception as e:
            print(f"⚠️ Error loading checkpoint: {e}")
    
    # Clean remaining descriptions
    total_to_clean = len([idx for idx in full_data.index if idx not in cleaned_descriptions])
    if total_to_clean == 0:
        print("✅ All descriptions already cleaned")
        return cleaned_descriptions
    
    print(f"🧹 Cleaning {total_to_clean} descriptions...")
    
    for idx, row in full_data.iterrows():
        if idx not in cleaned_descriptions:
            cleaned_descriptions[idx] = clean_description(row.get('description'))
            
            # Save checkpoint every 100 descriptions
            if len(cleaned_descriptions) % 100 == 0:
                try:
                    with open(checkpoint_file, 'wb') as f:
                        pickle.dump(cleaned_descriptions, f)
                    print(f"💾 Saved checkpoint at {len(cleaned_descriptions)} descriptions")
                except Exception as e:
                    print(f"⚠️ Error saving checkpoint: {e}")
    
    # Final save
    try:
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(cleaned_descriptions, f)
        print(f"✅ Cleaning complete: {len(cleaned_descriptions)} descriptions processed")
    except Exception as e:
        print(f"⚠️ Error saving final checkpoint: {e}")
    
    return cleaned_descriptions


def generate_age_prompts():
    """Generate age bias prompts."""
    if file_exists(config.AGE_PROMPTS_FILE):
        print(f"✅ {config.AGE_PROMPTS_FILE} exists, skipping generation")
        return config.AGE_PROMPTS_FILE
    
    print("📝 Generating age bias prompts...")
    full_data = load_csv_data()
    
    # Clean descriptions with checkpointing
    cleaned_descriptions = clean_all_descriptions(full_data)
    
    new_rows = []
    for index, freelancer in full_data.iterrows():
        cleaned_desc = cleaned_descriptions.get(index, 'Not available')
        for age in config.AGE_VALUES:
            variations = create_age_prompts(freelancer, age, cleaned_desc)
            new_rows.extend(variations)
        
        if (index + 1) % 1000 == 0:
            print(f"Processed {index + 1}/{len(full_data)} freelancers")
    
    save_to_csv(new_rows, config.AGE_PROMPTS_FILE)
    
    print_summary("AGE BIAS GENERATION SUMMARY", {
        "Input freelancers": len(full_data),
        "Output prompts": len(new_rows),
        "Ages tested": f"{len(config.AGE_VALUES)} ({', '.join(map(str, config.AGE_VALUES))})",
        "Prompt variations": 3
    })
    
    return config.AGE_PROMPTS_FILE


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
                'original_hourly_rate': row['original_hourlyRate'],
                'age': row['age'],
                'prompt_variation': row['prompt_variation'],
                'source_file': row['source_file']
            })
            results.append(result)
    
    return results


def run_api_processing(prompts_file: str):
    """Run API processing with parallel execution."""
    df = pd.read_csv(prompts_file)
    completed_tasks = load_completed_tasks(config.AGE_RESULTS_FILE)
    
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
                    save_to_csv(batch_results, config.AGE_RESULTS_FILE, append=True)
                    batch_results = []
                
                if (i + 1) % 10 == 0:
                    print_progress(i + 1, len(tasks), success_count, failed_count)
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_count += 1
    
    # Save remaining results
    if batch_results:
        save_to_csv(batch_results, config.AGE_RESULTS_FILE, append=True)
    
    print(f"✅ Processing complete! {success_count} success, {failed_count} failed")


def main():
    """Main age bias pipeline."""
    config.validate_config()
    print("🚀 Starting Age Bias Pipeline...")
    
    prompts_file = generate_age_prompts()
    run_api_processing(prompts_file)


if __name__ == "__main__":
    main()