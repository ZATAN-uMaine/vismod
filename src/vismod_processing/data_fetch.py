import io
import os
import random
import time
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, HttpError

# Constants for the file paths and names
LOCAL_PREVIOUS_DOWNLOADS_FILE = "/tmp/vismod_previous_downloads.txt" # TODO: Change this to a more permanent location # noqa
LOCAL_TDMS_STORAGE_DIR = "/tmp/vismod_tdms_files"


def cleanTmpFiles():
    """
    Clean up the temporary files
    """
    if os.path.exists(LOCAL_TDMS_STORAGE_DIR):
        for file in os.listdir(LOCAL_TDMS_STORAGE_DIR):
            os.remove(os.path.join(LOCAL_TDMS_STORAGE_DIR, file))


def exponential_backoff_request(
    request_callable, max_retries=5, max_backoff=64
):
    """
    Retry a request with exponential backoff
    """
    for n in range(max_retries):
        try:
            response = request_callable().execute()
            return response

        # Catch API request errors
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
    """
    Fetch the list of previously downloaded files from the local file
    """
    if not os.path.exists(LOCAL_PREVIOUS_DOWNLOADS_FILE):
        return []
    with open(LOCAL_PREVIOUS_DOWNLOADS_FILE, "r") as file:
        return file.read().splitlines()


def update_downloads_file(filename):
    """
    Update the local file with the name of the downloaded file
    """
    with open(LOCAL_PREVIOUS_DOWNLOADS_FILE, "a") as file:
        file.write(filename + "\n")
    print(f"Updated local file with download: {filename}")


def list_tdms_files(service):
    """
    Query the Google api for a list of files,
    filter for only the .tdms, sort them
    """
    FOLDER_ID = os.getenv("FOLDER_ID")
    if not FOLDER_ID or len(FOLDER_ID) < 5:
        print("$FOLDER_ID not provided by environment")
        return None

    query = (
        f"'{FOLDER_ID}' in parents and "
        "(mimeType='application/octet-stream' or mimeType='text/plain') "
        "and trashed=false"
    )
    # Request the list of files from the drive
    results = exponential_backoff_request(
        lambda: service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name, createdTime)",
            orderBy="createdTime desc",
            pageSize=2,  # Request only the newest file
            supportsAllDrives=True,
        )
    )

    # If the request failed, return an empty list
    if not results:
        return []
    results = results.get("files", [])

    # Filter for only the .tdms files
    file_name_regex = re.compile("^.*\\.tdms$")
    file_list = []
    for file in results:
        name = file["name"]
        if file_name_regex.match(name):
            file_list.append(file)

    # Return the list of .tdms files
    return file_list


def tdmsDownload() -> list[str]:
    """
    Downloads TDMS files from Drive.
    Returns list of string file paths for any new TDMS files.
    """
    # Create the google api service
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY or len(GOOGLE_API_KEY) < 5:
        print("$GOOGLE_API_KEY not available from environment")
        return []

    previous_downloads = fetch_previous_downloads_from_file()
    service = build("drive", "v3", developerKey=GOOGLE_API_KEY)

    # Get the list of files
    data_file_list = list_tdms_files(service)

    # Create the local storage directory if it doesn't exist
    if not os.path.exists(LOCAL_TDMS_STORAGE_DIR):
        os.makedirs(LOCAL_TDMS_STORAGE_DIR)

    # Download the newest file if it hasn't been downloaded before
    local_files = []
    if len(data_file_list) > 0:
        item = data_file_list[0]
        if item["name"] not in previous_downloads:
            print(f"Downloading {item['name']}...")
            file_path = os.path.join(LOCAL_TDMS_STORAGE_DIR, item["name"])
            fh = io.FileIO(file_path, "wb")
            media = service.files().get_media(fileId=item["id"])
            downloader = MediaIoBaseDownload(fh, media)
            done = False

            # Download the file
            while not done:
                try:
                    status, done = downloader.next_chunk()
                    print(
                        f"Download {int(status.progress() * 100)}% complete."
                    )  # noqa

                # Catch API request errors
                except HttpError as e:
                    print(f"Failed to download {item['name']}: {e}")
                    fh.close()
                    os.remove(file_path)
                    break

            # If the download was successful, update the local file
            if done:
                update_downloads_file(item["name"])
                local_files.append(file_path)
    else:
        print("No new files to download.")

    return local_files


# Allow this file to be run standalone
if __name__ == "__main__":
    load_dotenv()
    new_files = tdmsDownload()
    print(new_files)
