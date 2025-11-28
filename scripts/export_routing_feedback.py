#!/usr/bin/env python3
"""
Export routing feedback data for model fine-tuning.

This script exports collected user feedback on routing decisions to JSONL format,
suitable for training the local classifier model.

Usage:
    uv run python scripts/export_routing_feedback.py --output training_data.jsonl
    uv run python scripts/export_routing_feedback.py --corrections-only
    uv run python scripts/export_routing_feedback.py --stats
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Project root setup
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.database.connection import AsyncSessionLocal, init_db
from api.database.repositories.feedback_repo import FeedbackRepository


async def get_stats():
    """Print feedback collection statistics."""
    async with AsyncSessionLocal() as db:
        repo = FeedbackRepository(db)
        stats = await repo.get_stats()
        
        print("\n📊 Routing Feedback Statistics")
        print("=" * 40)
        print(f"Total records:      {stats['total_records']:,}")
        print(f"Pending review:     {stats['pending_review']:,}")
        print(f"Confirmed correct:  {stats['confirmed_correct']:,}")
        print(f"User corrections:   {stats['corrected']:,}")
        print(f"Already exported:   {stats['exported']:,}")
        print("=" * 40)
        
        # Calculate export potential
        unexported = stats['confirmed_correct'] + stats['corrected'] - stats['exported']
        print(f"Available for export: {max(0, unexported):,}")


async def export_feedback(
    output_path: str,
    corrections_only: bool = False,
    include_confirmed: bool = True,
    mark_exported: bool = True
):
    """Export feedback records to JSONL format."""
    async with AsyncSessionLocal() as db:
        repo = FeedbackRepository(db)
        
        records = await repo.get_for_training_export(
            include_corrections_only=corrections_only,
            include_confirmed_correct=include_confirmed,
            unexported_only=True
        )
        
        if not records:
            print("No new records to export.")
            return
        
        # Convert to training examples
        examples = []
        corrections_count = 0
        confirmed_count = 0
        
        for record in records:
            training_examples = record.to_training_example()
            for ex in training_examples:
                examples.append(ex)
            
            if record.corrected_tools:
                corrections_count += 1
            else:
                confirmed_count += 1
        
        # Write to JSONL file
        output_file = Path(output_path)
        with open(output_file, 'w') as f:
            for example in examples:
                f.write(json.dumps(example) + '\n')
        
        print(f"\n✅ Exported {len(examples)} training examples to {output_file}")
        print(f"   - From {len(records)} feedback records")
        print(f"   - Corrections: {corrections_count}")
        print(f"   - Confirmed correct: {confirmed_count}")
        
        # Mark as exported
        if mark_exported:
            record_ids = [r.id for r in records]
            await repo.mark_as_exported(record_ids)
            await db.commit()
            print(f"   - Marked {len(record_ids)} records as exported")


async def main():
    parser = argparse.ArgumentParser(description='Export routing feedback for model training')
    parser.add_argument('--output', '-o', type=str, default='routing_feedback.jsonl',
                        help='Output file path (JSONL format)')
    parser.add_argument('--corrections-only', action='store_true',
                        help='Only export records with user corrections')
    parser.add_argument('--no-mark-exported', action='store_true',
                        help='Do not mark records as exported')
    parser.add_argument('--stats', action='store_true',
                        help='Show statistics only, do not export')
    
    args = parser.parse_args()
    
    # Initialize database
    await init_db()
    
    if args.stats:
        await get_stats()
    else:
        await export_feedback(
            output_path=args.output,
            corrections_only=args.corrections_only,
            mark_exported=not args.no_mark_exported
        )


if __name__ == '__main__':
    asyncio.run(main())
