from DrissionPage import ChromiumPage, ChromiumOptions
import time
import random
import argparse
import sys

def main(target_url, drag_distance):
    print("🚀 Browser open ho raha hai (Headed Mode for recording)...")
    
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-infobars')
    
    # --- YAHAN CHANGE HAI ---
    # GitHub par record karne ke liye headless mode khatam karna zaroori hai
    # co.set_argument('--headless=new') # <-- Is line ko comment ya delete kar dein
    # ------------------------
    
    co.set_argument('--disable-gpu') # Stability ke liye zaroori hai Virtual display par
    co.set_argument('--window-size=1920,1080')
    
    # Baaki saara code bilkul same rahega jaisa pehle tha...
    # (Pichla code yahan paste karein main function ke andar)
    
    page = ChromiumPage(co)
    page.set.load_mode('none') 
    
    print(f"🌍 Website par ja rahe hain: {target_url}")
    # ... (Rest of your script code) ...
    # Zaroori: Script ke aakhir mein page.quit() lazmi ho.
    page.quit() 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="M3U8 Scraper with Slider Captcha Bypass")
    parser.add_argument('--url', type=str, required=True, help="Target stream URL")
    parser.add_argument('--drag', type=int, required=True, help="Slider drag distance in pixels")
    
    args = parser.parse_args()
    main(args.url, args.drag)
