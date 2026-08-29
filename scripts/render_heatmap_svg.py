import json
from datetime import datetime, timedelta

def main():
    # Load contribution data
    with open("data/contributions.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    days = data.get("days", [])
    username = data.get("username", "AdityaRunwal")

    # SVG Layout constants
    CELL_SIZE = 10
    GAP = 3
    STEP = CELL_SIZE + GAP  # 13px per cell+gap
    WEEKS = 53

    OFFSET_X = 40
    OFFSET_Y = 55

    WIDTH = 840
    HEIGHT = 195

    PALETTE = [
        "#161b22",  # Level 0
        "#0e4429",  # Level 1
        "#006d32",  # Level 2
        "#26a641",  # Level 3
        "#39d353"   # Level 4
    ]

    # Convert contribution data into dictionary
    contribution_map = {
        day["date"]: day.get("level", 0)
        for day in days
    }

    # Find starting Sunday (52 weeks ago from current week's Sunday)
    if days:
        # Determine latest date in dataset or today
        latest_date_str = max(d["date"] for d in days)
        anchor_date = datetime.strptime(latest_date_str, "%Y-%m-%d").date()
    else:
        anchor_date = datetime.today().date()

    # Calculate Sunday of anchor week
    sunday_of_anchor_week = anchor_date - timedelta(days=(anchor_date.weekday() + 1) % 7)
    start_date = sunday_of_anchor_week - timedelta(weeks=WEEKS - 1)

    svg = []

    # SVG Header
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
    svg.append('<style>')
    svg.append('  .header-text { font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, monospace; font-size: 14px; font-weight: 600; fill: #c9d1d9; }')
    svg.append('  .prompt-user { fill: #58a6ff; }')
    svg.append('  .label-text { font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, monospace; font-size: 10px; fill: #8b949e; }')
    svg.append('  .cell { rx: 2px; ry: 2px; transition: stroke 0.15s ease; }')
    svg.append('  .cell:hover { stroke: #ffffff; stroke-width: 1px; }')
    svg.append('</style>')

    # Background card
    svg.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1"/>')

    # Title / Command prompt header
    svg.append(f'<text x="20" y="30" class="header-text">')
    svg.append(f'  <tspan class="prompt-user">{username}</tspan>')
    svg.append(f'  <tspan fill="#8b949e">@github</tspan>')
    svg.append(f'  <tspan fill="#79c0ff"> ~ $</tspan>')
    svg.append(f'  <tspan fill="#d2a8ff"> ./contributions.sh</tspan>')
    svg.append(f'</text>')

    # Day of week labels (Mon, Wed, Fri)
    day_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for day_idx, label in day_labels.items():
        ly = OFFSET_Y + day_idx * STEP + 9
        svg.append(f'<text x="12" y="{ly}" class="label-text">{label}</text>')

    # Track month labels to display above columns
    last_month = None
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Render grid cells
    for week in range(WEEKS):
        week_start_date = start_date + timedelta(weeks=week)
        
        # Month label logic: display when month changes and column has space
        current_month = week_start_date.month
        if current_month != last_month:
            last_month = current_month
            mx = OFFSET_X + week * STEP
            svg.append(f'<text x="{mx}" y="{OFFSET_Y - 8}" class="label-text">{month_names[current_month - 1]}</text>')

        for day_of_week in range(7):
            current_date = week_start_date + timedelta(days=day_of_week)
            date_string = current_date.isoformat()

            level = contribution_map.get(date_string, 0)
            color = PALETTE[min(max(level, 0), 4)]

            x = OFFSET_X + week * STEP
            y = OFFSET_Y + day_of_week * STEP

            svg.append(f'<rect class="cell" x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}"><title>{date_string}: level {level}</title></rect>')

    # Legend at bottom
    legend_y = OFFSET_Y + 7 * STEP + 18
    legend_x = OFFSET_X

    svg.append(f'<text x="{legend_x}" y="{legend_y + 9}" class="label-text">Less</text>')
    
    rect_start_x = legend_x + 32
    for idx, color in enumerate(PALETTE):
        rx = rect_start_x + idx * (CELL_SIZE + GAP)
        svg.append(f'<rect class="cell" x="{rx}" y="{legend_y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}"/>')

    more_x = rect_start_x + len(PALETTE) * (CELL_SIZE + GAP) + 6
    svg.append(f'<text x="{more_x}" y="{legend_y + 9}" class="label-text">More</text>')

    svg.append('</svg>')

    # Write SVG file
    output_content = "\n".join(svg) + "\n"
    with open("contrib-heatmap.svg", "w", encoding="utf-8") as file:
        file.write(output_content)

    print("Contribution heatmap SVG generated successfully!")

if __name__ == "__main__":
    main()

