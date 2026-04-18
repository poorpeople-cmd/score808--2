from DrissionPage import ChromiumPage, ChromiumOptions
import time
import random
import argparse
import sys
import threading
import os

# ==========================================
# 📸 BACKGROUND SCREENSHOT LOGIC
# ==========================================
keep_taking_screenshots = True

def continuous_screenshots(page):
    """Background thread jo har 2 second mein screenshot lega"""
    folder_name = "screenshots"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    count = 1
    while keep_taking_screenshots:
        try:
            if not page:
                break
            
            # Screenshot save karein
            file_path = f"{folder_name}/shot_{count}.png"
            page.get_screenshot(path=file_path)
            
            count += 1
            time.sleep(2) # Har 2 second baad taake file size limit cross na ho
        except Exception:
            # Agar browser band ho jaye toh error ko ignore kar ke loop break kar do
            break

# ==========================================
# 🚀 MAIN LOGIC
# ==========================================
def main(target_url, drag_distance):
    global keep_taking_screenshots
    keep_taking_screenshots = True
    
    print("🚀 Browser config set kar rahe hain (Puppeteer Style)...")
    
    co = ChromiumOptions()
    # GitHub Actions mein Chrome ka exact path
    co.set_browser_path('/usr/bin/google-chrome')
    
    # ==========================================
    # 🛡️ PROXY SETUP (Tareeqa 2 - Agar WARP fail ho jaye)
    # Agar WARP kaam na kare, toh apni proxy yahan dalein aur shuru se '#' hata dein:
    # co.set_argument('--proxy-server=http://username:password@ip:port')
    # ==========================================
    
    # ⚙️ EXACT PUPPETEER REFERENCE ARGUMENTS
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-setuid-sandbox')
    co.set_argument('--disable-blink-features=AutomationControlled')
    co.set_argument('--mute-audio')
    co.set_argument('--autoplay-policy=no-user-gesture-required')
    
    # Server stability ke liye zaroori (Crash aur Hang rokenge)
    co.set_argument('--disable-dev-shm-usage') 
    co.set_argument('--disable-gpu')
    co.set_argument('--window-size=1280,720')
    
    try:
        print("⏳ Chrome launch ho raha hai...")
        page = ChromiumPage(co)
        page.set.load_mode('none') 
        
        # ---------------------------------------------------------
        # 📸 Start Screenshot Thread (Chrome khulne ke foran baad)
        # ---------------------------------------------------------
        screenshot_thread = threading.Thread(target=continuous_screenshots, args=(page,), daemon=True)
        screenshot_thread.start()
        print("📸 Background Screenshot recording shuru ho gayi hai...")
        # ---------------------------------------------------------
        
        print(f"🌍 Website par ja rahe hain: {target_url}")
        page.get(target_url)

        print("⏳ Page load hone ka 5 seconds wait kar rahe hain...")
        time.sleep(5)

        # ==========================================
        # 🛡️ CLOUDFLARE TURNSTILE BYPASS (Coordinate Click)
        # ==========================================
        click_x = 200  # X axis
        click_y = 348  # Y axis

        print(f"🎯 Cloudflare checkbox par click set kiya: X={click_x}, Y={click_y}")

        # 1. Screen par ek bada Dot draw karna
        js_draw_dot = f"""
        let dot = document.createElement('div');
        dot.style.position = 'fixed';
        dot.style.left = '{click_x}px';
        dot.style.top = '{click_y}px';
        dot.style.width = '30px';
        dot.style.height = '30px';
        dot.style.backgroundColor = 'rgba(255, 0, 0, 0.7)';
        dot.style.border = '3px solid black';
        dot.style.borderRadius = '50%';
        dot.style.zIndex = '999999';
        dot.style.pointerEvents = 'none';
        dot.style.transform = 'translate(-50%, -50%)';
        document.body.appendChild(dot);
        """
        page.run_js(js_draw_dot)
        
        page.get_screenshot(path="screenshots/00_before_click_dot.png")
        print("📸 Click se pehle ka screenshot liya (Dot ke sath).")
        time.sleep(1)

        # 2. Asal Click perform karna
        print("🖱️ Mouse move kar ke CLICK kar rahe hain...")
        page.actions.move_to((click_x, click_y)).click()

        # 3. 10 seconds tak result ke screenshots lena
        print("📸 Click ho gaya! Ab 10 seconds tak verification ka result capture kar rahe hain...")
        for i in range(1, 6): 
            shot_path = f"screenshots/0{i}_after_click_result.png"
            page.get_screenshot(path=shot_path)
            print(f"   -> Result Saved: {shot_path}")
            time.sleep(2) 
            
        print("✅ 10 second ka wait aur capturing puri hui. Ab aage badh rahe hain...")

        # ==========================================
        # 🔄 SMART RETRY LOOP (For Slider puzzle)
        # ==========================================
        attempt_count = 1
        is_solved = False

        while attempt_count <= 5:
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
                print("🎉 BINGO! Slider ya Cloudflare DOM se clear ho gaya hai. Puzzle Solved!")
                is_solved = True
                break 

        # ==========================================
        # 🧠 ADVANCED HYBRID DATA CAPTURE
        # ==========================================
        if is_solved:
            print("\n✅ Video play ho rahi hai. Ab JS ke zariye M3U8 nikal rahe hain...")
            
            js_checker = """
            const entry = window.performance.getEntriesByType("resource").find(r => r.name.includes(".m3u8"));
            if (entry) {
                return {
                    "m3u8_url": entry.name,
                    "referrer": document.referrer,
                    "iframe_url": window.location.href, 
                    "user_agent": navigator.userAgent
                };
            }
            return null;
            """
            
            extracted_data = None
            for i in range(15):
                print(f"📡 Scan #{i+1}: JS Network log check kar raha hai...")
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
                    
                    print("🖥️ AAPKI FFMPEG COMMAND READY HAI:")
                    print(ffmpeg_cmd)
                    print("=====================================================================\n")
                    break
                    
                time.sleep(2) 

            if not extracted_data:
                print("❌ M3U8 link 30 seconds wait karne ke baad bhi nahi mila.")

        else:
            print("\n❌ MISSION FAILED! Puzzle solve nahi hua.")

    except Exception as e:
        print(f"\n🚨 SCRIPT CRASH HO GAYI! Error ki tafseel:\n{e}")

    finally:
        print("🛑 Browser aur Screenshot thread ko band kar rahe hain...")
        # ---------------------------------------------------------
        # 📸 Stop Screenshot Thread Safely
        # ---------------------------------------------------------
        keep_taking_screenshots = False
        time.sleep(2) 
        
        if 'page' in locals() and page:
            page.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="M3U8 Scraper with Slider Captcha Bypass")
    parser.add_argument('--url', type=str, required=True, help="Target stream URL")
    parser.add_argument('--drag', type=int, required=True, help="Slider drag distance in pixels")
    
    args = parser.parse_args()
    main(args.url, args.drag)

















