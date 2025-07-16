# Screenshot Tool Usage

This folder contains the script and driver for generating a long image from the trip itinerary HTML.

## Files:
- `gen_trip_long_image.py`: Python script to convert the HTML itinerary to a long PNG image using Edge (headless).
- `msedgedriver.exe`: Edge WebDriver (must match your Edge browser version).

## Usage:
1. Ensure your itinerary HTML is at:
   `docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.3.html`
2. Place `msedgedriver.exe` in this folder (already present).
3. Run the script from this directory:
   ```
   python gen_trip_long_image.py
   ```
4. The output image will be saved as:
   `docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.3_long.png`

## Notes:
- If you update the HTML, rerun the script to regenerate the image.
- The script is path-agnostic and will work as long as the directory structure is unchanged.
- For other HTML files, adjust the `HTML_PATH` and `IMG_PATH` variables in the script as needed.
