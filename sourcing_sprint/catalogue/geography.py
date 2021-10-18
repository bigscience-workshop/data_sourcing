import json

import folium
from folium import Marker
from folium.plugins import MarkerCluster
from jinja2 import Template
import pandas as pd

regions, countries, region_tree = json.load(open("resources/country_regions.json", encoding="utf-8"))
country_centers = json.load(open("resources/country_center_coordinates.json", encoding="utf-8"))
country_mappings = json.load(open("resources/country_mappings.json", encoding="utf-8"))

WORLD_GEO_URL = (
    "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
)

ICON_CREATE_FUNCTIOM = """
    function(cluster) {
        var markers = cluster.getAllChildMarkers();
        var sum = 0;
        for (var i = 0; i < markers.length; i++) {
            sum += markers[i].options.props.resources;
        }

        return L.divIcon({
             html: '<b>' + sum + '</b>',
             className: 'marker-cluster marker-cluster-small',
             iconSize: new L.Point(20, 20)
        });
    }
"""

class MarkerWithProps(Marker):
    _template = Template(
        """
        {% macro script(this, kwargs) %}
        var {{this.get_name()}} = L.marker(
            [{{this.location[0]}}, {{this.location[1]}}],
            {
                icon: new L.Icon.Default(),
                {%- if this.draggable %}
                draggable: true,
                autoPan: true,
                {%- endif %}
                {%- if this.props %}
                props : {{ this.props }}
                {%- endif %}
                }
            )
            .addTo({{this._parent.get_name()}});
        {% endmacro %}
        """
    )

    def __init__(self, location, popup=None, tooltip=None, icon=None, draggable=False, props=None):
        super(MarkerWithProps, self).__init__(
            location=location, popup=popup, tooltip=tooltip, icon=icon, draggable=draggable
        )
        self.props = json.loads(json.dumps(props))

def get_region_center(region_name):
    latitudes = []
    longitudes = []
    for name in region_tree[region_name]:
        if name in region_tree:
            region_latitudes, region_longitudes = get_region_center(name)
            latitudes += region_latitudes
            longitudes += region_longitudes
        elif name in country_centers or name in country_mappings["to_center"]:
            country_center = country_centers[country_mappings["to_center"].get(name, name)]
            latitudes += [float(country_center["latitude"])]
            longitudes += [float(country_center["longitude"])]
    return latitudes, longitudes

def get_region_countries(region_name):
    countries = []
    for name in region_tree[region_name]:
        if name in region_tree:
            countries += get_region_countries(name)
        else:
            countries += [name]
    return countries

def make_choro_map(resource_counts, marker_thres=0):
    world_map = folium.Map(tiles="cartodbpositron", location=[0, 0], zoom_start=1.5)
    marker_cluster = MarkerCluster(icon_create_function=ICON_CREATE_FUNCTIOM)
    marker_cluster.add_to(world_map)
    for name, count in resource_counts.items():
        if name in country_centers or name in country_mappings["to_center"]:
            country_center = country_centers[country_mappings["to_center"].get(name, name)]
            MarkerWithProps(
                location=[country_center["latitude"], country_center["longitude"]],
                popup=f"{'Region' if name in region_tree else 'Country'} : {name}<br> \n Resources : {count} <br>",
                props={"name": name, "resources": count},
            ).add_to(marker_cluster)
        # put a pin at the center of the region
        elif name in region_tree:
            latitudes, longitudes = get_region_center(name)
            if len(latitudes) > 0:
                lat = sum(latitudes) / len(latitudes)
                lon = sum(longitudes) / len(longitudes)
                MarkerWithProps(
                    location=[lat, lon],
                    popup=f"{'Region' if name in region_tree else 'Country'} : {name}<br> \n Resources : {count} <br>",
                    props={"name": name, "resources": count},
                ).add_to(marker_cluster)
    # for choropleth, add counts to all countries in a region
    choropleth_counts = {}
    for loc_name in list(resource_counts.keys()):
        if loc_name in region_tree:
            for country_name in get_region_countries(loc_name):
                choropleth_counts[country_name] = choropleth_counts.get(country_name, 0) + resource_counts[loc_name]
        else:
            choropleth_counts[loc_name] = choropleth_counts.get(loc_name, 0) + resource_counts[loc_name]
    df_resource_counts = pd.DataFrame(
        [(country_mappings["to_outline"].get(n, n), c) for n, c in choropleth_counts.items()],
        columns=["Name", "Resources"],
    )
    folium.Choropleth(
        geo_data=WORLD_GEO_URL,
        name="resource map",
        data=df_resource_counts,
        columns=["Name", "Resources"],
        key_on="feature.properties.name",
        fill_color="PuRd",
        nan_fill_color="white",
    ).add_to(world_map)
    return world_map
