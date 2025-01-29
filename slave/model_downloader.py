import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from time import sleep

import requests
import tqdm
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, RequestException, Timeout
from tqdm.contrib.concurrent import thread_map

base = os.environ.get("HF_ENDPOINT") or "https://huggingface.co"


class ModelDownloader:
    def __init__(self, max_retries=5):
        """
        Initialize the ModelDownloader.

        :param max_retries: Maximum number of retries for the underlying HTTP session.
        """
        self.max_retries = max_retries
        self.session = self.get_session()
        # Add a chunk_callback you can set from outside to track progress
        # Each time a download chunk is saved, we call: self.chunk_callback(filename, ratio)
        # ratio is a float from 0.0 to 1.0
        self.chunk_callback = None  
        self.progress_bar = None

    def get_session(self):
        """
        Create a requests Session, mounting an HTTPAdapter for retries if max_retries > 0.
        If HF_USER and HF_PASS are set, uses basic auth.
        If an HF_TOKEN is available, sets a Bearer token.
        """
        session = requests.Session()
        if self.max_retries:
            session.mount('https://cdn-lfs.huggingface.co', HTTPAdapter(max_retries=self.max_retries))
            session.mount('https://huggingface.co', HTTPAdapter(max_retries=self.max_retries))

        if os.getenv('HF_USER') is not None and os.getenv('HF_PASS') is not None:
            session.auth = (os.getenv('HF_USER'), os.getenv('HF_PASS'))

        # Attempt to load token from huggingface_hub
        token = None
        try:
            from huggingface_hub import get_token
            token = get_token()
        except ImportError:
            pass

        # Or load from environment variable
        if token is None:
            token = os.getenv("HF_TOKEN")

        if token is not None:
            session.headers = {'authorization': f'Bearer {token}'}

        return session

    def sanitize_model_and_branch_names(self, model, branch):
        """
        Normalize the model and branch names, stripping trailing slashes,
        pulling out branch from 'model:branch' if present, and validating branch.
        """
        if model.endswith('/'):
            model = model[:-1]

        if model.startswith(base + '/'):
            model = model[len(base) + 1:]

        # If model is in the form "org/repo:branch", parse the branch
        model_parts = model.split(":")
        model = model_parts[0] if len(model_parts) > 0 else model
        branch = model_parts[1] if len(model_parts) > 1 else branch

        if branch is None:
            branch = "main"
        else:
            pattern = re.compile(r"^[a-zA-Z0-9._-]+$")
            if not pattern.match(branch):
                raise ValueError(
                    "Invalid branch name. Only alphanumeric characters, period, underscore and dash are allowed.")

        return model, branch

    def get_download_links_from_huggingface(self, model, branch,
                                            text_only=False,
                                            specific_file=None,
                                            exclude_pattern=None):
        """
        Query HuggingFace's model tree API to build a list of relevant files to download.
        Returns: (links, sha256, is_lora, is_llamacpp)
        """
        session = self.session
        page = f"/api/models/{model}/tree/{branch}"
        cursor = b""

        links = []
        sha256 = []
        classifications = []
        has_pytorch = False
        has_pt = False
        has_gguf = False
        has_safetensors = False
        is_lora = False

        while True:
            url = f"{base}{page}" + (f"?cursor={cursor.decode()}" if cursor else "")
            r = session.get(url, timeout=10)
            r.raise_for_status()
            content = r.content

            dict_data = json.loads(content)
            if len(dict_data) == 0:
                break

            for item in dict_data:
                fname = item['path']
                if specific_file not in [None, ''] and fname != specific_file:
                    continue

                # Exclude files matching the exclude pattern
                if exclude_pattern is not None and re.match(exclude_pattern, fname):
                    continue

                # Check if it's an adapter (LoRA) file
                if not is_lora and fname.endswith(('adapter_config.json', 'adapter_model.bin')):
                    is_lora = True

                # Classify file types
                is_pytorch = re.match(r"(pytorch|adapter|gptq)_model.*\.bin", fname)
                is_safetensors = re.match(r".*\.safetensors", fname)
                is_pt = re.match(r".*\.pt", fname)
                is_gguf = re.match(r".*\.gguf", fname)
                is_tiktoken = re.match(r".*\.tiktoken", fname)
                is_tokenizer = re.match(r"(tokenizer|ice|spiece).*\.model", fname) or is_tiktoken
                is_text = re.match(r".*\.(txt|json|py|md)", fname) or is_tokenizer

                if any((is_pytorch, is_safetensors, is_pt, is_gguf, is_tokenizer, is_text)):
                    # If the file uses LFS, store its SHA256
                    if 'lfs' in item:
                        sha256.append([fname, item['lfs']['oid']])

                    # If it's a text file or tokenizer
                    if is_text:
                        links.append(f"{base}/{model}/resolve/{branch}/{fname}")
                        classifications.append('text')
                        continue

                    # If text_only is True, skip non-text files
                    if not text_only:
                        links.append(f"{base}/{model}/resolve/{branch}/{fname}")
                        if is_safetensors:
                            has_safetensors = True
                            classifications.append('safetensors')
                        elif is_pytorch:
                            has_pytorch = True
                            classifications.append('pytorch')
                        elif is_pt:
                            has_pt = True
                            classifications.append('pt')
                        elif is_gguf:
                            has_gguf = True
                            classifications.append('gguf')

            # Build the next cursor
            last_path = dict_data[-1]["path"]
            cursor = base64.b64encode(f'{{"file_name":"{last_path}"}}'.encode()) + b':50'
            cursor = base64.b64encode(cursor)
            cursor = cursor.replace(b'=', b'%3D')

        # If both pytorch/pt/gguf & safetensors exist, keep only safetensors
        if (has_pytorch or has_pt or has_gguf) and has_safetensors:
            has_gguf = False
            for i in range(len(classifications) - 1, -1, -1):
                if classifications[i] in ['pytorch', 'pt', 'gguf']:
                    links.pop(i)

        # For GGUF, try to pick Q4_K_M if no specific_file is given
        if has_gguf and specific_file is None:
            has_q4km = any('q4_k_m' in link.lower() for link in links)
            if has_q4km:
                # Remove all .gguf except those containing q4_k_m
                for i in range(len(classifications) - 1, -1, -1):
                    if 'q4_k_m' not in links[i].lower():
                        links.pop(i)
            else:
                # If no Q4_K_M is found, remove all .gguf
                for i in range(len(classifications) - 1, -1, -1):
                    if links[i].lower().endswith('.gguf'):
                        links.pop(i)

        is_llamacpp = has_gguf and (specific_file is not None)
        return links, sha256, is_lora, is_llamacpp

    def get_output_folder(self, model, branch, is_lora, is_llamacpp=False, model_dir=None):
        """
        Force all downloads to /mnt/storagedrive/Storage/TextGenStorage/models/gguf/
        regardless of model or branch.
        """
        return Path("/mnt/storagedrive/Storage/TextGenStorage/models/gguf")

    def get_single_file(self, url, output_folder, start_from_scratch=False):
        """
        Download a single file from `url` into `output_folder`, possibly resuming 
        if the file partially exists (and start_from_scratch=False).
        """
        filename = Path(url.rsplit('/', 1)[1])
        output_path = output_folder / filename

        max_retries = 7
        attempt = 0
        while attempt < max_retries:
            attempt += 1
            session = self.session
            headers = {}
            mode = 'wb'

            try:
                # If partial file exists and not re-downloading
                if output_path.exists() and not start_from_scratch:
                    r = session.get(url, stream=True, timeout=20)
                    total_size = int(r.headers.get('content-length', 0))
                    if output_path.stat().st_size >= total_size:
                        return

                    headers = {'Range': f'bytes={output_path.stat().st_size}-'}
                    mode = 'ab'

                with session.get(url, stream=True, headers=headers, timeout=30) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    block_size = 1024 * 1024  # 1MB
                    filename_str = str(filename)

                    tqdm_kwargs = {
                        'total': total_size,
                        'unit': 'B',
                        'unit_scale': True,
                        'unit_divisor': 1024,
                        'bar_format': '{desc}{percentage:3.0f}%|{bar:50}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]',
                        'desc': f"{filename_str}: "
                    }

                    with open(output_path, mode) as f:
                        with tqdm.tqdm(**tqdm_kwargs) as t:
                            downloaded = 0
                            for data in r.iter_content(block_size):
                                f.write(data)
                                t.update(len(data))
                                downloaded += len(data)

                                # >>> Chunk callback to track progress <<<
                                if self.chunk_callback and total_size > 0:
                                    ratio = float(downloaded) / float(total_size)
                                    self.chunk_callback(filename_str, ratio)

                break  # success, exit retry loop

            except (RequestException, ConnectionError, Timeout) as e:
                print(f"Error downloading {filename}: {e}.")
                print(f"That was attempt {attempt}/{max_retries}.", end=' ')
                if attempt < max_retries:
                    print(f"Retry begins in {2 ** attempt} seconds.")
                    sleep(2 ** attempt)
                else:
                    print("Failed to download after the maximum number of attempts.")

    def start_download_threads(self, file_list, output_folder, start_from_scratch=False, threads=4):
        """
        Download all files in file_list concurrently using thread_map.
        """
        thread_map(
            lambda url: self.get_single_file(url, output_folder, start_from_scratch=start_from_scratch),
            file_list,
            max_workers=threads,
            disable=True  # disable tqdm's extra console output
        )

    def download_model_files(self, model, branch, links, sha256, output_folder,
                             progress_bar=None,
                             start_from_scratch=False,
                             threads=4,
                             specific_file=None,
                             is_llamacpp=False):
        """
        Main method to download model files to output_folder with optional concurrency.
        Writes a 'huggingface-metadata.txt' if not a llama.cpp model.
        """
        self.progress_bar = progress_bar

        # Make sure folder exists
        output_folder.mkdir(parents=True, exist_ok=True)

        # If not is_llamacpp, store some metadata about the download
        if not is_llamacpp:
            metadata = (
                f"url: https://huggingface.co/{model}\n"
                f"branch: {branch}\n"
                f"download date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            sha256_str = '\n'.join([f'    {item[1]} {item[0]}' for item in sha256])
            if sha256_str:
                metadata += f"sha256sum:\n{sha256_str}\n"

            (output_folder / 'huggingface-metadata.txt').write_text(metadata)

        # Print status
        if specific_file:
            print(f"Downloading {specific_file} to {output_folder}")
        else:
            print(f"Downloading the model to {output_folder}")

        # Actually download
        self.start_download_threads(links, output_folder, start_from_scratch=start_from_scratch, threads=threads)

    def check_model_files(self, model, branch, links, sha256, output_folder):
        """
        Validate checksums of existing model files in output_folder.
        """
        validated = True
        for item in sha256:
            fpath = output_folder / item[0]
            if not fpath.exists():
                print(f"The following file is missing: {fpath}")
                validated = False
                continue

            with open(fpath, "rb") as f:
                file_bytes = f.read()
                file_hash = hashlib.sha256(file_bytes).hexdigest()
                if file_hash != item[1]:
                    print(f"Checksum failed: {item[0]}  {item[1]}")
                    validated = False
                else:
                    print(f"Checksum validated: {item[0]}  {item[1]}")

        if validated:
            print('[+] Validated checksums of all model files!')
        else:
            print('[-] Invalid checksums. Rerun download-model.py with the --clean flag.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('MODEL', type=str, default=None, nargs='?')
    parser.add_argument('--branch', type=str, default='main', help='Name of the Git branch to download from.')
    parser.add_argument('--threads', type=int, default=4, help='Number of files to download simultaneously.')
    parser.add_argument('--text-only', action='store_true', help='Only download text files (txt/json).')
    parser.add_argument('--specific-file', type=str, default=None, help='Name of the specific file to download.')
    parser.add_argument('--exclude-pattern', type=str, default=None, help='Regex pattern to exclude files.')
    parser.add_argument('--output', type=str, default=None, help='Ignore: we now force a specific folder.')
    parser.add_argument('--model-dir', type=str, default=None, help='Ignore: we now force a specific folder.')
    parser.add_argument('--clean', action='store_true', help='Do not resume any partial downloads.')
    parser.add_argument('--check', action='store_true', help='Validate previously downloaded files.')
    parser.add_argument('--max-retries', type=int, default=5, help='Max retry attempts for each file download.')
    args = parser.parse_args()

    branch = args.branch
    model = args.MODEL
    specific_file = args.specific_file
    exclude_pattern = args.exclude_pattern

    if model is None:
        print("Error: Please specify the model you'd like to download (e.g. 'facebook/opt-1.3b').")
        sys.exit(1)

    downloader = ModelDownloader(max_retries=args.max_retries)

    try:
        model, branch = downloader.sanitize_model_and_branch_names(model, branch)
    except ValueError as err_branch:
        print(f"Error: {err_branch}")
        sys.exit(1)

    # Collect the files to download
    links, sha256, is_lora, is_llamacpp = downloader.get_download_links_from_huggingface(
        model, branch,
        text_only=args.text_only,
        specific_file=specific_file,
        exclude_pattern=exclude_pattern
    )

    # Force everything to the same folder
    output_folder = downloader.get_output_folder(model, branch, is_lora, is_llamacpp=is_llamacpp)

    if args.check:
        downloader.check_model_files(model, branch, links, sha256, output_folder)
    else:
        downloader.download_model_files(
            model,
            branch,
            links,
            sha256,
            output_folder,
            specific_file=specific_file,
            threads=args.threads,
            is_llamacpp=is_llamacpp,
            start_from_scratch=args.clean
        )
