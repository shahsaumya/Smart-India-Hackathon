import urllib
import http.client
import json
from app.models import OTP 
from django.shortcuts import render_to_response
from app.forms import OTPForm
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files import File
from django.conf import settings
import json
import numpy as np
import pickle
import pandas as pd
import os
import random
import tensorflow as tf
from django.views.decorators.csrf import csrf_protect, csrf_exempt

BASE = os.path.dirname(os.path.abspath(__file__))

tf.set_random_seed(1)
np.random.seed(1)
random.seed(1)

data = list()

with open(os.path.join(BASE, 'Saumitra1' + '.csv')) as f:
    skipped_first_line = False
    for line in f.readlines():
        if not skipped_first_line:
            skipped_first_line = True
            continue
        else:
            line = line.strip().split(',')
            d = [int(float(x)) for x in line[1:]]
            data.append(d)



def otp(request):
		#print(data)
	return render(request,'send_otp.html')


def send_otp(request):
	print(123)
	num = "9867328811"
	conn = http.client.HTTPConnection("2factor.in")
	#OTP.objects.create(number = '9819515144')
	payload = "{}"
	url = "/API/V1/3be6f8b8-1781-11e7-9462-00163ef91450/SMS/"+num+"/323184"
	conn.request("GET", url, payload)
	res = conn.getresponse()
	data = res.read()
	data = str(data,'utf-8')
	data = json.loads(data)
	#objects = OTP.objects.filter(number__icontains = '9819515144')
	#objects[0].session_id= data['Details']
	student=OTP(session_id=data['Details'],otp=323184,number = '9867328811')
	student.save()
	return submit_otp(request)

	#print(objects[0].session_id)
	#print(data)




def submit_otp(request):	
	if request.method=='POST':
		otp_form = OTPForm(request.POST)
		if otp_form.is_valid():
			cd = otp_form.cleaned_data
			if(cd['otp']!='323184'):
				return render(request,'verify_wrong.html')
			else:
				return render(request,'auth.html')		

			#objects = OTP.objects.all()
			#objects[0].otp = cd['otp']
			#print (objects[0].otp)
			



			#return render(request,'submit_otp.html',{'form':otp_form})

	else:
		otp_form = OTPForm()
	return render(request,'verify_otp.html',{'form':otp_form})


def verify_otp(request):
	ob = OTP.objects.all()
	a=ob[0]
	

	'''

	for obj in ob:
		if obj['session_id']!='Request Rejected - Spam Filter':
			a.append(obj)
	print (a )'''
	conn = http.client.HTTPConnection("2factor.in")
	payload = "{}"
	conn.request("GET", "/API/V1/643743b1-1698-11e7-9462-00163ef91450/SMS/VERIFY/"+a.session_id+"/323184", payload)
	res = conn.getresponse()
	data = res.read()	
	print(data.decode("utf-8"))

	return render(request,'auth.html')

def index(request):
	return render(request,'index.html')

def register(request):
	return render(request,'register.html')

def train(request):
	return render(request,'train.html')

def table(request):
	return render(request,'tables_dynamic.html')

def contacts(request):
	return render(request,'contacts.html')

def projects(request):
	return render(request,'projects.html')

def project_detail(request):
	return render(request,'project_detail.html')	

def profile(request):
	return render(request,'profile.html')

def index2(request):
	return render(request,'index2.html')	
	
	
######################### Neural Network #######################

z_dim = 5
batch_size = 10
n_epoch = 100

def xavier_init(size):
    in_dim = size[0]
    xavier_stddev = 1. / tf.sqrt(in_dim / 2.)
    return tf.random_normal(shape=size, stddev=xavier_stddev)


X = tf.placeholder(tf.float32, shape=[None, 24])

D_W1 = tf.Variable(xavier_init([24, 6]))
D_b1 = tf.Variable(tf.zeros(shape=[6]))

