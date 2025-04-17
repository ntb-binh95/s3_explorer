import os
import boto3
from dotenv import load_dotenv
from simple_term_menu import TerminalMenu

# Load environment variables from .env file
load_dotenv()

# Fetch AWS credentials from environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

bucket_name = 'manatesting'  # Replace with your bucket name

# Create our boto3 session and client using the desired credentials
boto3_session = boto3.session.Session()
s3_client = boto3_session.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# Start off with empty string to get top-level folder list
selected_folder = ""

def delete_folder(s3_client, bucket_name, folder):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder)
    
    if 'Contents' in response:
        objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
        s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})
        print(f"Deleted {len(objects_to_delete)} objects from {folder}.")
    else:
        print("Folder is empty or does not exist.")

def create_folder(s3_client, bucket_name, folder_name):
    # Create a new folder by adding an empty object with a key ending in '/'
    folder_key = f"{folder_name}/" if not folder_name.endswith('/') else folder_name
    s3_client.put_object(Bucket=bucket_name, Key=folder_key)
    print(f"Folder '{folder_key}' created successfully.")

# Allow the user to select folders until we run out of folders
while True:
    list_of_objects = s3_client.list_objects(Bucket=bucket_name, Prefix=selected_folder, Delimiter="/")

    if 'CommonPrefixes' not in list_of_objects:
        break

    folder_paths = [x['Prefix'] for x in list_of_objects['CommonPrefixes']]
    folders: list = [folder_path[len(selected_folder):-1] for folder_path in folder_paths]

    if "/" in selected_folder:
        folders.append("Back To Previous Folder")
    folders.append("Create New Folder")  # Added option to create a new folder
    folders.append("Delete This Folder")  # Option to delete the folder
    folders.append("Exit Bucket Browser")

    folder_menu = TerminalMenu(folders)
    folder_menu_selection_index = folder_menu.show()

    if folders[folder_menu_selection_index] == "Back To Previous Folder":
        selected_folder = ("/".join(selected_folder.split("/")[:-2]))
        if selected_folder:
            selected_folder += "/"
    elif folders[folder_menu_selection_index] == "Create New Folder":
        new_folder_name = input("Enter the name of the new folder: ")
        if new_folder_name:
            if "/" in new_folder_name:
                print("Folder name cannot contain '/' character.")
            else:
                create_folder(s3_client, bucket_name, selected_folder + new_folder_name)
    elif folders[folder_menu_selection_index] == "Delete This Folder":
        confirm_delete = input(f"Are you sure you want to delete the folder '{selected_folder}'? (y/n) ")
        if confirm_delete.lower() == 'y':
            delete_folder(s3_client, bucket_name, selected_folder)
            if selected_folder:
                selected_folder = selected_folder[:-1].rsplit('/', 1)[0] + "/"
    elif folders[folder_menu_selection_index] == "Exit Bucket Browser":
        exit()
    else:
        selected_folder = folder_paths[folder_menu_selection_index]

print(f"\nSelected Folder: {selected_folder}\n")

if selected_folder == "":
    print("No folders found in bucket.")

print("No more folder levels, would you like to:\n")
download_options = ["Download Single File From The Folder", "Download The Complete Folder", "Exit Download Menu"]
download_menu = TerminalMenu(download_options)
download_menu_selection_index = download_menu.show()

if download_options[download_menu_selection_index] == "Exit Download Menu":
    print("Exiting Download Menu")
    exit()

files_in_selected_folder = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=selected_folder) 

if download_options[download_menu_selection_index] == "Download Single File From The Folder":
    files = [file['Key'][len(selected_folder):] for file in files_in_selected_folder['Contents']]
    file_menu = TerminalMenu(files)
    file_menu_selection_index = file_menu.show()
    selected_file = files_in_selected_folder['Contents'][file_menu_selection_index]['Key']

    print("Downloading: " + selected_file)
    s3_client.download_file(bucket_name, selected_file, selected_file[len(selected_folder):])
    print("")

if download_options[download_menu_selection_index] == "Download The Complete Folder":
    print(f"Downloading {len(files_in_selected_folder['Contents'])} files..\n")
    confirm_download_folder = input("Are you sure you want to download these files? (y/n) ")
    if confirm_download_folder.lower() == 'n':
        print("Download aborted, no files downloaded.\n")
        exit()

    folder_to_download_into = selected_folder.split('/')[-2]
    if not os.path.exists(folder_to_download_into):
        os.mkdir(folder_to_download_into)

    for file in files_in_selected_folder['Contents']:
        selected_file = file['Key']
        print("Downloading: " + file['Key'][len(selected_folder):])
        s3_client.download_file(bucket_name, selected_file, f"{folder_to_download_into}/" + selected_file[len(selected_folder):])
        print("")