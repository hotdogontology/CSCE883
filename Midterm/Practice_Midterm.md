# CSCE 883 practice midterm

**100 points • suggested 120 minutes • one single-sided page of notes.** This is an original study exam based on HW1–3 and lectures 1–9, with varied numbers and inputs. The suggested time is not the professor's announced exam duration. No code writing is required. Show derivations and intermediate arithmetic; report nonexact numerical results to three decimals. Use natural logs for likelihood/loss and base-2 logs for entropy. Calculator use here is optional; actual exam calculator rules were not supplied.

Do not open `Practice_Midterm_Answers.md` until finished. Suggested pacing: Q1–3 35 minutes, Q4–6 45 minutes, Q7–9 30 minutes, review 10 minutes.

## Q1. Naive Bayes and unequal error costs — 10 points

*HW1 Q3 variation; lectures 2–3.* Classify a Red, Domestic, SUV using these training counts. There are 8 Yes and 12 No cases. Each feature is binary (Red/Yellow, Domestic/Imported, SUV/Sports).

| Count within class | Yes | No |
|---|---:|---:|
| Red | 6 | 3 |
| Domestic | 2 | 9 |
| SUV | 4 | 8 |

a. State the NB assumption and compute priors, three conditionals per class, and both unsmoothed posterior scores. Predict the class under 0/1 loss. (6)

b. Normalize the scores to obtain P(Yes|x). False-positive cost is 1 and false-negative cost is 4, with zero correct-class cost. Compute each action's conditional risk and choose the minimum-risk action. (3)

c. If the Yes SUV count were zero, what would its Laplace-smoothed conditional probability be? (1)

## Q2. MLE derivations — 14 points

*HW2 Q1–4 variations; lecture 4.*

a. X takes values 0,1,2,3 with probabilities $2\theta/3,\theta/3,2(1-\theta)/3,(1-\theta)/3$, respectively, where $0\le\theta\le1$. Observed counts are $(n_0,n_1,n_2,n_3)=(3,3,1,1)$. Write the likelihood, log likelihood, derivative, MLE, and a maximum check. (6)

b. For independent observations with $f(x|b)=(2b)^{-1}e^{-|x|/b}$, b>0, derive the MLE and evaluate it for −2, 0, 1, 5. (3)

c. For Gaussian observations 1, 2, 3, derive the MLE mean and variance using log-likelihood derivatives. Explain why the variance denominator is 3 rather than 2. (3)

d. For independent Poisson observations 0, 1, 3, 4, use the log likelihood to obtain the rate MLE. You may start from $P(x|\lambda)=\lambda^xe^{-\lambda}/x!$. (2)

## Q3. Gaussian neural regression and metrics — 12 points

*HW2 Q5/Q8 and HW3 Q5 variations.*

a. A network predicts mean $\mu_i$ and log variance $s_i=\log\sigma_i^2$. Derive the Gaussian negative log likelihood for independent pairs $(x_i,y_i)$, including the constant. Explain the purpose of the log-variance term and when this becomes MSE minimization. (4)

b. Confusion matrix rows are true class, columns predicted class, both ordered [0,1]:

| | Predicted 0 | Predicted 1 |
|---|---:|---:|
| True 0 | 30 | 10 |
| True 1 | 5 | 55 |

Treat **class 0 as positive**, as in HW2 Q8. Find TP/FP/TN/FN, accuracy, class-0 precision/recall/F1, and macro-F1. (5)

c. Explain why ROC/AUC should use scores and which probability column to select for class 0. (1)

d. Targets are [1,2,3], predictions [2,2,2]. Compute MAE, RMSE, and R². Explain what a negative R² on another model would mean. (2)

## Q4. Decision-tree calculation and forest interpretation — 10 points

*HW2 Q7 variation plus Q6.* An eight-example binary dataset has four positive and four negative labels. Candidate A has two branches: A=0 contains (3 positive,1 negative), A=1 contains (1 positive,3 negative). Candidate B has two branches: B=0 contains (2 positive,0 negative), B=1 contains (2 positive,4 negative).

a. Compute parent entropy, each candidate's weighted child entropy and information gain; choose the root. You may use $H(3/4)=0.8113$ and $H(1/3)=0.9183$. (6)

b. An ID feature uniquely identifies every training row. Explain why its apparent information gain is misleading. What should happen at a leaf with conflicting labels and no remaining informative features? (2)

c. Contrast an RF with a cascade forest. Why should training probability features supplied to later cascade layers be out-of-fold predictions? (2)

## Q5. Hand convolution, pooling, and CNN sizes — 14 points

*Your explicit classroom warning; HW3 Q1B variation; lecture 7.* Use NN cross-correlation: **do not flip the kernel**. Input has one channel, stride 1, padding 0, and bias b=1:

$$X=\begin{bmatrix}1&2&0\\0&1&3\\2&1&0\end{bmatrix},\qquad K=\begin{bmatrix}1&-1\\0&2\end{bmatrix}.$$

