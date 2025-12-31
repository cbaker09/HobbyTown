# Store Route Planner v2.0 - Automatic Airport Selection

## 🎯 What's New

**The biggest change:** You no longer select an airport manually! The app automatically finds the closest airport to your selected stores.

## ✨ Key Improvements

### Before (v1.0)
1. Select stores
2. **Manually choose airport** ❌ 
3. View optimized route

### After (v2.0)
1. Select stores
2. **App auto-finds closest airport** ✅
3. View optimized route

## 🚀 How It Works Now

### Step-by-Step

**1. Filter Stores (Optional)**
- Region: "Southeast"
- State: "GA"
- City: (Leave as "All Cities")

**2. Select Stores**
- Choose the stores you want to visit
- Example: Select all 5 Georgia stores

**3. Automatic Airport Detection**
The app:
- Calculates the geographic center (centroid) of your selected stores
- Finds the closest airport to that center
- **Automatically recommends the best airport**

**4. View Optimized Route**
- Starting from the recommended airport
- Visiting stores in optimal order
- Returning to the same airport

### Example

**Selected Stores:**
- GAKEN (Kennesaw, GA)
- GABUF (Buford, GA)
- GACOL (Columbus, GA)
- GACO2 (Columbus, GA)
- GAAUG (Martinez, GA)

**What Happens:**
```
1. App calculates center point of these 5 stores
2. Searches all airports for closest one
3. Finds: ATL (Atlanta) - 68.4 miles from center
4. Recommends ATL as arrival airport
5. Optimizes route starting from ATL
```

**Your Optimized Route:**
```
✈️  ATL → Stop 1 (GAKEN): 28.4 mi
🏪 Stop 1 → Stop 2 (GABUF): 36.2 mi
🏪 Stop 2 → Stop 3 (GAAUG): 117.9 mi
🏪 Stop 3 → Stop 4 (GACOL): 184.1 mi
🏪 Stop 4 → Stop 5 (GACO2): 0.0 mi
🔄 Stop 5 → ATL: 87.7 mi

Total: 454.3 miles
```

## 🔍 Airport Override Feature

Don't like the recommended airport? No problem!

**Expand "See Other Nearby Airports":**
- View the 5 closest airports
- See distances to your store group
- Select a different airport if preferred

**Example:**
```
Recommended: ATL (68.4 mi from stores)

Nearby Options:
- ATL - William B Hartsfield-Atlanta: 68.4 mi ← Recommended
- AGS - Augusta Regional: 89.2 mi
- MCN - Middle Georgia Regional: 102.1 mi
- CSG - Columbus Metro: 115.3 mi
- CHA - Chattanooga Metro: 134.7 mi

Override: Choose any of these instead
```

## 📊 Real-World Examples

### Example 1: Regional Manager - Florida Visit

**Task:** Visit all Florida stores

**Your Actions:**
1. Filter: State = "FL"
2. Select: FLBRA, FLCLE (2 stores)

**App Response:**
```
✈️ Recommended Airport: TPA - Tampa International (14.2 miles from stores)

Optimized Route:
TPA → FLBRA (Brandon): 15.3 mi
FLBRA → FLCLE (Clearwater): 19.8 mi
FLCLE → TPA: 12.4 mi

Round Trip: 47.5 miles
```

### Example 2: Multi-State Tour

**Task:** Visit stores across multiple states

**Your Actions:**
1. No filters
2. Select: Stores in AL, GA, FL (mix of states)

**App Response:**
```
✈️ Recommended Airport: ATL - Atlanta (Central location)

The app finds the geographic middle point and recommends
the airport closest to that center, minimizing total travel.
```

### Example 3: Single City Focus

**Task:** Audit all Columbus, GA stores

**Your Actions:**
1. Filter: City = "Columbus"
2. Select: GACOL, GACO2

**App Response:**
```
✈️ Recommended Airport: CSG - Columbus Metro (3.2 miles from stores)

Optimized Route:
CSG → GACOL: 3.8 mi
GACOL → GACO2: 0.0 mi (same location)
GACO2 → CSG: 2.9 mi

Round Trip: 6.7 miles
```

## 🎯 Benefits of Automatic Selection

### Time Savings
- ⏱️ No need to research which airport to use
- ⏱️ No manual comparison of distances
- ⏱️ Instant recommendation

### Accuracy
- 📍 Mathematically optimal airport selection
- 📍 Based on actual geographic center
- 📍 Considers all selected stores equally

### Flexibility
- 🔄 Changes automatically as you add/remove stores
- 🔄 Always shows nearby alternatives
- 🔄 Easy to override if needed

## 💡 Pro Tips

### Get the Best Results

**Tip 1: Group Stores Geographically**
```
✅ Good: Select all stores in one region
❌ Avoid: Selecting stores 500+ miles apart
```

**Tip 2: Use Filters First**
```
✅ Good: Filter by State, then select stores
❌ Skip: Picking random stores across the country
```