D_W2 = tf.Variable(xavier_init([6, 1]))
D_b2 = tf.Variable(tf.zeros(shape=[1]))

theta_D = [D_W1, D_W2, D_b1, D_b2]

Z = tf.placeholder(tf.float32, shape=[None, z_dim])

G_W1 = tf.Variable(xavier_init([z_dim, 6]))
G_b1 = tf.Variable(tf.zeros(shape=[6]))

G_W2 = tf.Variable(xavier_init([6, 24]))
G_b2 = tf.Variable(tf.zeros(shape=[24]))

theta_G = [G_W1, G_W2, G_b1, G_b2]


def sample_Z(m, n):
    return np.random.uniform(-1., 1., size=[m, n])


def generator(z):
    G_h1 = tf.nn.relu(tf.matmul(z, G_W1) + G_b1)
    G_log_prob = tf.matmul(G_h1, G_W2) + G_b2
    G_prob = tf.nn.sigmoid(G_log_prob)

    return G_prob


def discriminator(x):
    D_h1 = tf.nn.relu(tf.matmul(x, D_W1) + D_b1)
    D_logit = tf.matmul(D_h1, D_W2) + D_b2
    D_prob = tf.nn.sigmoid(D_logit)

    return D_prob, D_logit

G_sample = generator(Z)
D_real, D_logit_real = discriminator(X)
D_fake, D_logit_fake = discriminator(G_sample)


D_loss_real = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logit_real, labels=tf.ones_like(D_logit_real)))
D_loss_fake = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logit_fake, labels=tf.zeros_like(D_logit_fake)))
D_loss = D_loss_real + D_loss_fake
G_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logit_fake, labels=tf.ones_like(D_logit_fake)))

D_solver = tf.train.AdamOptimizer().minimize(D_loss, var_list=theta_D)
G_solver = tf.train.AdamOptimizer().minimize(G_loss, var_list=theta_G)

n_batch = len(data) // batch_size
batched_data = np.array_split(data, n_batch)

# Start session
sess = tf.Session()
tf.global_variables_initializer().run(session=sess)

# Epoch-training
for epoch in range(n_epoch):
    err_G = []
    err_D = []

    # Batch training
    for b_idx in range(n_batch):
        x_btch = batched_data[b_idx]
        _, D_loss_curr = sess.run([D_solver, D_loss], feed_dict={X: x_btch, Z: sample_Z(batch_size, z_dim)})
        _, G_loss_curr = sess.run([G_solver, G_loss], feed_dict={Z: sample_Z(batch_size, z_dim)})

        err_D.append(D_loss_curr)
        err_G.append(G_loss_curr)

    print("Epoch %d G:%f  D:%f" % (epoch, np.mean(err_G), np.mean(err_D)))

seq_len = 50
data_1 = []
skipped_first_line = 0
with open(os.path.join(BASE, 'Saumitra2' + '.csv')) as f:
    for line in f.readlines():
        if skipped_first_line < 2:
            skipped_first_line += 1
            continue
        else:
            line = line.strip().split(',')
            d = [int(float(x)) for x in line[1:]]
            data_1.append(d)

splitted_data = []
for i in range(len(data_1) - seq_len):
    splitted_data.append(data_1[i:i + seq_len])

######################### Neural Network #######################

z_dim_1 = 5
batch_size_1 = 40
n_epoch_1 = 2
rnn_neurons_1 = 5

X_1 = tf.placeholder(tf.float32, shape=[None, seq_len, 7])

D_W1_1 = tf.Variable(xavier_init([rnn_neurons_1, 4]))
D_b1_1 = tf.Variable(tf.zeros(shape=[4]))

D_W2_1 = tf.Variable(xavier_init([4, 1]))
D_b2_1 = tf.Variable(tf.zeros(shape=[1]))

theta_D_1 = [D_W1_1, D_W2_1, D_b1_1, D_b2_1]

