## Config
import torch
# set up firebase
import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate("./firebase-admin2.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'fashion-diffusion.appspot.com'
})

from diffusers import DiffusionPipeline
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
# pipeline = DiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16)
model_id = "stabilityai/stable-diffusion-2-1-base"
scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
## Testing generating speed
from diffusers import DPMSolverMultistepScheduler
pipeline = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
pipe = pipeline.to("cuda")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

## Setting up web server
from flask_cors import CORS
from flask import request, Response
from flask import Flask
from uuid import uuid4
import io
import datetime
from firebase_admin import storage
import pytz
from firebase_admin import firestore

app = Flask('Testing')
CORS(app)
bucket = storage.bucket()
db = firestore.client()

@app.route('/')
def home():
  return "Hello, World!"

@app.route('/image', methods=["POST", "GET"])
def getImage():

  negative = "out of frame, duplicate, watermark, signature, text, ugly, morbid, mutated, deformed, blurry, bad anatomy, bad proportions, cloned face, disfigured, fused fingers, fused limbs, too many fingers, long neck, twisted face, three legs"
  # return res
  ## get data 
  data = {}
  data["formal"] = request.json["formal"]
  data["gender"] = request.json["gender"]
  data["prompt"] = request.json["prompt"]
  data["publish"] = False
  data["season"] = request.json["season"]
  data["style"] = request.json["style"]
  data["color"] = request.json["color"]
  data["createdDate"] = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
  data["userID"] = request.json["userID"]
  ## create image
  step = 30
  image = pipe(data["prompt"], negative_prompt=negative, num_inference_steps=step).images[0] 
  token = uuid4()
  strToken = str(token)
  metadata = {"firebaseStorageDownloadTokens": token}
  image.save(f"./" + strToken + ".png")
  blob = bucket.blob("/" + strToken +".png")
  blob.metadata = metadata
  with open("./" + strToken + ".png", "rb") as image_file:
    blob.upload_from_file(image_file, content_type="image/png")
  api = blob.generate_signed_url(expiration=datetime.datetime(2024, 1, 20), method='GET', access_token=token)
  print(api)
  data["imageUrl"] = api
  ## Save data to firebase
  db.collection("cloth").add(data)
  res = Response(api)
  return res

app.run(host='0.0.0.0')


