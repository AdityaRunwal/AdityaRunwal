import json
from datetime import datetime, timedelta

# Load contribution data
with open("data/contributions.json", "r", encoding="utf-8") as file:
    data = json.load(file)

days = data["days"]

# SVG settings

CELL_SIZE = 11
GAP = 4
WEEKS = 53

WIDTH = 900
HEIGHT = 180

PALETTE = [
"#161b22",
"#0e4429",
"#006d32",
"#26a641",
"#39d353"
]

# Convert contribution data into dictionary

contribution_map = {
day["date"]: day["level"]
for day in days
}

today = datetime.today().date()

# Find starting Sunday

start_date = today - timedelta(days=(today.weekday() + 1) % 7)
start_date -= timedelta(weeks=WEEKS - 1)

svg = []

svg.append(f''' <svg xmlns="http://www.w3.org/2000/svg"
  width="{WIDTH}"
  height="{HEIGHT}"
  viewBox="0 0 {WIDTH} {HEIGHT}">

<style>
@keyframes appear {{
    from {{
        opacity: 0;
        transform: translateY(-10px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.cell {{
    animation: appear 0.5s ease forwards;
    opacity: 0;
}}
</style>

<rect width="100%" height="100%" rx="12" fill="#0d1117"/>

<text x="30" y="30"
   fill="#c9d1d9"
   font-family="monospace"
   font-size="16">
{data["username"]}@github ~ $ contributions </text>
''')

# Draw contribution cells

for week in range(WEEKS):
    for day_of_week in range(7):


        current_date = start_date + timedelta(
        weeks=week,
        days=day_of_week
    )

    date_string = current_date.isoformat()

    level = contribution_map.get(date_string, 0)

    x = 30 + week * (CELL_SIZE + GAP)
    y = 50 + day_of_week * (CELL_SIZE + GAP)

    delay = (week + day_of_week) * 0.01

    svg.append(f'''
```

<rect
 class="cell"
 x="{x}"
 y="{y}"
 width="{CELL_SIZE}"
 height="{CELL_SIZE}"
 rx="3"
 fill="{PALETTE[min(level, 4)]}"
 style="animation-delay:{delay}s"
/>
''')

svg.append(''' <text x="30" y="165"
   fill="#8b949e"
   font-family="monospace"
   font-size="12">
Less ▢ ▢ ▢ ▢ ▢ More </text>

</svg>
''')

with open("contrib-heatmap.svg", "w", encoding="utf-8") as file:
    file.write("\n".join(svg))

print("Contribution heatmap SVG created successfully!")