**Tip 3: Check the Override Options**
```
Sometimes the 2nd or 3rd closest airport has:
- Better flight schedules
- Lower fares
- More convenient rental cars

Always check the nearby airports list!
```

**Tip 4: Consider Return Flights**
```
The app optimizes for ROUND TRIPS - you return to
the same airport you arrived at. This is typically
most cost-effective for manager trips.
```

## 🔧 Technical Details

### How Centroid Calculation Works

```python
# Given selected stores with coordinates:
stores = [
    (33.64, -84.43),  # Store 1
    (34.02, -84.62),  # Store 2
    (32.46, -84.99),  # Store 3
]

# Calculate centroid (average of all coordinates):
centroid_lat = (33.64 + 34.02 + 32.46) / 3 = 33.37
centroid_lon = (-84.43 + -84.62 + -84.99) / 3 = -84.68

# Find closest airport to (33.37, -84.68)
```

### Distance Calculation
- Uses **geodesic distance** (great circle)
- Accounts for Earth's curvature
- Accurate for distances up to 1000 miles

### Route Optimization
- **Nearest-neighbor algorithm**
- Starts at airport
- Always goes to closest unvisited store
- Continues until all stores visited
- Calculates return to airport

## 📋 Quick Reference

### App Flow

```
1. Upload Data
   ├─ stores.xlsx (your store data)
   └─ airports.csv (airport locations)

2. Filter Stores (Optional)
   ├─ By Region
   ├─ By State
   └─ By City

3. Select Stores
   └─ Multi-select the stores to visit

4. Auto Airport Selection
   ├─ App calculates store centroid
   ├─ Finds closest airport
   └─ Shows recommendation

5. View Optimized Route
   ├─ Interactive map
   ├─ Distance table
   ├─ Trip insights
   └─ Download CSV
```

### What You See

**Dashboard Metrics:**
- ✈️ Recommended Airport (with distance)
- 🏪 Stores to Visit
- 🛣️ First Store Distance
- 📏 Total Driving Distance
- 🔄 Round Trip Total

**Route Details Table:**
| Stop | Store | City | Owner | Email | Leg (mi) | Total (mi) |
|------|-------|------|-------|-------|----------|------------|
| 1    | GAKEN | Kennesaw | Mike | ... | 28.4 | 28.4 |
| 2    | GABUF | Buford | Dusty | ... | 36.2 | 64.6 |

**Interactive Map:**
- 🔵 Blue airplane: Arrival airport
- 🔴 Numbered markers: Stores (1, 2, 3...)
- 🟠 Orange lines: Driving route
- 🔵 Blue dashed: Return to airport

## 🚗 Using the Route

### Download and Share

1. **Click "Download Route Details"**
   - Gets CSV file with all info
   - Includes: stops, distances, contacts

2. **Share with Manager**
   - Email the CSV
   - Include map screenshot
   - Note the round-trip mileage

3. **Track the Trip**
   - Use leg distances for progress
   - Call stores to confirm visits
   - Log actual mileage for comparison

### Planning Considerations

**Time Estimation:**
```
Total Driving: 454 miles
Average Speed: 60 mph on highways, 30 mph in cities
Estimated Drive Time: 8-10 hours
Add: Meetings (2 hrs/store), lunch, gas stops
Realistic Trip: 1.5 days
```

**Lodging:**
```
If Round Trip > 400 miles → Consider overnight
Look for hotels near Stop 3 (halfway point)
```

**Expense Budgeting:**
```
Mileage: 454 mi × $0.67/mi = $304
Flight: ~$200-400
Hotel: $100-150
Meals: $50-75
Total: ~$650-925
```

## ❓ FAQs

**Q: What if I don't like the recommended airport?**
A: Click "See Other Nearby Airports" and select any of the 5 closest alternatives.

**Q: Can I select stores from different states?**
A: Yes! The app will find the optimal central airport for your selection.

**Q: Does it account for flight availability?**
A: No, it only considers geographic distance. Check flight schedules separately.

**Q: What if two stores are at the same address?**
A: The route will show 0.0 miles between them (like GACOL and GACO2).

**Q: Can I plan a one-way trip?**
A: Currently the app assumes round trips. For one-way, ignore the return distance.

**Q: How accurate are the distances?**
A: Geodesic distances are 95-98% accurate. Actual driving is typically 20-30% longer.

## 🎓 Best Practices

### For Managers

✅ **Review route before booking flights**
✅ **Check alternate airports for better fares**
✅ **Download route CSV for offline access**
✅ **Add 20-30% buffer to distance estimates**
✅ **Call stores to confirm availability**

### For Planners

✅ **Group stores by region for efficient routes**
✅ **Plan trips of 3-5 stores max per day**
✅ **Consider store hours and time zones**
✅ **Build in flexibility for delays**
✅ **Track actual vs. estimated mileage**

---

## 🚀 Ready to Start?

Launch the app:
```bash
streamlit run store_route_planner_v2.py
```

**No more guessing which airport to use - the app does it for you!** ✈️
