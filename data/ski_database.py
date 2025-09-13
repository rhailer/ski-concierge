"""
Comprehensive ski database with current models, prices, and retailer links
"""

SKI_DATABASE = {
    "all_mountain": {
        "beginner": [
            {
                "name": "Rossignol Experience 80 CI",
                "price_range": "$400-500",
                "description": "Perfect for beginners with confidence-inspiring stability and easy turn initiation.",
                "retailers": {
                    "REI": "https://www.rei.com/product/rossignol-experience-80-ci",
                    "Backcountry": "https://www.backcountry.com/rossignol-experience-80-ci-ski",
                    "Evo": "https://www.evo.com/skis/rossignol-experience-80-ci"
                },
                "specs": {"length": "150-180cm", "waist": "80mm", "radius": "14-18m"}
            },
            {
                "name": "Salomon XDR 80 Ti",
                "price_range": "$450-550",
                "description": "Excellent progression ski with titanal reinforcement for stability at higher speeds.",
                "retailers": {
                    "Salomon": "https://www.salomon.com/en-us/shop/product/xdr-80-ti.html",
                    "REI": "https://www.rei.com/product/salomon-xdr-80-ti",
                    "Christy Sports": "https://www.christysports.com/salomon-xdr-80-ti"
                },
                "specs": {"length": "155-185cm", "waist": "80mm", "radius": "15-19m"}
            }
        ],
        "intermediate": [
            {
                "name": "Völkl Deacon 79",
                "price_range": "$600-700",
                "description": "Precise carving ski with excellent edge hold and responsive handling for progressing intermediates.",
                "retailers": {
                    "Völkl": "https://www.volkl.com/us/skis/deacon-79",
                    "Powder7": "https://www.powder7.com/Volkl-Deacon-79-Skis",
                    "Backcountry": "https://www.backcountry.com/volkl-deacon-79-ski"
                },
                "specs": {"length": "156-184cm", "waist": "79mm", "radius": "13.4-17.7m"}
            },
            {
                "name": "Head Kore 85",
                "price_range": "$550-650",
                "description": "Lightweight and versatile with excellent performance on groomed runs and light powder.",
                "retailers": {
                    "Head": "https://www.head.com/en/skis/kore-85",
                    "REI": "https://www.rei.com/product/head-kore-85",
                    "Evo": "https://www.evo.com/skis/head-kore-85"
                },
                "specs": {"length": "149-184cm", "waist": "85mm", "radius": "15-19m"}
            }
        ],
        "advanced": [
            {
                "name": "Dynastar M-Pro 90",
                "price_range": "$700-800",
                "description": "Race-inspired all-mountain ski with titanal construction for expert-level performance.",
                "retailers": {
                    "Dynastar": "https://www.dynastar.com/us/m-pro-90",
                    "Powder7": "https://www.powder7.com/Dynastar-M-Pro-90-Skis",
                    "Backcountry": "https://www.backcountry.com/dynastar-m-pro-90-ski"
                },
                "specs": {"length": "158-186cm", "waist": "90mm", "radius": "16-20m"}
            }
        ]
    },
    "powder": {
        "intermediate": [
            {
                "name": "Blizzard Black Pearl 97",
                "price_range": "$650-750",
                "description": "Female-specific powder ski with excellent float and stability in deep snow.",
                "retailers": {
                    "Blizzard": "https://www.blizzard-ski.com/us/black-pearl-97",
                    "REI": "https://www.rei.com/product/blizzard-black-pearl-97",
                    "Backcountry": "https://www.backcountry.com/blizzard-black-pearl-97-ski"
                },
                "specs": {"length": "152-180cm", "waist": "97mm", "radius": "15-19m"}
            }
        ],
        "advanced": [
            {
                "name": "DPS Wailer 106",
                "price_range": "$900-1100",
                "description": "Premium powder ski with carbon fiber construction for ultimate performance in deep snow.",
                "retailers": {
                    "DPS": "https://www.dpsskis.com/products/wailer-a106-c2",
                    "Powder7": "https://www.powder7.com/DPS-Wailer-106-Skis",
                    "Backcountry": "https://www.backcountry.com/dps-wailer-106-ski"
                },
                "specs": {"length": "160-194cm", "waist": "106mm", "radius": "18-25m"}
            }
        ]
    },
    "carving": {
        "intermediate": [
            {
                "name": "Rossignol Hero Athlete GS",
                "price_range": "$550-650",
                "description": "Race-inspired carving ski perfect for aggressive groomed run skiing.",
                "retailers": {
                    "Rossignol": "https://www.rossignol.com/us/hero-athlete-gs",
                    "REI": "https://www.rei.com/product/rossignol-hero-athlete-gs",
                    "Christy Sports": "https://www.christysports.com/rossignol-hero-athlete-gs"
                },
                "specs": {"length": "156-188cm", "waist": "68mm", "radius": "17-23m"}
            }
        ]
    }
}

def get_ski_recommendations(skill_level, terrain_preference, budget_range=None, gender=None):
    """
    Get ski recommendations based on user preferences
    """
    recommendations = []
    
    # Match terrain preference
    terrain_key = None
    if "powder" in terrain_preference.lower() or "deep" in terrain_preference.lower():
        terrain_key = "powder"
    elif "carving" in terrain_preference.lower() or "groomed" in terrain_preference.lower():
        terrain_key = "carving"
    else:
        terrain_key = "all_mountain"
    
    # Get skis for terrain and skill level
    if terrain_key in SKI_DATABASE and skill_level in SKI_DATABASE[terrain_key]:
        recommendations.extend(SKI_DATABASE[terrain_key][skill_level])
    
    # If specific terrain doesn't have options, fall back to all-mountain
    if not recommendations and skill_level in SKI_DATABASE["all_mountain"]:
        recommendations.extend(SKI_DATABASE["all_mountain"][skill_level])
    
    return recommendations[:3]  # Return top 3 recommendations