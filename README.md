# binvox-stl-dataloader

If on Windows, you will need to install [Git Bash](https://gitforwindows.org/).

To begin, open Git Bash, `cd` into whatever folder you'd like to clone the repository and run `git clone https://github.com/noahadhikari/binvox-stl-dataloader.git`. Open this folder in VSCode or a similar editor.

The download script for the folders is `download_all_models.py` and for the ratings is `get_all_ratings.py`.

All of the folders to be downloaded are located in the Python dictionary `ALL_FILE_FOLDERS`. Add additional folders with their folderIds to download them. Please try to name the key appropriately if possible, and feel free to comment out the ones that have already been downloaded.

Assumes the binvox folder contains the string "Binvox" and the stl folder contains the string "rotated".

You'll also need to have a `.env` file in your root directory set up as follows:

```
GOOGLE_API_KEY = {your api key here}
```

### Acquiring Google credentials

To acquire this key, go to `console.cloud.google.com/` and go to "APIs and Services". Enable the Google Drive API and then go to Credentials and enable an API key for Google Drive.

Follow the quickstart here and see if you can get `quickstart.py` working: https://developers.google.com/drive/api/quickstart/python

You'll also need to create an OAuth client ID and add the following to its Authorized JavaScript origins (unsure of how many of these are necessary):
- http://localhost
- https://model-rating.vercel.app
- http://localhost:8080

and the following to Authorized redirect URIs:
- http://localhost:3000/api/auth/callback/google
- https://model-rating.vercel.app/api/auth/callback/google
- http://localhost
- http://localhost:8080/

### Python dependencies
- tqdm
- google-api-client
