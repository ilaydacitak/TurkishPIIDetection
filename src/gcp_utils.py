import os
import io
import re
import ast
import sys
import time
import json
import dotenv
import base64
import importlib
from tqdm import tqdm
from pathlib import Path

from google import genai
from google.genai import types

## List all batch jobs
def list_all_batch_jobs(client):
    for job in client.batches.list():
        print(f"Job Name: {job.name}")
        print(f"Job Status: {job.state.name}")
        print(f"Job Creation Time: {job.create_time}")
        print("-" * 30)

## Get the status of a job
def get_job_status(client, job_name):
    job = client.batches.get(name=job_name)

    print(f"--- Job Details: {job.name} ---")
    print(f"Status: {job.state.name}")

    # If the job started of finished, show the logs
    if hasattr(job, 'completion_metrics'):
        print("\n[Metrics]")
        print(f"# requests: {job.completion_metrics.total_count}")
        print(f"Success: {job.completion_metrics.successful_count}")
        print(f"Fail: {job.completion_metrics.failed_count}")
        print(f"Waiting: {job.completion_metrics.pending_count}")

    # If the job status is JOB_STATE_FAILED
    if job.error:
        print("\n[Fail Report]")
        print(f"Fail Code: {job.error.code}")
        print(f"Fail Message: {job.error.message}")

    # Timestamps
    print(f"\nCreated: {job.create_time}")
    if hasattr(job, 'update_time'):
        print(f"Last Update: {job.update_time}")