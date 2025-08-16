package utils

import (
	"bytes"
	"context"
	"fmt"
	"net/url"
	"os"
	"sync"
	"time"

	"github.com/Azure/azure-sdk-for-go/sdk/azidentity"
	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob/sas"
	"github.com/sirupsen/logrus"
)

type AzureStorageHelper struct {
	client        *azblob.Client
	accountName   string
	containerName string
	accountKey    string
}

var (
	azureInstance *AzureStorageHelper
	azureOnce     sync.Once
)

// GetAzureStorageHelper returns singleton instance of Azure Storage Helper
func GetAzureStorageHelper() *AzureStorageHelper {
	azureOnce.Do(func() {
		azureInstance = &AzureStorageHelper{}
		if err := azureInstance.initialize(); err != nil {
			logrus.Errorf("Failed to initialize Azure Storage: %v", err)
		}
	})
	return azureInstance
}

// initialize sets up the Azure Storage client
func (ash *AzureStorageHelper) initialize() error {
	// Azure Storage configuration
	ash.accountName = os.Getenv("AZURE_STORAGE_ACCOUNT_NAME")
	ash.containerName = os.Getenv("AZURE_STORAGE_CONTAINER_NAME")
	if ash.containerName == "" {
		ash.containerName = "coursewagon-images"
	}

	// Method 1: Using connection string (most common for development)
	connectionString := os.Getenv("AZURE_STORAGE_CONNECTION_STRING")

	if connectionString != "" {
		// Initialize with connection string
		client, err := azblob.NewClientFromConnectionString(connectionString, nil)
		if err != nil {
			return fmt.Errorf("failed to create client from connection string: %w", err)
		}
		ash.client = client

		// Extract account key from connection string for SAS generation
		ash.extractAccountKeyFromConnectionString(connectionString)
		logrus.Info("Azure Storage initialized with connection string")
	} else if ash.accountName != "" {
		// Method 2: Using Azure credentials (for production with managed identity)
		accountURL := fmt.Sprintf("https://%s.blob.core.windows.net", ash.accountName)
		
		credential, err := azidentity.NewDefaultAzureCredential(nil)
		if err != nil {
			return fmt.Errorf("failed to create Azure credential: %w", err)
		}

		client, err := azblob.NewClient(accountURL, credential, nil)
		if err != nil {
			return fmt.Errorf("failed to create client with credentials: %w", err)
		}
		ash.client = client
		logrus.Info("Azure Storage initialized with Azure credentials")
	} else {
		return fmt.Errorf("no Azure Storage configuration found")
	}

	// Ensure container exists
	if err := ash.ensureContainerExists(); err != nil {
		return fmt.Errorf("failed to ensure container exists: %w", err)
	}

	return nil
}

// extractAccountKeyFromConnectionString extracts account key for SAS generation
func (ash *AzureStorageHelper) extractAccountKeyFromConnectionString(connectionString string) {
	// Parse connection string to extract AccountKey
	parts := map[string]string{}
	for _, part := range bytes.Split([]byte(connectionString), []byte(";")) {
		if len(part) == 0 {
			continue
		}
		kv := bytes.SplitN(part, []byte("="), 2)
		if len(kv) == 2 {
			parts[string(kv[0])] = string(kv[1])
		}
	}
	
	if key, exists := parts["AccountKey"]; exists {
		ash.accountKey = key
	}
}

// ensureContainerExists creates the container if it doesn't exist
func (ash *AzureStorageHelper) ensureContainerExists() error {
	ctx := context.Background()
	
	// Try to get container properties to check if it exists
	_, err := ash.client.ServiceClient().NewContainerClient(ash.containerName).GetProperties(ctx, nil)
	if err == nil {
		// Container exists
		return nil
	}

	// Container doesn't exist, create it
	logrus.Infof("Creating container: %s", ash.containerName)
	_, err = ash.client.ServiceClient().NewContainerClient(ash.containerName).Create(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to create container %s: %w", ash.containerName, err)
	}

	logrus.Infof("Container %s created successfully", ash.containerName)
	return nil
}

