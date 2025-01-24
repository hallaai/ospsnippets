from zipfile import ZipFile

def replace_in_zip_file(zip_filepath, target_file, old_string, new_string):
    with ZipFile(zip_filepath, 'r') as zip_ref:
        # Read all files in the zip
        zip_info = zip_ref.infolist()

        # Create a new zip file in memory
        with ZipFile('temp.zip', 'w') as new_zip:  # Use a temporary file
            for file_info in zip_info:
                with zip_ref.open(file_info) as f:
                    content = f.read().decode('utf-8') # Decode to string
                    if file_info.filename == target_file:
                        content = content.replace(old_string, new_string)
                    new_zip.writestr(file_info.filename, content.encode('utf-8')) # Encode back

    # Replace the original zip with the updated one
    import os
    os.remove(zip_filepath)  # Remove original
    os.rename('temp.zip', zip_filepath)  # Rename temp file


# Example Usage:
replace_in_zip_file('merged.gtfs.zip', 'agency.txt', 'Europe/Berlin', 'Europe/Oslo')