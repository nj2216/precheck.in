import json
import requests
import time
import threading

THREADS = 10  # Number of threads to use
lock = threading.Lock()

def get_pincode(place, district, state):
    # The API expects only the place name, so we use the address or name field
    url = f"https://api.postalpincode.in/postoffice/{place}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data and data[0]['Status'] == 'Success':
            for post_office in data[0]['PostOffice']:
                # Match district and state for better accuracy
                if (post_office['District'].lower() == district.lower() and
                    post_office['State'].lower() == state.lower()):
                    return post_office['Pincode']
            # Fallback: return first pincode if no exact match
            return data[0]['PostOffice'][0]['Pincode']
    except Exception as e:
        print(f"Error fetching pincode for {place}: {e}")
    return "XXXXXX"

def worker(entries):
    for entry in entries:
        place = entry.get('address') or entry.get('name')
        district = entry.get('city')
        state = entry.get('state')
        pincode = get_pincode(place, district, state)
        with lock:
            entry['postcode'] = pincode
        print(f"{place}, {district}, {state} => {pincode}")
        time.sleep(0.5)  # Be polite to the API

def threaded_update(data):
    chunk_size = (len(data) + THREADS - 1) // THREADS
    threads = []
    for i in range(THREADS):
        chunk = data[i*chunk_size:(i+1)*chunk_size]
        t = threading.Thread(target=worker, args=(chunk,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

with open('phc_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

threaded_update(data)

with open('phc_data_with_pincode.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Updated data saved to phc_data_with_pincode.json")