# ============= click done i am not reboot =======================

# from DrissionPage import ChromiumPage, ChromiumOptions
# import time
# import random
# import argparse
# import sys
# import threading
# import os

# # ==========================================
# # 📸 BACKGROUND SCREENSHOT LOGIC
# # ==========================================
# keep_taking_screenshots = True

# def continuous_screenshots(page):
#     """Background thread jo har 2 second mein screenshot lega"""
#     folder_name = "screenshots"
#     if not os.path.exists(folder_name):
#         os.makedirs(folder_name)
        
#     count = 1
#     while keep_taking_screenshots:
#         try:
#             if not page:
#                 break
            
#             # Screenshot save karein
#             file_path = f"{folder_name}/shot_{count}.png"
#             page.get_screenshot(path=file_path)
            
#             count += 1
#             time.sleep(2) # Har 2 second baad taake file size limit cross na ho
#         except Exception:
#             # Agar browser band ho jaye toh error ko ignore kar ke loop break kar do
#             break

# # ==========================================
# # 🚀 MAIN LOGIC
# # ==========================================
# def main(target_url, drag_distance):
#     global keep_taking_screenshots
#     keep_taking_screenshots = True
    
#     print("🚀 Browser config set kar rahe hain (Puppeteer Style)...")
    
#     co = ChromiumOptions()
#     # GitHub Actions mein Chrome ka exact path
#     co.set_browser_path('/usr/bin/google-chrome')
    
#     # ⚙️ EXACT PUPPETEER REFERENCE ARGUMENTS
#     co.set_argument('--no-sandbox')
#     co.set_argument('--disable-setuid-sandbox')
#     co.set_argument('--disable-blink-features=AutomationControlled')
#     co.set_argument('--mute-audio')
#     co.set_argument('--autoplay-policy=no-user-gesture-required')
    
