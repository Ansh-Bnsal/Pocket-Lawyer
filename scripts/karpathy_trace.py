import requests
import json


def karpathy_trace():
    print("=============================================")
    print("🔍 [PHASE 1] THE LOGIN & TOKEN ACQUISITION")
    print("=============================================")
    # Login as an Ansh test user (or register if not exists)
    base_url = "http://127.0.0.1:5000/api"
    
    # Let's try to login with a demo user
    try:
        res = requests.post(f"{base_url}/auth/login", json={"email": "client@demo.com", "password": "password123"})
        if res.status_code != 200:
            print("Login failed, attempting register...")
            res = requests.post(f"{base_url}/auth/register", json={"name": "Test Client", "email": "client@demo.com", "password": "password123", "role": "client"})
        token = res.json().get('token')
        print(f"[X] Authentication Secure. Token: {token[:10]}...")
    except Exception as e:
        print(f"Failed to auth: {e}")
        return

    print("\n=============================================")
    print("🔍 [PHASE 2] THE SSE STREAM (/chat)")
    print("=============================================")
    headers = {"Authorization": f"Bearer {token}"}
    files = {'message': (None, 'I was harassed today')}
    
    pending_promotion = None
    ai_text = ""
    history = [{"role": "user", "content": "I was harassed today"}]

    try:
        response = requests.post(f"{base_url}/chat", headers=headers, files=files, stream=True)
        if response.status_code != 200:
            print(f"[X] Chat failed. HTTP {response.status_code}")
            print(response.text)
            return
            
        print("[X] Stream Connected. Listening to chunks...")
        current_event = "message"
        
        # Manual SSE parser
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('event: '):
                    current_event = decoded_line[7:].strip()
                elif decoded_line.startswith('data: '):
                    payload = decoded_line[6:].strip()
                    if payload and payload != '{}':
                        data = json.loads(payload)
                        if current_event == 'intent':
                            print(f"\n   [INTENT CAPTURED] {data}")
                            if data.get('is_case_worthy'):
                                pending_promotion = data
                                print(f"   --> pendingPromotion Set: {pending_promotion.get('title')}")
                            else:
                                print(f"   --> is_case_worthy evaluates to FALSE or is missing!")
                        elif current_event == 'message':
                            if 'text' in data: ai_text += data['text']
                        elif current_event == 'close':
                            print("\n   [CLOSE THREAD] Stream finished.")
    except Exception as e:
        print(f"Stream error: {e}")
        return

    print("\n=============================================")
    print("🔍 [PHASE 3] THE GHOST-PROMOTION (/chat/promote)")
    print("=============================================")
    if not pending_promotion:
        print("[!] FATAL: pendingPromotion was never set. AI did not flag as case worthy.")
        print('To force it, use explicitly case-worthy text like: "I am being sued in court for breach of contract and need immediate legal representation."')
        return
        
    print("[X] pendingPromotion is VALID. Formulating history array...")
    history.append({"role": "ai", "content": ai_text})
    
    try:
        promo_res = requests.post(f"{base_url}/chat/promote", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, 
                                  json={"title": pending_promotion.get('title', 'Legal Incident'), "history": history})
        if promo_res.status_code in [200, 201]:
            print(f"[X] SUCCESS: Case officially created! {promo_res.json()}")
        else:
            print(f"[!] FAILED TO PROMOTE: HTTP {promo_res.status_code}")
            print(promo_res.text)
    except Exception as e:
        print(f"Promotion error: {e}")

if __name__ == "__main__":
    karpathy_trace()