a. Calculate all four output entries, showing the multiplication for each. Apply ReLU, then 2×2 max pooling with stride 2. (6)

b. A different architecture takes input $2×8×8$, applies Conv2D with 3 output channels, 3×3 kernels, stride 1, no padding, one bias per output channel; then 2×2 max pooling, stride 2; flatten; and a dense layer with 4 outputs and biases. Give every output shape, convolution weights/biases per filter and total parameters, pooling parameters, flatten length, dense parameters, and network total. (6)

c. Explain local connectivity and weight sharing. For multi-channel input, does each output filter see one input channel or all input channels under groups=1? (2)

## Q6. Backpropagation and gradient propagation — 16 points

*HW3 Q1A/Q2 variations; lectures 6–7.* Let $h_1=\phi(w_1x)$, $h_2=\phi(w_2x)$, $z=w_3h_1+w_4h_2$, $p=\sigma(z)$, and $L=-y\log p-(1-y)\log(1-p)$. There are no biases.

a. Derive $\partial L/\partial z$ and all four weight gradients for sigmoid hidden units. Show chain-rule factors and the gradient-descent update rule. How would the output delta change if the loss were $\frac12(p-y)^2$? (6)

b. Use x=1, y=1, $w_1=w_2=0$, $w_3=1$, $w_4=-1$, sigmoid hidden units, and learning rate 0.1. Calculate h1, h2, z, p, all gradients, and all simultaneous updated weights. (4)

c. Replace the hidden activation by $\phi_k(u)=\log(1+e^{2ku})/(2k)$. Derive its derivative, state the replacement factors in the hidden-weight gradients, and explain the limit as k increases. Can ReLU backpropagate at zero? (2)

d. For $h_l=\sigma(w_lh_{l-1})$ with $|w_l|\le1$, derive a depth-L upper bound on $|\partial h_L/\partial x|$. Give the Jacobian of $h_{l+1}=h_l+F_l(h_l)$. Why do neither small sigmoid derivatives alone nor residual connections establish universal training guarantees? (3)

e. Why might using epsilon=$10^{-12}$ instead of $10^{-5}$ make a central finite-difference gradient check worse? (1)

## Q7. Explain existing code and audit evaluation — 10 points

*HW1 Q1/Q5; HW3 Q3.* Explain the following code; propose corrections **in words**, without writing replacement code.

```python
train = np.loadtxt("train.csv", delimiter=",")
test = np.loadtxt("test.csv", delimiter=",")
scaler.fit(np.vstack([train, test]))
train_x, test_x = scaler.transform(train), scaler.transform(test)
train_y, test_y = train[:, -1], test[:, -1]
dist = np.sum(train_x - test_x[0], axis=1)
idx = np.argsort(dist)[:4]
prediction = np.bincount(train_y[idx].astype(int)).argmax()
```

a. Identify three substantive correctness/evaluation problems. Explain what each affected operation does and the correction. (6)

b. What does the final line do on a tie, and how does that differ from the HW1 tie policy? (1)

c. A researcher tries 20 network architectures and reports the highest test R², repeating five times. Explain the selection bias; give a valid train/validation/test sequence. If rows share a material identity and deployment concerns new materials, how should the split change? (3)

## Q8. Explain a four-line diffusion loss — 8 points

*Your classroom example; lecture 9.* Here x0 is a batch of clean images, t is a sampled timestep per image, and a is $\bar\alpha_t$, already reshaped for broadcasting:

```python
noise = torch.randn_like(x0)
xt = a.sqrt() * x0 + (1 - a).sqrt() * noise
pred_noise = model(xt, t)
loss = ((pred_noise - noise) ** 2).mean()
```

a. Interpret every line. Identify the model inputs, prediction target, loss, and quantities that are learned versus fixed. Explain why t is supplied. (4)

b. A single-element example has a=0.64, x0=2, noise=−1, pred_noise=0.5. Calculate xt, loss, and $\partial loss/\partial pred\_noise$. Recover the clean estimate using the predicted noise. (2)

c. Contrast this training method with generation from a diffusion model, and contrast diffusion with a vanilla GAN. (2)

## Q9. Architecture and experiment concepts — 6 points

*Lectures 6–8; AI-assisted HW3 Q4–5.* Answer briefly.

a. What does an RNN remember, how are its weights shared, and how do LSTM forget/input/output gates regulate its cell? (2)

b. In DNA classification, a frequency logistic-regression model is unchanged by within-sequence shuffling, but a frozen CNN loses accuracy. What is supported, what is not established, and what would retraining on shuffled sequences test? (2)

c. Explain GAN mode collapse and a non-saturating generator loss. Contrast a denoising autoencoder's target with the epsilon-prediction diffusion target. (2)

---

**Optional extra rehearsal (unscored):** Explain dropout at training/evaluation; negative test R² versus a training-mean baseline; why lower training MSE with greater MLP depth need not improve test performance; why `backward()` and `optimizer.step()` are separate; why analytic/autodiff/finite-difference checks are complementary.
