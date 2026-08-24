# Results

Three frozen encoders, three datasets, four targets. Every model went through the same procedure. The backbone is frozen, an attentive probe is trained on top for 20 epochs across a six point hyperparameter grid, and the best probe on validation is what gets reported. That protocol comes from the EchoJEPA paper and I did not change any of it, so my numbers can be compared against theirs directly.

Logged MAE from the eval code is scaled by target_std because of the issue described in notes/known_issues.md. Everything below has already been divided.

## Whether the pipeline works

| Model | Validation | Test | Published |
|---|---|---|---|
| PanEcho | 5.094 | 5.393 | 5.10 |
| EchoPrime | 5.066 | 5.077 | 4.87 |
| EchoJEPA-L | 4.928 | 5.259 | 5.76 |

All on EchoNet-Dynamic LVEF in EF points. Every model lands close to what its authors reported, and EchoJEPA-L comes in better than published on validation. This is the only cell here with an external reference, so it is what makes the rest worth reading.

## PanEcho on EchoNet-Dynamic, EF

Data was 7465 train, 1288 validation, 1277 test. A4C only, one video per study, natively 112 by 112.

Validation MAE 5.094 at epoch 16, test 5.393, R squared 0.622. Published for this cell is 5.10.

Zero-shot gives 6.448 with R squared 0.434 and a bias of +4.21. So the trained probe beats PanEcho's own supervised head by about one MAE point and lifts R squared from 0.43 to 0.62.

That +4.21 bias is worth a note. PanEcho's EF training mean is 59.0 and EchoNet-Dynamic's is 55.78, a gap of 3.2, so the bias looks like a distribution difference between what the model saw during training and what it sees here. I checked whether it is a pure offset by subtracting it and recomputing, and MAE only fell from 6.448 to 6.015. So it is not a calibration shift you could fix with a constant. The model compresses toward the middle as well as reading high.

That compression shows up directly in the scatter plot. Predictions cluster around 60 to 65 no matter what the truth is, and severe dysfunction gets under called, roughly 30 predicted where the truth is 15. Clinically that is the wrong direction to be wrong in.

The training curve is monotone and flattens right at the published line around epoch 16.

## PanEcho on EchoNet-LVH, LVIDd

Data was 10232 train, 1141 validation, 340 test, out of 11713 videos with none missing. PLAX only, official splits.

Validation MAE 0.444 at epoch 17, test 0.451, R squared 0.369. There is no published number for this cell.

Zero-shot gives 0.452 with R squared 0.335, so the probe adds essentially nothing on MAE here, though it does lift R squared a little.

Relative to the target mean the error is 9.6 percent, which is almost exactly the same as EF's 9.7 percent, on a completely different target, unit and view. The test split is only 340 videos so the R squared has fairly wide error bars.

## PanEcho on MIMIC-IV-Echo, LVEDD

6643 studies had both an mp4 and an lvedd label. One random clip per study out of a median of 41, seed 0. No view filtering, so PLAX, A4C, subcostal and Doppler are all mixed together. Split by subject rather than by study, because a patient can have several studies and splitting by study would leak.

Validation MAE 0.557 at epoch 18, test 0.590, R squared 0.070.

Zero-shot gives 0.585 with R squared 0.097. Predicting the mean gives 0.610, so both of them are only marginally better than a constant.

This is the same physical measurement as the EchoNet-LVH cell but at a different hospital, and it goes from 0.451 to 0.590, roughly 31 percent worse. The label distributions are nearly identical between the two datasets, 4.705 plus or minus 0.834 against 4.560 plus or minus 0.789, so the gap is not caused by the labels being different. Three things changed at the same time and I cannot separate them, which are the lack of view filtering, the random clip selection, and having two and a half times less training data.

## PanEcho on MIMIC-IV-Echo, RVSP

5810 studies had a tr_mmhg label. Same clip selection and split policy as LVEDD.

Validation MAE 10.034, training 8.338, test 8.298 with R squared -0.003. Zero-shot gives 8.756 with R squared -0.061. Predicting the mean gives 8.847.

So both sit essentially at the baseline. This is also the only cell where validation error comes out above training error, which means the probe fit the training set and did not generalise. Both have a large negative bias of around -3.3, so the model systematically under calls pressure.

Units are not the explanation here. PanEcho's RVSP head has a mean of 30.47 and MIMIC's tr_mmhg has a mean of 29.76.

There is a confound I could not resolve. RVSP is derived from the tricuspid regurgitation jet velocity measured on spectral Doppler, plus a right atrial pressure estimate taken from the subcostal view of the inferior vena cava. Neither of those is a normal B-mode cine. This experiment feeds one random clip out of a median of 41, so the odds of that clip containing the Doppler trace are roughly one in forty. Two explanations are still open. Either the representation does not encode pressure information at all, or the model was never shown the input the measurement comes from. Running the same cell with every clip per study would tell them apart.

Worth adding that LVEDD survives the same random clip selection reasonably well while RVSP does not, and there is a straightforward reason. The left ventricle shows up in most views, so a random clip usually contains something usable. The tricuspid Doppler trace either is in the clip or it is not.

