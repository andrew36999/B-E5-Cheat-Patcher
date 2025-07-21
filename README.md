# Cheater-Cleaner

Tired of the CHEATER label in your playthrough? Me too. So I spent 5 hours of my time figuring out what variables make the CHEATER label stick.

It turns out the two variables are `WasDC` in the first few lines of a zlib compressed save in either of the streams (they shift) and the number in the `Console_end` variable. The number can range from 3000 to 6000 to 30000, it doesn't seem to matter, only specific numbers hit so there is no > or <, there are specific numbers which trigger the CHEATER label and make it more complex then simply deleting the WasDC line.

So for simplicity's sake, I wrote this python script and also made a .exe version.

## Features

- Clean save files to remove the CHEATER flag
- Creates timestamped backups before modifying files
- Simple GUI interface for easy use
- Supports `.nsv` save file formats

## Installation

### Option 1: Use Pre-built Executable (Recommended - No Requirements)

1. Download the latest `E5_Save_Cleaner.exe` from the [Releases](../../releases) page
2. Run the executable directly - **no Python installation or dependencies required**

### Option 2: Run from Python Source

**Requirements:**
- Python 3.7+ installed

**Steps:**
1. Download the python file either with the webui or with commands:
   ```bash
   git clone https://github.com/andrew36999/B-E5-Save-Cleaner.git
   cd Cheater-Cleaner
   ```

2. Run the script:
   ```bash
   python E5_Cheat_Patcher.py
   ```

## Usage

1. Launch the application (either `E5_Save_Cleaner.exe` or `python E5__Save_Cleaner.py`)
2. Click "Choose Save Folder" and select your Brigade E5 saves directory (It is the game folder inside your Steam directroy called "Saves")
3. Select a save file from the list (supports `.nsv` formats)
4. Click "Patch Selected" to clean the file
5. The tool will create a timestamped backup and patch the original file


## How It Works

The tool modifies two specific variables that trigger the CHEATER flag:

1. **`WasDC` lines**: Removes any lines matching `WasDC` (debug/cheat detection markers) from zlib compressed streams
2. **`Console_end` variable**: Replaces the console information block with clean values:
   ```
   ConsoleInfo  0 0.4 0
   Console_end  6160
   ```

The specific numbers in `Console_end` can range from 3000 to 30000, but only certain values trigger the CHEATER flag. Rather than trying to determine safe values, the tool uses known clean values that work consistently.

All other save data and game progress is preserved exactly as-is.
This method was tested many times with different save files and is now 100% consistently working!

## Compatibility

- **Windows** (tested and confirmed working)
- **Linux/Mac** (should work with Python installed, but untested)
- **Compatible with Brigade E5: New Jagged Union save files only**
- **File formats**: `.nsv` save files

## Disclaimer

This tool modifies game save files. While it creates backups, use at your own risk. The authors are not responsible for any data loss or game issues.