#     # Server stability ke liye zaroori (Crash aur Hang rokenge)
#     co.set_argument('--disable-dev-shm-usage') 
#     co.set_argument('--disable-gpu')
#     co.set_argument('--window-size=1280,720')
    
#     try:
#         print("⏳ Chrome launch ho raha hai...")
#         page = ChromiumPage(co)
#         page.set.load_mode('none') 
        
#         # ---------------------------------------------------------
#         # 📸 Start Screenshot Thread (Chrome khulne ke foran baad)
#         # ---------------------------------------------------------
#         screenshot_thread = threading.Thread(target=continuous_screenshots, args=(page,), daemon=True)
#         screenshot_thread.start()
#         print("📸 Background Screenshot recording shuru ho gayi hai...")
#         # ---------------------------------------------------------
        
#         print(f"🌍 Website par ja rahe hain: {target_url}")
#         page.get(target_url)

#         print("⏳ Page load hone ka 5 seconds wait kar rahe hain...")
#         time.sleep(5)

#         # ==========================================
#         # 🛡️ CLOUDFLARE TURNSTILE BYPASS (Coordinate Click)
#         # ==========================================
#         click_x = 200  # X axis (Aapki requirement ke mutabiq 200 set kiya)
#         click_y = 348  # Y axis (Aapka bataya hua exact spot)

#         print(f"🎯 Cloudflare checkbox par click set kiya: X={click_x}, Y={click_y}")

#         # 1. Screen par ek bada Dot (Chapaa) draw karna taake screenshot mein nazar aaye
#         js_draw_dot = f"""
#         let dot = document.createElement('div');
#         dot.style.position = 'fixed';
#         dot.style.left = '{click_x}px';
#         dot.style.top = '{click_y}px';
#         dot.style.width = '30px';
#         dot.style.height = '30px';
#         dot.style.backgroundColor = 'rgba(255, 0, 0, 0.7)'; // Translucent Red
#         dot.style.border = '3px solid black';
#         dot.style.borderRadius = '50%';
#         dot.style.zIndex = '999999';
#         dot.style.pointerEvents = 'none'; // Taki click dot ke aar-paar guzar jaye
#         dot.style.transform = 'translate(-50%, -50%)'; // Dot ko exact center par align karega
#         document.body.appendChild(dot);
#         """
#         page.run_js(js_draw_dot)
        
#         # Ek screenshot click se pehle lay lo taake dot dekh sakein
#         page.get_screenshot(path="screenshots/00_before_click_dot.png")
#         print("📸 Click se pehle ka screenshot liya (Dot ke sath).")
#         time.sleep(1)

#         # 2. Asal Click perform karna
#         print("🖱️ Mouse move kar ke CLICK kar rahe hain...")
#         page.actions.move_to((click_x, click_y)).click()

#         # 3. Agle 10 seconds tak result ke screenshots lena
#         print("📸 Click ho gaya! Ab 10 seconds tak verification ka result capture kar rahe hain...")
#         for i in range(1, 6): # 5 dafa loop chalega
#             shot_path = f"screenshots/0{i}_after_click_result.png"
#             page.get_screenshot(path=shot_path)
#             print(f"   -> Result Saved: {shot_path}")
#             time.sleep(2) # Har screenshot ke baad 2 second wait (5x2 = 10 seconds)
            
#         print("✅ 10 second ka wait aur capturing puri hui. Ab aage badh rahe hain...")

#         # ==========================================
#         # 🔄 SMART RETRY LOOP (For Slider puzzle agar aa jaye)
#         # ==========================================
#         attempt_count = 1
#         is_solved = False

#         while attempt_count <= 5:
#             print(f"\n🔄 Attempt #{attempt_count} shuru...")
            
#             iframes = page.eles('tag:iframe')
#             slider_btn = None
            
#             for f in iframes:
#                 try:
#                     frame_obj = page.get_frame(f)
#                     btn = frame_obj.ele('.range-btn', timeout=1)
#                     if btn:
#                         slider_btn = btn
#                         break
#                 except:
#                     pass
                    
#             if slider_btn:
#                 print(f"⚠️ Slider mila. Drag start kar rahe hain ({drag_distance}px)...")
                
