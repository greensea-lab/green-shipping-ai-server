from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

import geopandas as gpd
import folium
from folium.plugins import MiniMap, Fullscreen, MousePosition, MeasureControl

# Reuse the existing routing implementation
from app.models.geo.geo_models import route as route_mod

router = APIRouter()


class RouteMapRequest(BaseModel):
    origin: str = Field(..., description="Origin port name as in CSV")
    dest: str = Field(..., description="Destination port name as in CSV")


def _load_nonempty_gdf(path: str) -> Optional[gpd.GeoDataFrame]:
    gdf = gpd.read_file(path)
    if gdf is None or "geometry" not in gdf.columns:
        return None
    gdf = gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty]
    return gdf if len(gdf) else None


@router.post("/route-map", response_class=HTMLResponse, summary="OD로 해상 경로 계산 후 HTML 지도 반환")
def create_route_map(req: RouteMapRequest):
    """
    Compute a sea route between two ports using the existing A* pipeline,
    then render a Folium map and return as HTML.
    """
    # Set OD for the underlying module and run the pipeline (writes GeoJSONs)
    try:
        route_mod.ORIGIN_NAME = req.origin
        route_mod.DEST_NAME = req.dest
        route_mod.run_pipeline()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route computation failed: {e}")

    # Build a Folium map from the produced GeoJSONs (no file save; return HTML)
    route_path = route_mod.ROUTE_PATH
    od_path = route_mod.OD_PATH

    od = _load_nonempty_gdf(od_path)
    if od is None or len(od) == 0:
        raise HTTPException(status_code=500, detail="OD points are empty after routing")

    route = _load_nonempty_gdf(route_path)

    # Compute center/bounds
    if route is not None and len(route):
        r4326 = route.to_crs("EPSG:4326")
        union = r4326.unary_union
        center = union.centroid
        minx, miny, maxx, maxy = r4326.total_bounds
    else:
        o4326 = od.to_crs("EPSG:4326")
        union = o4326.unary_union
        center = union.centroid
        minx, miny, maxx, maxy = o4326.total_bounds

    # Create map
    m = folium.Map(location=[center.y, center.x], zoom_start=4,
                   tiles="OpenStreetMap", control_scale=True)

    # Route layer (if available)
    if route is not None and len(route):
        folium.GeoJson(
            route.__geo_interface__,
            name="Sea Route (A*)",
            style_function=lambda f: {"color": "#ff6b00", "weight": 5, "opacity": 0.95},
        ).add_to(m)

    # OD markers
    for _, r in od.iterrows():
        lat, lon = r.geometry.y, r.geometry.x
        folium.CircleMarker(
            location=(lat, lon),
            radius=6,
            color="#1f77b4",
            fill=True,
            fill_opacity=0.95,
            tooltip=r.get("name", "Port"),
        ).add_to(m)

    # Controls and fit bounds
    MiniMap(toggle_display=True).add_to(m)
    Fullscreen().add_to(m)
    MousePosition(position="bottomleft", separator=" | ", prefix="Lat/Lon:").add_to(m)
    m.add_child(MeasureControl(primary_length_unit="nautical_miles"))
    folium.LayerControl(collapsed=False).add_to(m)

    try:
        m.fit_bounds([[miny, minx], [maxy, maxx]], padding=(20, 20))
    except Exception:
        pass

    # Return as HTML (do not save a file)
    html = m.get_root().render()
    return HTMLResponse(content=html, media_type="text/html")

