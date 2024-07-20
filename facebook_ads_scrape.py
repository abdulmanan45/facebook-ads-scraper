import time
import random
from multiprocessing.pool import ThreadPool
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, ElementNotInteractableException, ElementNotVisibleException, ElementNotSelectableException


# List of advertiser IDs
# adv_ids = ['188186581192773', '227098687156852', '543755195637715'] 
# adv_ids = ['160454767141274', '647369422130557', '109114801600782']
            #jazz           #telenor        #onic              #jazzcash            #zong         #nayatel          #ufone
# adv_ids = ['109706490881', '113127139019', '106098912537249', '304153223024822', '199939918311', '169618516422633', '111665325705']
adv_ids = ['109706490881', '113127139019', '188186581192773', '304153223024822', '199939918311', '169618516422633', '111665325705']

# Dictionary to store platform styles so we can identify them later
platform_styles = {'facebook': 'width: 12px; height: 12px; mask-image: url("https://static.xx.fbcdn.net/rsrc.php/v3/yA/r/galtHrQ0mV-.png"); mask-position: -34px -335px;',
             'instagram': 'width: 12px; height: 12px; mask-image: url("https://static.xx.fbcdn.net/rsrc.php/v3/y7/r/RBY2XQNTT-A.png"); mask-position: -14px -545px;',
             'messenger': 'width: 12px; height: 12px; mask-image: url("https://static.xx.fbcdn.net/rsrc.php/v3/yA/r/galtHrQ0mV-.png"); mask-position: -47px -335px;',
             'audience_network': 'width: 12px; height: 12px; mask-image: url("https://static.xx.fbcdn.net/rsrc.php/v3/yA/r/galtHrQ0mV-.png"); mask-position: -106px -186px;'}