One other thing about the label itself. MIMIC's tr_mmhg turns out to equal four times tr_velocity squared, rounded, on 99.6 percent of studies, with no right atrial pressure term added. So it is an arithmetic restatement of another column in the same file rather than an independent measurement.

## EchoPrime

EF gives validation 5.066, test 5.077, R squared 0.664. Published for EchoPrime on this cell is 4.87.

LVIDd gives validation 0.426, test 0.458, R squared 0.342.

LVEDD gives validation 0.523, test 0.557, R squared 0.208.

EchoPrime beats PanEcho by about 6 percent on EF and 6 percent on MIMIC LVEDD, and loses to it by 1.6 percent on EchoNet-LVH LVIDd. The clearest separation is R squared on MIMIC, 0.208 against 0.070, which is roughly triple the explained variance. MIMIC is the only dataset here with unfiltered mixed views and EchoPrime was trained with view information, which is a plausible explanation, though I did not test it directly.

One thing to keep in mind is that EchoPrime is built as a multi video model with attention across the views in a study, and here it only ever gets one clip. That part of the architecture is switched off, so these numbers describe its encoder rather than the full model.

## EchoJEPA-L

EF gives validation 4.928, which is the best validation result of the three models and better than its own published 5.76. Test comes to 5.259 with R squared 0.650.

LVIDd gives validation 0.371 and test 0.411, both the best of the three by a decent margin. Against the baseline it is 26 percent better where the other two are 19 and 17.

It also has the highest prediction spread ratio of any model on any cell at 0.87, meaning its outputs cover 87 percent of the range patients actually span.

No MIMIC cells, since EchoJEPA-L was pretrained on MIMIC-IV-Echo and running it there would be testing on training data.

Note that it wins EF on validation but loses to EchoPrime on test, while winning LVIDd on both. With single runs and no seed variance, a difference that size should not be read as meaningful.

## Prediction spread

MAE tells you the size of the error but not whether the model is responding to the input at all. A model that outputs the same number for every patient can still score reasonably if the label distribution is narrow. So I compared the standard deviation of the predictions against the standard deviation of the labels.

Averaged by dataset the ratio is 0.76 on EchoNet-Dynamic, 0.58 on EchoNet-LVH and 0.32 on MIMIC. The worst single cell is PanEcho on MIMIC RVSP at 0.16, where the label SD is 11.62 and the prediction SD is 1.91.

Across all thirteen cells this ratio correlates with how much better than the baseline the model does, at 0.88. So it is not an arbitrary quantity, it tracks the thing that actually matters.

## An extra experiment on repeat clips

Separately from the benchmark I took 150 MIMIC studies with at least six A4C clips each and ran PanEcho's native heads on every clip.

Within study standard deviation for EF came to 3.44 points, against 5.19 between studies. So six clips of the same view, same patient, same sitting, and the answer shifts by 3.44 EF points depending on which one you pick. That is comparable to the model's total MAE on EchoNet-Dynamic. The ratio holds across all five targets I tested, between 0.66 and 0.84.

Every benchmark here, mine included, feeds one clip per study and reports the result as if it were a property of the model.

I also checked whether that within study disagreement predicts error, and whether the model contradicting its own definitional identities does. EF should equal LVEDV minus LVESV over LVEDV, and PanEcho predicts all three separately, so the violation is computable without any ground truth at all. Both correlated with error at first look, 0.37 and 0.30 on 95 studies. But error itself correlates at 0.71 with how far the patient sits from the dataset average, and once I controlled for that, the partial correlations dropped to 0.20 and 0.13, the second of which is not significant. Most of the apparent signal was regression toward the mean rather than genuine uncertainty. I am reporting that as a negative result.

## Something else that did not hold

ASE guidelines say to take the tricuspid velocity from several windows and use the highest one. The maximum of several noisy estimates is biased upward and the bias grows with how many you take, so studies scanned from more windows should record higher velocities. I tested it and the correlation came to 0.018 across 5810 studies, with t of 1.36. It does not hold.

## Caveats

The logged MAE is scaled by target_std and has to be divided, with a different divisor for each cell. This is the easiest way to get a wrong number out of this repo.

Every config uses resolution 112, which each wrapper then upscales to 224 internally. EchoNet-Dynamic is natively 112 so nothing is lost, but EchoNet-LVH is 1024 by 768 and MIMIC is 1016 by 708, so both are downscaled and then upscaled again. Those two are probably understated. I kept 112 everywhere so the three models are directly comparable, but the ablation has not been run.

MIMIC had no view filtering in these runs. Per clip view labels for all 525,141 files became available afterwards.

MIMIC uses one random clip per study with seed 0, and the variance across seeds is unmeasured.

MIMIC is split by subject rather than by study, to avoid patient leakage.

The PanEcho EF run changed GPU count partway through, epoch 1 on four and epochs 2 to 20 resumed on six, which shifts the learning rate schedule by roughly 2.5 percent over 24,900 steps. The result still matched the published number.

Single run per cell, no seed variance anywhere. Differences under a few percent should not be treated as real.

Embedding dimensions differ across the three models, 768, 512 and 1024, so probe capacity is not identical between rows.
