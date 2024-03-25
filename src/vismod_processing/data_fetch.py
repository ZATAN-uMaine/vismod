import io
import os
import random
import time
import re
from dotenv import load_dotenv

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, HttpError

LOCAL_PREVIOUS_DOWNLOADS_FILE = "/tmp/vismod_previous_downloads.txt"
LOCAL_TDMS_STORAGE_DIR = "/tmp/vismod_tdms_files"


def exponential_backoff_request(
    request_callable, max_retries=5, max_backoff=64
):
    for n in range(max_retries):
        try:
            response = request_callable().execute()
            return response
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                wait_time = min((2**n) + random.random(), max_backoff)
                print(
                    f"Request failed with status {e.resp.status}, "
                    f"retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)
            else:
                print(
                    f"Request failed with status {e.resp.status}, "
                    f"error: {e}"
                )
                return None
    print("Maximum retries reached, giving up.")
    return None


def fetch_previous_downloads_from_file():
    if not os.path.exists(LOCAL_PREVIOUS_DOWNLOADS_FILE):
        return []
    with open(LOCAL_PREVIOUS_DOWNLOADS_FILE, "r") as file:
        return file.read().splitlines()


def update_downloads_file(filename):
    with open(LOCAL_PREVIOUS_DOWNLOADS_FILE, "a") as file:
        file.write(filename + "\n")
    print(f"Updated local file with download: {filename}")


def list_tdms_files(service):
    """
    Query the Google api for a list of files,
    filter for only the .tdms, sort them
    """
    FOLDER_ID = os.getenv("FOLDER_ID")
    query = (
        f"'{FOLDER_ID}' in parents and "
        "(mimeType='application/octet-stream' or mimeType='text/plain') "
        "and trashed=false"
    )
    results = exponential_backoff_request(
        lambda: service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name, createdTime)",
            orderBy="createdTime desc",  # Sort by createdTime, newest first
            pageSize=2,  # Request only the newest file
            supportsAllDrives=True,
        )
    )
    results = results.get("files", [])
    if not results:
        return []

    file_name_regex = re.compile("^.*\\.tdms$")
    file_list = []
    for file in results:
        name = file["name"]
        if file_name_regex.match(name):
            file_list.append(file)

    return file_list


def get_specified_tdms_file(service, file_name):
    """
    Finds a specified TDMS file by name.
    """
    FOLDER_ID = os.getenv("FOLDER_ID")
    query = (
        f"'{FOLDER_ID}' in parents and "
        "(mimeType='application/octet-stream' or mimeType='text/plain') "
        "and trashed=false"
        f"and name ='{file_name}'"
    )
    results = exponential_backoff_request(
        lambda: service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name, createdTime)",
            pageSize=2,  # Request only the newest file
            supportsAllDrives=True,
        )
    )
    results = results.get("files", [])
    if not results:
        return []
    return results


def tdmsDownload(target_file=None) -> list[str]:
    """
    Downloads TDMS files from Drive.
    Returns list of string file paths for any new TDMS files.
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    previous_downloads = fetch_previous_downloads_from_file()
    service = build("drive", "v3", developerKey=GOOGLE_API_KEY)

    data_file_list = []
    if target_file is not None:
        data_file_list = get_specified_tdms_file(service, target_file)
    else:
        data_file_list = list_tdms_files(service)

    if not os.path.exists(LOCAL_TDMS_STORAGE_DIR):
        os.makedirs(LOCAL_TDMS_STORAGE_DIR)

    local_files = []
    if len(data_file_list) > 0:
        item = data_file_list[0]  # Get the newest file
        if item["name"] not in previous_downloads:
            print(f"Downloading {item['name']}...")
            file_path = os.path.join(LOCAL_TDMS_STORAGE_DIR, item["name"])
            fh = io.FileIO(file_path, "wb")
            media = service.files().get_media(fileId=item["id"])
            downloader = MediaIoBaseDownload(fh, media)
            done = False
            while not done:
                try:
                    status, done = downloader.next_chunk()
                    print(
                        f"Download {int(status.progress() * 100)}% complete."
                    )  # noqa
                except HttpError as e:
                    print(f"Failed to download {item['name']}: {e}")
                    fh.close()
                    os.remove(file_path)  # Remove partially downloaded file
                    break  # Exit the download loop on error

            if done:
                # Update the local tracking file with the new download
                update_downloads_file(item["name"])
                local_files.append(file_path)
    else:
        print("No new files to download.")

    return local_files


# can run this file by itself
if __name__ == "__main__":
    load_dotenv()
    new_files = tdmsDownload()
    print(new_files)
