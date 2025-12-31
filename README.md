# Store Route Planner - Streamlit App

A comprehensive Streamlit application for planning manager trips from airports to store locations, with interactive mapping and route optimization.

## Features

✅ **Interactive Mapping**: View all stores and airports on a dynamic map  
✅ **Route Planning**: Plan trips from any airport to multiple stores  
✅ **Distance Calculations**: Automatic distance calculations between locations  
✅ **Geocoding**: Convert addresses to coordinates if needed  
✅ **Advanced Filtering**: Filter stores by Region, State, or City  
✅ **Trip Analytics**: Get insights on nearest/farthest stores and total distances  
✅ **Export Routes**: Download route details as CSV files  

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run store_route_planner.py
```

The app will open in your browser at `http://localhost:8501`

## File Formats

### Stores File (Excel - book1.xlsx)
Your file should contain these columns:
- **StoreCode**: Unique store identifier (e.g., ALMOB)
- **StoreID**: Store ID number
- **StoreName**: Full store name
- **Region**: Store region
- **State**: Two-letter state code
- **City**: City name
- **Address**: Street address
- **AddressLine2**: Additional address info (optional)
- **Zip**: ZIP code
- **Phone**: Store phone number
- **Email**: Store email
- **Owner**: Store owner name
- **OwnerEmail**: Owner's email
- **SubRegion**: Sub-region classification
- **Lat**: Latitude (required for mapping)
- **Long**: Longitude (required for mapping)

### Airports File (CSV - airports.csv)
Your file should contain these columns:
- **IATA**: Airport code (e.g., ORD, DEN)
- **AIRPORT**: Full airport name
- **CITY**: Airport city
- **STATE**: State code
- **COUNTRY**: Country (usually USA)
- **LATITUDE**: Airport latitude
- **LONGITUDE**: Airport longitude

## Usage Guide

### Step 1: Upload Your Files
1. Click "Browse files" in the sidebar
2. Upload your store Excel file (book1.xlsx)
3. Upload your airport CSV file (airports.csv)

### Step 2: View Your Data
- Go to the **"Data Overview"** tab to see all stores and airports
- Review the metrics showing total stores, regions, and coordinate coverage

### Step 3: Explore the Map
- Go to the **"Interactive Map"** tab
- Blue airplane icons = Airports
- Red store icons = Store locations
- Click any marker for detailed information
- Use the layer control to toggle airports/stores on/off

### Step 4: Plan a Route

1. Go to the **"Route Planning"** tab

2. **Filter Your Stores** (optional):
   - Select a specific Region (e.g., "Atlanta")
   - Select a specific State (e.g., "GA")
   - Select a specific City (e.g., "Columbus")

3. **Select Departure Airport**:
   - Choose from dropdown (e.g., "ATL - William B Hartsfield-Atlanta Intl")

4. **Select Store(s) to Visit**:
   - Choose one or more stores from the filtered list
   - Stores are shown as: "STOREODE - City, State (Address)"

5. **View Results**:
   - Route summary with key metrics
   - Detailed table sorted by distance from airport
   - Interactive map showing the route
   - Trip insights (nearest, farthest, round-trip distance)

6. **Download Route**:
   - Click "Download Route Details" to export as CSV

### Step 5: Geocode Missing Addresses (if needed)

If any stores are missing coordinates:

1. Go to the **"Geocode Addresses"** tab
2. Click "Geocode Missing Stores" to automatically add coordinates
3. Download the updated file with coordinates

For manual geocoding:
1. Enter street address, city, state, and ZIP
2. Click "Get Coordinates"
3. View the coordinates and location on the map

## Example Workflow

### Scenario: Regional Manager Trip to Georgia Stores

1. **Upload Files**: Upload book1.xlsx and airports.csv

2. **Filter Stores**:
   - Region: "Atlanta"
   - State: "GA"

3. **Select Airport**:
   - "ATL - William B Hartsfield-Atlanta Intl (Atlanta, GA)"

