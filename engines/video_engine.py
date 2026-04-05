"""
Video Walkthrough Engine — Generate plant walkthrough script + storyboard.
Uses AI to create narration script, then guides user to create video
from existing 3D renders using free tools (Canva, CapCut, etc.)
"""
from engines.ai_engine import ask_ai, is_ai_available


def generate_walkthrough_script(cfg, company):
    """AI generates a 60-second narration script for plant walkthrough video."""
    if not is_ai_available():
        return None, "AI not available"

    prompt = f"""Create a professional 60-second video narration script for a virtual plant walkthrough.

Plant Details:
- Type: Bio-Modified Bitumen Plant
- Capacity: {cfg['capacity_tpd']:.0f} MT/Day
- Location: {cfg.get('location', '')}, {cfg.get('state', '')}
- Investment: Rs {cfg['investment_cr']:.2f} Crore
- Client: {cfg.get('client_name', 'Investor')}
- Consultant: {company.get('trade_name', 'PPS Anantams')}

Script format (each section = 1 camera shot):

SHOT 1 (0-10 sec): Aerial establishing shot
[Narration text for this shot]

SHOT 2 (10-20 sec): Raw material receiving area
[Narration text]

SHOT 3 (20-30 sec): Pyrolysis reactor zone
[Narration text]

SHOT 4 (30-40 sec): Bio-oil blending section
[Narration text]

SHOT 5 (40-50 sec): Storage & dispatch area
[Narration text]

SHOT 6 (50-60 sec): Closing with financials
[Narration text mentioning ROI {cfg.get('roi_pct', 20):.1f}% and payback {cfg.get('break_even_months', 30)} months]

Professional investor-grade tone. Each shot narration = 2-3 sentences max."""

    result, provider = ask_ai(prompt, "You are a professional industrial video script writer.", 1500)
    return result, provider


def generate_storyboard(cfg):
    """Generate storyboard matching existing drawings to video shots."""
    capacity = int(cfg['capacity_tpd'])
    storyboard = [
        {"shot": 1, "duration": "0-10 sec", "description": "Aerial view of complete plant",
         "drawing": f"SITE_LAYOUT_{capacity}TPD_Professional.png", "camera": "Drone shot, top-down"},
        {"shot": 2, "duration": "10-20 sec", "description": "Raw material area — biomass receiving",
         "drawing": f"Layout_TopView_{capacity}TPD.png", "camera": "Ground level, left to right pan"},
        {"shot": 3, "duration": "20-30 sec", "description": "Pyrolysis reactor — heart of the plant",
         "drawing": f"PFD_{capacity}TPD.png", "camera": "Close-up of reactor, show temperature"},
        {"shot": 4, "duration": "30-40 sec", "description": "Bio-oil blending with VG-30 bitumen",
         "drawing": f"Machinery_Layout_{capacity}TPD.png", "camera": "Medium shot, show blending tanks"},
        {"shot": 5, "duration": "40-50 sec", "description": "Storage tanks & truck loading",
         "drawing": f"Tank_Farm_{capacity}TPD.png", "camera": "Wide shot of tank farm"},
        {"shot": 6, "duration": "50-60 sec", "description": "Closing — plant overview with data overlay",
         "drawing": f"CAD_Site_Layout_{capacity}TPD.png", "camera": "Pull back to aerial, add text overlay"},
    ]
    return storyboard


def get_video_creation_guide():
    """Return step-by-step guide for creating video from storyboard + drawings."""
    return """
## How to Create Your Plant Walkthrough Video (FREE)

### Method 1: Canva (Easiest — Free Plan Available)
1. Go to canva.com → Create Video
2. Upload all 6 drawings from the storyboard
3. Add each drawing as a slide (10 seconds each)
4. Apply Ken Burns effect (slow zoom/pan) to each
5. Record narration using the AI script above
6. Add background music (Canva has free tracks)
7. Export as MP4

### Method 2: CapCut (Free — Mobile + Desktop)
1. Download CapCut (free)
2. Import all 6 drawings
3. Apply pan/zoom transitions
4. Add text overlays for key metrics
5. Record or paste narration audio
6. Export 1080p MP4

### Method 3: PowerPoint to Video
1. Create 6-slide PPTX (each slide = 1 drawing)
2. Add transitions (Morph works great)
3. Record narration using Slide Show → Record
4. Export as MP4 (File → Export → Video)

### Pro Tip:
Use the AI-generated 3D renders from AI Plant Layouts page
instead of 2D drawings for a more impressive result!
"""
