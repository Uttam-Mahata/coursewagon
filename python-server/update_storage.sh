#!/bin/bash

# Script to update storage references from Azure to unified storage helper

# Update course_service.py
sed -i 's/self\.azure_storage\.upload_image/self.storage_helper.upload_image/g' services/course_service.py
sed -i 's/# Upload to Azure Storage/# Upload to storage (GCS primary, Azure\/Firebase fallback)/g' services/course_service.py

# Update subject_service.py
sed -i 's/from utils\.azure_storage_helper import AzureStorageHelper/from utils.unified_storage_helper import storage_helper/g' services/subject_service.py
sed -i 's/self\.azure_storage = AzureStorageHelper()/self.storage_helper = storage_helper/g' services/subject_service.py
sed -i 's/self\.azure_storage\.upload_image/self.storage_helper.upload_image/g' services/subject_service.py
sed -i 's/self\.azure_storage\.delete_image/self.storage_helper.delete_image/g' services/subject_service.py

echo "Updated storage references in service files"
