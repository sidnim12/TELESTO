"""Generate batch records from simulation output data.

Equivalent to Generate_Batch_records.m.
"""

import numpy as np
import csv
from pathlib import Path


def generate_batch_records(raw_batch_data, batches_file_name, batch_run_flags=None):
    """Generate batch records and export to CSV.

    Parameters:
        raw_batch_data: Dict of batch results {batch_name: Xref}.
        batches_file_name: Base filename for output files.
        batch_run_flags: Batch run configuration flags.

    Returns:
        batch_records: Cleaned batch data dict.
    """
    all_batches = list(raw_batch_data.keys())
    num_of_batches = len(all_batches)

    # Fields to remove from export
    fields_to_remove = {
        'sc', 'abc', 'a0', 'a1', 'a3', 'a4',
        'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8', 'n9',
        'nm', 'phi0', 'Culture_age', 'mup', 'mux', 'X_CER',
        'mu_X_calc', 'mu_P_calc', 'F_discharge_cal', 'CO2_d',
        'NH3', 'PAA', 'Viscosity', 'X', 'PRBS_noise_addition'
    }

    all_batch_stats = []
    all_batch_data = []

    for batch_no in range(1, num_of_batches + 1):
        batch_ref = all_batches[batch_no - 1]
        batch = raw_batch_data[batch_ref]

        # Get exportable variables
        all_vars = [attr for attr in dir(batch)
                    if not attr.startswith('_') and attr not in fields_to_remove
                    and attr != 'Stats' and attr != 'Raman_Spec'
                    and hasattr(getattr(batch, attr), 't')]

        # Build data matrix
        if all_vars:
            first_var = getattr(batch, all_vars[0])
            batch_data = first_var.t.reshape(-1, 1)  # Time column

            for var_name in all_vars:
                channel = getattr(batch, var_name)
                batch_data = np.column_stack([batch_data, channel.y])

        # Fault reference
        if np.sum(batch.Fault_ref.y) == 0:
            batch_fault_ref = np.zeros(len(batch.Fault_ref.y))
        else:
            batch_fault_ref = np.ones(len(batch.Fault_ref.y))

        # Add batch ID and fault flag
        batch_id = np.full(batch_data.shape[0], batch_no)
        batch_data = np.column_stack([batch_data, batch_fault_ref, batch_id])

        # Add Raman data if present
        if hasattr(batch, 'Raman_Spec') and hasattr(batch.Raman_Spec, 'Intensity'):
            batch_data = np.column_stack([batch_data,
                                          batch.Raman_Spec.Intensity.T])

        all_batch_data.append(batch_data)

        # Statistics
        stats = [
            batch_no,
            -batch.Stats.Penicllin_harvested_during_batch / 1000,
            batch.Stats.Penicllin_harvested_end_of_batch / 1000,
            batch.Stats.Penicllin_yield_total / 1000,
            batch_fault_ref[-1]
        ]
        all_batch_stats.append(stats)
        print(stats)

    # Write main CSV
    if all_batch_data:
        combined_data = np.vstack(all_batch_data)

        # Build headers
        headers = ['Time (h)'] + all_vars + ['Fault flag', 'Batch_ref']
        if hasattr(batch, 'Raman_Spec') and hasattr(batch.Raman_Spec, 'Wavelength'):
            raman_headers = [str(w) for w in batch.Raman_Spec.Wavelength]
            headers.extend(raman_headers)

        csv_file = f'{batches_file_name}.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in combined_data:
                writer.writerow(row)
        print(f'Written: {csv_file}')

    # Write statistics CSV
    stats_headers = ['Batch ref', 'Penicllin_harvested_during_batch(kg)',
                     'Penicllin_harvested_end_of_batch (kg)',
                     'Penicllin_yield_total (kg)', 'Fault ref(0-NoFault 1-Fault)']
    stats_file = f'{batches_file_name}_Statistics.csv'
    with open(stats_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(stats_headers)
        for row in all_batch_stats:
            writer.writerow(row)
    print(f'Written: {stats_file}')

    # Clean batch records (remove internal fields)
    batch_records = {}
    for batch_ref in all_batches:
        batch = raw_batch_data[batch_ref]

        # Remove NaN entries from offline measurements
        if hasattr(batch, 'PAA_offline'):
            mask = ~np.isnan(batch.PAA_offline.y)
            batch.PAA_offline.y = batch.PAA_offline.y[mask]
            batch.PAA_offline.t = batch.PAA_offline.t[mask]
        if hasattr(batch, 'P_offline'):
            mask = ~np.isnan(batch.P_offline.y)
            batch.P_offline.y = batch.P_offline.y[mask]
            batch.P_offline.t = batch.P_offline.t[mask]
        if hasattr(batch, 'NH3_offline'):
            mask = ~np.isnan(batch.NH3_offline.y)
            batch.NH3_offline.y = batch.NH3_offline.y[mask]
            batch.NH3_offline.t = batch.NH3_offline.t[mask]
        if hasattr(batch, 'X_offline'):
            mask = ~np.isnan(batch.X_offline.y)
            batch.X_offline.y = batch.X_offline.y[mask]
            batch.X_offline.t = batch.X_offline.t[mask]
        if hasattr(batch, 'Viscosity_offline'):
            mask = ~np.isnan(batch.Viscosity_offline.y)
            batch.Viscosity_offline.y = batch.Viscosity_offline.y[mask]
            batch.Viscosity_offline.t = batch.Viscosity_offline.t[mask]

        # Convert O2 to percent
        if hasattr(batch, 'O2'):
            batch.O2.y = batch.O2.y * 100

        batch_records[batch_ref] = batch

    return batch_records