#                 slider_btn.hover()
#                 time.sleep(random.uniform(0.5, 1.0))
                
#                 print(f"➡️ Dragging {drag_distance}px...")
#                 slider_btn.drag(drag_distance, 0, duration=1.5)
                
#                 print("⏳ Drag complete. Result ke liye 3 seconds wait kar rahe hain...")
#                 time.sleep(3)
#                 attempt_count += 1
#             else:
#                 print("🎉 BINGO! Slider ya Cloudflare DOM se clear ho gaya hai. Puzzle Solved!")
#                 is_solved = True
#                 break 

#         # ==========================================
#         # 🧠 ADVANCED HYBRID DATA CAPTURE
#         # ==========================================
#         if is_solved:
#             print("\n✅ Video play ho rahi hai. Ab JS ke zariye M3U8 nikal rahe hain...")
            
#             js_checker = """
#             const entry = window.performance.getEntriesByType("resource").find(r => r.name.includes(".m3u8"));
#             if (entry) {
#                 return {
#                     "m3u8_url": entry.name,
#                     "referrer": document.referrer,
#                     "iframe_url": window.location.href, 
#                     "user_agent": navigator.userAgent
#                 };
#             }
#             return null;
#             """
            
#             extracted_data = None
#             for i in range(15):
#                 print(f"📡 Scan #{i+1}: JS Network log check kar raha hai...")
#                 extracted_data = page.run_js(js_checker)
                
#                 if not extracted_data:
#                     iframes = page.eles('tag:iframe')
#                     for f in iframes:
#                         try:
#                             frame_obj = page.get_frame(f)
#                             data = frame_obj.run_js(js_checker)
#                             if data:
#                                 extracted_data = data
#                                 break
#                         except:
#                             pass
                
#                 if extracted_data:
#                     m3u8 = extracted_data['m3u8_url']
#                     referer = extracted_data['iframe_url']
#                     ua = extracted_data['user_agent']
                    
#                     ffmpeg_cmd = f'ffmpeg -headers "Referer: {referer}" -user_agent "{ua}" -i "{m3u8}" -c copy live_recording.ts'

#                     print("\n🔥 KAMAAL HO GAYA! Mukammal Data Capture Ho Gaya:")
#                     print("=====================================================================")
#                     print(f"🎬 M3U8 Link  : {m3u8}")
#                     print(f"🔗 Referrer   : {extracted_data['referrer']}")
#                     print(f"📄 Iframe URL : {referer}")
#                     print(f"🕵️ User-Agent : {ua}")
#                     print("=====================================================================\n")
                    
#                     print("🖥️ AAPKI FFMPEG COMMAND READY HAI:")
#                     print(ffmpeg_cmd)
#                     print("=====================================================================\n")
#                     break
                    
#                 time.sleep(2) 

#             if not extracted_data:
#                 print("❌ M3U8 link 30 seconds wait karne ke baad bhi nahi mila.")

#         else:
#             print("\n❌ MISSION FAILED! Puzzle solve nahi hua.")

#     except Exception as e:
#         print(f"\n🚨 SCRIPT CRASH HO GAYI! Error ki tafseel:\n{e}")

#     finally:
#         print("🛑 Browser aur Screenshot thread ko band kar rahe hain...")
#         # ---------------------------------------------------------
#         # 📸 Stop Screenshot Thread Safely
#         # ---------------------------------------------------------
#         keep_taking_screenshots = False
#         time.sleep(2) # Thread ko mukammal rukne ka thoda time dein
        
#         if 'page' in locals() and page:
#             page.quit()

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description="M3U8 Scraper with Slider Captcha Bypass")
#     parser.add_argument('--url', type=str, required=True, help="Target stream URL")
#     parser.add_argument('--drag', type=int, required=True, help="Slider drag distance in pixels")
    
#     args = parser.parse_args()
#     main(args.url, args.drag)


























# ======== 1 screen par dot lagye hai takreebn srf y axis mei thoraa confusion hai x=200 and y=350 ===============

# from DrissionPage import ChromiumPage, ChromiumOptions
# import time
# import os

# def main(target_url):
#     print("🚀 Browser config set kar rahe hain (Mapping Mode)...")
    
#     co = ChromiumOptions()
#     co.set_browser_path('/usr/bin/google-chrome')
    
