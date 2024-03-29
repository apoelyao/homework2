import math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# CRR european option
def CRR_european_option_value(S0, K, T, r, sigma, otype, Q, M=4):
    ''' European option valuation.
    Parameters
    ==========
    S0 : float
        stock/index level at time 0
    K : float
        strike price
    T : float
        date of maturity
    r : float
        constant, risk-less short rate
    sigma : float
        volatility
    otype : string
        either 'call' or 'put'
    Q : dividend

    M : int
        number of time intervals
    '''
    # generate binomial tree
    dt = T / M  # length of time interval
    df = math.exp(-r * dt)  # discount per interval

    # calculate the u d p value
    u = math.exp(sigma * math.sqrt(dt))  # up movement
    d = 1 / u  # down movement
    q = (math.exp(r * dt-Q * dt) - d) / (u - d)  # martingale branch probability

    # initialization of the power matrix
    mu = np.arange(M + 1)
    mu = np.resize(mu, (M + 1, M + 1))
    #print(mu)
    md = np.transpose(mu)
    #print(md)
    #print(mu - md)
    mu = u ** (mu - md)
    md = d ** md
    #print(mu)
    #print(md)
    
    #generate the stock price on each node
    S = S0 * mu * md

    # generate the option price on each node
    if otype == 'call':
        V = np.maximum(S - K, 0)  # inner values for European call option
    else:
        V = np.maximum(K - S, 0)  # inner values for European put option

    #use weighted average re-calculate the option price on each node
    for z in range(0, M):  # backwards iteration
        #re-calculate the price column by column,from last step to first
        V[0:M - z, M - z - 1] = (q * V[0:M - z, M - z] +
                         (1 - q) * V[1:M - z + 1, M - z]) * df
    return V,S

# CRR america option
def CRR_american_option_value(S0, K, T, r, sigma, otype, Q, M=4):
    # generate binomial tree
    dt = T / M  # length of time interval
    df = math.exp(-r * dt)  # discount per interval
    inf = math.exp(r * dt)  # discount per interval

    # calculate the value of u d p
    u = math.exp(sigma * math.sqrt(dt))  # up movement
    d = 1 / u  # down movement
    q = (math.exp(r * dt - Q * dt) - d) / (u - d)  # martingale branch probability
    
    # initialization of the power matrix
    mu = np.arange(M + 1)
    mu = np.resize(mu, (M + 1, M + 1))
    md = np.transpose(mu)
    
    mus = u ** (mu - md)
    mds = d ** md
    
    # generate the stock price on each node
    S = S0 * mus * mds 
        
    # calculate the expection price of the stock on each node
    mes = S0 * inf ** mu

    # generate the option value of all leaf nodes
    if otype == 'call':
        V = np.maximum(S - K, 0)     
        #calculate earnings from advance exercise on each node
        oreturn = mes - K
    else:
        V = np.maximum(K - S, 0)       
        #calculate earnings from advance exercise on each node
        oreturn = K - mes

    # compare the weighted average with the advance exercise earning, get value of initial option
    for z in range(0, M):  # backwards iteration
        
        ovalue = (q * V[0:M - z, M - z] +
                         (1 - q) * V[1:M - z + 1, M - z]) * df
        #re-calculate the price column by column,from last step to first
        #option price is the max value
        V[0:M - z, M - z - 1] = np.maximum(ovalue, oreturn[0:M - z, M - z - 1])
        
    return V,S

def calculate_delta(C,S):
    return (C[0,1]- C[1,1])/ (S[0,1] - S[1,1]) #C,S defined as matrices generated while calculating euro option

def calculate_gamma(C,S):
    return (((C[0,2] - C[1,2]) / (S[0,2] - S[1,2])) - \
    ((C[1,2] - C[2,2]) / (S[1,2] - S[2,2]))) / \
    (0.5 * (S[0,2] - S[2,2])) #gamma value formula

def calculate_vega(px_plu_sig,px_min_sig,diff_s):
    return (px_plu_sig - px_min_sig) / (2*diff_s) #vega value formula

def calculate_theta(C,dt):
    return (C[1,2] - C[0,0]) / (2*dt) #theta value formula

def calculate_rho(px_plu_r, px_min_r, diff_rr):
    return (px_plu_r - px_min_r) / (2*diff_rr) #rho value formula

# insert variables
S0 = 100.0  # index level
K = 100.0  # option strike
T = 1.0  # maturity date
r = 0.05  # risk-less short rate
sigma = 0.2  # volatility
M = 4 #int
Q = 0.02 #dividend
dt = T/M #one period time
diff_sigma = 0.001 * sigma #value of sigma change
diff_r = 0.001*r #value of interest rate change

print("america option call price")
C1,S1=CRR_american_option_value(S0,K,T,r,sigma,'call', Q, 4)
print(C1[0,0])

print("america option put price")
C2,S2=CRR_american_option_value(S0,K,T,r,sigma,'put', Q, 4)
print(C2[0,0])

print("european option call price")
C,S=CRR_european_option_value(S0,K,T,r,sigma,'call', Q, 4)
print(C[0,0])

print("european option put price")
C3,S3=CRR_european_option_value(S0,K,T,r,sigma,'put', Q, 4)
print(C3[0,0])

print("delta value")
print(calculate_delta(C,S)) #delta value calculate base on european option call, so as other greek value
print("gamma value")
print(calculate_gamma(C,S))
print("theta value")
print(calculate_theta(C,dt))

C_max_sigma,S_max_sigma=CRR_american_option_value(S0,K,T,r,sigma+diff_sigma,'call',Q,4) #define C(sigma+delta sigma)
C_min_sigma,S_min_sigma=CRR_american_option_value(S0,K,T,r,sigma-diff_sigma,'call',Q,4) #define C(sigma-delta sigma)

C_max_r,S_max_r=CRR_european_option_value(S0,K,T,r+diff_r,sigma,'call',Q,4) #define C(r+delta r)
C_min_r,S_min_r=CRR_european_option_value(S0,K,T,r-diff_r,sigma,'call',Q,4) #define C(r-delta r)


print("vega value")
print(calculate_vega(C_max_sigma[0,0],C_min_sigma[0,0],dt))
print("rho value")
print(calculate_rho(C_max_r[0,0],C_min_r[0,0],dt))