// UploadImage uploads an image to Azure Storage and returns the URL
func (ash *AzureStorageHelper) UploadImage(imageData []byte, imagePath string) (string, error) {
	if ash.client == nil {
		return "", fmt.Errorf("Azure Storage client not initialized")
	}

	ctx := context.Background()
	
	// Add file extension if not present
	if len(imagePath) > 0 && imagePath[len(imagePath)-4:] != ".png" {
		imagePath += ".png"
	}

	// Get blob client
	blobClient := ash.client.ServiceClient().NewContainerClient(ash.containerName).NewBlobClient(imagePath)

	// Upload the image
	_, err := blobClient.UploadBuffer(ctx, imageData, &azblob.UploadBufferOptions{
		HTTPHeaders: &azblob.BlobHTTPHeaders{
			BlobContentType: getStringPtr("image/png"),
		},
	})
	if err != nil {
		return "", fmt.Errorf("failed to upload image: %w", err)
	}

	// Generate the public URL
	imageURL := fmt.Sprintf("https://%s.blob.core.windows.net/%s/%s", ash.accountName, ash.containerName, imagePath)
	
	logrus.Infof("Image uploaded successfully to: %s", imageURL)
	return imageURL, nil
}

// UploadImageWithSAS uploads an image and returns a SAS URL with expiry
func (ash *AzureStorageHelper) UploadImageWithSAS(imageData []byte, imagePath string, expiryHours int) (string, error) {
	// First upload the image
	_, err := ash.UploadImage(imageData, imagePath)
	if err != nil {
		return "", err
	}

	// Generate SAS URL
	return ash.GenerateSASURL(imagePath, expiryHours)
}

// GenerateSASURL generates a SAS URL for an existing blob
func (ash *AzureStorageHelper) GenerateSASURL(blobPath string, expiryHours int) (string, error) {
	if ash.accountKey == "" {
		// If no account key, return the direct URL (assuming public access)
		return fmt.Sprintf("https://%s.blob.core.windows.net/%s/%s", ash.accountName, ash.containerName, blobPath), nil
	}

	// Create SAS token
	now := time.Now().UTC()
	expiry := now.Add(time.Duration(expiryHours) * time.Hour)

	sasURL, err := sas.BlobSignatureValues{
		Protocol:      sas.ProtocolHTTPS,
		ExpiryTime:    expiry,
		Permissions:   sas.BlobPermissions{Read: true}.String(),
		ContainerName: ash.containerName,
		BlobName:      blobPath,
	}.SignWithSharedKey(ash.accountName, ash.accountKey)

	if err != nil {
		return "", fmt.Errorf("failed to generate SAS URL: %w", err)
	}

	fullURL := fmt.Sprintf("https://%s.blob.core.windows.net/%s/%s?%s", ash.accountName, ash.containerName, blobPath, sasURL)
	return fullURL, nil
}

// DeleteImage deletes an image from Azure Storage
func (ash *AzureStorageHelper) DeleteImage(imagePath string) error {
	if ash.client == nil {
		return fmt.Errorf("Azure Storage client not initialized")
	}

	ctx := context.Background()
	blobClient := ash.client.ServiceClient().NewContainerClient(ash.containerName).NewBlobClient(imagePath)

	_, err := blobClient.Delete(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to delete image: %w", err)
	}

	logrus.Infof("Image deleted successfully: %s", imagePath)
	return nil
}

// ListImages lists all images in a specific path
func (ash *AzureStorageHelper) ListImages(pathPrefix string) ([]string, error) {
	if ash.client == nil {
		return nil, fmt.Errorf("Azure Storage client not initialized")
	}

	ctx := context.Background()
	containerClient := ash.client.ServiceClient().NewContainerClient(ash.containerName)

	var imageURLs []string
	pager := containerClient.NewListBlobsFlatPager(&azblob.ListBlobsFlatOptions{
		Prefix: &pathPrefix,
	})

	for pager.More() {
		resp, err := pager.NextPage(ctx)
		if err != nil {
			return nil, fmt.Errorf("failed to list blobs: %w", err)
		}

		for _, blob := range resp.Segment.BlobItems {
			imageURL := fmt.Sprintf("https://%s.blob.core.windows.net/%s/%s", ash.accountName, ash.containerName, *blob.Name)
			imageURLs = append(imageURLs, imageURL)
		}
	}

	return imageURLs, nil
}

// IsInitialized checks if the Azure Storage helper is properly initialized
func (ash *AzureStorageHelper) IsInitialized() bool {
	return ash.client != nil && ash.accountName != ""
}

// getStringPtr returns a pointer to a string
func getStringPtr(s string) *string {
	return &s
}