# Function to perform the scraping for a single adv_id
def scrape_ads(adv_id):

    # Parameters for the search
    min_date = ''#'2024-07-02'
    max_date = ''

    url = f'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=PK&view_all_page_id={adv_id}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&start_date[min]={min_date}&start_date[max]={max_date}&search_type=page&media_type=all'

    # Setup WebDriver
    options = webdriver.ChromeOptions()
    #options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
    #options.add_argument('--uder-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')    

    driver = webdriver.Chrome(options=options)
    driver.get(url)


    # Initialize DataFrame
    columns = ['library_id', 'activity_status', 'start_date', 'facebook', 'instagram', 'messenger', 'audience_network', 'amount_spent(PKR)', 'impressions','links', 'video',]
    ads_df = pd.DataFrame(columns=columns)

    def extract_platforms(platforms_str):
        platforms = [0, 0, 0, 0]
        platforms_str = platforms_str.split(' | ')

        # Find whether each platform is present in the platforms_str through style attribute
        if platform_styles['facebook'] in platforms_str:
            platforms[0] = 1
        if platform_styles['instagram'] in platforms_str:
            platforms[1] = 1
        if platform_styles['messenger'] in platforms_str:
            platforms[2] = 1
        if platform_styles['audience_network'] in platforms_str:
            platforms[3] = 1

        return platforms

    # Function to extract details from an element
    def extract_ad_details(ad_type):
        ad_data = []
        # Extract ad details based on the type of ad button clicked
        if ad_type == 'summary details':
            try:    
                # Extract platform fields from each ad 
                ads_platforms = [] 
                fields = driver.execute_script("""
                                    return document.querySelectorAll("div.xrvj5dj.x18m771g.x1amjocr.xkj13zw.xvg9xk2.x1jr1mh3 > div > div > div.x1cy8zhl.x78zum5.xyamay9.x1pi30zi.x18d9i69.x1swvt13.x1n2onr6 > div > div.x78zum5.xdt5ytf.x2lwn1j.xeuugli > div:nth-child(4) > div");
                """)
                count=0

                # Extract platform styles in each platform field
                for field in fields:
                    platforms = []
                    styles = field.find_elements(By.CLASS_NAME, 'xtwfq29')

                    
                    for style in styles:
                        platform = style.get_attribute("style")

                        #convert platform to string and append to platforms list (each ad has multiple platforms)
                        platforms.append(str(platform))

                    #convert platforms list to string platform
                    platform = ' | '.join(platforms)
                    # Append platform to ads_platforms list (for each ad different platforms may be appended)
                    ads_platforms.append(platform)
                    count+=1

                # Extract other details of each ad
                elements = driver.execute_script("""
                        return document.querySelectorAll("div.xrvj5dj.x18m771g.x1amjocr.xkj13zw.xvg9xk2.x1jr1mh3 > div > div > div.x78zum5.xyamay9.x1pi30zi.x18d9i69.x1swvt13.x1n2onr6");
                """)
                for element in elements:
                    ad_data.append(element.text)
                

            except NoSuchElementException as e:
                print(f"Error extracting details: {e}")
                return None
            
        # do the same for ad details
        elif ad_type == 'ad details':
            try:
                # Extract platform styles from ad details (as there is only one ad, only one platform style list is returned)
                platforms = []
                styles = driver.execute_script("""
                        return document.querySelectorAll("body > div > div.x1dr59a3.xixxii4.x13vifvy.x17qophe.xn9wirt.xbqvh2t.x1c8ul09.xofcydl.xxziih7.x12w9bfk.x19991ni.x1hc1fzr > div.x1qjc9v5.x9f619.x78zum5.xdt5ytf.x1nhvcw1.xg6iff7.xurb0ha.x1sxyh0.x1l90r2v > div > div > div > div > div.x9f619.x78zum5.x1iyjqo2.x5yr21d.x2lwn1j.x1n2onr6.xh8yej3 > div.xw2csxc.x1odjw0f.xwib8y2.xh8yej3 > div.x8bgqxi.x78zum5.x5yr21d.xl56j7k > div > div:nth-child(2) > div > div > div.x78zum5.xdt5ytf.x2lwn1j.xeuugli > div:nth-child(4) > div > div > div > div > div > div > div ");
                """)

                if len(styles) == 0:
                    print('No platform found')

                for style in styles:
                    platform = style.get_attribute("style")
                    #convert platform to string and append to platforms list
                    platforms.append(str(platform))

                #convert platforms list to string platform
                platform = ' | '.join(platforms)

                element = driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div[2]/div/div[2]/div/div/div[1]')
                # Append ad details to ad_data list
                ad_data.append(element.text + "\n" + platform)

            except NoSuchElementException as e:
                print(f"Error extracting details: {e}")
                return None
        
        # Return ad data and platforms list if summary details are extracted
        if ad_type == 'summary details':
            return ad_data, ads_platforms
        # Return ad data if ad details are extracted (platforms are returned as a string at the end of the ad details)
        else:
            return ad_data

    # Function to extract all links from an ad element
    def extract_all_links(ad_type):
        links = []
        if ad_type == 'summary details':
            try:
                link_elements = driver.execute_script("""
                    return document.querySelectorAll("div.xrvj5dj.x18m771g.x1amjocr.xkj13zw.xvg9xk2.x1jr1mh3 > div > div > div.xh8yej3 > div > div > div.x6ikm8r.x10wlt62 a");
                """)
                for link in link_elements:
                    links.append(link.get_attribute("href"))
            
            except NoSuchElementException as e:
                print(f"Error extracting links: {e}")
                return None
            
        elif ad_type == 'ad details':
            try:
                link_elements = driver.execute_script("""
                                            
                    return document.querySelector("div.x178xt8z.xm81vs4.xso031l.xy80clv.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x15bcfbt.xolcy6v.x3ckiwt.xc2dlm9.x2izyaf.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.x1t2gpz5.x9f619.x6ikm8r.x10wlt62.x1n2onr6 > div > div.x6ikm8r.x10wlt62 a ");  """)

                if link_elements:
                    links.append(link_elements.get_attribute("href"))

            except NoSuchElementException as e:
                print(f"Error extracting links: {e}")
                return None
            
        return links

    # Function to extract video or image URLs
    def extract_video(ad_type):
        videos = []
        if ad_type == 'summary details':
            try:
                elements = driver.execute_script("""  
                    return document.querySelectorAll("div.xrvj5dj.x18m771g.x1amjocr.xkj13zw.xvg9xk2.x1jr1mh3 > div > div > div.xh8yej3 > div > div > div.x6ikm8r.x10wlt62 > div.x14ju556.x1n2onr6 > div > div > div > div > div > div > video");
                """)
                
                # If no videos found, extract images
                if len(elements) == 0:
                    elements = driver.execute_script("""  
                            return document.querySelectorAll("div.xrvj5dj.x18m771g.x1amjocr.xkj13zw.xvg9xk2.x1jr1mh3 > div > div > div.xh8yej3 > div > div > div._23n- > div > div > div > div > div > div > a > div.x1ywc1zp.x78zum5.xl56j7k.x1e56ztr.x1277o0a > img, div.xrvj5dj.x18m771g.x1amjocr.xkj13zw.xvg9xk2.x1jr1mh3 > div > div > div.xh8yej3 > div > div > div.x6ikm8r.x10wlt62 > a > div.x1ywc1zp.x78zum5.xl56j7k.x1e56ztr.x1277o0a > img, div.xrvj5dj.x18m771g.x1amjocr.xkj13zw.xvg9xk2.x1jr1mh3 > div > div > div.xh8yej3 > div > div > div.x6ikm8r.x10wlt62 > div.x1ywc1zp.x78zum5.xl56j7k.x1e56ztr.x1277o0a > img");
                    """)
                    for element in elements:
                        img = element.get_attribute("src")
                        videos.append(img)
                else:
                    for element in elements:
                        video = element.get_attribute("src")
                        videos.append(video)
            
            except NoSuchElementException as e:
                print(f"Error extracting video: {e}")
                return None
        elif ad_type == 'ad details':
            try:
                # Check for video first
                video = driver.find_element(By.XPATH, '/html/body/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/video')
                videos.append(video.get_attribute("src"))
            except (ElementNotSelectableException, ElementNotInteractableException, ElementNotVisibleException, NoSuchElementException) as e:
                print(f"Error extracting video: {e}")

                try:
                    # Check for image if no video found
                    img = driver.find_element(By.CSS_SELECTOR, 'body > div > div.x1dr59a3.xixxii4.x13vifvy.x17qophe.xn9wirt.xbqvh2t.x1c8ul09.xofcydl.xxziih7.x12w9bfk.x19991ni.x1hc1fzr > div.x1qjc9v5.x9f619.x78zum5.xdt5ytf.x1nhvcw1.xg6iff7.xurb0ha.x1sxyh0.x1l90r2v > div > div > div > div > div.x9f619.x78zum5.x1iyjqo2.x5yr21d.x2lwn1j.x1n2onr6.xh8yej3 > div.xw2csxc.x1odjw0f.xwib8y2.xh8yej3 > div.x8bgqxi.x78zum5.x5yr21d.xl56j7k > div > div > div > div > div.x178xt8z.xm81vs4.xso031l.xy80clv.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x15bcfbt.xolcy6v.x3ckiwt.xc2dlm9.x2izyaf.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.x1t2gpz5.x9f619.x6ikm8r.x10wlt62.x1n2onr6 > div._7jyg._7jyi > div.x6ikm8r.x10wlt62 img')
                    videos.append(img.get_attribute("src"))

                except NoSuchElementException as e:
                   print(f"No image or video found: {e}")
            
        return videos


        

    # Main loop to interact with ads and store data
    try:
        time.sleep(random.uniform(2, 10))                            # random intial sleep
        # Wait for the page to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll to the bottom of the page to load more ads
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(10, 14))

            # Break the loop if the page height doesn't change after scrolling i.e all ads are loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Wait for the ad buttons to load
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "See ad details") or contains(text(), "See summary details")]')))
        # Find all ad buttons
        ad_buttons = driver.find_elements(By.XPATH, '//div[contains(text(), "See ad details") or contains(text(), "See summary details")]')
        print(f'Found {len(ad_buttons)} ad buttons')

        for i, ad_button in enumerate(ad_buttons):
            retries = 3
            while retries > 0:
                try:
                    # Scroll to the ad button and click it
                    driver.execute_script("arguments[0].scrollIntoViewIfNeeded();", ad_button)
                    time.sleep(random.uniform(2, 3))
                    driver.execute_script("arguments[0].click();", ad_button)
                    time.sleep(random.uniform(3, 5))

                    # Extract ad details, links, and video
                    if "summary details" in ad_button.text.lower():
                        ad_details, ads_platform  = extract_ad_details('summary details')
                        links = extract_all_links('summary details')
                        videos = extract_video('summary details')
                        if len(links) == 0:
                            links = None
                        else:
                            links = ' | '.join(links)

                        # Add data to DataFrame
                        for j, details in enumerate(ad_details):
                            row_index = len(ads_df)

                            if videos:
                                video_url = videos[j] if j < len(videos) else None  # Match each ad with a video
                            
                            else:
                                video_url = None

                            if not details:
                                ads_df.loc[row_index] = {
                                    'library_id': None,
                                    'activity_status': None,
                                    'start_date': None,
                                    'facebook' : None,
                                    'instagram' : None,
                                    'messenger' : None,
                                    'amount_spent(PKR)': None,
                                    'impressions': None,
                                    'links': None,
                                    'video': None

                                }
                            else:
                                details_split = details.split('\n')
                                # Extract platforms from the respective string in ads_platform for each ad
                                platforms_arr = extract_platforms(ads_platform[j])
                                
                                ads_df.loc[row_index] = {
                                    'library_id': '\'' + details_split[0].split(': ')[1] if len(details_split) > 0 else None,
                                    'activity_status': details_split[1] if len(details_split) > 1 else None,
                                    'start_date': details_split[2] if len(details_split) > 2 else None,
                                    'facebook' : platforms_arr[0],
                                    'instagram' : platforms_arr[1],
                                    'messenger' : platforms_arr[2],
                                    'audience_network' : platforms_arr[3],
                                    'amount_spent(PKR)': details_split[8] if len(details_split) > 7 else None,
                                    'impressions': details_split[10] if len(details_split) > 9 else None,
                                    'links': links,
                                    'video': video_url
                                }


                    elif "ad details" in ad_button.text.lower():
                        ad_details = extract_ad_details('ad details')
                        links = extract_all_links('ad details')
                        videos = extract_video('ad details')
                        row_index = len(ads_df)
                        video_url = videos[0] if videos else None

                        if links:
                            links = links[0] if len(links) > 0 else None

                        if not ad_details:
                            ads_df.loc[row_index] = {
                                'library_id' : None,
                                'activity_status' : None,
                                'start_date' : None,
                                'facebook' : None,
                                'instagram' : None,
                                'messenger' : None,
                                'audience_network' : None,
                                'amount_spent(PKR)' : None,
                                'impressions' : None
                            }
                        else:
                            details_split = ad_details[0].split('\n')
                            # Extract platforms from the last string in details_split (from style attribute of the platform icons)
                            platforms_arr = extract_platforms(details_split[-1])
                            ads_df.loc[row_index] = {
                                'library_id': '\'' + details_split[0].split(': ')[1] if len(details_split) > 0 else None,
                                'activity_status': details_split[1] if len(details_split) > 1 else None,
                                'start_date': details_split[2] if len(details_split) > 2 else None,
                                'facebook' : platforms_arr[0],
                                'instagram' : platforms_arr[1],
                                'messenger' : platforms_arr[2],
                                'audience_network' : platforms_arr[3],
                                'amount_spent(PKR)': details_split[8] if len(details_split) > 7 else None,
                                'impressions': details_split[10] if len(details_split) > 9 else None,
                                'links': links,
                                'video': video_url
                            }


                    close_button = driver.find_element(By.XPATH, '//div[contains(text(), "Close")]')
                    driver.execute_script("arguments[0].click();", close_button)
                    time.sleep(random.uniform(2, 4))

                    break

                except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
                    print(f'Error interacting with ad: {e}')
                    retries -= 1                                                                                          #reduce retries by 1
                    # if multiple errors occur, skip the ad
                    if retries == 0:
                        print('Skipping this ad due to repeated errors.')
                    continue

                except ElementClickInterceptedException:
                    # Remove overlay if it exists
                    try:
                        overlay = driver.find_element(By.CSS_SELECTOR, 'div[class*="overlay"]')
                        driver.execute_script("arguments[0].style.display='none';", overlay)
                        print('Overlay removed.')
                    except NoSuchElementException:
                        print('No overlay found to remove.')
                    retries -= 1
                    if retries == 0:
                        print('Skipping this ad due to repeated click interception.')
                    continue

    finally:
        driver.quit()
        print(ads_df)
        date_of_scrape = time.strftime("%Y-%m-%d")
        time_of_scrape = time.strftime("%H-%M-%S")
        ads_df.to_csv(f'preprocessed/{adv_id}_{date_of_scrape}_{time_of_scrape}.csv', index=False)

#use pool of threads to scrape ads for each advertiser ID
pool = ThreadPool(processes=4)
pool.map(scrape_ads, adv_ids)
pool.close()
pool.join()

print("Scraping completed.")
