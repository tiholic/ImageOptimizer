#!/bin/bash
# ImageOptimizer API Examples using cURL

# Configuration
BASE_URL="http://localhost:8000/api"
TOKEN="your-token-here"  # Replace with your actual token

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function to print section headers
print_section() {
    echo -e "\n${BLUE}$1${NC}"
    echo "=================================================="
}

# Example 1: Get Authentication Token (if you have username/password)
print_section "1. Get Authentication Token"
echo "curl -X POST $BASE_URL/auth/token/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"username\":\"user@example.com\",\"password\":\"password\"}'"

# Example 2: List Storage Providers
print_section "2. List Storage Providers"
echo "curl -X GET $BASE_URL/storage/providers/ \\"
echo "  -H 'Authorization: Token $TOKEN'"

# Example 3: Create AWS S3 Storage Provider
print_section "3. Create AWS S3 Storage Provider"
cat << 'EOF'
curl -X POST $BASE_URL/storage/providers/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My S3 Bucket",
    "provider_type": "s3",
    "is_default": true,
    "config": {
      "bucket": "my-images-bucket",
      "region": "us-east-1"
    },
    "credentials": {
      "access_key_id": "YOUR_ACCESS_KEY",
      "secret_access_key": "YOUR_SECRET_KEY"
    }
  }'
EOF

# Example 4: Create Azure Blob Storage Provider
print_section "4. Create Azure Blob Storage Provider"
cat << 'EOF'
curl -X POST $BASE_URL/storage/providers/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Azure Blob Storage",
    "provider_type": "azure",
    "is_default": false,
    "config": {
      "container": "images"
    },
    "credentials": {
      "account_name": "myaccount",
      "account_key": "YOUR_ACCOUNT_KEY"
    }
  }'
EOF

# Example 5: Test Storage Connection
print_section "5. Test Storage Connection"
echo "curl -X POST $BASE_URL/storage/providers/1/test_connection/ \\"
echo "  -H 'Authorization: Token $TOKEN'"

# Example 6: Upload Image with Optimization
print_section "6. Upload Image with Optimization"
echo "curl -X POST $BASE_URL/images/ \\"
echo "  -H 'Authorization: Token $TOKEN' \\"
echo "  -F 'image=@/path/to/image.jpg' \\"
echo "  -F 'optimize=true' \\"
echo "  -F 'tags=vacation,beach'"

# Example 7: List Images
print_section "7. List Images"
echo "curl -X GET $BASE_URL/images/ \\"
echo "  -H 'Authorization: Token $TOKEN'"

# Example 8: Get Image Details
print_section "8. Get Image Details"
echo "curl -X GET $BASE_URL/images/1/ \\"
echo "  -H 'Authorization: Token $TOKEN'"

# Example 9: Update Image Tags
print_section "9. Update Image Tags"
echo "curl -X PATCH $BASE_URL/images/1/ \\"
echo "  -H 'Authorization: Token $TOKEN' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"tags\":[\"vacation\",\"beach\",\"sunset\"]}'"

# Example 10: Get Image Statistics
print_section "10. Get Image Statistics"
echo "curl -X GET $BASE_URL/images/stats/ \\"
echo "  -H 'Authorization: Token $TOKEN'"

# Example 11: Delete Image
print_section "11. Delete Image"
echo "curl -X DELETE $BASE_URL/images/1/ \\"
echo "  -H 'Authorization: Token $TOKEN'"

# Example 12: Set Storage Provider as Default
print_section "12. Set Storage Provider as Default"
echo "curl -X POST $BASE_URL/storage/providers/1/set_default/ \\"
echo "  -H 'Authorization: Token $TOKEN'"

print_section "Notes"
echo "1. Replace \$TOKEN with your actual API token"
echo "2. Replace image IDs and provider IDs with actual values"
echo "3. Update file paths to point to actual image files"
echo "4. Update storage credentials with your actual credentials"
echo ""
echo -e "${GREEN}To get your token, login via Google OAuth and create one in Django admin${NC}"
