import streamlit as st
import overpy
import pandas as pd

# Function to fetch hotels with detailed info
def get_hotels(city_name):
    api = overpy.Overpass()
    query = f"""
    [out:json][timeout:60];
    area["name"="{city_name}"]->.searchArea;
    (
      node["tourism"~"hotel|hostel|guest_house|motel"](area.searchArea);
      way["tourism"~"hotel|hostel|guest_house|motel"](area.searchArea);
      relation["tourism"~"hotel|hostel|guest_house|motel"](area.searchArea);
    );
    out center;
    """
    result = api.query(query)
    hotels = []

    def extract_info(tags, lat, lon):
        return {
            "name": tags.get("name", "Unnamed"),
            "street": tags.get("addr:street", ""),
            "housenumber": tags.get("addr:housenumber", ""),
            "city": tags.get("addr:city", ""),
            "postcode": tags.get("addr:postcode", ""),
            "country": tags.get("addr:country", ""),
            "phone": tags.get("phone", tags.get("contact:phone", "")),
            "website": tags.get("website", tags.get("contact:website", "")),
            "email": tags.get("email", tags.get("contact:email", "")),
            "stars": tags.get("stars", ""),
            "opening_hours": tags.get("opening_hours", ""),
            "lat": lat,
            "lon": lon
        }

    for node in result.nodes:
        hotels.append(extract_info(node.tags, node.lat, node.lon))
    for way in result.ways:
        hotels.append(extract_info(way.tags, way.center_lat, way.center_lon))
    for rel in result.relations:
        hotels.append(extract_info(rel.tags, rel.center_lat, rel.center_lon))

    return hotels


# Streamlit UI
st.set_page_config(layout="wide")  # 🔑 Makes page full-width
st.title("🌍 Hotel Finder (OSM)")
city = st.text_input("Enter City or Country Name:", "New York")

if st.button("Find Hotels"):
    with st.spinner("Fetching hotels..."):
        hotels = get_hotels(city)

        if not hotels:
            st.warning("No hotels found!")
        else:
            st.success(f"Found {len(hotels)} hotels in {city} ✅")

            # Convert to DataFrame
            df = pd.DataFrame(hotels)

            # Show big wide dataframe
            st.dataframe(df, use_container_width=True, height=600)  # 🔑 Bigger grid

            # Download option
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv, f"{city}_hotels.csv", "text/csv")
