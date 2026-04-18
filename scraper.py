from DrissionPage import ChromiumPage, ChromiumOptions
import time
import random
import argparse
import sys

def main(target_url, drag_distance):
    print("🚀 Browser open ho raha hai (Headless Mode)...")
    
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-infobars')
    co.set_argument('--headless=new') # GitHub Actions ke liye zaroori hai
    co.set_argument('--disable-gpu')
    co.set_argument('--window-size=1920,1080')
    
    page = ChromiumPage(co)
    page.set.load_mode('none') 
    
    print(f"🌍 Website par ja rahe hain: {target_url}")
    page.get(target_url)

    print("⏳ Puzzle load hone ka 5 seconds wait kar rahe hain...")
    time.sleep(5)

    # ==========================================
    # 🔄 SMART RETRY LOOP (Max 5 attempts for safety)
    # ==========================================
    attempt_count = 1
    is_solved = False

    while attempt_count <= 5: # Action minutes bachane ke liye max 5 limits
        print(f"\n🔄 Attempt #{attempt_count} shuru...")
        
        iframes = page.eles('tag:iframe')
        slider_btn = None
        
        for f in iframes:
            try:
                frame_obj = page.get_frame(f)
                btn = frame_obj.ele('.range-btn', timeout=1)
                if btn:
                    slider_btn = btn
                    break
            except:
                pass
                
        if slider_btn:
            print(f"⚠️ Slider mila. Drag start kar rahe hain ({drag_distance}px)...")
            
            slider_btn.hover()
            time.sleep(random.uniform(0.5, 1.0))
            
            print(f"➡️ Dragging {drag_distance}px...")
            slider_btn.drag(drag_distance, 0, duration=1.5)
            
            print("⏳ Drag complete. Result ke liye 3 seconds wait kar rahe hain...")
            time.sleep(3)
            attempt_count += 1
        else:
            print("🎉 BINGO! Slider DOM se gayab ho gaya hai. Puzzle Solved!")
            is_solved = True
            break 

    # ==========================================
    # 🧠 ADVANCED HYBRID DATA CAPTURE & FFMPEG GEN
    # ==========================================
    if is_solved:
        print("\n✅ Video play ho rahi hai. Ab JS ke zariye M3U8 aur extra data nikal rahe hain...")
        
        js_checker = """
        const entry = window.performance.getEntriesByType("resource").find(r => r.name.includes(".m3u8"));
        if (entry) {
            return {
                "m3u8_url": entry.name,
                "referrer": document.referrer,
                "iframe_url": window.location.href, 
                "user_agent": navigator.userAgent,
                "host": window.location.hostname
            };
        }
        return null;
        """
        
        extracted_data = None
        
        for i in range(15):
            print(f"📡 Scan #{i+1}: JS Network log aur Headers check kar raha hai...")
            extracted_data = page.run_js(js_checker)
            
            if not extracted_data:
                iframes = page.eles('tag:iframe')
                for f in iframes:
                    try:
                        frame_obj = page.get_frame(f)
                        data = frame_obj.run_js(js_checker)
                        if data:
                            extracted_data = data
                            break
                    except:
                        pass
            
            if extracted_data:
                m3u8 = extracted_data['m3u8_url']
                referer = extracted_data['iframe_url']
                ua = extracted_data['user_agent']
                
                ffmpeg_cmd = f'ffmpeg -headers "Referer: {referer}" -user_agent "{ua}" -i "{m3u8}" -c copy live_recording.ts'

                print("\n🔥 KAMAAL HO GAYA! Mukammal Data Capture Ho Gaya:")
                print("=====================================================================")
                print(f"🎬 M3U8 Link  : {m3u8}")
                print(f"🔗 Referrer   : {extracted_data['referrer']}")
                print(f"📄 Iframe URL : {referer}")
                print(f"🕵️ User-Agent : {ua}")
                print("=====================================================================\n")
                
                print("🖥️ AAPKI FFMPEG COMMAND READY HAI (Copy kar ke CMD mein paste karein):")
                print("👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇")
                print(ffmpeg_cmd)
                print("👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆\n")
                break
                
            time.sleep(2) 

        if not extracted_data:
            print("❌ M3U8 link 30 seconds wait karne ke baad bhi nahi mila.")

    else:
        print("\n❌ MISSION FAILED! Puzzle solve nahi hua (Attempts finished).")

    print("🛑 Script ka kaam mukammal ho gaya hai.")
    page.quit() # GitHub Actions mein memory leak bachane ke liye page close zaroori hai

if __name__ == '__main__':
    # CLI Arguments setup karna taake GitHub Actions se data le sakein
    parser = argparse.ArgumentParser(description="M3U8 Scraper with Slider Captcha Bypass")
    parser.add_argument('--url', type=str, required=True, help="Target stream URL")
    parser.add_argument('--drag', type=int, required=True, help="Slider drag distance in pixels")
    
    args = parser.parse_args()
    main(args.url, args.drag)