Z_1 = tf.placeholder(tf.float32, shape=[None, seq_len, z_dim_1])

R_W1_1 = tf.Variable(xavier_init([rnn_neurons_1, 4]))
R_b1_1 = tf.Variable(tf.zeros(shape=[4]))

G_W2_1 = tf.Variable(xavier_init([4, 7]))
G_b2_1 = tf.Variable(tf.zeros(shape=[7]))

theta_G_1 = [R_W1_1, G_W2_1, R_b1_1, G_b2_1]

def sample_Z_1(m, n):
    return np.random.uniform(-1., 1., size=[m, seq_len, n])

with tf.variable_scope('lstm1_1'):
    lstm_1_1 = tf.contrib.rnn.BasicLSTMCell(rnn_neurons_1)
    lstm_op_1_1, _ = tf.nn.dynamic_rnn(lstm_1_1, Z_1, dtype=tf.float32)
    G_h1_1 = tf.map_fn(lambda x: tf.nn.relu(tf.matmul(x, R_W1_1) + R_b1_1), lstm_op_1_1)
    G_sample_1 = tf.map_fn(lambda x: tf.nn.sigmoid(tf.matmul(x, G_W2_1) + G_b2_1), G_h1_1)

with tf.variable_scope('lstm2_1'):
    lstm_2_1 = tf.contrib.rnn.BasicLSTMCell(rnn_neurons_1)
    lstm_op_2_1, _ = tf.nn.dynamic_rnn(lstm_2_1, X_1, dtype=tf.float32)
    D_h1_1 = tf.map_fn(lambda y: tf.nn.relu(tf.matmul(y, D_W1_1) + D_b1_1), lstm_op_2_1)
    D_logit_real_1 = tf.matmul(D_h1_1[-1], D_W2_1) + D_b2_1
    D_real_1 = tf.nn.relu(D_logit_real_1)

with tf.variable_scope('lstm3_1'):
    lstm_op_3_1, _ = tf.nn.dynamic_rnn(lstm_2_1, G_sample_1, dtype=tf.float32)
    D_h1_2_1 = tf.map_fn(lambda y: tf.nn.relu(tf.matmul(y, D_W1_1) + D_b1_1), lstm_op_3_1)
    D_logit_fake_1 = tf.matmul(D_h1_2_1[-1], D_W2_1) + D_b2_1
    D_fake_1 = tf.nn.relu(D_logit_fake_1)

D_loss_real_1 = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logit_real_1, labels=tf.ones_like(D_logit_real_1)))
D_loss_fake_1 = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logit_fake_1, labels=tf.zeros_like(D_logit_fake_1)))
D_loss_1 = D_loss_real_1 + D_loss_fake_1
G_loss_1 = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D_logit_fake_1, labels=tf.ones_like(D_logit_fake_1)))

D_solver_1 = tf.train.AdamOptimizer().minimize(D_loss_1, var_list=theta_D_1)
G_solver_1 = tf.train.AdamOptimizer().minimize(G_loss_1, var_list=theta_G_1)

n_batch_1 = len(splitted_data) // batch_size_1
batched_data_1 = np.array_split(splitted_data, n_batch_1)

# Start session
sess1 = tf.Session()
tf.global_variables_initializer().run(session=sess1)

# Epoch-training
for epoch in range(n_epoch_1):
    err_G_1 = []
    err_D_1 = []

    # Batch training
    for b_idx in range(n_batch_1):
        x_btch_1 = batched_data_1[b_idx]
        _, D_loss_curr_1 = sess1.run([D_solver_1, D_loss_1], feed_dict={X_1: x_btch_1, Z_1: sample_Z_1(batch_size_1, z_dim_1)})
        _, G_loss_curr_1 = sess1.run([G_solver_1, G_loss_1], feed_dict={Z_1: sample_Z_1(batch_size_1, z_dim_1)})

        err_D_1.append(D_loss_curr_1)
        err_G_1.append(G_loss_curr_1)

    print("Epoch %d G:%f  D:%f" % (epoch, np.mean(err_G_1), np.mean(err_D_1)))


