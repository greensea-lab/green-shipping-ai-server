# app/models/geo.py
import geopandas as gpd
import geodatasets as gds
import matplotlib.pyplot as plt

# 1) Natural Earth 'land' 데이터 경로 (geodatasets가 자동 캐시)
land_path = gds.get_path("naturalearth.land")
land = gpd.read_file(land_path)

# 2) 보기 좋은 세계지도 투영: Robinson (ESRI:54030)
#    EPSG 코드가 아니라 ESRI 코드 사용 (pyproj가 인식)
land_robinson = land.to_crs("ESRI:54030")

# 3) 스타일 설정: 바다(배경)=푸른색, 육지=옅은 갈색
OCEAN = "#7fb6ff"     # 푸른색(바다)
LAND  = "#d8c3a5"     # 옅은 갈색(육지)
EDGE  = "#594f43"     # 연한 바다/육지 경계선색

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=150)
ax.set_facecolor(OCEAN)  # 바다 색
land_robinson.plot(ax=ax, facecolor=LAND, edgecolor=EDGE, linewidth=0.3, antialiased=True)

# 여백/축/제목
ax.set_axis_off()
plt.title("World map (Robinson) — ocean emphasized, land muted", fontsize=12)
plt.tight_layout()
plt.show()