#     co.set_argument('--no-sandbox')
#     co.set_argument('--disable-setuid-sandbox')
#     co.set_argument('--disable-blink-features=AutomationControlled')
#     co.set_argument('--mute-audio')
#     co.set_argument('--disable-dev-shm-usage') 
#     co.set_argument('--disable-gpu')
#     co.set_argument('--window-size=1280,720')
    
#     try:
#         print("⏳ Chrome launch ho raha hai...")
#         page = ChromiumPage(co)
#         page.set.load_mode('none') 
        
#         # Screenshots folder banana
#         if not os.path.exists("screenshots"):
#             os.makedirs("screenshots")
        
#         print(f"🌍 Website par ja rahe hain: {target_url}")
#         page.get(target_url)

#         print("⏳ Cloudflare Check load hone ka 8 seconds wait kar rahe hain...")
#         time.sleep(8)
        
#         # Original screenshot bina map ke
#         page.get_screenshot(path="screenshots/1_original_screen.png")
#         print("📸 Original screenshot save ho gaya.")

#         # =========================================================
#         # 🗺️ MAGIC TRICK: DRAW FULL SCREEN COORDINATE MAP
#         # =========================================================
#         print("\n🗺️ Poori screen par Coordinates ka jaal (Grid) bicha rahe hain...")
        
#         js_draw_grid = """
#         let step = 80; // Har 80px ke baad nishaan lagega
#         let width = window.innerWidth;
#         let height = window.innerHeight;

#         // Ek transparent overlay banayen
#         let overlay = document.createElement('div');
#         overlay.style.position = 'fixed';
#         overlay.style.top = '0';
#         overlay.style.left = '0';
#         overlay.style.width = '100vw';
#         overlay.style.height = '100vh';
#         overlay.style.pointerEvents = 'none'; // Taake click mein masla na kare
#         overlay.style.zIndex = '999999';
#         document.body.appendChild(overlay);

#         for (let y = 40; y < height; y += step) {
#             for (let x = 40; x < width; x += step) {
#                 // Laal Nuqta (Red Dot)
#                 let dot = document.createElement('div');
#                 dot.style.position = 'absolute';
#                 dot.style.left = x + 'px';
#                 dot.style.top = y + 'px';
#                 dot.style.width = '6px';
#                 dot.style.height = '6px';
#                 dot.style.background = 'red';
#                 dot.style.borderRadius = '50%';
                
#                 // Coordinates Text (Peela Rang)
#                 let label = document.createElement('div');
#                 label.style.position = 'absolute';
#                 label.style.left = (x + 8) + 'px';
#                 label.style.top = (y - 5) + 'px';
#                 label.style.color = 'yellow';
#                 label.style.background = 'rgba(0, 0, 0, 0.8)'; // Black background for visibility
#                 label.style.fontSize = '12px';
#                 label.style.fontFamily = 'monospace';
#                 label.style.padding = '2px 4px';
#                 label.innerText = `${x},${y}`;
                
#                 overlay.appendChild(dot);
#                 overlay.appendChild(label);
#             }
#         }
#         """
#         # Script execute kar ke grid draw karein
#         page.run_js(js_draw_grid)
#         time.sleep(2) # Grid draw hone ka wait

#         # Mapped screenshot save karein
#         map_path = "screenshots/2_coordinate_map.png"
#         page.get_screenshot(path=map_path)
#         print(f"📸 Coordinate Map Screenshot save ho gaya: {map_path}")
        
#         print("\n✅ MISSION ACCOMPLISHED!")
#         print("GitHub Actions se 'screenshots' folder download karein.")
#         print("'2_coordinate_map.png' open karein aur Cloudflare box ke qareeb wala peela number (X,Y) note kar lein.")

#     except Exception as e:
#         print(f"\n🚨 SCRIPT CRASH HO GAYI! Error:\n{e}")

#     finally:
#         print("🛑 Browser band kar rahe hain...")
#         if 'page' in locals() and page:
#             page.quit()

# if __name__ == '__main__':
#     # Test karne ke liye direct target URL yahan daal dein
#     TARGET = "https://www.808fubo15.com/football/2871794-wellington-phoenix-vs-western-sydney.html"
#     main(TARGET)





































































































# ========================================= belwo ===============================









# from DrissionPage import ChromiumPage, ChromiumOptions
# import time
# import random
# import argparse
# import sys
# import threading
# import os

