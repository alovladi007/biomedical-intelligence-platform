#!/bin/bash
#
# CT Segmentation Datasets Downloader
#
# Datasets:
# 1. Medical Segmentation Decathlon (http://medicaldecathlon.com/)
# 2. CHAOS Challenge (https://chaos.grand-challenge.org/)
# 3. KiTS19 - Kidney Tumor Segmentation (https://kits19.grand-challenge.org/)
#
# Total Size: ~50 GB
#
# Usage: ./download_ct_datasets.sh [dataset_name]
#   dataset_name: decathlon, chaos, kits19, or all (default: all)
#

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_ROOT/data/raw/ct-segmentation"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CT Segmentation Datasets Downloader${NC}"
echo -e "${GREEN}========================================${NC}"

# Dataset selection
DATASET_CHOICE="${1:-all}"

# Check requirements
echo -e "\n${YELLOW}Checking requirements...${NC}"

# Check disk space (need at least 60GB free)
REQUIRED_SPACE_GB=60
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
    exit 1
fi

# Create directory
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

echo -e "\n${GREEN}Download directory: $DATA_DIR${NC}\n"

#################################################
# Medical Segmentation Decathlon
#################################################
download_decathlon() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Medical Segmentation Decathlon${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "10 different medical imaging tasks"
    echo -e "Size: ~30 GB"
    echo -e "URL: http://medicaldecathlon.com/\n"

    mkdir -p "$DATA_DIR/decathlon"
    cd "$DATA_DIR/decathlon"

    # Decathlon tasks (download via Google Drive or direct links)
    TASKS=(
        "Task01_BrainTumour"
        "Task02_Heart"
        "Task03_Liver"
        "Task04_Hippocampus"
        "Task05_Prostate"
        "Task06_Lung"
        "Task07_Pancreas"
        "Task08_HepaticVessel"
        "Task09_Spleen"
        "Task10_Colon"
    )

    echo -e "${YELLOW}Medical Segmentation Decathlon requires manual download:${NC}"
    echo -e "1. Visit: http://medicaldecathlon.com/"
    echo -e "2. Download tasks (requires registration)"
    echo -e "3. Place in: $DATA_DIR/decathlon/\n"

    echo -e "${GREEN}Available tasks:${NC}"
    for task in "${TASKS[@]}"; do
        echo -e "  - $task"
    done

    echo -e "\n${YELLOW}Alternative: Use their Python API${NC}"
    echo -e "pip install medicaldecathlon"
    echo -e "python -c 'from medicaldecathlon import download; download()'\n"

    cd "$DATA_DIR"
}

#################################################
# CHAOS Challenge
#################################################
download_chaos() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}CHAOS Challenge Dataset${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "Combined Healthy Abdominal Organ Segmentation"
    echo -e "Size: ~10 GB"
    echo -e "URL: https://chaos.grand-challenge.org/\n"

    mkdir -p "$DATA_DIR/chaos"
    cd "$DATA_DIR/chaos"

    echo -e "${YELLOW}CHAOS dataset requires:${NC}"
    echo -e "1. Register at: https://chaos.grand-challenge.org/"
    echo -e "2. Accept terms and conditions"
    echo -e "3. Download training and test sets"
    echo -e "4. Place in: $DATA_DIR/chaos/\n"

    echo -e "${GREEN}Dataset structure:${NC}"
    echo -e "  chaos/"
    echo -e "  ├── Train_Sets/"
    echo -e "  │   ├── CT/"
    echo -e "  │   └── MR/"
    echo -e "  └── Test_Sets/\n"

    cd "$DATA_DIR"
}

#################################################
# KiTS19 - Kidney Tumor Segmentation
#################################################
download_kits19() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}KiTS19 - Kidney Tumor Segmentation${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "210 CT scans with kidney tumor annotations"
    echo -e "Size: ~10 GB"
    echo -e "URL: https://github.com/neheller/kits19\n"

    mkdir -p "$DATA_DIR/kits19"
    cd "$DATA_DIR/kits19"

    # KiTS19 can be downloaded via GitHub
    if command -v git &> /dev/null; then
        echo -e "${GREEN}Cloning KiTS19 repository...${NC}"

        if [ ! -d "kits19" ]; then
            git clone https://github.com/neheller/kits19.git
            cd kits19

            echo -e "\n${GREEN}Installing kits19 Python package...${NC}"
            pip install -e .

            echo -e "\n${GREEN}Downloading KiTS19 data...${NC}"
            python -m starter_code.get_imaging

            echo -e "${GREEN}✓ KiTS19 dataset downloaded successfully${NC}"
        else
            echo -e "${GREEN}✓ KiTS19 repository already exists${NC}"
        fi
    else
        echo -e "${RED}Git not found. Please install git to download KiTS19.${NC}"
        echo -e "${YELLOW}Alternative: Manual download${NC}"
        echo -e "1. Visit: https://github.com/neheller/kits19"
        echo -e "2. Follow installation instructions"
        echo -e "3. Run: python -m starter_code.get_imaging\n"
    fi

    cd "$DATA_DIR"
}

#################################################
# Main execution
#################################################

case "$DATASET_CHOICE" in
    decathlon)
        download_decathlon
        ;;
    chaos)
        download_chaos
        ;;
    kits19)
        download_kits19
        ;;
    all)
        download_decathlon
        download_chaos
        download_kits19
        ;;
    *)
        echo -e "${RED}Invalid dataset choice: $DATASET_CHOICE${NC}"
        echo -e "Usage: $0 [decathlon|chaos|kits19|all]"
        exit 1
        ;;
esac

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Download Instructions Complete${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${GREEN}Dataset locations:${NC}"
echo -e "  Medical Segmentation Decathlon: $DATA_DIR/decathlon/"
echo -e "  CHAOS Challenge: $DATA_DIR/chaos/"
echo -e "  KiTS19: $DATA_DIR/kits19/\n"

echo -e "${YELLOW}Note:${NC} Most CT datasets require registration due to data use agreements."
echo -e "Please follow the instructions above to complete the downloads.\n"

echo -e "${GREEN}Next steps:${NC}"
echo -e "1. Complete dataset registrations and downloads"
echo -e "2. Verify data integrity"
echo -e "3. Run preprocessing: python scripts/preprocess_ct_scans.py"
echo -e "4. Start model training\n"

echo -e "${GREEN}Done!${NC}\n"