def predict(data):
    d_res = sess.run(D_real, feed_dict={X: np.reshape(data, [1, -1])})
    result = d_res[0][0]

    if result < 0.5:
        return False
    else:
        return True

def predict_1(data):
    d_res = sess1.run(D_real_1, feed_dict={X_1: np.reshape(data, [1, seq_len, -1])})
    result = d_res[0][0]

    if result < 0.38:
        return False
    else:
        return True


def predict(data):
    d_res = sess.run(D_real, feed_dict={X: np.reshape(data, [1, -1])})
    result = d_res[0][0]

    if result < 0.5:
        return False
    else:
        return True


# Create your views here.

def login(req):
	return render(req, 'login.html', {"username": "Saumitra"})


def cont_auth(req):
	return render(req, 'auth.html', {"username": "Saumitra"})

@csrf_exempt
def send_details(req):
	username = req.POST['username']
	password = req.POST['password']
	jsonR = req.POST['json']
	wasEntered = not (jsonR == 'nope')
	# Authenticate here
	authenticated = True
	# Authenticate end

	if authenticated and not jsonR == 'nope':
		processedJson = preprocess(jsonR)
		verify_dynamics = check_keyboard_dynamics(username, processedJson)
		if not verify_dynamics:
			return redirect(req, reverse('otp_login'))
		else:
			with open(os.path.join(BASE,  username + '.csv'), 'a+') as f:
				dFile = File(f)
				dFile.write(processedJson)

	return JsonResponse({"authenticated": authenticated, "wasEntered": wasEntered})

# @csrf_protect
@csrf_exempt
def send_login_details(req):
    username = req.POST['username']
    password = req.POST['password']
    jsonR = req.POST['json']
    # Authenticate here
    authenticated = True
    # Authenticate wasEntere
    if authenticated:
        processedJson = preprocessLogin(jsonR)
        print('PROCESSED', processedJson)
        verify = predict(processedJson)
        print('VERIFICATION', verify)

        if not verify:
            authenticated = False

    return JsonResponse({"authenticated": authenticated})


def predict_login(username, processed):
	print('login', processed)
	return True


def check_keyboard_dynamics(username, processed):
	# processed.csv or processed.nparray
	print(processed)
	username = username.strip()
	try:
		with open(os.path.join(BASE, username + '.csv'), 'r') as f:
			ff = File(f)
			processed_data = ff.read()

	except IOError:
		#file doesnt exist
		pass

	return True


def formatForLogin(dataS):
    finS = []
    ind = 0
    for r in dataS:
        curr = 0
        finS.append({})
        for i in r:
            keyVal = i['key'] + '-' +str(curr) + '-'
            finS[ind][keyVal+'kftime'] = i['kftime']
            finS[ind][keyVal+'ftime'] = i['ftime']
            finS[ind][keyVal+'time'] = i['time']
            curr+=1
            
        finS[ind]['totaltime'] = sum([x['time'] for x in r])

        ind += 1
        
    return finS


def formatData(dataS):
    finS = []
    for r in dataS:
        for i in r:
            finS.append(i)

    return finS


def preprocessLogin(dataS):
	finS = formatForLogin(json.loads('[' + dataS[:-1] + ']'))
	dfS = pd.DataFrame(finS)
	dfS.drop('p-0-ftime', axis=1, inplace=True)
	dfS.fillna(dfS.mean(), inplace=True)
	print(dfS.head())
	return dfS.as_matrix().ravel()


def preprocess(dataS):
	finS = formatData(json.loads('[' + dataS[:-1] + ']'))
	dfS = pd.DataFrame(finS)
	dfS.fillna(dfS.mean(), inplace=True)
	return dfS.to_csv(index=False, header=None)