# # ==========================================
# # 📸 BACKGROUND SCREENSHOT LOGIC
# # ==========================================
# keep_taking_screenshots = True

# def continuous_screenshots(page):
#     """Background thread jo har 2 second mein screenshot lega"""
#     folder_name = "screenshots"
#     if not os.path.exists(folder_name):
#         os.makedirs(folder_name)
        
#     count = 1
#     while keep_taking_screenshots:
#         try:
#             if not page:
#                 break
            
#             # Screenshot save karein
#             file_path = f"{folder_name}/shot_{count}.png"
#             page.get_screenshot(path=file_path)
            
#             count += 1
#             time.sleep(2) # Har 2 second baad taake file size limit cross na ho
#         except Exception:
#             # Agar browser band ho jaye toh error ko ignore kar ke loop break kar do
#             break

# # ==========================================
# # 🚀 MAIN LOGIC
# # ==========================================
# def main(target_url, drag_distance):
#     global keep_taking_screenshots
#     keep_taking_screenshots = True
    
#     print("🚀 Browser config set kar rahe hain (Puppeteer Style)...")
    
#     co = ChromiumOptions()
#     # GitHub Actions mein Chrome ka exact path
#     co.set_browser_path('/usr/bin/google-chrome')
    
#     # ⚙️ EXACT PUPPETEER REFERENCE ARGUMENTS
#     co.set_argument('--no-sandbox')
#     co.set_argument('--disable-setuid-sandbox')
#     co.set_argument('--disable-blink-features=AutomationControlled')
#     co.set_argument('--mute-audio')
#     co.set_argument('--autoplay-policy=no-user-gesture-required')
    
#     # Server stability ke liye zaroori (Crash aur Hang rokenge)
#     co.set_argument('--disable-dev-shm-usage') 
#     co.set_argument('--disable-gpu')
#     co.set_argument('--window-size=1280,720')
    
#     try:
#         print("⏳ Chrome launch ho raha hai...")
#         page = ChromiumPage(co)
#         page.set.load_mode('none') 
        
#         # ---------------------------------------------------------
#         # 📸 Start Screenshot Thread (Chrome khulne ke foran baad)
#         # ---------------------------------------------------------
#         screenshot_thread = threading.Thread(target=continuous_screenshots, args=(page,), daemon=True)
#         screenshot_thread.start()
#         print("📸 Background Screenshot recording shuru ho gayi hai...")
#         # ---------------------------------------------------------
        
#         print(f"🌍 Website par ja rahe hain: {target_url}")
#         page.get(target_url)

#         print("⏳ Puzzle load hone ka 5 seconds wait kar rahe hain...")
#         time.sleep(5)

#         # 🔄 SMART RETRY LOOP
#         attempt_count = 1
#         is_solved = False

#         while attempt_count <= 5:
#             print(f"\n🔄 Attempt #{attempt_count} shuru...")
            
#             iframes = page.eles('tag:iframe')
#             slider_btn = None
            
#             for f in iframes:
#                 try:
#                     frame_obj = page.get_frame(f)
#                     btn = frame_obj.ele('.range-btn', timeout=1)
#                     if btn:
#                         slider_btn = btn
#                         break
#                 except:
#                     pass
                    
#             if slider_btn:
#                 print(f"⚠️ Slider mila. Drag start kar rahe hain ({drag_distance}px)...")
                
#                 slider_btn.hover()
#                 time.sleep(random.uniform(0.5, 1.0))
                
#                 print(f"➡️ Dragging {drag_distance}px...")
#                 slider_btn.drag(drag_distance, 0, duration=1.5)
                
#                 print("⏳ Drag complete. Result ke liye 3 seconds wait kar rahe hain...")
#                 time.sleep(3)
#                 attempt_count += 1
#             else:
#                 print("🎉 BINGO! Slider DOM se gayab ho gaya hai. Puzzle Solved!")
#                 is_solved = True
#                 break 

#         # 🧠 ADVANCED HYBRID DATA CAPTURE
#         if is_solved:
#             print("\n✅ Video play ho rahi hai. Ab JS ke zariye M3U8 nikal rahe hain...")
            
