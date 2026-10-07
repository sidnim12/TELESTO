"""Main entry point for generating multiple batches.

Equivalent to Generate_Production_Batch_data_V4.m.
"""

import numpy as np
from .simulation_runner import indpensim_run
from .batch_records import generate_batch_records


def run_production(batch_run_flags=None, save_batch=True, output_filename='IndPenSim_V2_export'):
    """Generate multiple batches for a production phase.

    Parameters:
        batch_run_flags: Dict with batch configuration. If None, uses defaults.
            Keys:
            - Batch_fault_order_reference: list of fault codes
            - Control_strategy: list of control strategy flags
            - Batch_length: list of batch length flags
            - Raman_spec: list of Raman spec flags
        save_batch: Whether to save results.
        output_filename: Base filename for output.

    Returns:
        raw_batch_data: Dict of batch results.
        batch_records: Cleaned batch records.
    """
    if batch_run_flags is None:
        batch_run_flags = {
            'Batch_fault_order_reference': [0, 1],
            'Control_strategy': [0, 1],
            'Batch_length': [1, 0],
            'Raman_spec': [1, 2],
        }

    Num_of_Batches = len(batch_run_flags['Batch_fault_order_reference'])
    Operational_days = 336
    Bioreactor_turn_around_time = 3
    Production_Phase_in_years = (Num_of_Batches * (11 + 3)) / Operational_days

    raw_batch_data = {}
    summary_of_campaign = []

    for Batch_no in range(1, Num_of_Batches + 1):
        batch_name = f'Batch_{Batch_no:02d}'
        print(f'\n=== Running {batch_name} ===')

        Xref = indpensim_run(Batch_no, batch_run_flags)
        raw_batch_data[batch_name] = Xref

        campaign_row = [
            Xref.Stats.Penicllin_harvested_during_batch,
            Xref.Stats.Penicllin_harvested_end_of_batch,
            Xref.Stats.Penicllin_yield_total,
            Xref.Fg.t[-1] / 24.0
        ]
        summary_of_campaign.append(campaign_row)

        # Check if production phase time exceeded
        total_days = sum(np.ceil(row[3]) for row in summary_of_campaign)
        total_days += Batch_no * Bioreactor_turn_around_time
        if total_days > Production_Phase_in_years * Operational_days:
            print(f'Production phase limit reached after batch {Batch_no}')
            break

    # Generate batch records and CSV
    batch_records = generate_batch_records(raw_batch_data, output_filename,
                                           batch_run_flags)

    if save_batch:
        try:
            import pickle
            save_file = f'{output_filename}.pkl'
            with open(save_file, 'wb') as f:
                pickle.dump({
                    'batch_records': batch_records,
                    'raw_batch_data': raw_batch_data,
                    'summary': summary_of_campaign
                }, f)
            print(f'Saved: {save_file}')
        except Exception as e:
            print(f'Warning: Could not save pickle file: {e}')

    return raw_batch_data, batch_records


def main():
    """Entry point for command-line execution."""
    print('IndPenSim V2.01 - Python Translation')
    print('Generating production batch data...\n')

    raw_batch_data, batch_records = run_production()

    print('\n=== Production Complete ===')
    print(f'Generated {len(raw_batch_data)} batches')


if __name__ == '__main__':
    main()
