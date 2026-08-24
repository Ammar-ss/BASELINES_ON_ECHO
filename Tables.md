# Tables

Every number from the benchmark. All MAE values have already been divided by target_std to undo the scaling issue described in notes/known_issues.md.

Test MAE is recomputed across all test samples from the saved prediction files. Validation MAE is the best of the six probes as logged during training.

## Setup

| Dataset | Target | Unit | Native resolution | Views | Train | Val | Test | Label mean | Label SD |
|---|---|---|---|---|---|---|---|---|---|
| EchoNet-Dynamic | EF | % | 112 x 112 | A4C only | 7465 | 1288 | 1277 | 55.78 | 12.41 |
| EchoNet-LVH | LVIDd | cm | 1024 x 768 | PLAX only | 10232 | 1141 | 340 | 4.705 | 0.834 |
| MIMIC-IV-Echo | LVEDD | cm | 1016 x 708 | unfiltered | 4019 | 911 | 1004 | 4.560 | 0.789 |
| MIMIC-IV-Echo | RVSP | mmHg | 1016 x 708 | unfiltered | 4019 | 911 | 880 | 29.76 | 11.72 |

Every run used 20 epochs, resolution 112 upscaled to 224 internally by each wrapper, 16 frames per clip, frame step 2, two segments per video, and a six point grid over learning rate and weight decay.

## Models

| Model | Architecture | Parameters | Embedding dim | Pretraining |
|---|---|---|---|---|
| PanEcho | ConvNeXt-Tiny per frame, then 4 layer transformer | 42M | 768 | Supervised, 39 clinical tasks, over 1M videos |
| EchoPrime | MViT-v2-S, video native | 35M | 512 | Contrastive, 12M video and report pairs |
| EchoJEPA-L | ViT-Large, joint embedding predictive | 300M | 1024 | Self supervised on MIMIC-IV-Echo, from V-JEPA 2 |

## Test MAE

| Model | EF (%) | LVIDd (cm) | LVEDD (cm) | RVSP (mmHg) |
|---|---|---|---|---|
| PanEcho | 5.393 | 0.451 | 0.590 | 8.298 |
| EchoPrime | 5.077 | 0.458 | 0.557 | not run |
| EchoJEPA-L | 5.259 | 0.411 | contaminated | contaminated |
| PanEcho zero-shot | 6.448 | 0.452 | 0.585 | 8.756 |

## Validation MAE

| Model | EF (%) | LVIDd (cm) | LVEDD (cm) | RVSP (mmHg) |
|---|---|---|---|---|
| PanEcho | 5.094 | 0.444 | 0.557 | 10.034 |
| EchoPrime | 5.066 | 0.426 | 0.523 | not run |
| EchoJEPA-L | 4.928 | 0.371 | contaminated | contaminated |

Validation is what the probe was picked on, so it is optimistically biased and test is the honest number. Both are here because the published figures sit closer to my validation than my test, which hints they may be validation selected as well.

## R squared

| Model | EF | LVIDd | LVEDD | RVSP |
|---|---|---|---|---|
| PanEcho | 0.622 | 0.369 | 0.070 | -0.003 |
| EchoPrime | 0.664 | 0.342 | 0.208 | not run |
| EchoJEPA-L | 0.650 | 0.460 | contaminated | contaminated |
| PanEcho zero-shot | 0.434 | 0.335 | 0.097 | -0.061 |

R squared below zero means the predictions do worse than just using the dataset average. It is not bounded at zero here because the model was never fitted on this data.

## Bias

Mean prediction minus mean label. Positive means the model reads high.

| Model | EF | LVIDd | LVEDD | RVSP |
|---|---|---|---|---|
| PanEcho | +1.42 | +0.02 | +0.05 | -3.30 |
| EchoPrime | +0.95 | -0.03 | +0.07 | not run |
| EchoJEPA-L | -0.18 | +0.05 | contaminated | contaminated |
| PanEcho zero-shot | +4.21 | -0.01 | 0.00 | -3.27 |

Both RVSP rows under predict pressure by more than three mmHg, which is the worse direction clinically since it means calling pulmonary hypertension milder than it actually is.

For zero-shot EF I checked whether the +4.21 is just an offset by subtracting it and recomputing. MAE only dropped from 6.448 to 6.015, so it is not a simple calibration shift. The model compresses toward the middle of the range as well as reading high.

## Compared against predicting the average

Predicting the dataset mean for every patient gives an MAE of 9.09 on EF, 0.554 on LVIDd, 0.610 on LVEDD and 8.85 on RVSP.

