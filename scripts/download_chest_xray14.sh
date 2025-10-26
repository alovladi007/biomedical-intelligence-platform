#!/bin/bash
#
# NIH ChestX-ray14 Dataset Downloader
#
# Dataset: 112,120 chest X-ray images from 30,805 patients
# Size: ~45 GB
# Source: https://nihcc.app.box.com/v/ChestXray-NIHCC
#
# Usage: ./download_chest_xray14.sh
#

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_ROOT/data/raw/chest-xray"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}NIH ChestX-ray14 Dataset Downloader${NC}"
echo -e "${GREEN}========================================${NC}"

# Check requirements
echo -e "\n${YELLOW}Checking requirements...${NC}"

# Check disk space (need at least 50GB free)
REQUIRED_SPACE_GB=50
AVAILABLE_SPACE=$(df -BG "$PROJECT_ROOT" | tail -1 | awk '{print $4}' | sed 's/G//')

if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE_GB" ]; then
    echo -e "${RED}Error: Insufficient disk space!${NC}"
    echo -e "Required: ${REQUIRED_SPACE_GB}GB, Available: ${AVAILABLE_SPACE}GB"
    exit 1
fi

echo -e "${GREEN}✓ Disk space OK (${AVAILABLE_SPACE}GB available)${NC}"

# Check for wget or curl
if command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget -c"
    echo -e "${GREEN}✓ Using wget for downloads${NC}"
elif command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -C - -O"
    echo -e "${GREEN}✓ Using curl for downloads${NC}"
else
    echo -e "${RED}Error: Neither wget nor curl found!${NC}"
    echo "Please install wget or curl first:"
    echo "  macOS: brew install wget"
    echo "  Ubuntu/Debian: sudo apt-get install wget"
    exit 1
fi

# Create directory
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

echo -e "\n${GREEN}Download directory: $DATA_DIR${NC}\n"

# NIH ChestX-ray14 download links (Box.com links)
# NOTE: Box.com links may require authentication. Alternative approach:
# Use the NIH Clinical Center download page or kaggle API

echo -e "${YELLOW}Important: This dataset is ~45GB and will take significant time to download.${NC}"
echo -e "${YELLOW}Please ensure you have a stable internet connection.${NC}\n"

read -p "Continue with download? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Download cancelled.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Starting download...${NC}\n"

# Download metadata files
echo -e "${YELLOW}Downloading metadata...${NC}"

# Data Entry file
if [ ! -f "Data_Entry_2017.csv" ]; then
    echo "Downloading Data_Entry_2017.csv..."
    wget -c https://nihcc.box.com/shared/static/vfk49d74nhbxq3nqjg0900w5nvkorp5c.gz \
        -O Data_Entry_2017.csv.gz
    gunzip Data_Entry_2017.csv.gz
    echo -e "${GREEN}✓ Data_Entry_2017.csv downloaded${NC}"
else
    echo -e "${GREEN}✓ Data_Entry_2017.csv already exists${NC}"
fi

# BBox annotations
if [ ! -f "BBox_List_2017.csv" ]; then
    echo "Downloading BBox_List_2017.csv..."
    wget -c https://nihcc.box.com/shared/static/sp5y2k2z7b89l8nqcc9yq1nklmr41y2e.gz \
        -O BBox_List_2017.csv.gz
    gunzip BBox_List_2017.csv.gz
    echo -e "${GREEN}✓ BBox_List_2017.csv downloaded${NC}"
else
    echo -e "${GREEN}✓ BBox_List_2017.csv already exists${NC}"
fi

# Download image archives (12 files total, ~3.7GB each)
echo -e "\n${YELLOW}Downloading image archives (12 files, ~45GB total)...${NC}"
echo -e "${YELLOW}This will take a while. Downloads are resumable if interrupted.${NC}\n"

