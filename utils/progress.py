import time

def print_progress(completed: int, total: int, success: int, failed: int):
    """Print progress update."""
    success_rate = (success / (success + failed) * 100) if (success + failed) > 0 else 0
    print(f"📊 Progress: {completed}/{total} | ✅ {success} success | ❌ {failed} failed | 📈 {success_rate:.1f}% success rate")


def print_summary(title: str, data: dict):
    """Print summary statistics."""
    print(f"\n{'='*60}")
    print(title)
    print('='*60)
    for key, value in data.items():
        if isinstance(value, (int, float)):
            print(f"{key}: {value:,}" if isinstance(value, int) else f"{key}: {value:.1f}")
        else:
            print(f"{key}: {value}")
    print('='*60)