4. **Select Stores**:
   - GAKEN - Kennesaw, GA
   - GACOL - Columbus, GA
   - (Any other Georgia stores)

5. **Review Route**:
   - See stores ordered by distance
   - Total distance from airport: ~150 miles
   - Store-to-store distance: ~75 miles
   - Round trip: ~225 miles

6. **Export**:
   - Download CSV with store details, contacts, and distances

## Key Metrics Explained

### Route Summary Metrics

**Stores to Visit**: Number of stores selected for the trip

**Total Distance from Airport**: Sum of direct distances from airport to each store

**Average Distance**: Mean distance from airport to stores

**Store-to-Store**: Total driving distance if visiting stores in order (by proximity)

### Trip Insights

**Nearest Store**: The closest store to the selected airport

**Farthest Store**: The most distant store from the airport

**Round Trip Distance**: Total mileage for complete trip (Airport → All Stores → Airport)

## Map Legend

- 🔵 Blue Airplane Icon = Airport
- 🔴 Red Store Icon = Store location
- 🟢 Green Dashed Lines = Direct routes from airport to each store
- 🟠 Orange Solid Line = Store-to-store route (in distance order)
- 🔢 Numbered Circles = Stop order (1, 2, 3...)

## Tips & Best Practices

### For Best Results:

1. **Pre-filter stores** by region/state before selecting to reduce clutter
2. **Select 3-5 stores** per trip for realistic manager visits
3. **Check round-trip distance** to ensure it's within one day's travel
4. **Download routes** for sharing with managers or record-keeping
5. **Use IATA codes** (ATL, ORD, DEN) when searching for airports

### Distance Calculations:

- All distances are calculated using **geodesic (great circle) distance**
- This represents "as the crow flies" distance
- Actual driving distances will be longer (typically 20-30% more)
- Use store-to-store distance as an estimate for actual driving

### Geocoding Notes:

- Geocoding uses OpenStreetMap's free Nominatim service
- Rate limited to 1 request per second
- May take time for large batches (20 stores = ~20 seconds)
- Some addresses may fail to geocode - verify address format
- Results are cached to avoid repeated API calls

## Troubleshooting

**Issue**: "No stores match your filter criteria"  
**Solution**: Reset filters to "All Regions/States/Cities"

**Issue**: Stores not appearing on map  
**Solution**: Check that Lat/Long columns have valid coordinates

**Issue**: Geocoding fails for an address  
**Solution**: Try adding more detail (suite numbers, landmarks) or verify address format

**Issue**: Map not loading  
**Solution**: Refresh the page or check internet connection

## Technical Details

### Technologies Used:
- **Streamlit**: Web application framework
- **Folium**: Interactive mapping library
- **GeoPy**: Geocoding and distance calculations
- **Pandas**: Data manipulation
- **OpenStreetMap**: Map tiles and geocoding service

### Performance:
- Handles 100+ stores efficiently
- Real-time distance calculations
- Caches geocoding results for speed
- Responsive filtering and selection

### Data Privacy:
- All processing happens locally
- No data sent to external servers (except OpenStreetMap for geocoding)
- Store and airport data remains on your machine

## Future Enhancements

Potential features to add:
- [ ] Actual driving directions (Google Maps API)
- [ ] Multi-day trip planning
- [ ] Cost estimation (fuel, hotels)
- [ ] Calendar integration
- [ ] Historical trip tracking
- [ ] Optimal route algorithms (TSP solver)
- [ ] Export to Google Maps/Apple Maps

## Support

For issues or questions:
1. Check this README
2. Review the in-app instructions (sidebar)
3. Verify your data file formats match the expected structure

## Sample Data Overview

Your current data includes:
- **20 stores** across multiple states (AL, FL, GA, etc.)
- **Multiple airports** with major US hubs
- **Complete contact information** for each store
- **Pre-geocoded coordinates** for immediate use

Enjoy planning your store visits! 🗺️✈️
