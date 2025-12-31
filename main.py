import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
import requests
import polyline as pl

# Page configuration
st.set_page_config(
    page_title="Store Route Planner",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Store Location & Airport Route Planner")
st.caption("Automatically finds the closest airport and optimizes your route")

# Initialize geocoder
@st.cache_resource
def get_geocoder():
    return Nominatim(user_agent="store_route_planner")

geocoder = get_geocoder()

# Geocoding function with caching
@st.cache_data
def geocode_address(address, city, state, zip_code):
    """Convert address components to latitude and longitude"""
    try:
        # Combine address components
        full_address = f"{address}, {city}, {state} {zip_code}"
        time.sleep(1)  # Respect rate limits
        location = geocoder.geocode(full_address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        st.error(f"Geocoding error for {full_address}: {str(e)}")
        return None, None

# Calculate distance between two points
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in miles between two coordinates"""
    return geodesic((lat1, lon1), (lat2, lon2)).miles

# Get driving route using OSRM (OpenStreetMap Routing Machine)
@st.cache_data(ttl=3600)
def get_driving_route(start_lat, start_lon, end_lat, end_lon):
    """
    Get actual driving route between two points using OSRM.
    Returns: (route_coordinates, distance_miles, duration_minutes)
    """
    try:
        # OSRM API endpoint (free, no API key needed)
        url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            'overview': 'full',
            'geometries': 'geojson'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['code'] == 'Ok' and len(data['routes']) > 0:
                route = data['routes'][0]
                
                # Extract route coordinates
                coordinates = route['geometry']['coordinates']
                # Convert from [lon, lat] to [lat, lon] for folium
                route_coords = [[coord[1], coord[0]] for coord in coordinates]
                
                # Get distance in miles (OSRM returns meters)
                distance_miles = route['distance'] / 1609.34
                
                # Get duration in minutes (OSRM returns seconds)
                duration_minutes = route['duration'] / 60
                
                return route_coords, distance_miles, duration_minutes
            else:
                return None, None, None
        else:
            return None, None, None
            
    except Exception as e:
        # If routing fails, return None (will fall back to straight line)
        return None, None, None

# Optimize route using nearest neighbor algorithm
def optimize_route_nearest_neighbor(stores, start_lat, start_lon):
    """
    Optimize route using nearest neighbor algorithm starting from airport.
    Returns stores dataframe sorted in optimal visit order.
    """
    if len(stores) == 0:
        return stores
    
    stores = stores.copy()
    route = []
    remaining = list(stores.index)
    
    # Start from airport location
    current_lat, current_lon = start_lat, start_lon
    
    # Build route by always going to nearest unvisited store
    while remaining:
        # Calculate distances from current location to all remaining stores
        distances = []
        for idx in remaining:
            store = stores.loc[idx]
            dist = calculate_distance(current_lat, current_lon, 
                                     store['Latitude'], store['Longitude'])
            distances.append((idx, dist))
        
        # Find nearest store
        nearest_idx, nearest_dist = min(distances, key=lambda x: x[1])
        route.append(nearest_idx)
        remaining.remove(nearest_idx)
        
        # Update current location to the store we just added
        current_lat = stores.loc[nearest_idx, 'Latitude']
        current_lon = stores.loc[nearest_idx, 'Longitude']
    
    # Return stores in optimized order
    return stores.loc[route]

# Sidebar for file uploads
st.sidebar.header("📁 Upload Data Files")

# Store file upload
store_file = st.sidebar.file_uploader(
    "Upload Store Locations (CSV/Excel)",
    type=['csv', 'xlsx'],
    help="File should contain: Address, Email, Owner, and optionally Latitude/Longitude"
)

# Airport file upload
airport_file = st.sidebar.file_uploader(
    "Upload Airport Locations (CSV/Excel)",
    type=['csv', 'xlsx'],
    help="File should contain: Airport Name, Latitude, Longitude"
)

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Data Overview", 
    "🌍 Interactive Map", 
    "🛣️ Route Planning",
    "📍 Geocode Addresses"
])

# Load data
stores_df = None
airports_df = None

if store_file:
    if store_file.name.endswith('.csv'):
        stores_df = pd.read_csv(store_file)
    else:
        stores_df = pd.read_excel(store_file)
    
    # Standardize column names for easier handling
    if 'Lat' in stores_df.columns:
        stores_df['Latitude'] = stores_df['Lat']
    if 'Long' in stores_df.columns:
        stores_df['Longitude'] = stores_df['Long']

if airport_file:
    if airport_file.name.endswith('.csv'):
        airports_df = pd.read_csv(airport_file)
    else:
        airports_df = pd.read_excel(airport_file)
    
    # Standardize column names
    if 'LATITUDE' in airports_df.columns:
        airports_df['Latitude'] = airports_df['LATITUDE']
    if 'LONGITUDE' in airports_df.columns:
        airports_df['Longitude'] = airports_df['LONGITUDE']

# TAB 1: Data Overview
with tab1:
    st.header("Data Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏪 Store Locations")
        if stores_df is not None:
            st.dataframe(stores_df, use_container_width=True)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Stores", len(stores_df))
            with col_b:
                if 'Latitude' in stores_df.columns and 'Longitude' in stores_df.columns:
                    stores_with_coords = stores_df.dropna(subset=['Latitude', 'Longitude'])
                    st.metric("Stores with Coordinates", len(stores_with_coords))
            with col_c:
                if 'Region' in stores_df.columns:
                    st.metric("Regions", stores_df['Region'].nunique())
        else:
            st.info("Please upload a store locations file")
    
    with col2:
        st.subheader("✈️ Airport Locations")
        if airports_df is not None:
            st.dataframe(airports_df, use_container_width=True)
            st.metric("Total Airports", len(airports_df))
        else:
            st.info("Please upload an airport locations file")

# TAB 2: Interactive Map
with tab2:
    st.header("Interactive Map")
    
    if stores_df is not None or airports_df is not None:
        # Create base map - center of USA
        center_lat = 39.8283
        center_lon = -98.5795
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=4,
            tiles='OpenStreetMap'
        )
        
        # Add airports to map
        if airports_df is not None and 'Latitude' in airports_df.columns:
            airport_group = folium.FeatureGroup(name='Airports')
            
            for idx, row in airports_df.iterrows():
                if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
                    airport_name = row.get('AIRPORT', row.get('Airport Name', 'Airport'))
                    iata_code = row.get('IATA', row.get('Code', ''))
                    city = row.get('CITY', row.get('City', ''))
                    state = row.get('STATE', row.get('State', ''))
                    
                    popup_html = f"""
                    <b>{airport_name}</b><br>
                    Code: {iata_code}<br>
                    Location: {city}, {state}<br>
                    Lat: {row['Latitude']:.4f}<br>
                    Lon: {row['Longitude']:.4f}
                    """
                    
                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']],
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"{iata_code} - {airport_name}",
                        icon=folium.Icon(color='blue', icon='plane', prefix='fa')
                    ).add_to(airport_group)
            
            airport_group.add_to(m)
        
        # Add stores to map
        if stores_df is not None and 'Latitude' in stores_df.columns:
            store_group = folium.FeatureGroup(name='Stores')
            
            for idx, row in stores_df.iterrows():
                if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
                    popup_html = f"""
                    <b>{row.get('StoreName', 'Store')}</b><br>
                    Code: {row.get('StoreCode', 'N/A')}<br>
                    Address: {row.get('Address', '')}<br>
                    City: {row.get('City', '')}, {row.get('State', '')} {row.get('Zip', '')}<br>
                    Owner: {row.get('Owner', 'N/A')}<br>
                    Email: {row.get('Email', 'N/A')}<br>
                    Phone: {row.get('Phone', 'N/A')}<br>
                    Region: {row.get('Region', 'N/A')}
                    """
                    
                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{row.get('StoreCode', 'Store')} - {row.get('City', '')}",
                        icon=folium.Icon(color='red', icon='store', prefix='fa')
                    ).add_to(store_group)
            
            store_group.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Display map
        st_folium(m, width=1400, height=600)
        
    else:
        st.info("Upload store and/or airport data to view the map")

# TAB 3: Route Planning
with tab3:
    st.header("Route Planning with Automatic Airport Selection")
    
    if stores_df is not None and airports_df is not None:
        # Check if stores have coordinates
        if 'Latitude' not in stores_df.columns or 'Longitude' not in stores_df.columns:
            st.warning("Please geocode your store addresses first in the 'Geocode Addresses' tab")
        else:
            # Filter section
            st.subheader("🔍 Filter Options")
            
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                # Region filter
                if 'Region' in stores_df.columns:
                    regions = ['All Regions'] + sorted(stores_df['Region'].dropna().unique().tolist())
                    selected_region = st.selectbox("Filter by Region", regions)
                else:
                    selected_region = 'All Regions'
            
            with filter_col2:
                # State filter
                if 'State' in stores_df.columns:
                    states = ['All States'] + sorted(stores_df['State'].dropna().unique().tolist())
                    selected_state = st.selectbox("Filter by State", states)
                else:
                    selected_state = 'All States'
            
            with filter_col3:
                # City filter
                if 'City' in stores_df.columns:
                    cities = ['All Cities'] + sorted(stores_df['City'].dropna().unique().tolist())
                    selected_city = st.selectbox("Filter by City", cities)
                else:
                    selected_city = 'All Cities'
            
            # Apply filters
            filtered_stores = stores_df.copy()
            if selected_region != 'All Regions':
                filtered_stores = filtered_stores[filtered_stores['Region'] == selected_region]
            if selected_state != 'All States':
                filtered_stores = filtered_stores[filtered_stores['State'] == selected_state]
            if selected_city != 'All Cities':
                filtered_stores = filtered_stores[filtered_stores['City'] == selected_city]
            
            st.info(f"Showing {len(filtered_stores)} stores after filtering")
            
            st.markdown("---")
            
            # Store selection (NO manual airport selection)
            st.subheader("🏪 Select Stores to Visit")
            
            if len(filtered_stores) > 0:
                store_display = filtered_stores.apply(
                    lambda x: f"{x.get('StoreCode', 'N/A')} - {x.get('City', '')}, {x.get('State', '')} ({x.get('Address', '')})",
                    axis=1
                ).tolist()
                
                selected_stores_display = st.multiselect(
                    "Choose stores for this trip",
                    store_display,
                    help="Select stores - the app will automatically find the closest airport and optimize the route"
                )
            else:
                st.warning("No stores match your filter criteria")
                selected_stores_display = []
            
            if selected_stores_display:
                # Get selected store indices
                selected_indices = [store_display.index(s) for s in selected_stores_display]
                selected_stores = filtered_stores.iloc[selected_indices].copy()
                
                # Calculate centroid (geographic center) of selected stores
                centroid_lat = selected_stores['Latitude'].mean()
                centroid_lon = selected_stores['Longitude'].mean()
                
                st.markdown("---")
                
                # Find closest airport to the centroid
                airports_df['Distance_to_Stores'] = airports_df.apply(
                    lambda row: calculate_distance(
                        centroid_lat, centroid_lon,
                        row['Latitude'], row['Longitude']
                    ),
                    axis=1
                )
                
                closest_airport = airports_df.loc[airports_df['Distance_to_Stores'].idxmin()]
                airport_lat = closest_airport['Latitude']
                airport_lon = closest_airport['Longitude']
                airport_name = closest_airport.get('AIRPORT', closest_airport.get('Airport Name', 'Airport'))
                airport_code = closest_airport.get('IATA', closest_airport.get('Code', ''))
                airport_city = closest_airport.get('CITY', closest_airport.get('City', ''))
                airport_state = closest_airport.get('STATE', closest_airport.get('State', ''))
                
                # Show recommended airport
                st.success(f"✈️ **Recommended Airport:** {airport_code} - {airport_name} ({airport_city}, {airport_state})")
                st.caption(f"📍 Closest airport to your selected stores ({closest_airport['Distance_to_Stores']:.1f} miles from geographic center)")
                
                # Option to see other nearby airports
                with st.expander("🔍 See Other Nearby Airports (Optional Override)"):
                    nearby_airports = airports_df.nsmallest(5, 'Distance_to_Stores').copy()
                    display_cols = []
                    if 'IATA' in nearby_airports.columns:
                        display_cols.append('IATA')
                    if 'AIRPORT' in nearby_airports.columns:
                        display_cols.append('AIRPORT')
                    if 'CITY' in nearby_airports.columns:
                        display_cols.append('CITY')
                    if 'STATE' in nearby_airports.columns:
                        display_cols.append('STATE')
                    display_cols.append('Distance_to_Stores')
                    
                    nearby_display = nearby_airports[display_cols].copy()
                    nearby_display.columns = ['Code', 'Airport Name', 'City', 'State', 'Distance (mi)']
                    nearby_display['Distance (mi)'] = nearby_display['Distance (mi)'].round(1)
                    st.dataframe(nearby_display, use_container_width=True)
                    
                    # Allow override if needed
                    override_options = ['✓ Use Recommended (' + airport_code + ')'] + [
                        f"{row['IATA']} - {row['AIRPORT']}" 
                        for _, row in nearby_airports.iterrows() 
                        if row['IATA'] != airport_code
                    ]
                    
                    override_selection = st.selectbox(
                        "Override airport selection?",
                        override_options,
                        help="Change to a different airport if needed"
                    )
                    
                    if not override_selection.startswith('✓'):
                        # Extract IATA code from selection
                        override_code = override_selection.split(' - ')[0]
                        override_row = airports_df[airports_df['IATA'] == override_code].iloc[0]
                        airport_lat = override_row['Latitude']
                        airport_lon = override_row['Longitude']
                        airport_name = override_row.get('AIRPORT', override_row.get('Airport Name', 'Airport'))
                        airport_code = override_row.get('IATA', override_row.get('Code', ''))
                        airport_city = override_row.get('CITY', override_row.get('City', ''))
                        airport_state = override_row.get('STATE', override_row.get('State', ''))
                        st.info(f"✈️ Using: {airport_code} - {airport_name}")
                
                st.markdown("---")
                
                # Optimize route using nearest neighbor algorithm starting from airport
                route_stores = optimize_route_nearest_neighbor(selected_stores, airport_lat, airport_lon)
                route_stores = route_stores.reset_index(drop=True)
                
                # Calculate distance from airport to first store
                route_stores['Distance_from_Airport'] = route_stores.apply(
                    lambda row: calculate_distance(
                        airport_lat, airport_lon,
                        row['Latitude'], row['Longitude']
                    ),
                    axis=1
                )
                
                # Calculate distance from previous store (for driving route)
                route_stores['Distance_from_Previous'] = 0.0
                for i in range(len(route_stores)):
                    if i == 0:
                        # First store: distance from airport
                        route_stores.at[i, 'Distance_from_Previous'] = route_stores.at[i, 'Distance_from_Airport']
                    else:
                        # Subsequent stores: distance from previous store
                        prev_lat = route_stores.iloc[i-1]['Latitude']
                        prev_lon = route_stores.iloc[i-1]['Longitude']
                        curr_lat = route_stores.iloc[i]['Latitude']
                        curr_lon = route_stores.iloc[i]['Longitude']
                        route_stores.at[i, 'Distance_from_Previous'] = calculate_distance(
                            prev_lat, prev_lon, curr_lat, curr_lon
                        )
                
                # Calculate cumulative distance
                route_stores['Cumulative_Distance'] = route_stores['Distance_from_Previous'].cumsum()
                
                # Display route information
                st.subheader("📋 Optimized Route Summary")
                
                # Calculate total driving distance (store to store)
                total_driving_distance = route_stores['Distance_from_Previous'].sum()
                
                # Calculate distance back to airport from last store
                last_store_to_airport = calculate_distance(
                    route_stores.iloc[-1]['Latitude'],
                    route_stores.iloc[-1]['Longitude'],
                    airport_lat, airport_lon
                )
                round_trip = total_driving_distance + last_store_to_airport
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                with metric_col1:
                    st.metric("Stores to Visit", len(route_stores))
                with metric_col2:
                    st.metric("First Store Distance", f"{route_stores.iloc[0]['Distance_from_Airport']:.1f} mi")
                with metric_col3:
                    st.metric("Total Driving Distance", f"{total_driving_distance:.1f} mi")
                with metric_col4:
                    st.metric("Round Trip Total", f"{round_trip:.1f} mi")
                
                # Display route table
                st.subheader("🗺️ Optimized Route Details")
                
                st.info(f"**Route Strategy:** Starting from {airport_code}, visiting stores in optimal order using nearest-neighbor algorithm")
                
                # Create display dataframe
                display_df = route_stores[[
                    'StoreCode', 'StoreName', 'Address', 'City', 'State', 'Zip',
                    'Owner', 'Email', 'Phone', 'Distance_from_Previous', 'Cumulative_Distance'
                ]].copy()
                
                display_df['Distance_from_Previous'] = display_df['Distance_from_Previous'].round(1)
                display_df['Cumulative_Distance'] = display_df['Cumulative_Distance'].round(1)
                display_df.insert(0, 'Stop', range(1, len(display_df) + 1))
                
                # Rename columns for clarity
                display_df = display_df.rename(columns={
                    'Distance_from_Previous': 'Leg_Distance_mi',
                    'Cumulative_Distance': 'Total_Distance_mi'
                })
                
                st.dataframe(display_df, use_container_width=True)
                
                # Add explanation
                st.caption("**Leg Distance**: Distance from previous location (airport for Stop 1, previous store for others)")
                st.caption("**Total Distance**: Cumulative driving distance from airport through current stop")
                
                # Download button
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Route Details",
                    data=csv,
                    file_name=f"route_{airport_code}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
                # Create route map
                st.subheader("🗺️ Route Visualization")
                
                # Add toggle for road routing
                col_toggle1, col_toggle2 = st.columns([3, 1])
                with col_toggle1:
                    st.info("📍 Map shows actual driving routes using road networks (powered by OpenStreetMap)")
                with col_toggle2:
                    show_roads = st.checkbox("Use Road Routes", value=True, help="Show actual driving routes on roads (recommended)")
                
                # Calculate map center and zoom
                all_lats = [airport_lat] + route_stores['Latitude'].tolist()
                all_lons = [airport_lon] + route_stores['Longitude'].tolist()
                center_map_lat = sum(all_lats) / len(all_lats)
                center_map_lon = sum(all_lons) / len(all_lons)
                
                route_map = folium.Map(
                    location=[center_map_lat, center_map_lon],
                    zoom_start=6
                )
                
                # Add airport marker
                folium.Marker(
                    location=[airport_lat, airport_lon],
                    popup=f"<b>{airport_code} - {airport_name}</b><br>Arrival Airport<br>Start of Route",
                    tooltip=f"Arrival: {airport_code}",
                    icon=folium.Icon(color='blue', icon='plane', prefix='fa', icon_color='white')
                ).add_to(route_map)
                
                # Add store markers with optimized route information
                for idx, row in route_stores.iterrows():
                    stop_num = idx + 1
                    
                    # Build popup HTML with leg and cumulative distances
                    popup_html = f"""
                    <div style='width: 280px'>
                        <h4>Stop {stop_num}: {row['StoreCode']}</h4>
                        <b>{row['StoreName']}</b><br>
                        {row['Address']}<br>
                        {row['City']}, {row['State']} {row['Zip']}<br><br>
                        <b>Owner:</b> {row['Owner']}<br>
                        <b>Email:</b> {row['Email']}<br>
                        <b>Phone:</b> {row['Phone']}<br><br>
                        <b>Leg Distance:</b> {row['Distance_from_Previous']:.1f} miles<br>
                        <b>Total Distance:</b> {row['Cumulative_Distance']:.1f} miles from airport
                    </div>
                    """
                    
                    tooltip_text = f"Stop {stop_num}: {row['StoreCode']} ({row['Distance_from_Previous']:.1f} mi)"
                    
                    # Store marker with numbered icon
                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=tooltip_text,
                        icon=folium.Icon(
                            color='red', 
                            icon='info-sign', 
                            prefix='glyphicon'
                        )
                    ).add_to(route_map)
                    
                    # Add numbered label
                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']],
                        icon=folium.DivIcon(html=f"""
                            <div style="
                                font-size: 14pt; 
                                color: white; 
                                font-weight: bold;
                                text-align: center;
                                background-color: #d63384;
                                border-radius: 50%;
                                width: 30px;
                                height: 30px;
                                line-height: 30px;
                                margin-left: -15px;
                                margin-top: -15px;
                                border: 2px solid white;
                            ">{stop_num}</div>
                        """)
                    ).add_to(route_map)
                    
                    # Draw route line from previous location to this store
                    if idx == 0:
                        # First store: line from airport
                        prev_lat, prev_lon = airport_lat, airport_lon
                        line_label = f"Airport → Stop 1: {row['Distance_from_Previous']:.1f} mi"
                    else:
                        # Subsequent stores: line from previous store
                        prev_lat = route_stores.iloc[idx-1]['Latitude']
                        prev_lon = route_stores.iloc[idx-1]['Longitude']
                        line_label = f"Stop {idx} → Stop {stop_num}: {row['Distance_from_Previous']:.1f} mi"
                    
                    if show_roads:
                        # Try to get actual driving route
                        route_coords, driving_dist, driving_time = get_driving_route(
                            prev_lat, prev_lon,
                            row['Latitude'], row['Longitude']
                        )
                        
                        if route_coords:
                            # Use actual road route
                            popup_text = f"{line_label}<br>Driving Time: ~{driving_time:.0f} min"
                            folium.PolyLine(
                                locations=route_coords,
                                color='#FF6B35',  # Orange-red for driving route
                                weight=4,
                                opacity=0.8,
                                popup=popup_text,
                                tooltip=f"{driving_dist:.1f} mi, ~{driving_time:.0f} min"
                            ).add_to(route_map)
                        else:
                            # Fallback to straight line if routing fails
                            folium.PolyLine(
                                locations=[
                                    [prev_lat, prev_lon],
                                    [row['Latitude'], row['Longitude']]
                                ],
                                color='#FF6B35',
                                weight=4,
                                opacity=0.6,
                                popup=line_label,
                                dash_array='5, 5'  # Dashed to indicate it's not actual route
                            ).add_to(route_map)
                    else:
                        # Show straight line (direct distance)
                        folium.PolyLine(
                            locations=[
                                [prev_lat, prev_lon],
                                [row['Latitude'], row['Longitude']]
                            ],
                            color='#FF6B35',
                            weight=4,
                            opacity=0.8,
                            popup=line_label
                        ).add_to(route_map)
                
                # Add return line to airport from last store
                if show_roads:
                    return_coords, return_dist, return_time = get_driving_route(
                        route_stores.iloc[-1]['Latitude'],
                        route_stores.iloc[-1]['Longitude'],
                        airport_lat, airport_lon
                    )
                    
                    if return_coords:
                        popup_text = f"Return to {airport_code}: {return_dist:.1f} mi<br>Driving Time: ~{return_time:.0f} min"
                        folium.PolyLine(
                            locations=return_coords,
                            color='#4A90E2',  # Blue for return
                            weight=3,
                            opacity=0.6,
                            popup=popup_text,
                            tooltip=f"{return_dist:.1f} mi, ~{return_time:.0f} min"
                        ).add_to(route_map)
                    else:
                        # Fallback to straight line
                        folium.PolyLine(
                            locations=[
                                [route_stores.iloc[-1]['Latitude'], route_stores.iloc[-1]['Longitude']],
                                [airport_lat, airport_lon]
                            ],
                            color='#4A90E2',
                            weight=3,
                            opacity=0.6,
                            dash_array='10, 5',
                            popup=f"Return to {airport_code}: {last_store_to_airport:.1f} mi (estimated)"
                        ).add_to(route_map)
                else:
                    # Show straight line
                    folium.PolyLine(
                        locations=[
                            [route_stores.iloc[-1]['Latitude'], route_stores.iloc[-1]['Longitude']],
                            [airport_lat, airport_lon]
                        ],
                        color='#4A90E2',
                        weight=3,
                        opacity=0.6,
                        dash_array='10, 5',
                        popup=f"Return to {airport_code}: {last_store_to_airport:.1f} mi"
                    ).add_to(route_map)
                
                st_folium(route_map, width=1400, height=600)
                
                # Trip Insights
                st.subheader("📊 Trip Insights")
                
                insight_col1, insight_col2, insight_col3 = st.columns(3)
                
                with insight_col1:
                    first_store = route_stores.iloc[0]
                    st.success(f"""
                    **🎯 First Stop (Nearest)**
                    
                    {first_store['StoreCode']} - {first_store['City']}, {first_store['State']}
                    
                    {first_store['Distance_from_Airport']:.1f} miles from {airport_code}
                    """)
                
                with insight_col2:
                    last_store = route_stores.iloc[-1]
                    st.info(f"""
                    **🏁 Last Stop**
                    
                    {last_store['StoreCode']} - {last_store['City']}, {last_store['State']}
                    
                    {last_store_to_airport:.1f} miles back to {airport_code}
                    """)
                
                with insight_col3:
                    st.warning(f"""
                    **🔄 Complete Round Trip**
                    
                    {airport_code} → {len(route_stores)} Stores → {airport_code}
                    
                    {round_trip:.1f} miles total
                    """)
                
                # Add route efficiency info
                st.markdown("---")
                st.subheader("🚗 Route Breakdown")
                
                breakdown_col1, breakdown_col2 = st.columns(2)
                
                with breakdown_col1:
                    st.markdown("**Outbound Journey**")
                    for idx, row in route_stores.iterrows():
                        if idx == 0:
                            st.text(f"✈️  {airport_code} → Stop 1 ({row['StoreCode']}): {row['Distance_from_Previous']:.1f} mi")
                        else:
                            prev_code = route_stores.iloc[idx-1]['StoreCode']
                            st.text(f"🏪 Stop {idx} ({prev_code}) → Stop {idx+1} ({row['StoreCode']}): {row['Distance_from_Previous']:.1f} mi")
                
                with breakdown_col2:
                    st.markdown("**Summary Statistics**")
                    st.metric("Total Outbound Distance", f"{total_driving_distance:.1f} mi")
                    st.metric("Return to Airport", f"{last_store_to_airport:.1f} mi")
                    if len(route_stores) > 1:
                        avg_leg = total_driving_distance / len(route_stores)
                        st.metric("Average Leg Distance", f"{avg_leg:.1f} mi")
                
    else:
        st.info("Please upload both store and airport data to plan routes")

# TAB 4: Geocode Addresses
with tab4:
    st.header("Geocode Store Addresses")
    st.write("Convert store addresses to latitude and longitude coordinates")
    
    if stores_df is not None:
        # Check if coordinates already exist
        has_coords = 'Latitude' in stores_df.columns and 'Longitude' in stores_df.columns
        
        if has_coords:
            stores_with_coords = stores_df.dropna(subset=['Latitude', 'Longitude'])
            stores_without_coords = stores_df[
                stores_df['Latitude'].isna() | stores_df['Longitude'].isna()
            ]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Stores with Coordinates", len(stores_with_coords))
            with col2:
                st.metric("Stores Missing Coordinates", len(stores_without_coords))
            
            if len(stores_without_coords) > 0:
                st.warning(f"{len(stores_without_coords)} stores are missing coordinates")
                
                if st.button("🌍 Geocode Missing Stores"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, row in stores_without_coords.iterrows():
                        address = f"{row['Address']}, {row['City']}, {row['State']} {row['Zip']}"
                        status_text.text(f"Geocoding: {row['StoreCode']} - {address}")
                        
                        lat, lon = geocode_address(row['Address'], row['City'], row['State'], row['Zip'])
                        
                        if lat and lon:
                            stores_df.at[idx, 'Latitude'] = lat
                            stores_df.at[idx, 'Longitude'] = lon
                            stores_df.at[idx, 'Lat'] = lat
                            stores_df.at[idx, 'Long'] = lon
                        
                        progress = (idx + 1) / len(stores_without_coords)
                        progress_bar.progress(progress)
                    
                    st.success(f"✅ Geocoded {len(stores_without_coords)} stores!")
                    
                    # Offer download
                    csv = stores_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Updated Store Data (CSV)",
                        data=csv,
                        file_name="stores_with_coordinates.csv",
                        mime="text/csv"
                    )
                    
                    status_text.empty()
                    progress_bar.empty()
            else:
                st.success("✅ All stores have coordinates!")
        
        # Manual geocoding
        st.markdown("---")
        st.subheader("🔍 Geocode Individual Address")
        
        manual_col1, manual_col2 = st.columns(2)
        with manual_col1:
            manual_address = st.text_input("Street Address")
            manual_city = st.text_input("City")
        with manual_col2:
            manual_state = st.text_input("State")
            manual_zip = st.text_input("ZIP Code")
        
        if st.button("Get Coordinates"):
            if manual_address and manual_city and manual_state:
                with st.spinner("Geocoding..."):
                    lat, lon = geocode_address(manual_address, manual_city, manual_state, manual_zip)
                    
                    if lat and lon:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.success(f"**Latitude:** {lat:.6f}")
                        with col2:
                            st.success(f"**Longitude:** {lon:.6f}")
                        
                        # Show on small map
                        mini_map = folium.Map(location=[lat, lon], zoom_start=15)
                        folium.Marker(
                            [lat, lon],
                            popup=f"{manual_address}, {manual_city}, {manual_state} {manual_zip}",
                            icon=folium.Icon(color='red', icon='map-marker', prefix='fa')
                        ).add_to(mini_map)
                        st_folium(mini_map, width=700, height=400)
                    else:
                        st.error("Could not geocode this address. Please check the format.")
            else:
                st.warning("Please fill in at least Address, City, and State")
    else:
        st.info("Please upload a store locations file first")

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ How It Works")
st.sidebar.markdown("""
1. **Upload Files**: Store Excel and Airport CSV
2. **Select Stores**: Choose which stores to visit
3. **Automatic Airport**: App finds closest airport
4. **Optimized Route**: Nearest-neighbor algorithm
5. **Download**: Get route details as CSV
""")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Key Features")
st.sidebar.markdown("""
- ✈️ Automatic airport selection
- 🗺️ Optimized route planning
- 📊 Distance calculations
- 🔄 Round trip planning
- 📥 CSV export
""")