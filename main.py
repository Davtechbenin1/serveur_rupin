#Coding:utf-8
"""
	Gestion des données du logiciel
"""
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import HTTPException
from fastapi.responses import FileResponse, StreamingResponse

import uvicorn

from ws_manager import ConnectionManager
import logging,sys,os

import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
import boto3
from botocore.client import Config
import botocore
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size = 500)

ws_manager = ConnectionManager()

# -----------------------
# CONFIGURATION B2
# -----------------------
B2_KEY_ID = "005fbf4bbd072e40000000001"
B2_APP_KEY = "K005Tshmfa1XAq6Ej2eA6YWY8WgfAgY"
B2_BUCKET_NAME = "nanabinze"
B2_ENDPOINT = "https://s3.us-east-005.backblazeb2.com"

S3 = boto3.resource(
	"s3",endpoint_url = B2_ENDPOINT,
	aws_access_key_id=B2_KEY_ID,
	aws_secret_access_key=B2_APP_KEY,
	config=Config(signature_version="s3v4")
)
bucket = S3.Bucket(B2_BUCKET_NAME)
# -----------------------
# ROUTE UPLOAD
# -----------------------
@app.post("/api/upload")
async def upload_file(file:UploadFile = File(...)):
	try:
		content = await file.read()
		bucket.put_object(Key=file.filename, Body = content,
			ContentType=file.content_type)
		return {"filename":file.filename, "message":"OK"}
	except botocore.exceptions.EndpointConnectionError:
		return {"filename":"media/logo.png", "message":"ERROR"}

# -----------------------
# ROUTE DOWNLOAD
# -----------------------
@app.get("/api/download/{filename}")
async def download_file(filename: str):
	#try:
	obj = bucket.Object(filename)
	response = obj.get()
	
	return StreamingResponse(
		response["Body"],
		media_type=response["ContentType"]
	)
	#except botocore.exceptions.EndpointConnectionError:
	#	return "Connexion error"

@app.put("/api/select/{ent_name}")
async def get_direct_data(ent_name:str,request:Request):
	data = await request.json()
	data = json.loads(data)
	ent_name = data.get('base_name')
	where = data.get('where')
	id = data.get('id')
	date = data.get('date')
	if isinstance(where,(list,tuple)):
		base_table = list()
		for part in where:
			th_p = await ws_manager.th_base_hand.set_my_where(
				ent_name,part)
			base_table.append(th_p)
	else:
		base_table = await ws_manager.th_base_hand.set_my_where(
			ent_name,where)
	dic = await ws_manager.th_base_hand.get_data(base_table, date, id)
	return dic

# Gestion du web socket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await ws_manager.connect(websocket)
	try:
		while True:
			raw = await websocket.receive_text()
			result = await ws_manager.handle_message(
				websocket,raw)
	except WebSocketDisconnect:
		await ws_manager.disconnect(websocket)
	except RuntimeError:
		await ws_manager.disconnect(websocket)

logging.basicConfig(
	format = "%(levelname)s: %(message)s",
	level = logging.INFO
)
#'''
if __name__ == "__main__":

	host = "localhost"
	port = 8010
	inf_dic = {"host":host,'port':port,"user":"postgres",
		"pass_word":'davtechbenin',"postgres_host":"localhost",
		"postgres_port":"5432"}
	
	uvicorn.run(app,port = port,host = host,reload = False,
		log_level = "info")
	#"""
#'''
