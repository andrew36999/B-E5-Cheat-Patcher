# Save Cleaner

Tired of the CHEATER label in your playthrough? Me too. So I spent 8 hours of my time figuring out what variables make the CHEATER label stick.

It turns out the two variables are `WasDC` in the first few lines of a zlib compressed save in either of the streams (they shift) and the number in the `Console_end` variable. The number can range from 3000 to 6000 to 30000, it doesn't seem to matter, only specific numbers hit so there is no > or <, there are specific numbers which trigger the CHEATER label and make it more complex then simply deleting the WasDC line.

So for simplicity's sake, I wrote this python script and also made a .exe version.


## Features

- Clean save files to remove the CHEATER flag using a cycle-safe method
- Captures clean encryption blocks from valid saves
- Creates timestamped backups before modifying files
- Two-step process ensures 100% consistent results
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
1. Download the python file either with the web UI or with commands:
   ```bash
   git clone https://github.com/andrew36999/Cheater-Cleaner.git
   ```

2. Run the script:
   ```bash
   python E5_Save_Cleaner.py
   ```

## Usage

**Important: Turn off Steam Cloud in the game properties before starting!**

### Step-by-Step Process:

1. Launch the application (either `E5_Save_Cleaner.exe` or `python E5_Save_Cleaner.py`)
2. **Pause your game** (this is crucial!)
3. Create a clean save (without cheats) while paused
4. Click "**Catch Encryption Cycle**" and select your clean save file
5. Now cheat in your game and create another save while still paused
6. Click "**Clean Cheated Save**" and select your cheated save file
7. The tool will create a timestamped backup and patch the original file

**Note:** The game must remain paused during the entire process for this method to work correctly. The save directory is typically located in your Steam directory under the game folder called "Saves".


## How It Works

The tool uses a revolutionary **cycle-safe method** that captures the encryption pattern from clean saves:

### Two-Step Process:
1. **Catch Encryption Cycle**: Captures the clean `ConsoleInfo` block from a valid, non-cheated save
2. **Clean Cheated Save**: Applies the captured clean block to remove cheating markers

### Technical Details:
The tool modifies two specific variables that trigger the CHEATER flag:

1. **`WasDC` lines**: Removes any lines matching `WasDC` (debug/cheat detection markers) from zlib compressed streams
2. **`Console_end` variable**: Replaces the entire console information block with the captured clean values from your own save file

This method ensures the encryption cycle matches your specific game instance, making it **100% consistently working** across different save files and game states.

All other save data and game progress is preserved exactly as-is.

**This method was tested many times with different save files and is now 100% consistently working!**

## Compatibility

- **Windows** (tested and confirmed working)
- **Linux/Mac** (should work with Python installed, but untested)
- **Compatible with Brigade E5: New Jagged Union save files only**
- **File formats**: `.nsv` save files

## Disclaimer

This tool modifies game save files. While it creates backups, use at your own risk. The authors are not responsible for any data loss or game issues.
