import os.path

import cython

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from tqdm import tqdm

# import istarmap # import to apply patch
from multiprocessing import Pool
import threading

ALL_FILE_FOLDERS = {
    # "URAP3D_STL": "1P0k67JaVkJRyFysUC_G8bKmRQQD_TKhq",
    # "CAD_PARTS_FOLDER": "1kvid8nlRhSFrnIzrZbjt5uOOuEixPBpN",
    "PARTS_0_1_3950": "1rIlKhyHHyQ55RW8igH7ywnH0hXMLDwA_",
    "PARTS_0_3951_5450": "1cKpVz3Vol2F8-i-V6ixnGkH94Al8VsjP",
    "PARTS_0_5451_9606": "1CkJ30EDPfz8g0okPQPW19vkoqzdClYg8",
    "PARTS_1_1_2500": "1j_J4PxkVZlfP7kqhP4JwyUG29bYVLbNJ",
    "PARTS_1_2501_7500": "155SmkUlp2Z8nVb_VjUgoTNPRMO1jl9gQ",
    "PARTS_1_7501_11227": "1ZtDlxIVOq_B6gbryrtXZTQXJpv3bodEv",
    "PARTS_2_1_3500": "1Ju7G3RB-KLtC4i8drcGdN2YEcUczueov",
    "PARTS_2_3501_7500": "1kUIWVdyryIcETdOQik29T1DPVZAWJ9-a",
    "PARTS_2_7501_11076": "1ZwfiDKMlHZgpgZOOJhqBUwQnBFjXQhZd",
    "PARTS_3_1_5500": "19rsrWC1dmBtCD9uPJCC5QdwOWD7VYeY7",
    "PARTS_3_5501_10844": "1GOTtPLaxOlAguBdNuKfpeLn8UuA5OCxA",
    "PARTS_4_1_5500": "1xXbNZ2fGW_9wz3ezM84ckqCq91cTySwR",
    "PARTS_4_5501_8000": "1I5fMkCzS26gT4yjnd5VIB80ga2glWzNc",
    "PARTS_4_8001_10154": "1RlXw5gWgBt9Ce2nHgrdPy-1i5dCPKf-7",
}

BINVOX_MIMETYPE = 'application/octet-stream'
STL_MIMETYPE = 'application/vnd.ms-pki.stl'
FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'

ENTRIES_PER_PAGE = 1000 

MAX_PAGES = 1000 # how many pages to go per folder, set to 1 for testing

NUM_THREADS = 60 # just put the max that works?? i don't know what number is maximum, but can find by doubling

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive']

def load_google_api_key(cwd):
    # load api key from .env
    with open(os.path.join(cwd, ".env"), "r") as f:
        for line in f.readlines():
            if line.startswith("GOOGLE_API_KEY"):
                return line.split("=")[1].strip()

def token_login():

    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_files_directly_in(folderId, service, mimeType=None, nextPageToken=None):

    # Call the Drive v3 API
    query = f"'{folderId}' in parents"  # needs space!
    if mimeType:
        query += f" and mimeType = '{mimeType}'"
    # query = f"'{FOLDER_ID}' in parents and mimeType = '{binvox_mimeType}'" # binvox
    results = []
    try:
        results = service.files().list(
            pageSize=ENTRIES_PER_PAGE,
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=nextPageToken).execute()
    except HttpError:
        print(f"Error for token {nextPageToken}")

    return results


def download_all_binvox_stl_files_in(folderId, service):
    # Assumes structure is "Binvox_files_default_res" and "rotated_files"
    direct_files = get_files_directly_in(folderId, service)
    binvox_folder = [f for f in direct_files.get('files', []) if f['mimeType'] == FOLDER_MIMETYPE and "Binvox" in f['name']][0]
    stl_folder = [f for f in direct_files.get('files', []) if f['mimeType'] == FOLDER_MIMETYPE and "rotated" in f['name']][0]
    
    print(f"binvox folder: {binvox_folder}, stl folder: {stl_folder}")
    
    # for binvox_file in tqdm(get_all_files_of_type(binvox_folder['id'], service, BINVOX_MIMETYPE)):
    #     download_file(binvox_folder['id'], binvox_file['id'], service, BINVOX_MIMETYPE)
        
    # for stl_file in tqdm(get_all_files_of_type(stl_folder['id'], service, STL_MIMETYPE)):
    #     download_file(stl_folder['id'], stl_file['id'], service, STL_MIMETYPE)
    
    
    # use multiprocessing to parallelize the above loops
    with Pool(NUM_THREADS) as p:
        binvox_iter = [(binvox_folder['id'], binvox_file['id'], service, BINVOX_MIMETYPE) for binvox_file in get_all_files_of_type(binvox_folder['id'], service, BINVOX_MIMETYPE)]
        stl_iter = [(stl_folder['id'], stl_file['id'], service, STL_MIMETYPE) for stl_file in get_all_files_of_type(stl_folder['id'], service, STL_MIMETYPE)]
        
        all_iter = binvox_iter + stl_iter
        p.starmap(download_file, tqdm(all_iter))
        
    
    

def get_all_files_of_type(folderId, service, mimeType, pageLimit=MAX_PAGES):

    direct_files = get_files_directly_in(folderId, service)
    results = [f for f in direct_files.get('files', []) if f['mimeType'] == mimeType]
    
    i = 1
    while ('nextPageToken' in direct_files and i < pageLimit):
        print(f"Page {i} for {folderId}")
        direct_files = get_files_directly_in(folderId, service, nextPageToken=direct_files['nextPageToken'])
        results += [f for f in direct_files.get('files', []) if f['mimeType'] == mimeType]
        
        i += 1
        
        
    return results

def download_file(folder_id, file_id, service, mimeType):
    str_type = ""
    if mimeType == BINVOX_MIMETYPE:
        str_type = "binvox"
    elif mimeType == STL_MIMETYPE:
        str_type = "stl"
        
    path = os.path.join("data", str_type, folder_id)
    
    if not os.path.exists(path):
        os.makedirs(path)
    request = service.files().get_media(fileId=file_id)
    with open(os.path.join(path, file_id), "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            # print("Download %d%%." % int(status.progress() * 100))


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """

    os.chdir(os.path.dirname(__file__))
    creds = token_login()

    try:
        service = build('drive', 'v3', credentials=creds)
        # items = get_all_files_of_type(ALL_FILE_FOLDERS["PARTS_1_1_2500"], service, BINVOX_MIMETYPE)
        
        for folder in ALL_FILE_FOLDERS.keys():
            print(f"Starting {folder}")
            download_all_binvox_stl_files_in(ALL_FILE_FOLDERS[folder], service)
            print(f"Done with {folder}")
            
            
        # use multiprocessing to parallelize the above loop
        
        # with Pool(NUM_THREADS) as p:
        #     p.starmap(download_all_binvox_stl_files_in, [(ALL_FILE_FOLDERS[folder], service) for folder in ALL_FILE_FOLDERS.keys()])
        
        # print('Files:')
        # for item in items:
        #     print(u'{0} ({1})'.format(item['name'], item['id']))

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
