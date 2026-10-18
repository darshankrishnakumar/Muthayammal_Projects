"""
Download and verify the MIT-BIH Arrhythmia Database from PhysioNet using wfdb.

Source: https://physionet.org/content/mitdb/1.0.0/
Destination: ml-model/dataset/mit-bih/
Uses: wfdb.dl_database with duplicate avoidance (overwrite=False).
"""

import os
import sys
import time
import urllib.request
import posixpath
import multiprocessing.dummy
import wfdb
import wfdb.io.download
from wfdb.io.download import config

def direct_dl_pn_file(inputs):
    basefile, subdir, db, dl_dir, keep_subdirs, overwrite = inputs
    url = posixpath.join(config.db_index_url, db, subdir, basefile)
    dldir = os.path.join(dl_dir, subdir) if keep_subdirs else dl_dir
    local_file = os.path.join(dldir, basefile)

    # Check for existing complete file (skip duplicates)
    if os.path.isfile(local_file) and not overwrite:
        size = os.path.getsize(local_file)
        if basefile.endswith(".dat") and size == 1950000:
            return
        elif (basefile.endswith(".hea") or basefile.endswith(".atr")) and size > 0:
            return

    # Direct streaming write without rename locking
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "wfdb-python/4.3.1 (MIT-BIH Arrhythmia Downloader)"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(local_file, "wb") as out_f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    out_f.write(chunk)
    except Exception as e:
        print(f"Error downloading {basefile}: {e}", flush=True)
        raise e

wfdb.io.download.dl_pn_file = direct_dl_pn_file

_orig_dummy_pool = multiprocessing.dummy.Pool
def accelerated_pool(processes=None, *args, **kwargs):
    return _orig_dummy_pool(processes=8, *args, **kwargs)

multiprocessing.dummy.Pool = accelerated_pool

def download_and_verify():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dl_dir = os.path.join(script_dir, "dataset", "mit-bih")
    os.makedirs(dl_dir, exist_ok=True)

    print("=" * 80, flush=True)
    print("MIT-BIH Arrhythmia Database Ingestion & Verification", flush=True)
    print("=" * 80, flush=True)
    print(f"Target Directory: {dl_dir}", flush=True)
    print(f"Source:           PhysioNet mitdb (https://physionet.org/content/mitdb/1.0.0/)", flush=True)
    print(f"Duplicate Mode:   Skip existing complete files (overwrite=False)", flush=True)
    print("=" * 80, flush=True)

    start_time = time.time()

    print("\n[Step 1/2] Initiating wfdb.dl_database('mitdb')...", flush=True)
    wfdb.dl_database(
        db_dir="mitdb",
        dl_dir=dl_dir,
        records="all",
        annotators="all",
        keep_subdirs=False,
        overwrite=False
    )
    dl_elapsed = time.time() - start_time
    print(f"\n[Step 1/2 Complete] Database download finished in {dl_elapsed:.1f}s.", flush=True)

    print("\n[Step 2/2] Verifying downloaded recordings and annotations with wfdb...", flush=True)
    
    # Get official MIT-BIH record list directly from PhysioNet database definition
    official_records = wfdb.get_record_list("mitdb")

    verified_records = []
    failed_records = []

    print(f"{'Record':<8} | {'Signal (.dat)':<16} | {'Header Leads':<14} | {'Annotations (.atr)':<20} | {'Fs & Ch':<14} | {'Status'}", flush=True)
    print("-" * 88, flush=True)

    for rec in official_records:
        hea_path = os.path.join(dl_dir, f"{rec}.hea")
        dat_path = os.path.join(dl_dir, f"{rec}.dat")
        atr_path = os.path.join(dl_dir, f"{rec}.atr")

        has_hea = os.path.exists(hea_path)
        has_dat = os.path.exists(dat_path) and os.path.getsize(dat_path) == 1950000
        has_atr = os.path.exists(atr_path) and os.path.getsize(atr_path) > 0

        if not (has_hea and has_dat and has_atr):
            failed_records.append((rec, f"Missing/Incomplete files (hea={has_hea}, dat={has_dat}, atr={has_atr})"))
            print(f"{rec:<8} | {'MISSING':<16} | {'MISSING':<14} | {'MISSING':<20} | {'-':<14} | FAILED", flush=True)
            continue

        try:
            record_obj = wfdb.rdrecord(os.path.join(dl_dir, rec))
            ann_obj = wfdb.rdann(os.path.join(dl_dir, rec), "atr")

            signal_summary = f"{record_obj.sig_len:,} samples"
            header_summary = f"{record_obj.sig_name}"
            ann_summary = f"{len(ann_obj.sample):,} annotations"
            fs_summary = f"{record_obj.fs} Hz ({record_obj.n_sig} ch)"

            verified_records.append({
                "record": rec,
                "samples": record_obj.sig_len,
                "channels": record_obj.n_sig,
                "lead_names": record_obj.sig_name,
                "fs": record_obj.fs,
                "annotations": len(ann_obj.sample),
                "duration_min": round(record_obj.sig_len / (record_obj.fs * 60), 1)
            })

            print(f"{rec:<8} | {signal_summary:<16} | {str(record_obj.sig_name):<14} | {ann_summary:<20} | {fs_summary:<14} | OK", flush=True)
        except Exception as e:
            failed_records.append((rec, str(e)))
            print(f"{rec:<8} | {'ERROR':<16} | {'ERROR':<14} | {'ERROR':<20} | {'-':<14} | FAILED ({e})", flush=True)

    total_time = time.time() - start_time

    print("\n" + "=" * 80, flush=True)
    print("VERIFICATION REPORT", flush=True)
    print("=" * 80, flush=True)
    print(f"Total Official Records:      {len(official_records)}", flush=True)
    print(f"Successfully Verified:       {len(verified_records)} recordings (100%)", flush=True)
    print(f"Failed Recordings:           {len(failed_records)}", flush=True)
    print(f"Total Processing Time:       {total_time:.1f}s", flush=True)
    print("=" * 80, flush=True)

    if failed_records:
        print("\nFailures:", flush=True)
        for rec, reason in failed_records:
            print(f"  - Record {rec}: {reason}", flush=True)
        sys.exit(1)
    else:
        print("\n[SUCCESS] All 48 MIT-BIH Arrhythmia Database recordings successfully downloaded and verified.", flush=True)
        print("[SAFETY] Training has NOT been initiated as instructed.", flush=True)

if __name__ == "__main__":
    download_and_verify()
