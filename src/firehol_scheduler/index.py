import contextlib
import glob
import os
import shutil
import tempfile

from git import Repo
from prolific_firehol import config


def handler(_, __):
    main_dir = tempfile.gettempdir() + "/"
    directory_path = os.path.join(main_dir, "blocklist-ipsets")
    clean_up(directory_path)
    Repo.clone_from("https://github.com/firehol/blocklist-ipsets.git", directory_path)
    ip_set_files = get_ipset_files(directory_path)
    traverse_ipset_files(ip_set_files)
    clean_up(directory_path)


def get_ipset_files(store: str) -> list:
    return glob.glob(f"{store}/*.ipset")


def traverse_ipset_files(ip_set_files):
    for i, ipset_file in enumerate(ip_set_files):
        upload_file(ipset_file, ipset_file.split("/")[-1])


def upload_file(file_name, file_key):
    file_store = config.FileStore(
        os.environ.get("BUCKET_NAME", "firehol-blocklist-storage-bucket")
    )
    try:
        file_store.upload(file_name, file_key)
    except Exception as e:
        print(f"Error uploading {file_name}: {e}")


def clean_up(file_path):
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(file_path)
