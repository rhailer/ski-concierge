"""
Austrian 1980s style ski illustrations in SVG format
"""

SKIER_ICON = """
<svg width="40" height="40" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <style>
    .ski-line { fill: none; stroke: #2c3e50; stroke-width: 2; stroke-linecap: round; }
    .skier-body { fill: none; stroke: #2c3e50; stroke-width: 2.5; stroke-linecap: round; }
  </style>
  <!-- Skier head -->
  <circle cx="50" cy="20" r="8" class="ski-line"/>
  <!-- Body -->
  <line x1="50" y1="28" x2="50" y2="55" class="skier-body"/>
  <!-- Arms -->
  <line x1="50" y1="35" x2="35" y2="45" class="skier-body"/>
  <line x1="50" y1="35" x2="65" y2="45" class="skier-body"/>
  <!-- Legs -->
  <line x1="50" y1="55" x2="40" y2="75" class="skier-body"/>
  <line x1="50" y1="55" x2="60" y2="75" class="skier-body"/>
  <!-- Skis -->
  <line x1="25" y1="80" x2="55" y2="78" class="ski-line"/>
  <line x1="45" y1="82" x2="75" y2="80" class="ski-line"/>
  <!-- Poles -->
  <line x1="35" y1="45" x2="30" y2="65" class="ski-line"/>
  <line x1="65" y1="45" x2="70" y2="65" class="ski-line"/>
  <circle cx="30" cy="65" r="2" class="ski-line"/>
  <circle cx="70" cy="65" r="2" class="ski-line"/>
</svg>
"""

MOUNTAIN_ICON = """
<svg width="30" height="30" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <path d="M20,80 L35,45 L50,65 L65,35 L80,80 Z" 
        fill="none" stroke="#34495e" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M30,75 L40,55 L50,70 L60,45 L70,75" 
        fill="none" stroke="#7f8c8d" stroke-width="1.5" stroke-linejoin="round"/>
</svg>
"""

MIC_ICON = """
<svg width="24" height="24" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="40" y="20" width="20" height="35" rx="10" 
        fill="none" stroke="#e74c3c" stroke-width="3"/>
  <line x1="50" y1="55" x2="50" y2="75" stroke="#e74c3c" stroke-width="3"/>
  <path d="M30,50 Q30,65 50,65 Q70,65 70,50" 
        fill="none" stroke="#e74c3c" stroke-width="3"/>
  <line x1="40" y1="75" x2="60" y2="75" stroke="#e74c3c" stroke-width="3"/>
</svg>
"""

TERRAIN_ICONS = {
    "all_mountain": """
<svg width="20" height="20" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <path d="M15,75 L30,45 L45,60 L60,35 L75,55 L90,75" 
        fill="none" stroke="#2c3e50" stroke-width="2" stroke-linejoin="round"/>
  <circle cx="40" cy="25" r="8" fill="none" stroke="#f39c12" stroke-width="2"/>
</svg>
""",
    "powder": """
<svg width="20" height="20" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="25" cy="30" r="3" fill="#ecf0f1"/>
  <circle cx="35" cy="25" r="4" fill="#ecf0f1"/>
  <circle cx="45" cy="35" r="3" fill="#ecf0f1"/>
  <circle cx="55" cy="28" r="5" fill="#ecf0f1"/>
  <circle cx="65" cy="40" r="3" fill="#ecf0f1"/>
  <circle cx="75" cy="35" r="4" fill="#ecf0f1"/>
  <path d="M20,60 L40,35 L60,45 L80,30" 
        fill="none" stroke="#2c3e50" stroke-width="2"/>
</svg>
""",
    "carving": """
<svg width="20" height="20" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <path d="M20,75 L80,75" stroke="#2c3e50" stroke-width="3"/>
  <path d="M25,70 Q50,45 75,70" fill="none" stroke="#3498db" stroke-width="2"/>
  <path d="M30,65 Q50,50 70,65" fill="none" stroke="#3498db" stroke-width="2"/>
</svg>
""",
    "park": """
<svg width="20" height="20" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <path d="M20,70 Q35,50 50,70 Q65,50 80,70" 
        fill="none" stroke="#2c3e50" stroke-width="2"/>
  <rect x="45" y="30" width="10" height="20" fill="none" stroke="#e67e22" stroke-width="2"/>
</svg>
"""
}