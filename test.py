import requests
import time

url = "https://super-fast-object-detection.p.rapidapi.com/detect"

headers = {
    "x-rapidapi-host": "super-fast-object-detection.p.rapidapi.com",
    "x-rapidapi-key": "e5894aae1bmsh56f932fdebc726dp11fec1jsn6f2ebad3f61c"
}


total_time = 0
success_count = 0
failure_count = 0

image_path = "/home/tamnv/Downloads/car.jpg"
for i in range(100):
    try:
        with open(image_path, "rb") as f:
            files = {"image": f}
            start_time = time.time()
            response = requests.post(url, headers=headers, files=files)
            end_time = time.time()

            if response.status_code == 200:
                success_count += 1
            else:
                failure_count += 1

            elapsed_time = end_time - start_time
            total_time += elapsed_time

            print(f"Request {i+1}: Status {response.status_code}, Time {elapsed_time:.2f}s")

            # Optional: print the response content
            # print(response.text)
            time.sleep(1)

    except Exception as e:
        print(f"Request {i+1}: Failed - {str(e)}")
        failure_count += 1

    # Optional: add a small delay between requests to avoid overwhelming the API
    time.sleep(0.1)

average_time = total_time / 100
print(f"\nResults:")
print(f"Total requests: 100")
print(f"Successful requests: {success_count}")
print(f"Failed requests: {failure_count}")
print(f"Average time per request: {average_time:.2f}s")