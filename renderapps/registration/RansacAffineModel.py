
import ransac
from numpy import vstack
import cv2
import numpy as np

class RansacAffineModel(object):

	def __init__(self,debug=False):
		self.debug = debug

	def fit(self,data):
		data = data.T
		#print("This is data shape")
		#print(data)
		fp = data[:2,:]
		tp = data[2:,:]
		fp = fp.T.astype(np.float32)
		tp = tp.T.astype(np.float32)
		return cv2.estimateRigidTransform(fp, tp,True)
	def transformAffine(self, fp,A):
		fp = fp.T
		fp = np.vstack((fp,np.ones(fp.shape[1])))
		newfp = np.dot(A,fp)
		return newfp.T

	def get_error(self,data,A):
		if A is None:
			A = np.array([[1.0, 0.0, 0.0],[0.0,1.0,0.0]])
		data = data.T
		fp = data[:2,:]
		tp = data[2:,:]
		fp = fp.T.astype(np.float32)
		tp = tp.T.astype(np.float32)
		#print(fp.shape)
		#print(tp.shape)
		#print(A)
		#print(A.shape)
		#print ("This is A: ")
		#print(A)
		#print("This is squrt")

		fp_transformed = self.transformAffine(fp,A)

		return np.sqrt(sum((tp.T-fp_transformed.T))**2)

	def A_from_ransac(r,fp,tp,model,maxiter=5000,match_threshold=5):

		data = vstack((fp,tp))
		A,ransac_data = ransac.ransac(data.T,model,3,maxiter,match_threshold,0,debug=False,return_all=True)
		return A,ransac_data['inliers']
