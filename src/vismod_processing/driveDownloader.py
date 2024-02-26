from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, HttpError
import io
import os
from dotenv import load_dotenv
import random
import time

# Local directory to save the downloaded files
local_directory = "tdms_files"
if not os.path.exists(local_directory):
    os.makedirs(local_directory)

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")


LOCAL_PREVIOUS_DOWNLOADS_FILE = "previous_downloads.txt"


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


def tdmsDownload(GOOGLE_API_KEY, local_directory):
    previous_downloads = fetch_previous_downloads_from_file()
    service = build("drive", "v3", developerKey=GOOGLE_API_KEY)

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
            pageSize=1,  # Request only the newest file
            supportsAllDrives=True,
        )
    )

    if not results:
        print("No files to download.")
        return

    items = results.get("files", [])
    if items:
        item = items[0]  # Get the newest file
        if item["name"] not in previous_downloads:
            print(f"Downloading {item['name']}...")
            file_path = os.path.join(local_directory, item["name"])
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
    else:
        print("No new files to download.")


tdmsDownload(GOOGLE_API_KEY, local_directory)