#             js_checker = """
#             const entry = window.performance.getEntriesByType("resource").find(r => r.name.includes(".m3u8"));
#             if (entry) {
#                 return {
#                     "m3u8_url": entry.name,
#                     "referrer": document.referrer,
#                     "iframe_url": window.location.href, 
#                     "user_agent": navigator.userAgent
#                 };
#             }
#             return null;
#             """
            
#             extracted_data = None
#             for i in range(15):
#                 print(f"📡 Scan #{i+1}: JS Network log check kar raha hai...")
#                 extracted_data = page.run_js(js_checker)
                
#                 if not extracted_data:
#                     iframes = page.eles('tag:iframe')
#                     for f in iframes:
#                         try:
#                             frame_obj = page.get_frame(f)
#                             data = frame_obj.run_js(js_checker)
#                             if data:
#                                 extracted_data = data
#                                 break
#                         except:
#                             pass
                
#                 if extracted_data:
#                     m3u8 = extracted_data['m3u8_url']
#                     referer = extracted_data['iframe_url']
#                     ua = extracted_data['user_agent']
                    
#                     ffmpeg_cmd = f'ffmpeg -headers "Referer: {referer}" -user_agent "{ua}" -i "{m3u8}" -c copy live_recording.ts'

#                     print("\n🔥 KAMAAL HO GAYA! Mukammal Data Capture Ho Gaya:")
#                     print("=====================================================================")
#                     print(f"🎬 M3U8 Link  : {m3u8}")
#                     print(f"🔗 Referrer   : {extracted_data['referrer']}")
#                     print(f"📄 Iframe URL : {referer}")
#                     print(f"🕵️ User-Agent : {ua}")
#                     print("=====================================================================\n")
                    
#                     print("🖥️ AAPKI FFMPEG COMMAND READY HAI:")
#                     print(ffmpeg_cmd)
#                     print("=====================================================================\n")
#                     break
                    
#                 time.sleep(2) 

#             if not extracted_data:
#                 print("❌ M3U8 link 30 seconds wait karne ke baad bhi nahi mila.")

#         else:
#             print("\n❌ MISSION FAILED! Puzzle solve nahi hua.")

#     except Exception as e:
#         print(f"\n🚨 SCRIPT CRASH HO GAYI! Error ki tafseel:\n{e}")

#     finally:
#         print("🛑 Browser aur Screenshot thread ko band kar rahe hain...")
#         # ---------------------------------------------------------
#         # 📸 Stop Screenshot Thread Safely
#         # ---------------------------------------------------------
#         keep_taking_screenshots = False
#         time.sleep(2) # Thread ko mukammal rukne ka thoda time dein
        
#         if 'page' in locals() and page:
#             page.quit()

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description="M3U8 Scraper with Slider Captcha Bypass")
#     parser.add_argument('--url', type=str, required=True, help="Target stream URL")
#     parser.add_argument('--drag', type=int, required=True, help="Slider drag distance in pixels")
    
#     args = parser.parse_args()
#     main(args.url, args.drag)






























# =========================== i think done and m3u8 link not capture =========================================


# from DrissionPage import ChromiumPage, ChromiumOptions
# import time
# import random
# import argparse
# import sys

# def main(target_url, drag_distance):
#     print("🚀 Browser config set kar rahe hain (Puppeteer Style)...")
    
#     co = ChromiumOptions()
#     # GitHub Actions mein Chrome ka exact path
#     co.set_browser_path('/usr/bin/google-chrome')
    
#     # ==========================================
#     # ⚙️ EXACT PUPPETEER REFERENCE ARGUMENTS
#     # ==========================================
#     co.set_argument('--no-sandbox')
#     co.set_argument('--disable-setuid-sandbox')
#     co.set_argument('--disable-blink-features=AutomationControlled')
#     co.set_argument('--mute-audio')
#     co.set_argument('--autoplay-policy=no-user-gesture-required')
    
#     # Server stability ke liye zaroori (Crash aur Hang rokenge)
#     co.set_argument('--disable-dev-shm-usage') 
#     co.set_argument('--disable-gpu')
#     co.set_argument('--window-size=1280,720')
    
#     try:
#         print("⏳ Chrome launch ho raha hai...")
#         page = ChromiumPage(co)
#         page.set.load_mode('none') 
        
#         print(f"🌍 Website par ja rahe hain: {target_url}")
#         page.get(target_url)

#         print("⏳ Puzzle load hone ka 5 seconds wait kar rahe hain...")
#         time.sleep(5)