# NIH Box.com download links for the 12 image archives
declare -A DOWNLOAD_LINKS=(
    ["images_001.tar.gz"]="https://nihcc.box.com/shared/static/vfk49d74nhbxq3nqjg0900w5nvkorp5c"
    ["images_002.tar.gz"]="https://nihcc.box.com/shared/static/i28rlmbvmfjbl8p2n3ril0pptcmcu9d1"
    ["images_003.tar.gz"]="https://nihcc.box.com/shared/static/f1t00wrtdk94satdfb9olcolqx20z2jp"
    ["images_004.tar.gz"]="https://nihcc.box.com/shared/static/0aowwzs5lhjrceb3qp67ahp0rd1l1etg"
    ["images_005.tar.gz"]="https://nihcc.box.com/shared/static/v5e3goj22zr6h8tzualxfsqlqaygfbsn"
    ["images_006.tar.gz"]="https://nihcc.box.com/shared/static/asi7ikud9jwnkrnkj99jnpfkjdes7l6l"
    ["images_007.tar.gz"]="https://nihcc.box.com/shared/static/jn1b4mw4n6lnh74ovmcjb8y48h8xj07n"
    ["images_008.tar.gz"]="https://nihcc.box.com/shared/static/tvpxmn7qyrgl0w8wfh9kqfjskv6nmm1j"
    ["images_009.tar.gz"]="https://nihcc.box.com/shared/static/upyy3ml7qdumlgk2rfcvlb9k6gvqq2pj"
    ["images_010.tar.gz"]="https://nihcc.box.com/shared/static/l6nilvfa9cg3s28tqv1qc1olm3gnz54p"
    ["images_011.tar.gz"]="https://nihcc.box.com/shared/static/hhq8fkdgvcari67vfhs7ppg2w6ni4jze"
    ["images_012.tar.gz"]="https://nihcc.box.com/shared/static/ioqwiy20ihqwyr8pf4c24eazhh281pbu"
)

TOTAL_FILES=12
CURRENT_FILE=0

# Note: Box.com links may require manual download or alternative methods
# Suggest using Kaggle API instead:

echo -e "${YELLOW}NOTE: Direct download from Box.com may require authentication.${NC}"
echo -e "${YELLOW}Alternative: Download via Kaggle (recommended)${NC}\n"
echo -e "To download via Kaggle:"
echo -e "1. Install kaggle: pip install kaggle"
echo -e "2. Set up API key: https://www.kaggle.com/docs/api"
echo -e "3. Run: kaggle datasets download -d nih-chest-xrays/data"
echo -e "\nFor manual download:"
echo -e "Visit: https://nihcc.app.box.com/v/ChestXray-NIHCC\n"

# Attempt downloads
for filename in "${!DOWNLOAD_LINKS[@]}"; do
    CURRENT_FILE=$((CURRENT_FILE + 1))

    if [ -f "$filename" ]; then
        echo -e "${GREEN}✓ [$CURRENT_FILE/$TOTAL_FILES] $filename already downloaded${NC}"
    else
        echo -e "${YELLOW}Downloading [$CURRENT_FILE/$TOTAL_FILES] $filename...${NC}"
        wget -c "${DOWNLOAD_LINKS[$filename]}" -O "$filename" || {
            echo -e "${RED}Download failed for $filename${NC}"
            echo -e "${YELLOW}You may need to download manually from:${NC}"
            echo -e "${YELLOW}https://nihcc.app.box.com/v/ChestXray-NIHCC${NC}"
            continue
        }
        echo -e "${GREEN}✓ $filename downloaded${NC}"
    fi
done

# Extract archives
echo -e "\n${YELLOW}Extracting archives...${NC}"
mkdir -p images

for i in {001..012}; do
    archive="images_${i}.tar.gz"
    if [ -f "$archive" ]; then
        echo "Extracting $archive..."
        tar -xzf "$archive" -C images/ || {
            echo -e "${RED}Failed to extract $archive${NC}"
        }
    fi
done

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Download Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\nDataset location: $DATA_DIR"
echo -e "Images: $DATA_DIR/images/"
echo -e "Metadata: $DATA_DIR/Data_Entry_2017.csv"
echo -e "Bounding boxes: $DATA_DIR/BBox_List_2017.csv"

# Summary
echo -e "\n${GREEN}Dataset Summary:${NC}"
echo -e "  Total images: $(ls images/*.png 2>/dev/null | wc -l)"
echo -e "  Disk usage: $(du -sh images/ 2>/dev/null | cut -f1)"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Verify dataset integrity"
echo -e "2. Run preprocessing: python scripts/preprocess_chest_xray.py"
echo -e "3. Start model training"

echo -e "\n${GREEN}Done!${NC}\n"
