#NOTE: Deep sort needs the format `top_left_x, top_left_y, width,height

from libraries.deep_sort import nn_matching
from libraries.deep_sort.tracker import Tracker 
from libraries.application_util import preprocessing as prep
from libraries.application_util import visualization
from libraries.deep_sort.detection import Detection

import numpy as np

import matplotlib.pyplot as plt

import torch
import torchvision
from scipy.stats import multivariate_normal

class deepsort_rbc():
	def __init__(self,wt_path=None):
		#loading this encoder is slow, should be done only once.
		#self.encoder = generate_detections.create_box_encoder("deep_sort/resources/networks/mars-small128.ckpt-68577")		
		self.encoder = torch.load('ckpts\model640.pt',map_location=torch.device('cpu'))			
			
		#self.encoder = self.encoder.cuda()
		self.encoder = self.encoder.eval()
		print("Deep sort model loaded from path: ", wt_path)

		self.metric = nn_matching.NearestNeighborDistanceMetric("cosine",.5 , 100)
		self.tracker= Tracker(self.metric)

		self.transforms = torchvision.transforms.Compose([ \
				torchvision.transforms.ToPILImage(),\
				torchvision.transforms.Resize((128,128)),\
				torchvision.transforms.ToTensor()])

	def reset_tracker(self):
		self.tracker= Tracker(self.metric)


	def pre_process(self,frame,detections):	

		transforms = torchvision.transforms.Compose([ \
			torchvision.transforms.ToPILImage(),\
			torchvision.transforms.Resize((128,128)),\
			torchvision.transforms.ToTensor()])
			
		crops = []
		for d in detections:

			for i in range(len(d)):
				if d[i] <0:
					d[i] = 0	

			img_h,img_w,img_ch = frame.shape

			xmin,ymin,w,h = d

			if xmin > img_w:
				xmin = img_w

			if ymin > img_h:
				ymin = img_h

			xmax = xmin + w
			ymax = ymin + h

			ymin = abs(int(ymin))
			ymax = abs(int(ymax))
			xmin = abs(int(xmin))
			xmax = abs(int(xmax))

			try:
				crop = frame[ymin:ymax,xmin:xmax,:]
				crop = transforms(crop)
				crops.append(crop)
			except:
				continue
		if len(crops):
			crops = torch.stack(crops)
		return crops

	def extract_features_only(self,frame,coords):

		for i in range(len(coords)):
			if coords[i] <0:
				coords[i] = 0	


		img_h,img_w,_ = frame.shape
				
		xmin,ymin,w,h = coords

		if xmin > img_w:
			xmin = img_w

		if ymin > img_h:
			ymin = img_h

		xmax = xmin + w
		ymax = ymin + h

		ymin = abs(int(ymin))
		ymax = abs(int(ymax))
		xmin = abs(int(xmin))
		xmax = abs(int(xmax))
		
		crop = frame[ymin:ymax,xmin:xmax,:]
		#crop = crop.astype(np.uint8)

		#print(crop.shape,[xmin,ymin,xmax,ymax],frame.shape)

		crop = self.transforms(crop)
		crop = crop.cpu()

		
		#input_ = crop * 1
		input_ = torch.unsqueeze(crop,0)

		features = self.encoder.forward_once(input_)
		features = features.detach().cpu().numpy()

		corrected_crop = [xmin,ymin,xmax,ymax]

		return features,corrected_crop


	def run_deep_sort(self, frame, out_scores, out_boxes):

		if len(out_boxes) == 0:			
			self.tracker.predict()
			print('No detections')
			trackers = self.tracker.tracks
			return trackers, []

		detections = np.array(out_boxes)
		#features = self.encoder(frame, detections.copy())
		try:
			processed_crops = self.pre_process(frame,detections).cpu()
			processed_crops = 1 * processed_crops

			features = self.encoder.forward_once(processed_crops)
			features = features.detach().cpu().numpy()

			if len(features.shape)==1:
				features = np.expand_dims(features,0)


			dets = [Detection(bbox, score, feature) \
						for bbox,score, feature in\
					zip(detections,out_scores, features)]

			outboxes = np.array([d.tlwh for d in dets])

			outscores = np.array([d.confidence for d in dets])
			indices = prep.non_max_suppression(outboxes, 0.8,outscores)
			
			dets = [dets[i] for i in indices]

			self.tracker.predict()
			self.tracker.update(dets)	
		except:
			dets = []
		return self.tracker,dets



