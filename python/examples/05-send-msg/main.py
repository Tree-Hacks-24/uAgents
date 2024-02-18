from uagents import Agent, Context, Bureau, Model
import json
import requests
import base64

class VerifyMessage(Model):
    img1_base64: str
    img2_base64: str

alice = Agent(name="alice", seed="alice recovery phrase")
bob = Agent(name="bob", seed="bob recovery phrase")

def encode_image_base64(image_path):
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def verify(img1, img2):
    if not img1.startswith('data:image'):
        img1 = f"data:image/jpeg;base64,{img1}"
    if not img2.startswith('data:image'):
        img2 = f"data:image/jpeg;base64,{img2}"
    
    url = 'http://44.200.4.19:5000/verify'
    data = {
        "img1_path": img1,
        "img2_path": img2,
        "model_name": "VGG-Face",
        "detector_backend": "mtcnn",
        "distance_metric": "euclidean"
    }
    json_data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, data=json_data, headers=headers)
        if response.status_code == 200:
            print("Verification successful.")
            print(response.json())  # Assuming JSON response
            return response.json()  # Return the JSON response for further processing if needed
        else:
            print(f"Error in verification: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@alice.on_interval(period=60.0)
async def send_message(ctx: Context):
    # Example usage of converting image files to base64 strings before sending
    # Here you should replace 'path/to/image1.jpg' and 'path/to/image2.jpg' with actual paths
    img1_base64 = encode_image_base64('./img1.jpg')
    img2_base64 = encode_image_base64('./img2.jpg')
    print("Hey Bob, I want you to check if these two faces are the same people.")
    await ctx.send(bob.address, VerifyMessage(img1_base64=img1_base64, img2_base64=img2_base64))

@bob.on_message(model=VerifyMessage)
async def message_handler(ctx: Context, sender: str, msg: VerifyMessage):
    ctx.logger.info(f"Attempting to verify images from {sender}")
    verify_result = verify(msg.img1_base64, msg.img2_base64)
    # Here you can add more logic based on the verification result,
    # e.g., sending a response back or logging the result.
    ctx.logger.info(f"Verification result received: {verify_result}")

bureau = Bureau()
bureau.add(alice)
bureau.add(bob)

if __name__ == "__main__":
    bureau.run()