| Model | EF | LVIDd | LVEDD | RVSP |
|---|---|---|---|---|
| PanEcho | 41% better | 19% better | 3% better | 6% better |
| EchoPrime | 44% better | 17% better | 9% better | not run |
| EchoJEPA-L | 42% better | 26% better | contaminated | contaminated |
| PanEcho zero-shot | 29% better | 18% better | 4% better | 1% better |

This is the table that changes how the others read. A raw MAE means nothing without knowing how hard the task is, and on MIMIC almost nothing is doing much better than a constant.

## Prediction spread

Standard deviation of the predictions over standard deviation of the labels. Near 1 means the model covers the range patients actually span, near 0 means it is close to a constant.

| Model | Dataset | Target | SD labels | SD predictions | Ratio |
|---|---|---|---|---|---|
| EchoJEPA-L | EchoNet-Dynamic | EF | 12.23 | 10.58 | 0.87 |
| PanEcho | EchoNet-Dynamic | EF | 12.23 | 9.77 | 0.80 |
| EchoPrime | EchoNet-Dynamic | EF | 12.23 | 9.46 | 0.77 |
| PanEcho zero-shot | EchoNet-Dynamic | EF | 12.23 | 7.18 | 0.59 |
| EchoJEPA-L | EchoNet-LVH | LVIDd | 0.71 | 0.54 | 0.76 |
| EchoPrime | EchoNet-LVH | LVIDd | 0.71 | 0.41 | 0.58 |
| PanEcho | EchoNet-LVH | LVIDd | 0.71 | 0.40 | 0.56 |
| PanEcho zero-shot | EchoNet-LVH | LVIDd | 0.71 | 0.29 | 0.41 |
| EchoPrime | MIMIC | LVEDD | 0.79 | 0.36 | 0.46 |
| PanEcho zero-shot | MIMIC | LVEDD | 0.79 | 0.24 | 0.31 |
| PanEcho | MIMIC | LVEDD | 0.79 | 0.16 | 0.20 |
| PanEcho zero-shot | MIMIC | RVSP | 11.62 | 5.46 | 0.47 |
| PanEcho | MIMIC | RVSP | 11.62 | 1.91 | 0.16 |

Averaged by dataset the ratio comes to 0.76 on EchoNet-Dynamic, 0.58 on EchoNet-LVH and 0.32 on MIMIC. Across all thirteen cells the ratio correlates with how much better than the average the model does, at 0.88.

## Reproduction check

| Cell | My validation | My test | Published |
|---|---|---|---|
| PanEcho on EchoNet-Dynamic EF | 5.094 | 5.393 | 5.10 |
| EchoPrime on EchoNet-Dynamic EF | 5.066 | 5.077 | 4.87 |
| EchoJEPA-L on EchoNet-Dynamic EF | 4.928 | 5.259 | 5.76 |

No published numbers exist for any other cell in this benchmark.

For reference, the EchoJEPA paper reports RVSP on their own internal Toronto data at 4.54 for EchoJEPA-G, 5.01 for EchoJEPA-L, 5.36 for EchoMAE-L, 5.49 for PanEcho and 5.65 for EchoPrime. All far better than what I get, but they use a multi view protocol rather than one random clip per study.

## Same measurement, two hospitals

LVIDd in EchoNet-LVH and LVEDD in MIMIC are the same physical measurement.

| | EchoNet-LVH | MIMIC | Change |
|---|---|---|---|
| PanEcho MAE | 0.451 cm | 0.590 cm | 31% worse |
| EchoPrime MAE | 0.458 cm | 0.557 cm | 22% worse |
| PanEcho R squared | 0.369 | 0.070 | down 0.30 |
| EchoPrime R squared | 0.342 | 0.208 | down 0.13 |
| Label mean and SD | 4.705 ± 0.834 | 4.560 ± 0.789 | almost identical |
| Training samples | 10232 | 4019 | 2.5x fewer |
| Views | PLAX only | unfiltered, one random clip of about 41 | |

The label distributions match closely so the drop cannot be blamed on the labels being different. Three things changed at once and I cannot separate them.

## Repeat clips of the same view

150 MIMIC studies with at least six A4C clips each, 900 clips in total, run through PanEcho's native heads.

| Target | SD within a study | SD between studies | Ratio |
|---|---|---|---|
| EF | 3.44 | 5.19 | 0.66 |
| LVEDV | 14.31 | 17.69 | 0.81 |
| LVESV | 8.23 | 12.11 | 0.68 |
| LVIDd | 0.17 | 0.21 | 0.84 |
| LVIDs | 0.19 | 0.27 | 0.69 |

Six clips of the same view, same patient, same sitting. The EF prediction moves by 3.44 points depending on which clip gets used, which is about the same size as the model's total error on EchoNet-Dynamic.