#         # ==========================================
#         # 🔄 SMART RETRY LOOP
#         # ==========================================
#         attempt_count = 1
#         is_solved = False

#         while attempt_count <= 5:
#             print(f"\n🔄 Attempt #{attempt_count} shuru...")
            
#             iframes = page.eles('tag:iframe')
#             slider_btn = None
            
#             for f in iframes:
#                 try:
#                     frame_obj = page.get_frame(f)
#                     btn = frame_obj.ele('.range-btn', timeout=1)
#                     if btn:
#                         slider_btn = btn
#                         break
#                 except:
#                     pass
                    
#             if slider_btn:
#                 print(f"⚠️ Slider mila. Drag start kar rahe hain ({drag_distance}px)...")
                
#                 slider_btn.hover()
#                 time.sleep(random.uniform(0.5, 1.0))
                
#                 print(f"➡️ Dragging {drag_distance}px...")
#                 slider_btn.drag(drag_distance, 0, duration=1.5)
                
#                 print("⏳ Drag complete. Result ke liye 3 seconds wait kar rahe hain...")
#                 time.sleep(3)
#                 attempt_count += 1
#             else:
#                 print("🎉 BINGO! Slider DOM se gayab ho gaya hai. Puzzle Solved!")
#                 is_solved = True
#                 break 

#         # ==========================================
#         # 🧠 ADVANCED HYBRID DATA CAPTURE
#         # ==========================================
#         if is_solved:
#             print("\n✅ Video play ho rahi hai. Ab JS ke zariye M3U8 nikal rahe hain...")
            
#             js_checker = """
#             const entry = window.performance.getEntriesByType("resource").find(r => r.name.includes(".m3u8"));
#             if (entry) {
#                 return {
#                     "m3u8_url": entry.name,
#                     "referrer": document.referrer,
#                     "iframe_url": window.location.href, 
#                     "user_agent": navigator.userAgent
#                 };
#             }
#             return null;
#             """
            
#             extracted_data = None
#             for i in range(15):
#                 print(f"📡 Scan #{i+1}: JS Network log check kar raha hai...")
#                 extracted_data = page.run_js(js_checker)
                
#                 if not extracted_data:
#                     iframes = page.eles('tag:iframe')
#                     for f in iframes:
#                         try:
#                             frame_obj = page.get_frame(f)
#                             data = frame_obj.run_js(js_checker)
#                             if data:
#                                 extracted_data = data
#                                 break
#                         except:
#                             pass
                
#                 if extracted_data:
#                     m3u8 = extracted_data['m3u8_url']
#                     referer = extracted_data['iframe_url']
#                     ua = extracted_data['user_agent']
                    
#                     ffmpeg_cmd = f'ffmpeg -headers "Referer: {referer}" -user_agent "{ua}" -i "{m3u8}" -c copy live_recording.ts'

#                     print("\n🔥 KAMAAL HO GAYA! Mukammal Data Capture Ho Gaya:")
#                     print("=====================================================================")
#                     print(f"🎬 M3U8 Link  : {m3u8}")
#                     print(f"🔗 Referrer   : {extracted_data['referrer']}")
#                     print(f"📄 Iframe URL : {referer}")
#                     print(f"🕵️ User-Agent : {ua}")
#                     print("=====================================================================\n")
                    
#                     print("🖥️ AAPKI FFMPEG COMMAND READY HAI:")
#                     print(ffmpeg_cmd)
#                     print("=====================================================================\n")
#                     break
                    
#                 time.sleep(2) 

#             if not extracted_data:
#                 print("❌ M3U8 link 30 seconds wait karne ke baad bhi nahi mila.")

#         else:
#             print("\n❌ MISSION FAILED! Puzzle solve nahi hua.")

#     except Exception as e:
#         print(f"\n🚨 SCRIPT CRASH HO GAYI! Error ki tafseel:\n{e}")

#     finally:
#         print("🛑 Browser ko band kar rahe hain taake agla run theek se ho.")
#         if 'page' in locals():
#             page.quit()

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description="M3U8 Scraper with Slider Captcha Bypass")
#     parser.add_argument('--url', type=str, required=True, help="Target stream URL")
#     parser.add_argument('--drag', type=int, required=True, help="Slider drag distance in pixels")
    
#     args = parser.parse_args()
#     main(args.url, args.drag)
